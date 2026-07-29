import pandas as pd
import json
import os

print("=== AUDITORIA DE DATOS Y METRICAS ===")

# 1. Chequeo de df_master_limpio
try:
    df = pd.read_csv('src/df_master_limpio.csv')
    print(f"df_master_limpio.csv: N={len(df)}, features={df.shape[1]}")
    print("Variables objetivo:")
    if 'rendimiento_bajo' in df.columns:
        print(f" - rendimiento_bajo: {df['rendimiento_bajo'].sum()} ({(df['rendimiento_bajo'].sum()/len(df)*100):.1f}%)")
    if 'graduado' in df.columns:
        print(f" - graduado: {df['graduado'].sum()} ({(df['graduado'].sum()/len(df)*100):.1f}%)")
    
    if 'En_Formacion' in df.columns:
        print(f" - En_Formacion: {df['En_Formacion'].sum()}")
        
    print("Nombres de columnas (primeras 10):", list(df.columns)[:10])
except Exception as e:
    print("Error leyendo df_master_limpio:", e)

print("\n=== METRICAS MATERIAS ===")
try:
    df_mat = pd.read_csv('src/metricas_materias.csv')
    print("Materias con modelos:", df_mat['materia'].tolist())
    print(df_mat[['materia', 'roc_auc', 'f1_score']])
except Exception as e:
    print("Error leyendo metricas_materias:", e)

print("\n=== COMPARATIVAS ===")
try:
    df_rb = pd.read_csv('src/comparativa_rendimiento_bajo.csv')
    print("Comparativa Rendimiento Bajo (Mejor modelo):")
    best_rb = df_rb.sort_values('roc_auc', ascending=False).iloc[0]
    print(f"Modelo: {best_rb['modelo']}, ROC-AUC: {best_rb['roc_auc']:.4f}")
    
    df_gr = pd.read_csv('src/comparativa_graduado.csv')
    print("Comparativa Graduado (Mejor modelo):")
    best_gr = df_gr.sort_values('roc_auc', ascending=False).iloc[0]
    print(f"Modelo: {best_gr['modelo']}, ROC-AUC: {best_gr['roc_auc']:.4f}")
except Exception as e:
    print("Error leyendo comparativas:", e)
