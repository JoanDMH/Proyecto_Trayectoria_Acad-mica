"""
Entrenamiento reproducible del modelo principal (rendimiento_bajo y graduado).
Metodologia (Fase 4): sin SMOTE, GridSearchCV (f1_weighted, CV-5) para hiperparametros,
metricas por cross_val_predict out-of-fold sobre el dataset completo.
Umbral: 0.29 para rendimiento_bajo (alertas: prioriza Recall+), 0.50 para graduado.
Genera: comparativa_*.csv, mejor_modelo.pkl, resultados y artefactos de la app.
Uso: python src/entrenar_principal.py [rb|gr|ensamblar]
"""
import os, sys, json, joblib
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict
from sklearn.metrics import (f1_score, roc_auc_score, average_precision_score,
                             matthews_corrcoef, accuracy_score, recall_score, precision_score)

SEED = 42
SRC = os.path.dirname(os.path.abspath(__file__))
TMP = '/tmp/d'
FEATURES = ['sexo','nivel_edu_padre','nivel_edu_madre','nivel_edu_max_padres','repitio_escolar',
            'estrato','log_ingresos','sisben_nivel','tipo_plantel','zona_rural','vive_con',
            'situacion_padres','icfes_total','icfes_mat','icfes_lec','icfes_nat','cohorte_encoded','prom_sem1']
UMBRAL = {'rendimiento_bajo': 0.29, 'graduado': 0.50}

def data(target):
    df = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'))
    d = df[FEATURES + [target]].dropna()
    return d[FEATURES].values, d[target].values

def entrenar(target):
    X, y = data(target)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    modelos = {
        'Árbol de Decisión': (DecisionTreeClassifier(random_state=SEED),
            {'max_depth': [2,3,4,5], 'min_samples_split': [2,4,8], 'criterion': ['gini','entropy']}),
        'Random Forest': (RandomForestClassifier(random_state=SEED),
            {'n_estimators': [50,100,200], 'max_depth': [2,3,5,None], 'min_samples_split': [2,4], 'max_features': ['sqrt','log2']}),
        'XGBoost': (XGBClassifier(random_state=SEED, eval_metric='logloss'),
            {'n_estimators': [50,100], 'max_depth': [2,3], 'learning_rate': [0.05,0.1]}),
    }
    u = UMBRAL[target]; filas = {}; fitted = {}
    for nombre, (base, grid) in modelos.items():
        gs = GridSearchCV(base, grid, cv=cv, scoring='f1_weighted', n_jobs=-1)
        gs.fit(X, y)
        best = gs.best_estimator_
        p = cross_val_predict(best, X, y, cv=cv, method='predict_proba', n_jobs=-1)[:, 1]
        yp = (p >= u).astype(int)
        filas[nombre] = {'Recall+': recall_score(y, yp), 'Prec+': precision_score(y, yp, zero_division=0),
                         'F1+': f1_score(y, yp), 'F1-mac': f1_score(y, yp, average='macro'),
                         'AUC': roc_auc_score(y, p), 'AvgP': average_precision_score(y, p),
                         'MCC': matthews_corrcoef(y, yp), 'Acc': accuracy_score(y, yp)}
        fitted[nombre] = best
        print(f"  {nombre}: F1-mac={filas[nombre]['F1-mac']:.3f} AUC={filas[nombre]['AUC']:.3f} Recall+={filas[nombre]['Recall+']:.3f}")
    joblib.dump({'filas': filas, 'fitted': fitted, 'X': X, 'y': y}, os.path.join(TMP, f'_princ_{target}.pkl'))
    print(f"[OK] cache {target}")

def ensamblar():
    rb = joblib.load(os.path.join(TMP, '_princ_rendimiento_bajo.pkl'))
    gr = joblib.load(os.path.join(TMP, '_princ_graduado.pkl'))
    for target, res, fname in [('rendimiento_bajo', rb, 'comparativa_rendimiento_bajo.csv'),
                               ('graduado', gr, 'comparativa_graduado.csv')]:
        d = pd.DataFrame(res['filas']).T
        d.index.name = 'Modelo'
        d.to_csv(os.path.join(SRC, fname))
        print(f"[OK] {fname}")
    # modelo principal: RF para rendimiento_bajo (alineado con el predictor de la app)
    best_rb = rb['fitted']['Random Forest']; best_gr = gr['fitted']['XGBoost']
    imp_rb = pd.Series(best_rb.feature_importances_, index=FEATURES).sort_values(ascending=False)
    imp_gr = pd.Series(best_gr.feature_importances_, index=FEATURES).sort_values(ascending=False)
    joblib.dump(best_rb, os.path.join(SRC, 'mejor_modelo.pkl'))
    joblib.dump(FEATURES, os.path.join(SRC, 'feature_names.pkl'))
    joblib.dump(UMBRAL['rendimiento_bajo'], os.path.join(SRC, 'umbral_optimo.pkl'))
    joblib.dump({'target': 'rendimiento_bajo'}, os.path.join(SRC, 'config_modelo.pkl'))
    res_rb = {'mejor_modelo': best_rb, 'mejor_nombre': 'Random Forest', 'importancias': imp_rb, 'feature_cols': FEATURES}
    res_gr = {'mejor_modelo': best_gr, 'mejor_nombre': 'XGBoost', 'importancias': imp_gr, 'feature_cols': FEATURES}
    joblib.dump(res_rb, os.path.join(SRC, 'resultado_rb.pkl'))
    joblib.dump(res_gr, os.path.join(SRC, 'resultado_gr.pkl'))
    joblib.dump({'imp_rb': imp_rb.to_dict(), 'imp_gr': imp_gr.to_dict(),
                 'resultado_rb': res_rb, 'resultado_gr': res_gr},
                os.path.join(SRC, 'resultados_completos.pkl'))
    print("[OK] artefactos del modelo principal")
    print("\nImportancias RF (rendimiento_bajo):"); print(imp_rb.head(8).round(3).to_string())
    print("\nImportancias XGB (graduado):"); print(imp_gr.head(8).round(3).to_string())

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'todo'
    os.makedirs(TMP, exist_ok=True)
    if cmd == 'rb': entrenar('rendimiento_bajo')
    elif cmd == 'gr': entrenar('graduado')
    elif cmd == 'ensamblar': ensamblar()
