"""Figuras de la ponencia (estilo ggplot2 · theme_bw) con plotnine. Datos: agregados y OOF anónimos."""
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from plotnine import *
from sklearn.metrics import precision_recall_curve, roc_curve, average_precision_score, roc_auc_score

D = '/tmp/claude-0/d3/data/'
O = '/tmp/claude-0/d3/fig/'
FONT = 'Carlito'
BASE = 17
ALG = ['Random Forest', 'SVM', 'XGBoost', 'Árbol de decisión', 'Regresión logística']
COL = {'Random Forest': '#2a78d6', 'SVM': '#eb6834', 'XGBoost': '#1baf7a', 'Árbol de decisión': '#eda100',
       'Regresión logística': '#e87ba4'}
MAP = {'Random Forest': 'Random Forest', 'SVM (RBF)': 'SVM', 'XGBoost': 'XGBoost', 'Árbol de Decisión': 'Árbol de decisión',
       'Regresión Logística (L2)': 'Regresión logística'}
coma = lambda v, d=2: f'{v:.{d}f}'.replace('.', ',')
lab_coma = lambda d=1: (lambda xs: [('%.2f' % x).rstrip('0').rstrip('.').replace('.', ',') if abs(x) > 1e-12 else '0' for x in xs])

TEMA = (theme_bw(base_size=BASE, base_family=FONT) +
        theme(panel_grid_minor=element_blank(), panel_border=element_rect(color='#7F7F7F'),
              axis_text=element_text(color='#333333'), strip_background=element_rect(fill='#E6E6E6', color='#7F7F7F'),
              strip_text=element_text(size=BASE, weight='bold'), legend_key=element_blank(),
              plot_background=element_rect(fill='white', color='white'), legend_title=element_blank()))


def guardar(p, nombre, w, h):
    p.save(O + nombre, width=w, height=h, dpi=220, verbose=False)
    print('ok', nombre)


# ── 1 · Duración de los no graduados ─────────────────────────────────────────
# Fase 2, §4.4 (59 desertores de las cohortes 2017-2 y 2018-1)
d = pd.DataFrame({'periodos': [0, 1, 2, 3, 4, 6, 8, 9], 'n': [5, 25, 8, 12, 5, 1, 2, 1]})
d['grupo'] = np.where(d.periodos <= 2, '≤ 2 semestres', '> 2 semestres')
tot = d.n.sum()
d['lab'] = d.n.astype(str)
p = (ggplot(d, aes('factor(periodos)', 'n', fill='grupo')) + geom_col(width=.72) +
     geom_text(aes(label='lab'), va='bottom', nudge_y=.3, size=BASE, family=FONT) +
     scale_fill_manual(values={'≤ 2 semestres': '#c0392b', '> 2 semestres': '#9db9e3'}) +
     labs(x='Semestres con actividad antes de abandonar (59 desertores)', y='Estudiantes') + TEMA + theme(legend_position=(.8, .8)))
guardar(p, 'f01_duracion.png', 7.2, 4.6)

# ── 2 · Embudo de poblaciones ────────────────────────────────────────────────
e = pd.DataFrame({'etapa': ['Admitidos (2017-2 y 2018-1)', 'Con actividad académica', 'Expuestos al art. 19', 'Casos art. 19'],
                  'n': [95, 90, 80, 19]})
e['etapa'] = pd.Categorical(e.etapa, categories=e.etapa[::-1])
p = (ggplot(e, aes('etapa', 'n')) + geom_col(fill='#2a78d6', width=.65) +
     geom_text(aes(label='n'), ha='left', nudge_y=1.5, size=BASE + 1, family=FONT, fontweight='bold') + coord_flip() +
     scale_y_continuous(limits=(0, 108), expand=(0, 0)) + labs(x='', y='Estudiantes de Ingeniería de Sistemas') + TEMA)
guardar(p, 'f02_embudo.png', 7.0, 3.6)

# ── 3 · Asignaturas críticas (plan 2011 vs equivalente 2018) ─────────────────
h = pd.read_csv(D + 'materias_criticas.csv').head(8)
c = pd.read_csv(D + 'materias_criticas_canonicas.csv').set_index('materia')['indice']
eq = {'MATEMATICAS II': ('Matemáticas II', 'CALCULO INTEGRAL', 'Cálculo integral'), 'FISICA I': ('Física I', 'FISICA MECANICA', 'Física mecánica'),
      'ALGEBRA LINEAL': ('Álgebra Lineal', 'ALGEBRA LINEAL', 'Álgebra lineal'), 'MATEMATICAS I': ('Matemáticas I', 'CALCULO DIFERENCIAL', 'Cálculo diferencial'),
      'FUNDAMENTOS DE PROGRAMACION': ('Fund. de Programación', 'ALGORITMIA Y PROGRAMACION', 'Algoritmia y programación'),
      'FISICA II': ('Física II', 'ELECTRICIDAD Y MAGNETISMO', 'Electricidad y magnetismo'),
      'PENSAMIENTO LOGICO MATEMATICO': ('Pensamiento lógico', 'DESARROLLO DEL PENSAMIENTO LOGICO MATEMATICO', 'Desarrollo del pensamiento lógico'),
      'MATEMATICAS ESPECIALES': ('Matemáticas Especiales', 'MATEMATICAS ESPECIALES', 'Matemáticas especiales')}
filas = []
for _, r in h.iterrows():
    a, kc, b = eq[r.materia]
    lab = f'{a}  ≡  {b}' if a.lower() != b.lower() else a
    filas += [{'curso': lab, 'plan': 'Plan 2011', 'indice': r.indice}, {'curso': lab, 'plan': 'Equivalente plan 2018', 'indice': c.get(kc, np.nan)}]
m = pd.DataFrame(filas)
orden = list(dict.fromkeys(m.curso))[::-1]
m['curso'] = pd.Categorical(m.curso, categories=orden)
m['plan'] = pd.Categorical(m.plan, categories=['Plan 2011', 'Equivalente plan 2018'])
p = (ggplot(m, aes('indice', 'curso', color='plan')) + geom_line(aes(group='curso'), color='#BBBBBB', size=1.4) +
     geom_point(size=5.5) + scale_color_manual(values={'Plan 2011': '#c0392b', 'Equivalente plan 2018': '#2a78d6'}) +
     scale_x_continuous(limits=(0, 1.02), breaks=[0, .25, .5, .75, 1], labels=lab_coma(2)) +
     labs(x='Índice de criticidad (0,70 × reprobación + 0,30 × repitencia)', y='') + TEMA +
     theme(legend_position='top', legend_text=element_text(size=BASE), axis_text_y=element_text(size=BASE - 1)))
guardar(p, 'f03_criticas.png', 11.4, 4.75)

# ── 4 · Factores sin asociación ──────────────────────────────────────────────
f = pd.read_csv(D + 'factores.csv').dropna(subset=['PROMEDIO_CARRERA'])
f['Género'] = np.where(f.sexo == 1, 'Hombres', 'Mujeres')
p = (ggplot(f, aes('Género', 'PROMEDIO_CARRERA')) + geom_boxplot(width=.5, outlier_shape='', fill='#dbe6f5') +
     geom_jitter(width=.12, height=0, alpha=.55, size=2.2, color='#2a78d6') +
     labs(x='', y='Promedio de carrera', title='Género · Mann-Whitney p = 0,246') + TEMA + theme(plot_title=element_text(size=BASE)))
guardar(p, 'f04a_genero.png', 3.7, 3.9)
bins = pd.cut(f.nivel_edu_max_padres, [-1, 4, 8, 12], labels=['Hasta\nbachillerato', 'Técnico o\ntecnólogo', 'Universitario\no más'])
f['Educación'] = bins
p = (ggplot(f, aes('Educación', 'PROMEDIO_CARRERA')) + geom_boxplot(width=.5, outlier_shape='', fill='#dbe6f5') +
     geom_jitter(width=.12, height=0, alpha=.55, size=2.2, color='#2a78d6') +
     labs(x='', y='', title='Educación de los padres · Spearman p > 0,6') + TEMA + theme(plot_title=element_text(size=BASE)))
guardar(p, 'f04b_padres.png', 4.7, 3.9)
r = f.groupby('repitio_escolar').rendimiento_bajo.agg(['mean', 'size']).reset_index()
r['Repitió'] = np.where(r.repitio_escolar == 1, 'Sí repitió', 'No repitió')
r['lab'] = [f'{coma(100*a,0)} %\n(n = {b})' for a, b in zip(r['mean'], r['size'])]
p = (ggplot(r, aes('Repitió', 'mean')) + geom_col(width=.5, fill='#9db9e3') + geom_text(aes(label='lab'), va='bottom', nudge_y=.02, size=BASE - 2, family=FONT) +
     scale_y_continuous(limits=(0, .75), labels=lambda xs: [f'{int(x*100)} %' for x in xs]) +
     labs(x='', y='Con promedio < 3,0', title='Repitencia escolar · χ² p = 0,215') + TEMA + theme(plot_title=element_text(size=BASE)))
guardar(p, 'f04c_repitencia.png', 3.7, 3.9)

# ── 5 · Magnitud de los sesgos medidos ───────────────────────────────────────
s = pd.DataFrame({'fuente': ['Selección de variables fuera del pliegue', 'Hiperparámetros fuera del pliegue · XGBoost',
                             'Hiperparámetros fuera del pliegue · Árbol', 'Hiperparámetros fuera del pliegue · Random Forest'],
                  'sesgo': [0.150, 0.046, 0.011, 0.008]})
s['fuente'] = pd.Categorical(s.fuente, categories=s.fuente[::-1])
s['lab'] = ['+' + coma(v, 3) for v in s.sesgo]
p = (ggplot(s, aes('fuente', 'sesgo')) + geom_col(fill='#c0392b', width=.6) +
     geom_hline(yintercept=.03, linetype='dashed', color='#333333', size=.9) +
     annotate('text', x=4.42, y=.033, label='umbral de relevancia 0,03', ha='left', size=BASE - 2, family=FONT) +
     geom_text(aes(label='lab'), ha='left', nudge_y=.003, size=BASE, family=FONT, fontweight='bold') + coord_flip() +
     scale_y_continuous(limits=(0, .18), labels=lab_coma(2)) + labs(x='', y='AUC-PR inflado respecto a la medición honesta') + TEMA)
guardar(p, 'f05_sesgos.png', 11.0, 3.6)

# ── 6 · Selección de variables (ablación) ────────────────────────────────────
a = pd.read_csv(D + 'ablation_subconjuntos.csv')
nombres = {'S7': 'Solo promedio 1.er semestre (1)', 'S3': 'S3 · académicas (6)', 'S2': 'Todas las candidatas (19)',
           'S5': 'Sin redundancias (17)', 'S1': 'Solo ingreso: socioeconómicas + Saber 11 (17)', 'S4': 'Solo socioeconómicas (11)'}
a['k'] = a.subconjunto.str[:2]
a = a[a.k.isin(nombres)].copy()
a['nombre'] = a.k.map(nombres)
a['nombre'] = pd.Categorical(a.nombre, categories=a.sort_values('RF_AUC_PR').nombre)
a['destacado'] = np.where(a.k == 'S3', 'S3', 'otro')
a['lab'] = [coma(v, 3) for v in a.RF_AUC_PR]
p = (ggplot(a, aes('nombre', 'RF_AUC_PR', color='destacado')) +
     geom_hline(yintercept=.2375, linetype='dashed', color='#c0392b') +
     geom_pointrange(aes(ymin='RF_AUC_PR - RF_sd', ymax='RF_AUC_PR + RF_sd'), size=1.1) +
     annotate('text', x=0.6, y=.245, label='azar 0,24', ha='left', size=BASE - 2, color='#c0392b', family=FONT) +
     geom_text(aes(label='lab'), nudge_x=.33, size=BASE - 2, color='#333333', family=FONT) +
     scale_color_manual(values={'S3': '#2a78d6', 'otro': '#7F7F7F'}, guide=None) + coord_flip() +
     scale_y_continuous(limits=(0.2, 0.85), labels=lab_coma(1)) + labs(x='', y='AUC-PR (Random Forest)') + TEMA)
guardar(p, 'f06_ablacion.png', 7.4, 4.5)

# ── 7 · Importancia por permutación ──────────────────────────────────────────
pi = pd.read_csv(D + 'permutacion_importancia.csv').rename(columns={'Unnamed: 0': 'var'}).head(8)
nv = {'prom_sem1': 'Promedio 1.er semestre', 'icfes_total': 'Saber 11 · total', 'icfes_mat': 'Saber 11 · matemáticas',
      'sisben_nivel': 'Nivel SISBÉN', 'cohorte_encoded': 'Cohorte', 'estrato': 'Estrato', 'repitio_escolar': 'Repitencia escolar',
      'nivel_edu_max_padres': 'Educación de los padres'}
pi['nombre'] = pi['var'].map(nv)
pi['lab'] = [coma(v, 3) for v in pi.caida_AUC_PR_media]
pi['nombre'] = pd.Categorical(pi.nombre, categories=pi.nombre[::-1])
p = (ggplot(pi, aes('nombre', 'caida_AUC_PR_media')) + geom_col(fill='#2a78d6', width=.65) +
     geom_text(aes(label='lab'), ha='left', nudge_y=.005, size=BASE - 2, family=FONT) +
     coord_flip() + scale_y_continuous(limits=(0, .36), labels=lab_coma(2)) +
     labs(x='', y='Caída del AUC-PR al permutar la variable') + TEMA)
guardar(p, 'f07_permutacion.png', 6.0, 4.5)

# ── 8 · Hiperparámetros elegidos en los 50 pliegues (RF) ─────────────────────
hp = pd.read_csv(D + 'art19_hiperparametros_por_pliegue.csv')
import json
rf = pd.DataFrame(hp[hp.modelo == 'Random Forest'].params.apply(json.loads).tolist())
rows = []
for k, nom in [('max_depth', 'max_depth (profundidad)'), ('min_samples_leaf', 'min_samples_leaf (hoja mínima)'),
               ('max_features', 'max_features (variables por corte)')]:
    v = rf[k].apply(lambda z: ('sin límite' if k == 'max_depth' else 'todas') if (z is None or (isinstance(z, float) and np.isnan(z))) else str(int(z)) if isinstance(z, (int, float)) else str(z))
    for val, n in v.value_counts().items():
        rows.append({'param': nom, 'valor': val, 'n': n})
h2 = pd.DataFrame(rows)
p = (ggplot(h2, aes('valor', 'n')) + geom_col(fill='#2a78d6', width=.6) + geom_text(aes(label='n'), va='bottom', nudge_y=.6, size=BASE - 2, family=FONT) +
     facet_wrap('~param', scales='free_x') + labs(x='', y='Pliegues (de 50)') + TEMA)
guardar(p, 'f08_hiperparametros.png', 11.4, 3.9)

# ── 9 · AUC-PR por repetición (art. 19) ──────────────────────────────────────
mr = pd.read_csv(D + 'art19_metricas_por_repeticion.csv')
mr['alg'] = pd.Categorical(mr.modelo.map(MAP), categories=ALG[::-1])
mean = mr.groupby('alg', observed=True).AUC_PR.mean().reset_index()
mean['lab'] = [coma(v, 3) for v in mean.AUC_PR]
p = (ggplot(mr, aes('alg', 'AUC_PR', color='alg')) + geom_hline(yintercept=.2375, linetype='dashed', color='#c0392b') +
     geom_boxplot(width=.45, outlier_shape='', color='#555555', fill='white') + geom_jitter(width=.12, height=0, size=3, alpha=.85) +
     annotate('text', x=0.55, y=.25, label='azar = 0,24 (proporción de casos)', ha='left', size=BASE - 2, color='#c0392b', family=FONT) +
     geom_point(mean, aes('alg', 'AUC_PR'), shape='D', size=5, color='black') +
     geom_text(mean, aes('alg', 'AUC_PR', label='lab'), nudge_x=.38, size=BASE, color='black', family=FONT, fontweight='bold') +
     scale_color_manual(values=COL, guide=None) + coord_flip() + scale_y_continuous(limits=(0.2, 0.9), labels=lab_coma(1)) +
     labs(x='', y='AUC-PR en cada una de las 10 repeticiones (rombo negro = media)') + TEMA)
guardar(p, 'f09_aucpr_repeticiones.png', 11.4, 4.7)

# ── 10 · Comparaciones pareadas (Nadeau-Bengio) ──────────────────────────────
cp = pd.read_csv(D + 'i3bis_comparaciones_art19.csv')
cp['a'] = cp.modelo_a.map(MAP); cp['b'] = cp.modelo_b.map(MAP)
M = []
for _, r in cp.iterrows():
    M.append({'fila': r.a, 'col': r.b, 'delta': r.diferencia, 'p': r.p_valor})
    M.append({'fila': r.b, 'col': r.a, 'delta': -r.diferencia, 'p': r.p_valor})
M = pd.DataFrame(M)
M['lab'] = [f"{'+' if d > 0 else ''}{coma(d, 3)}\np = {coma(pv, 3)}" for d, pv in zip(M.delta, M.p)]
M['sig'] = np.where((M.p < .05) & (M.delta.abs() >= .03), 'sí', 'no')
M['fila'] = pd.Categorical(M.fila, categories=ALG[::-1]); M['col'] = pd.Categorical(M.col, categories=ALG)
p = (ggplot(M, aes('col', 'fila', fill='delta')) + geom_tile(color='white', size=1.5) +
     geom_text(M[M.sig == 'sí'], aes(label='lab'), size=BASE - 3, family=FONT, fontweight='bold') +
     geom_text(M[M.sig == 'no'], aes(label='lab'), size=BASE - 3, family=FONT, color='#555555') +
     scale_fill_gradient2(low='#c0392b', mid='#f7f7f7', high='#2a78d6', midpoint=0, limits=(-.2, .2), name='Δ AUC-PR\n(fila − columna)') +
     labs(x='', y='') + TEMA + theme(axis_text_x=element_text(rotation=12), legend_title=element_text(size=BASE - 3)))
guardar(p, 'f10_pareadas.png', 11.0, 4.7)

# ── 11 · Curvas PR y ROC (OOF promedio) ──────────────────────────────────────
o = pd.read_csv(D + 'oof_art19_algoritmos.csv')
cur = []
for alg in ALG:
    pp, rr, _ = precision_recall_curve(o.y, o[alg])
    cur.append(pd.DataFrame({'x': rr, 'y': pp, 'alg': alg, 'panel': 'Precisión frente a exhaustividad'}))
    fp, tp, _ = roc_curve(o.y, o[alg])
    cur.append(pd.DataFrame({'x': fp, 'y': tp, 'alg': alg, 'panel': 'Curva ROC'}))
CU = pd.concat(cur); CU['alg'] = pd.Categorical(CU.alg, categories=ALG)
CU['panel'] = pd.Categorical(CU.panel, categories=['Precisión frente a exhaustividad', 'Curva ROC'])
ref = pd.DataFrame({'panel': pd.Categorical(['Precisión frente a exhaustividad'], categories=CU.panel.cat.categories), 'y': [.2375]})
diag = pd.DataFrame({'panel': pd.Categorical(['Curva ROC'] * 2, categories=CU.panel.cat.categories), 'x': [0, 1], 'y': [0, 1]})
p = (ggplot(CU, aes('x', 'y', color='alg')) + geom_path(size=1.2) +
     geom_hline(ref, aes(yintercept='y'), linetype='dashed', color='#c0392b') +
     geom_line(diag, aes('x', 'y'), linetype='dashed', color='#999999', inherit_aes=False) +
     facet_wrap('~panel') + scale_color_manual(values=COL) +
     scale_x_continuous(breaks=[0, .25, .5, .75, 1], labels=lab_coma()) + scale_y_continuous(breaks=[0, .25, .5, .75, 1], labels=lab_coma()) +
     labs(x='Exhaustividad (izq.) · Tasa de falsos positivos (der.)', y='Precisión (izq.) · Tasa de verdaderos positivos (der.)') +
     TEMA + theme(legend_position='right', aspect_ratio=1, axis_title=element_text(size=BASE - 2)))
guardar(p, 'f11_curvas.png', 11.4, 4.9)

# ── 12 · Matrices de confusión (modelo desplegado, niveles) ──────────────────
k = pd.read_csv(D + 'oof_art19_calibracion.csv')
y, pr0 = k.y.values, k['sin calibrar'].values
cm = []
for nivel, u in [('Confirmado · umbral 0,63', .63), ('Seguimiento · umbral 0,13', .13)]:
    yp = (pr0 >= u).astype(int)
    for real in (1, 0):
        for pred in (1, 0):
            n = int(((y == real) & (yp == pred)).sum())
            cm.append({'nivel': nivel, 'Real': 'Con bajo rendimiento' if real else 'Sin bajo rendimiento',
                       'Predicho': 'Alerta' if pred else 'Sin alerta', 'n': n, 'ok': 'acierto' if real == pred else 'error'})
cm = pd.DataFrame(cm)
cm['Real'] = pd.Categorical(cm.Real, categories=['Sin bajo rendimiento', 'Con bajo rendimiento'])
cm['Predicho'] = pd.Categorical(cm.Predicho, categories=['Alerta', 'Sin alerta'])
cm['lab'] = cm.n.astype(str)
p = (ggplot(cm, aes('Predicho', 'Real', fill='ok')) + geom_tile(color='white', size=2) +
     geom_text(aes(label='lab'), size=BASE + 12, family=FONT, fontweight='bold', color='#222222') +
     scale_fill_manual(values={'acierto': '#cfe0f5', 'error': '#f6d3cf'}, guide=None) + facet_wrap('~nivel') +
     labs(x='Predicción del modelo', y='Realidad') + TEMA + theme(panel_grid=element_blank()))
guardar(p, 'f12_confusion.png', 11.0, 4.5)

# ── 13 · Curva de umbral ─────────────────────────────────────────────────────
cu = pd.read_csv(D + 'mvp_curva_umbral_art19.csv')
cl = cu.melt(id_vars='umbral', value_vars=['recall', 'precision', 'pct_cohorte'], var_name='m', value_name='v')
cl['m'] = cl.m.map({'recall': 'Casos detectados (recall)', 'precision': 'Alertas acertadas (precisión)', 'pct_cohorte': '% de la cohorte alertada'})
cl['m'] = pd.Categorical(cl.m, categories=['Casos detectados (recall)', 'Alertas acertadas (precisión)', '% de la cohorte alertada'])
p = (ggplot(cl, aes('umbral', 'v', color='m', linetype='m')) + geom_step(size=1.3) +
     geom_vline(xintercept=[.13, .63], color='#333333', linetype='dotted', size=.9) +
     annotate('text', x=.14, y=1.04, label='Seguimiento', ha='left', size=BASE - 2, family=FONT) +
     annotate('text', x=.64, y=1.04, label='Confirmado', ha='left', size=BASE - 2, family=FONT) +
     scale_color_manual(values=['#2a78d6', '#eb6834', '#7F7F7F']) + scale_linetype_manual(values=['solid', 'solid', 'dashed']) +
     scale_y_continuous(labels=lambda xs: [f'{int(round(x*100))} %' for x in xs], limits=(0, 1.07), breaks=[0, .25, .5, .75, 1]) + scale_x_continuous(breaks=[0, .1, .2, .3, .4, .5, .6, .7, .8, .9], labels=lab_coma()) +
     labs(x='Umbral del puntaje de riesgo', y='') + TEMA + theme(legend_position='top'))
guardar(p, 'f13_umbral.png', 11.0, 4.6)

# ── 14 · Graduación ──────────────────────────────────────────────────────────
g = pd.read_csv(D + 'grad_metricas_por_repeticion.csv')
g['alg'] = pd.Categorical(g.modelo.map(MAP), categories=ALG[::-1])
gm = g.groupby('alg', observed=True).AUC_PR.mean().reset_index()
gm['lab'] = [coma(v, 3) for v in gm.AUC_PR]
p = (ggplot(g, aes('alg', 'AUC_PR', color='alg')) + geom_hline(yintercept=35 / 90, linetype='dashed', color='#c0392b') +
     geom_boxplot(width=.45, outlier_shape='', color='#555555', fill='white') + geom_jitter(width=.12, height=0, size=3, alpha=.85) +
     annotate('text', x=0.55, y=.40, label='azar = 0,39', ha='left', size=BASE - 2, color='#c0392b', family=FONT) +
     geom_point(gm, aes('alg', 'AUC_PR'), shape='D', size=5, color='black') +
     geom_text(gm, aes('alg', 'AUC_PR', label='lab'), nudge_x=.38, size=BASE, color='black', family=FONT, fontweight='bold') +
     scale_color_manual(values=COL, guide=None) + coord_flip() + scale_y_continuous(limits=(0.35, 0.85), labels=lab_coma(1)) +
     labs(x='', y='AUC-PR de graduación en cada repetición (rombo negro = media)') + TEMA)
guardar(p, 'f14_graduacion.png', 11.4, 4.6)

# ── 15 · Simultaneidad: todos vs solo predictivos ────────────────────────────
sm = pd.DataFrame({'esc': ['Todos los casos (n = 80)', 'Solo casos futuros (n = 72)'] * 2,
                   'tipo': ['Modelo', 'Modelo', 'Azar', 'Azar'], 'v': [.750, .473, .2375, .1528]})
sm['esc'] = pd.Categorical(sm.esc, categories=['Todos los casos (n = 80)', 'Solo casos futuros (n = 72)'])
sm['tipo'] = pd.Categorical(sm.tipo, categories=['Modelo', 'Azar'])
sm['lab'] = [coma(v, 3) for v in sm.v]
p = (ggplot(sm, aes('esc', 'v', fill='tipo')) + geom_col(position=position_dodge(.75), width=.7) +
     geom_text(aes(label='lab'), position=position_dodge(.75), va='bottom', size=BASE, family=FONT) +
     annotate('text', x=1, y=.86, label='3,16 × el azar', size=BASE, family=FONT, fontweight='bold') +
     annotate('text', x=2, y=.59, label='3,10 × el azar', size=BASE, family=FONT, fontweight='bold') +
     scale_fill_manual(values={'Modelo': '#2a78d6', 'Azar': '#BBBBBB'}) + scale_y_continuous(limits=(0, .95), labels=lab_coma(1)) +
     labs(x='', y='AUC-PR') + TEMA + theme(legend_position='top'))
guardar(p, 'f15_simultaneidad.png', 6.2, 4.6)

# ── 16 · Diagrama de calibración ─────────────────────────────────────────────
rows = []
for col, nom in [('sin calibrar', 'Sin calibrar'), ('isotónica', 'Isotónica'), ('Platt (sigmoide)', 'Platt')]:
    q = pd.qcut(k[col].rank(method='first'), 5, labels=False)
    t = k.assign(q=q).groupby('q').agg(pred=(col, 'mean'), obs=('y', 'mean')).reset_index(); t['m'] = nom
    rows.append(t)
cal = pd.concat(rows); cal['m'] = pd.Categorical(cal.m, categories=['Sin calibrar', 'Isotónica', 'Platt'])
p = (ggplot(cal, aes('pred', 'obs', color='m')) + geom_abline(slope=1, intercept=0, linetype='dashed', color='#999999') +
     geom_line(size=1.2) + geom_point(size=3.5) + scale_color_manual(values=['#2a78d6', '#1baf7a', '#eb6834']) +
     coord_equal(xlim=(0, 1), ylim=(0, 1)) + scale_x_continuous(labels=lab_coma(1)) + scale_y_continuous(labels=lab_coma(1)) +
     labs(x='Probabilidad media predicha (quintiles)', y='Proporción observada') + TEMA + theme(legend_position=(.25, .8)))
guardar(p, 'f16_calibracion.png', 5.4, 5.0)

# ── 17 · Semestre a semestre: lift ───────────────────────────────────────────
t = pd.read_csv(D + 'mvp_trayectoria_art20.csv')
t['lab'] = [coma(v, 2) for v in t.lift]; t['alg'] = t.modelo.map(MAP); t['Corte'] = 'Corte ' + t.corte.astype(str)
p = (ggplot(t, aes('Corte', 'lift', fill='alg')) + geom_col(position=position_dodge(.75), width=.7) +
     geom_hline(yintercept=1, linetype='dashed', color='#c0392b') +
     geom_text(aes(label='lab'), position=position_dodge(.75), va='bottom', size=BASE - 2, family=FONT) +
     scale_fill_manual(values={'Random Forest': '#2a78d6', 'Regresión logística': '#e87ba4'}) +
     scale_y_continuous(limits=(0, 3.3), labels=lab_coma(1)) + annotate('text', x=0.6, y=3.15, label='Alerta art. 19 al cierre del 1.er semestre: 3,1', ha='left', size=BASE - 1, family=FONT, color='#2a78d6') +
     geom_hline(yintercept=3.14, color='#2a78d6', linetype='dotted') +
     annotate('text', x=3.45, y=1.08, label='azar', size=BASE - 2, color='#c0392b', family=FONT) +
     labs(x='', y='Lift sobre el azar (AUC-PR / proporción)') + TEMA + theme(legend_position='top'))
guardar(p, 'f17_semestral.png', 6.6, 4.6)

# ── 18 · Sensibilidad al plan de estudios ────────────────────────────────────
sp = pd.read_csv(D + 'cambio_plan_sensibilidad.csv')
sp['esc'] = ['Referencia', 'Sin ingreso por\nhomologación', 'Plan 2018\nsin reentrenar', 'Plan 2018\nreentrenado']
sp['esc'] = pd.Categorical(sp.esc, categories=sp.esc)
sp['lab'] = [coma(v, 3) for v in sp.AUC_PR]
p = (ggplot(sp, aes('esc', 'AUC_PR')) + geom_hline(yintercept=.2375, linetype='dashed', color='#c0392b') +
     geom_pointrange(aes(ymin='AUC_PR - sd', ymax='AUC_PR + sd'), color='#2a78d6', size=1.1) +
     geom_text(aes(label='lab'), nudge_x=.28, size=BASE - 1, family=FONT) +
     scale_y_continuous(limits=(0.2, 0.85), labels=lab_coma(1)) + labs(x='', y='AUC-PR') + TEMA)
guardar(p, 'f18_plan.png', 6.4, 4.4)

# ── 19 · Curva de aprendizaje ────────────────────────────────────────────────
ca = pd.read_csv(D + 'curva_aprendizaje.csv')
p = (ggplot(ca, aes('n_entrenamiento', 'AUC_PR_validacion')) +
     geom_ribbon(aes(ymin='AUC_PR_validacion - sd_validacion/2', ymax='AUC_PR_validacion + sd_validacion/2'), fill='#2a78d6', alpha=.15) +
     geom_line(color='#2a78d6', size=1.3) + geom_point(color='#2a78d6', size=3.5) +
     geom_hline(yintercept=.838, linetype='dashed', color='#555555') +
     annotate('text', x=26, y=.86, label='techo estimado ≈ 0,84', ha='left', size=BASE - 2, family=FONT) +
     scale_y_continuous(limits=(0.3, 0.95), labels=lab_coma(1)) + labs(x='Estudiantes en entrenamiento', y='AUC-PR de validación') + TEMA)
guardar(p, 'f19_aprendizaje.png', 5.6, 4.4)
