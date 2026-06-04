# -*- coding: utf-8 -*-
"""
save_evaluation_plots.py
Fase 5 CRISP-DM — Evaluación de Modelos
Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

Genera y guarda físicamente las visualizaciones requeridas:
1. fig1_matrices_confusion.png
2. fig2_curvas_roc_pr.png
3. fig3_cv_por_fold.png

Además actualiza train_test_split.json a la nueva población de 89 estudiantes.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.metrics import (
    confusion_matrix, roc_curve, auc, precision_recall_curve,
    average_precision_score, f1_score, recall_score,
    precision_score, matthews_corrcoef, accuracy_score, roc_auc_score
)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

# Configuración
SEED = 42
UMBRAL_RB = 0.29
UMBRAL_GR = 0.50
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(SRC_DIR)
FASE5_DIR = os.path.join(WORKSPACE_DIR, 'Fase 5')
FASE3_DIR = os.path.join(WORKSPACE_DIR, 'Fase 3')
ASSETS_DIR = os.path.join(WORKSPACE_DIR, 'assets')

# Crear directorios si no existen
for d in [FASE5_DIR, FASE3_DIR, ASSETS_DIR]:
    os.makedirs(d, exist_ok=True)

# 1. Cargar Datos
df = pd.read_csv(os.path.join(SRC_DIR, 'df_master_limpio.csv'))
features = joblib.load(os.path.join(SRC_DIR, 'feature_names.pkl'))
X = df[features].values

# 2. Regenerar y guardar train_test_split.json para N=89
indices = np.arange(len(df))
idx_train, idx_test = train_test_split(
    indices, test_size=0.2, random_state=SEED, stratify=df['rendimiento_bajo'].values
)

split_data = {
    "seed": SEED,
    "test_size": 0.2,
    "n_total": int(len(df)),
    "n_train": int(len(idx_train)),
    "n_test": int(len(idx_test)),
    "stratify_target": "rendimiento_bajo",
    "idx_train": [int(x) for x in idx_train],
    "idx_test": [int(x) for x in idx_test]
}

for path in [
    os.path.join(SRC_DIR, 'train_test_split.json'),
    os.path.join(FASE3_DIR, '04_train_test_split.json')
]:
    with open(path, 'w') as f:
        json.dump(split_data, f, indent=2)
print("[OK] train_test_split.json actualizado y guardado.")

# 3. Obtener predicciones CV-5
CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

def get_cv_probs(target, umbral):
    y = df[target].values
    X_tr, y_tr = X[idx_train], y[idx_train]
    counts = np.bincount(y_tr)
    if counts.min() / counts.max() < 0.4 and counts.min() >= 3:
        sm = SMOTE(random_state=SEED, k_neighbors=min(3, counts.min()-1))
        X_tr, y_tr = sm.fit_resample(X_tr, y_tr)
    
    m = XGBClassifier(
        n_estimators=100, max_depth=3, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        use_label_encoder=False, eval_metric='logloss',
        verbosity=0, random_state=SEED
    )
    m.fit(X_tr, y_tr)
    prob_cv = cross_val_predict(m, X, y, cv=CV, method='predict_proba')[:, 1]
    return y, prob_cv, (prob_cv >= umbral).astype(int), m

y_rb, prob_rb, yp_rb, modelo_rb = get_cv_probs('rendimiento_bajo', UMBRAL_RB)
y_gr, prob_gr, yp_gr, modelo_gr = get_cv_probs('graduado', UMBRAL_GR)

# 4. Generar fig1_matrices_confusion.png
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
cm_rb = confusion_matrix(y_rb, yp_rb)
sns.heatmap(cm_rb, annot=True, fmt='d', cmap='Blues', cbar=False, annot_kws={"size": 14})
plt.title(f'Rendimiento Bajo (umbral {UMBRAL_RB})')
plt.xlabel('Predicho')
plt.ylabel('Real')
plt.xticks([0.5, 1.5], ['Normal', 'Riesgo'])
plt.yticks([0.5, 1.5], ['Normal', 'Riesgo'])

plt.subplot(1, 2, 2)
cm_gr = confusion_matrix(y_gr, yp_gr)
sns.heatmap(cm_gr, annot=True, fmt='d', cmap='Oranges', cbar=False, annot_kws={"size": 14})
plt.title(f'Graduación (umbral {UMBRAL_GR})')
plt.xlabel('Predicho')
plt.ylabel('Real')
plt.xticks([0.5, 1.5], ['No Graduado', 'Graduado'])
plt.yticks([0.5, 1.5], ['No Graduado', 'Graduado'])

plt.suptitle('Matrices de Confusión - CV-5 (n=89)', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FASE5_DIR, 'fig1_matrices_confusion.png'), bbox_inches='tight', dpi=150)
plt.savefig(os.path.join(ASSETS_DIR, 'fig1_matrices_confusion.png'), bbox_inches='tight', dpi=150)
plt.close()
print("[OK] fig1_matrices_confusion.png guardado.")

# Imprimir métricas de matriz de confusión para rendimiento_bajo
tn, fp, fn, tp = cm_rb.ravel()
print(f"\nMétricas Reales Rendimiento Bajo:")
print(f"  Falsos Negativos (FN): {fn}")
print(f"  Falsos Positivos (FP): {fp}")
print(f"  Verdaderos Positivos (TP): {tp}")
print(f"  Verdaderos Negativos (TN): {tn}")
print(f"  Recall (Sensibilidad): {recall_score(y_rb, yp_rb):.3f}")
print(f"  Precision: {precision_score(y_rb, yp_rb):.3f}")
print(f"  F1-Score: {f1_score(y_rb, yp_rb):.3f}")
print(f"  F1-Score Macro: {f1_score(y_rb, yp_rb, average='macro'):.3f}")
print(f"  AUC-ROC: {roc_auc_score(y_rb, prob_rb):.3f}")

# Imprimir métricas de matriz de confusión para graduado
tn_g, fp_g, fn_g, tp_g = cm_gr.ravel()
print(f"\nMétricas Reales Graduación:")
print(f"  Falsos Negativos (FN): {fn_g}")
print(f"  Falsos Positivos (FP): {fp_g}")
print(f"  Verdaderos Positivos (TP): {tp_g}")
print(f"  Verdaderos Negativos (TN): {tn_g}")
print(f"  Recall: {recall_score(y_gr, yp_gr):.3f}")
print(f"  Precision: {precision_score(y_gr, yp_gr):.3f}")
print(f"  F1-Score Macro: {f1_score(y_gr, yp_gr, average='macro'):.3f}")
print(f"  AUC-ROC: {roc_auc_score(y_gr, prob_gr):.3f}\n")

# 5. Generar fig2_curvas_roc_pr.png
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# ROC Rendimiento Bajo
fpr_rb, tpr_rb, _ = roc_curve(y_rb, prob_rb)
auc_rb = roc_auc_score(y_rb, prob_rb)
axes[0, 0].plot(fpr_rb, tpr_rb, label=f'XGBoost (AUC={auc_rb:.3f})', color='blue')
axes[0, 0].plot([0, 1], [0, 1], 'k--', alpha=0.5)
# Encontrar tasa de verdaderos positivos en el umbral
idx_u_rb = np.argmin(np.abs(_ - UMBRAL_RB))
axes[0, 0].scatter(fpr_rb[idx_u_rb], tpr_rb[idx_u_rb], color='red', s=80, label=f'Umbral {UMBRAL_RB}')
axes[0, 0].set_title('ROC - Rendimiento Bajo')
axes[0, 0].set_xlabel('Falsos Positivos (1 - Especificidad)')
axes[0, 0].set_ylabel('Verdaderos Positivos (Sensibilidad)')
axes[0, 0].legend()

# ROC Graduación
fpr_gr, tpr_gr, _ = roc_curve(y_gr, prob_gr)
auc_gr = roc_auc_score(y_gr, prob_gr)
axes[0, 1].plot(fpr_gr, tpr_gr, label=f'XGBoost (AUC={auc_gr:.3f})', color='orange')
axes[0, 1].plot([0, 1], [0, 1], 'k--', alpha=0.5)
idx_u_gr = np.argmin(np.abs(_ - UMBRAL_GR))
axes[0, 1].scatter(fpr_gr[idx_u_gr], tpr_gr[idx_u_gr], color='red', s=80, label=f'Umbral {UMBRAL_GR}')
axes[0, 1].set_title('ROC - Graduación')
axes[0, 1].set_xlabel('Falsos Positivos')
axes[0, 1].set_ylabel('Verdaderos Positivos')
axes[0, 1].legend()

# PR Rendimiento Bajo
prec_rb, rec_rb, _ = precision_recall_curve(y_rb, prob_rb)
ap_rb = average_precision_score(y_rb, prob_rb)
axes[1, 0].plot(rec_rb, prec_rb, label=f'AvgPrec={ap_rb:.3f}', color='blue')
base_rb = y_rb.sum() / len(y_rb)
axes[1, 0].axhline(base_rb, color='gray', linestyle=':', label=f'Base {base_rb:.2f}')
# Marcar umbral
idx_pr_u_rb = np.argmin(np.abs(_ - UMBRAL_RB))
axes[1, 0].scatter(rec_rb[idx_pr_u_rb], prec_rb[idx_pr_u_rb], color='red', s=80)
axes[1, 0].set_title('Prec-Recall - Rendimiento Bajo')
axes[1, 0].set_xlabel('Recall')
axes[1, 0].set_ylabel('Precision')
axes[1, 0].legend()

# PR Graduación
prec_gr, rec_gr, _ = precision_recall_curve(y_gr, prob_gr)
ap_gr = average_precision_score(y_gr, prob_gr)
axes[1, 1].plot(rec_gr, prec_gr, label=f'AvgPrec={ap_gr:.3f}', color='orange')
base_gr = y_gr.sum() / len(y_gr)
axes[1, 1].axhline(base_gr, color='gray', linestyle=':', label=f'Base {base_gr:.2f}')
idx_pr_u_gr = np.argmin(np.abs(_ - UMBRAL_GR))
axes[1, 1].scatter(rec_gr[idx_pr_u_gr], prec_gr[idx_pr_u_gr], color='red', s=80)
axes[1, 1].set_title('Prec-Recall - Graduación')
axes[1, 1].set_xlabel('Recall')
axes[1, 1].set_ylabel('Precision')
axes[1, 1].legend()

plt.suptitle('Curvas de Evaluación de Clasificadores (CV-5, n=89)', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FASE5_DIR, 'fig2_curvas_roc_pr.png'), bbox_inches='tight', dpi=150)
plt.savefig(os.path.join(ASSETS_DIR, 'fig2_curvas_roc_pr.png'), bbox_inches='tight', dpi=150)
plt.close()
print("[OK] fig2_curvas_roc_pr.png guardado.")

# 6. Generar fig3_cv_por_fold.png
def cv_folds(target, umbral):
    y = df[target].values
    rows = []
    for fold, (tr_i, te_i) in enumerate(CV.split(X, y), 1):
        # Entrenar modelo en fold de entrenamiento
        # Aplicamos SMOTE si es desbalanceado
        X_fold_tr, y_fold_tr = X[tr_i], y[tr_i]
        counts = np.bincount(y_fold_tr)
        if counts.min() / counts.max() < 0.4 and counts.min() >= 3:
            sm = SMOTE(random_state=SEED, k_neighbors=min(2, counts.min()-1))
            X_fold_tr, y_fold_tr = sm.fit_resample(X_fold_tr, y_fold_tr)
            
        m = XGBClassifier(
            n_estimators=100, max_depth=3, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8,
            use_label_encoder=False, eval_metric='logloss',
            verbosity=0, random_state=SEED
        )
        m.fit(X_fold_tr, y_fold_tr)
        prob_i = m.predict_proba(X[te_i])[:, 1]
        yp_i   = (prob_i >= umbral).astype(int)
        
        rec = recall_score(y[te_i], yp_i, zero_division=0)
        f1_mac = f1_score(y[te_i], yp_i, average='macro', zero_division=0)
        mcc = matthews_corrcoef(y[te_i], yp_i)
        
        rows.append({
            'Fold': f'Fold {fold}',
            'Recall+': rec,
            'F1-mac': f1_mac,
            'MCC': mcc
        })
    return pd.DataFrame(rows)

df_cv_rb = cv_folds('rendimiento_bajo', UMBRAL_RB)
df_cv_gr = cv_folds('graduado', UMBRAL_GR)

# Imprimir métricas por fold
print("\nMétricas de Validación Cruzada por Fold para Rendimiento Bajo:")
print(df_cv_rb.to_string(index=False))
print(f"  Recall+ : {df_cv_rb['Recall+'].mean():.3f} +/- {df_cv_rb['Recall+'].std():.3f}")
print(f"  F1-mac  : {df_cv_rb['F1-mac'].mean():.3f} +/- {df_cv_rb['F1-mac'].std():.3f}")
print(f"  MCC     : {df_cv_rb['MCC'].mean():.3f} +/- {df_cv_rb['MCC'].std():.3f}")

print("\nMétricas de Validación Cruzada por Fold para Graduación:")
print(df_cv_gr.to_string(index=False))
print(f"  Recall+ : {df_cv_gr['Recall+'].mean():.3f} +/- {df_cv_gr['Recall+'].std():.3f}")
print(f"  F1-mac  : {df_cv_gr['F1-mac'].mean():.3f} +/- {df_cv_gr['F1-mac'].std():.3f}")
print(f"  MCC     : {df_cv_gr['MCC'].mean():.3f} +/- {df_cv_gr['MCC'].std():.3f}\n")

# Graficar
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
df_melt_rb = df_cv_rb.melt(id_vars='Fold', var_name='Métrica', value_name='Valor')
sns.barplot(data=df_melt_rb, x='Fold', y='Valor', hue='Métrica', palette='muted')
plt.title('Rendimiento Bajo - Estabilidad por Fold')
plt.ylim(0, 1.1)
plt.ylabel('Score')
plt.xlabel('')
plt.legend(loc='lower left')

plt.subplot(1, 2, 2)
df_melt_gr = df_cv_gr.melt(id_vars='Fold', var_name='Métrica', value_name='Valor')
sns.barplot(data=df_melt_gr, x='Fold', y='Valor', hue='Métrica', palette='muted')
plt.title('Graduación - Estabilidad por Fold')
plt.ylim(0, 1.1)
plt.ylabel('Score')
plt.xlabel('')
plt.legend(loc='lower left')

plt.suptitle('Estabilidad de Métricas en CV-5 (n=89)', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FASE5_DIR, 'fig3_cv_por_fold.png'), bbox_inches='tight', dpi=150)
plt.savefig(os.path.join(ASSETS_DIR, 'fig3_cv_por_fold.png'), bbox_inches='tight', dpi=150)
plt.close()
print("[OK] fig3_cv_por_fold.png guardado.")
