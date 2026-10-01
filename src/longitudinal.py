"""
longitudinal.py — WP-OE1.4 · Sub-modelos por corte semestral

Cambia la pregunta del modelo. Hasta ahora era:

    "¿Este estudiante activará el art. 19 en algún momento de su carrera?"
    (usando solo datos de ingreso y primer semestre)

Ahora es, para cada corte k:

    "Dado que este estudiante llegó al corte k SIN haber activado el art. 19,
     ¿lo activará después?"
    (usando toda la información acumulada hasta k)

Esto resuelve el problema detectado en RC-035: el 44 % de los eventos ocurre en
el primer semestre, donde `prom_sem1` es contemporáneo al evento y no lo predice.
Al condicionar a "haber sobrevivido hasta k", esos casos salen de la población en
riesgo y lo que queda es predicción genuina.

Incorpora además las variables normativas identificadas en RC-014 y nunca usadas:
    · promedio ponderado acumulado hasta k
    · % de créditos reprobados acumulado y del último periodo
    · activaciones del art. 20 (>50 % de créditos reprobados) acumuladas
    · máximo de veces que ha cursado una misma asignatura (arts. 21-22)
    · créditos cursados y nº de asignaturas

Reglas heredadas:
    RC-008  Un sub-modelo por corte; nunca se mezclan cortes en un entrenamiento.
            Corte modelable solo si n >= 60 y eventos futuros >= 15.
    RC-036  Con la FCBI completa, los cortes 1-3 son viables.
    RC-021  Validación anidada obligatoria en toda comparación de algoritmos.

Uso:  python src/longitudinal.py
Salidas: src/longitudinal_dataset_k{1,2,3}.csv · src/longitudinal_resultados.csv
"""
import os, sys, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import (cargar_datos, OBS_VALIDAS, _periodo_a_orden,
                           _es_periodo_regular, PROGRAMAS_FCBI)
from comparacion_estadistica import comparar

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import average_precision_score, roc_auc_score

SEED = 42
SRC = os.path.dirname(os.path.abspath(__file__))
N_REP = 10
CORTES = [1, 2, 3]
MIN_N, MIN_EV = 60, 15          # regla de viabilidad RC-008

# Variables de ingreso (disponibles en cualquier corte)
INGRESO = ['icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat',
           'estrato', 'log_ingresos', 'sisben_nivel', 'repitio_escolar',
           'sexo', 'tipo_plantel', 'zona_rural', 'nivel_edu_max_padres',
           'cohorte_encoded']

# Variables acumuladas hasta el corte (las nuevas — arts. 19-22)
ACUMULADAS = ['prom_ponderado_acum', 'pct_creditos_reprob_acum',
              'pct_creditos_reprob_ultimo', 'n_art20_acum', 'max_veces_cursado',
              'creditos_acum', 'n_asignaturas_acum']


def panel_estudiante_periodo(mat, clave_curso='MATERIA'):
    """Construye el panel (estudiante × periodo) con acumulados y eventos.

    `clave_curso`: 'MATERIA' (histórico) o 'CODIGO_CANONICO' (equivalencias entre
    planes, src/equivalencias.py) para contar repeticiones del mismo curso."""
    m = mat.copy()
    if clave_curso != 'MATERIA':
        from equivalencias import normalizar_materias
        m = normalizar_materias(m)
    m['_CURSO'] = m['MATERIA'] if clave_curso == 'MATERIA' else m['CURSO_INTENTOS']
    m['OBS'] = m['OBSERVACION'].astype(str).str.strip().str.upper()
    m['ord'] = m['PERIODO_INSCRIPCION'].map(_periodo_a_orden)
    m['regular'] = m['PERIODO_INSCRIPCION'].map(_es_periodo_regular)
    v = m[m['OBS'].isin(OBS_VALIDAS) & m['DEFINITIVA'].notna()].copy()
    v = v.sort_values(['CODIGO_INST', 'ord'])
    v['reprob'] = (v['DEFINITIVA'] < 3.0).astype(int)
    v['vez'] = v.groupby(['CODIGO_INST', '_CURSO']).cumcount() + 1
    v['num'] = v['DEFINITIVA'] * v['CREDITOS']
    v['crep'] = v['CREDITOS'] * v['reprob']

    per = (v.groupby(['CODIGO_INST', 'ord'])
           .agg(creditos=('CREDITOS', 'sum'), cred_reprob=('crep', 'sum'),
                num=('num', 'sum'), n_asig=('MATERIA', 'size'),
                regular=('regular', 'max'), max_vez=('vez', 'max'))
           .reset_index().sort_values(['CODIGO_INST', 'ord']))

    g = per.groupby('CODIGO_INST')
    per['k'] = g.cumcount() + 1                       # índice de periodo cursado
    per['creditos_acum'] = g['creditos'].cumsum()
    per['cred_reprob_acum'] = g['cred_reprob'].cumsum()
    per['num_acum'] = g['num'].cumsum()
    per['n_asignaturas_acum'] = g['n_asig'].cumsum()
    per['prom_ponderado_acum'] = per['num_acum'] / per['creditos_acum']
    per['pct_creditos_reprob_acum'] = per['cred_reprob_acum'] / per['creditos_acum']
    per['pct_creditos_reprob_ultimo'] = per['cred_reprob'] / per['creditos']
    per['max_veces_cursado'] = g['max_vez'].cummax()

    # Art. 20: reprueba >50 % de los créditos del periodo (restricción de carga)
    per['art20'] = ((per['pct_creditos_reprob_ultimo'] > 0.5) &
                    (per['pct_creditos_reprob_ultimo'] < 1)).astype(int)
    per['n_art20_acum'] = per.groupby('CODIGO_INST')['art20'].cumsum()

    # Art. 19: evento
    r4 = (v[(v['vez'] >= 4) & (v['reprob'] == 1)]
          .groupby(['CODIGO_INST', 'ord']).size().reset_index(name='rep4'))
    per = per.merge(r4, on=['CODIGO_INST', 'ord'], how='left').fillna({'rep4': 0})
    per['evento_art19'] = (((per['pct_creditos_reprob_ultimo'] == 1) &
                            (per['prom_ponderado_acum'] < 3.0) & per['regular']) |
                           (per['rep4'] > 0)).astype(int)
    return per


def dataset_corte(per, base, k):
    """
    Población en riesgo en el corte k: cursó al menos k periodos y NO había
    activado el art. 19 hasta k (inclusive). Target: lo activa después de k.
    """
    hasta_k = per[per['k'] <= k]
    ya = set(hasta_k[hasta_k['evento_art19'] == 1]['CODIGO_INST'].astype(str))
    despues = per[(per['k'] > k) & (per['evento_art19'] == 1)]
    fut = set(despues['CODIGO_INST'].astype(str))

    snap = per[per['k'] == k].copy()                  # foto al cierre del corte
    snap['cod'] = snap['CODIGO_INST'].astype(str)
    snap = snap[~snap['cod'].isin(ya)]                # en riesgo: aún no activó
    snap['y'] = snap['cod'].isin(fut).astype(int)

    d = snap[['cod', 'y'] + ACUMULADAS].merge(
        base, left_on='cod', right_on='CODIGO_INST', how='inner')
    return d.dropna(subset=INGRESO + ACUMULADAS + ['y'])


def rf():
    return RandomForestClassifier(n_estimators=200, max_depth=4,
                                  random_state=SEED, n_jobs=-1)


def evaluar(X, y, n_rep=N_REP):
    ap, au = [], []
    for r in range(n_rep):
        cv = StratifiedKFold(5, shuffle=True, random_state=SEED + r)
        p = np.zeros(len(y), dtype=float)
        for tr, te in cv.split(X, y):
            p[te] = rf().fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
        ap.append(average_precision_score(y, p)); au.append(roc_auc_score(y, p))
    return np.array(ap), float(np.mean(au))


def construir_datasets():
    """Fase 1 — construye y persiste los datasets por corte (lectura de Excel)."""
    car, mat, he, pc, ps, pob = cargar_datos(PROGRAMAS_FCBI)
    base = pd.read_csv(os.path.join(SRC, 'df_master_fcbi.csv'))
    base['CODIGO_INST'] = base['CODIGO_INST'].astype(str)
    per = panel_estudiante_periodo(mat)
    per.to_csv(os.path.join(SRC, 'longitudinal_panel.csv'), index=False)
    print(f'Panel estudiante-periodo: {len(per)} filas · '
          f'{per.CODIGO_INST.nunique()} estudiantes\n')
    for k in CORTES:
        d = dataset_corte(per, base, k)
        y = d['y'].values.astype(int)
        viable = (len(y) >= MIN_N and int(y.sum()) >= MIN_EV)
        d.to_csv(os.path.join(SRC, f'longitudinal_dataset_k{k}.csv'), index=False)
        print(f'  corte {k}: en riesgo {len(y)} · eventos futuros {int(y.sum())} '
              f'({y.mean():.1%}) · {"VIABLE" if viable else "NO VIABLE"}')
    print('\n[OK] datasets persistidos. Ahora: python src/longitudinal.py evaluar [k]')


def main(solo_k=None):
    """Fase 2 — evalúa los cortes ya construidos."""
    filas = []
    for k in CORTES:
        if solo_k and k != solo_k:
            continue
        f = os.path.join(SRC, f'longitudinal_dataset_k{k}.csv')
        if not os.path.exists(f):
            print(f'[!] falta {f} — ejecuta antes: python src/longitudinal.py datasets')
            continue
        d = pd.read_csv(f)
        y = d['y'].values.astype(int)
        n, ev = len(y), int(y.sum())
        viable = (n >= MIN_N and ev >= MIN_EV)
        print(f'═══ CORTE {k} · en riesgo {n} · eventos futuros {ev} '
              f'({y.mean():.1%}) · {"VIABLE" if viable else "NO VIABLE"} ═══')
        if not viable:
            print('   (se omite: no cumple la regla de RC-008)\n'); continue

        ap_ing, auc_ing = evaluar(d[INGRESO].values, y)
        ap_ac, auc_ac = evaluar(d[ACUMULADAS].values, y)
        ap_tod, auc_tod = evaluar(d[INGRESO + ACUMULADAS].values, y)
        base_pr = y.mean()
        print(f'   línea base AUC-PR (azar) = {base_pr:.4f}')
        for nom, ap, auc in [('Solo ingreso', ap_ing, auc_ing),
                             ('Solo acumuladas (arts. 19-22)', ap_ac, auc_ac),
                             ('Ingreso + acumuladas', ap_tod, auc_tod)]:
            print(f'   {nom:32s} AUC-PR={ap.mean():.4f} ± {ap.std():.4f}  '
                  f'AUC-ROC={auc:.3f}  lift={ap.mean()/base_pr:.2f}x')
            filas.append({'corte': k, 'conjunto': nom, 'n': n, 'eventos': ev,
                          'baseline': round(base_pr, 4),
                          'AUC_PR': round(ap.mean(), 4), 'sd': round(ap.std(), 4),
                          'AUC_ROC': round(auc, 4),
                          'lift': round(ap.mean() / base_pr, 2)})
        c = comparar(ap_tod, ap_ing, 'Ingreso + acumuladas', 'Solo ingreso')
        print(f'   ¿Aportan las variables acumuladas? Δ={c["diferencia"]:+.4f} '
              f'p={c["p_valor"]:.3f}')
        print(f'      {c["veredicto"][:74]}\n')
        filas.append({'corte': k, 'conjunto': 'CONTRASTE acumuladas vs ingreso',
                      'n': n, 'eventos': ev, 'baseline': round(base_pr, 4),
                      'AUC_PR': round(c['diferencia'], 4), 'sd': None,
                      'AUC_ROC': None, 'lift': round(c['p_valor'], 4)})

    out = os.path.join(SRC, 'longitudinal_resultados.csv')
    nuevo = pd.DataFrame(filas)
    if os.path.exists(out) and solo_k:
        prev = pd.read_csv(out)
        nuevo = pd.concat([prev[prev['corte'] != solo_k], nuevo], ignore_index=True)
    nuevo.sort_values(['corte', 'conjunto']).to_csv(out, index=False)
    print(f'[OK] {out}')


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'todo'
    if arg == 'datasets':
        construir_datasets()
    elif arg == 'evaluar':
        main(int(sys.argv[2]) if len(sys.argv) > 2 else None)
    else:
        construir_datasets(); main()
