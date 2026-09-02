"""
Entrenamiento reproducible de los modelos de reprobacion por materia critica.
Metricas por VALIDACION CRUZADA (CV-5 estratificada, out-of-fold) - sin fugas:
- prom_global excluye la materia objetivo
- nota_mat1 no se usa en el modelo de Matematicas I
Genera: src/metricas_materias.csv y src/modelos_materias.pkl
"""
import os, sys, joblib
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import cargar_datos, construir_features_materias
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict
from sklearn.metrics import f1_score, roc_auc_score

SEED = 42
SRC = os.path.dirname(os.path.abspath(__file__))

def main():
    ing_car, ing_mat, ing_he, ing_pc, ing_ps, _ = cargar_datos()
    datasets = construir_features_materias(ing_mat)
    filas, modelos = [], {}
    for materia, (X, y, sub) in datasets.items():
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
        gs = GridSearchCV(RandomForestClassifier(random_state=SEED),
                          {'n_estimators': [50, 100], 'max_depth': [2, 3]},
                          cv=cv, scoring='f1_weighted', n_jobs=-1)
        gs.fit(X, y)
        best = gs.best_estimator_
        y_oof = cross_val_predict(best, X, y, cv=cv, n_jobs=-1)
        p_oof = cross_val_predict(best, X, y, cv=cv, method='predict_proba', n_jobs=-1)[:, 1]
        filas.append({'MATERIA': materia,
                      'F1-w':  round(f1_score(y, y_oof, average='weighted'), 3),
                      'F1-mac':round(f1_score(y, y_oof, average='macro'), 3),
                      'AUC':   round(roc_auc_score(y, p_oof), 3),
                      'N': len(y), 'rep': round(y.mean(), 3)})
        modelos[materia] = best
        print(f"  {materia}: F1w={filas[-1]['F1-w']} AUC={filas[-1]['AUC']} N={len(y)} rep={y.mean():.0%}")
    pd.DataFrame(filas).to_csv(os.path.join(SRC, 'metricas_materias.csv'), index=False)
    joblib.dump(modelos, os.path.join(SRC, 'modelos_materias.pkl'))
    print(' metricas_materias.csv y modelos_materias.pkl')

if __name__ == '__main__':
    main()
