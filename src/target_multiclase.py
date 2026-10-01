"""
target_multiclase.py — WP-OE1.3 / P1 · Variable objetivo de trayectoria

Construye el target comprometido en la propuesta de grado: el **estado académico
al final del seguimiento**, con salidas probabilísticas por estudiante.

La propuesta enuncia cuatro clases: graduado · activo · desertor · rezagado.
Este script las construye, **aplica la regla de viabilidad pre-registrada en
RC-008** y documenta el resultado sin forzarlo:

    "Si la clase 'rezagado' queda con menos de 25 estudiantes o menos de 5 por
     pliegue, el target colapsa a 3 clases y el rezago pasa a indicador continuo
     secundario."

Definiciones (pre-registradas antes de ver los resultados de modelado):

    GRADUADO  estado final GRADUADO en el historial
    ACTIVO    último estado MATRICULADO y reciente (>= 2024-1)
    DESERTOR  resto: dejó de estudiar sin graduarse
    REZAGADO  activo que excede el tiempo nominal del plan (10 semestres)

⚠ CENSURA A LA DERECHA: los estudiantes ACTIVOS no tienen desenlace conocido —
podrían graduarse o desertar después del cierre de la ventana (2026-1). Su clase
describe su **estado al final del seguimiento**, que es exactamente lo que la
propuesta pide, pero no es un desenlace definitivo. Se marca con `censurado=1`.

Uso:  python src/target_multiclase.py
Salidas: src/df_master_fcbi_multiclase.csv · src/multiclase_distribucion.csv
"""
import os, sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import OBS_VALIDAS, _periodo_a_orden

SRC = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(SRC), 'Datos')
PROGRAMAS = ['INGENIERIA DE SISTEMAS', 'INGENIERIA ELECTRONICA', 'BIOLOGIA']

UMBRAL_RECIENTE = '2024-1'      # criterio de recencia (RC-002)
SEMESTRES_PLAN = 10             # duración nominal del plan de estudios
MIN_CLASE = 25                  # regla RC-008
MIN_POR_PLIEGUE = 5             # regla RC-008
N_PLIEGUES = 5


def construir():
    he = pd.read_excel(os.path.join(DATA, 'historial_estados_recod.xlsx'))
    mat = pd.read_excel(os.path.join(DATA, 'detalle_materias_recod.xlsx'))
    for d in (he, mat):
        d['PROG'] = d['PROGRAMA'].astype(str).str.strip().str.upper()
        d['cod'] = d['CODIGO_INST'].astype(str)
    he = he[he.PROG.isin(PROGRAMAS)].copy()
    mat = mat[mat.PROG.isin(PROGRAMAS)].copy()

    he['E'] = he['ESTADO'].astype(str).str.strip().str.upper()
    he['ord'] = he['PERIODO_ESTADO'].map(_periodo_a_orden)
    ult = he.sort_values('ord').groupby('cod').tail(1)[['cod', 'E', 'ord', 'PROG']].copy()
    ult['reciente'] = (ult['ord'] >= _periodo_a_orden(UMBRAL_RECIENTE)).astype(int)
    grad = set(he[he.E == 'GRADUADO']['cod'])

    # Progreso académico
    v = mat[mat['OBSERVACION'].astype(str).str.strip().str.upper().isin(OBS_VALIDAS)
            & mat['DEFINITIVA'].notna()].copy()
    prog = (v.assign(ap=np.where(v['DEFINITIVA'] >= 3.0, v['CREDITOS'], 0))
            .groupby('cod')
            .agg(creditos_aprobados=('ap', 'sum'),
                 periodos_cursados=('PERIODO_INSCRIPCION', 'nunique'))
            .reset_index())
    d = ult.merge(prog, on='cod', how='left').fillna(
        {'creditos_aprobados': 0, 'periodos_cursados': 0})

    # ── Clases ──────────────────────────────────────────────────────────────
    es_grad = d['cod'].isin(grad)
    es_activo = (d['E'] == 'MATRICULADO') & (d['reciente'] == 1) & ~es_grad
    d['clase_3'] = np.select([es_grad, es_activo], ['GRADUADO', 'ACTIVO'],
                             default='DESERTOR')

    # Rezago: excede el tiempo nominal del plan
    d['periodos_sobre_plan'] = d['periodos_cursados'] - SEMESTRES_PLAN
    d['rezagado'] = ((d['clase_3'] == 'ACTIVO') &
                     (d['periodos_cursados'] > SEMESTRES_PLAN)).astype(int)
    d['clase_4'] = np.where(d['rezagado'] == 1, 'REZAGADO', d['clase_3'])

    # Censura a la derecha: los activos no tienen desenlace definitivo
    d['censurado'] = (d['clase_3'] == 'ACTIVO').astype(int)
    return d


def viabilidad(d):
    """Aplica la regla pre-registrada de RC-008 sobre la clase minoritaria."""
    filas = []
    for col, etiqueta in [('clase_4', '4 clases (propuesta)'),
                          ('clase_3', '3 clases (colapsada)')]:
        vc = d[col].value_counts()
        minoritaria = vc.idxmin()
        n_min = int(vc.min())
        por_pliegue = n_min / N_PLIEGUES
        ok = (n_min >= MIN_CLASE) and (por_pliegue >= MIN_POR_PLIEGUE)
        filas.append({'target': etiqueta, 'clases': len(vc),
                      'clase_minoritaria': minoritaria, 'n_minoritaria': n_min,
                      'por_pliegue': round(por_pliegue, 1),
                      'viable_RC008': 'Sí' if ok else 'No'})
    return pd.DataFrame(filas)


def main():
    d = construir()
    base = pd.read_csv(os.path.join(SRC, 'df_master_fcbi.csv'))
    base['cod'] = base['CODIGO_INST'].astype(str)
    j = base.merge(d.drop(columns=['PROG']), on='cod', how='left')
    print(f'Población de modelado FCBI: {len(j)} estudiantes\n')

    print('═══ DISTRIBUCIÓN DE CLASES ═══')
    for col, et in [('clase_4', '4 clases (como la propone la propuesta)'),
                    ('clase_3', '3 clases')]:
        print(f'\n{et}:')
        vc = j[col].value_counts()
        for k, n in vc.items():
            print(f'   {k:12s} {n:4d}  ({n/len(j):5.1%})')

    print('\n═══ POR PROGRAMA (3 clases) ═══')
    ct = pd.crosstab(j['programa_corto'], j['clase_3'])
    print(ct.to_string())

    print('\n═══ REGLA DE VIABILIDAD PRE-REGISTRADA (RC-008) ═══')
    vb = viabilidad(j)
    print(vb.to_string(index=False))
    print(f'\n   Criterio: clase minoritaria >= {MIN_CLASE} estudiantes '
          f'Y >= {MIN_POR_PLIEGUE} por pliegue (CV-{N_PLIEGUES})')

    print('\n═══ INDICADOR CONTINUO DE REZAGO ═══')
    act = j[j['clase_3'] == 'ACTIVO']
    print(f'   Activos: {len(act)} · periodos cursados mediana '
          f'{act["periodos_cursados"].median():.0f} (plan nominal {SEMESTRES_PLAN})')
    print(f'   De ellos, por encima del plan: {int(act["rezagado"].sum())} '
          f'({act["rezagado"].mean():.0%})')
    g = j[j['clase_3'] == 'GRADUADO']
    print(f'   Graduados: periodos mediana {g["periodos_cursados"].median():.0f} · '
          f'máximo {g["periodos_cursados"].max():.0f}')

    print('\n═══ CENSURA ═══')
    cen = j[j['censurado'] == 1]
    print(f'   {len(cen)} estudiantes censurados (activos sin desenlace definitivo)')
    print('   por programa:', dict(cen['programa_corto'].value_counts()))

    j.to_csv(os.path.join(SRC, 'df_master_fcbi_multiclase.csv'), index=False)
    vb.to_csv(os.path.join(SRC, 'multiclase_distribucion.csv'), index=False)
    print('\n[OK] src/df_master_fcbi_multiclase.csv · src/multiclase_distribucion.csv')


if __name__ == '__main__':
    main()
