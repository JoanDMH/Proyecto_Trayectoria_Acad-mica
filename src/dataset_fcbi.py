"""
dataset_fcbi.py — WP-OE1.5 (parcial) · Dataset maestro de los tres programas

Construye `src/df_master_fcbi.csv` con los 262 estudiantes de Ing. de Sistemas,
Ing. Electrónica y Biología (cohortes 2017-2 y 2018-1), con el target del art. 19
y la variable `programa`.

Y responde la pregunta abierta en RC-036 **midiendo, no opinando**:

    ¿Un modelo conjunto para los tres programas supera a modelos separados?

Regla pre-registrada: el conjunto sustituye a los separados solo si NO pierde más
de 0,03 de AUC-PR frente a la media ponderada de los separados. Si pierde más, se
mantienen separados.

Protocolo idéntico al de I-3 bis (RC-033): conjunto S3, CV-5 × 10 repeticiones,
Random Forest, AUC-PR, SEED=42.

Uso:  python src/dataset_fcbi.py
Salidas: src/df_master_fcbi.csv, src/fcbi_conjunto_vs_separado.csv
"""
import os, sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import (cargar_datos, construir_features_estudiante,
                           construir_target_art19, PROGRAMAS_FCBI)
from comparacion_estadistica import comparar, DELTA_RELEVANTE

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import average_precision_score, roc_auc_score

SEED = 42
SRC = os.path.dirname(os.path.abspath(__file__))
N_REP = 10
TARGET = 'bajo_rendimiento_art19'

# Conjunto S3 (RC-032) + indicador de programa para el modelo conjunto
S3 = ['prom_sem1', 'sin_primer_semestre',
      'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat']

CORTO = {'INGENIERIA DE SISTEMAS': 'Sistemas',
         'INGENIERIA ELECTRONICA': 'Electrónica',
         'BIOLOGIA': 'Biología'}


def construir():
    """Dataset maestro de los tres programas con el target del art. 19."""
    car, mat, he, pc, ps, pob = cargar_datos(PROGRAMAS_FCBI)
    df, feats = construir_features_estudiante(car, he, pc, ps)

    # Programa de cada estudiante
    prog = (car.set_index(car['CODIGO_ESTUDIANTIL'].astype(str))['PROGRAMA']
            .str.strip().str.upper())
    df['CODIGO_INST'] = df['CODIGO_INST'].astype(str)
    df['programa'] = df['CODIGO_INST'].map(prog)
    df['programa_corto'] = df['programa'].map(CORTO)
    # Codificación one-hot para el modelo conjunto
    for p, c in CORTO.items():
        df[f'prog_{c.lower()}'] = (df['programa'] == p).astype(int)

    # Target del art. 19 (misma función que el pipeline de Sistemas)
    t = construir_target_art19(mat, verbose=False)
    t['CODIGO_INST'] = t['CODIGO_INST'].astype(str)
    df = df.merge(t, on='CODIGO_INST', how='left')
    df['tiene_actividad_academica'] = df['tiene_actividad_academica'].fillna(0).astype(int)
    df['n_periodos_cursados'] = df['n_periodos_cursados'].fillna(0).astype(int)
    for c in ('art19_n_eventos', 'art19_dudoso'):
        df[c] = df[c].fillna(0).astype(int)

    df.to_csv(os.path.join(SRC, 'df_master_fcbi.csv'), index=False)
    return df


def rf():
    return RandomForestClassifier(n_estimators=200, max_depth=4,
                                  random_state=SEED, n_jobs=-1)


def evaluar(X, y, n_rep=N_REP):
    """AUC-PR por repetición con CV-5 estratificada."""
    out = []
    for r in range(n_rep):
        cv = StratifiedKFold(5, shuffle=True, random_state=SEED + r)
        p = np.zeros(len(y), dtype=float)
        for tr, te in cv.split(X, y):
            p[te] = rf().fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
        out.append(average_precision_score(y, p))
    return np.array(out)


def main():
    df = construir()
    exp = df[df['tiene_actividad_academica'] == 1].copy()
    print(f'Dataset FCBI: {len(df)} estudiantes · expuestos {len(exp)} · '
          f'positivos {int(exp[TARGET].sum())} ({exp[TARGET].mean():.1%})')
    print(f'Línea base AUC-PR (azar) = {exp[TARGET].mean():.4f}\n')

    print('=== Distribución por programa ===')
    t = (exp.groupby('programa_corto')
         .agg(n=(TARGET, 'size'), positivos=(TARGET, 'sum')).reset_index())
    t['prevalencia'] = (t['positivos'] / t['n']).round(3)
    print(t.to_string(index=False))

    # ── Modelos separados: uno por programa ─────────────────────────────────
    print('\n=== A · MODELOS SEPARADOS (uno por programa) ===')
    sep, pesos = {}, {}
    for p, c in CORTO.items():
        s = exp[exp['programa'] == p].dropna(subset=S3 + [TARGET])
        y = s[TARGET].astype(int).values
        if y.sum() < 8:
            print(f'  {c}: positivos insuficientes'); continue
        sc = evaluar(s[S3].values, y)
        sep[c] = sc; pesos[c] = len(y)
        print(f'  {c:12s} n={len(y):3d} pos={y.sum():3d}  AUC-PR={sc.mean():.4f} ± {sc.std():.4f}  '
              f'(base {y.mean():.3f}, lift {sc.mean()/y.mean():.2f}x)')

    # Media ponderada por tamaño: el desempeño esperado del enfoque separado
    tot = sum(pesos.values())
    sep_pond = sum(sep[c] * pesos[c] for c in sep) / tot

    # ── Modelo conjunto ─────────────────────────────────────────────────────
    print('\n=== B · MODELO CONJUNTO (los tres programas juntos) ===')
    cols_prog = [f'prog_{c.lower()}' for c in CORTO.values()]
    e = exp.dropna(subset=S3 + [TARGET])
    y = e[TARGET].astype(int).values
    conj_sin = evaluar(e[S3].values, y)
    conj_con = evaluar(e[S3 + cols_prog].values, y)
    print(f'  Sin indicador de programa   n={len(y)} pos={y.sum()}  '
          f'AUC-PR={conj_sin.mean():.4f} ± {conj_sin.std():.4f}')
    print(f'  Con indicador de programa   n={len(y)} pos={y.sum()}  '
          f'AUC-PR={conj_con.mean():.4f} ± {conj_con.std():.4f}')

    # ── Veredicto ───────────────────────────────────────────────────────────
    print('\n=== C · VEREDICTO (regla pre-registrada: ΔAUC-PR ≥ 0,03) ===')
    filas = []
    for nom, arr in [('Conjunto sin indicador', conj_sin),
                     ('Conjunto con indicador', conj_con)]:
        c = comparar(arr, sep_pond, nom, 'Separados (media ponderada)')
        filas.append({'comparacion': nom, 'AUC_PR': round(arr.mean(), 4),
                      'separados_ponderado': round(sep_pond.mean(), 4),
                      'diferencia': round(c['diferencia'], 4),
                      'p_valor': round(c['p_valor'], 4),
                      'veredicto': c['veredicto']})
        print(f'  {nom:26s} Δ={c["diferencia"]:+.4f}  p={c["p_valor"]:.3f}')
        print(f'    {c["veredicto"][:78]}')
    c2 = comparar(conj_con, conj_sin, 'Con indicador', 'Sin indicador')
    filas.append({'comparacion': 'Con vs sin indicador de programa',
                  'AUC_PR': round(conj_con.mean(), 4),
                  'separados_ponderado': round(conj_sin.mean(), 4),
                  'diferencia': round(c2['diferencia'], 4),
                  'p_valor': round(c2['p_valor'], 4), 'veredicto': c2['veredicto']})
    print(f'\n  ¿Aporta el indicador de programa? Δ={c2["diferencia"]:+.4f} p={c2["p_valor"]:.3f}')
    print(f'    {c2["veredicto"][:78]}')

    pd.DataFrame(filas).to_csv(
        os.path.join(SRC, 'fcbi_conjunto_vs_separado.csv'), index=False)
    for c, sc in sep.items():
        pd.DataFrame({'programa': c, 'repeticion': range(len(sc)), 'AUC_PR': sc}).to_csv(
            os.path.join(SRC, f'fcbi_separado_{c.lower()}.csv'), index=False)
    print('\n[OK] src/df_master_fcbi.csv · src/fcbi_conjunto_vs_separado.csv')


if __name__ == '__main__':
    main()
