"""
verificacion_fcbi.py — WP-OE1.1 / paso I-5
Verificación de comprensión de datos para Ing. Electrónica y Biología.

Pregunta rectora: ¿lo aprendido sobre los datos de Ing. de Sistemas (calidad,
huecos, semántica, definición del target) aplica igual a los otros dos programas,
y son mezclables en un modelo único?

Bloques:
  A · Cobertura y llaves por programa
  B · Nulos de las variables del modelo
  C · Target del art. 19 aplicado a los tres programas
  D · EDA comparativo (¿mezclables?)
  E · Viabilidad de cortes longitudinales con la muestra FCBI completa

Uso:  python src/verificacion_fcbi.py
Salidas: Fase 2/08_verificacion_fcbi.md + src/fcbi_*.csv
"""
import os, sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import (NIVEL_EDU_MAP, OBS_VALIDAS, _periodo_a_orden,
                           _es_periodo_regular)

SRC = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(SRC)
DATA = os.path.join(RAIZ, 'Datos')
COHORTES = ['2017-2', '2018-1']
PROGRAMAS = ['INGENIERIA DE SISTEMAS', 'INGENIERIA ELECTRONICA', 'BIOLOGIA']
CORTO = {'INGENIERIA DE SISTEMAS': 'Sistemas',
         'INGENIERIA ELECTRONICA': 'Electrónica',
         'BIOLOGIA': 'Biología'}

VARS_MODELO = ['SEXO', 'NIVEL_ED_PADRE', 'NIVEL_ED_MADRE', 'ANOS_REPITIO',
               'ESTRATO_ACTUAL', 'TIPO_PLANTEL', 'ZONA_LUGAR_RESIDENCIA',
               'INGRESOS', 'SISBEN']


def cargar():
    car = pd.read_excel(os.path.join(DATA, 'caracterización.xlsx'))
    mat = pd.read_excel(os.path.join(DATA, 'detalle_materias_recod.xlsx'))
    he = pd.read_excel(os.path.join(DATA, 'historial_estados_recod.xlsx'))
    pc = pd.read_excel(os.path.join(DATA, 'PROMEDIOS_DE_CARRERA.xlsx'))
    ps = pd.read_excel(os.path.join(DATA, 'promedios_semestre.xlsx'))
    for d in (car, mat, he, pc, ps):
        if 'PROGRAMA' in d.columns:
            d['PROG'] = d['PROGRAMA'].astype(str).str.strip().str.upper()
    car = car[car['PERIODO_INGRESO'].astype(str).str.strip().isin(COHORTES)].copy()
    car['CODIGO_INST'] = car['CODIGO_ESTUDIANTIL']   # la caracterización usa otro nombre de llave
    for nom, d in (('mat', mat), ('he', he), ('pc', pc), ('ps', ps)):
        if 'COHORTE' in d.columns:
            d.drop(d[~d['COHORTE'].astype(str).str.strip().isin(COHORTES)].index,
                   inplace=True)
    return car, mat, he, pc, ps


# ── A · Cobertura y llaves ───────────────────────────────────────────────────
def bloque_a(car, mat, he, pc, ps):
    filas = []
    for p in PROGRAMAS:
        c = car[car.PROG == p]
        ids = set(c['CODIGO_INST'].astype(str))
        filas.append({
            'Programa': CORTO[p],
            'Caracterización': len(c),
            'En historial': len(ids & set(he[he.PROG == p]['CODIGO_INST'].astype(str))),
            'Con notas': len(ids & set(mat[mat.PROG == p]['CODIGO_INST'].astype(str))),
            'Con prom. carrera': len(ids & set(
                pc[(pc.PROG == p) & pc['PROMEDIO_CARRERA'].notna()]['CODIGO_INST'].astype(str))),
            'Con prom. semestre': len(ids & set(ps[ps.PROG == p]['CODIGO_INST'].astype(str))),
        })
    d = pd.DataFrame(filas)
    d['Pérdida hasta prom. carrera'] = d['Caracterización'] - d['Con prom. carrera']
    return d


# ── B · Nulos de las variables del modelo ────────────────────────────────────
def bloque_b(car):
    filas = []
    for v in VARS_MODELO:
        if v not in car.columns:
            continue
        f = {'Variable': v}
        for p in PROGRAMAS:
            c = car[car.PROG == p]
            f[CORTO[p]] = round(c[v].isna().mean(), 3)
        filas.append(f)
    return pd.DataFrame(filas)


# ── C · Target del art. 19 por programa ──────────────────────────────────────
def target_art19(mat, prog):
    m = mat[mat.PROG == prog].copy()
    m['OBS'] = m['OBSERVACION'].astype(str).str.strip().str.upper()
    m['ord'] = m['PERIODO_INSCRIPCION'].map(_periodo_a_orden)
    m['regular'] = m['PERIODO_INSCRIPCION'].map(_es_periodo_regular)
    val = m[m['OBS'].isin(OBS_VALIDAS) & m['DEFINITIVA'].notna()].copy()
    if val.empty:
        return pd.DataFrame()
    val = val.sort_values(['CODIGO_INST', 'ord'])
    val['reprob'] = (val['DEFINITIVA'] < 3.0).astype(int)
    val['vez'] = val.groupby(['CODIGO_INST', 'MATERIA']).cumcount() + 1
    val['num'] = val['DEFINITIVA'] * val['CREDITOS']
    val['crep'] = val['CREDITOS'] * val['reprob']
    per = (val.groupby(['CODIGO_INST', 'ord'])
           .agg(cred=('CREDITOS', 'sum'), crep=('crep', 'sum'), num=('num', 'sum'),
                regular=('regular', 'max')).reset_index()
           .sort_values(['CODIGO_INST', 'ord']))
    per['prom_ac'] = (per.groupby('CODIGO_INST')['num'].cumsum() /
                      per.groupby('CODIGO_INST')['cred'].cumsum())
    per['pct'] = per['crep'] / per['cred']
    r4 = (val[(val['vez'] >= 4) & (val['reprob'] == 1)]
          .groupby(['CODIGO_INST', 'ord']).size().reset_index(name='rep4'))
    per = per.merge(r4, on=['CODIGO_INST', 'ord'], how='left').fillna({'rep4': 0})
    per['evento'] = (((per['pct'] == 1) & (per['prom_ac'] < 3.0) & per['regular']) |
                     (per['rep4'] > 0))
    ev = per[per['evento']].groupby('CODIGO_INST')['ord'].min().rename('ord_ev').reset_index()
    expo = per.groupby('CODIGO_INST').agg(n_periodos=('ord', 'nunique')).reset_index()
    out = expo.merge(ev, on='CODIGO_INST', how='left')
    out['y'] = out['ord_ev'].notna().astype(int)
    return out


def bloque_c(mat, car):
    filas, detalle = [], {}
    for p in PROGRAMAS:
        t = target_art19(mat, p)
        if t.empty:
            continue
        c = car[car.PROG == p]
        ing = (c.set_index(c['CODIGO_INST'].astype(str))['PERIODO_INGRESO']
               .astype(str).str.strip().map(_periodo_a_orden))
        t['cod'] = t['CODIGO_INST'].astype(str)
        t['ord_ing'] = t['cod'].map(ing)
        t['sem_ev'] = t['ord_ev'] - t['ord_ing'] + 1
        detalle[p] = t
        filas.append({
            'Programa': CORTO[p],
            'Expuestos (con notas)': len(t),
            'Positivos art. 19': int(t['y'].sum()),
            'Prevalencia': round(t['y'].mean(), 3),
            'Eventos en sem. 1': int((t['sem_ev'] <= 1).sum()),
            'Eventos en sem. >=2': int((t['sem_ev'] >= 2).sum()),
        })
    return pd.DataFrame(filas), detalle


# ── D · EDA comparativo ──────────────────────────────────────────────────────
def bloque_d(car, pc, he):
    filas = []
    for p in PROGRAMAS:
        c = car[car.PROG == p]
        ids = set(c['CODIGO_INST'].astype(str))
        pr = pc[(pc.PROG == p) & pc['PROMEDIO_CARRERA'].notna()]
        h = he[he.PROG == p].copy()
        h['E'] = h['ESTADO'].astype(str).str.strip().str.upper()
        grad = h[h.E == 'GRADUADO']['CODIGO_INST'].astype(str).nunique()
        icfes = [x for x in ('PUNTAJE_MATEMATICAS', 'PUNTAJE_GLOBAL') if x in c.columns]
        filas.append({
            'Programa': CORTO[p],
            'n': len(c),
            'Mujeres': round((c['SEXO'].astype(str).str.upper().str.startswith('F')).mean(), 3),
            'Estrato medio': round(pd.to_numeric(c['ESTRATO_ACTUAL'], errors='coerce').mean(), 2),
            'Prom. carrera medio': round(pr['PROMEDIO_CARRERA'].mean(), 3),
            'Prom. carrera sd': round(pr['PROMEDIO_CARRERA'].std(), 3),
            'Graduados': grad,
            'Tasa graduación': round(grad / len(ids), 3) if ids else np.nan,
        })
    return pd.DataFrame(filas)


# ── E · Viabilidad de cortes longitudinales con FCBI completa ────────────────
def bloque_e(detalle):
    todo = pd.concat([d.assign(prog=CORTO[p]) for p, d in detalle.items()],
                     ignore_index=True)
    filas = []
    for k in range(1, 9):
        riesgo = todo[(todo['n_periodos'] >= k) &
                      (todo['sem_ev'].isna() | (todo['sem_ev'] > k))]
        ev = int((riesgo['sem_ev'] > k).sum())
        filas.append({'Corte (semestre)': k, 'En riesgo': len(riesgo),
                      'Eventos futuros': ev,
                      'Modelable (n>=60 y ev>=15)': 'Sí' if (len(riesgo) >= 60 and ev >= 15) else 'No'})
    return pd.DataFrame(filas), todo


def main():
    car, mat, he, pc, ps = cargar()
    print(f'Caracterización (cohortes {COHORTES}): {len(car)} estudiantes\n')

    print('═══ A · COBERTURA Y LLAVES POR PROGRAMA ═══')
    a = bloque_a(car, mat, he, pc, ps); print(a.to_string(index=False))
    a.to_csv(os.path.join(SRC, 'fcbi_cobertura.csv'), index=False)

    print('\n═══ B · NULOS DE LAS VARIABLES DEL MODELO ═══')
    b = bloque_b(car); print(b.to_string(index=False))
    b.to_csv(os.path.join(SRC, 'fcbi_nulos.csv'), index=False)

    print('\n═══ C · TARGET DEL ART. 19 POR PROGRAMA ═══')
    c, detalle = bloque_c(mat, car); print(c.to_string(index=False))
    c.to_csv(os.path.join(SRC, 'fcbi_target_art19.csv'), index=False)

    print('\n═══ D · EDA COMPARATIVO — ¿son mezclables? ═══')
    dd = bloque_d(car, pc, he); print(dd.to_string(index=False))
    dd.to_csv(os.path.join(SRC, 'fcbi_eda_comparativo.csv'), index=False)

    print('\n═══ E · VIABILIDAD DE CORTES LONGITUDINALES (FCBI completa) ═══')
    e, todo = bloque_e(detalle); print(e.to_string(index=False))
    e.to_csv(os.path.join(SRC, 'fcbi_viabilidad_cortes.csv'), index=False)
    todo.to_csv(os.path.join(SRC, 'fcbi_target_detalle.csv'), index=False)

    print('\n[OK] Salidas en src/: fcbi_cobertura.csv, fcbi_nulos.csv,')
    print('     fcbi_target_art19.csv, fcbi_eda_comparativo.csv,')
    print('     fcbi_viabilidad_cortes.csv, fcbi_target_detalle.csv')


if __name__ == '__main__':
    main()
