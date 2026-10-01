"""
seleccion_variables.py — WP-OE1.2 · Verificación empírica del conjunto de features

Responde tres preguntas que hasta ahora NO se habían contestado con evidencia:

  1. ¿Qué variables aportan realmente capacidad predictiva?
     -> IMPORTANCIA POR PERMUTACIÓN, no MDI. La importancia por impureza (`feature_
        importances_`) mide cuántas veces el árbol usó la variable para partir, no
        cuánto aporta a predecir: favorece a las variables con muchos valores
        distintos. Demostrado en RC-019: dos columnas de ruido puro capturaron el
        14,3 % de la importancia MDI, una de ellas por encima de 13 variables reales.

  2. ¿Hay redundancia estructural?
     -> Dos variables son funciones deterministas de otras ya incluidas:
          nivel_edu_max_padres = max(nivel_edu_padre, nivel_edu_madre)
          icfes_total          = icfes_mat + icfes_ing + icfes_lec + icfes_soc + icfes_nat
        (de esas cinco componentes, tres están además incluidas por separado).

  3. ¿Hacen falta 19 variables para el mismo desempeño?
     -> ABLATION sobre subconjuntos definidos a priori, evaluados con el MISMO
        protocolo anidado de I-3 y comparados con la prueba de Nadeau-Bengio.

Protocolo idéntico a ESPEC_I3.md: SEED=42, CV-5 estratificada repetida, AUC-PR como
métrica principal, umbral de relevancia ΔAUC-PR ≥ 0,03.

Uso:  python src/seleccion_variables.py
Salidas: src/permutacion_importancia.csv
         src/redundancia_vif.csv
         src/ablation_subconjuntos.csv
         src/ablation_comparaciones.csv
"""
import os, sys, json, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comparacion_estadistica import evaluar_repetido, comparar, tabla_comparativa

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score

SEED = 42
SRC = os.path.dirname(os.path.abspath(__file__))
N_REP = 15
TARGET = 'bajo_rendimiento_art19'

FEATURES = [
    'sexo', 'nivel_edu_padre', 'nivel_edu_madre', 'nivel_edu_max_padres',
    'repitio_escolar', 'estrato', 'log_ingresos', 'sisben_nivel',
    'tipo_plantel', 'zona_rural', 'vive_con', 'situacion_padres',
    'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat',
    'cohorte_encoded', 'prom_sem1', 'sin_primer_semestre'
]

# ── Subconjuntos definidos A PRIORI (no elegidos tras ver resultados) ────────
SUBCONJUNTOS = {
    'S1 · solo ingreso (socioec. + SABER 11)':
        [f for f in FEATURES if f not in ('prom_sem1', 'sin_primer_semestre')],
    'S2 · S1 + primer semestre  [= set completo, 19]':
        FEATURES,
    'S3 · solo académicas':
        ['icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat',
         'prom_sem1', 'sin_primer_semestre'],
    'S4 · solo socioeconómicas':
        ['sexo', 'nivel_edu_padre', 'nivel_edu_madre', 'repitio_escolar', 'estrato',
         'log_ingresos', 'sisben_nivel', 'tipo_plantel', 'zona_rural', 'vive_con',
         'situacion_padres'],
    'S5 · sin redundancias estructurales (17)':
        [f for f in FEATURES if f not in ('nivel_edu_max_padres', 'icfes_total')],
    'S6 · mínimo (top-5 por permutación)':
        None,   # se completa en tiempo de ejecución
    'S7 · solo prom_sem1 (referencia)':
        ['prom_sem1'],
}


def cargar():
    df = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'))
    df = df[df['tiene_actividad_academica'] == 1].copy()
    d = df[FEATURES + [TARGET]].dropna()
    return d[FEATURES], d[TARGET].astype(int)


def rf():
    return RandomForestClassifier(n_estimators=200, max_depth=4,
                                  random_state=SEED, n_jobs=-1)


def logreg():
    return Pipeline([('s', StandardScaler()),
                     ('c', LogisticRegression(max_iter=1000, random_state=SEED))])


# ── 1. Importancia por permutación ───────────────────────────────────────────
def importancia_permutacion(X, y, n_repeats=30):
    """
    Mide la CAÍDA DE AUC-PR al barajar cada variable, promediada sobre los pliegues
    de validación cruzada. A diferencia de MDI, una variable irrelevante da ~0.
    Se calcula sobre datos NO vistos en el entrenamiento de cada pliegue.
    """
    filas = []
    for r in range(5):
        cv = StratifiedKFold(5, shuffle=True, random_state=SEED + r)
        for tr, te in cv.split(X, y):
            m = rf().fit(X.iloc[tr], y.iloc[tr])
            pi = permutation_importance(m, X.iloc[te], y.iloc[te],
                                        scoring='average_precision',
                                        n_repeats=n_repeats, random_state=SEED,
                                        n_jobs=-1)
            filas.append(pd.Series(pi.importances_mean, index=X.columns))
    imp = pd.DataFrame(filas)
    out = pd.DataFrame({
        'caida_AUC_PR_media': imp.mean(),
        'sd': imp.std(),
        'veces_positiva': (imp > 0).mean(),
    }).sort_values('caida_AUC_PR_media', ascending=False)
    # Importancia MDI para contrastar el sesgo
    out['MDI_referencia'] = pd.Series(
        rf().fit(X, y).feature_importances_, index=X.columns)
    return out


# ── 2. Redundancia: VIF y correlaciones ──────────────────────────────────────
def redundancia(X):
    Xs = (X - X.mean()) / X.std().replace(0, 1)
    Xs = Xs.fillna(0)
    filas = []
    for c in X.columns:
        otras = [o for o in X.columns if o != c]
        # R² de regresar c contra las demás -> VIF = 1/(1-R²)
        A = np.column_stack([np.ones(len(Xs)), Xs[otras].values])
        beta, *_ = np.linalg.lstsq(A, Xs[c].values, rcond=None)
        pred = A @ beta
        ss_res = ((Xs[c].values - pred) ** 2).sum()
        ss_tot = ((Xs[c].values - Xs[c].values.mean()) ** 2).sum()
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        vif = 1 / (1 - r2) if r2 < 0.9999 else np.inf
        filas.append({'variable': c, 'R2_vs_resto': round(r2, 4),
                      'VIF': round(vif, 2) if np.isfinite(vif) else np.inf})
    return pd.DataFrame(filas).sort_values('VIF', ascending=False)


# ── 3. Ablation ──────────────────────────────────────────────────────────────
def ablation(X, y, subconjuntos):
    res_rf, res_lr = {}, {}
    for nom, cols in subconjuntos.items():
        if not cols:
            continue
        Xi = X[cols].values
        res_rf[nom] = evaluar_repetido(rf, Xi, y.values, n_rep=N_REP,
                                       metrica=average_precision_score)
        res_lr[nom] = evaluar_repetido(logreg, Xi, y.values, n_rep=N_REP,
                                       metrica=average_precision_score)
    return res_rf, res_lr


# ── 3-bis. Selección ANIDADA (corrige el sesgo de RC-030) ───────────────────
def seleccion_anidada(X, y, k=5, n_rep=15):
    """
    Estima honestamente el desempeño de "quedarse con las k mejores variables".

    ⚠️ POR QUÉ EXISTE ESTA FUNCIÓN (RC-030): la primera versión de este script
    calculaba la importancia sobre TODA la muestra, congelaba el top-k y lo
    evaluaba por validación cruzada sobre esos mismos datos. Los pliegues de
    prueba habían participado en elegir las variables, así que el resultado
    (S6: Δ=+0,085, p=0,002) estaba inflado. Es la misma fuga que RC-021
    documentó para los hiperparámetros, trasladada a las features
    (Ambroise & McLachlan, 2002, PNAS).

    Aquí la selección ocurre DENTRO de cada pliegue de entrenamiento: cada
    pliegue elige sus propias k variables sin ver el pliegue de prueba. El
    resultado es comparable con los subconjuntos definidos a priori.

    Devuelve (scores_por_repeticion, frecuencia_de_seleccion_por_variable).
    """
    scores, elegidas = [], []
    for r in range(n_rep):
        cv = StratifiedKFold(5, shuffle=True, random_state=SEED + r)
        y_prob = np.zeros(len(y), dtype=float)
        for tr, te in cv.split(X, y):
            Xtr, ytr = X.iloc[tr], y.iloc[tr]
            # --- selección usando SOLO el pliegue de entrenamiento ---
            m = rf().fit(Xtr, ytr)
            pi = permutation_importance(m, Xtr, ytr, scoring='average_precision',
                                        n_repeats=10, random_state=SEED, n_jobs=-1)
            top = list(X.columns[np.argsort(pi.importances_mean)[::-1][:k]])
            elegidas.extend(top)
            # --- evaluación sobre el pliegue de prueba, nunca visto ---
            m2 = rf().fit(Xtr[top], ytr)
            y_prob[te] = m2.predict_proba(X.iloc[te][top])[:, 1]
        scores.append(average_precision_score(y, y_prob))
    frec = (pd.Series(elegidas).value_counts() / (n_rep * 5)).rename('frecuencia')
    return np.array(scores), frec


def main():
    X, y = cargar()
    print(f'Población: n={len(X)}  positivos={int(y.sum())} ({y.mean():.1%})')
    print(f'Línea base AUC-PR (azar) = prevalencia = {y.mean():.4f}\n')

    print('═══ 1. IMPORTANCIA POR PERMUTACIÓN (caída de AUC-PR al barajar) ═══')
    imp = importancia_permutacion(X, y)
    print(imp.round(4).to_string())
    imp.to_csv(os.path.join(SRC, 'permutacion_importancia.csv'))
    utiles = imp[imp['caida_AUC_PR_media'] > 0].index.tolist()
    print(f'\nVariables con aporte positivo: {len(utiles)} de {len(FEATURES)}')

    print('\n═══ 2. REDUNDANCIA (VIF sobre variables estandarizadas) ═══')
    red = redundancia(X)
    print(red.to_string(index=False))
    red.to_csv(os.path.join(SRC, 'redundancia_vif.csv'), index=False)

    # ⚠️ S6 queda DESACTIVADO (RC-030): definirlo con el top-5 calculado sobre
    # toda la muestra y evaluarlo por CV sobre esa misma muestra infla el
    # resultado. Se sustituye por `seleccion_anidada()`, que elige dentro de
    # cada pliegue de entrenamiento. Se conserva el cálculo solo como
    # referencia descriptiva, marcado y fuera de la comparación.
    top5_global = imp.index[:5].tolist()
    print(f'\n[referencia descriptiva, NO comparable] top-5 global: {top5_global}')
    SUBCONJUNTOS.pop('S6 · mínimo (top-5 por permutación)', None)

    print('\n═══ 3. ABLATION DE SUBCONJUNTOS (AUC-PR, CV-5 × 15 rep) ═══')
    res_rf, res_lr = ablation(X, y, SUBCONJUNTOS)

    print('\n--- Random Forest ---')
    print(tabla_comparativa(res_rf))
    print('\n--- Regresión Logística ---')
    print(tabla_comparativa(res_lr))

    filas = []
    for nom in res_rf:
        filas.append({'subconjunto': nom,
                      'n_features': len(SUBCONJUNTOS[nom]),
                      'RF_AUC_PR': round(res_rf[nom].mean(), 4),
                      'RF_sd': round(res_rf[nom].std(), 4),
                      'LR_AUC_PR': round(res_lr[nom].mean(), 4),
                      'LR_sd': round(res_lr[nom].std(), 4)})
    df_abl = pd.DataFrame(filas).sort_values('RF_AUC_PR', ascending=False)
    df_abl.to_csv(os.path.join(SRC, 'ablation_subconjuntos.csv'), index=False)

    print('\n═══ 4. ¿Se puede reducir sin perder desempeño? ═══')
    ref = 'S2 · S1 + primer semestre  [= set completo, 19]'
    comps = []
    for nom in res_rf:
        if nom == ref:
            continue
        c = comparar(res_rf[nom], res_rf[ref], nom, 'set completo (19)')
        comps.append(c)
        print(f"  {nom:44s} Δ={c['diferencia']:+.4f} p={c['p_valor']:.3f} -> {c['veredicto'][:52]}")
    pd.DataFrame(comps).to_csv(os.path.join(SRC, 'ablation_comparaciones.csv'), index=False)

    print('\n═══ 5. SELECCIÓN ANIDADA — estimación honesta del top-k (RC-030) ═══')
    print('  La selección ocurre dentro de cada pliegue de entrenamiento.')
    filas_an = []
    for k in (3, 5, 8):
        sc, frec = seleccion_anidada(X, y, k=k)
        ref = res_rf[ref_nom] if (ref_nom := 'S2 · S1 + primer semestre  [= set completo, 19]') in res_rf else None
        c = comparar(sc, ref, f'top-{k} anidado', 'set completo (19)') if ref is not None else None
        filas_an.append({'k': k, 'AUC_PR': round(sc.mean(), 4), 'sd': round(sc.std(), 4),
                         'delta_vs_completo': round(c['diferencia'], 4) if c else None,
                         'p_valor': round(c['p_valor'], 4) if c else None,
                         'veredicto': c['veredicto'] if c else ''})
        print(f'\n  top-{k}: AUC-PR = {sc.mean():.4f} ± {sc.std():.4f}')
        if c:
            print(f'         vs set completo: Δ={c["diferencia"]:+.4f} p={c["p_valor"]:.3f}')
            print(f'         {c["veredicto"][:70]}')
        print(f'         variables más seleccionadas: '
              f'{", ".join(f"{v} ({p:.0%})" for v, p in frec.head(6).items())}')
    pd.DataFrame(filas_an).to_csv(os.path.join(SRC, 'seleccion_anidada.csv'), index=False)

    print('\n[OK] Salidas en src/: permutacion_importancia.csv, redundancia_vif.csv,')
    print('     ablation_subconjuntos.csv, ablation_comparaciones.csv, seleccion_anidada.csv')
    print('\nREGLA DE DECISIÓN pre-registrada: un subconjunto reducido sustituye al')
    print('completo solo si NO pierde más de 0,03 de AUC-PR (empate técnico).')
    print('Los subconjuntos a priori (S1–S5, S7) son comparables directamente.')
    print('El top-k SOLO es comparable en su versión anidada (bloque 5).')


if __name__ == '__main__':
    main()
