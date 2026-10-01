"""
Pruebas de humo de TRAYECTA (trayecta/motor.py) con las cohortes sintéticas.

  · procesa cohortes del plan 2011, del 2018 y mezcladas sin errores
  · el indicador art. 19 del panel semestral coincide, estudiante a estudiante, con el
    target oficial del pipeline (preprocessing.construir_target_art19)
  · detecta a los estudiantes que cambian de plan

Uso:  python -m pytest tests/ -q
"""
import os
import sys

import pandas as pd
import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'trayecta'))
import motor  # noqa: E402

DEMO = os.path.join(RAIZ, 'trayecta', 'datos_demo')


@pytest.fixture(scope='module')
def modelos():
    return motor.cargar_modelos()


def _cohorte(c):
    return (pd.read_csv(os.path.join(DEMO, f'{c}_materias.csv')),
            pd.read_csv(os.path.join(DEMO, f'{c}_ingreso.csv')))


@pytest.mark.parametrize('c', ['A', 'B'])
def test_procesa_cohorte(c, modelos):
    mat, ing = _cohorte(c)
    errores, _, rep = motor.validar_entrada(mat, ing)
    assert not errores and rep['codigos_fuera_de_catalogo'] == []
    est, panel = motor.procesar_cohorte(mat, ing, modelos)
    assert len(est) == ing['CODIGO_INST'].nunique()
    assert est['p_art19'].between(0, 1).all() and est['p_graduacion'].between(0, 1).all()
    assert set(est['nivel_alerta']) <= set(motor.NIVELES)
    # coherencia: el art. 19 del panel semestral = target oficial del pipeline
    por_panel = panel.groupby('CODIGO_INST')['art19'].max()
    oficial = est.set_index('CODIGO_INST')['art19_observado']
    assert (por_panel.reindex(oficial.index).fillna(0).astype(int) == oficial).all()


def test_detecta_cambio_de_plan(modelos):
    mat, ing = _cohorte('A')
    est, _ = motor.procesar_cohorte(mat, ing, modelos)
    pref = mat.assign(p=mat['CODIGO_MATERIA'].astype(str).str[:3]).groupby('CODIGO_INST')['p'].nunique()
    assert (est['planes'] == 'IS-2011/IS-2018').sum() == int((pref == 2).sum()) > 0


def test_variables_s3_imputan_como_el_pipeline():
    mat = pd.DataFrame([['X1', '2026-1', '2026-2', 603203, 'CALCULO INTEGRAL', 4, 2.5, 'N']],
                       columns=motor.COLS_MATERIAS)
    ing = pd.DataFrame(columns=motor.COLS_INGRESO)
    f = motor.variables_s3(mat, ing).iloc[0]
    assert f['sin_primer_semestre'] == 1 and f['prom_sem1'] == motor.MEDIANA_PROM_SEM1
    assert f['icfes_total'] == sum(motor.MEDIANAS_ICFES.values())
