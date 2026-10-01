"""
entrenar_mvp.py — Modelos empaquetados para el software de trayectoria (MVP, CICI 2026)

Tres modelos, todos bajo el protocolo del proyecto (SEED=42, CV-5 estratificada repetida,
validación ANIDADA para comparar algoritmos, AUC-PR como métrica primaria con su línea
base, t de Nadeau-Bengio, umbral de relevancia ΔAUC-PR ≥ 0,03, parsimonia ante empate):

  M1 · alerta_art19      Bajo rendimiento art. 19, cierre del 1.er semestre. Random Forest
                         sobre S3 (RC-033: AUC-PR 0,745 ± 0,025). Aquí se EMPAQUETA y se
                         evalúa su CALIBRACIÓN (E-CALIB / D-APP).
  M2 · graduacion        Graduación, misma comparación de 5 algoritmos sobre S3 (I-5d).
  M3 · trayectoria_k     Riesgo semestre a semestre: en el corte k (1-3), estudiante que aún
                         NO ha reprobado más de la mitad de los créditos de un periodo
                         (supuesto del art. 20) → ¿lo hará después? Sistemas + Electrónica
                         (poblaciones comparables, RC-036), k contado SOLO sobre periodos
                         regulares (corrige el conteo de longitudinal.py, que incluía los
                         intersemestrales -0 como cortes).

Ejecución por etapas (cada una cabe en ~3 min y se cachea en src/_cache_mvp/):
    python src/entrenar_mvp.py calib              # M1: calibración (hiperparámetros fijos)
    python src/entrenar_mvp.py art19              # M1: ajuste final + umbrales + paquete
    python src/entrenar_mvp.py grad <rep> [algo]  # M2: una repetición anidada (0-9)
    python src/entrenar_mvp.py grad_final         # M2: consolidar, elegir y empaquetar
    python src/entrenar_mvp.py long <k> <rep>     # M3: una repetición anidada del corte k
    python src/entrenar_mvp.py long_final         # M3: consolidar y empaquetar
Salidas: modelos/*.joblib, modelos/tarjetas/*.json, src/mvp_*.csv
"""
import os, sys, json, time, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, joblib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import (average_precision_score, roc_auc_score, brier_score_loss,
                             log_loss, precision_score, recall_score)
from xgboost import XGBClassifier
import sklearn, xgboost

SEED = 42
SRC = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(SRC)
OUT = os.path.join(RAIZ, 'modelos')
TARJ = os.path.join(OUT, 'tarjetas')
CACHE = os.path.join(SRC, '_cache_mvp')
for _d in (OUT, TARJ, CACHE):
    os.makedirs(_d, exist_ok=True)
N_REP, N_EXT, N_INT = 10, 5, 4
DELTA = 0.03
S3 = ['prom_sem1', 'sin_primer_semestre', 'icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat']
PARSIMONIA = ['Regresión Logística (L2)', 'Árbol de Decisión', 'Random Forest', 'XGBoost', 'SVM (RBF)']


def versiones():
    return {'python': sys.version.split()[0], 'scikit-learn': sklearn.__version__,
            'xgboost': xgboost.__version__, 'pandas': pd.__version__, 'numpy': np.__version__}


def algoritmos():
    """Rejillas idénticas a I-3 bis (entrenar_i3bis.py, presupuesto equilibrado RC-025)."""
    return {
        'Regresión Logística (L2)': (
            Pipeline([('sc', StandardScaler()),
                      ('clf', LogisticRegression(random_state=SEED, max_iter=2000))]),
            {'clf__C': [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 100.0],
             'clf__class_weight': [None, 'balanced']}),
        'Árbol de Decisión': (
            DecisionTreeClassifier(random_state=SEED),
            {'max_depth': [2, 3, 4, 5], 'min_samples_leaf': [1, 2, 4],
             'criterion': ['gini', 'entropy']}),
        'Random Forest': (
            RandomForestClassifier(random_state=SEED, n_jobs=1),
            {'n_estimators': [150], 'max_depth': [2, 3, 4, None],
             'min_samples_leaf': [1, 2, 4], 'max_features': ['sqrt', None]}),
        'SVM (RBF)': (
            Pipeline([('sc', StandardScaler()),
                      ('clf', SVC(random_state=SEED, probability=True))]),
            {'clf__C': [0.1, 0.5, 1.0, 5.0, 10.0], 'clf__gamma': ['scale', 'auto', 0.01, 0.1]}),
        'XGBoost': (
            XGBClassifier(random_state=SEED, eval_metric='logloss', n_jobs=1, min_child_weight=1),
            {'n_estimators': [100, 200], 'max_depth': [2, 3],
             'learning_rate': [0.03, 0.1], 'reg_lambda': [0.5, 1.0, 2.0]}),
    }


def rf_modal():
    """Configuración más frecuente en los pliegues de I-3 bis (bitácora 20260915_090639)."""
    return RandomForestClassifier(n_estimators=150, max_depth=3, max_features=None,
                                  min_samples_leaf=1, random_state=SEED, n_jobs=-1)


def ece(y, p, bins=5):
    """Error de calibración esperado con bins de igual frecuencia (n pequeño)."""
    q = np.quantile(p, np.linspace(0, 1, bins + 1)); q[0], q[-1] = -1, 2
    idx = np.digitize(p, q[1:-1])
    return float(sum(abs(y[idx == b].mean() - p[idx == b].mean()) * (idx == b).mean()
                     for b in range(bins) if (idx == b).any()))


def curva_umbral(y, p, paso=0.01):
    filas = []
    for u in np.round(np.arange(0.01, 0.96, paso), 2):
        yp = (p >= u).astype(int)
        if yp.sum() == 0:
            break
        filas.append({'umbral': float(u), 'recall': recall_score(y, yp),
                      'precision': precision_score(y, yp, zero_division=0),
                      'alertas': int(yp.sum()), 'pct_cohorte': float(yp.mean())})
    return pd.DataFrame(filas)


def niveles_alerta(y, p):
    """
    Tres puntos de operación (RC-035), definidos por regla y no a ojo:
      confirmado  · el umbral MÁS BAJO con precisión ≥ 0,90 (máxima cobertura sin
                    apenas falsas alarmas); si no existe, el de máxima precisión
      equilibrado · regla RC-034: recall ≥ 0,75 y, entre ellos, máxima precisión
      cobertura   · el umbral más alto que aún detecta el 100 % de los casos
    """
    c = curva_umbral(y, p)
    alta = c[c['precision'] >= 0.90]
    conf = alta.iloc[0] if len(alta) else c.loc[c['precision'].idxmax()]
    eq = c[c['recall'] >= 0.75]
    eq = eq.loc[eq['precision'].idxmax()] if len(eq) else c.iloc[0]
    tot = c[c['recall'] >= 0.999]
    tot = tot.iloc[-1] if len(tot) else c.iloc[0]
    fmt = lambda r: {k: (round(float(v), 4) if k != 'alertas' else int(v)) for k, v in r.items()}
    return {'confirmado': fmt(conf), 'equilibrado': fmt(eq), 'cobertura': fmt(tot)}, c


def datos_sistemas(col, solo_expuestos):
    df = pd.read_csv(os.path.join(SRC, 'df_master_limpio.csv'), dtype={'CODIGO_INST': str})
    if solo_expuestos:
        df = df[df['tiene_actividad_academica'] == 1]
    df = df.dropna(subset=S3 + [col])
    return df, df[S3].values, df[col].astype(int).values


def guardar_tarjeta(nombre, tarjeta):
    with open(os.path.join(TARJ, f'{nombre}.json'), 'w', encoding='utf-8') as f:
        json.dump(tarjeta, f, ensure_ascii=False, indent=1, default=float)


# ── M1 · calibración ─────────────────────────────────────────────────────────
def cmd_calib():
    df, X, y = datos_sistemas('bajo_rendimiento_art19', True)
    variantes = {'sin calibrar': None, 'Platt (sigmoide)': 'sigmoid', 'isotónica': 'isotonic'}
    filas, oof = [], {k: np.zeros(len(y)) for k in variantes}
    t0 = time.time()
    for r in range(N_REP):
        p = {k: np.zeros(len(y)) for k in variantes}
        for tr, te in StratifiedKFold(N_EXT, shuffle=True, random_state=SEED + r).split(X, y):
            for k, met in variantes.items():
                m = rf_modal() if met is None else CalibratedClassifierCV(
                    rf_modal(), method=met, cv=StratifiedKFold(N_INT, shuffle=True, random_state=SEED + 100 + r))
                p[k][te] = m.fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
        for k in variantes:
            oof[k] += p[k] / N_REP
            filas.append({'variante': k, 'rep': r, 'AUC_PR': average_precision_score(y, p[k]),
                          'AUC_ROC': roc_auc_score(y, p[k]), 'Brier': brier_score_loss(y, p[k]),
                          'ECE': ece(y, p[k]), 'logloss': log_loss(y, np.clip(p[k], 1e-4, 1 - 1e-4)),
                          'p_media': p[k].mean()})
    d = pd.DataFrame(filas)
    res = d.groupby('variante').agg(['mean', 'std']).drop(columns='rep')
    res.columns = [f'{a}_{b}' for a, b in res.columns]
    res['prevalencia'] = y.mean()
    res = res.round(4)
    res.to_csv(os.path.join(SRC, 'mvp_calibracion_art19.csv'))
    joblib.dump({'oof': oof, 'y': y, 'cod': df['CODIGO_INST'].values}, os.path.join(CACHE, 'calib_oof.pkl'))
    print(res[['AUC_PR_mean', 'AUC_PR_std', 'Brier_mean', 'ECE_mean', 'logloss_mean', 'p_media_mean']].to_string())
    print(f'prevalencia {y.mean():.4f} · {time.time()-t0:.0f}s')


def cmd_art19():
    """Ajuste final (búsqueda en la rejilla de I-3 bis sobre los 80) + calibración decidida
    por la regla pre-registrada: se adopta la variante calibrada si reduce el Brier y el ECE
    sin perder más de 0,03 de AUC-PR frente a la versión sin calibrar."""
    cal = pd.read_csv(os.path.join(SRC, 'mvp_calibracion_art19.csv'), index_col=0)
    base = cal.loc['sin calibrar']
    cands = [v for v in ['Platt (sigmoide)', 'isotónica']
             if cal.at[v, 'Brier_mean'] < base['Brier_mean'] and cal.at[v, 'ECE_mean'] < base['ECE_mean']
             and base['AUC_PR_mean'] - cal.at[v, 'AUC_PR_mean'] <= DELTA]
    elegida = min(cands, key=lambda v: cal.at[v, 'Brier_mean']) if cands else 'sin calibrar'
    metodo = {'Platt (sigmoide)': 'sigmoid', 'isotónica': 'isotonic'}.get(elegida)

    df, X, y = datos_sistemas('bajo_rendimiento_art19', True)
    base_rf, grid = algoritmos()['Random Forest']
    gs = GridSearchCV(base_rf, grid, cv=StratifiedKFold(N_INT, shuffle=True, random_state=SEED),
                      scoring='average_precision', n_jobs=-1).fit(X, y)
    mejor = gs.best_estimator_
    modelo = mejor if metodo is None else CalibratedClassifierCV(
        mejor, method=metodo, cv=StratifiedKFold(N_EXT, shuffle=True, random_state=SEED)).fit(X, y)

    oof = joblib.load(os.path.join(CACHE, 'calib_oof.pkl'))['oof'][elegida]
    niveles, curva = niveles_alerta(y, oof)
    curva.to_csv(os.path.join(SRC, 'mvp_curva_umbral_art19.csv'), index=False)
    imp = pd.Series(mejor.feature_importances_, index=S3).sort_values(ascending=False)
    canon = pd.read_csv(os.path.join(SRC, 'i3bis_tabla_art19.csv')).set_index('Modelo').loc['Random Forest']
    paquete = {'nombre': 'alerta_art19', 'modelo': modelo, 'features': S3, 'umbrales': niveles,
               'calibracion': elegida, 'version': '1.0-mvp', 'versiones': versiones()}
    joblib.dump(paquete, os.path.join(OUT, 'alerta_art19.joblib'))
    joblib.dump({'cod': df['CODIGO_INST'].values, 'p_oof': oof, 'y': y},
                os.path.join(CACHE, 'oof_art19.pkl'))
    guardar_tarjeta('alerta_art19', {
        'modelo': 'Alerta de bajo rendimiento — art. 19 del Reglamento Estudiantil',
        'pregunta': '¿Este estudiante perderá la calidad de estudiante por bajo rendimiento '
                    '(art. 19) en algún momento de la carrera?',
        'momento_de_uso': 'Al cierre del primer periodo académico',
        'algoritmo': 'Random Forest', 'hiperparametros': gs.best_params_,
        'variables': S3, 'poblacion': 'Ing. de Sistemas, cohortes 2017-2 y 2018-1, expuestos al art. 19',
        'n': int(len(y)), 'positivos': int(y.sum()), 'linea_base_auc_pr': round(float(y.mean()), 4),
        'desempeno_canonico': {'fuente': 'RC-033 (I-3 bis, CV-5×10 anidada)',
                               'auc_pr': float(canon['AUC_PR_media']), 'sd': float(canon['AUC_PR_sd']),
                               'ic95': [float(canon['IC95_lo']), float(canon['IC95_hi'])]},
        'calibracion': {'variante_adoptada': elegida,
                        'tabla': cal[['AUC_PR_mean', 'Brier_mean', 'ECE_mean', 'logloss_mean']].to_dict('index'),
                        'regla': 'se adopta si reduce Brier y ECE sin perder > 0,03 de AUC-PR'},
        'niveles_alerta': niveles,
        'importancia_mdi_referencial': imp.round(4).to_dict(),
        'limitaciones': ['Sin validación externa: todo procede de remuestreo sobre 80 casos (P18).',
                         'El 42 % de los positivos activa el art. 19 en el primer semestre: el modelo los '
                         'detecta, no los anticipa (RC-035). Solo-predictivo: AUC-PR 0,473 (lift 3,10×).',
                         'Etiquetas del reglamento 2022 aplicadas a cohortes regidas por el Acuerdo 015 de '
                         '2003 (D-REGIMEN).',
                         'Para cohortes del plan 2018 el promedio del 1.er semestre se desplaza en promedio '
                         '+0,125 (sale Álgebra Lineal): el ordenamiento se conserva (AUC-PR 0,749) pero los '
                         'umbrales deben revisarse (src/cambio_plan_sensibilidad.csv).'],
        'versiones': versiones()})
    print('calibración adoptada:', elegida, '| mejores hiperparámetros:', gs.best_params_)
    print(json.dumps(niveles, indent=1))


# ── M2 · graduación (I-5d) ───────────────────────────────────────────────────
def cmd_grad(rep, solo=None):
    df, X, y = datos_sistemas('graduado', False)
    outer = StratifiedKFold(N_EXT, shuffle=True, random_state=SEED + rep)
    inner = StratifiedKFold(N_INT, shuffle=True, random_state=SEED + 100 + rep)
    for nom, (base, grid) in algoritmos().items():
        if solo and nom != solo:
            continue
        f = os.path.join(CACHE, f'grad_{rep}_{nom}.pkl')
        if os.path.exists(f):
            continue
        t0 = time.time(); p = np.zeros(len(y)); params = []
        for tr, te in outer.split(X, y):
            gs = GridSearchCV(base, grid, cv=inner, scoring='average_precision', n_jobs=-1).fit(X[tr], y[tr])
            p[te] = gs.predict_proba(X[te])[:, 1]; params.append(gs.best_params_)
        joblib.dump({'p': p, 'ap': average_precision_score(y, p), 'roc': roc_auc_score(y, p),
                     'params': params}, f)
        print(f'rep {rep} · {nom:26s} AUC-PR={average_precision_score(y, p):.4f} ({time.time()-t0:.0f}s)')


def _consolidar(prefijo, nombres, n_rep):
    ap = {n: [] for n in nombres}; roc = {n: [] for n in nombres}; probs = {n: 0 for n in nombres}
    for n in nombres:
        for r in range(n_rep):
            d = joblib.load(os.path.join(CACHE, f'{prefijo}_{r}_{n}.pkl'))
            ap[n].append(d['ap']); roc[n].append(d['roc']); probs[n] = probs[n] + d['p'] / n_rep
    return ap, roc, probs


def elegir(ap, n_train, n_test):
    """Regla pre-registrada (ESPEC_I3): el mejor por AUC-PR media; si la diferencia con un
    rival más parsimonioso no es significativa (Nadeau-Bengio, p≥0,05) o es < 0,03, se
    declara empate y se prefiere el más parsimonioso."""
    from comparacion_estadistica import t_corregido_nadeau_bengio
    orden = sorted(ap, key=lambda k: -np.mean(ap[k]))
    lider = orden[0]; comps = []
    for rival in orden[1:]:
        t, p, dif = t_corregido_nadeau_bengio(np.array(ap[lider]), np.array(ap[rival]), N_EXT)
        comps.append({'lider': lider, 'rival': rival, 'delta': round(float(dif), 4), 'p': round(float(p), 4),
                      'empate': bool(p >= 0.05 or dif < DELTA)})
    empatados = [lider] + [c['rival'] for c in comps if c['empate']]
    elegido = min(empatados, key=lambda k: PARSIMONIA.index(k) if k in PARSIMONIA else 99)
    return elegido, comps


def cmd_grad_final():
    df, X, y = datos_sistemas('graduado', False)
    nombres = list(algoritmos())
    ap, roc, probs = _consolidar('grad', nombres, N_REP)
    tabla = pd.DataFrame({n: {'AUC_PR': np.mean(ap[n]), 'sd': np.std(ap[n]),
                              'IC95_lo': np.percentile(ap[n], 2.5), 'IC95_hi': np.percentile(ap[n], 97.5),
                              'AUC_ROC': np.mean(roc[n])} for n in nombres}).T.sort_values('AUC_PR', ascending=False).round(4)
    tabla['linea_base'] = round(float(y.mean()), 4)
    tabla.to_csv(os.path.join(SRC, 'mvp_graduacion_comparativa.csv'), index_label='Modelo')
    n_te = len(y) // N_EXT; elegido, comps = elegir(ap, len(y) - n_te, n_te)
    pd.DataFrame(comps).to_csv(os.path.join(SRC, 'mvp_graduacion_comparaciones.csv'), index=False)
    base, grid = algoritmos()[elegido]
    gs = GridSearchCV(base, grid, cv=StratifiedKFold(N_INT, shuffle=True, random_state=SEED),
                      scoring='average_precision', n_jobs=-1).fit(X, y)
    oof = probs[elegido]
    c = curva_umbral(y, oof)
    c['f1'] = 2 * c['precision'] * c['recall'] / (c['precision'] + c['recall'] + 1e-9)
    u = float(c.loc[c['f1'].idxmax(), 'umbral'])
    joblib.dump({'nombre': 'graduacion', 'modelo': gs.best_estimator_, 'features': S3,
                 'umbral': u, 'version': '1.0-mvp', 'versiones': versiones()},
                os.path.join(OUT, 'graduacion.joblib'))
    joblib.dump({'cod': df['CODIGO_INST'].values, 'p_oof': oof, 'y': y}, os.path.join(CACHE, 'oof_grad.pkl'))
    guardar_tarjeta('graduacion', {
        'modelo': 'Probabilidad de graduación', 'algoritmo': elegido, 'hiperparametros': gs.best_params_,
        'variables': S3, 'poblacion': 'Ing. de Sistemas 2017-2 y 2018-1 con actividad (n=90)',
        'n': int(len(y)), 'positivos': int(y.sum()), 'linea_base_auc_pr': round(float(y.mean()), 4),
        'comparativa': tabla.to_dict('index'), 'comparaciones': comps,
        'regla': 'ESPEC_I3: mejor AUC-PR; empate (p≥0,05 o Δ<0,03) → más parsimonioso',
        'umbral_referencia': u,
        'limitaciones': ['Ventana de observación ~17 periodos: «no graduado» mezcla abandono y rezago.',
                         'Sin validación externa.', 'Probabilidades sin calibrar: usar como ordenamiento.'],
        'versiones': versiones()})
    print(tabla.to_string()); print('elegido:', elegido); print(pd.DataFrame(comps).to_string())


# ── M3 · trayectoria semestre a semestre (art. 20) ───────────────────────────
ING_LONG = ['icfes_total', 'icfes_mat', 'icfes_lec', 'icfes_nat', 'prog_sistemas']
ACU = ['prom_ponderado_acum', 'pct_creditos_reprob_acum', 'pct_creditos_reprob_ultimo',
       'n_art20_acum', 'max_veces_cursado', 'creditos_acum', 'n_asignaturas_acum']
CORTES = [1, 2, 3]
PROGS_LONG = ['INGENIERIA DE SISTEMAS', 'INGENIERIA ELECTRONICA']


def panel_regular():
    """Panel estudiante × periodo REGULAR. Las notas intersemestrales (-0) se acumulan en el
    siguiente periodo regular (cuentan para el promedio acumulado, art. 40 par. 1) pero no
    abren un corte nuevo. Clave de curso canónica (equivalencias entre planes)."""
    from preprocessing import cargar_datos, OBS_VALIDAS, _periodo_a_orden
    from equivalencias import normalizar_materias
    _, mat, *_ = cargar_datos(PROGS_LONG)
    m = normalizar_materias(mat)
    m = m[m['OBSERVACION'].astype(str).str.upper().isin(OBS_VALIDAS) & m['DEFINITIVA'].notna()].copy()
    m['ord'] = m['PERIODO_INSCRIPCION'].map(_periodo_a_orden)
    m['regular'] = m['PERIODO_INSCRIPCION'].astype(str).str.endswith(('-1', '-2'))
    m = m.sort_values(['CODIGO_INST', 'ord'])
    m['ord_reg'] = m['ord'].where(m['regular'])
    m['ord_reg'] = m.groupby('CODIGO_INST')['ord_reg'].transform(lambda s: s.bfill())
    m = m.dropna(subset=['ord_reg'])
    m['reprob'] = (m['DEFINITIVA'] < 3.0).astype(int)
    m['vez'] = m.groupby(['CODIGO_INST', 'CURSO_INTENTOS']).cumcount() + 1
    m['num'] = m['DEFINITIVA'] * m['CREDITOS']; m['crep'] = m['CREDITOS'] * m['reprob']
    reg = m[m['regular']]
    per_reg = reg.groupby(['CODIGO_INST', 'ord_reg']).agg(cred_p=('CREDITOS', 'sum'), crep_p=('crep', 'sum'))
    per = m.groupby(['CODIGO_INST', 'ord_reg']).agg(creditos=('CREDITOS', 'sum'), cred_reprob=('crep', 'sum'),
                                                    num=('num', 'sum'), n_asig=('CREDITOS', 'size'),
                                                    max_vez=('vez', 'max'))
    per = per.join(per_reg).reset_index().sort_values(['CODIGO_INST', 'ord_reg'])
    per[['cred_p', 'crep_p']] = per[['cred_p', 'crep_p']].fillna(0)
    g = per.groupby('CODIGO_INST')
    per['k'] = g.cumcount() + 1
    per['creditos_acum'] = g['creditos'].cumsum(); per['cred_reprob_acum'] = g['cred_reprob'].cumsum()
    per['num_acum'] = g['num'].cumsum(); per['n_asignaturas_acum'] = g['n_asig'].cumsum()
    per['prom_ponderado_acum'] = per['num_acum'] / per['creditos_acum']
    per['prom_periodo'] = per['num'] / per['creditos']
    per['pct_creditos_reprob_acum'] = per['cred_reprob_acum'] / per['creditos_acum']
    per['pct_creditos_reprob_ultimo'] = np.where(per['cred_p'] > 0, per['crep_p'] / per['cred_p'].clip(lower=1), 0)
    # Art. 20 con el redondeo de su parágrafo: % entero (≥ ,5 sube) > 50.
    # Evento «E20+»: pierde más de la mitad de los créditos del periodo (incluye la pérdida total).
    per['e20'] = (np.floor(per['pct_creditos_reprob_ultimo'] * 100 + 0.5) > 50).astype(int)
    per['n_art20_acum'] = per.groupby('CODIGO_INST')['e20'].cumsum()
    per['max_veces_cursado'] = per.groupby('CODIGO_INST')['max_vez'].cummax()
    per['periodo_txt'] = per['ord_reg'].map(lambda o: f'{int(o)//3}-{int(o)%3}')
    return per


def dataset_corte_e20(per, base, k):
    hasta = per[per['k'] <= k]
    ya = set(hasta[hasta['e20'] == 1]['CODIGO_INST'].astype(str))
    fut = set(per[(per['k'] > k) & (per['e20'] == 1)]['CODIGO_INST'].astype(str))
    sigue = set(per[per['k'] > k]['CODIGO_INST'].astype(str))
    s = per[per['k'] == k].copy(); s['cod'] = s['CODIGO_INST'].astype(str)
    s = s[~s['cod'].isin(ya)]
    s['y'] = s['cod'].isin(fut).astype(int)
    s['continua'] = s['cod'].isin(sigue).astype(int)
    d = s[['cod', 'y', 'continua', 'periodo_txt'] + ACU].merge(base, left_on='cod', right_on='CODIGO_INST', how='inner')
    return d.dropna(subset=ING_LONG + ACU)


def _datos_long(k):
    f = os.path.join(CACHE, f'long_k{k}.pkl')
    if os.path.exists(f):
        return joblib.load(f)
    per = panel_regular()
    per.to_csv(os.path.join(CACHE, 'panel_regular.csv'), index=False)
    base = pd.read_csv(os.path.join(SRC, 'df_master_fcbi.csv'), dtype={'CODIGO_INST': str})
    base = base[base['programa'].isin(PROGS_LONG)]
    for kk in CORTES:
        joblib.dump(dataset_corte_e20(per, base, kk), os.path.join(CACHE, f'long_k{kk}.pkl'))
    return joblib.load(f)


def algoritmos_long():
    """Presupuesto EQUILIBRADO de 8 configuraciones por algoritmo (RC-025), reducido
    respecto a I-3 bis por el límite de cómputo; se declara antes de ver resultados."""
    return {
        'Regresión Logística (L2)': (
            Pipeline([('sc', StandardScaler()), ('clf', LogisticRegression(random_state=SEED, max_iter=2000))]),
            {'clf__C': [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 100.0]}),
        'Random Forest': (
            RandomForestClassifier(random_state=SEED, n_jobs=1, max_features='sqrt'),
            {'n_estimators': [150], 'max_depth': [2, 3, 4, None], 'min_samples_leaf': [1, 4]}),
    }


def cmd_long(k, rep):
    d = _datos_long(k)
    X = d[ING_LONG + ACU].values; y = d['y'].astype(int).values
    outer = StratifiedKFold(N_EXT, shuffle=True, random_state=SEED + rep)
    inner = StratifiedKFold(N_INT, shuffle=True, random_state=SEED + 100 + rep)
    for nom, (base, grid) in algoritmos_long().items():
        f = os.path.join(CACHE, f'longk{k}_{rep}_{nom}.pkl')
        if os.path.exists(f):
            continue
        t0 = time.time(); p = np.zeros(len(y))
        for tr, te in outer.split(X, y):
            gs = GridSearchCV(base, grid, cv=inner, scoring='average_precision', n_jobs=-1).fit(X[tr], y[tr])
            p[te] = gs.predict_proba(X[te])[:, 1]
        joblib.dump({'p': p, 'ap': average_precision_score(y, p), 'roc': roc_auc_score(y, p)}, f)
        print(f'k={k} rep {rep} · {nom:26s} AUC-PR={average_precision_score(y, p):.4f} '
              f'ROC={roc_auc_score(y, p):.3f} ({time.time()-t0:.0f}s)')


def cmd_long_final():
    filas, paquetes, oofs = [], {}, {}
    for k in CORTES:
        d = _datos_long(k)
        X = d[ING_LONG + ACU].values; y = d['y'].astype(int).values
        nombres = list(algoritmos_long())
        ap, roc, probs = _consolidar(f'longk{k}', nombres, N_REP)
        n_te = len(y) // N_EXT; elegido, comps = elegir(ap, len(y) - n_te, n_te)
        sis = (d['prog_sistemas'] == 1).values
        for n in nombres:
            filas.append({'corte': k, 'modelo': n, 'n': len(y), 'eventos': int(y.sum()),
                          'linea_base': round(y.mean(), 4), 'AUC_PR': round(np.mean(ap[n]), 4),
                          'sd': round(np.std(ap[n]), 4), 'AUC_ROC': round(np.mean(roc[n]), 4),
                          'lift': round(np.mean(ap[n]) / y.mean(), 2),
                          'AUC_ROC_sistemas_oof': round(roc_auc_score(y[sis], probs[n][sis]), 4),
                          'n_sistemas': int(sis.sum()), 'eventos_sistemas': int(y[sis].sum()),
                          'elegido': n == elegido})
        base, grid = algoritmos_long()[elegido]
        gs = GridSearchCV(base, grid, cv=StratifiedKFold(N_INT, shuffle=True, random_state=SEED),
                          scoring='average_precision', n_jobs=-1).fit(X, y)
        niveles, _ = niveles_alerta(y, probs[elegido])
        paquetes[k] = {'modelo': gs.best_estimator_, 'algoritmo': elegido, 'hiperparametros': gs.best_params_,
                       'umbrales': niveles, 'n': int(len(y)), 'eventos': int(y.sum()),
                       'comparaciones': comps}
        oofs[k] = pd.DataFrame({'cod': d['cod'].values, 'k': k, 'p_oof': probs[elegido], 'y': y,
                                'continua': d['continua'].values})
    tabla = pd.DataFrame(filas)
    tabla.to_csv(os.path.join(SRC, 'mvp_trayectoria_art20.csv'), index=False)
    joblib.dump({'nombre': 'trayectoria_art20', 'features': ING_LONG + ACU, 'cortes': paquetes,
                 'version': '1.0-mvp', 'versiones': versiones()}, os.path.join(OUT, 'trayectoria_art20.joblib'))
    pd.concat(oofs.values()).to_csv(os.path.join(CACHE, 'oof_trayectoria.csv'), index=False)
    guardar_tarjeta('trayectoria_art20', {
        'modelo': 'Riesgo semestre a semestre — pérdida de más de la mitad de los créditos (art. 20)',
        'pregunta': 'En el corte k, para quien aún no ha reprobado más del 50 % de los créditos de un '
                    'periodo: ¿le ocurrirá en un periodo posterior?',
        'poblacion': 'Ing. de Sistemas + Ing. Electrónica (comparables, RC-036), cohortes 2017-2 y 2018-1',
        'variables': ING_LONG + ACU, 'resultados': filas,
        'cortes': {k: {kk: vv for kk, vv in v.items() if kk != 'modelo'} for k, v in paquetes.items()},
        'limitaciones': ['Señal modesta (cribado, no diagnóstico).',
                         'Quien abandona tras el corte sin reprobar queda como «sin evento» (censura): '
                         'el modelo no predice deserción.',
                         'Entrenado con dos programas; aplicado a Sistemas.', 'Sin validación externa.'],
        'versiones': versiones()})
    print(tabla.to_string(index=False))


if __name__ == '__main__':
    a = sys.argv[1:]
    {'calib': lambda: cmd_calib(),
     'art19': lambda: cmd_art19(),
     'grad': lambda: cmd_grad(int(a[1]), a[2] if len(a) > 2 else None),
     'grad_final': lambda: cmd_grad_final(),
     'long': lambda: cmd_long(int(a[1]), int(a[2])),
     'long_final': lambda: cmd_long_final()}[a[0]]()
