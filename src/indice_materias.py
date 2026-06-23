"""
Calculo reproducible del indice de criticidad por materia.
CRISP-DM Fase 2 - Universidad de los Llanos - Ing. de Sistemas (cohortes 2017-2 / 2018-1).

Indice = 0.70*tasa_reprob_norm + 0.30*rep_media_norm  (centrado en reprobacion)
(normalizacion min-max sobre las materias con N >= N_MIN).

Uso:  python src/indice_materias.py   ->  genera src/materias_criticas.csv
"""
import os
import pandas as pd

PROG = 'INGENIERIA DE SISTEMAS'
COHORTES = ['2017-2', '2018-1']
OBS_VALIDAS = {'N', 'H', 'F', 'R', 'TG'}   # observaciones con nota valida
N_MIN = 20                                  # materias cursadas por >= 20 estudiantes
PESOS = {'reprobacion': 0.70, 'repitencia': 0.30}

_BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(_BASE), 'Datos')
OUT_CSV = os.path.join(_BASE, 'materias_criticas.csv')


def calcular_indice(data_dir=DATA_DIR):
    mat = pd.read_excel(os.path.join(data_dir, 'detalle_materias.xlsx'))
    mat = mat[(mat['PROGRAMA'].str.strip().str.upper() == PROG) &
              (mat['COHORTE'].astype(str).str.strip().isin(COHORTES))].copy()
    mat['OBS'] = mat['OBSERVACION'].astype(str).str.strip().str.upper()

    val = mat[mat['OBS'].isin(OBS_VALIDAS) & mat['DEFINITIVA'].notna()].copy()
    ult = (val.sort_values('PERIODO_INSCRIPCION', ascending=False)
              .drop_duplicates(subset=['CODIGO_INST', 'MATERIA'], keep='first'))
    veces = val.groupby(['CODIGO_INST', 'MATERIA']).size().reset_index(name='veces')

    filas = []
    for materia, s in ult.groupby(ult['MATERIA'].str.strip()):
        N = len(s)
        if N < N_MIN:
            continue
        n_rep = int((s['DEFINITIVA'] < 3.0).sum())
        prom = s.loc[s['DEFINITIVA'] >= 3.0, 'DEFINITIVA'].mean()
        repm = veces.loc[veces['MATERIA'].str.strip() == materia, 'veces'].mean()
        filas.append({'materia': materia, 'N': N, 'reprobados': n_rep,
                      'tasa_reprobacion': round(n_rep / N, 4),
                      'promedio_aprobados': round(prom, 3),
                      'repitencia_media': round(repm, 3)})

    d = pd.DataFrame(filas).dropna(subset=['promedio_aprobados'])
    nm = lambda x: (x - x.min()) / (x.max() - x.min())
    d['indice'] = (PESOS['reprobacion'] * nm(d['tasa_reprobacion']) +
                   PESOS['repitencia']  * nm(d['repitencia_media'])).round(4)
    d = d.sort_values('indice', ascending=False).reset_index(drop=True)
    d.insert(0, 'rank', d.index + 1)
    # modelable: clase positiva suficiente (>= 10 reprobados) para un clasificador fiable
    d['modelable'] = d['reprobados'] >= 10
    return d


if __name__ == '__main__':
    d = calcular_indice()
    d.to_csv(OUT_CSV, index=False, encoding='utf-8')
    print(f'[OK] {OUT_CSV}  ({len(d)} materias con N>={N_MIN})')
    print(d.head(8).to_string(index=False))
