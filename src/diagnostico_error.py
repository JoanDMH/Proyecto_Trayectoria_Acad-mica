"""
diagnostico_error.py — Diagnóstico de sobreajuste y estimación del error de generalización

Complementa la validación cruzada de I-3 con tres análisis que ella no puede dar:

  1. CURVA DE APRENDIZAJE — ¿el modelo está limitado por datos o por sesgo?
     Si train y validación convergen alto y separados, sobra varianza (sobreajuste);
     si convergen juntos y bajos, el límite es la información disponible. Con n=80
     esta distinción decide si conviene ampliar la muestra (FCBI completa, n≈275)
     o cambiar de variables.

  2. BRECHA TRAIN-VALIDACIÓN por algoritmo — medida directa del sobreajuste.
     La validación cruzada sola informa el error de generalización pero NO cuánto
     de la capacidad se está perdiendo por memorización.

  3. BOOTSTRAP .632+ — segundo estimador del error de generalización, independiente
     de la partición en pliegues. Si coincide con la CV, la estimación es robusta;
     si difiere mucho, la CV está sujeta a la partición concreta.

  4. CURVA DE VALIDACIÓN de los hiperparámetros de regularización de XGBoost,
     para verificar si su bajo desempeño en I-3 se debía a la rejilla empobrecida.

Uso:  python src/diagnostico_error.py
Salidas: src/curva_aprendizaje.csv, src/brecha_train_val.csv,
         src/bootstrap_632.csv, src/curva_validacion_xgb.csv
"""
import os, sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import average_precision_score
from xgboost import XGBClassifier

SEED = 42
SRC = os.path.dirname(os.path.abspath(__file__))
TARGET = 'bajo_rendimiento_art19'
FEATURES = [
    'sexo', 'nivel_edu_padre', 'nivel_edu_madre', 'nivel_edu_max_padres',
    'repitio_escolar', 'estrato', 'log_ingresos', 'sisben_nivel',
    'tipo_plantel', 'zona_rural', 'vive_con', 'situacion_padres',
    'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat',
    'cohorte_encoded', 'prom_sem1', 'sin_primer_semestre'
]


def cargar():
    df = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'))
    df = df[df['tiene_actividad_academica'] == 1]
    d = df[FEATURES + [TARGET]].dropna()
    return d[FEATURES].values, d[TARGET].astype(int).values


MODELOS = {
    'Regresión Logística (L2)': lambda: Pipeline(
        [('s', StandardScaler()), ('c', LogisticRegression(max_iter=1000, random_state=SEED))]),
    'Árbol de Decisión': lambda: DecisionTreeClassifier(max_depth=3, random_state=SEED),
    'Random Forest': lambda: RandomForestClassifier(
        n_estimators=200, max_depth=4, random_state=SEED, n_jobs=-1),
    'SVM (RBF)': lambda: Pipeline(
        [('s', StandardScaler()), ('c', SVC(probability=True, random_state=SEED))]),
    'XGBoost (rejilla vieja)': lambda: XGBClassifier(
        n_estimators=100, max_depth=3, learning_rate=0.1,
        random_state=SEED, eval_metric='logloss', n_jobs=1),
    'XGBoost (regularizado)': lambda: XGBClassifier(
        n_estimators=200, max_depth=2, learning_rate=0.03, min_child_weight=3,
        subsample=0.8, reg_lambda=5.0,
        random_state=SEED, eval_metric='logloss', n_jobs=1),
}


# ── 1 y 2. Brecha train-validación ───────────────────────────────────────────
def brecha_train_val(X, y, n_rep=15):
    filas = []
    for nom, f in MODELOS.items():
        tr_s, te_s = [], []
        for r in range(n_rep):
            cv = StratifiedKFold(5, shuffle=True, random_state=SEED + r)
            for tr, te in cv.split(X, y):
                m = f().fit(X[tr], y[tr])
                tr_s.append(average_precision_score(y[tr], m.predict_proba(X[tr])[:, 1]))
                te_s.append(average_precision_score(y[te], m.predict_proba(X[te])[:, 1]))
        filas.append({'modelo': nom,
                      'AUC_PR_train': round(np.mean(tr_s), 4),
                      'AUC_PR_validacion': round(np.mean(te_s), 4),
                      'brecha': round(np.mean(tr_s) - np.mean(te_s), 4),
                      'sd_validacion': round(np.std(te_s), 4)})
    return pd.DataFrame(filas).sort_values('brecha')


# ── 3. Curva de aprendizaje ──────────────────────────────────────────────────
def curva_aprendizaje(X, y, modelo='Random Forest', fracciones=(0.4, 0.55, 0.7, 0.85, 1.0),
                      n_rep=20):
    f = MODELOS[modelo]
    filas = []
    for frac in fracciones:
        tr_s, te_s, ns = [], [], []
        for r in range(n_rep):
            cv = StratifiedKFold(5, shuffle=True, random_state=SEED + r)
            for tr, te in cv.split(X, y):
                if frac < 1.0:
                    tr, _ = train_test_split(tr, train_size=frac, random_state=SEED + r,
                                             stratify=y[tr])
                if len(np.unique(y[tr])) < 2:
                    continue
                m = f().fit(X[tr], y[tr])
                tr_s.append(average_precision_score(y[tr], m.predict_proba(X[tr])[:, 1]))
                te_s.append(average_precision_score(y[te], m.predict_proba(X[te])[:, 1]))
                ns.append(len(tr))
        filas.append({'fraccion': frac, 'n_entrenamiento': int(np.mean(ns)),
                      'AUC_PR_train': round(np.mean(tr_s), 4),
                      'AUC_PR_validacion': round(np.mean(te_s), 4),
                      'sd_validacion': round(np.std(te_s), 4)})
    return pd.DataFrame(filas)


# ── 4. Bootstrap .632+ ───────────────────────────────────────────────────────
def bootstrap_632(X, y, modelo='Random Forest', B=200):
    """
    Estimador .632+ de Efron-Tibshirani: combina el error aparente (sobreoptimista)
    con el error out-of-bag (pesimista), corrigiendo por la tasa de no-información.
    Es independiente de la partición en pliegues, así que valida la estimación de CV.
    """
    f = MODELOS[modelo]
    rng = np.random.RandomState(SEED)
    n = len(y)
    m_full = f().fit(X, y)
    ap_aparente = average_precision_score(y, m_full.predict_proba(X)[:, 1])
    gamma = y.mean()          # tasa de no-información para AUC-PR = prevalencia
    oob = []
    for b in range(B):
        idx = rng.randint(0, n, n)
        fuera = np.setdiff1d(np.arange(n), idx)
        if len(fuera) < 5 or len(np.unique(y[idx])) < 2 or len(np.unique(y[fuera])) < 2:
            continue
        m = f().fit(X[idx], y[idx])
        oob.append(average_precision_score(y[fuera], m.predict_proba(X[fuera])[:, 1]))
    ap_oob = float(np.mean(oob))
    # Versión para métricas donde MÁS es mejor
    R = (ap_aparente - ap_oob) / (ap_aparente - gamma) if ap_aparente > gamma else 0.0
    R = float(np.clip(R, 0, 1))
    w = 0.632 / (1 - 0.368 * R)
    ap_632 = (1 - w) * ap_aparente + w * ap_oob
    return {'modelo': modelo, 'AUC_PR_aparente': round(ap_aparente, 4),
            'AUC_PR_oob': round(ap_oob, 4), 'peso_w': round(w, 4),
            'AUC_PR_632plus': round(ap_632, 4), 'n_bootstrap': len(oob)}


# ── 5. Curva de validación: regularización de XGBoost ────────────────────────
def curva_validacion_xgb(X, y, n_rep=10):
    filas = []
    for mcw in [1, 3, 5]:
        for lam in [0.5, 1.0, 5.0, 20.0]:
            s = []
            for r in range(n_rep):
                cv = StratifiedKFold(5, shuffle=True, random_state=SEED + r)
                for tr, te in cv.split(X, y):
                    m = XGBClassifier(n_estimators=200, max_depth=2, learning_rate=0.03,
                                      min_child_weight=mcw, subsample=0.8, reg_lambda=lam,
                                      random_state=SEED, eval_metric='logloss',
                                      n_jobs=1).fit(X[tr], y[tr])
                    s.append(average_precision_score(y[te], m.predict_proba(X[te])[:, 1]))
            filas.append({'min_child_weight': mcw, 'reg_lambda': lam,
                          'AUC_PR': round(np.mean(s), 4), 'sd': round(np.std(s), 4)})
    return pd.DataFrame(filas).sort_values('AUC_PR', ascending=False)


def main():
    X, y = cargar()
    print(f'n={len(y)}  positivos={int(y.sum())} ({y.mean():.1%})')
    print(f'Línea base AUC-PR (azar) = {y.mean():.4f}\n')

    print('═══ 1. BRECHA TRAIN–VALIDACIÓN (diagnóstico de sobreajuste) ═══')
    b = brecha_train_val(X, y)
    print(b.to_string(index=False))
    b.to_csv(os.path.join(SRC, 'brecha_train_val.csv'), index=False)
    print('\n  Lectura: brecha grande = el modelo memoriza. Brecha pequeña con')
    print('  validación baja = el límite es la información, no el algoritmo.')

    print('\n═══ 2. CURVA DE APRENDIZAJE (Random Forest) ═══')
    c = curva_aprendizaje(X, y)
    print(c.to_string(index=False))
    c.to_csv(os.path.join(SRC, 'curva_aprendizaje.csv'), index=False)
    print('\n  Si la validación sigue subiendo al 100 %, más datos ayudarían')
    print('  -> argumento empírico para extender a FCBI (n≈275, paso I-5).')

    print('\n═══ 3. BOOTSTRAP .632+ (segundo estimador, independiente de la CV) ═══')
    filas = [bootstrap_632(X, y, m) for m in
             ['Regresión Logística (L2)', 'Random Forest', 'XGBoost (regularizado)']]
    db = pd.DataFrame(filas)
    print(db.to_string(index=False))
    db.to_csv(os.path.join(SRC, 'bootstrap_632.csv'), index=False)
    print('\n  Si .632+ coincide con la CV anidada, la estimación es robusta.')

    print('\n═══ 4. CURVA DE VALIDACIÓN — regularización de XGBoost ═══')
    cx = curva_validacion_xgb(X, y)
    print(cx.to_string(index=False))
    cx.to_csv(os.path.join(SRC, 'curva_validacion_xgb.csv'), index=False)
    print('\n  Compara el mejor valor con el 0,528 obtenido en I-3 con la rejilla')
    print('  empobrecida (8 combinaciones, sin regularización).')

    print('\n[OK] Salidas en src/: brecha_train_val.csv, curva_aprendizaje.csv,')
    print('     bootstrap_632.csv, curva_validacion_xgb.csv')


if __name__ == '__main__':
    main()
