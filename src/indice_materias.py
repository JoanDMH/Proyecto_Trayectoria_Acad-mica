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
OBS_VALIDAS = {'N', 'C', 'H'}   # nota valida (C = curso intersemestral, incluido jul-2026)
N_MIN = 20                                  # materias cursadas por >= 20 estudiantes
PESOS = {'reprobacion': 0.70, 'repitencia': 0.30}

_BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(_BASE), 'Datos')
OUT_CSV = os.path.join(_BASE, 'materias_criticas.csv')
OUT_CSV_CANON = os.path.join(_BASE, 'materias_criticas_canonicas.csv')


def calcular_indice(data_dir=DATA_DIR, canonico=False, mat=None):
    """canonico=True agrupa por curso canónico entre planes (src/equivalencias.py):
    p. ej. MATEMATICAS II (2011) y CALCULO INTEGRAL (2018) cuentan como un solo curso.
    `mat` permite pasar un detalle de materias ya cargado (cohortes nuevas)."""
    if mat is None:
        mat = pd.read_excel(os.path.join(data_dir, 'detalle_materias_recod.xlsx'))
    if canonico:
        import sys
        sys.path.insert(0, _BASE)
        from equivalencias import normalizar_materias
        mat = normalizar_materias(mat)
        mat['MATERIA_ORIGINAL'] = mat['MATERIA']
        mat['MATERIA'] = mat['MATERIA_CANONICA']
    mat = mat[(mat['PROGRAMA'].str.strip().str.upper() == PROG) &
              (mat['COHORTE'].astype(str).str.strip().isin(COHORTES))].copy()
    mat['OBS'] = mat['OBSERVACION'].astype(str).str.strip().str.upper()

    val = mat[mat['OBS'].isin(OBS_VALIDAS) & mat['DEFINITIVA'].notna()].copy()
    ult = (val.sort_values('PERIODO_INSCRIPCION', ascending=False)
              .drop_duplicates(subset=['CODIGO_INST', 'MATERIA'], keep='first'))
    if canonico:   # intentos por curso real; una fusión n:1 no cuenta como repetición
        veces = (val.groupby(['CODIGO_INST', 'MATERIA', 'CURSO_INTENTOS']).size()
                    .groupby(level=[0, 1]).max().reset_index(name='veces'))
    else:
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
    import sys
    canon = '--canonico' in sys.argv
    d = calcular_indice(canonico=canon)
    out = OUT_CSV_CANON if canon else OUT_CSV
    d.to_csv(out, index=False, encoding='utf-8')
    print(f'[OK] {out}  ({len(d)} materias con N>={N_MIN})')
    print(d.head(8).to_string(index=False))
