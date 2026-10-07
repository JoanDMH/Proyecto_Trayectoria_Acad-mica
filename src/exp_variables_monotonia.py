# -*- coding: utf-8 -*-
"""
exp_variables_monotonia.py — Experimento pre-registrado (oct-2026, RC-052/RC-053)
Pre-registro: docs/PREREGISTRO_EXP_VARIABLES_MONOTONIA.md (escrito ANTES de ejecutar).

Dos preguntas, mismos datos, mismas semillas que I-3 bis (RC-033) e I-5d (RC-049):

  E1 · ¿Alguna de las 13 variables excluidas de S3 (p. ej. repitio_escolar) mejora
       a S3 al añadirla?  Etapa 1 = cribado con hiperparámetros fijos (los desplegados);
       Etapa 2 = confirmación con validación anidada completa para toda variable que
       en el cribado gane ≥ 0,01, y siempre para repitio_escolar.
  E2 · ¿Imponer monotonía (más promedio / más Saber 11 nunca sube el riesgo ni baja
       la graduación) cuesta capacidad predictiva?  Validación anidada completa.

Uso (se reanuda solo; el entorno corta a los 180 s):
    python exp_variables_monotonia.py cribado      # E1 etapa 1
    python exp_variables_monotonia.py anidado      # E1 etapa 2 + E2
    python exp_variables_monotonia.py informe
"""
import json, os, sys, time, warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold

SRC = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(SRC, '_cache_exp_oct')
os.makedirs(CACHE, exist_ok=True)
SEED, N_REP, N_EXT, N_INT = 42, 10, 5, 4
PRESUPUESTO = float(os.environ.get('PRESUPUESTO', 140))   # no se inicia un pliegue después de este tiempo
T0 = time.time()

S3 = ['prom_sem1', 'sin_primer_semestre', 'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat']
EXCLUIDAS = ['repitio_escolar', 'sexo', 'nivel_edu_padre', 'nivel_edu_madre', 'nivel_edu_max_padres',
             'estrato', 'log_ingresos', 'sisben_nivel', 'tipo_plantel', 'zona_rural', 'vive_con',
             'situacion_padres', 'cohorte_encoded']
OBJ = {'art19': {'col': 'bajo_rendimiento_art19', 'expuestos': True, 'signo': -1,
                 'fijo': dict(max_depth=3, max_features=None, min_samples_leaf=1)},
       'grad': {'col': 'graduado', 'expuestos': False, 'signo': +1,
                'fijo': dict(max_depth=4, max_features=None, min_samples_leaf=1)}}
GRID = {'n_estimators': [150], 'max_depth': [2, 3, 4, None], 'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', None]}          # idéntica a entrenar_i3bis.py


def cargar(obj, variables):
    d = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'))
    if OBJ[obj]['expuestos']:
        d = d[d['tiene_actividad_academica'] == 1]
    return d[variables].values.astype(float), d[OBJ[obj]['col']].astype(int).values


def mono(obj, variables, cuales):
    """Vector monotonic_cst: −1 riesgo / +1 graduación en las variables indicadas."""
    s = OBJ[obj]['signo']
    return [s if v in cuales else 0 for v in variables]


def configs(fase):
    c = []
    for o in OBJ:
        if fase == 'cribado':
            c.append((o, 'S3', S3, None, 'fijo'))
            c += [(o, f'S3+{v}', S3 + [v], None, 'fijo') for v in EXCLUIDAS]
            c.append((o, 'S3+todas', S3 + EXCLUIDAS, None, 'fijo'))
        else:
            c.append((o, 'S3', S3, None, 'anidado'))
            for v in candidatas(o):
                c.append((o, f'S3+{v}', S3 + [v], None, 'anidado'))
            c.append((o, 'S3 monotono (promedio y Saber 11)', S3, S3[:1] + S3[2:], 'anidado'))
            c.append((o, 'S3 monotono (solo promedio)', S3, ['prom_sem1'], 'anidado'))
    return c


def ruta(o, nombre, modo):
    return os.path.join(CACHE, f'{o}__{modo}__{nombre}.json'.replace('/', '-'))


def correr(o, nombre, variables, monot, modo):
    r = ruta(o, nombre, modo)
    res = json.load(open(r, encoding='utf8')) if os.path.exists(r) else \
        {'objetivo': o, 'nombre': nombre, 'modo': modo, 'variables': variables, 'monotonia': monot,
         'ap': [], 'roc': [], 'probas': [], 'hiper': []}
    X, y = cargar(o, variables)
    cst = mono(o, variables, monot) if monot else None
    while len(res['ap']) < N_REP:
        rep = len(res['ap'])
        ext = StratifiedKFold(N_EXT, shuffle=True, random_state=SEED + rep)
        inn = StratifiedKFold(N_INT, shuffle=True, random_state=SEED + 100 + rep)
        # Avance guardado por pliegue: una repetición anidada tarda ~110 s y el entorno corta a los 180 s
        par = res.get('parcial') or {'rep': rep, 'p': [0.0] * len(y), 'hechos': [], 'hiper': []}
        p = np.array(par['p'])
        for k, (tr, te) in enumerate(ext.split(X, y)):
            if k in par['hechos']:
                continue
            if time.time() - T0 > PRESUPUESTO:
                res['parcial'] = par
                json.dump(res, open(r, 'w', encoding='utf8'), ensure_ascii=False)
                return False
            if modo == 'fijo':
                est = RandomForestClassifier(n_estimators=150, random_state=SEED, n_jobs=-1,
                                             monotonic_cst=cst, **OBJ[o]['fijo']).fit(X[tr], y[tr])
            else:
                gs = GridSearchCV(RandomForestClassifier(random_state=SEED, n_jobs=1, monotonic_cst=cst),
                                  GRID, cv=inn, scoring='average_precision', n_jobs=-1).fit(X[tr], y[tr])
                est = gs.best_estimator_
                par['hiper'].append({k2: str(v) for k2, v in gs.best_params_.items()})
            p[te] = est.predict_proba(X[te])[:, 1]
            par['p'] = p.tolist(); par['hechos'].append(k)
            if modo != 'fijo':
                res['parcial'] = par
                json.dump(res, open(r, 'w', encoding='utf8'), ensure_ascii=False)
        res.pop('parcial', None)
        res['hiper'] += par['hiper']
        res['ap'].append(float(average_precision_score(y, p)))
        res['roc'].append(float(roc_auc_score(y, p)))
        res['probas'].append(np.round(p, 5).tolist())
        res['n'], res['positivos'] = int(len(y)), int(y.sum())
        json.dump(res, open(r, 'w', encoding='utf8'), ensure_ascii=False)
        print(f'  {o:5s} {modo:7s} {nombre:38s} rep {rep + 1:2d}  AUC-PR {res["ap"][-1]:.3f}', flush=True)
    return True


def leer(o, nombre, modo):
    r = ruta(o, nombre, modo)
    return json.load(open(r, encoding='utf8')) if os.path.exists(r) else None


def nb(a, b):
    """t pareada corregida de Nadeau-Bengio sobre las 10 repeticiones (como en RC-033)."""
    d = np.asarray(a) - np.asarray(b)
    k = len(d)
    if np.allclose(d, 0):
        return float(d.mean()), 1.0
    t = d.mean() / np.sqrt((1 / k + (1 / N_EXT) / (1 - 1 / N_EXT)) * d.var(ddof=1))
    return float(d.mean()), float(2 * (1 - stats.t.cdf(abs(t), k - 1)))


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for i, j in enumerate(o):
        run = max(run, min(1, (m - i) * ps[j])); adj[j] = run
    return adj


def candidatas(o):
    """Variables que pasan al anidado: Δ ≥ 0,01 en el cribado, y siempre repitio_escolar."""
    ref = leer(o, 'S3', 'fijo')
    out = ['repitio_escolar']
    for v in EXCLUIDAS:
        r = leer(o, f'S3+{v}', 'fijo')
        if ref and r and len(r['ap']) == N_REP and np.mean(r['ap']) - np.mean(ref['ap']) >= 0.01 and v not in out:
            out.append(v)
    return out


def tabla(o, modo, nombres):
    ref = leer(o, 'S3', modo)
    filas = []
    if not ref or len(ref['ap']) < N_REP:
        return pd.DataFrame()
    for n in nombres:
        r = leer(o, n, modo)
        if not r or len(r['ap']) < N_REP:
            continue
        dif, p = nb(r['ap'], ref['ap']) if n != 'S3' else (0.0, np.nan)
        filas.append({'objetivo': o, 'modo': modo, 'configuracion': n, 'AUC_PR': np.mean(r['ap']),
                      'sd': np.std(r['ap']), 'AUC_ROC': np.mean(r['roc']), 'delta': dif, 'p': p})
    t = pd.DataFrame(filas)
    if t.empty:
        return t
    m = t['configuracion'] != 'S3'
    if m.sum():
        t.loc[m, 'p_holm'] = holm(t.loc[m, 'p'].values)
    return t


if __name__ == '__main__':
    fase = sys.argv[1] if len(sys.argv) > 1 else 'cribado'
    if fase in ('cribado', 'anidado'):
        pend = 0
        for c in configs(fase):
            if not correr(*c):
                pend += 1
        print('PENDIENTE' if pend else 'COMPLETO', f'{time.time() - T0:.0f} s')
    else:
        out = []
        for o in OBJ:
            out.append(tabla(o, 'fijo', ['S3'] + [f'S3+{v}' for v in EXCLUIDAS] + ['S3+todas']))
            out.append(tabla(o, 'anidado', ['S3'] + [f'S3+{v}' for v in candidatas(o)] +
                             ['S3 monotono (promedio y Saber 11)', 'S3 monotono (solo promedio)']))
        t = pd.concat(out, ignore_index=True)
        t.round(4).to_csv(os.path.join(SRC, 'exp_variables_monotonia.csv'), index=False)
        with pd.option_context('display.width', 200, 'display.max_rows', 200):
            print(t.round(4).to_string(index=False))
