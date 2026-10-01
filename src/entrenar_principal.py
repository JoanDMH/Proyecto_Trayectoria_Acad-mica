"""
entrenar_principal.py
Fase 4 CRISP-DM - Modelado y comparación rigurosa de algoritmos.
Universidad de los Llanos · Ingeniería de Sistemas (Cohortes 2017-2 y 2018-1).

Protocolo pre-registrado I-3 (ESPEC_I3.md, RC-016, RC-017, RC-021):
- Targets:
  * bajo_rendimiento_art19 (Art. 19 del reglamento vigente, 19 positivos de 80).
  * graduado (35 positivos de 80).
- Población: tiene_actividad_academica == 1 (n = 80). Sin holdout minúsculo.
- Features: 19 variables (incluye indicador sin_primer_semestre de I-2).
- Validación: 15 repeticiones de CV-5 estratificada anidada (GridSearchCV interno 4-fold).
- Métrica principal: AUC-PR (average_precision), adecuada para clases desbalanceadas (24 %).
- Comparación pareada: t-test con corrección de varianza de Nadeau-Bengio (2003).
- Criterio de ganador: umbral de relevancia práctica ΔAUC-PR >= 0.03.
  Si la diferencia es menor, empate técnico y selección por parsimonia (Logística -> Árbol -> RF -> XGBoost -> SVM).
"""
import os
import sys
import json
import joblib
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import (
    average_precision_score, roc_auc_score, recall_score, precision_score,
    f1_score, matthews_corrcoef, accuracy_score
)

from comparacion_estadistica import t_corregido_nadeau_bengio, comparar, tabla_comparativa, matriz_comparaciones

SEED = 42
SRC = os.path.dirname(os.path.abspath(__file__))
N_REPETICIONES = 15
N_SPLITS_EXT = 5
N_SPLITS_INT = 4
DELTA_RELEVANTE = 0.03

FEATURES = [
    'sexo', 'nivel_edu_padre', 'nivel_edu_madre', 'nivel_edu_max_padres',
    'repitio_escolar', 'estrato', 'log_ingresos', 'sisben_nivel',
    'tipo_plantel', 'zona_rural', 'vive_con', 'situacion_padres',
    'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat',
    'cohorte_encoded', 'prom_sem1', 'sin_primer_semestre'
]

def get_modelos():
    return {
        'Regresión Logística (L2)': (
            Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression(random_state=SEED, max_iter=1000))]),
            {'clf__C': [0.01, 0.1, 1.0, 10.0, 100.0]}
        ),
        'Árbol de Decisión': (
            DecisionTreeClassifier(random_state=SEED),
            {'max_depth': [2, 3, 4, 5], 'min_samples_split': [2, 4, 8], 'criterion': ['gini', 'entropy']}
        ),
        'Random Forest': (
            RandomForestClassifier(random_state=SEED, n_jobs=1),
            {'n_estimators': [50, 100, 200], 'max_depth': [2, 3, 5, None], 'min_samples_split': [2, 4], 'max_features': ['sqrt', 'log2']}
        ),
        'SVM (RBF)': (
            Pipeline([('scaler', StandardScaler()), ('clf', SVC(random_state=SEED, probability=True))]),
            {'clf__C': [0.1, 1.0, 10.0], 'clf__gamma': ['scale', 'auto', 0.01, 0.1]}
        ),
        # XGBoost — rejilla CORREGIDA (RC-025).
        # La versión anterior era {n_estimators:[50,100], max_depth:[2,3],
        # learning_rate:[0.05,0.1]} = 8 combinaciones, SIN ningún hiperparámetro de
        # regularización, frente a las 48 de Random Forest. El algoritmo competía
        # con seis veces menos presupuesto de ajuste y sin sus mecanismos propios de
        # control de sobreajuste: su último lugar (AUC-PR 0,528) era en parte un
        # artefacto del diseño experimental, no una propiedad del algoritmo.
        # Se añaden los tres controles que XGBoost usa contra el sobreajuste:
        #   min_child_weight -> peso mínimo por hoja (crítico con 19 positivos)
        #   subsample        -> submuestreo de filas por árbol
        #   reg_lambda       -> penalización L2 sobre los pesos de las hojas
        'XGBoost': (
            XGBClassifier(random_state=SEED, eval_metric='logloss', n_jobs=1),
            {'n_estimators': [100, 200], 'max_depth': [2, 3],
             'learning_rate': [0.03, 0.1], 'min_child_weight': [1, 3],
             'subsample': [0.8, 1.0], 'reg_lambda': [1.0, 5.0]}
        ),
    }


# Presupuesto de búsqueda por algoritmo (nº de combinaciones). Se documenta para
# poder afirmar que la comparación es justa: un algoritmo con menos combinaciones
# compite en desventaja, y esa desventaja no es una propiedad del algoritmo.
PRESUPUESTO_REJILLA = {
    'Regresión Logística (L2)': 5,   # C
    'Árbol de Decisión': 24,         # max_depth × min_samples_split × criterion
    'Random Forest': 48,             # n_estimators × max_depth × min_samples_split × max_features
    'SVM (RBF)': 12,                 # C × gamma
    'XGBoost': 64,                   # corregido en RC-025 (antes: 8)
}

def data(target):
    """Carga df_master_limpio.csv y filtra estudiantes con actividad académica real (n=80)."""
    df = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'))
    df_act = df[df['tiene_actividad_academica'] == 1].copy()
    d = df_act[FEATURES + [target]].dropna()
    return d[FEATURES].values, d[target].values.astype(int)

def optimizar_umbral(y_true, y_probs, target_name):
    """
    Analiza la curva de umbrales out-of-fold.
    Para bajo_rendimiento_art19: prioriza Recall+ (falso negativo crítico en alertas tempranas).
    Para graduado: balancea F1-macro y MCC.
    """
    umbrales = np.arange(0.10, 0.71, 0.02)
    filas = []
    for u in umbrales:
        yp = (y_probs >= u).astype(int)
        rec = recall_score(y_true, yp, zero_division=0)
        prec = precision_score(y_true, yp, zero_division=0)
        f1 = f1_score(y_true, yp, zero_division=0)
        f1_mac = f1_score(y_true, yp, average='macro', zero_division=0)
        # F2 score: beta=2 pondera el recall el doble que la precisión
        f2 = (1 + 4) * (prec * rec) / (4 * prec + rec) if (4 * prec + rec) > 0 else 0.0
        mcc = matthews_corrcoef(y_true, yp)
        acc = accuracy_score(y_true, yp)
        filas.append({
            'umbral': round(u, 2), 'Recall+': rec, 'Prec+': prec,
            'F1+': f1, 'F1-mac': f1_mac, 'F2+': f2, 'MCC': mcc, 'Acc': acc
        })
    df_u = pd.DataFrame(filas)
    
    if target_name == 'bajo_rendimiento_art19':
        # Buscamos umbral con Recall >= 0.70 que maximice F2 o F1-mac
        candidatos = df_u[df_u['Recall+'] >= 0.70]
        if not candidatos.empty:
            mejor = candidatos.sort_values(by=['F2+', 'F1-mac'], ascending=False).iloc[0]
            u_opt = float(mejor['umbral'])
        else:
            u_opt = float(df_u.sort_values(by='F1-mac', ascending=False).iloc[0]['umbral'])
    else:
        mejor = df_u.sort_values(by=['F1-mac', 'MCC'], ascending=False).iloc[0]
        u_opt = float(mejor['umbral'])
        
    return u_opt, df_u

def evaluar_algoritmos_anidados(target_name):
    """
    Ejecuta el protocolo de 15 repeticiones de CV-5 estratificada anidada
    de forma directa, limpia y libre de contención de procesos.
    """
    X, y = data(target_name)
    n_pos = int(y.sum())
    print(f"\n{'='*70}")
    print(f"EVALUACIÓN ANIDADA | Target: {target_name} | n={len(y)} (Positivos: {n_pos}, {n_pos/len(y):.1%})")
    print(f"{'='*70}")
    
    modelos = get_modelos()
    res_pr = {m: [] for m in modelos}
    res_roc = {m: [] for m in modelos}
    probs_oof = {m: np.zeros(len(y)) for m in modelos}
    
    print(f"Ejecutando {N_REPETICIONES} repeticiones de CV-{N_SPLITS_EXT} anidada (GridSearchCV interno {N_SPLITS_INT}-fold)...")
    for r in range(N_REPETICIONES):
        outer = StratifiedKFold(n_splits=N_SPLITS_EXT, shuffle=True, random_state=SEED + r)
        inner = StratifiedKFold(n_splits=N_SPLITS_INT, shuffle=True, random_state=SEED + 100 + r)
        
        for nom, (base, grid) in modelos.items():
            p_r = np.zeros(len(y))
            for train_idx, test_idx in outer.split(X, y):
                gs = GridSearchCV(base, grid, cv=inner, scoring='average_precision', n_jobs=1)
                gs.fit(X[train_idx], y[train_idx])
                p_r[test_idx] = gs.predict_proba(X[test_idx])[:, 1]
                
            res_pr[nom].append(average_precision_score(y, p_r))
            res_roc[nom].append(roc_auc_score(y, p_r))
            probs_oof[nom] += p_r / N_REPETICIONES
            
        print(f"  Repetición {r+1}/{N_REPETICIONES} completada.")
        
    print("\n--- TABLA COMPARATIVA AUC-PR (Métrica Principal) ---")
    print(tabla_comparativa(res_pr))
    
    print("\n--- TABLA COMPARATIVA AUC-ROC ---")
    print(tabla_comparativa(res_roc))
    
    matriz_pr = matriz_comparaciones(res_pr)
    
    u_opt_dict = {}
    filas_metricas = {}
    curvas_umbrales = {}
    for nom in modelos:
        u_m, df_u_m = optimizar_umbral(y, probs_oof[nom], target_name)
        u_opt_dict[nom] = u_m
        curvas_umbrales[nom] = df_u_m
        
        yp = (probs_oof[nom] >= u_m).astype(int)
        filas_metricas[nom] = {
            'Umbral': u_m,
            'Recall+': recall_score(y, yp, zero_division=0),
            'Prec+': precision_score(y, yp, zero_division=0),
            'F1+': f1_score(y, yp, zero_division=0),
            'F1-mac': f1_score(y, yp, average='macro', zero_division=0),
            'AUC': roc_auc_score(y, probs_oof[nom]),
            'AvgP': average_precision_score(y, probs_oof[nom]),
            'MCC': matthews_corrcoef(y, yp),
            'Acc': accuracy_score(y, yp)
        }
    
    df_comp = pd.DataFrame(filas_metricas).T
    df_comp.index.name = 'Modelo'
    
    return {
        'target': target_name,
        'res_pr': res_pr,
        'res_roc': res_roc,
        'matriz_pr': matriz_pr,
        'df_comp': df_comp,
        'probs_oof': probs_oof,
        'u_opt_dict': u_opt_dict,
        'curvas_umbrales': curvas_umbrales,
        'X': X, 'y': y
    }

def ejecutar_pipeline_completo():
    """Ejecuta I-3 completo para bajo_rendimiento_art19 y graduado, y persiste artefactos."""
    res_art19 = evaluar_algoritmos_anidados('bajo_rendimiento_art19')
    res_grad = evaluar_algoritmos_anidados('graduado')
    
    # 1. Guardar tablas comparativas de 8 métricas
    path_art19 = os.path.join(SRC, 'comparativa_bajo_rendimiento_art19.csv')
    path_rb_compat = os.path.join(SRC, 'comparativa_rendimiento_bajo.csv')
    path_grad = os.path.join(SRC, 'comparativa_graduado.csv')
    
    res_art19['df_comp'].to_csv(path_art19)
    res_art19['df_comp'].to_csv(path_rb_compat) # Retrocompatibilidad app
    res_grad['df_comp'].to_csv(path_grad)
    print(f"\n[OK] Guardado {path_art19}")
    print(f"[OK] Guardado {path_rb_compat} (para compatibilidad)")
    print(f"[OK] Guardado {path_grad}")
    
    # 2. Guardar matrices de comparaciones pareadas con p-valor Nadeau-Bengio
    df_mat_art19 = pd.DataFrame(res_art19['matriz_pr'])
    path_mat_art19 = os.path.join(SRC, 'matriz_comparaciones_art19.csv')
    df_mat_art19.to_csv(path_mat_art19, index=False)
    
    df_mat_grad = pd.DataFrame(res_grad['matriz_pr'])
    path_mat_grad = os.path.join(SRC, 'matriz_comparaciones_graduado.csv')
    df_mat_grad.to_csv(path_mat_grad, index=False)
    print(f"[OK] Guardado {path_mat_art19}")
    print(f"[OK] Guardado {path_mat_grad}")
    
    # 3. Guardar tablas estadísticas con medias e IC 95%
    filas_stat_art19 = []
    for nom, v in res_art19['res_pr'].items():
        v = np.asarray(v, float)
        lo, hi = np.percentile(v, [2.5, 97.5])
        filas_stat_art19.append({
            'Modelo': nom,
            'AUC_PR_media': round(float(v.mean()), 3),
            'AUC_PR_sd': round(float(v.std()), 3),
            'IC_95_lo': round(float(lo), 3),
            'IC_95_hi': round(float(hi), 3)
        })
    df_stat_art19 = pd.DataFrame(filas_stat_art19).sort_values(by='AUC_PR_media', ascending=False)
    path_stat_art19 = os.path.join(SRC, 'tabla_comparativa_art19.csv')
    df_stat_art19.to_csv(path_stat_art19, index=False)
    print(f"[OK] Guardado {path_stat_art19}")
    
    # Guardar curva de umbrales para el modelo principal (Random Forest)
    path_u_art19 = os.path.join(SRC, 'curva_umbrales_art19.csv')
    res_art19['curvas_umbrales']['Random Forest'].to_csv(path_u_art19, index=False)
    print(f"[OK] Guardado {path_u_art19}")
    
    # 4. Ajustar modelo final sobre n=80 con GridSearchCV
    print("\nAjustando modelo final sobre n=80 con GridSearchCV...")
    modelos_dict = get_modelos()
    
    base_rf, grid_rf = modelos_dict['Random Forest']
    cv_final = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    gs_final_rf = GridSearchCV(base_rf, grid_rf, cv=cv_final, scoring='average_precision', n_jobs=1)
    gs_final_rf.fit(res_art19['X'], res_art19['y'])
    mejor_modelo_rf = gs_final_rf.best_estimator_
    
    base_xgb, grid_xgb = modelos_dict['XGBoost']
    gs_final_xgb = GridSearchCV(base_xgb, grid_xgb, cv=cv_final, scoring='average_precision', n_jobs=1)
    gs_final_xgb.fit(res_grad['X'], res_grad['y'])
    mejor_modelo_xgb = gs_final_xgb.best_estimator_
    
    imp_rf = pd.Series(mejor_modelo_rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
    imp_xgb = pd.Series(mejor_modelo_xgb.feature_importances_, index=FEATURES).sort_values(ascending=False)
    
    u_art19 = res_art19['u_opt_dict']['Random Forest']
    u_grad = res_grad['u_opt_dict']['XGBoost']
    
    joblib.dump(mejor_modelo_rf, os.path.join(SRC, 'mejor_modelo.pkl'))
    joblib.dump(FEATURES, os.path.join(SRC, 'feature_names.pkl'))
    joblib.dump(u_art19, os.path.join(SRC, 'umbral_optimo.pkl'))
    joblib.dump({'target': 'bajo_rendimiento_art19', 'umbral': u_art19, 'algoritmo': 'Random Forest'}, os.path.join(SRC, 'config_modelo.pkl'))
    
    res_rb_dict = {
        'mejor_modelo': mejor_modelo_rf, 'mejor_nombre': 'Random Forest',
        'importancias': imp_rf, 'feature_cols': FEATURES, 'umbral': u_art19
    }
    res_gr_dict = {
        'mejor_modelo': mejor_modelo_xgb, 'mejor_nombre': 'XGBoost',
        'importancias': imp_xgb, 'feature_cols': FEATURES, 'umbral': u_grad
    }
    joblib.dump(res_rb_dict, os.path.join(SRC, 'resultado_rb.pkl'))
    joblib.dump(res_gr_dict, os.path.join(SRC, 'resultado_gr.pkl'))
    joblib.dump({
        'imp_rb': imp_rf.to_dict(), 'imp_gr': imp_xgb.to_dict(),
        'resultado_rb': res_rb_dict, 'resultado_gr': res_gr_dict
    }, os.path.join(SRC, 'resultados_completos.pkl'))
    
    print("\n[OK] Artefactos de inferencia guardados exitosamente en src/")
    print(f"  Umbral optimizado para bajo rendimiento Art. 19 (RF): {u_art19:.2f}")
    print(f"  Umbral optimizado para graduación (XGBoost): {u_grad:.2f}")
    print("\nTop 5 features Random Forest (bajo_rendimiento_art19):")
    print(imp_rf.head(5).round(3).to_string())
    
    # Reporte de veredictos
    print("\n" + "="*70)
    print("VEREDICTO ESTADÍSTICO DE COMPARACIÓN DE ALGORITMOS (I-3)")
    print("="*70)
    print("Comparaciones clave sobre bajo_rendimiento_art19:")
    for comp in res_art19['matriz_pr']:
        if ('Random Forest' in (comp['modelo_a'], comp['modelo_b'])) or ('SVM (RBF)' in (comp['modelo_a'], comp['modelo_b'])):
            print(f"  * {comp['modelo_a']} vs {comp['modelo_b']}: Δ={comp['diferencia']:+.3f}, p_corregido={comp['p_valor']:.4f} -> {comp['veredicto']}")

if __name__ == '__main__':
    ejecutar_pipeline_completo()
