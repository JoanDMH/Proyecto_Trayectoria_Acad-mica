"""
generar_demo.py — Cohortes SINTÉTICAS para demostrar TRAYECTA sin exponer datos reales.

Ningún registro procede de un estudiante real: las trayectorias se simulan a partir de
parámetros agregados y públicos del estudio (planes de estudio oficiales, dificultad
relativa de las asignaturas según el índice de criticidad, rangos de SABER 11). Sirven
para mostrar el software en público (CICI 2026); los resultados NO describen a la
Universidad.

Genera en datos_demo/:
    A_materias.csv / A_ingreso.csv   Cohorte A (ingreso 2018-2, plan 2011, 8 semestres),
                                     con 6 estudiantes que CAMBIAN al plan 2018 en 2021
    B_materias.csv / B_ingreso.csv   Cohorte B (ingreso 2025-1, plan 2018, 3 semestres)

Uso:  python trayecta/generar_demo.py
"""
import os
import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
OUT = os.path.join(AQUI, 'datos_demo')
SEED = 2026

CAT = pd.read_csv(os.path.join(RAIZ, 'src', 'planes_estudio', 'catalogo_cursos.csv'), dtype={'codigo': str})
CAT = CAT[CAT['tipo'] != 'ADM']
EQ = pd.read_csv(os.path.join(RAIZ, 'src', 'planes_estudio', 'equivalencias_IS_2011_2018.csv'),
                 dtype={'codigo_plan_2011': str, 'codigo_plan_2018': str})
A2 = EQ[EQ['sentido'].isin(['cambia_a_2018', 'institucional_inferida'])]

# Dificultad relativa (resta a la nota esperada). Las cinco críticas según el índice.
DIFICULTAD = {'602203': .55, '603203': .55, '602204': .50, '603205': .50, '602104': .45, '603204': .45,
              '602103': .40, '603103': .40, '602101': .30, '603101': .30, '602302': .25, '603303': .25,
              '602304': .25, '603304': .25, '602202': .15}


def _periodos(inicio, n):
    a, s = map(int, inicio.split('-'))
    out = []
    for _ in range(n):
        out.append(f'{a}-{s}')
        a, s = (a, 2) if s == 1 else (a + 1, 1)
    return out


def _nombre(c):
    return CAT.set_index('codigo').at[c, 'nombre'].upper()


def simular(prefijo, cohorte, plan, n_est, n_periodos, rng, cambio_plan=0, cambio_en=None):
    plan_cat = CAT[CAT['plan'] == plan].sort_values(['semestre', 'codigo'])
    periodos = _periodos(cohorte, n_periodos)
    filas, ingreso = [], []
    for i in range(n_est):
        cod = f'{prefijo}{i + 1:03d}'
        a = rng.normal(0, 1)
        icfes = {'PMATN': 65 + 5.5 * (0.75 * a + 0.66 * rng.normal()),
                 'PCRIN': 63 + 6.0 * (0.55 * a + 0.83 * rng.normal()),
                 'PNATN': 64 + 5.5 * (0.60 * a + 0.80 * rng.normal()),
                 'PINGN': 63 + 8.0 * (0.40 * a + 0.92 * rng.normal()),
                 'PCIUN': 62 + 6.5 * (0.45 * a + 0.89 * rng.normal())}
        ingreso.append({'CODIGO_INST': cod, 'COHORTE': cohorte,
                        **{k: int(np.clip(round(v), 35, 100)) for k, v in icfes.items()}})
        cursos_plan = plan_cat.copy()
        aprobados, intentos = set(), {}
        cambia = i < cambio_plan
        for t, per in enumerate(periodos):
            if cambia and cambio_en and per == cambio_en:   # cambio al plan 2018 (Art. 2 RA-036)
                mapa = dict(zip(A2['codigo_plan_2011'], A2['codigo_plan_2018']))
                aprobados = {mapa.get(c, c) for c in aprobados if mapa.get(c, c).startswith('603')}
                intentos = {mapa.get(c, c): v for c, v in intentos.items()}
                cursos_plan = CAT[CAT['plan'] == 'IS-2018'].sort_values(['semestre', 'codigo'])
            nivel = t + 1
            pend = cursos_plan[(~cursos_plan['codigo'].isin(aprobados)) & (cursos_plan['semestre'] <= nivel)]
            if pend.empty:
                break
            # repetidos primero, luego por semestre; tope de 18 créditos
            pend = pend.assign(rep=pend['codigo'].map(lambda c: -intentos.get(c, 0))).sort_values(['rep', 'semestre'])
            carga, cr = [], 0
            for _, c in pend.iterrows():
                if cr + c['creditos'] <= 18:
                    carga.append(c); cr += c['creditos']
            notas = []
            for c in carga:
                mu = 3.45 + 0.75 * a + 0.04 * t - DIFICULTAD.get(c['codigo'], rng.uniform(0, .15))
                nota = float(np.clip(round(rng.normal(mu, 0.7), 1), 0, 5))
                intentos[c['codigo']] = intentos.get(c['codigo'], 0) + 1
                if nota >= 3.0:
                    aprobados.add(c['codigo'])
                notas.append(nota)
                filas.append({'CODIGO_INST': cod, 'COHORTE': cohorte, 'PERIODO_INSCRIPCION': per,
                              'CODIGO_MATERIA': c['codigo'], 'MATERIA': _nombre(c['codigo']),
                              'CREDITOS': int(c['creditos']), 'DEFINITIVA': nota, 'OBSERVACION': 'N'})
            prom = float(np.mean(notas)) if notas else 3.0
            todo_perdido = all(n < 3.0 for n in notas)
            if todo_perdido and prom < 3.0 and t > 0 and rng.random() < 0.8:
                break                                    # pierde la calidad de estudiante
            p_abandono = 1 / (1 + np.exp(-(-2.4 + 2.8 * (3.0 - prom) - 0.25 * t)))
            if rng.random() < p_abandono:
                break
    return pd.DataFrame(filas), pd.DataFrame(ingreso)


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(SEED)
    ma, ia = simular('SIM-A', '2018-2', 'IS-2011', 48, 8, rng, cambio_plan=6, cambio_en='2021-1')
    mb, ib = simular('SIM-B', '2025-1', 'IS-2018', 42, 3, rng)
    for nom, m, i in (('A', ma, ia), ('B', mb, ib)):
        m.to_csv(os.path.join(OUT, f'{nom}_materias.csv'), index=False, encoding='utf-8')
        i.to_csv(os.path.join(OUT, f'{nom}_ingreso.csv'), index=False, encoding='utf-8')
        print(f'Cohorte {nom}: {i.shape[0]} estudiantes · {m.shape[0]} registros de notas')


if __name__ == '__main__':
    main()
