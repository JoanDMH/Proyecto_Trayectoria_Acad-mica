"""
preprocessing.py
Fase 3 CRISP-DM — Preparación de datos
Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

Correcciones aplicadas post-Fase 2:
- Población base: 89 estudiantes (cruce car ∩ historial)
- 18 features seleccionadas
- OBSERVACION: excluye O (Homologada), I (Intercambio), C (Cancelada), E (En curso)
- Promedio materias: solo notas >= 3.0, última nota por estudiante-materia
- Materias críticas corregidas con índice compuesto
- Mapeo NIVEL_ED sin código 6 (salto 5 → 7)
"""

import os
import pandas as pd
import numpy as np

# ── Configuración ────────────────────────────────────────────────────────────
PROG     = 'INGENIERIA DE SISTEMAS'
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
    'FISICA I',
    'MATEMATICAS II',
    'ALGEBRA LINEAL',
    'PROGRAMACION',
    'MATEMATICAS ESPECIALES',
]

# OBSERVACION válidas para análisis de notas
OBS_VALIDAS = {'N', 'H', 'F', 'R', 'TG'}


# ── Carga y filtrado ─────────────────────────────────────────────────────────

def cargar_datos():
    """Carga los 5 datasets y filtra por cohortes/programa, excluyendo nulos de promedio acumulado."""
    df_car = pd.read_excel(os.path.join(DATA_DIR, 'caracterización.xlsx'))
    df_mat = pd.read_excel(os.path.join(DATA_DIR, 'detalle_materias.xlsx'))
    df_he  = pd.read_excel(os.path.join(DATA_DIR, 'historial_estados_.xlsx'))
    df_pc  = pd.read_excel(os.path.join(DATA_DIR, 'PROMEDIOS_DE_CARRERA.xlsx'))
    df_ps  = pd.read_excel(os.path.join(DATA_DIR, 'promedios_semestre.xlsx'))

    ing_car = df_car[
        (df_car['PROGRAMA'].str.strip().str.upper() == PROG) &
        (df_car['PERIODO_INGRESO'].astype(str).str.strip().isin(COHORTES))
    ].copy().reset_index(drop=True)

    for df in [df_mat, df_he, df_pc, df_ps]:
        df['PROGRAMA'] = df['PROGRAMA'].str.strip().str.upper()
        df['COHORTE']  = df['COHORTE'].astype(str).str.strip()

    ing_mat = df_mat[(df_mat['PROGRAMA'] == PROG) & (df_mat['COHORTE'].isin(COHORTES))].copy().reset_index(drop=True)
    ing_he  = df_he [(df_he ['PROGRAMA'] == PROG) & (df_he ['COHORTE'].isin(COHORTES))].copy().reset_index(drop=True)
    ing_pc  = df_pc [(df_pc ['PROGRAMA'] == PROG) & (df_pc ['COHORTE'].isin(COHORTES))].copy().reset_index(drop=True)
    ing_ps  = df_ps [(df_ps ['PROGRAMA'] == PROG) & (df_ps ['COHORTE'].isin(COHORTES))].copy().reset_index(drop=True)

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
    # Mapeamos prom_sem1 según la cohorte de ingreso de cada estudiante
    prom_s1 = ing_ps[['CODIGO_INST', 'PERIODO_INSCRIPCION', 'PROMEDIO_SEMESTRE']].copy()
    prom_s1.columns = ['CODIGO_INST', 'COHORTE', 'prom_sem1']
    
    df = df.merge(prom_s1, on=['CODIGO_INST', 'COHORTE'], how='left')
    df['prom_sem1'] = df['prom_sem1'].fillna(df['prom_sem1'].median())

    # ── Promedio acumulado de carrera ─────────────────────────────────────────
    df = df.merge(ing_pc[['CODIGO_INST', 'PROMEDIO_CARRERA']], on='CODIGO_INST', how='left')

    # ── Targets ──────────────────────────────────────────────────────────────
    ing_he['estado_limpio'] = ing_he['ESTADO'].str.strip().str.upper()
    graduados = set(ing_he[ing_he['estado_limpio'] == 'GRADUADO']['CODIGO_INST'].astype(str))

    df['graduado']         = df['CODIGO_INST'].astype(str).isin(graduados).astype(int)
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
        # Rendimiento primer semestre
        'prom_sem1',
    ]

    info_cols   = ['CODIGO_INST', 'COHORTE', 'SEXO', 'NIVEL_ED_PADRE', 'NIVEL_ED_MADRE',
                   'ANOS_REPITIO', 'ESTRATO_ACTUAL', 'TIPO_PLANTEL', 'ZONA_LUGAR_RESIDENCIA']
    target_cols = ['graduado', 'rendimiento_bajo', 'PROMEDIO_CARRERA']

    df_out = df[info_cols + feature_cols + target_cols].copy()
    return df_out, feature_cols


# ── Features por materia crítica ─────────────────────────────────────────────

def construir_features_materias(ing_mat):
    """
    Features para predecir reprobación en cada materia crítica (pregunta d).
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

    # Promedio global del estudiante (todas las materias)
    prom_global = (
        ult.groupby('CODIGO_INST')['DEFINITIVA']
        .mean().reset_index(name='prom_global')
    )

    # Nota en Matemáticas I como predictor base
    mat1 = ult[ult['MATERIA'].str.strip() == 'MATEMATICAS I'][['CODIGO_INST', 'DEFINITIVA']].rename(
        columns={'DEFINITIVA': 'nota_mat1'}
    )

    datasets = {}
    for materia in MATERIAS_CRITICAS:
        sub = ult[ult['MATERIA'].str.strip() == materia].copy()
        if len(sub) < 10:
            continue
        sub['reprobado'] = (sub['DEFINITIVA'] < 3.0).astype(int)
        sub = sub.merge(prom_global, on='CODIGO_INST', how='left')
        sub = sub.merge(
            veces[veces['MATERIA'] == materia][['CODIGO_INST', 'veces_cursada']],
            on='CODIGO_INST', how='left'
        )
        sub = sub.merge(mat1, on='CODIGO_INST', how='left')
        sub['veces_cursada'] = sub['veces_cursada'].fillna(1).astype(int)
        sub['nota_mat1']     = sub['nota_mat1'].fillna(sub['prom_global'])

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
    if verbose:
        print("Construyendo features de materias críticas...")
    datasets_materias = construir_features_materias(ing_mat)

    # Guardar
    src_dir = os.path.dirname(os.path.abspath(__file__))
    df_master.to_csv(os.path.join(src_dir, 'df_master_limpio.csv'), index=False)

    if verbose:
        print(f"\n[OK] df_master_limpio.csv guardado: {df_master.shape}")
        print(f"  Features ({len(feature_cols)}): {feature_cols}")
        print(f"  Targets: graduado={df_master['graduado'].sum()}/{len(df_master)}, "
              f"rendimiento_bajo={df_master['rendimiento_bajo'].sum()}/{len(df_master)}")
        print(f"  Materias críticas válidas: {list(datasets_materias.keys())}")
        nulos = df_master[feature_cols].isnull().sum()
        if nulos.any():
            print(f"  [WARNING] Nulos en features: {nulos[nulos>0].to_dict()}")
        else:
            print("  [OK] Sin nulos en features")

    return df_master, feature_cols, datasets_materias


if __name__ == '__main__':
    pipeline_completo()
