# -*- coding: utf-8 -*-
"""
arnes_experimentos.py — protocolo comun para los bloques PCA / bayesianos / pocos datos
(peticion del asesor, 2026-09-29)

Replica EXACTAMENTE el protocolo de I-3 bis (RC-033) para que cualquier resultado
nuevo sea comparable y las pruebas pareadas sean validas:

    · poblacion   n=80 expuestos (tiene_actividad_academica == 1)
    · objetivo    bajo_rendimiento_art19  (19 positivos, prevalencia 0,2375)
    · validacion  CV externa estratificada de 5 pliegues, 10 repeticiones
    · anidamiento GridSearchCV de 4 pliegues DENTRO de cada pliegue externo
    · semilla     42 (la repeticion r usa SEED + r, identica en todas las config.)
    · metrica     AUC-PR primaria (linea base = prevalencia), AUC-ROC secundaria

Regla que no se negocia: cualquier transformacion que aprenda de los datos
—escalado, PCA, PLS, seleccion— va DENTRO del Pipeline, de modo que se ajusta
solo con el pliegue de entrenamiento. Ajustarla antes de la CV es la tercera
forma de fuga documentada en RC-021/RC-032.
"""
import json, os, warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import average_precision_score, roc_auc_score
from scipy import stats

SRC = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(SRC, '_cache_experimentos')
os.makedirs(CACHE, exist_ok=True)

SEED, N_REP, N_EXT, N_INT = 42, 10, 5, 4

V19 = ['sexo', 'nivel_edu_padre', 'nivel_edu_madre', 'nivel_edu_max_padres',
       'repitio_escolar', 'estrato', 'log_ingresos', 'sisben_nivel',
       'tipo_plantel', 'zona_rural', 'vive_con', 'situacion_padres',
       'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat',
       'cohorte_encoded', 'prom_sem1', 'sin_primer_semestre']

S3 = ['prom_sem1', 'sin_primer_semestre', 'icfes_total',
      'icfes_mat', 'icfes_lec', 'icfes_nat']

ETIQUETAS = {
    'sexo': 'Sexo', 'nivel_edu_padre': 'Educación del padre',
    'nivel_edu_madre': 'Educación de la madre',
    'nivel_edu_max_padres': 'Educación máx. de los padres',
    'repitio_escolar': 'Repitió año escolar', 'estrato': 'Estrato',
    'log_ingresos': 'Log. ingresos familiares', 'sisben_nivel': 'Nivel SISBEN',
    'tipo_plantel': 'Tipo de plantel', 'zona_rural': 'Zona rural',
    'vive_con': 'Vive con', 'situacion_padres': 'Situación de los padres',
    'icfes_total': 'SABER 11 · total', 'icfes_mat': 'SABER 11 · matemáticas',
    'icfes_lec': 'SABER 11 · lectura', 'icfes_nat': 'SABER 11 · naturales',
    'cohorte_encoded': 'Cohorte', 'prom_sem1': 'Promedio 1er semestre',
    'sin_primer_semestre': 'Sin primer semestre',
}


def cargar(variables=V19):
    d = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'))
    e = d[d.tiene_actividad_academica == 1]
    sub = e[list(variables) + ['bajo_rendimiento_art19']].dropna()
    X = sub[list(variables)].values.astype(float)
    y = sub['bajo_rendimiento_art19'].astype(int).values
    return X, y, list(variables)


# --------------------------------------------------------------------- nucleo
def evaluar(nombre, construir, variables=S3, grid=None, n_rep=N_REP,
            usar_cache=True, verbose=True):
    """Evalua una configuracion con el protocolo anidado y cachea el resultado.

    construir() -> estimador de sklearn (Pipeline si hay preprocesado).
    grid: dict de hiperparametros; si es None no hay busqueda interna.
    Devuelve dict con ap[], roc[] por repeticion y las probabilidades medias.
    """
    ruta = os.path.join(CACHE, f'{nombre}.json')
    res = None
    if usar_cache and os.path.exists(ruta):
        with open(ruta, encoding='utf8') as f:
            res = json.load(f)
        if len(res.get('ap', [])) >= n_rep:
            if verbose:
                print(f'  [cache] {nombre:38s} AUC-PR {np.mean(res["ap"]):.3f}')
            return res
    if res is None:
        res = {'nombre': nombre, 'variables': list(variables), 'ap': [], 'roc': [],
               'probas': [], 'hiperparametros': []}

    X, y, _ = cargar(variables)
    res['n'], res['positivos'] = int(len(y)), int(y.sum())

    # Se guarda tras CADA repeticion: el entorno de ejecucion corta a los 180 s,
    # asi que el calculo tiene que poder reanudarse donde se quedo.
    for r in range(len(res['ap']), n_rep):
        cv = StratifiedKFold(N_EXT, shuffle=True, random_state=SEED + r)
        p = np.zeros(len(y))
        for tr, te in cv.split(X, y):
            est = construir()
            if grid:
                inner = StratifiedKFold(N_INT, shuffle=True, random_state=SEED)
                gs = GridSearchCV(est, grid, scoring='average_precision',
                                  cv=inner, n_jobs=-1, refit=True)
                gs.fit(X[tr], y[tr])
                est = gs.best_estimator_
                res['hiperparametros'].append({k: str(v) for k, v in gs.best_params_.items()})
            else:
                est.fit(X[tr], y[tr])
            p[te] = est.predict_proba(X[te])[:, 1]
        res['ap'].append(float(average_precision_score(y, p)))
        res['roc'].append(float(roc_auc_score(y, p)))
        res['probas'].append(p.tolist())
        with open(ruta, 'w', encoding='utf8') as f:
            json.dump(res, f, ensure_ascii=False)
        if verbose:
            print(f'    rep {r+1}/{n_rep}  AUC-PR {res["ap"][-1]:.3f}', flush=True)

    res['proba_media'] = np.mean(res['probas'], axis=0).tolist()
    with open(ruta, 'w', encoding='utf8') as f:
        json.dump(res, f, ensure_ascii=False)
    if verbose:
        print(f'  {nombre:38s} AUC-PR {np.mean(res["ap"]):.3f} ± {np.std(res["ap"]):.3f}'
              f'   AUC-ROC {np.mean(res["roc"]):.3f}')
    return res


# ------------------------------------------------- prueba t corregida (RC-021)
def t_nadeau_bengio(a, b, n_test=1 / N_EXT):
    """t pareada corregida de Nadeau-Bengio para CV repetida.

    La t clasica es anticonservadora aqui porque los pliegues comparten datos de
    entrenamiento. La correccion infla la varianza por (1/k + n_test/n_train).
    """
    d = np.asarray(a, float) - np.asarray(b, float)
    k = len(d)
    if k < 2 or np.allclose(d, 0):
        return float(d.mean()), np.nan, np.nan
    corr = (1.0 / k) + (n_test / (1.0 - n_test))
    t = d.mean() / np.sqrt(corr * d.var(ddof=1))
    p = 2 * (1 - stats.t.cdf(abs(t), k - 1))
    return float(d.mean()), float(t), float(p)


def comparar_contra(base, otros, clave='ap'):
    """Tabla de cada configuracion frente a la de referencia."""
    filas = []
    for r in otros:
        dif, t, p = t_nadeau_bengio(r[clave], base[clave])
        filas.append({
            'Configuración': r['nombre'],
            'AUC-PR': round(float(np.mean(r['ap'])), 4),
            'DE': round(float(np.std(r['ap'])), 4),
            'AUC-ROC': round(float(np.mean(r['roc'])), 4),
            'Δ vs referencia': round(dif, 4),
            't corregido': None if np.isnan(t) else round(t, 3),
            'p': None if np.isnan(p) else round(p, 4),
            'Veredicto': veredicto(dif, p),
        })
    return pd.DataFrame(filas)


def veredicto(dif, p, delta_relevante=0.03):
    if np.isnan(p):
        return 'sin diferencia'
    if p >= 0.05:
        return 'empate estadístico'
    return ('mejora relevante' if dif >= delta_relevante else
            'mejora marginal') if dif > 0 else (
            'peor (relevante)' if dif <= -delta_relevante else 'peor (marginal)')


def prevalencia():
    _, y, _ = cargar(S3)
    return float(y.mean())
