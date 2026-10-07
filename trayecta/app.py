"""
TRAYECTA · Sistema de alerta y seguimiento de trayectoria académica — Ing. de Sistemas
Universidad de los Llanos · Facultad de Ciencias Básicas e Ingeniería

Producto mínimo viable del proyecto «Modelo predictivo de trayectoria académica FCBI»
(DGI/Unillanos C07-02-2026-027). Referencia de producto: SPADIES (MEN, Colombia).
Visualizaciones en D3 (trayecta/componentes/viz), sin dependencias de internet.

Ejecutar desde la raíz del repositorio:
    streamlit run trayecta/app.py
"""
import os

import numpy as np
import pandas as pd
import streamlit as st

import motor
from componentes import viz

AQUI = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(AQUI, 'datos_demo')
LOCALES = os.path.join(AQUI, 'datos_locales')      # generado por preparar_datos_reales.py; fuera de git
SRC = motor.SRC
PAGINAS = ['Panorama', 'Ficha del estudiante', 'Asignaturas críticas', 'Cargar cohorte', 'Simulador']
ICONOS = {'Panorama': '◉', 'Ficha del estudiante': '◍', 'Asignaturas críticas': '▤',
          'Cargar cohorte': '⇪', 'Simulador': '◎'}
SIT_INFO = motor.SITUACIONES
FUENTE_LEGIBLE = {'propio': 'Curso del plan 2018', 'Art. 2': 'Equivalencia oficial 2011 → 2018',
                  'Art. 1': 'Equivalencia oficial 2011 → 2018', 'institucional': 'Curso institucional',
                  'sin_equivalente': 'Curso 2011 sin equivalente', 'sin_catalogo': 'Código no reconocido'}

st.set_page_config(page_title='TRAYECTA · Ing. de Sistemas', page_icon='◉', layout='wide',
                   initial_sidebar_state='expanded')

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stMarkdown, button, input, textarea { font-family: Inter, "Segoe UI", system-ui, sans-serif !important; }
.stApp { background: #F5F7FB; }
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1400px; }
h1, h2, h3 { color: #14213D; letter-spacing: -.3px; }
h3 { font-size: 1.05rem !important; font-weight: 700 !important; }
/* barra lateral */
[data-testid="stSidebar"] { background: linear-gradient(185deg, #0F172A 0%, #1E1B4B 60%, #0B3B4E 100%); }
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] div { background-color: transparent !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div { background-color: rgba(255,255,255,.08) !important; border-radius: 10px; border: 1px solid rgba(255,255,255,.18) !important; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child { display: none !important; }
[data-testid="stSidebar"] [role="radiogroup"] label { padding: 7px 10px; border-radius: 10px; margin-bottom: 2px; transition: background .15s; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,.07); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background: rgba(99,102,241,.35); }
.marca { font-weight: 800; font-size: 26px; letter-spacing: 1.5px; background: linear-gradient(90deg,#A5B4FC,#67E8F9);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.pill { display:inline-block; font-size:11px; font-weight:700; letter-spacing:.6px; padding:3px 9px; border-radius:999px; }
.pill.real { background: rgba(52,211,153,.16); color:#6EE7B7 !important; border:1px solid rgba(52,211,153,.4); }
.pill.demo { background: rgba(251,191,36,.18); color:#FCD34D !important; border:1px solid rgba(251,191,36,.4); }
/* banda de título de página */
.banda { display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin: 2px 0 10px; }
.banda h1 { font-size: 30px; font-weight: 800; margin: 0; padding: 0; }
.banda .ctx { color:#64748B; font-size: 14px; }
/* tira de hechos (sin tarjetas) */
.tira { display:flex; flex-wrap:wrap; gap: 0; margin: 4px 0 14px; background: #fff; border-radius: 16px;
        box-shadow: 0 1px 2px rgba(20,33,61,.06), 0 8px 24px rgba(20,33,61,.06); overflow:hidden; }
.tira > div { padding: 14px 22px; border-right: 1px solid #EEF2F7; }
.tira > div:last-child { border-right: none; }
.tira .v { font-size: 26px; font-weight: 800; color:#14213D; line-height:1.1; }
.tira .l { font-size: 12px; color:#64748B; margin-top: 2px; }
.nivel { display:inline-flex; align-items:center; gap:7px; font-weight:800; }
.nivel i { width: 12px; height: 12px; border-radius: 50%; display:inline-block; }
.panel { background:#fff; border-radius:18px; padding: 16px 18px 8px; box-shadow: 0 1px 2px rgba(20,33,61,.06), 0 8px 24px rgba(20,33,61,.06); }
[data-testid="stPopover"] button { border-radius: 999px; padding: 0 .55rem; min-height: 1.8rem; }
/* botón flotante «Acerca de» (esquina inferior derecha) */
.st-key-acerca { position: fixed; right: 26px; bottom: 22px; z-index: 999990; width: auto !important; }
.st-key-acerca button { width: 46px; height: 46px; min-height: 46px; padding: 0; border-radius: 50%; border: none;
  background: linear-gradient(135deg,#4F46E5,#0891B2); color: #fff; font-size: 20px; font-weight: 700;
  box-shadow: 0 6px 18px rgba(30,27,75,.35); opacity: .8; transition: opacity .15s, transform .15s; }
.st-key-acerca button:hover { opacity: 1; transform: translateY(-2px); color: #fff; border: none; }
.st-key-acerca button p { font-size: 20px; }
.sit { border-left: 4px solid var(--c); background:#fff; border-radius: 12px; padding: 12px 16px; margin-top: 6px;
       box-shadow: 0 1px 2px rgba(20,33,61,.06); }
.sit b { color:#14213D; } .sit .f { color:#64748B; font-size: 12px; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

COLOR_NIVEL = {'Confirmado': '#D93F3F', 'Seguimiento': '#E8A317', 'Sin alerta': '#1F9D6B'}


def nivel_html(n):
    return f'<span class="nivel"><i style="background:{COLOR_NIVEL.get(n, "#94A3B8")}"></i>{n}</span>'


def banda(titulo, contexto=''):
    st.markdown(f'<div class="banda"><h1>{titulo}</h1><span class="ctx">{contexto}</span></div>',
                unsafe_allow_html=True)


def tira(items):
    st.markdown('<div class="tira">' + ''.join(f'<div><div class="v">{v}</div><div class="l">{l}</div></div>'
                                              for v, l in items) + '</div>', unsafe_allow_html=True)


@st.cache_data
def _catalogo_nombres():
    from equivalencias import cargar_catalogo, _norm
    c = cargar_catalogo().sort_values('plan', ascending=False)        # prioriza el nombre del plan 2018
    return {_norm(n): n for n in c['nombre']}


def nombre_oficial(txt):
    from equivalencias import _norm
    n = _catalogo_nombres().get(_norm(txt), str(txt).title())
    return n if len(n) <= 36 else n[:34] + '…'


def coma(v, d=2):
    return f'{v:.{d}f}'.replace('.', ',')


def ayuda(texto):
    with st.popover('?'):
        st.markdown(texto)


@st.cache_resource
def modelos():
    return motor.cargar_modelos()


@st.cache_data
def cohorte_demo(cual):
    mats = [pd.read_csv(os.path.join(DEMO, f'{c}_materias.csv')) for c in cual]
    ings = [pd.read_csv(os.path.join(DEMO, f'{c}_ingreso.csv')) for c in cual]
    return pd.concat(mats, ignore_index=True), pd.concat(ings, ignore_index=True)


@st.cache_data
def cohorte_local():
    return (motor.leer_csv(os.path.join(LOCALES, 'materias.csv')),
            motor.leer_csv(os.path.join(LOCALES, 'ingreso.csv')))


@st.cache_data(show_spinner='Procesando cohorte…')
def procesar(mat, ing):
    return motor.procesar_cohorte(mat, ing, modelos())


M = modelos()
U = M['art19']['umbrales']
T19 = M['tarjetas'].get('alerta_art19', {})
TGR = M['tarjetas'].get('graduacion', {})
if st.session_state.get('pagina') not in PAGINAS:
    st.session_state['pagina'] = PAGINAS[0]
if '_ir_a' in st.session_state:                      # navegación programática (clic en el enjambre)
    st.session_state['pagina'] = st.session_state.pop('_ir_a')

# ── Barra lateral ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="marca">TRAYECTA</div><div style="font-size:12.5px;opacity:.8;margin-top:-4px">'
                'Alerta y trayectoria académica<br>Ingeniería de Sistemas · Unillanos</div>', unsafe_allow_html=True)
    st.write('')
    st.radio('Navegación', PAGINAS, key='pagina', label_visibility='collapsed',
             format_func=lambda p: f'{ICONOS[p]}   {p}')
    st.write('')
    fuentes = {'Cohorte A · 2018-2 · plan 2011': ['A'], 'Cohorte B · 2025-1 · plan 2018': ['B'],
               'Ambas cohortes': ['A', 'B']}
    if os.path.exists(os.path.join(LOCALES, 'materias.csv')):
        fuentes = {'Cohortes reales · 2017-2 y 2018-1': 'reales', **fuentes}
    if 'cargada' in st.session_state:
        fuentes = {'Cohorte cargada': None, **fuentes}
    fuente = st.selectbox('Cohorte', list(fuentes))
    if fuentes[fuente] == 'reales':
        st.markdown('<span class="pill real">DATOS INSTITUCIONALES</span>', unsafe_allow_html=True,
                    help='Datos reales de la Universidad, leídos solo en este equipo. No los comparta.')
    elif fuentes[fuente] is not None:
        st.markdown('<span class="pill demo">DATOS SINTÉTICOS</span>', unsafe_allow_html=True,
                    help='Cohortes de demostración: ningún estudiante es real. Sirven para conocer la herramienta '
                         'antes de cargar datos de la Universidad.')

if fuentes[fuente] is None:
    MAT, ING = st.session_state['cargada']
    sintetico = False
elif fuentes[fuente] == 'reales':
    MAT, ING = cohorte_local()
    sintetico = False
else:
    MAT, ING = cohorte_demo(tuple(fuentes[fuente]))
    sintetico = True
EST, PANEL = procesar(MAT, ING)
pagina = st.session_state['pagina']


def ir_a_ficha(evento):
    if evento and evento.get('accion') == 'ficha' and evento.get('t') != st.session_state.get('_ultimo_evento'):
        st.session_state['_ultimo_evento'] = evento.get('t')
        st.session_state['sel'] = evento['id']
        st.session_state['_ir_a'] = 'Ficha del estudiante'
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
if pagina == 'Panorama':
    n = len(EST)
    cnt = EST['nivel_alerta'].value_counts()
    planes = sorted(set('/'.join(EST['planes'].dropna()).split('/')))
    viz('hero', {
        'titulo': 'Panorama de la cohorte', 'subtitulo': fuente,
        'chips': [f'plan {p}' for p in planes] + (['datos sintéticos'] if sintetico else []),
        'n': n, 'confirmado': int(cnt.get('Confirmado', 0)), 'seguimiento': int(cnt.get('Seguimiento', 0)),
        'sin': int(cnt.get('Sin alerta', 0)), 'observados': int(EST['art19_observado'].sum()),
        'grad_media': float(EST['p_graduacion'].mean()),
        'ayuda': "La alerta estima el riesgo de <b>perder la calidad de estudiante por bajo rendimiento</b>, "
                 "con la información disponible al terminar el primer semestre.<br>"
                 f"<b>Confirmado</b>: riesgo alto. En los datos históricos, {U['confirmado']['precision']*100:.0f} % "
                 "de estas alertas correspondieron a estudiantes que sí perdieron la calidad.<br>"
                 f"<b>Seguimiento</b>: riesgo moderado. Con este nivel se identifica a "
                 f"{U['equilibrado']['recall']*100:.0f} % de quienes la perdieron, a cambio de más alertas.<br>"
                 "Cuántos estudiantes acompañar lo decide la Universidad según su capacidad de acompañamiento."}, key='hero')

    ev = viz('enjambre', {'umbrales': {'confirmado': U['confirmado']['umbral'], 'equilibrado': U['equilibrado']['umbral']},
                          'estudiantes': [{'id': r.CODIGO_INST, 'p': r.p_art19, 'g': r.p_graduacion, 'nivel': r.nivel_alerta,
                                           'sem': None if pd.isna(r.semestres_cursados) else int(r.semestres_cursados),
                                           'sit': r.situacion_actual, 'obs': int(r.art19_observado)}
                                          for r in EST.itertuples()], 'alto': 310},
             titulo='Cada punto es un estudiante',
             ayuda='Más a la derecha, mayor riesgo de perder la calidad de estudiante por bajo rendimiento. '
                   'Borde oscuro: el estudiante ya la perdió. Haga clic en un punto para abrir su ficha.', key='enjambre')
    ir_a_ficha(ev)

    izq, der = st.columns([1.05, 1])
    with izq:
        if not PANEL.empty:
            t = PANEL.groupby(['semestre', 'situacion']).size().reset_index(name='n')
            viz('situacion', {'filas': t.to_dict('records'), 'sit_info': SIT_INFO},
                titulo='Situación académica por semestre',
                ayuda='Qué condición del Reglamento Estudiantil tenía cada estudiante al cerrar cada semestre. '
                      'Se calcula con las notas: no es una predicción. Pase el cursor por un color para ver qué '
                      'significa. La columna se acorta a medida que los estudiantes se retiran o se gradúan.', key='sit')
    with der:
        c1, c2 = st.columns([1, .12])
        c1.subheader('Lista de priorización')
        with c2:
            ayuda('Estudiantes ordenados de mayor a menor riesgo. Descargue la lista para el programa de '
                  'acompañamiento académico.')
        tabla = EST[['CODIGO_INST', 'nivel_alerta', 'p_art19', 'p_graduacion', 'semestres_cursados', 'situacion_actual']] \
            .sort_values('p_art19', ascending=False)
        legible = motor.tabla_legible(EST)
        st.dataframe(tabla, hide_index=True, use_container_width=True, height=318, column_config={
            'CODIGO_INST': 'Código', 'nivel_alerta': 'Alerta',
            'p_art19': st.column_config.ProgressColumn('Riesgo', min_value=0, max_value=1, format='%.2f'),
            'p_graduacion': st.column_config.ProgressColumn('Graduación', min_value=0, max_value=1, format='%.2f'),
            'semestres_cursados': 'Sem.', 'situacion_actual': 'Situación'})
        st.download_button('Descargar lista', legible.to_csv(index=False).encode('utf-8-sig'),
                           'trayecta_priorizacion.csv', 'text/csv')

# ════════════════════════════════════════════════════════════════════════════
elif pagina == 'Ficha del estudiante':
    orden = EST.sort_values('p_art19', ascending=False)
    con_eventos = set(PANEL.loc[PANEL['situacion'] != motor.SIN_RESTRICCION, 'CODIGO_INST']) if not PANEL.empty else set()
    ilustr = orden[(orden['nivel_alerta'] != 'Sin alerta') & (orden['semestres_cursados'].fillna(0) >= 4)
                   & orden['CODIGO_INST'].isin(con_eventos)]
    ids = list(orden['CODIGO_INST'])
    sel = st.session_state.get('sel')
    i0 = ids.index(sel) if sel in ids else (ids.index(ilustr['CODIGO_INST'].iloc[0]) if len(ilustr) else 0)
    c1, c2 = st.columns([1, 2.2])
    cod = c1.selectbox('Estudiante', ids, index=i0,
                       format_func=lambda c: f"{c} · {orden.set_index('CODIGO_INST').at[c, 'nivel_alerta']}")
    st.session_state['sel'] = cod
    e = EST.set_index('CODIGO_INST').loc[cod]
    p = PANEL[PANEL['CODIGO_INST'] == cod].sort_values('semestre')
    avisos = []
    if e['art19_observado'] == 1:
        avisos.append(f"⚑ perdió la calidad de estudiante en {e['art19_primer_periodo']}")
    if isinstance(e.get('planes'), str) and '/' in e['planes']:
        avisos.append('🔁 cambió de plan 2011 → 2018')
    f2 = lambda v: '—' if pd.isna(v) else f'{v:.2f}'.replace('.', ',')
    viz('estudiante', {'id': cod, 'sub': f"cohorte {e['COHORTE']} · plan {e.get('planes', '')}", 'nivel': e['nivel_alerta'],
                       'p': float(e['p_art19']), 'g': float(e['p_graduacion']), 'avisos': avisos,
                       'zonas': [[0, U['equilibrado']['umbral'], '#1F9D6B'], [U['equilibrado']['umbral'], U['confirmado']['umbral'], '#E8A317'],
                                 [U['confirmado']['umbral'], 1, '#D93F3F']],
                       'hechos': [['semestres cursados', str(int(e.get('semestres_cursados', 0) or 0))],
                                  ['promedio 1.er semestre', f2(e['prom_sem1'])],
                                  ['promedio acumulado', f2(e.get('prom_acumulado'))],
                                  ['situación actual', str(e.get('situacion_actual', '—'))],
                                  ['semestres con inscripción limitada', str(int(e.get('veces_art20', 0) or 0))]]},
        key='hero_est')
    if e['art19_observado'] == 1:
        st.caption('Este estudiante ya perdió la calidad de estudiante: la alerta confirma lo ocurrido, no lo anticipa.')

    izq, der = st.columns([1.6, 1])
    with izq:
        if not p.empty:
            viz('trayectoria', {'semestres': [{
                'semestre': int(r.semestre), 'periodo': r.periodo, 'plan': r.plan,
                'prom_periodo': None if pd.isna(r.prom_periodo) else float(r.prom_periodo),
                'prom_acum': float(r.prom_acumulado), 'cred_aprob': int(r.creditos - r.cred_reprob),
                'cred_reprob': int(r.cred_reprob), 'situacion': r.situacion} for r in p.itertuples()], 'sit_info': SIT_INFO},
                titulo='Trayectoria semestre a semestre',
                ayuda='Arriba: promedios del semestre y acumulado (la zona tenue está por debajo de 3,0). '
                      'Centro: situación académica al cerrar cada semestre; los símbolos se explican en la leyenda '
                      'inferior. Abajo: créditos aprobados y reprobados. Pase el cursor por un semestre para ver '
                      'el detalle y qué implica su situación.', key='tray')
    with der:
        vars_ = [('prom_sem1', 'Promedio 1.er semestre', 2), ('icfes_mat', 'Saber 11 · matemáticas', 0),
                 ('icfes_lec', 'Saber 11 · lectura crítica', 0), ('icfes_nat', 'Saber 11 · c. naturales', 0),
                 ('icfes_total', 'Saber 11 · total', 0)]
        viz('perfil', {'vars': [{'nombre': n, 'valor': float(e[k]), 'dec': d, 'cohorte': EST[k].astype(float).tolist()}
                                for k, n, d in vars_]},
            titulo='Ingreso frente a la cohorte',
            ayuda='Puntos grises: compañeros de cohorte. Línea vertical: valor del estudiante típico. Punto grande: '
                  'este estudiante (rojo si está en el 25 % más bajo, ámbar si está por debajo de la mitad). '
                  'La etiqueta p indica qué porcentaje de la cohorte tiene un valor igual o menor. '
                  'El promedio del primer semestre es el dato que más influye en la alerta.', key='perfil')
        sit = e.get('situacion_actual')
        sit = sit if sit in SIT_INFO else motor.SIN_RESTRICCION
        info = SIT_INFO[sit]
        color = {motor.SIN_RESTRICCION: '#94A3B8', motor.PROMEDIO_BAJO: '#E58A3A', motor.LIMITE_CURSOS: '#D2602E',
                 motor.SOLO_REPROBADOS: '#B23B28', motor.PIERDE: '#7A1E22'}[sit]
        st.markdown(f'<div class="sit" style="--c:{color}"><div style="font-size:12px;color:#64748B;font-weight:700;'
                    f'letter-spacing:.5px">SITUACIÓN EN EL ÚLTIMO SEMESTRE</div><b style="font-size:16px">{sit}</b>'
                    f'<div style="margin-top:6px">{info["que_paso"]}</div><div style="margin-top:4px"><b>Qué implica:</b> '
                    f'{info["implica"]}</div>' + (f'<div class="f">Fundamento: {info["fundamento"]}</div>' if info['fundamento'] else '')
                    + '</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
elif pagina == 'Asignaturas críticas':
    banda('Asignaturas críticas', 'cursos donde más estudiantes reprueban o deben repetir')
    izq, der = st.columns(2)
    with izq:
        c = pd.read_csv(os.path.join(SRC, 'materias_criticas_canonicas.csv')).head(10)
        h = pd.read_csv(os.path.join(SRC, 'materias_criticas.csv')).set_index('materia')['indice']
        eq2011 = {'CALCULO INTEGRAL': 'Matemáticas II', 'FISICA MECANICA': 'Física I', 'CALCULO DIFERENCIAL': 'Matemáticas I',
                  'ALGORITMIA Y PROGRAMACION': 'Fundamentos de Programación', 'ELECTRICIDAD Y MAGNETISMO': 'Física II',
                  'SISTEMAS DIGITALES': 'Electrónica Básica', 'PROGRAMACION ORIENTADA A OBJETOS': 'Programación'}
        viz('barras', {'items': [{'nombre': nombre_oficial(r.materia), 'valor': r.indice, 'destacado': i < 5,
                                  'nota': ('plan 2011: ' + eq2011[r.materia]) if r.materia in eq2011 else 'mismo nombre en ambos planes'}
                                 for i, r in enumerate(c.itertuples())], 'margen': 280, 'color': '#B23B28', 'color2': '#E9B8A8'},
            titulo='Histórico · cohortes 2017-2 y 2018-1',
            ayuda='El índice combina la proporción de estudiantes que reprueban el curso (70 %) y cuántas veces, en '
                  'promedio, deben cursarlo (30 %); 1 es el curso más crítico. Los cursos del plan 2011 se agrupan '
                  'con su equivalente del plan 2018 (por ejemplo, Matemáticas II con Cálculo integral). '
                  'Muestra lo ocurrido; no es una predicción.',
            key='crit_est')
    with der:
        m = motor.normalizar_materias(MAT)
        m = m[m['OBSERVACION'].astype(str).str.upper().isin(motor.OBS_VALIDAS) & m['DEFINITIVA'].notna()]
        n_min = max(5, int(0.2 * MAT['CODIGO_INST'].nunique()))
        ult = m.sort_values('PERIODO_INSCRIPCION').groupby(['CODIGO_INST', 'MATERIA_CANONICA']).tail(1)
        veces = m.groupby(['CODIGO_INST', 'MATERIA_CANONICA', 'CURSO_INTENTOS']).size().groupby(level=[0, 1]).max() \
            .rename('veces').reset_index()
        g = ult.groupby('MATERIA_CANONICA').agg(N=('DEFINITIVA', 'size'), tasa=('DEFINITIVA', lambda s: (s < 3).mean()))
        g = g.join(veces.groupby('MATERIA_CANONICA')['veces'].mean()).query('N >= @n_min')
        nm = lambda x: (x - x.min()) / (x.max() - x.min() + 1e-9)
        g['indice'] = 0.7 * nm(g['tasa']) + 0.3 * nm(g['veces'])
        g = g.sort_values('indice', ascending=False).head(10).reset_index()
        viz('barras', {'items': [{'nombre': nombre_oficial(r.MATERIA_CANONICA), 'valor': r.indice, 'destacado': i < 5,
                                  'nota': f'{int(r.N)} estudiantes · reprobación {r.tasa*100:.0f} % · intentos {r.veces:.2f}'}
                                 for i, r in enumerate(g.itertuples())], 'margen': 280, 'color': '#B23B28', 'color2': '#E9B8A8'},
            titulo='Cohorte seleccionada', ayuda=f'Mismo índice, calculado con la cohorte elegida en la barra lateral. '
                                              f'Solo incluye cursos tomados por al menos {n_min} estudiantes.', key='crit_coh')

# ════════════════════════════════════════════════════════════════════════════
elif pagina == 'Cargar cohorte':
    c1, c2 = st.columns([1, .06])
    with c1:
        banda('Cargar una cohorte', 'plan 2011 (602xxx), plan 2018 (603xxx) o mezclados')
    with c2:
        ayuda('Cargue dos archivos con el formato del extracto del SIIF (CSV o Excel): las notas de los cursos y '
              'los puntajes Saber 11. **No incluya nombres ni números de documento**: basta un código. '
              'Los cursos del plan 2011 se traducen automáticamente a su equivalente del plan 2018, así que '
              'puede mezclar estudiantes de ambos planes. Descargue las plantillas para ver el formato.')
    plantilla_m = pd.DataFrame([['EST001', '2026-1', '2026-1', 603103, 'CALCULO DIFERENCIAL', 4, 3.2, 'N']], columns=motor.COLS_MATERIAS)
    plantilla_i = pd.DataFrame([['EST001', '2026-1', 66, 63, 64, 60, 62]], columns=motor.COLS_INGRESO)
    a, b, c = st.columns([1, 1, 1])
    fm = a.file_uploader('Materias cursadas', type=['csv', 'xlsx'])
    fi = b.file_uploader('Ingreso (Saber 11)', type=['csv', 'xlsx'])
    with c:
        st.download_button('Plantilla de materias', plantilla_m.to_csv(index=False).encode('utf-8-sig'), 'plantilla_materias.csv')
        st.download_button('Plantilla de ingreso', plantilla_i.to_csv(index=False).encode('utf-8-sig'), 'plantilla_ingreso.csv')
        usar_demo = st.toggle('Probar con la cohorte A (sintética)')
    if usar_demo:
        fm, fi = os.path.join(DEMO, 'A_materias.csv'), os.path.join(DEMO, 'A_ingreso.csv')
    if fm and fi:
        mat, ing = motor.leer_csv(fm), motor.leer_csv(fi)
        errores, avisos, rep = motor.validar_entrada(mat, ing)
        for er in errores:
            st.error(er)
        if not errores:
            norm = motor.normalizar_materias(mat)
            planes = norm['PLAN'].value_counts()
            fuentes_eq = norm['EQUIV_FUENTE'].map(lambda f: FUENTE_LEGIBLE.get(f, f)).value_counts()
            viz('carga', {'ok': not rep['codigos_fuera_de_catalogo'], 'planes': list(planes.index),
                          'estudiantes': int(mat['CODIGO_INST'].nunique()), 'registros': int(rep['registros']),
                          'fuera': len(rep['codigos_fuera_de_catalogo']), 'mezcla': int(rep['estudiantes_con_planes_mezclados']),
                          'fuentes': [{'fuente': k, 'n': int(v)} for k, v in fuentes_eq.items()]}, key='carga')
            for av in avisos:
                st.warning(av)
            if rep['discrepancias_de_nombre']:
                with st.expander(f"{len(rep['discrepancias_de_nombre'])} diferencia(s) de nombre frente al plan oficial"):
                    st.dataframe(pd.DataFrame(rep['discrepancias_de_nombre'],
                                              columns=['código', 'nombre en el archivo', 'nombre oficial']), hide_index=True)
            if st.button('Procesar y usar esta cohorte', type='primary'):
                st.session_state['cargada'] = (mat, ing)
                est, _ = motor.procesar_cohorte(mat, ing, M)
                st.success('Cohorte lista: selecciónela en «Cohorte» (barra lateral).')
                legible = motor.tabla_legible(est)
                st.dataframe(legible, hide_index=True, use_container_width=True)
                st.download_button('Descargar resultados', legible.to_csv(index=False).encode('utf-8-sig'),
                                   'trayecta_resultados.csv')

# ════════════════════════════════════════════════════════════════════════════
elif pagina == 'Simulador':
    c1, c2 = st.columns([1, .06])
    with c1:
        banda('Simulador', 'estudiante hipotético al cierre del 1.er semestre')
    with c2:
        ayuda('Mueva los valores para ver cómo cambia el riesgo de un estudiante hipotético. Son los mismos seis '
              'datos que usa la herramienta. El puntaje sirve para **ordenar** a los estudiantes por riesgo; no es '
              'una certeza sobre una persona: guíese por el nivel de alerta, no por el decimal.')
    izq, der = st.columns([1, 1.6])
    with izq:
        prom = st.slider('Promedio del primer semestre', 0.0, 5.0, 3.3, 0.1)
        sin1 = st.toggle('Sin notas de primer semestre', help='Caso de quien ingresó por homologación y no cursó el '
                                                               'primer semestre en el programa.')
        mat_ = st.slider('Saber 11 · matemáticas', 30, 100, 65)
        lec = st.slider('Saber 11 · lectura crítica', 30, 100, 63)
        nat = st.slider('Saber 11 · ciencias naturales', 30, 100, 64)
        otros = st.slider('Saber 11 · inglés + sociales', 60, 200, 125)
    x = pd.DataFrame([{'prom_sem1': motor.MEDIANA_PROM_SEM1 if sin1 else prom, 'sin_primer_semestre': int(sin1),
                       'icfes_total': mat_ + lec + nat + otros, 'icfes_mat': mat_, 'icfes_lec': lec, 'icfes_nat': nat}])
    p19 = float(M['art19']['modelo'].predict_proba(x[M['art19']['features']].values)[0, 1])
    pg = float(M['grad']['modelo'].predict_proba(x[M['grad']['features']].values)[0, 1])
    nivel = motor.nivel_alerta(p19, U)
    with der:
        g1, g2 = st.columns(2)
        with g1:
            viz('gauge', {'valor': p19, 'etiqueta': nivel.upper(), 'color': COLOR_NIVEL[nivel],
                          'zonas': [[0, U['equilibrado']['umbral'], '#1F9D6B'],
                                    [U['equilibrado']['umbral'], U['confirmado']['umbral'], '#E8A317'],
                                    [U['confirmado']['umbral'], 1, '#D93F3F']]},
                titulo='Riesgo de perder la calidad de estudiante', key='g19')
        with g2:
            viz('gauge', {'valor': pg, 'etiqueta': 'GRADUACIÓN', 'color': '#2A78D6'}, titulo='Probabilidad de graduación', key='ggr')

# ── «Acerca de»: condiciones de uso, modelos, comparación con el azar y límites ──
@st.dialog('Acerca de TRAYECTA', width='large')
def acerca():
    auc = T19.get('desempeno_canonico', {}).get('auc_pr', 0.745)
    azar = T19.get('linea_base_auc_pr', 0.2375)
    try:
        import ast
        auc_g = ast.literal_eval(TGR['comparativa'])['Random Forest']['AUC_PR']
    except Exception:
        auc_g = 0.705
    azar_g = TGR.get('linea_base_auc_pr', 0.389)
    t1, t2, t3, t4 = st.tabs(['Uso responsable', 'Qué calcula', 'Qué tan confiable es', 'Limitaciones'])
    with t1:
        st.markdown(
            '- TRAYECTA **apoya** al equipo académico; no reemplaza su criterio. Ninguna decisión sobre un estudiante '
            'debe tomarse solo con el puntaje.\n'
            '- Úsela para **priorizar el acompañamiento**, nunca para sancionar, excluir o etiquetar a un estudiante.\n'
            '- Los datos académicos son personales: cargue solo códigos, sin nombres ni documentos, y no comparta las '
            'listas descargadas fuera del personal autorizado.\n'
            '- Está pensada para **Ingeniería de Sistemas**, con estudiantes de los planes de estudio 2011 y 2018. '
            'En otros programas sus resultados no son válidos.\n'
            '- La alerta se calcula con la información disponible **al terminar el primer semestre** de cada '
            'estudiante.')
    with t2:
        st.markdown(f"""
**1 · Alerta de bajo rendimiento.** Estima el riesgo de que el estudiante **pierda la calidad de estudiante por bajo
rendimiento** en algún momento de la carrera. Usa seis datos: el promedio del primer semestre, si tiene o no notas de
primer semestre y cuatro puntajes de la prueba Saber 11 (total, matemáticas, lectura crítica y ciencias naturales).
Se clasifica en tres niveles:

- **Confirmado** · riesgo alto (puntaje desde {coma(U['confirmado']['umbral'])}).
- **Seguimiento** · riesgo moderado (desde {coma(U['equilibrado']['umbral'])}).
- **Sin alerta** · riesgo bajo.

**2 · Probabilidad de graduación.** Con los mismos seis datos, estima qué tan probable es que el estudiante se gradúe.

Ambos cálculos usan un **bosque aleatorio** (*Random Forest*): combina 150 árboles de decisión, cada uno aprendido
de los casos históricos, y promedia sus respuestas. Se eligió tras compararlo con otros cuatro métodos.

**3 · Situación académica por semestre.** No es una predicción: aplica las reglas del Reglamento Estudiantil a las
notas de cada semestre.""")
        for k, v in SIT_INFO.items():
            st.markdown(f"- **{k}.** {v['que_paso']} {v['implica']}" +
                        (f" <span style='color:#64748B;font-size:12px'>({v['fundamento']})</span>" if v['fundamento'] else ''),
                        unsafe_allow_html=True)
    with t3:
        st.markdown(
            'Una forma honesta de saber si la herramienta sirve es compararla con **elegir estudiantes al azar**. '
            'Las cifras provienen de los estudiantes de Ingeniería de Sistemas que ingresaron en 2017-2 y 2018-1, '
            'evaluados siempre con casos que la herramienta no había visto.')
        a, b = st.columns(2)
        with a:
            viz('barras', {'items': [{'nombre': 'TRAYECTA', 'valor': auc, 'destacado': True},
                                     {'nombre': 'Al azar', 'valor': azar}], 'margen': 90, 'fila': 44},
                titulo='Alerta de bajo rendimiento',
                ayuda='Capacidad para ubicar primero a quienes sí perdieron la calidad de estudiante (1 = perfecta). '
                      'Al azar se obtiene la proporción de casos en la población.', key='ac_a')
            st.markdown(f"**{auc / azar:.1f} veces** mejor que el azar.".replace('.', ',', 1))
        with b:
            viz('barras', {'items': [{'nombre': 'TRAYECTA', 'valor': auc_g, 'destacado': True},
                                     {'nombre': 'Al azar', 'valor': azar_g}], 'margen': 90, 'fila': 44,
                           'color': '#1F9D6B', 'color2': '#CBD5E1'},
                titulo='Probabilidad de graduación',
                ayuda='Capacidad para ubicar primero a quienes sí se graduaron (1 = perfecta).', key='ac_g')
            st.markdown(f"**{auc_g / azar_g:.1f} veces** mejor que el azar.".replace('.', ',', 1))
        st.markdown(
            f"- De cada 13 estudiantes con alerta **Confirmado**, {round(13 * U['confirmado']['precision'])} "
            "efectivamente perdieron la calidad de estudiante.\n"
            f"- El nivel **Seguimiento** identifica a {U['equilibrado']['recall'] * 100:.0f} % de quienes la perdieron, "
            "a cambio de alertar a cerca de la mitad de la cohorte.")
        curva = pd.read_csv(os.path.join(SRC, 'mvp_curva_umbral_art19.csv'))
        viz('curva', {'filas': curva.to_dict('records'),
                      'marcas': [{'u': U['confirmado']['umbral'], 'nombre': 'Confirmado'},
                                 {'u': U['equilibrado']['umbral'], 'nombre': 'Seguimiento'}]},
            titulo='Qué se gana y qué se pierde al mover el umbral',
            ayuda='Un umbral más bajo detecta más casos, pero alerta a más estudiantes que no los son. Cuántos '
                  'estudiantes acompañar es una decisión de la Universidad según su capacidad.', key='ac_c')
    with t4:
        st.markdown(
            '- Los modelos se construyeron con **80 a 90 estudiantes** de dos cohortes. Aún no se han comprobado con '
            'cohortes nuevas; los resultados deben revisarse cuando haya más datos.\n'
            '- Casi la mitad de quienes pierden la calidad de estudiante lo hacen **en el primer semestre**. En esos '
            'casos la alerta confirma lo ocurrido; no lo anticipa.\n'
            '- El puntaje sirve para **ordenar** a los estudiantes por riesgo. No es un porcentaje exacto de '
            'probabilidad para una persona.\n'
            '- Predecir la situación de cada semestre no funcionó mejor que el azar; por eso esa parte se calcula '
            'con las reglas del reglamento y no con un modelo.\n'
            '- «No graduado» incluye tanto a quien abandonó como a quien aún no termina.\n'
            '- Los estudiantes del plan 2018 tienden a obtener un promedio de primer semestre algo más alto; los '
            'niveles de alerta deberán revisarse con la primera cohorte completa de ese plan.\n'
            '- Los puntajes Saber 11 que falten se reemplazan por un valor típico, lo que reduce la precisión para '
            'ese estudiante.')


with st.container(key='acerca'):
    if st.button('i', help='Acerca de TRAYECTA: uso responsable, modelos y limitaciones'):
        acerca()
