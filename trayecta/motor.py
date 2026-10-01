"""
motor.py — Núcleo de TRAYECTA (software de trayectoria académica, Ing. de Sistemas)

Separa la lógica de la interfaz: todo lo que la app muestra sale de aquí, y aquí solo se
usan los mismos componentes del pipeline de investigación (src/), de modo que la app no
puede «inventar» una regla distinta a la del estudio.

Entradas (formato del extracto SIIF, sin datos nominales):
    materias  CODIGO_INST, COHORTE, PERIODO_INSCRIPCION, CODIGO_MATERIA, MATERIA,
              CREDITOS, DEFINITIVA, OBSERVACION
    ingreso   CODIGO_INST, COHORTE, PMATN, PCRIN, PNATN, PINGN, PCIUN   (SABER 11)

Funciona con cohortes del plan 2011 (602xxx), del plan 2018 (603xxx) o mezcladas: la capa
de equivalencias (src/equivalencias.py, Resolución Académica 036 de 2017) traduce cada
curso a su identidad canónica antes de contar repeticiones o calcular indicadores.
"""
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, 'src')
MODELOS = os.path.join(RAIZ, 'modelos')
sys.path.insert(0, SRC)

from equivalencias import normalizar_materias, validar as validar_equivalencias  # noqa: E402
from preprocessing import construir_target_art19, OBS_VALIDAS, _periodo_a_orden   # noqa: E402

COLS_MATERIAS = ['CODIGO_INST', 'COHORTE', 'PERIODO_INSCRIPCION', 'CODIGO_MATERIA',
                 'MATERIA', 'CREDITOS', 'DEFINITIVA', 'OBSERVACION']
COLS_INGRESO = ['CODIGO_INST', 'COHORTE', 'PMATN', 'PCRIN', 'PNATN', 'PINGN', 'PCIUN']

# Medianas de la muestra de entrenamiento (df_master_limpio, n=90): imputación idéntica
# a la del pipeline (preprocessing.py) para que una cohorte nueva se trate igual.
MEDIANA_PROM_SEM1 = 3.4
MEDIANAS_ICFES = {'PMATN': 65.0, 'PCRIN': 63.0, 'PNATN': 64.0, 'PINGN': 63.0, 'PCIUN': 63.0}

NIVELES = ('Confirmado', 'Seguimiento', 'Sin alerta')


# ── Modelos ──────────────────────────────────────────────────────────────────
def cargar_modelos():
    art19 = joblib.load(os.path.join(MODELOS, 'alerta_art19.joblib'))
    grad = joblib.load(os.path.join(MODELOS, 'graduacion.joblib'))
    tarjetas = {}
    for n in ('alerta_art19', 'graduacion', 'trayectoria_art20'):
        f = os.path.join(MODELOS, 'tarjetas', f'{n}.json')
        if os.path.exists(f):
            with open(f, encoding='utf-8') as fh:
                tarjetas[n] = json.load(fh)
    return {'art19': art19, 'grad': grad, 'tarjetas': tarjetas}


# ── Validación de la entrada ─────────────────────────────────────────────────
def validar_entrada(mat, ing):
    """Devuelve (errores, avisos, informe_equivalencias)."""
    errores, avisos = [], []
    for nombre, df, cols in (('materias', mat, COLS_MATERIAS), ('ingreso', ing, COLS_INGRESO)):
        falt = [c for c in cols if c not in df.columns]
        if falt:
            errores.append(f'Al archivo de {nombre} le faltan columnas: {", ".join(falt)}')
    if errores:
        return errores, avisos, None
    rep = validar_equivalencias(mat.assign(PROGRAMA='INGENIERIA DE SISTEMAS'))
    if rep['codigos_fuera_de_catalogo']:
        avisos.append(f'{len(rep["codigos_fuera_de_catalogo"])} código(s) de curso no pertenecen a '
                      f'ningún plan conocido de Ing. de Sistemas: '
                      f'{", ".join(rep["codigos_fuera_de_catalogo"][:8])}')
    if rep['discrepancias_de_creditos']:
        avisos.append(f'{len(rep["discrepancias_de_creditos"])} curso(s) con créditos distintos al plan oficial')
    sin_ing = set(mat['CODIGO_INST'].astype(str)) - set(ing['CODIGO_INST'].astype(str))
    if sin_ing:
        avisos.append(f'{len(sin_ing)} estudiante(s) sin registro de SABER 11: se usará el valor típico de la cohorte de referencia')
    return errores, avisos, rep


# ── Situaciones del Reglamento Estudiantil, en lenguaje claro ────────────────
# La interfaz nunca muestra solo el número del artículo: muestra qué ocurrió, qué implica
# y, como referencia secundaria, el artículo que lo establece.
SIN_RESTRICCION = 'Sin restricciones'
PROMEDIO_BAJO = 'Promedio acumulado bajo'
LIMITE_CURSOS = 'Máximo cuatro cursos'
SOLO_REPROBADOS = 'Solo puede inscribir reprobados'
PIERDE = 'Pierde la calidad de estudiante'
SITUACIONES = {   # orden de menor a mayor gravedad
    SIN_RESTRICCION: {
        'que_paso': 'No se activó ninguna condición del Reglamento Estudiantil en este semestre.',
        'implica': 'Puede matricularse con normalidad.',
        'fundamento': ''},
    PROMEDIO_BAJO: {
        'que_paso': 'Su promedio acumulado de carrera quedó por debajo de 3,0.',
        'implica': 'Todavía no tiene restricciones, pero si además reprueba todos los cursos de un semestre, '
                   'pierde la calidad de estudiante. Conviene acompañarlo desde ahora.',
        'fundamento': 'Reglamento Estudiantil, artículo 19'},
    LIMITE_CURSOS: {
        'que_paso': 'Reprobó un curso que ya había reprobado antes (segunda vez o más).',
        'implica': 'En el semestre siguiente puede inscribir como máximo cuatro cursos, dando prioridad a los '
                   'que reprobó.',
        'fundamento': 'Reglamento Estudiantil, artículo 21'},
    SOLO_REPROBADOS: {
        'que_paso': 'Reprobó más de la mitad de los créditos que cursó en el semestre.',
        'implica': 'En el semestre siguiente solo puede inscribir los cursos que reprobó, y debe remitirse al '
                   'programa de acompañamiento académico.',
        'fundamento': 'Reglamento Estudiantil, artículos 20 y 23'},
    PIERDE: {
        'que_paso': 'Reprobó todos los cursos del semestre teniendo un promedio acumulado inferior a 3,0, o '
                    'reprobó el mismo curso por cuarta vez.',
        'implica': 'Deja de ser estudiante del programa por bajo rendimiento. Puede solicitar reintegro en las '
                   'condiciones que fija el reglamento.',
        'fundamento': 'Reglamento Estudiantil, artículo 19'},
}

# Nombres legibles para las tablas y archivos que descarga el usuario
COLUMNAS_LEGIBLES = {
    'CODIGO_INST': 'Código', 'COHORTE': 'Cohorte', 'nivel_alerta': 'Nivel de alerta',
    'p_art19': 'Puntaje de riesgo académico', 'p_graduacion': 'Probabilidad de graduación',
    'semestres_cursados': 'Semestres cursados', 'situacion_actual': 'Situación en el último semestre',
    'prom_sem1': 'Promedio del primer semestre', 'prom_acumulado': 'Promedio acumulado',
    'art19_observado': 'Ya perdió la calidad de estudiante (1 = sí)',
    'veces_art20': 'Semestres con inscripción limitada a reprobados', 'planes': 'Planes de estudio cursados',
    'ultimo_periodo': 'Último periodo'}


def tabla_legible(est):
    """Resultados por estudiante con encabezados en lenguaje claro (para descargar)."""
    cols = [c for c in COLUMNAS_LEGIBLES if c in est.columns]
    t = est[cols].sort_values('p_art19', ascending=False).rename(columns=COLUMNAS_LEGIBLES)
    return t.round(3)


# ── Trayectoria semestre a semestre ──────────────────────────────────────────
def _txt(o):
    return f'{int(o) // 3}-{int(o) % 3}'


def panel_trayectoria(mat):
    """
    Panel estudiante × periodo REGULAR con indicadores normativos del Reglamento vigente.
    Las notas intersemestrales (-0) se suman al periodo regular siguiente (art. 40 par. 1)
    sin abrir un periodo nuevo. Repeticiones contadas por curso canónico entre planes.
    """
    m = normalizar_materias(mat)
    m['CODIGO_INST'] = m['CODIGO_INST'].astype(str)
    m['OBS'] = m['OBSERVACION'].astype(str).str.strip().str.upper()
    m = m[m['OBS'].isin(OBS_VALIDAS) & m['DEFINITIVA'].notna()].copy()
    if m.empty:
        return pd.DataFrame()
    m['ord'] = m['PERIODO_INSCRIPCION'].map(_periodo_a_orden)
    m['regular'] = m['PERIODO_INSCRIPCION'].astype(str).str.endswith(('-1', '-2'))
    m = m.sort_values(['CODIGO_INST', 'ord'])
    m['ord_reg'] = m['ord'].where(m['regular'])
    m['ord_reg'] = m.groupby('CODIGO_INST')['ord_reg'].transform(lambda s: s.bfill())
    m = m.dropna(subset=['ord_reg'])
    m['reprob'] = (m['DEFINITIVA'] < 3.0).astype(int)
    m['vez'] = m.groupby(['CODIGO_INST', 'CURSO_INTENTOS']).cumcount() + 1
    m['num'] = m['DEFINITIVA'] * m['CREDITOS']
    m['crep'] = m['CREDITOS'] * m['reprob']
    m['rep2'] = ((m['vez'] >= 2) & (m['reprob'] == 1)).astype(int)
    m['rep4'] = ((m['vez'] >= 4) & (m['reprob'] == 1)).astype(int)

    reg = m[m['regular']]
    pr = reg.groupby(['CODIGO_INST', 'ord_reg']).agg(cred_p=('CREDITOS', 'sum'), crep_p=('crep', 'sum'),
                                                     aprobados_p=('reprob', lambda s: int((s == 0).sum())),
                                                     num_p=('num', 'sum'))
    per = m.groupby(['CODIGO_INST', 'ord_reg']).agg(
        creditos=('CREDITOS', 'sum'), cred_reprob=('crep', 'sum'), num=('num', 'sum'),
        n_cursos=('CREDITOS', 'size'), max_vez=('vez', 'max'), rep2=('rep2', 'max'), rep4=('rep4', 'max'),
        plan=('PLAN', lambda s: '/'.join(sorted(set(s.dropna())))))
    per = per.join(pr).reset_index().sort_values(['CODIGO_INST', 'ord_reg'])
    per[['cred_p', 'crep_p', 'aprobados_p', 'num_p']] = per[['cred_p', 'crep_p', 'aprobados_p', 'num_p']].fillna(0)
    g = per.groupby('CODIGO_INST')
    per['semestre'] = g.cumcount() + 1
    per['periodo'] = per['ord_reg'].map(_txt)
    per['creditos_acum'] = g['creditos'].cumsum()
    per['prom_acumulado'] = g['num'].cumsum() / per['creditos_acum']
    per['prom_periodo'] = np.where(per['cred_p'] > 0, per['num_p'] / per['cred_p'].clip(lower=1), np.nan)
    per['pct_reprob_periodo'] = np.where(per['cred_p'] > 0, per['crep_p'] / per['cred_p'].clip(lower=1), 0.0)
    pct_entero = np.floor(per['pct_reprob_periodo'] * 100 + 0.5)          # art. 20 parágrafo
    per['art19'] = (((per['pct_reprob_periodo'] >= 0.999) & (per['prom_acumulado'] < 3.0)) |
                    (per['rep4'] == 1)).astype(int)
    per['art20'] = ((pct_entero > 50) & (per['aprobados_p'] > 0)).astype(int)
    per['art21'] = per['rep2'].astype(int)
    per['situacion'] = np.select(
        [per['art19'] == 1, per['art20'] == 1, per['art21'] == 1, per['prom_acumulado'] < 3.0],
        [PIERDE, SOLO_REPROBADOS, LIMITE_CURSOS, PROMEDIO_BAJO], default=SIN_RESTRICCION)
    return per[['CODIGO_INST', 'semestre', 'periodo', 'plan', 'n_cursos', 'creditos', 'cred_reprob',
                'prom_periodo', 'prom_acumulado', 'pct_reprob_periodo', 'max_vez',
                'art19', 'art20', 'art21', 'situacion']]


# ── Variables del modelo (conjunto S3) ───────────────────────────────────────
def variables_s3(mat, ing):
    m = mat.copy()
    m['CODIGO_INST'] = m['CODIGO_INST'].astype(str)
    m['OBS'] = m['OBSERVACION'].astype(str).str.strip().str.upper()
    v = m[m['OBS'].isin(OBS_VALIDAS) & m['DEFINITIVA'].notna() &
          (m['PERIODO_INSCRIPCION'].astype(str) == m['COHORTE'].astype(str))]
    v = v.assign(num=v['DEFINITIVA'] * v['CREDITOS'])
    s1 = v.groupby('CODIGO_INST').agg(num=('num', 'sum'), cr=('CREDITOS', 'sum'))
    s1 = (s1['num'] / s1['cr']).rename('prom_sem1')
    base = (m.groupby('CODIGO_INST')['COHORTE'].first().astype(str).to_frame()
            .join(s1, how='left'))
    i = ing.copy()
    i['CODIGO_INST'] = i['CODIGO_INST'].astype(str)
    i = i.drop(columns=['COHORTE'], errors='ignore').set_index('CODIGO_INST')
    base = base.join(i[[c for c in MEDIANAS_ICFES if c in i.columns]], how='left')
    for c, med in MEDIANAS_ICFES.items():
        base[c] = pd.to_numeric(base.get(c), errors='coerce').fillna(med)
    base['sin_primer_semestre'] = base['prom_sem1'].isna().astype(int)
    base['prom_sem1'] = base['prom_sem1'].fillna(MEDIANA_PROM_SEM1)
    base['icfes_mat'] = base['PMATN']
    base['icfes_lec'] = base['PCRIN']
    base['icfes_nat'] = base['PNATN']
    base['icfes_total'] = base[list(MEDIANAS_ICFES)].sum(axis=1)
    return base.reset_index()


def nivel_alerta(p, umbrales):
    if p >= umbrales['confirmado']['umbral']:
        return 'Confirmado'
    if p >= umbrales['equilibrado']['umbral']:
        return 'Seguimiento'
    return 'Sin alerta'


# ── Proceso completo de una cohorte ──────────────────────────────────────────
def procesar_cohorte(mat, ing, modelos):
    """Devuelve (estudiantes, panel). Una fila por estudiante con predicción y estado."""
    mat = mat.copy()
    mat['CODIGO_INST'] = mat['CODIGO_INST'].astype(str)
    panel = panel_trayectoria(mat)
    feats = variables_s3(mat, ing)
    a19 = modelos['art19']
    gr = modelos['grad']
    X = feats[a19['features']].values
    feats['p_art19'] = a19['modelo'].predict_proba(X)[:, 1]
    feats['p_graduacion'] = gr['modelo'].predict_proba(feats[gr['features']].values)[:, 1]
    feats['nivel_alerta'] = feats['p_art19'].map(lambda p: nivel_alerta(p, a19['umbrales']))

    obs = construir_target_art19(mat, clave_curso='CODIGO_CANONICO')
    obs['CODIGO_INST'] = obs['CODIGO_INST'].astype(str)
    feats = feats.merge(obs[['CODIGO_INST', 'bajo_rendimiento_art19', 'art19_primer_periodo',
                             'n_periodos_cursados']], on='CODIGO_INST', how='left')
    feats['art19_observado'] = feats['bajo_rendimiento_art19'].fillna(0).astype(int)
    if not panel.empty:
        ult = panel.sort_values('semestre').groupby('CODIGO_INST').tail(1).set_index('CODIGO_INST')
        feats = feats.join(ult[['semestre', 'periodo', 'prom_acumulado', 'situacion', 'plan']]
                           .rename(columns={'semestre': 'semestres_cursados', 'periodo': 'ultimo_periodo',
                                            'situacion': 'situacion_actual', 'plan': 'plan_ultimo'}),
                           on='CODIGO_INST')
        planes = panel.groupby('CODIGO_INST')['plan'].agg(lambda s: '/'.join(sorted(set('/'.join(s).split('/')))))
        feats['planes'] = feats['CODIGO_INST'].map(planes)
        n20 = panel.groupby('CODIGO_INST')['art20'].sum()
        feats['veces_art20'] = feats['CODIGO_INST'].map(n20).fillna(0).astype(int)
    return feats, panel


def leer_csv(archivo):
    """Lee CSV o XLSX con separador , o ; (exportaciones de Excel en español)."""
    nombre = getattr(archivo, 'name', str(archivo))
    if nombre.lower().endswith(('.xlsx', '.xls')):
        return pd.read_excel(archivo)
    df = pd.read_csv(archivo, sep=None, engine='python', encoding='utf-8-sig')
    for c in ('DEFINITIVA', 'PMATN', 'PCRIN', 'PNATN', 'PINGN', 'PCIUN'):
        if c in df.columns and df[c].dtype == object:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '.'), errors='coerce')
    return df
