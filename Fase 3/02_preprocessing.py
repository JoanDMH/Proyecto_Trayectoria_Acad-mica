"""
preprocessing.py
Fase 3 CRISP-DM — Preparación de datos
Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

Correcciones aplicadas:
- Población base: 90 estudiantes (cruce car ∩ historial con actividad)
- 19 features seleccionadas (incluye indicador sin_primer_semestre de I-2)
- Insumos: detalle_materias_recod.xlsx e historial_estados_recod.xlsx (generados
  desde los originales por src/recodificacion.py)
- OBSERVACION validas para notas: N, C (curso intersemestral, INCLUIDO jul-2026), H.
  Excluidas: O/V/I (notas externas), A/P/R/E (sin nota)
- Promedio materias: solo notas >= 3.0, última nota por estudiante-materia
- Materias críticas corregidas con índice compuesto
- Mapeo NIVEL_ED sin código 6 (salto 5 → 7)
- Corrección auditoría H-3 / I-2 (septiembre 2026): sustitución de imputación simple
  de prom_sem1 por indicador explícito `sin_primer_semestre` + imputación.
"""

import os
import pandas as pd
import numpy as np

# ── Configuración ────────────────────────────────────────────────────────────
PROG     = 'INGENIERIA DE SISTEMAS'   # por defecto; parametrizable desde cargar_datos(programas=...)
PROGRAMAS_FCBI = ['INGENIERIA DE SISTEMAS', 'INGENIERIA ELECTRONICA', 'BIOLOGIA']
COHORTES = ['2017-2', '2018-1']
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Datos')

# Mapeo NIVEL_ED (códigos DANE, sin código 6)
NIVEL_EDU_MAP = {
    1: 0,   # Analfabeta
    2: 1,   # Primaria incompleta
    3: 2,   # Primaria completa
    4: 3,   # Bachillerato incompleto
    5: 4,   # Bachillerato completo
    7: 5,   # Técnico incompleto
    8: 6,   # Técnico completo
    9: 7,   # Tecnólogo incompleto
    10: 8,  # Tecnólogo completo
    11: 9,  # Universitario incompleto
    12: 10, # Universitario completo
    13: 11, # Posgrado incompleto
    14: 12, # Posgrado completo
}

NIVEL_EDU_LABELS = {
    0: 'Analfabeta',
    1: 'Primaria incompleta',
    2: 'Primaria completa',
    3: 'Bachillerato incompleto',
    4: 'Bachillerato completo',
    5: 'Técnico incompleto',
    6: 'Técnico completo',
    7: 'Tecnólogo incompleto',
    8: 'Tecnólogo completo',
    9: 'Universitario incompleto',
    10: 'Universitario completo',
    11: 'Posgrado incompleto',
    12: 'Posgrado completo',
}

# Materias críticas (top 5 por índice compuesto, post-corrección)
MATERIAS_CRITICAS = [
    'MATEMATICAS II',
    'FISICA I',
    'ALGEBRA LINEAL',
    'MATEMATICAS I',
    'FUNDAMENTOS DE PROGRAMACION',
]

# OBSERVACION validas para notas (diccionario corregido jul-2026):
# N=Normal, C=Curso intersemestral (nota real, puede reprobarse), H=Habilitada.
# A/P/R/E no tienen nota; O/V/I son notas externas.
OBS_VALIDAS = {'N', 'C', 'H'}


# ── Carga y filtrado ─────────────────────────────────────────────────────────

def cargar_datos(programas=None):
    """
    Carga los 5 datasets y filtra por cohortes/programa, excluyendo nulos de
    promedio acumulado.

    `programas`: lista de programas a incluir. Por defecto solo Ing. de Sistemas
    (comportamiento histórico, del que depende `app.py`). Pasar
    `PROGRAMAS_FCBI` para construir el conjunto de los tres programas del
    alcance (WP-OE1.1 / RC-036).
    """
    progs = [PROG] if programas is None else list(programas)
    df_car = pd.read_excel(os.path.join(DATA_DIR, 'caracterización.xlsx'))
    # Archivos RECODIFICADOS (generados por src/recodificacion.py desde los originales)
    df_mat = pd.read_excel(os.path.join(DATA_DIR, 'detalle_materias_recod.xlsx'))
    df_he  = pd.read_excel(os.path.join(DATA_DIR, 'historial_estados_recod.xlsx'))
    df_pc  = pd.read_excel(os.path.join(DATA_DIR, 'PROMEDIOS_DE_CARRERA.xlsx'))
    df_ps  = pd.read_excel(os.path.join(DATA_DIR, 'promedios_semestre.xlsx'))

    ing_car = df_car[
        (df_car['PROGRAMA'].str.strip().str.upper().isin(progs)) &
        (df_car['PERIODO_INGRESO'].astype(str).str.strip().isin(COHORTES))
    ].copy().reset_index(drop=True)

    for df in [df_mat, df_he, df_pc, df_ps]:
        df['PROGRAMA'] = df['PROGRAMA'].str.strip().str.upper()
        df['COHORTE']  = df['COHORTE'].astype(str).str.strip()

    ing_mat = df_mat[(df_mat['PROGRAMA'].isin(progs)) & (df_mat['COHORTE'].isin(COHORTES))].copy().reset_index(drop=True)
    ing_he  = df_he [(df_he ['PROGRAMA'].isin(progs)) & (df_he ['COHORTE'].isin(COHORTES))].copy().reset_index(drop=True)
    ing_pc  = df_pc [(df_pc ['PROGRAMA'].isin(progs)) & (df_pc ['COHORTE'].isin(COHORTES))].copy().reset_index(drop=True)
    ing_ps  = df_ps [(df_ps ['PROGRAMA'].isin(progs)) & (df_ps ['COHORTE'].isin(COHORTES))].copy().reset_index(drop=True)

    # Población base inicial: estudiantes presentes en caracterización E historial
    cod_car = set(ing_car['CODIGO_ESTUDIANTIL'].astype(str))
    cod_he  = set(ing_he['CODIGO_INST'].astype(str))
    poblacion_base = cod_car & cod_he

    # Exclusión metodológica: Estudiantes con promedio acumulado nulo (NaN) en PROMEDIOS_DE_CARRERA.xlsx
    estudiantes_con_promedio = set(ing_pc[ing_pc['PROMEDIO_CARRERA'].notna()]['CODIGO_INST'].astype(str))
    poblacion_base = poblacion_base & estudiantes_con_promedio

    # Filtrar todas las tablas a la población base depurada (89 estudiantes)
    ing_car = ing_car[ing_car['CODIGO_ESTUDIANTIL'].astype(str).isin(poblacion_base)].copy()
    ing_mat = ing_mat[ing_mat['CODIGO_INST'].astype(str).isin(poblacion_base)].copy()
    ing_he  = ing_he [ing_he ['CODIGO_INST'].astype(str).isin(poblacion_base)].copy()
    ing_pc  = ing_pc [ing_pc ['CODIGO_INST'].astype(str).isin(poblacion_base)].copy()
    ing_ps  = ing_ps [ing_ps ['CODIGO_INST'].astype(str).isin(poblacion_base)].copy()

    return ing_car, ing_mat, ing_he, ing_pc, ing_ps, poblacion_base


# ── Features de estudiante ───────────────────────────────────────────────────

def construir_features_estudiante(ing_car, ing_he, ing_pc, ing_ps):
    """
    Construye el dataset nivel-estudiante con 18 features y targets.
    Retorna (df_master, feature_cols).
    """
    df = ing_car[[
        'CODIGO_ESTUDIANTIL',
        'SEXO', 'NIVEL_ED_PADRE', 'NIVEL_ED_MADRE',
        'ANOS_REPITIO', 'ESTRATO_ACTUAL', 'INGRESOS',
        'TIPO_PLANTEL', 'ZONA_LUGAR_RESIDENCIA',
        'SISBEN', 'URBANA_SISBEN', 'RURAL_SISBEN',
        'PMATN', 'PINGN', 'PCRIN', 'PCIUN', 'PNATN',
        'VIVE_CON', 'SITUACION_PADRES',
    ]].copy().rename(columns={'CODIGO_ESTUDIANTIL': 'CODIGO_INST'})

    # Cohorte
    df['COHORTE'] = ing_car['PERIODO_INGRESO'].astype(str).str.strip().values
    df['cohorte_encoded'] = (df['COHORTE'] == '2018-1').astype(int)

    # 1. sexo: 1=M, 0=F
    df['sexo'] = (df['SEXO'].str.strip().str.upper() == 'M').astype(int)

    # 2-4. nivel educativo padres (ordinal)
    df['nivel_edu_padre'] = pd.to_numeric(df['NIVEL_ED_PADRE'], errors='coerce').map(NIVEL_EDU_MAP).fillna(0).astype(int)
    df['nivel_edu_madre'] = pd.to_numeric(df['NIVEL_ED_MADRE'], errors='coerce').map(NIVEL_EDU_MAP).fillna(0).astype(int)
    df['nivel_edu_max_padres'] = df[['nivel_edu_padre', 'nivel_edu_madre']].max(axis=1)

    # 5. repitencia escolar
    df['repitio_escolar'] = (df['ANOS_REPITIO'].astype(str).str.strip().str.upper() == 'S').astype(int)

    # 6. estrato socioeconómico
    df['estrato'] = pd.to_numeric(df['ESTRATO_ACTUAL'], errors='coerce').fillna(2).astype(int)

    # 7-11. componentes Saber 11
    for col_raw, col_new in [('PMATN','icfes_mat'), ('PINGN','icfes_ing'),
                              ('PCRIN','icfes_lec'), ('PCIUN','icfes_soc'), ('PNATN','icfes_nat')]:
        med = pd.to_numeric(df[col_raw], errors='coerce').median()
        df[col_new] = pd.to_numeric(df[col_raw], errors='coerce').fillna(med)
    df['icfes_total'] = df[['icfes_mat','icfes_ing','icfes_lec','icfes_soc','icfes_nat']].sum(axis=1)

    # 12. tipo de plantel: 0=público, 1=privado
    df['tipo_plantel'] = (df['TIPO_PLANTEL'].str.strip().str.upper() == 'P').astype(int)

    # 13. zona residencia: 0=urbana, 1=rural
    df['zona_rural'] = (df['ZONA_LUGAR_RESIDENCIA'].str.strip().str.upper() == 'R').astype(int)

    # 14. ingresos del hogar (log para reducir asimetría)
    df['log_ingresos'] = np.log1p(pd.to_numeric(df['INGRESOS'], errors='coerce').fillna(df['INGRESOS'].median()))

    # 15. nivel SISBEN consolidado (0=sin SISBEN, 1-6 según nivel)
    def sisben_nivel(row):
        if str(row['SISBEN']).strip().upper() != 'S':
            return 0
        tipo = str(row['PUNTAJE_SISBEN']).strip().upper() if pd.notna(row.get('PUNTAJE_SISBEN')) else ''
        if tipo == 'U':
            return int(pd.to_numeric(row.get('URBANA_SISBEN', 1), errors='coerce') or 1)
        elif tipo == 'R':
            return int(pd.to_numeric(row.get('RURAL_SISBEN', 1), errors='coerce') or 1)
        return 1

    # Agregar PUNTAJE_SISBEN al df temporalmente
    df['PUNTAJE_SISBEN'] = ing_car['PUNTAJE_SISBEN'].values if 'PUNTAJE_SISBEN' in ing_car.columns else 'U'
    df['sisben_nivel'] = df.apply(sisben_nivel, axis=1)

    # 16. con quién vive (categórico 1-5)
    df['vive_con'] = pd.to_numeric(df['VIVE_CON'], errors='coerce').fillna(1).astype(int)

    # 17. situación de los padres (categórico 1-3)
    df['situacion_padres'] = pd.to_numeric(df['SITUACION_PADRES'], errors='coerce').fillna(1).astype(int)

    # ── Promedio primer semestre (alineado a la cohorte) ──────────────────────
    # Mapeamos prom_sem1 según la cohorte de ingreso de cada estudiante.
    # Corrección H-3 / I-2 (Auditoría 2026-09): 16 estudiantes carecen de promedio de primer semestre.
    # Se reemplaza la imputación simple por mediana por un indicador explícito `sin_primer_semestre`
    # + imputación de la mediana en prom_sem1 para preservar la muestra y capturar la ausencia como señal.
    prom_s1 = ing_ps[['CODIGO_INST', 'PERIODO_INSCRIPCION', 'PROMEDIO_SEMESTRE']].copy()
    prom_s1.columns = ['CODIGO_INST', 'COHORTE', 'prom_sem1']
    
    df = df.merge(prom_s1, on=['CODIGO_INST', 'COHORTE'], how='left')
    df['sin_primer_semestre'] = df['prom_sem1'].isna().astype(int)
    mediana_s1 = df['prom_sem1'].median()
    df['prom_sem1'] = df['prom_sem1'].fillna(mediana_s1)

    # Fuente directa del SIIF para `sin_primer_semestre` (RC-047): PENSUM (plan en el que
    # está matriculado) y HOMOLOGACION. En Ing. de Sistemas el indicador coincide 1:1 con
    # PENSUM 603 (ingreso por homologación al plan 2018). Se incorporan como columnas
    # informativas (NO son variables del modelo) y se reporta cualquier discrepancia.
    df = _agregar_pensum_homologacion(df, ing_pc)

    # ── Promedio acumulado de carrera ─────────────────────────────────────────
    df = df.merge(ing_pc[['CODIGO_INST', 'PROMEDIO_CARRERA']], on='CODIGO_INST', how='left')

    # ── Targets ──────────────────────────────────────────────────────────────
    ing_he['estado_limpio'] = ing_he['ESTADO'].str.strip().str.upper()
    graduados = set(ing_he[ing_he['estado_limpio'] == 'GRADUADO']['CODIGO_INST'].astype(str))

    df['graduado']         = df['CODIGO_INST'].astype(str).isin(graduados).astype(int)

    # ⚠️ OBSOLETO (RC-012 / RC-017): `rendimiento_bajo` = PROMEDIO_CARRERA < 3.0 quedó
    # DESCARTADO por tautológico — el promedio de carrera incluye el primer semestre,
    # que es su propio predictor dominante. Sin `prom_sem1` el modelo cae a AUC 0.483
    # (azar) y al excluir desertores tempranos cae de 0.761 a 0.546.
    # Se conserva SOLO como referencia histórica para comparaciones antes/después.
    # NO USAR para entrenar: el target vigente es `bajo_rendimiento_art19`
    # (ver construir_target_art19 y MARCO_NORMATIVO.md §3).
    df['rendimiento_bajo'] = (df['PROMEDIO_CARRERA'] < 3.0).astype(int)

    # ── Columnas finales ──────────────────────────────────────────────────────
    feature_cols = [
        # Socioeconómicas / familiares
        'sexo', 'nivel_edu_padre', 'nivel_edu_madre', 'nivel_edu_max_padres',
        'repitio_escolar', 'estrato', 'log_ingresos', 'sisben_nivel',
        'tipo_plantel', 'zona_rural', 'vive_con', 'situacion_padres',
        # Académicas de entrada
        'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat',
        # Cohorte
        'cohorte_encoded',
        # Rendimiento primer semestre (con indicador de imputación H-3/I-2)
        'prom_sem1',
        'sin_primer_semestre',
    ]

    info_cols   = ['CODIGO_INST', 'COHORTE', 'SEXO', 'NIVEL_ED_PADRE', 'NIVEL_ED_MADRE',
                   'ANOS_REPITIO', 'ESTRATO_ACTUAL', 'TIPO_PLANTEL', 'ZONA_LUGAR_RESIDENCIA',
                   'pensum', 'homologacion']
    target_cols = ['graduado', 'rendimiento_bajo', 'PROMEDIO_CARRERA']

    df_out = df[info_cols + feature_cols + target_cols].copy()
    return df_out, feature_cols


def _agregar_pensum_homologacion(df, ing_pc):
    """Añade `pensum` (PROMEDIOS_DE_CARRERA) y `homologacion` (homologaciones.xlsx)."""
    clave = df['CODIGO_INST'].astype(str)
    pen = ing_pc.assign(_c=ing_pc['CODIGO_INST'].astype(str)).drop_duplicates('_c').set_index('_c')['PENSUM']
    df['pensum'] = clave.map(pen).values
    f = os.path.join(DATA_DIR, 'homologaciones.xlsx')
    if os.path.exists(f):
        h = pd.read_excel(f)
        h = h.assign(_c=h['CODIGO_INST'].astype(str)).drop_duplicates('_c').set_index('_c')['HOMOLOGACION']
        df['homologacion'] = clave.map(h).values
    else:
        df['homologacion'] = np.nan
    # Plan «regular» de la cohorte = el más frecuente; quien está en otro plan sin
    # primer semestre calificado es ingreso por homologación.
    plan_regular = df['pensum'].mode().iloc[0] if df['pensum'].notna().any() else None
    otro_plan = (df['pensum'] != plan_regular) & df['pensum'].notna()
    disc = int((otro_plan.astype(int) != df['sin_primer_semestre']).sum())
    if disc:
        print(f'  [aviso] sin_primer_semestre difiere de PENSUM≠{plan_regular} en {disc} estudiante(s)')
    return df


# ── Target normativo: artículo 19 del Reglamento Estudiantil vigente ─────────

def _periodo_a_orden(p):
    """
    '2019-2' -> entero ordenable, sin colisiones.

    Sufijos presentes en los datos: -0 (curso intersemestral), -1 y -2 (periodos
    académicos regulares). El intersemestral se ordena al INICIO del año, antes
    del primer periodo regular.

    Corrección I-2b: la versión anterior (`anio*2 + (0 si sem=='1' else 1)`)
    colapsaba -0 y -2 en el mismo valor, mezclando 133 registros intersemestrales
    con el segundo periodo del mismo año.
    """
    anio, sem = str(p).strip().split('-')
    return int(anio) * 3 + {'0': 0, '1': 1, '2': 2}[sem]


def _es_periodo_regular(p):
    """True si es un periodo académico regular (-1 o -2), False si es intersemestral (-0)."""
    return str(p).strip().split('-')[1] in ('1', '2')


def construir_target_art19(ing_mat, verbose=False, clave_curso='MATERIA'):
    """
    Variable objetivo de bajo rendimiento según el ART. 19 del Reglamento Estudiantil
    vigente (aprobado dic-2021, rige desde 2022-1). Decisión RC-017 / paso I-1.

        Pierde la condición de estudiante quien repruebe el 100 % de los créditos
        inscritos Y su promedio ponderado de asignaturas cursadas sea inferior a
        3,0, O quien repruebe por cuarta vez un curso.

    Sustituye a `rendimiento_bajo` (= PROMEDIO_CARRERA < 3.0), descartado por
    tautológico en RC-012: el promedio de carrera incluye el primer semestre, que
    era su propio predictor dominante.

    IMPORTANTE — el target se re-deriva sobre datos históricos regidos por el
    Acuerdo Superior 015 de 2003 (derogado). Ver MARCO_NORMATIVO.md §1 y RC-015.
    Supuesto declarado: estabilidad del reglamento vigente durante la vida útil
    del modelo.

    Retorna DataFrame por estudiante con:
        CODIGO_INST
        bajo_rendimiento_art19  1 si activó el art. 19 en algún periodo
        art19_n_eventos         nº de periodos en que lo activó
        art19_primer_periodo    primer periodo con activación (None si nunca)
        art19_dudoso            1 si algún evento tiene cursos inscritos sin nota
                                en el mismo periodo (la condición "100 % de los
                                créditos inscritos" no es verificable con certeza)
        tiene_actividad_academica  1 si tiene al menos una nota propia válida
        n_periodos_cursados     nº de periodos con actividad calificada

    `clave_curso` (oct-2026, capa de equivalencias entre planes): clave con la que se
    cuentan los intentos de un MISMO curso para la vía de la cuarta reprobación.
    'MATERIA' (defecto) reproduce el comportamiento histórico. 'CODIGO_CANONICO'
    traduce los cursos del plan 2011 a su equivalente del plan 2018 según la
    Resolución Académica 036 de 2017 (ver src/equivalencias.py); es la opción
    normativamente correcta cuando un estudiante cambia de plan.
    """
    m = ing_mat.copy()
    if clave_curso != 'MATERIA':
        from equivalencias import normalizar_materias
        m = normalizar_materias(m)
    m['_CURSO'] = m['MATERIA'] if clave_curso == 'MATERIA' else m['CURSO_INTENTOS']
    m['OBS'] = m['OBSERVACION'].astype(str).str.strip().str.upper()
    m['ord'] = m['PERIODO_INSCRIPCION'].map(_periodo_a_orden)
    m['regular'] = m['PERIODO_INSCRIPCION'].map(_es_periodo_regular)

    # Cursos con nota propia y calificable (excluye O/V/I externas y A/P/R/E sin nota)
    val = m[m['OBS'].isin(OBS_VALIDAS) & m['DEFINITIVA'].notna()].copy()
    val = val.sort_values(['CODIGO_INST', 'ord'])
    val['reprob'] = (val['DEFINITIVA'] < 3.0).astype(int)
    val['vez']    = val.groupby(['CODIGO_INST', '_CURSO']).cumcount() + 1
    val['num']    = val['DEFINITIVA'] * val['CREDITOS']
    val['crep']   = val['CREDITOS'] * val['reprob']

    # Agregado por estudiante-periodo
    per = (val.groupby(['CODIGO_INST', 'ord'])
              .agg(creditos=('CREDITOS', 'sum'),
                   creditos_reprob=('crep', 'sum'),
                   num=('num', 'sum'))
              .reset_index()
              .sort_values(['CODIGO_INST', 'ord']))

    # Promedio ponderado ACUMULADO al cierre de cada periodo
    # (art. 19 parágrafo primero: contempla cursos aprobados y reprobados)
    per['prom_ponderado_acum'] = (per.groupby('CODIGO_INST')['num'].cumsum() /
                                  per.groupby('CODIGO_INST')['creditos'].cumsum())
    per['pct_creditos_reprob'] = per['creditos_reprob'] / per['creditos']

    # Cuarta reprobación de un mismo curso (vía alterna del art. 19)
    cuarta = (val[(val['vez'] >= 4) & (val['reprob'] == 1)]
              .groupby(['CODIGO_INST', 'ord']).size().reset_index(name='cuarta_reprob'))
    per = per.merge(cuarta, on=['CODIGO_INST', 'ord'], how='left')
    per['cuarta_reprob'] = per['cuarta_reprob'].fillna(0)

    # Cursos inscritos SIN nota válida en el mismo periodo: hacen que la condición
    # "100 % de los créditos inscritos" no sea verificable con certeza (RC-017)
    sin_nota = (m[~(m['OBS'].isin(OBS_VALIDAS) & m['DEFINITIVA'].notna())]
                .groupby(['CODIGO_INST', 'ord']).size().reset_index(name='n_sin_nota'))
    per = per.merge(sin_nota, on=['CODIGO_INST', 'ord'], how='left')
    per['n_sin_nota'] = per['n_sin_nota'].fillna(0)

    # Marca de periodo regular (-1/-2) vs. intersemestral (-0)
    reg = val.groupby(['CODIGO_INST', 'ord'])['regular'].max().reset_index()
    per = per.merge(reg, on=['CODIGO_INST', 'ord'], how='left')

    # ── Regla del art. 19 ────────────────────────────────────────────────────
    # La condición de "reprobar el 100 % de los créditos inscritos" se evalúa SOLO
    # sobre periodos académicos REGULARES. Un curso intersemestral (-0) no constituye
    # un periodo académico: el art. 15 parágrafo define el periodo entre matrículas
    # ordinarias, y el art. 40 parágrafo tercero excluye la nota intersemestral del
    # promedio de semestre. Su nota SÍ alimenta el promedio ponderado acumulado
    # (art. 40 parágrafo primero), que ya se calcula sobre todos los periodos.
    # La vía de la cuarta reprobación sí aplica en cualquier periodo: el art. 19 no
    # la condiciona al tipo de periodo.
    per['evento_art19'] = (
        ((per['pct_creditos_reprob'] == 1) & (per['prom_ponderado_acum'] < 3.0) &
         (per['regular'])) |
        (per['cuarta_reprob'] > 0)
    )

    ev = per[per['evento_art19']]
    agg = (ev.groupby('CODIGO_INST')
             .agg(art19_n_eventos=('evento_art19', 'size'),
                  _ord_min=('ord', 'min'),
                  art19_dudoso=('n_sin_nota', lambda s: int((s > 0).any())))
             .reset_index())

    # Periodo legible del primer evento
    ord2per = (val[['ord', 'PERIODO_INSCRIPCION']].drop_duplicates()
               .set_index('ord')['PERIODO_INSCRIPCION'].to_dict())
    agg['art19_primer_periodo'] = agg['_ord_min'].map(ord2per)
    agg = agg.drop(columns='_ord_min')

    # Exposición: solo quien cursó puede activar el artículo
    expo = (per.groupby('CODIGO_INST')
               .agg(n_periodos_cursados=('ord', 'nunique')).reset_index())

    out = expo.merge(agg, on='CODIGO_INST', how='left')
    out['art19_n_eventos'] = out['art19_n_eventos'].fillna(0).astype(int)
    out['art19_dudoso']    = out['art19_dudoso'].fillna(0).astype(int)
    out['bajo_rendimiento_art19'] = (out['art19_n_eventos'] > 0).astype(int)
    out['tiene_actividad_academica'] = 1

    if verbose:
        print(f"  [art.19] estudiantes con actividad calificada: {len(out)}")
        print(f"  [art.19] positivos: {int(out['bajo_rendimiento_art19'].sum())} "
              f"({out['bajo_rendimiento_art19'].mean():.1%}) | "
              f"dudosos: {int(out['art19_dudoso'].sum())}")

    return out


# ── Features por materia crítica ─────────────────────────────────────────────

def construir_features_materias(ing_mat):
    """
    ⛔ RETIRADO (I-4 / RC-022) — no usar para modelar.

    Construía las features de los modelos de reprobación por asignatura, retirados
    por FUGA TEMPORAL (RC-013): `prom_global` es el promedio del estudiante en el
    resto de la carrera y entre el 70 % y el 83 % de esa información proviene de
    semestres POSTERIORES a la asignatura que se predice. `veces_cursada` tampoco
    es observable antes de cursar la asignatura.

    Se conserva únicamente porque `pipeline_completo()` reporta qué asignaturas
    superan el mínimo de casos, dato descriptivo aún útil. El índice de criticidad
    vive en `src/indice_materias.py` y no está afectado.

    Retorna dict {materia: (X_array, y_array, df_materia)}.
    """
    ing_mat = ing_mat.copy()
    ing_mat['OBS'] = ing_mat['OBSERVACION'].astype(str).str.strip().str.upper()

    # Solo registros con OBSERVACION válida y nota registrada
    val = ing_mat[ing_mat['OBS'].isin(OBS_VALIDAS) & ing_mat['DEFINITIVA'].notna()].copy()

    # Última nota por estudiante-materia
    ult = (
        val.sort_values('PERIODO_INSCRIPCION', ascending=False)
        .drop_duplicates(subset=['CODIGO_INST', 'MATERIA'], keep='first')
        .copy()
    )

    # Veces cursada (repitencia)
    veces = (
        val.groupby(['CODIGO_INST', 'MATERIA'])
        .size().reset_index(name='veces_cursada')
    )

    # Nota en Matemáticas I como predictor base (aptitud matemática previa)
    mat1 = ult[ult['MATERIA'].str.strip() == 'MATEMATICAS I'][['CODIGO_INST', 'DEFINITIVA']].rename(
        columns={'DEFINITIVA': 'nota_mat1'}
    )

    datasets = {}
    for materia in MATERIAS_CRITICAS:
        sub = ult[ult['MATERIA'].str.strip() == materia].copy()
        if len(sub) < 10:
            continue
        sub['reprobado'] = (sub['DEFINITIVA'] < 3.0).astype(int)
        if sub['reprobado'].sum() < 10:   # clase positiva insuficiente -> no se modela
            continue

        # prom_global SIN la materia objetivo (evita fuga: la nota objetivo no entra al promedio)
        otras = ult[ult['MATERIA'].str.strip() != materia]
        prom_global = otras.groupby('CODIGO_INST')['DEFINITIVA'].mean().reset_index(name='prom_global')
        sub = sub.merge(prom_global, on='CODIGO_INST', how='left')
        sub = sub.merge(
            veces[veces['MATERIA'] == materia][['CODIGO_INST', 'veces_cursada']],
            on='CODIGO_INST', how='left'
        )
        sub['veces_cursada'] = sub['veces_cursada'].fillna(1).astype(int)

        features_mat = ['prom_global', 'veces_cursada']
        # nota_mat1 solo si la materia NO es Matemáticas I (si lo es, sería el propio target -> fuga)
        if materia != 'MATEMATICAS I':
            sub = sub.merge(mat1, on='CODIGO_INST', how='left')
            sub['nota_mat1'] = sub['nota_mat1'].fillna(sub['prom_global'])
            features_mat = ['prom_global', 'veces_cursada', 'nota_mat1']

        X = sub[features_mat].values
        y = sub['reprobado'].values
        datasets[materia] = (X, y, sub)

    return datasets


# ── Pipeline principal ────────────────────────────────────────────────────────

def pipeline_completo(verbose=True):
    """Ejecuta el pipeline completo y guarda artefactos en src/."""
    if verbose:
        print("Cargando datos...")
    ing_car, ing_mat, ing_he, ing_pc, ing_ps, poblacion = cargar_datos()
    if verbose:
        print(f"  Población base: {len(poblacion)} estudiantes")
    if verbose:
        print("Construyendo features de estudiante...")
    df_master, feature_cols = construir_features_estudiante(ing_car, ing_he, ing_pc, ing_ps)

    # ── Target normativo vigente (art. 19) — decisión RC-017 / paso I-2b ─────
    if verbose:
        print("Construyendo target normativo (art. 19 del Reglamento vigente)...")
    art19 = construir_target_art19(ing_mat, verbose=verbose)
    art19['CODIGO_INST'] = art19['CODIGO_INST'].astype(str)
    df_master['CODIGO_INST'] = df_master['CODIGO_INST'].astype(str)
    df_master = df_master.merge(art19, on='CODIGO_INST', how='left')

    # Estudiantes sin ninguna nota propia: no están expuestos al art. 19, que exige
    # reprobar créditos. Su expediente son homologaciones (OBS='O'). No se les asigna
    # target: quedan como NaN y `tiene_actividad_academica`=0 (decisión RC-019).
    df_master['tiene_actividad_academica'] = df_master['tiene_actividad_academica'].fillna(0).astype(int)
    df_master['n_periodos_cursados'] = df_master['n_periodos_cursados'].fillna(0).astype(int)
    for c in ['art19_n_eventos', 'art19_dudoso']:
        df_master[c] = df_master[c].fillna(0).astype(int)

    if verbose:
        print("Construyendo features de materias críticas...")
    datasets_materias = construir_features_materias(ing_mat)

    # Guardar
    src_dir = os.path.dirname(os.path.abspath(__file__))
    df_master.to_csv(os.path.join(src_dir, 'df_master_limpio.csv'), index=False)

    if verbose:
        exp = df_master[df_master['tiene_actividad_academica'] == 1]
        print(f"\n[OK] df_master_limpio.csv guardado: {df_master.shape}")
        print(f"  Features ({len(feature_cols)}): {feature_cols}")
        print(f"  TARGET VIGENTE bajo_rendimiento_art19 = "
              f"{int(exp['bajo_rendimiento_art19'].sum())}/{len(exp)} "
              f"(población expuesta; {int((df_master['tiene_actividad_academica']==0).sum())} "
              f"sin actividad académica excluidos)")
        print(f"  Targets: graduado={df_master['graduado'].sum()}/{len(df_master)}, "
              f"rendimiento_bajo(OBSOLETO)={df_master['rendimiento_bajo'].sum()}/{len(df_master)}")
        print(f"  Materias críticas válidas: {list(datasets_materias.keys())}")
        nulos = df_master[feature_cols].isnull().sum()
        if nulos.any():
            print(f"  [WARNING] Nulos en features: {nulos[nulos>0].to_dict()}")
        else:
            print("  [OK] Sin nulos en features")

    return df_master, feature_cols, datasets_materias


if __name__ == '__main__':
    pipeline_completo()
