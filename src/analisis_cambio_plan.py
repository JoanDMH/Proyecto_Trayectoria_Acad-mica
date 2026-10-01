"""
analisis_cambio_plan.py — Sensibilidad del modelo S3 a la población y al plan de estudios
(revisión de Fases 2-3, oct-2026). Hiperparámetros FIJOS en la configuración modal de
I-3 bis (max_depth=3, max_features=None, min_samples_leaf=1, 150 árboles) para aislar el
efecto de los datos; CV-5 estratificada × 10 repeticiones, SEED=42.

  A. Referencia: S3, n=80 expuestos.
  B. Sin la población PENSUM 603 (ingreso por homologación al plan 2018): n=74.
  C. «Composición 2018» del primer semestre: prom_sem1 recalculado SOLO con los cursos
     que en el plan 2018 siguen siendo de primer semestre (sale Álgebra Lineal, que pasa
     a 2.º). Simula cómo se vería la variable dominante para una cohorte del plan nuevo.
       C1 · el modelo entrenado con prom_sem1 original predice con la variable recompuesta
            (transferencia sin reentrenar)
       C2 · el modelo se reentrena con la variable recompuesta

Salida: src/cambio_plan_sensibilidad.csv
"""
import os, sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import cargar_datos, OBS_VALIDAS
from equivalencias import normalizar_materias
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import average_precision_score, roc_auc_score

SEED, NREP = 42, 10
SRC = os.path.dirname(os.path.abspath(__file__))
S3 = ['prom_sem1', 'sin_primer_semestre', 'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat']


def rf():
    return RandomForestClassifier(n_estimators=150, max_depth=3, max_features=None,
                                  min_samples_leaf=1, random_state=SEED, n_jobs=-1)


def cv(X, y, X_pred=None):
    ap, au = [], []
    for r in range(NREP):
        p = np.zeros(len(y))
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED + r).split(X, y):
            m = rf().fit(X[tr], y[tr])
            p[te] = m.predict_proba((X if X_pred is None else X_pred)[te])[:, 1]
        ap.append(average_precision_score(y, p)); au.append(roc_auc_score(y, p))
    return np.mean(ap), np.std(ap), np.mean(au)


def prom_sem1_composicion_2018(mat):
    m = normalizar_materias(mat)
    m = m[m['OBSERVACION'].astype(str).str.upper().isin(OBS_VALIDAS) & m['DEFINITIVA'].notna()]
    m = m[m['PERIODO_INSCRIPCION'].astype(str) == m['COHORTE'].astype(str)]
    m = m[m['SEMESTRE_CANONICO'] == 1]
    m = m.assign(num=m['DEFINITIVA'] * m['CREDITOS'])
    g = m.groupby('CODIGO_INST').agg(num=('num', 'sum'), cr=('CREDITOS', 'sum'))
    return (g['num'] / g['cr']).rename('prom_sem1_c2018')


def main():
    df = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'), dtype={'CODIGO_INST': str})
    pc = pd.read_excel(os.path.join(os.path.dirname(SRC), 'Datos', 'PROMEDIOS_DE_CARRERA.xlsx'))
    df['pensum'] = df['CODIGO_INST'].map(pc.assign(c=pc.CODIGO_INST.astype(str)).set_index('c')['PENSUM'])
    _, mat, *_ = cargar_datos()
    c18 = prom_sem1_composicion_2018(mat); c18.index = c18.index.astype(str)
    df['prom_sem1_c2018'] = df['CODIGO_INST'].map(c18)
    df['prom_sem1_c2018'] = df['prom_sem1_c2018'].fillna(df['prom_sem1'])  # sin 1.er semestre: igual que antes
    e = df[df['tiene_actividad_academica'] == 1].copy()
    y = e['bajo_rendimiento_art19'].astype(int).values
    filas = []

    def fila(nombre, n, pos, ap, sd, au, nota=''):
        filas.append({'escenario': nombre, 'n': n, 'positivos': pos,
                      'linea_base': round(pos / n, 4), 'AUC_PR': round(ap, 4), 'sd': round(sd, 4),
                      'AUC_ROC': round(au, 4), 'lift': round(ap / (pos / n), 2), 'nota': nota})

    X = e[S3].values
    fila('A · Referencia S3 (n=80)', len(y), int(y.sum()), *cv(X, y), 'hiperparámetros fijos (moda I-3 bis)')
    s = e[e['pensum'] == 602]; ys = s['bajo_rendimiento_art19'].astype(int).values
    fila('B · Sin ingreso por homologación (PENSUM 603)', len(ys), int(ys.sum()), *cv(s[S3].values, ys),
         'sin_primer_semestre queda constante = 0')
    Xc = e[['prom_sem1_c2018'] + S3[1:]].values
    fila('C1 · Composición 2018 sin reentrenar', len(y), int(y.sum()), *cv(X, y, X_pred=Xc),
         'entrena con prom_sem1, predice con la variable recompuesta')
    fila('C2 · Composición 2018 reentrenado', len(y), int(y.sum()), *cv(Xc, y))
    r = np.corrcoef(e['prom_sem1'], e['prom_sem1_c2018'])[0, 1]
    dif = (e['prom_sem1_c2018'] - e['prom_sem1'])
    out = pd.DataFrame(filas)
    out.to_csv(os.path.join(SRC, 'cambio_plan_sensibilidad.csv'), index=False)
    print(out.to_string(index=False))
    print(f'\ncorr(prom_sem1, composición 2018) = {r:.3f} · desplazamiento medio = {dif.mean():+.3f} '
          f'(sd {dif.std():.3f}) · estudiantes con cambio > 0,1: {(dif.abs() > 0.1).sum()}')
    print('\nPENSUM × sin_primer_semestre:\n', pd.crosstab(df['pensum'], df['sin_primer_semestre']))


if __name__ == '__main__':
    main()
