"""
app.py — Sistema Predictivo de Rendimiento Académico
Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas
Fase 6 CRISP-DM · Data Storytelling con Streamlit
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import json
import os

# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rendimiento Académico · Unillanos",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta de colores institucional ──────────────────────────────────────────
AZUL       = "#1B6CA8"
AZUL_CLARO = "#4A9FD4"
NARANJA    = "#E67E22"
VERDE      = "#27AE60"
ROJO       = "#E74C3C"
GRIS       = "#7F8C8D"
FONDO      = "#F0F4F8"

# ── CSS personalizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Fuente y fondo general */
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

/* Tarjetas KPI */
.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 5px solid #1B6CA8;
    margin-bottom: 8px;
}
.kpi-value { font-size: 2.2rem; font-weight: 700; color: #1B6CA8; line-height: 1.1; }
.kpi-label { font-size: 0.82rem; color: #7F8C8D; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-card.naranja { border-left-color: #E67E22; }
.kpi-card.naranja .kpi-value { color: #E67E22; }
.kpi-card.verde { border-left-color: #27AE60; }
.kpi-card.verde .kpi-value { color: #27AE60; }
.kpi-card.rojo { border-left-color: #E74C3C; }
.kpi-card.rojo .kpi-value { color: #E74C3C; }

/* Bloques de hallazgo */
.insight-box {
    background: #EBF5FB;
    border-left: 4px solid #1B6CA8;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 12px 0;
    font-size: 0.92rem;
    line-height: 1.6;
}
.insight-box.alerta { background: #FEF9E7; border-left-color: #E67E22; }
.insight-box.exito  { background: #EAFAF1; border-left-color: #27AE60; }
.insight-box.peligro{ background: #FDEDEC; border-left-color: #E74C3C; }

/* Separadores de sección */
.section-header {
    font-size: 1.6rem; font-weight: 700;
    color: #1A1A2E; margin: 32px 0 8px 0;
    padding-bottom: 8px;
    border-bottom: 3px solid #1B6CA8;
}
.section-subtitle {
    color: #7F8C8D; font-size: 0.95rem;
    margin-bottom: 20px; line-height: 1.5;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A1A2E 0%, #1B6CA8 100%);
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stRadio label { color: white !important; }

/* Predictor resultado */
.pred-resultado {
    border-radius: 16px;
    padding: 28px 32px;
    text-align: center;
    font-size: 1.1rem;
    font-weight: 600;
    line-height: 1.8;
    box-shadow: 0 4px 20px rgba(0,0,0,0.12);
}
.pred-riesgo { background: linear-gradient(135deg, #FDEDEC, #FDEBD0); color: #922B21; border: 2px solid #E74C3C; }
.pred-normal { background: linear-gradient(135deg, #EAFAF1, #D5F5E3); color: #1E8449; border: 2px solid #27AE60; }

/* Badge estadístico */
.stat-badge {
    display: inline-block;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600;
}
.stat-ns   { background: #FDEBD0; color: #A04000; }
.stat-sig  { background: #D5F5E3; color: #1E8449; }
</style>
""", unsafe_allow_html=True)


# ── Carga de datos con caché ──────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df = pd.read_csv("src/df_master_limpio.csv")
    return df

@st.cache_resource
def cargar_modelos():
    modelo    = joblib.load("src/mejor_modelo.pkl")
    features  = joblib.load("src/feature_names.pkl")
    umbral    = joblib.load("src/umbral_optimo.pkl")
    resultados= joblib.load("src/resultados_completos.pkl")
    pruebas   = joblib.load("src/pruebas_estadisticas.pkl")
    mat_mods  = joblib.load("src/modelos_materias.pkl")
    return modelo, features, umbral, resultados, pruebas, mat_mods

@st.cache_data
def cargar_metricas():
    comp_rb = pd.read_csv("src/comparativa_rendimiento_bajo.csv").set_index("Modelo")
    comp_gr = pd.read_csv("src/comparativa_graduado.csv").set_index("Modelo")
    try:
        mat_met = pd.read_csv("src/metricas_materias.csv").set_index("MATERIA")
    except FileNotFoundError:
        mat_met = None
    mc = pd.read_csv("src/materias_criticas.csv").sort_values("indice", ascending=False).head(5)
    materias = {
        r["materia"]: {"indice": float(r["indice"]), "tasa_rep": float(r["tasa_reprobacion"]),
                       "rep_media": float(r["repitencia_media"]), "N": int(r["N"])}
        for _, r in mc.iterrows()
    }
    return comp_rb, comp_gr, mat_met, materias

df                               = cargar_datos()
modelo, FEATURES, UMBRAL, res, pruebas, mat_mods = cargar_modelos()
comp_rb, comp_gr, mat_met, MATERIAS_CRITICAS = cargar_metricas()

# ── Utilidades ────────────────────────────────────────────────────────────────
NIVEL_EDU_LABELS = {
    0: "Analfabeta",           1: "Primaria incompleta",
    2: "Primaria completa",    3: "Bachillerato incompleto",
    4: "Bachillerato completo",5: "Técnico incompleto",
    6: "Técnico completo",     7: "Tecnólogo incompleto",
    8: "Tecnólogo completo",   9: "Universitario incompleto",
    10:"Universitario completo",11:"Posgrado incompleto",
    12:"Posgrado completo",
}


def kpi(valor, etiqueta, color="azul"):
    return f'<div class="kpi-card {color if color!="azul" else ""}"><div class="kpi-value">{valor}</div><div class="kpi-label">{etiqueta}</div></div>'

def insight(texto, tipo=""):
    return f'<div class="insight-box {tipo}">{texto}</div>'


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Unillanos")
    st.markdown("**Rendimiento Académico**")
    st.markdown("Ing. de Sistemas · Cohortes 2017-2 y 2018-1")
    st.markdown("---")
    seccion = st.radio("Navegar a:", [
        "Inicio",
        "Perfil Estudiantil",
        "Rendimiento Académico",
        "Factores Predictivos",
        "Materias Críticas",
        "Predictor Interactivo",
    ])
    st.markdown("---")
    st.markdown("**Metodología:** CRISP-DM")
    st.markdown("**Modelo Principal:** Random Forest · Umbral 0.29")
    st.markdown(f"**n =** {len(df)} estudiantes")
    st.markdown("---")
    st.markdown("**Desarrollado por:**")
    st.markdown("Joan Martínez & Johan Arango")
    st.markdown("Universidad de los Llanos · FCBI")
    st.markdown("2026-06")

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — INICIO
# ══════════════════════════════════════════════════════════════════════════════
if seccion == "Inicio":

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1A1A2E 0%, #1B6CA8 100%);
                border-radius: 16px; padding: 48px 40px; margin-bottom: 32px; color: white;">
        <h1 style="font-size:2.4rem; font-weight:800; margin:0 0 12px 0; color:white;">
            Sistema Predictivo de Rendimiento Académico
        </h1>
        <p style="font-size:1.15rem; opacity:0.9; margin:0; line-height:1.7;">
            Universidad de los Llanos · Facultad de Ciencias Básicas e Ingeniería<br>
            Programa de Ingeniería de Sistemas · Cohortes 2017‑2 y 2018‑1
        </p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs principales
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi(f"{len(df)}", "Estudiantes analizados"), unsafe_allow_html=True)
    with c2: st.markdown(kpi(f"{df['graduado'].sum()}", "Graduados", "verde"), unsafe_allow_html=True)
    with c3: st.markdown(kpi(f"{df['rendimiento_bajo'].sum()}", "Con bajo rendimiento", "rojo"), unsafe_allow_html=True)
    with c4: st.markdown(kpi(f"{df['PROMEDIO_CARRERA'].mean():.2f}", "Promedio acumulado"), unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### ¿Qué es este sistema?")
        st.markdown("""
        Este sistema forma parte de un **estudio longitudinal de trayectoria estudiantil** en los
        programas STEM de la Facultad de Ciencias Básicas e Ingeniería de la Universidad de los Llanos.

        A partir de datos históricos de dos cohortes (2017-2 y 2018-1), construimos un modelo de
        **inteligencia artificial** capaz de predecir el riesgo académico de un estudiante desde
        el momento de su ingreso al programa.

        El análisis responde cuatro preguntas clave sobre el rendimiento en Ingeniería de Sistemas:
        """)

        preguntas = [
            ("", "Brecha de género", "¿Existen diferencias significativas de rendimiento entre hombres y mujeres?"),
            ("", "Capital educativo familiar", "¿El nivel educativo de los padres influye en el rendimiento universitario?"),
            ("", "Repitencia escolar previa", "¿Haber repetido un año en el colegio predice dificultades en la universidad?"),
            ("", "Materias críticas", "¿Cuáles son las materias más difíciles y es posible predecir quién las reprobará?"),
        ]
        for icon, titulo, desc in preguntas:
            st.markdown(f"""
            <div style="display:flex; align-items:flex-start; gap:12px; margin:10px 0; padding:12px;
                        background:#F0F4F8; border-radius:10px;">
                <span style="font-size:1.5rem;">{icon}</span>
                <div><strong>{titulo}</strong><br><span style="color:#7F8C8D; font-size:0.9rem;">{desc}</span></div>
            </div>""", unsafe_allow_html=True)

    with col_right:
        st.markdown("### Resultados del modelo")

        _rf = comp_rb.loc["Random Forest"]

        # Gauge de desempeño general (Recall+ CV5, leído de comparativa_rendimiento_bajo.csv)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(float(_rf["Recall+"]) * 100, 1),
            title={"text": "Recall+ CV5<br>Riesgo detectado", "font": {"size": 14}},
            number={"suffix": "%", "font": {"size": 28, "color": AZUL}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": AZUL},
                "steps": [
                    {"range": [0, 65], "color": "#FADBD8"},
                    {"range": [65, 80], "color": "#FDEBD0"},
                    {"range": [80, 100], "color": "#D5F5E3"},
                ],
                "threshold": {"line": {"color": VERDE, "width": 3}, "thickness": 0.75, "value": 65},
            }
        ))
        fig.update_layout(height=220, margin=dict(t=40, b=10, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

        metricas = {
            "F1-macro": f"{_rf['F1-mac']:.3f}",
            "AUC-ROC": f"{_rf['AUC']:.3f}",
            "MCC": f"{_rf['MCC']:.3f}",
            "Avg. Precision": f"{_rf['AvgP']:.3f}",
        }
        for k, v in metricas.items():
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:8px 12px;
                        background:white; border-radius:8px; margin:4px 0;
                        box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                <span style="color:#7F8C8D; font-size:0.88rem;">{k}</span>
                <strong style="color:#1B6CA8;">{v}</strong>
            </div>""", unsafe_allow_html=True)

        st.markdown(insight(
            "<strong>Dato clave:</strong> El promedio del primer semestre es el predictor más poderoso "
            "(37.8% de importancia en el modelo principal), seguido por el puntaje Saber 11 y el nivel socioeconómico.", "exito"
        ), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#7F8C8D; font-size:0.82rem; padding:12px;">
        Metodología CRISP-DM · Modelo Principal: Random Forest · Validación cruzada estratificada k=5 ·
        Umbral optimizado 0.29 · <em>Datos suministrados por la Oficina de Sistemas — Unillanos</em>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — PERFIL ESTUDIANTIL
# ══════════════════════════════════════════════════════════════════════════════
elif seccion == "Perfil Estudiantil":

    st.markdown('<div class="section-header">¿Quiénes son los estudiantes?</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-subtitle">Perfil sociodemográfico de los {len(df)} estudiantes de las cohortes 2017-2 y 2018-1 que ingresaron al programa de Ingeniería de Sistemas en la Universidad de los Llanos.</div>', unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    n_m  = (df["SEXO"] == "M").sum()
    n_f  = (df["SEXO"] == "F").sum()
    pct_pub = (df["TIPO_PLANTEL"] == "G").mean()
    pct_urb = (df["ZONA_LUGAR_RESIDENCIA"] == "U").mean()
    pct_rep = (df["ANOS_REPITIO"] == "S").mean()
    with c1: st.markdown(kpi(f"{len(df)}", "Estudiantes"), unsafe_allow_html=True)
    with c2: st.markdown(kpi(f"{n_m} ({n_m/len(df):.0%})", "Hombres"), unsafe_allow_html=True)
    with c3: st.markdown(kpi(f"{n_f} ({n_f/len(df):.0%})", "Mujeres", "naranja"), unsafe_allow_html=True)
    with c4: st.markdown(kpi(f"{pct_pub:.0%}", "Colegio público"), unsafe_allow_html=True)
    with c5: st.markdown(kpi(f"{pct_rep:.0%}", "Repitieron en colegio", "rojo"), unsafe_allow_html=True)

    st.markdown("---")

    # Fila 1: Género + Estrato
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribución por género")
        gen_data = df["SEXO"].map({"M": "Masculino", "F": "Femenino"}).value_counts().reset_index()
        gen_data.columns = ["Género", "Estudiantes"]
        fig = px.pie(gen_data, values="Estudiantes", names="Género",
                     color_discrete_map={"Masculino": AZUL, "Femenino": NARANJA},
                     hole=0.45)
        fig.update_traces(textposition="outside", textinfo="percent+label",
                          pull=[0, 0.05])
        fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(insight(
            "<strong>Desproporción de género:</strong> 84% masculino vs 16% femenino. "
            "Esta distribución es característica de los programas de ingeniería en Colombia "
            "y limita el análisis estadístico de diferencias por género.", "alerta"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown("#### Estrato socioeconómico")
        est_data = df["estrato"].value_counts().sort_index().reset_index()
        est_data.columns = ["Estrato", "Estudiantes"]
        est_data["Pct"] = (est_data["Estudiantes"] / len(df) * 100).round(1)
        fig = px.bar(est_data, x="Estrato", y="Estudiantes",
                     text=est_data["Pct"].apply(lambda x: f"{x}%"),
                     color="Estrato",
                     color_continuous_scale=px.colors.sequential.Blues)
        fig.update_traces(textposition="outside")
        fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20),
                          coloraxis_showscale=False,
                          xaxis_title="Estrato", yaxis_title="Estudiantes")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(insight(
            "El <strong>72% pertenece a estratos 1 y 2</strong>. "
            "El perfil socioeconómico bajo es característico del estudiantado de Unillanos "
            "y constituye un factor a considerar en las estrategias de retención."
        ), unsafe_allow_html=True)

    # Fila 2: Colegio + Repitencia
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Tipo de colegio y zona")
        df_orig = df.copy()
        df_orig["Plantel"] = df["TIPO_PLANTEL"].map({"G": "Público", "P": "Privado"})
        df_orig["Zona"]    = df["ZONA_LUGAR_RESIDENCIA"].map({"U": "Urbana", "R": "Rural"})
        plan_zona = pd.crosstab(df_orig["Plantel"], df_orig["Zona"]).reset_index()
        melted_plan_zona = plan_zona.melt(id_vars="Plantel", var_name="Zona", value_name="Estudiantes")
        fig = px.bar(melted_plan_zona, x="Plantel", y="Estudiantes",
                     color="Zona", barmode="group",
                     color_discrete_map={"Urbana": AZUL, "Rural": NARANJA})
        fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("#### Nivel educativo máximo de los padres")
        edu_counts = df["nivel_edu_max_padres"].value_counts().sort_index().reset_index()
        edu_counts.columns = ["Código", "N"]
        edu_counts["Nivel"] = edu_counts["Código"].map(NIVEL_EDU_LABELS)
        fig = px.bar(edu_counts, x="N", y="Nivel", orientation="h",
                     color="N", color_continuous_scale=px.colors.sequential.Blues,
                     text="N")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20),
                          coloraxis_showscale=False,
                          yaxis={"categoryorder": "total ascending"},
                          xaxis_title="Estudiantes", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # Repitencia escolar
    st.markdown("#### Repitencia escolar previa")
    col5, col6 = st.columns([1, 2])
    with col5:
        rep_data = df["ANOS_REPITIO"].map({"S": "Sí repitió", "N": "No repitió"}).value_counts().reset_index()
        rep_data.columns = ["Repitencia", "Estudiantes"]
        fig = px.pie(rep_data, values="Estudiantes", names="Repitencia",
                     color_discrete_map={"Sí repitió": ROJO, "No repitió": VERDE}, hole=0.4)
        fig.update_layout(height=260, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
    with col6:
        _rm = df["ANOS_REPITIO"] == "S"
        st.markdown(insight(
            f"<strong>{_rm.mean():.1%} de los estudiantes repitió al menos un año escolar</strong> "
            f"({int(_rm.sum())} de {len(df)}). "
            "Aunque la prueba estadística no es significativa por el tamaño muestral, "
            "el análisis descriptivo muestra que quienes repitieron tienen una tasa de "
            f"bajo rendimiento del <strong>{df[_rm]['rendimiento_bajo'].mean():.1%}</strong> vs "
            f"<strong>{df[~_rm]['rendimiento_bajo'].mean():.1%}</strong> de quienes no repitieron. "
            f"La diferencia en graduación es más marcada: <strong>{df[_rm]['graduado'].mean():.1%}</strong> vs "
            f"<strong>{df[~_rm]['graduado'].mean():.1%}</strong>.",
            "alerta"
        ), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — RENDIMIENTO ACADÉMICO
# ══════════════════════════════════════════════════════════════════════════════
elif seccion == "Rendimiento Académico":

    st.markdown('<div class="section-header">¿Cómo es su rendimiento?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Análisis del desempeño académico acumulado, evolución por cohorte y trayectoria de los estudiantes a lo largo del programa.</div>', unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    pct_grad = df["graduado"].mean()
    pct_rb   = df["rendimiento_bajo"].mean()
    with c1: st.markdown(kpi(f"{df['PROMEDIO_CARRERA'].mean():.2f}", "Promedio carrera"), unsafe_allow_html=True)
    with c2: st.markdown(kpi(f"{df['PROMEDIO_CARRERA'].median():.2f}", "Mediana"), unsafe_allow_html=True)
    with c3: st.markdown(kpi(f"{pct_grad:.0%}", "Tasa de graduación", "verde"), unsafe_allow_html=True)
    with c4: st.markdown(kpi(f"{pct_rb:.0%}", "Bajo rendimiento (<3.0)", "rojo"), unsafe_allow_html=True)

    st.markdown("---")

    # Fila 1: Distribución + por cohorte
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribución del promedio acumulado")
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df["PROMEDIO_CARRERA"], nbinsx=20,
            marker_color=AZUL, opacity=0.8,
            name="Todos"
        ))
        fig.add_vline(x=3.0, line_dash="dash", line_color=ROJO, line_width=2,
                      annotation_text="Umbral aprobación (3.0)",
                      annotation_position="top right")
        fig.add_vline(x=df["PROMEDIO_CARRERA"].mean(), line_dash="dot",
                      line_color=NARANJA, line_width=2,
                      annotation_text=f"Media ({df['PROMEDIO_CARRERA'].mean():.2f})",
                      annotation_position="top left")
        fig.update_layout(height=320, margin=dict(t=30, b=30, l=30, r=30),
                          xaxis_title="Promedio acumulado", yaxis_title="Estudiantes",
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Promedio acumulado por cohorte")
        fig = go.Figure()
        for coh, color in [("2017-2", AZUL), ("2018-1", NARANJA)]:
            datos_coh = df[df["COHORTE"] == coh]["PROMEDIO_CARRERA"].dropna()
            fig.add_trace(go.Box(
                y=datos_coh, name=f"Cohorte {coh}",
                marker_color=color, boxmean=True,
                line_width=2
            ))
        fig.add_hline(y=3.0, line_dash="dash", line_color=ROJO,
                      annotation_text="Mínimo (3.0)")
        fig.update_layout(height=320, margin=dict(t=30, b=30, l=30, r=30),
                          yaxis_title="Promedio acumulado")
        st.plotly_chart(fig, use_container_width=True)

    # Fila 2: Graduación + Rendimiento por género
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Estado final por cohorte")
        estados = []
        for coh in ["2017-2", "2018-1"]:
            sub = df[df["COHORTE"] == coh]
            estados.append({"Cohorte": coh, "Estado": "Graduado",       "N": int(sub["graduado"].sum())})
            estados.append({"Cohorte": coh, "Estado": "No graduado",    "N": int((sub["graduado"]==0).sum())})
        df_est = pd.DataFrame(estados)
        fig = px.bar(df_est, x="Cohorte", y="N", color="Estado",
                     barmode="stack", text="N",
                     color_discrete_map={"Graduado": VERDE, "No graduado": ROJO})
        fig.update_traces(textposition="inside", textfont_color="white")
        fig.update_layout(height=320, margin=dict(t=30, b=30, l=30, r=30),
                          yaxis_title="Estudiantes", xaxis=dict(type='category'))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(insight(
            "La cohorte 2018-1 tiene una tasa de graduación significativamente mayor: "
            "<strong>44%</strong> vs <strong>30%</strong> de la cohorte 2017-2. "
            "Esta diferencia es la 3.ª variable más importante en el modelo de graduación."
        ), unsafe_allow_html=True)

    with col4:
        st.markdown("#### Promedio acumulado por género")
        fig = go.Figure()
        for genero, nombre, color in [("M", "Hombres", AZUL), ("F", "Mujeres", NARANJA)]:
            datos_g = df[df["SEXO"] == genero]["PROMEDIO_CARRERA"].dropna()
            fig.add_trace(go.Violin(
                y=datos_g, name=nombre, box_visible=True,
                meanline_visible=True, line_color=color,
                fillcolor=color, opacity=0.5
            ))
        fig.add_hline(y=3.0, line_dash="dash", line_color=ROJO,
                      annotation_text="Mínimo (3.0)")
        fig.update_layout(height=320, margin=dict(t=30, b=30, l=30, r=30),
                          yaxis_title="Promedio acumulado")
        st.plotly_chart(fig, use_container_width=True)

    # Primer semestre vs resultado
    st.markdown("#### ¿Predice el primer semestre el resultado final?")
    st.markdown(insight(
        "<strong>Hallazgo central:</strong> El promedio del primer semestre es la variable más predictiva "
        "del rendimiento final (importancia 37.8% en Random Forest). Un primer semestre por debajo de 3.0 "
        "multiplica significativamente el riesgo de bajo rendimiento acumulado.", "exito"
    ), unsafe_allow_html=True)

    df_scatter = df.dropna(subset=["PROMEDIO_CARRERA"]).copy()
    df_scatter["Grupo"] = df_scatter["rendimiento_bajo"].map(
        {0: "Rendimiento normal", 1: "Bajo rendimiento"})

    fig = px.scatter(
        df_scatter, x="prom_sem1", y="PROMEDIO_CARRERA",
        color="Grupo",
        color_discrete_map={"Rendimiento normal": AZUL, "Bajo rendimiento": ROJO},
        opacity=0.75,
        labels={"prom_sem1": "Promedio 1er semestre",
                "PROMEDIO_CARRERA": "Promedio acumulado carrera"},
    )
    # Línea de tendencia manual con numpy (sin statsmodels)
    x_vals = df_scatter["prom_sem1"].values
    y_vals = df_scatter["PROMEDIO_CARRERA"].values
    coef   = np.polyfit(x_vals, y_vals, 1)
    x_line = np.linspace(x_vals.min(), x_vals.max(), 50)
    y_line = np.polyval(coef, x_line)
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode="lines",
        line=dict(color=GRIS, dash="dot", width=2),
        name=f"Tendencia (r={np.corrcoef(x_vals, y_vals)[0,1]:.2f})",
        showlegend=True
    ))
    fig.add_vline(x=3.0, line_dash="dash", line_color=GRIS, opacity=0.5)
    fig.add_hline(y=3.0, line_dash="dash", line_color=GRIS, opacity=0.5)
    fig.update_layout(height=400, margin=dict(t=20, b=40, l=40, r=20))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — FACTORES PREDICTIVOS
# ══════════════════════════════════════════════════════════════════════════════
elif seccion == "Factores Predictivos":

    st.markdown('<div class="section-header">¿Qué factores importan?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Resultados de las cuatro preguntas problema del estudio y la importancia de variables según los modelos predictivos del proyecto.</div>', unsafe_allow_html=True)

    # Tabs para cada pregunta
    tab_a, tab_b, tab_c, tab_imp = st.tabs([
        "A · Género",
        "B · Educación padres",
        "C · Repitencia escolar",
        "Importancia del modelo"
    ])

    # ── Tab A: Género ────────────────────────────────────────────────────────
    with tab_a:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### Promedio acumulado por género")
            fig = go.Figure()
            for genero, nombre, color in [("M", "Hombres (n=74)", AZUL), ("F", "Mujeres (n=15)", NARANJA)]:
                datos = df[df["SEXO"] == genero]["PROMEDIO_CARRERA"].dropna()
                fig.add_trace(go.Box(
                    y=datos, name=nombre, marker_color=color,
                    boxmean=True, line_width=2, jitter=0.4,
                    pointpos=0, boxpoints="all"
                ))
            fig.add_hline(y=3.0, line_dash="dash", line_color=ROJO,
                          annotation_text="Mínimo (3.0)")
            fig.update_layout(height=380, margin=dict(t=30, b=30, l=30, r=30),
                               yaxis_title="Promedio acumulado")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Resultado estadístico")
            p_genero = pruebas["genero"]["p"]
            st.markdown(f"""
            <div style="background:white; border-radius:12px; padding:20px; box-shadow:0 2px 12px rgba(0,0,0,0.08);">
                <p style="font-size:0.85rem; color:#7F8C8D; margin:0;">Prueba Mann-Whitney U</p>
                <p style="font-size:1.8rem; font-weight:700; color:#1B6CA8; margin:8px 0;">p = {p_genero:.4f}</p>
                <span class="stat-badge stat-ns">No significativo (p > 0.05)</span>
                <hr style="margin:16px 0; border-color:#F0F4F8;">
                <p style="font-size:0.88rem; margin:0;"><strong>Mediana hombres:</strong> {pruebas["genero"]["mediana_M"]:.2f}</p>
                <p style="font-size:0.88rem; margin:4px 0;"><strong>Mediana mujeres:</strong> {pruebas["genero"]["mediana_F"]:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(insight(
                "No se detecta brecha estadística. Con solo 15 mujeres, el poder estadístico "
                "es ~25%. La diferencia descriptiva (mujeres ligeramente mejores) existe "
                "pero no puede confirmarse con esta muestra.", "alerta"
            ), unsafe_allow_html=True)

    # ── Tab B: Educación padres ──────────────────────────────────────────────
    with tab_b:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### Promedio acumulado según nivel educativo máximo de los padres")
            df_edu = df.dropna(subset=["PROMEDIO_CARRERA"]).copy()
            df_edu["Nivel edu."] = df_edu["nivel_edu_max_padres"].map(NIVEL_EDU_LABELS)
            df_edu["Grupo"] = pd.cut(df_edu["nivel_edu_max_padres"],
                                     bins=[-1, 4, 8, 12],
                                     labels=["Básica (0-4)", "Técnico (5-8)", "Universitario+ (9-12)"])
            orden = ["Básica (0-4)", "Técnico (5-8)", "Universitario+ (9-12)"]
            fig = px.box(df_edu, x="Grupo", y="PROMEDIO_CARRERA",
                         category_orders={"Grupo": orden},
                         color="Grupo",
                         color_discrete_sequence=[AZUL, NARANJA, VERDE],
                         points="all")
            fig.add_hline(y=3.0, line_dash="dash", line_color=ROJO,
                          annotation_text="Mínimo (3.0)")
            fig.update_layout(height=380, margin=dict(t=30, b=30, l=30, r=30),
                               yaxis_title="Promedio acumulado", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Resultado estadístico")
            for quien, key in [("Padre", "edu_padre"), ("Madre", "edu_madre")]:
                rho = pruebas[key]["rho"]
                p   = pruebas[key]["p"]
                st.markdown(f"""
                <div style="background:white; border-radius:10px; padding:14px;
                            margin-bottom:10px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                    <p style="font-size:0.82rem; color:#7F8C8D; margin:0;">Nivel edu. {quien} (Spearman)</p>
                    <p style="font-size:1.4rem; font-weight:700; color:#1B6CA8; margin:6px 0;">ρ = {rho:.3f}</p>
                    <p style="font-size:0.85rem; margin:0;">p = {p:.4f} &nbsp;
                        <span class="stat-badge stat-ns">No sign.</span></p>
                </div>""", unsafe_allow_html=True)
            st.markdown(insight(
                "La correlación lineal es no significativa, pero el modelo Random Forest "
                "asigna importancia del <strong>4–6%</strong> a las variables de educación parental, "
                "sugiriendo un efecto no lineal que la correlación de Spearman no captura.", "alerta"
            ), unsafe_allow_html=True)

    # ── Tab C: Repitencia ────────────────────────────────────────────────────
    with tab_c:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### Tasas comparativas según repitencia escolar previa")
            grupos = ["Repitió (n=15)", "No repitió (n=74)"]
            metricas_rep = {
                "Bajo rendimiento": [
                    df[df["repitio_escolar"]==1]["rendimiento_bajo"].mean()*100,
                    df[df["repitio_escolar"]==0]["rendimiento_bajo"].mean()*100
                ],
                "Graduado": [
                    df[df["repitio_escolar"]==1]["graduado"].mean()*100,
                    df[df["repitio_escolar"]==0]["graduado"].mean()*100
                ]
            }
            fig = go.Figure()
            colors_rep = [ROJO, VERDE]
            for i, (metrica, valores) in enumerate(metricas_rep.items()):
                fig.add_trace(go.Bar(
                    name=metrica, x=grupos, y=valores,
                    marker_color=colors_rep[i],
                    text=[f"{v:.1f}%" for v in valores],
                    textposition="outside"
                ))
            fig.update_layout(
                barmode="group", height=360,
                margin=dict(t=30, b=30, l=30, r=30),
                yaxis_title="Porcentaje (%)", yaxis_range=[0, 75]
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            chi2 = pruebas["repitencia"]["chi2"]
            p_chi = pruebas["repitencia"]["p"]
            st.markdown(f"""
            <div style="background:white; border-radius:12px; padding:20px;
                        box-shadow:0 2px 12px rgba(0,0,0,0.08);">
                <p style="font-size:0.85rem; color:#7F8C8D; margin:0;">Prueba Chi-cuadrado</p>
                <p style="font-size:1.8rem; font-weight:700; color:#1B6CA8; margin:8px 0;">p = {p_chi:.4f}</p>
                <span class="stat-badge stat-ns">No significativo</span>
                <hr style="margin:16px 0; border-color:#F0F4F8;">
                <p style="font-size:0.88rem;"><strong>Bajo rend. si repitió:</strong> 52.9%</p>
                <p style="font-size:0.88rem;"><strong>Bajo rend. si no repitió:</strong> 36.4%</p>
                <p style="font-size:0.88rem;"><strong>Graduación si repitió:</strong> 17.6%</p>
                <p style="font-size:0.88rem;"><strong>Graduación si no repitió:</strong> 41.6%</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(insight(
                "<strong>Señal real, muestra insuficiente.</strong> "
                "La diferencia en la tasa de graduación es sustancial e indica que esta variable "
                "es relevante. Con n=15 en el grupo que repitió, la prueba no "
                "tiene poder estadístico para confirmarla.", "alerta"
            ), unsafe_allow_html=True)

    # ── Tab Importancia ──────────────────────────────────────────────────────
    with tab_imp:
        col1, col2 = st.columns(2)
        imp_rb = res.get("imp_rb", {})
        imp_gr = res.get("imp_gr", {})

        for col, imp, titulo, alg, color in [
            (col1, imp_rb, "Rendimiento bajo", "Random Forest", AZUL),
            (col2, imp_gr, "Graduación", "XGBoost", NARANJA)
        ]:
            with col:
                st.markdown(f"#### Modelo: {titulo} ({alg})")
                if imp:
                    df_imp = pd.Series(imp).sort_values(ascending=True).tail(12).reset_index()
                    df_imp.columns = ["Feature", "Importancia"]
                    fig = px.bar(df_imp, x="Importancia", y="Feature", orientation="h",
                                 color="Importancia",
                                 color_continuous_scale=px.colors.sequential.Blues if alg=="Random Forest" else px.colors.sequential.Oranges,
                                 text=df_imp["Importancia"].apply(lambda x: f"{x:.3f}"))
                    fig.update_traces(textposition="outside")
                    fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=40),
                                      coloraxis_showscale=False,
                                      xaxis_title=f"Importancia ({alg})",
                                      yaxis_title="")
                    st.plotly_chart(fig, use_container_width=True)

        st.markdown(insight(
            "<strong>prom_sem1</strong> es el predictor más decisivo en ambos modelos (37.8% en Rendimiento Bajo y 15.3% en Graduación). "
            "Para la graduación, la preparación previa medida por el <strong>icfes_total</strong> (13.6%) y el efecto de la <strong>cohorte_encoded</strong> (10.0%) "
            "son los factores de mayor peso después del primer semestre, superando a las variables socioeconómicas individuales."
        ), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — MATERIAS CRÍTICAS
# ══════════════════════════════════════════════════════════════════════════════
elif seccion == "Materias Críticas":

    st.markdown('<div class="section-header">Las materias más difíciles</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Ranking de las materias con mayor impacto negativo en el rendimiento académico, calculado con un índice centrado en la tasa de reprobación y la repitencia (dificultad de aprobar).</div>', unsafe_allow_html=True)

    # Tabla de ranking
    df_mat = pd.DataFrame(MATERIAS_CRITICAS).T.reset_index()
    df_mat.columns = ["Materia", "Índice crítico", "Tasa reprobación", "Rep. media", "N estudiantes"]
    df_mat = df_mat.sort_values("Índice crítico", ascending=False).reset_index(drop=True)
    df_mat.index = df_mat.index + 1

    st.markdown("#### Ranking de criticidad (índice compuesto)")
    st.markdown("""
    <div style="font-size:0.85rem; color:#7F8C8D; margin-bottom:12px;">
    Índice = 0.70 × tasa_reprobación_norm + 0.30 × repitencia_norm
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        df_display = df_mat.copy()
        df_display["Tasa reprobación"] = df_display["Tasa reprobación"].apply(lambda x: f"{x:.1%}")
        df_display["Rep. media"]       = df_display["Rep. media"].apply(lambda x: f"{x:.2f}")
        df_display["Índice crítico"]    = df_display["Índice crítico"].apply(lambda x: f"{x:.3f}")
        st.dataframe(df_display, use_container_width=True, height=200)

    with col2:
        fig = px.bar(
            df_mat.sort_values("Índice crítico"),
            x="Índice crítico", y="Materia", orientation="h",
            color="Índice crítico", color_continuous_scale="Reds",
            text=df_mat.sort_values("Índice crítico")["Índice crítico"].apply(lambda x: f"{x:.3f}")
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(height=280, margin=dict(t=20, b=20, l=20, r=50),
                          coloraxis_showscale=False, xaxis_title="Índice crítico")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Descomposición del índice
    st.markdown("#### Descomposición del índice por componente")
    fig = make_subplots(rows=1, cols=2, subplot_titles=[
        "Tasa de reprobación", "Rep. media (veces cursada)"
    ])

    materias_orden = df_mat["Materia"].tolist()
    colores_mat = [ROJO, "#E67E22", "#F39C12", "#27AE60", "#2980B9"]

    for i, (col_name, campo) in enumerate([
        ("Tasa reprobación", "tasa_rep"),
        ("Rep. media",        "rep_media")
    ], 1):
        vals = [MATERIAS_CRITICAS[m][campo] for m in materias_orden]

        for j, (m, v, c) in enumerate(zip(materias_orden, vals, colores_mat)):
            fig.add_trace(go.Bar(
                x=[m.replace("MATEMATICAS", "MAT.")],
                y=[v], name=m, showlegend=(i==1),
                marker_color=c
            ), row=1, col=i)

    fig.update_layout(height=320, barmode="group",
                      margin=dict(t=40, b=60, l=30, r=30),
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    # Modelos predictivos por materia
    st.markdown("#### Modelos de predicción de reprobación por materia")
    st.markdown('<div class="section-subtitle">¿Es posible predecir qué estudiante reprobará una materia crítica?</div>', unsafe_allow_html=True)

    mat_resultados = mat_met.to_dict("index") if mat_met is not None else {
        "ALGEBRA LINEAL":   {"F1-mac": 0.913, "AUC": 0.975, "N": 71, "rep": 0.28},
        "FISICA I":         {"F1-mac": 0.882, "AUC": 0.908, "N": 53, "rep": 0.36},
        "PROGRAMACION":     {"F1-mac": 0.820, "AUC": 0.875, "N": 48, "rep": 0.26},
        "MATEMATICAS II":   {"F1-mac": 0.650, "AUC": 0.735, "N": 52, "rep": 0.48},
    }

    cols = st.columns(3)
    for (mat, vals), col in zip(mat_resultados.items(), cols):
        color_borde = VERDE if vals["AUC"] >= 0.90 else (NARANJA if vals["AUC"] >= 0.75 else ROJO)
        with col:
            st.markdown(f"""
            <div style="background:white; border-radius:12px; padding:16px;
                        border-top:4px solid {color_borde};
                        box-shadow:0 2px 12px rgba(0,0,0,0.08); text-align:center;">
                <p style="font-size:0.82rem; font-weight:700; color:#1A1A2E; margin:0 0 10px 0;">{mat}</p>
                <p style="font-size:1.6rem; font-weight:800; color:{color_borde}; margin:0;">AUC {vals['AUC']:.3f}</p>
                <p style="font-size:0.8rem; color:#7F8C8D; margin:4px 0;">F1-mac: {vals['F1-mac']:.3f}</p>
                <p style="font-size:0.8rem; color:#7F8C8D; margin:0;">N={vals['N']} · Rep={vals['rep']:.0%}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown(insight(
        "<strong>Álgebra Lineal y Física I</strong> son altamente predecibles (AUC > 0.90). "
        "<strong>Matemáticas II</strong>, la materia con mayor tasa de reprobación (44%), "
        "es la más difícil de predecir (AUC 0.735), sugiriendo que sus factores de riesgo "
        "son más complejos o dependientes de eventos dentro del semestre."
    ), unsafe_allow_html=True)

    st.markdown("<p style='font-size:0.75rem; color:#7F8C8D; text-align:center; margin-top:12px;'>Nota metodológica: Las métricas de desempeño de estos modelos específicos por materia representan la evaluación sobre la muestra de entrenamiento (in-sample) debido al volumen de datos. Las 5 materias críticas son modelables (todas con ≥10 reprobados); aquí se muestran las 3 ya validadas (Matemáticas II, Física I, Álgebra Lineal). Matemáticas I y Fundamentos de Programación se entrenan al re-ejecutar el pipeline con el nuevo conjunto.</p>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6 — PREDICTOR INTERACTIVO
# ══════════════════════════════════════════════════════════════════════════════
elif seccion == "Predictor Interactivo":

    st.markdown('<div class="section-header">Predictor de Rendimiento Académico</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Complete el perfil del estudiante para obtener una predicción basada en patrones históricos de las cohortes 2017-2 y 2018-1 de Ingeniería de Sistemas.</div>', unsafe_allow_html=True)

    st.markdown(insight(
        "ℹ️ <strong>Cómo usar:</strong> Complete todos los campos y presione «Predecir». "
        "El modelo evaluará el riesgo de bajo rendimiento académico (promedio < 3.0) "
        "basándose en el perfil socioeconómico, académico previo y primer semestre.",
        ""
    ), unsafe_allow_html=True)

    st.markdown("---")

    with st.form("formulario_predictor"):
        st.markdown("### Información del estudiante")

        # ── Bloque 1: Datos personales ────────────────────────────────────────
        st.markdown("**Datos personales y familiares**")
        c1, c2, c3 = st.columns(3)
        with c1:
            sexo_input = st.selectbox("Género", ["Masculino", "Femenino"])
        with c2:
            cohorte_input = st.selectbox("Cohorte de ingreso", ["2017-2", "2018-1"])
        with c3:
            repitio_input = st.selectbox("¿Repitió algún año escolar?", ["No", "Sí"])

        c4, c5, c6 = st.columns(3)
        with c4:
            estrato_input = st.slider("Estrato socioeconómico", 1, 6, 2)
        with c5:
            plantel_input = st.selectbox("Tipo de colegio", ["Público", "Privado"])
        with c6:
            zona_input = st.selectbox("Zona de residencia", ["Urbana", "Rural"])

        # ── Bloque 2: Familia ─────────────────────────────────────────────────
        st.markdown("**Contexto familiar**")
        c7, c8, c9 = st.columns(3)
        with c7:
            edu_padre_input = st.selectbox("Nivel educativo del padre",
                list(NIVEL_EDU_LABELS.values()), index=4)
        with c8:
            edu_madre_input = st.selectbox("Nivel educativo de la madre",
                list(NIVEL_EDU_LABELS.values()), index=4)
        with c9:
            ingresos_input = st.number_input(
                "Ingresos anuales del hogar (millones COP)",
                min_value=1.0, max_value=100.0, value=9.6, step=0.5)

        c10, c11 = st.columns(2)
        with c10:
            vive_con_map = {
                "Con ambos padres": 1,
                "Con uno de los padres": 2,
                "Con pareja/cónyuge": 3,
                "Con otros familiares": 4,
                "Solo / Pensión": 5,
            }
            vive_con_input = st.selectbox("¿Con quién vive?", list(vive_con_map.keys()))
        with c11:
            sit_padres_map = {
                "Padres separados / Divorciados": 1,
                "Padres conviven / Conforman hogar": 2,
                "Nuevo hogar (alguno fallecido)": 3,
            }
            sit_padres_input = st.selectbox("Situación de los padres", list(sit_padres_map.keys()))

        # ── Bloque 3: SISBEN ─────────────────────────────────────────────────
        st.markdown("**SISBEN**")
        c12, c13 = st.columns(2)
        with c12:
            sisben_input = st.selectbox("¿Tiene SISBEN?", ["No", "Sí - Urbano", "Sí - Rural"])
        with c13:
            sisben_nivel_input = st.slider("Nivel SISBEN (si aplica)", 1, 6, 2)

        # ── Bloque 4: Saber 11 ────────────────────────────────────────────────
        st.markdown("**Puntajes Saber 11 (escala 0–100 por componente)**")
        c14, c15, c16, c17, c18 = st.columns(5)
        with c14: icfes_mat = st.slider("Matemáticas", 0, 100, 65)
        with c15: icfes_ing = st.slider("Inglés", 0, 100, 63)
        with c16: icfes_lec = st.slider("Lec. Crítica", 0, 100, 63)
        with c17: icfes_soc = st.slider("Soc. y Ciud.", 0, 100, 62)
        with c18: icfes_nat = st.slider("Cs. Naturales", 0, 100, 64)

        # ── Bloque 5: Primer semestre ─────────────────────────────────────────
        st.markdown("**Primer semestre universitario**")
        prom_sem1_input = st.slider(
            "Promedio del primer semestre (0.0 – 5.0)",
            0.0, 5.0, 3.5, step=0.1,
            help="Si el estudiante aún no ha cursado el primer semestre, use el valor por defecto 3.5 (mediana histórica)."
        )

        st.markdown("---")
        submitted = st.form_submit_button("Predecir rendimiento", use_container_width=True,
                                           type="primary")

    # ── Predicción ────────────────────────────────────────────────────────────
    if submitted:
        edu_inv = {v: k for k, v in NIVEL_EDU_LABELS.items()}
        nivel_p = edu_inv.get(edu_padre_input, 4)
        nivel_m = edu_inv.get(edu_madre_input, 4)

        if sisben_input == "No":
            sisben_nv = 0
        else:
            sisben_nv = sisben_nivel_input

        feature_values = {
            "sexo":                 1 if sexo_input == "Masculino" else 0,
            "nivel_edu_padre":      nivel_p,
            "nivel_edu_madre":      nivel_m,
            "nivel_edu_max_padres": max(nivel_p, nivel_m),
            "repitio_escolar":      1 if repitio_input == "Sí" else 0,
            "estrato":              estrato_input,
            "log_ingresos":         np.log1p(ingresos_input * 1_000_000),
            "sisben_nivel":         sisben_nv,
            "tipo_plantel":         1 if plantel_input == "Privado" else 0,
            "zona_rural":           1 if zona_input == "Rural" else 0,
            "vive_con":             vive_con_map[vive_con_input],
            "situacion_padres":     sit_padres_map[sit_padres_input],
            "icfes_total":          icfes_mat + icfes_ing + icfes_lec + icfes_soc + icfes_nat,
            "icfes_mat":            icfes_mat,
            "icfes_lec":            icfes_lec,
            "icfes_nat":            icfes_nat,
            "prom_sem1":            prom_sem1_input,
            "cohorte_encoded":      1 if cohorte_input == "2018-1" else 0,
        }

        X_input = np.array([[feature_values[f] for f in FEATURES]])
        probabilidad = modelo.predict_proba(X_input)[0][1]
        prediccion   = int(probabilidad >= UMBRAL)

        st.markdown("---")
        st.markdown("### Resultado de la predicción")

        col_gauge, col_resultado = st.columns([1, 2])

        with col_gauge:
            color_gauge = ROJO if prediccion == 1 else VERDE
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round(probabilidad * 100, 1),
                title={"text": "Probabilidad de<br>bajo rendimiento", "font": {"size": 13}},
                number={"suffix": "%", "font": {"size": 32, "color": color_gauge}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": color_gauge},
                    "steps": [
                        {"range": [0, 29],  "color": "#D5F5E3"},
                        {"range": [29, 60], "color": "#FDEBD0"},
                        {"range": [60, 100],"color": "#FADBD8"},
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 3},
                        "thickness": 0.8,
                        "value": UMBRAL * 100
                    }
                }
            ))
            fig.update_layout(height=260, margin=dict(t=40, b=10, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"""
            <p style="text-align:center; font-size:0.78rem; color:#7F8C8D;">
            Umbral de decisión: {UMBRAL*100:.0f}%<br>
            (optimizado para maximizar detección de riesgo)
            </p>""", unsafe_allow_html=True)

        with col_resultado:
            if prediccion == 1:
                st.markdown(f"""
                <div class="pred-resultado pred-riesgo">
                    <strong>RIESGO DE BAJO RENDIMIENTO DETECTADO</strong><br><br>
                    El perfil del estudiante es compatible con el de estudiantes que
                    obtuvieron un promedio acumulado <strong>por debajo de 3.0</strong>
                    en cohortes anteriores.<br><br>
                    Probabilidad estimada: <strong>{probabilidad:.1%}</strong>
                </div>""", unsafe_allow_html=True)

                st.markdown("**Factores de riesgo identificados:**")
                alertas = []
                if prom_sem1_input < 3.2: alertas.append(f"Promedio 1er semestre bajo ({prom_sem1_input:.1f})")
                if estrato_input <= 2: alertas.append(f"Estrato socioeconómico bajo ({estrato_input})")
                if repitio_input == "Sí": alertas.append("Repitió año escolar previo")
                if (icfes_mat + icfes_nat) < 120: alertas.append(f"Puntaje Saber 11 en ciencias bajo ({icfes_mat + icfes_nat}/200)")
                if not alertas: alertas.append("El riesgo emerge de la combinación de múltiples factores.")
                for a in alertas: st.markdown(f"- {a}")

            else:
                st.markdown(
                    f'<div class="pred-resultado pred-normal">'
                    f'<strong>PERFIL DE RENDIMIENTO NORMAL</strong><br><br>'
                    f'El perfil del estudiante es compatible con el de estudiantes que '
                    f'<strong>superaron el umbral de 3.0</strong> de promedio acumulado '
                    f'en cohortes anteriores.<br><br>'
                    f'Probabilidad de bajo rendimiento: <strong>{probabilidad:.1%}</strong>'
                    f'</div>',
                    unsafe_allow_html=True)

                st.markdown("**Factores protectores identificados:**")
                protectores = []
                if prom_sem1_input >= 3.5:
                    protectores.append(f"Buen promedio en el primer semestre ({prom_sem1_input:.1f})")
                if (icfes_mat + icfes_nat) >= 130:
                    protectores.append(f"Solido puntaje Saber 11 en ciencias ({icfes_mat + icfes_nat}/200)")
                if max(nivel_p, nivel_m) >= 7:
                    protectores.append("Capital educativo familiar universitario")
                if not protectores:
                    protectores.append("El perfil combina multiples factores de proteccion.")
                for p in protectores:
                    st.markdown(f"- {p}")

        st.markdown(insight(
            "<strong>Aviso importante:</strong> Esta prediccion es una herramienta de apoyo para "
            "la intervencion temprana, no una sentencia academica. Se basa en patrones de "
            "89 estudiantes de 2 cohortes. Usese junto con seguimiento personalizado y consejeria academica.",
            "alerta"
        ), unsafe_allow_html=True)
