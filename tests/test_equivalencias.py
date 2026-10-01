"""
Pruebas de la capa de equivalencias entre planes (IS-2011 ↔ IS-2018).

Garantizan dos cosas:
  1. La tabla normativa transcrita es coherente con los acuerdos (totales de créditos,
     cursos, ausencia de contradicciones entre artículos).
  2. «Sin romper nada»: con los datos vigentes, usar la clave canónica produce
     EXACTAMENTE el mismo target del art. 19 que la clave histórica, y el dataset
     maestro no cambia.

Uso:  python -m pytest tests/ -q
"""
import os
import sys
import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, 'src')
sys.path.insert(0, SRC)

import equivalencias as eq  # noqa: E402

DATOS = os.path.join(RAIZ, 'Datos', 'detalle_materias_recod.xlsx')
hay_datos = pytest.mark.skipif(not os.path.exists(DATOS), reason='sin Datos/ (paquete anonimizado)')


# ── 1. Tabla normativa ───────────────────────────────────────────────────────
def test_totales_de_los_acuerdos():
    c = eq.cargar_catalogo()
    c = c[c['tipo'] != 'ADM']
    t = c.groupby('plan').agg(n=('codigo', 'size'), cred=('creditos', 'sum'))
    assert t.loc['IS-2011', 'cred'] == 167          # Acuerdo 008/2011
    assert t.loc['IS-2018', 'cred'] == 165          # Acuerdo 001/2017
    assert t.loc['IS-2018', 'n'] == 53              # «No. cursos del plan: 53»


def test_sin_contradicciones_entre_articulos():
    avisos = eq.verificar_consistencia()
    assert not [a for a in avisos if 'discrepan' in a or 'sin catálogo' in a], avisos


def test_mapa_es_funcion():
    m = eq.mapa_canonico()
    assert all(isinstance(v, tuple) and len(v) == 2 for v in m.values())


@pytest.mark.parametrize('origen,destino,fuente', [
    ('602203', '603203', 'Art. 2'),          # Matemáticas II -> Cálculo integral
    ('602204', '603205', 'Art. 2'),          # Física I -> Física mecánica
    ('602103', '603103', 'Art. 2'),          # Matemáticas I -> Cálculo diferencial
    ('602303', '603403', 'Art. 2'),          # relación 2:1
    ('602603', '603403', 'Art. 2'),
    ('602102', '603102', 'Art. 1'),          # solo Art. 1 (asimétrica)
    ('602105', '603104', 'institucional'),
])
def test_equivalencias_clave(origen, destino, fuente):
    d = eq.normalizar_materias(pd.DataFrame({'CODIGO_MATERIA': [int(origen)], 'MATERIA': ['x']}))
    assert d.at[0, 'CODIGO_CANONICO'] == destino
    assert d.at[0, 'EQUIV_FUENTE'] == fuente


def test_casos_sin_traduccion():
    d = eq.normalizar_materias(pd.DataFrame({
        'CODIGO_MATERIA': [602202, 603203, 612101, 999999],
        'MATERIA': ['MATEMATICA DISCRETA', 'CALCULO INTEGRAL', 'X', 'Y']}))
    assert list(d['EQUIV_FUENTE']) == ['sin_equivalente', 'propio', 'sin_catalogo', 'sin_catalogo']
    assert list(d['CODIGO_CANONICO']) == ['602202', '603203', '612101', '999999']
    assert d.at[2, 'PLAN'] == 'IE-612'


def test_columnas_originales_intactas():
    df = pd.DataFrame({'CODIGO_MATERIA': [602203], 'MATERIA': ['MATEMATICAS II']})
    out = eq.normalizar_materias(df)
    assert list(df.columns) == ['CODIGO_MATERIA', 'MATERIA']      # no muta la entrada
    assert out.at[0, 'MATERIA'] == 'MATEMATICAS II'
    assert out.at[0, 'MATERIA_CANONICA'] == 'CALCULO INTEGRAL'


# ── 2. Necesidad: un estudiante que cambia de plan ───────────────────────────
def _sintetico_cambio_de_plan():
    """Reprueba Matemáticas II tres veces en 2011 y Cálculo integral una vez en 2018."""
    filas = []
    for i, per in enumerate(['2019-1', '2019-2', '2020-1']):
        filas.append(('S1', per, 602203, 'MATEMATICAS II', 4, 2.0))
        filas.append(('S1', per, 602101, 'FUNDAMENTOS DE PROGRAMACION', 4, 3.5))
    filas.append(('S1', '2020-2', 603203, 'CALCULO INTEGRAL', 4, 2.0))
    filas.append(('S1', '2020-2', 603201, 'PROGRAMACIÓN ORIENTADA A OBJETOS', 4, 3.5))
    d = pd.DataFrame(filas, columns=['CODIGO_INST', 'PERIODO_INSCRIPCION', 'CODIGO_MATERIA',
                                     'MATERIA', 'CREDITOS', 'DEFINITIVA'])
    d['OBSERVACION'] = 'N'
    return d


def test_cuarta_reprobacion_entre_planes():
    from preprocessing import construir_target_art19
    d = _sintetico_cambio_de_plan()
    hist = construir_target_art19(d, clave_curso='MATERIA')
    canon = construir_target_art19(d, clave_curso='CODIGO_CANONICO')
    assert int(hist['bajo_rendimiento_art19'].iloc[0]) == 0     # la clave por nombre no lo ve
    assert int(canon['bajo_rendimiento_art19'].iloc[0]) == 1    # la canónica sí (4.ª vez)


# ── 3. No ruptura con los datos vigentes ─────────────────────────────────────
@hay_datos
def test_cobertura_total_de_la_extraccion():
    rep = eq.validar(pd.read_excel(DATOS))
    assert rep['codigos_fuera_de_catalogo'] == []
    assert rep['discrepancias_de_creditos'] == []
    assert rep['estudiantes_con_planes_mezclados'] == 0


@hay_datos
@pytest.mark.parametrize('programas', [None, 'FCBI'])
def test_target_art19_identico(programas):
    from preprocessing import cargar_datos, construir_target_art19, PROGRAMAS_FCBI
    progs = PROGRAMAS_FCBI if programas == 'FCBI' else None
    _, mat, *_ = cargar_datos(progs)
    a = construir_target_art19(mat).sort_values('CODIGO_INST').reset_index(drop=True)
    b = construir_target_art19(mat, clave_curso='CODIGO_CANONICO') \
        .sort_values('CODIGO_INST').reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b)


@hay_datos
def test_dataset_maestro_sin_cambios():
    """Reconstruye df_master_limpio en memoria y lo compara con el CSV versionado."""
    from preprocessing import cargar_datos, construir_features_estudiante, construir_target_art19
    car, mat, he, pc, ps, _ = cargar_datos()
    df, _ = construir_features_estudiante(car, he, pc, ps)
    art = construir_target_art19(mat, clave_curso='CODIGO_CANONICO')
    art['CODIGO_INST'] = art['CODIGO_INST'].astype(str)
    df['CODIGO_INST'] = df['CODIGO_INST'].astype(str)
    df = df.merge(art, on='CODIGO_INST', how='left')
    df['art19_n_eventos'] = df['art19_n_eventos'].fillna(0)      # igual que pipeline_completo
    ref = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'), dtype={'CODIGO_INST': str})
    df = df.set_index('CODIGO_INST').loc[ref['CODIGO_INST']]
    for col in ['prom_sem1', 'sin_primer_semestre', 'icfes_total', 'graduado',
                'bajo_rendimiento_art19', 'art19_n_eventos']:
        a = pd.to_numeric(df[col], errors='coerce').fillna(-1).values
        b = pd.to_numeric(ref.set_index('CODIGO_INST')[col], errors='coerce').fillna(-1).values
        assert (abs(a - b) < 1e-9).all(), col


@hay_datos
def test_indice_canonico_fusiona_planes():
    from indice_materias import calcular_indice
    hist = calcular_indice()
    canon = calcular_indice(canonico=True)
    assert 'MATEMATICAS II' in set(hist['materia'])
    assert 'CALCULO INTEGRAL' in set(canon['materia'])
    n_h = int(hist.loc[hist['materia'] == 'MATEMATICAS II', 'N'].iloc[0])
    n_c = int(canon.loc[canon['materia'] == 'CALCULO INTEGRAL', 'N'].iloc[0])
    assert n_c >= n_h


def test_fusion_no_cuenta_como_repeticion():
    """602303 y 602603 se fusionan en 603403, pero cursar ambos no es «repetir»."""
    from preprocessing import construir_target_art19
    filas = []
    for per in ['2019-1', '2019-2']:
        filas += [('S2', per, 602303, 'ECUACIONES DIFERENCIALES Y EN DIFERENCIA', 4, 2.0),
                  ('S2', per, 602603, 'MODELAMIENTO DE SISTEMAS', 3, 2.0),
                  ('S2', per, 602101, 'FUNDAMENTOS DE PROGRAMACION', 4, 4.0)]
    d = pd.DataFrame(filas, columns=['CODIGO_INST', 'PERIODO_INSCRIPCION', 'CODIGO_MATERIA',
                                     'MATERIA', 'CREDITOS', 'DEFINITIVA'])
    d['OBSERVACION'] = 'N'
    canon = construir_target_art19(d, clave_curso='CODIGO_CANONICO')
    assert int(canon['bajo_rendimiento_art19'].iloc[0]) == 0     # 2+2 intentos ≠ 4.ª vez


@hay_datos
def test_indice_historico_sin_cambios():
    from indice_materias import calcular_indice
    ref = pd.read_csv(os.path.join(SRC, 'materias_criticas.csv'))
    nuevo = calcular_indice()
    pd.testing.assert_frame_equal(ref[['materia', 'N', 'reprobados', 'indice']].reset_index(drop=True),
                                  nuevo[['materia', 'N', 'reprobados', 'indice']].reset_index(drop=True),
                                  check_dtype=False)
