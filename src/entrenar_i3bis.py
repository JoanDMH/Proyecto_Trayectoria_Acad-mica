"""
entrenar_i3bis.py — I-3 bis · Comparación definitiva de algoritmos

Incorpora las cuatro correcciones acumuladas de la auditoría:

  RC-032  Conjunto de variables = S3 (6 académicas), no las 19. S3 iguala al set
          completo (Δ=-0,0005, p=0,983) y no depende de ninguna selección guiada
          por los datos. PROHIBIDO seleccionar variables fuera del pliegue.
  RC-025  Presupuesto de búsqueda equilibrado entre algoritmos. La versión previa
          daba 8 combinaciones a XGBoost frente a 48 a Random Forest.
  RC-031  XGBoost con min_child_weight=1 y reg_lambda en rango bajo: la curva de
          validación mostró que regularizar agresivamente es contraproducente con
          19 positivos (min_child_weight=3 hunde el AUC-PR de 0,710 a 0,397).
  RC-027  Instrumentación completa: métricas por repetición, hiperparámetros de
          cada pliegue, versiones, hash de los datos. Permite prueba pareada y
          verificación de reproducibilidad.

  Población por target (corrige el error señalado antes de la corrida de I-3):
    bajo_rendimiento_art19 -> n=80, solo expuestos (quien no cursó no puede
                              reprobar créditos: no está en riesgo del art. 19)
    graduado               -> n=90, TODOS. Los 10 sin actividad académica son
                              negativos legítimos: ninguno se graduó. Excluirlos
                              elimina casos informativos e infla la prevalencia
                              del 38,9 % al 43,8 %.

Uso:
    python src/entrenar_i3bis.py art19      # target de bajo rendimiento
    python src/entrenar_i3bis.py graduado   # target de graduación
    python src/entrenar_i3bis.py consolidar # tablas + contrastes + artefactos
"""
import os, sys, json, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, joblib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comparacion_estadistica import comparar, tabla_comparativa, DELTA_RELEVANTE
from instrumentacion import Bitacora

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import (average_precision_score, roc_auc_score, f1_score,
                             recall_score, precision_score, matthews_corrcoef,
                             accuracy_score)
from xgboost import XGBClassifier

SEED = 42
SRC = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(SRC, '_i3bis_cache')
os.makedirs(CACHE, exist_ok=True)

N_REP, N_EXT, N_INT = 10, 5, 4   # 10 repeticiones: compromiso entre estabilidad y costo

# ── Conjunto de variables definitivo (S3, RC-032) ────────────────────────────
FEATURES = ['prom_sem1', 'sin_primer_semestre',
            'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat']

TARGETS = {
    'art19':    {'col': 'bajo_rendimiento_art19', 'solo_expuestos': True},
    'graduado': {'col': 'graduado',               'solo_expuestos': False},
}


def modelos():
    """Rejillas con presupuesto EQUILIBRADO: 16-24 combinaciones cada una.
    Antes de la corrección (RC-025) el rango era 8-48, una desventaja de 6:1
    para XGBoost que invalidaba la comparación."""
    return {
        'Regresión Logística (L2)': (
            Pipeline([('sc', StandardScaler()),
                      ('clf', LogisticRegression(random_state=SEED, max_iter=2000))]),
            {'clf__C': [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 100.0],
             'clf__class_weight': [None, 'balanced']},                           # 16
        ),
        'Árbol de Decisión': (
            DecisionTreeClassifier(random_state=SEED),
            {'max_depth': [2, 3, 4, 5], 'min_samples_leaf': [1, 2, 4],
             'criterion': ['gini', 'entropy']},                                  # 24
        ),
        'Random Forest': (
            RandomForestClassifier(random_state=SEED, n_jobs=1),
            {'n_estimators': [150], 'max_depth': [2, 3, 4, None],
             'min_samples_leaf': [1, 2, 4], 'max_features': ['sqrt', None]},     # 24
        ),
        'SVM (RBF)': (
            Pipeline([('sc', StandardScaler()),
                      ('clf', SVC(random_state=SEED, probability=True))]),
            {'clf__C': [0.1, 0.5, 1.0, 5.0, 10.0],
             'clf__gamma': ['scale', 'auto', 0.01, 0.1]},                        # 20
        ),
        # RC-031: min_child_weight fijo en 1. Con 19 positivos, exigir 3 instancias
        # por hoja bloquea los cortes sobre la clase minoritaria.
        'XGBoost': (
            XGBClassifier(random_state=SEED, eval_metric='logloss', n_jobs=1,
                          min_child_weight=1),
            {'n_estimators': [100, 200], 'max_depth': [2, 3],
             'learning_rate': [0.03, 0.1], 'reg_lambda': [0.5, 1.0, 2.0]},       # 24
        ),
    }


def data(clave):
    cfg = TARGETS[clave]
    df = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'))
    if cfg['solo_expuestos']:
        df = df[df['tiene_actividad_academica'] == 1]
    d = df[FEATURES + [cfg['col']]].dropna()
    return d[FEATURES].values, d[cfg['col']].astype(int).values


def evaluar(clave, solo=None):
    """
    Evalúa los algoritmos del target. `solo` permite ejecutar uno a la vez y
    acumular resultados en caché — necesario cuando el entorno limita el tiempo
    por ejecución. Cada modelo se cachea por separado y `consolidar()` los une.
    """
    cfg = TARGETS[clave]
    X, y = data(clave)
    bit = Bitacora(f'I3bis_{clave}' + (f'_{solo}' if solo else ''),
                   archivos_entrada=['src/df_master_limpio.csv'],
                   notas=(f'I-3 bis · target={cfg["col"]} · features=S3 ({len(FEATURES)}) '
                          f'· RC-025/027/031/032'), seed=SEED)
    bit.evento(f'n={len(y)} positivos={int(y.sum())} ({y.mean():.1%}) '
               f'baseline AUC-PR={y.mean():.4f}')

    todos = modelos()
    if solo:
        coincide = [k for k in todos if solo.lower() in k.lower()]
        if not coincide:
            print(f'[!] modelo no encontrado: {solo}. Opciones: {list(todos)}')
            return {}
        todos = {k: todos[k] for k in coincide}

    resultados, probs = {}, {}
    for nombre, (base, grid) in todos.items():
        n_comb = int(np.prod([len(v) for v in grid.values()]))
        bit.evento(f'{nombre}: rejilla de {n_comb} combinaciones')
        por_rep = []
        for r in range(N_REP):
            ext = StratifiedKFold(N_EXT, shuffle=True, random_state=SEED + r)
            interno = StratifiedKFold(N_INT, shuffle=True, random_state=SEED + 100 + r)
            p = np.zeros(len(y), dtype=float)
            for k, (tr, te) in enumerate(ext.split(X, y)):
                gs = GridSearchCV(base, grid, cv=interno,
                                  scoring='average_precision', n_jobs=1)
                gs.fit(X[tr], y[tr])
                p[te] = gs.best_estimator_.predict_proba(X[te])[:, 1]
                bit.registrar_fold(nombre, r, k, gs.best_params_, gs.best_score_,
                                   len(tr), len(te), int(y[tr].sum()), int(y[te].sum()))
            ap = average_precision_score(y, p)
            auc = roc_auc_score(y, p)
            bit.registrar_repeticion(nombre, r, {'AUC_PR': ap, 'AUC_ROC': auc})
            por_rep.append(ap)
            # Acumula para promediar entre repeticiones: una sola es ruidosa y
            # desplaza el umbral óptimo (corrección de RC-034).
            probs[nombre] = p.copy() if r == 0 else probs[nombre] + p
            if r == N_REP - 1:
                probs[nombre] /= N_REP
            # Progreso visible: sin esto, los modelos de conjunto dejan la consola
            # muda durante 15-25 minutos y parecen colgados.
            print(f'    rep {r+1:2d}/{N_REP}  AUC-PR={ap:.4f}  '
                  f'(media parcial {np.mean(por_rep):.4f})', flush=True)
        resultados[nombre] = np.array(por_rep)
        bit.evento(f'{nombre}: AUC-PR {np.mean(por_rep):.4f} ± {np.std(por_rep):.4f}')

    ruta = bit.cerrar(resumen={'target': cfg['col'], 'n': int(len(y)),
                               'positivos': int(y.sum()),
                               'features': FEATURES})
    # Cada modelo escribe su PROPIO archivo. Antes todos escribían en
    # `{clave}.pkl` con el patrón leer-actualizar-escribir, lo que perdía
    # resultados si dos modelos corrían en paralelo (el último en escribir
    # sobrescribía al otro). Ahora ejecutarlos simultáneamente es seguro.
    for nombre, arr in resultados.items():
        slug = ''.join(c if c.isalnum() else '_' for c in nombre)
        joblib.dump({'modelo': nombre, 'scores': arr, 'probs': probs.get(nombre),
                     'y': y, 'X': X, 'bitacora': ruta},
                    os.path.join(CACHE, f'{clave}__{slug}.pkl'))
    acum = cargar_cache(clave)
    print('\n' + tabla_comparativa(acum['resultados']))
    print(f"\nModelos acumulados: {len(acum['resultados'])} de 5")
    return resultados


def cargar_cache(clave):
    """Reúne los archivos por modelo (y el formato antiguo, si existe)."""
    res, probs, y, X, bits = {}, {}, None, None, []
    antiguo = os.path.join(CACHE, f'{clave}.pkl')
    if os.path.exists(antiguo):
        d = joblib.load(antiguo)
        res.update(d.get('resultados', {}))
        probs.update(d.get('probs', {}))
        y, X = d.get('y'), d.get('X')
        bits += d.get('bitacoras', [])
    for f in sorted(os.listdir(CACHE)):
        if f.startswith(f'{clave}__') and f.endswith('.pkl'):
            d = joblib.load(os.path.join(CACHE, f))
            res[d['modelo']] = d['scores']
            if d.get('probs') is not None:
                probs[d['modelo']] = d['probs']
            y, X = d['y'], d['X']
            bits.append(d.get('bitacora'))
    return {'resultados': res, 'probs': probs, 'y': y, 'X': X, 'bitacoras': bits}


def curva_umbral(y, p):
    """
    Curva de umbral operativa.

    Dos correcciones respecto a la primera versión:
      · Barre desde 0,02 (antes 0,10). Con umbrales altos se perdía de vista el
        rango donde se alcanza recall alto, y la curva parecía tener un techo
        de 0,684 que no existía.
      · Añade `n_alertas`: cuántos estudiantes habría que atender. Es la cifra
        que decide el umbral en la práctica — el Programa de Retención (art. 23)
        tiene capacidad finita.

    IMPORTANTE: `p` deben ser probabilidades PROMEDIADAS entre repeticiones, no
    las de una sola. Una repetición aislada es ruidosa y desplaza el óptimo.
    """
    filas = []
    for u in np.arange(0.02, 0.71, 0.02):
        yp = (p >= u).astype(int)
        if yp.sum() == 0:
            continue
        filas.append({'umbral': round(u, 2),
                      'Recall+': recall_score(y, yp, zero_division=0),
                      'Prec+': precision_score(y, yp, zero_division=0),
                      'F1+': f1_score(y, yp, zero_division=0),
                      'F1-mac': f1_score(y, yp, average='macro', zero_division=0),
                      'MCC': matthews_corrcoef(y, yp) if yp.sum() else 0.0,
                      'Acc': accuracy_score(y, yp),
                      'n_alertas': int(yp.sum()),
                      'pct_cohorte': round(yp.sum() / len(y), 3)})
    return pd.DataFrame(filas)


def recomendar_umbral(cur, recall_min=0.75):
    """
    Umbral por el criterio institucional declarado en RC-005: el falso negativo
    es el error caro en alertas tempranas. Se exige un recall mínimo y, entre los
    umbrales que lo cumplen, se toma el de mayor precisión (menos falsas alarmas).

    NO se elige por F1-macro: esa métrica premia el equilibrio entre clases y
    empuja a umbrales altos, lo que contradice el criterio del proyecto.
    """
    ok = cur[cur['Recall+'] >= recall_min]
    if ok.empty:
        return None
    return ok.loc[ok['Prec+'].idxmax()]


def consolidar():
    for clave in TARGETS:
        d = cargar_cache(clave)
        res, y = d['resultados'], d['y']
        if not res:
            print(f'[!] sin resultados para "{clave}" — ejecuta: '
                  f'python src/entrenar_i3bis.py {clave}')
            continue
        faltan = [m for m in modelos() if m not in res]
        if faltan:
            print(f'[!] ATENCIÓN — faltan {len(faltan)} modelos en "{clave}": '
                  f'{", ".join(faltan)}')
        print(f'\n{"="*70}\nTARGET: {TARGETS[clave]["col"]}  ·  n={len(y)}  '
              f'positivos={int(y.sum())}  baseline AUC-PR={y.mean():.4f}\n{"="*70}')
        print(tabla_comparativa(res))

        filas = [{'Modelo': k, 'AUC_PR_media': round(v.mean(), 4),
                  'AUC_PR_sd': round(v.std(), 4),
                  'IC95_lo': round(np.percentile(v, 2.5), 4),
                  'IC95_hi': round(np.percentile(v, 97.5), 4)}
                 for k, v in res.items()]
        pd.DataFrame(filas).sort_values('AUC_PR_media', ascending=False).to_csv(
            os.path.join(SRC, f'i3bis_tabla_{clave}.csv'), index=False)

        nombres = list(res)
        comps = [comparar(res[a], res[b], a, b)
                 for i, a in enumerate(nombres) for b in nombres[i + 1:]]
        pd.DataFrame(comps).to_csv(
            os.path.join(SRC, f'i3bis_comparaciones_{clave}.csv'), index=False)

        mejor = max(res, key=lambda k: res[k].mean())
        empatados = [k for k in res
                     if abs(res[k].mean() - res[mejor].mean()) < DELTA_RELEVANTE]
        print(f'\nMejor por AUC-PR: {mejor}')
        print(f'Empate técnico (Δ<{DELTA_RELEVANTE}): {", ".join(empatados)}')
        if clave == 'art19' and d['probs'].get(mejor) is not None:
            cu = curva_umbral(y, d['probs'][mejor])
            cu.to_csv(os.path.join(SRC, 'i3bis_curva_umbrales.csv'), index=False)
            rec = recomendar_umbral(cu, recall_min=0.75)
            print('\n--- Umbral operativo ---')
            if rec is not None:
                print(f'  Criterio institucional (RC-005: recall >= 0,75, luego '
                      f'máxima precisión):')
                print(f'    umbral {rec["umbral"]:.2f} -> Recall+ {rec["Recall+"]:.3f} · '
                      f'Prec+ {rec["Prec+"]:.3f} · {int(rec["n_alertas"])} alertas '
                      f'({rec["pct_cohorte"]:.0%} de la cohorte)')
            f1m = cu.loc[cu['F1-mac'].idxmax()]
            print(f'  Referencia — máximo F1-macro (NO es el criterio del proyecto):')
            print(f'    umbral {f1m["umbral"]:.2f} -> Recall+ {f1m["Recall+"]:.3f} · '
                  f'Prec+ {f1m["Prec+"]:.3f} · {int(f1m["n_alertas"])} alertas')
            print('\n  La elección final depende de la capacidad de atención del')
            print('  Programa de Retención (art. 23), no solo de la métrica.')
    print('\n[OK] Salidas: src/i3bis_tabla_*.csv, src/i3bis_comparaciones_*.csv, '
          'src/i3bis_curva_umbrales.csv')
    print('Bitácoras completas en bitacora/')


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'consolidar'
    solo = sys.argv[2] if len(sys.argv) > 2 else None
    if arg in TARGETS:
        evaluar(arg, solo)
    else:
        consolidar()
