"""
models.py
Fase 4 CRISP-DM — Modelado
Universidad de los Llanos · Cohorte 2017-2 · Ingeniería de Sistemas

Entrena Árbol de Decisión, Random Forest y XGBoost.
Selecciona el mejor por F1-weighted y lo guarda.
"""

import os
import warnings
import numpy as np
import pandas as pd
import joblib
from scipy import stats

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import (
    GridSearchCV, StratifiedKFold, cross_validate, train_test_split
)
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, classification_report,
    confusion_matrix
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

warnings.filterwarnings('ignore')

SEED = 42
SRC_DIR = os.path.dirname(__file__)

# Features disponibles en el momento de ingreso (sin data leakage)
FEATURES_ENTRADA = [
    'sexo', 'nivel_edu_padre', 'nivel_edu_madre', 'nivel_edu_max_padres',
    'repitio_escolar', 'estrato',
    'icfes_total', 'icfes_mat', 'cohorte_encoded'
]

# Features con información del 1er semestre
FEATURES_SEM1 = FEATURES_ENTRADA + ['prom_sem1']


def entrenar_modelos(df, feature_cols=None, target_col='rendimiento_bajo',
                     label='rendimiento_bajo'):
    """
    Entrena los 3 modelos candidatos con GridSearchCV y validación cruzada.
    Retorna el mejor modelo, las métricas y los resultados completos.
    """
    if feature_cols is None:
        feature_cols = FEATURES_ENTRADA

    # Eliminar filas con NaN en features o target
    cols_use = feature_cols + [target_col]
    df_clean = df[cols_use].dropna().copy()

    X = df_clean[feature_cols].values
    y = df_clean[target_col].values

    print(f"\n{'='*55}")
    print(f"TARGET: {target_col} | Features: {len(feature_cols)} | N={len(y)}")
    print(f"Distribución target: {dict(zip(*np.unique(y, return_counts=True)))}")

    # División estratificada 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    # SMOTE si hay desbalance (ratio < 0.4)
    counts = np.bincount(y_train)
    ratio  = counts.min() / counts.max() if counts.max() > 0 else 1.0
    if ratio < 0.4 and counts.min() >= 3:
        try:
            sm = SMOTE(random_state=SEED, k_neighbors=min(2, counts.min()-1))
            X_train_b, y_train_b = sm.fit_resample(X_train, y_train)
            print(f"  SMOTE aplicado: {len(y_train)} → {len(y_train_b)} muestras")
        except Exception:
            X_train_b, y_train_b = X_train, y_train
    else:
        X_train_b, y_train_b = X_train, y_train

    # ── Árbol de Decisión ─────────────────────────────────────────────────────
    param_dt = {
        'max_depth':        [2, 3, 5, None],
        'min_samples_split': [2, 4, 8],
        'min_samples_leaf':  [1, 2, 3],
        'criterion':         ['gini', 'entropy'],
    }
    gs_dt = GridSearchCV(
        DecisionTreeClassifier(random_state=SEED),
        param_dt, cv=CV, scoring='f1_weighted', n_jobs=-1
    )
    gs_dt.fit(X_train_b, y_train_b)

    # ── Random Forest ─────────────────────────────────────────────────────────
    param_rf = {
        'n_estimators': [50, 100, 200],
        'max_depth':    [2, 3, 5, None],
        'min_samples_split': [2, 4],
        'max_features': ['sqrt', 'log2'],
    }
    gs_rf = GridSearchCV(
        RandomForestClassifier(random_state=SEED),
        param_rf, cv=CV, scoring='f1_weighted', n_jobs=-1
    )
    gs_rf.fit(X_train_b, y_train_b)

    # ── XGBoost ───────────────────────────────────────────────────────────────
    scale_pw = (y_train_b == 0).sum() / max((y_train_b == 1).sum(), 1)
    param_xgb = {
        'n_estimators':   [50, 100, 200],
        'max_depth':      [2, 3, 5],
        'learning_rate':  [0.05, 0.1, 0.2],
        'subsample':      [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0],
    }
    gs_xgb = GridSearchCV(
        XGBClassifier(
            random_state=SEED, eval_metric='logloss',
            use_label_encoder=False, scale_pos_weight=scale_pw,
            verbosity=0
        ),
        param_xgb, cv=CV, scoring='f1_weighted', n_jobs=-1
    )
    gs_xgb.fit(X_train_b, y_train_b)

    # ── Evaluación en test ────────────────────────────────────────────────────
    modelos = {
        'Árbol de Decisión': gs_dt.best_estimator_,
        'Random Forest':     gs_rf.best_estimator_,
        'XGBoost':           gs_xgb.best_estimator_,
    }

    resultados = []
    for nombre, modelo in modelos.items():
        y_pred = modelo.predict(X_test)
        try:
            y_prob = modelo.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, y_prob)
        except Exception:
            auc = np.nan
        f1  = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        acc = accuracy_score(y_test, y_pred)
        resultados.append({
            'Modelo': nombre,
            'Accuracy': round(acc, 4),
            'F1-Score (weighted)': round(f1, 4),
            'AUC-ROC': round(auc, 4) if not np.isnan(auc) else 'N/A',
        })
        print(f"  {nombre}: Acc={acc:.3f} F1={f1:.3f} AUC={auc:.3f}")

    df_res = pd.DataFrame(resultados).sort_values('F1-Score (weighted)', ascending=False)

    # Modelo ganador
    mejor_nombre  = df_res.iloc[0]['Modelo']
    mejor_modelo  = modelos[mejor_nombre]
    mejor_f1      = df_res.iloc[0]['F1-Score (weighted)']

    print(f"\n  [OK] Mejor modelo: {mejor_nombre} (F1={mejor_f1})")

    # Validación cruzada del ganador (más robusta)
    cv_scores = cross_validate(
        mejor_modelo, X, y,
        cv=CV, scoring=['f1_weighted', 'accuracy', 'roc_auc'],
        return_train_score=False
    )
    print(f"  CV F1 (5-fold): {cv_scores['test_f1_weighted'].mean():.3f} ± "
          f"{cv_scores['test_f1_weighted'].std():.3f}")

    # Importancia de variables
    importancias = None
    if hasattr(mejor_modelo, 'feature_importances_'):
        importancias = pd.Series(
            mejor_modelo.feature_importances_,
            index=feature_cols
        ).sort_values(ascending=False)

    return {
        'mejor_modelo':    mejor_modelo,
        'mejor_nombre':    mejor_nombre,
        'df_resultados':   df_res,
        'cv_scores':       cv_scores,
        'importancias':    importancias,
        'X_test':          X_test,
        'y_test':          y_test,
        'feature_cols':    feature_cols,
        'target_col':      target_col,
    }


def entrenar_modelo_materia(X, y, materia):
    """Entrena un modelo de reprobación para una materia específica."""
    if len(y) < 10:
        return None

    CV = StratifiedKFold(n_splits=min(5, (y == 1).sum()), shuffle=True, random_state=SEED)

    param_rf = {
        'n_estimators': [50, 100],
        'max_depth': [2, 3],
    }
    gs = GridSearchCV(
        RandomForestClassifier(random_state=SEED),
        param_rf, cv=CV, scoring='f1_weighted', n_jobs=-1
    )
    try:
        gs.fit(X, y)
        y_pred = gs.best_estimator_.predict(X)
        f1 = f1_score(y, y_pred, average='weighted', zero_division=0)
        print(f"  {materia}: F1={f1:.3f} N={len(y)}")
        return gs.best_estimator_
    except Exception as e:
        print(f"  {materia}: Error - {e}")
        return None


def pruebas_estadisticas(df):
    """Ejecuta las pruebas estadísticas para las preguntas a, b, c."""
    resultados = {}

    # ── Pregunta a: Mann-Whitney género vs promedio ───────────────────────────
    hombres = df[df['sexo'] == 1]['PROMEDIO_CARRERA'].dropna()
    mujeres = df[df['sexo'] == 0]['PROMEDIO_CARRERA'].dropna()
    if len(mujeres) >= 2 and len(hombres) >= 2:
        stat_mw, p_mw = stats.mannwhitneyu(hombres, mujeres, alternative='two-sided')
        resultados['genero'] = {
            'prueba': 'Mann-Whitney U',
            'statistic': round(stat_mw, 4),
            'p_value': round(p_mw, 4),
            'p': round(p_mw, 4), # Llave para app.py
            'significativo': p_mw < 0.05,
            'media_M': round(hombres.mean(), 2),
            'media_F': round(mujeres.mean(), 2),
            'mediana_M': round(hombres.median(), 2), # Llave para app.py
            'mediana_F': round(mujeres.median(), 2), # Llave para app.py
            'n_M': len(hombres),
            'n_F': len(mujeres),
        }

    # ── Pregunta b: Spearman nivel educativo padres vs promedio ───────────────
    for col_edu, nombre in [('nivel_edu_padre', 'padre'), ('nivel_edu_madre', 'madre')]:
        sub = df[[col_edu, 'PROMEDIO_CARRERA']].dropna()
        if len(sub) >= 5:
            rho, p_sp = stats.spearmanr(sub[col_edu], sub['PROMEDIO_CARRERA'])
            resultados[f'edu_{nombre}'] = {
                'prueba': 'Spearman',
                'rho': round(rho, 4),
                'p_value': round(p_sp, 4),
                'p': round(p_sp, 4), # Llave para app.py
                'significativo': p_sp < 0.05,
            }

    # ── Pregunta c: repitencia vs tasa de reprobación ────────────────────────
    rep_si  = df[df['repitio_escolar'] == 1]['rendimiento_bajo'].dropna()
    rep_no  = df[df['repitio_escolar'] == 0]['rendimiento_bajo'].dropna()
    if len(rep_si) >= 2 and len(rep_no) >= 2:
        stat_c, p_chi = stats.chi2_contingency(
            pd.crosstab(df['repitio_escolar'], df['rendimiento_bajo'])
        )[:2]
        resultados['repitencia'] = {
            'prueba': 'Chi-cuadrado',
            'statistic': round(stat_c, 4),
            'chi2': round(stat_c, 4), # Llave para app.py
            'p_value': round(p_chi, 4),
            'p': round(p_chi, 4), # Llave para app.py
            'significativo': p_chi < 0.05,
            'tasa_rendimiento_bajo_SI': round(rep_si.mean(), 3),
            'tasa_rendimiento_bajo_NO': round(rep_no.mean(), 3),
            'n_repitio': len(rep_si),
            'n_no_repitio': len(rep_no),
        }

    return resultados


def pipeline_modelado():
    """Ejecuta el pipeline completo de modelado y guarda artefactos."""
    from preprocessing import pipeline_completo, construir_features_materias, cargar_datos

    df, feature_cols, datasets_materias = pipeline_completo()

    print("\n\n=== FASE 4: MODELADO ===")

    # Modelo principal: rendimiento_bajo
    resultado_rb = entrenar_modelos(df, feature_cols, 'rendimiento_bajo', 'rendimiento_bajo')
    resultado_gr = entrenar_modelos(df, feature_cols, 'graduado', 'graduado')

    # El modelo principal (mejor_modelo.pkl) debe ser rendimiento_bajo para alinearse con el predictor interactivo de la app
    resultado_final = resultado_rb
    target_principal = 'rendimiento_bajo'

    print(f"\nModelo principal seleccionado para: {target_principal}")

    # Modelos por materia crítica
    modelos_materias = {}
    print("\n=== Modelos por materia crítica ===")
    for materia, (X, y, _) in datasets_materias.items():
        m = entrenar_modelo_materia(X, y, materia)
        if m is not None:
            modelos_materias[materia] = m

    # Pruebas estadísticas
    print("\n=== Pruebas estadísticas ===")
    pruebas = pruebas_estadisticas(df)
    for k, v in pruebas.items():
        print(f"  {k}: p={v['p_value']} significativo={v['significativo']}")

    # Guardar artefactos
    joblib.dump(resultado_final['mejor_modelo'], os.path.join(SRC_DIR, 'mejor_modelo.pkl'))
    joblib.dump(resultado_final['feature_cols'], os.path.join(SRC_DIR, 'feature_names.pkl'))
    joblib.dump(resultado_rb,                   os.path.join(SRC_DIR, 'resultado_rb.pkl'))
    joblib.dump(resultado_gr,                   os.path.join(SRC_DIR, 'resultado_gr.pkl'))
    joblib.dump(modelos_materias,               os.path.join(SRC_DIR, 'modelos_materias.pkl'))
    joblib.dump(pruebas,                        os.path.join(SRC_DIR, 'pruebas_estadisticas.pkl'))
    joblib.dump({'target': target_principal},   os.path.join(SRC_DIR, 'config_modelo.pkl'))

    # Guardar umbral óptimo
    umbral_val = 0.29 if target_principal == 'rendimiento_bajo' else 0.50
    joblib.dump(umbral_val, os.path.join(SRC_DIR, 'umbral_optimo.pkl'))

    # Crear consolidado para la aplicación Streamlit
    resultados_completos = {
        'imp_rb': resultado_rb['importancias'].to_dict() if resultado_rb['importancias'] is not None else {},
        'imp_gr': resultado_gr['importancias'].to_dict() if resultado_gr['importancias'] is not None else {},
        'resultado_rb': resultado_rb,
        'resultado_gr': resultado_gr,
    }
    joblib.dump(resultados_completos, os.path.join(SRC_DIR, 'resultados_completos.pkl'))

    print(f"\nArtefactos guardados en {SRC_DIR}/")
    print("[OK] mejor_modelo.pkl")
    print("[OK] feature_names.pkl")
    print("[OK] resultado_rb.pkl / resultado_gr.pkl")
    print("[OK] modelos_materias.pkl")
    print("[OK] pruebas_estadisticas.pkl")
    print("[OK] umbral_optimo.pkl")
    print("[OK] resultados_completos.pkl")

    return resultado_final, modelos_materias, pruebas


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    pipeline_modelado()
