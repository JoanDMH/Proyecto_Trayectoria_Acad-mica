# Plan CRISP-DM: Sistema Predictivo de Rendimiento Académico
## Universidad de los Llanos — Cohortes 2017-2 y 2018-1 | Ingeniería de Sistemas

> **Nota para el agente de código:** Este documento es la hoja de ruta completa del proyecto. Cada fase debe ejecutarse en orden. Al finalizar cada fase, el agente debe verificar explícitamente los criterios de éxito antes de avanzar a la siguiente.

---

## Estructura del proyecto

```
proyecto_rendimiento_academico/
│
├── Datos/
│   ├── caracterización.xlsx
│   ├── detalle_materias.xlsx
│   ├── historial_estados_.xlsx
│   ├── PROMEDIOS_DE_CARRERA.xlsx
│   └── promedios_semestre.xlsx
│
├── notebooks/
│   ├── 01_comprension_negocio.ipynb
│   ├── 02_comprension_datos.ipynb
│   ├── 03_preparacion_datos.ipynb
│   ├── 04_modelado.ipynb
│   └── 05_evaluacion.ipynb
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── models.py
│   ├── evaluation.py
│   └── storytelling_components.py
│
├── assets/
│   └── styles.css
│
├── app.py                  ← Aplicación Dash principal
├── requirements.txt
└── README.md
```

---

## FASE 1: Comprensión del Negocio

### 1.1 Contexto institucional

- **Cliente:** Universidad de los Llanos
- **Proyecto marco:** Estudio longitudinal de trayectoria estudiantil — Facultad de Ciencias Básicas e Ingeniería (dimensiones STEM)
- **Alcance:** Cohortes **2017-2 y 2018-1**, programa **Ingeniería de Sistemas**
- **Objetivo general:** Construir un modelo predictivo del rendimiento académico que permita anticipar el desempeño de un estudiante específico basándose en perfiles similares históricos

### 1.2 Objetivos del negocio → Objetivos de minería de datos

| Objetivo de negocio | Objetivo de minería de datos | Tipo de tarea |
|---|---|---|
| Detectar brechas de género en rendimiento | Clasificación / prueba de hipótesis inferencial | Inferencia + Clasificación |
| Evaluar el efecto del nivel educativo de los padres | Regresión / clasificación del rendimiento | Predicción |
| Determinar si la repitencia previa predice fracaso universitario | Clasificación binaria (aprueba/reprueba, gradúa/no gradúa) | Predicción |
| Identificar las 5 materias críticas y predecir reprobación | Ranking + clasificación binaria por materia | Clasificación |

### 1.3 Preguntas problema

> Las preguntas pueden ajustarse en la Fase 2 si el análisis exploratorio revela patrones más relevantes.

**a. Brecha de género**
- ¿Existe diferencia estadísticamente significativa en el promedio acumulado entre hombres y mujeres de las cohortes 2017-2 y 2018-1?
- ¿Es el género un predictor útil del rendimiento académico cuando se controlan otras variables socioeconómicas?

**b. Nivel educativo de los padres**
- ¿El nivel educativo del padre y/o la madre predice significativamente el promedio semestral o acumulado del estudiante?

**c. Repitencia previa**
- ¿Haber repetido algún grado escolar antes de ingresar a la universidad se asocia con mayor probabilidad de reprobar materias o abandonar el programa?

**d. Materias críticas**
- ¿Cuáles son las 5 materias con peor combinación de: bajo promedio + alta tasa de reprobación + alta repitencia?
- ¿Es posible predecir qué estudiante reprobará alguna de estas materias, usando sus notas previas en materias correlacionadas?

### 1.4 Criterio de éxito de la fase

- [x] Preguntas formuladas con componente de inferencia, predicción o clasificación
- [x] Alcance delimitado (cohortes 2017-2 y 2018-1, programa Ingeniería de Sistemas)
- [x] Fuentes de datos identificadas

---

## FASE 2: Comprensión de los Datos

### 2.1 Instrucciones al agente de código

```python
# Paso 1: Cargar todos los archivos y revisar su estructura
import pandas as pd

archivos = {
    "caracterizacion": "Datos/caracterización.xlsx",
    "detalle_materias": "Datos/detalle_materias.xlsx",
    "historial_estados": "Datos/historial_estados_.xlsx",
    "promedios_carrera": "Datos/PROMEDIOS_DE_CARRERA.xlsx",
    "promedios_semestre": "Datos/promedios_semestre.xlsx"
}

dataframes = {}
for nombre, ruta in archivos.items():
    df = pd.read_excel(ruta)
    dataframes[nombre] = df
    print(f"\n{'='*50}")
    print(f"Archivo: {nombre}")
    print(f"Dimensiones: {df.shape}")
    print(f"Columnas: {df.columns.tolist()}")
    print(df.dtypes)
    print(df.head(3))
```

### 2.2 Tareas de exploración obligatorias

Para **cada** DataFrame, el agente debe ejecutar y documentar:

1. **Dimensiones y tipos de datos**
   ```python
   df.info()
   df.describe(include='all')
   ```

2. **Valores faltantes**
   ```python
   df.isnull().sum()
   (df.isnull().sum() / len(df) * 100).round(2)
   ```

3. **Duplicados**
   ```python
   df.duplicated().sum()
   ```

4. **Distribuciones de variables numéricas** (histogramas con `plotly.express`)

5. **Frecuencias de variables categóricas** (barras con `plotly.express`)

6. **Filtrado por cohorte y programa**
   ```python
   # Identificar columnas de cohorte y programa en cada DataFrame
   # Filtrar: cohorte == '2017-2', programa == 'Ingeniería de Sistemas'
   # Documentar cuántos registros quedan por tabla
   ```

7. **Análisis de correlación** entre variables numéricas (heatmap)

8. **Identificar llaves/claves** para unir los DataFrames (ej: código estudiante)

### 2.3 Análisis exploratorio específico por pregunta

#### Pregunta a — Género y rendimiento
```python
# Comparar distribución de promedios por género
# Prueba estadística: Mann-Whitney U (si no hay normalidad) o t-test
from scipy import stats

hombres = df_filtrado[df_filtrado['genero'] == 'M']['promedio_acumulado']
mujeres = df_filtrado[df_filtrado['genero'] == 'F']['promedio_acumulado']
stat, p = stats.mannwhitneyu(hombres, mujeres)
print(f"p-value: {p}")  # Si p < 0.05: diferencia significativa
```

#### Pregunta b — Nivel educativo padres
```python
# Distribución del nivel educativo en la cohorte
# Boxplot: nivel educativo padre/madre vs. promedio acumulado
# Correlación de Spearman (variable ordinal)
```

#### Pregunta c — Repitencia previa
```python
# Proporción de estudiantes que repitieron vs. no repitieron
# Comparar tasa de reprobación universitaria entre ambos grupos
# Comparar estado final (activo, retirado, graduado) entre grupos
```

#### Pregunta d — Materias críticas
```python
# Por materia, calcular:
# - Promedio de notas
# - Tasa de reprobación (nota < 3.0 o según criterio institucional)
# - Número de veces que los mismos estudiantes repiten la materia
# Crear índice compuesto y rankear top 5 peores
```

### 2.4 Criterio de éxito de la fase

- [ ] Todos los DataFrames explorados con las métricas indicadas
- [ ] Datos filtrados correctamente por cohorte 2017-2 e Ingeniería de Sistemas
- [ ] Variables clave identificadas para cada pregunta
- [ ] Clave de unión entre tablas confirmada
- [ ] Informe de calidad de datos: % faltantes, duplicados, outliers
- [ ] Preguntas problema validadas o ajustadas según hallazgos

> **⚠️ PAUSA:** El agente no debe avanzar a la Fase 3 sin confirmar estos criterios.

---

## FASE 3: Preparación de los Datos

### 3.1 Integración de tablas

```python
# Unir todas las tablas por el código del estudiante
# Verificar que el join no infle ni pierda registros inesperadamente
df_master = (
    df_caracterizacion
    .merge(df_promedios_carrera, on='codigo_estudiante', how='left')
    .merge(df_promedios_semestre, on='codigo_estudiante', how='left')
    .merge(df_historial_estados, on='codigo_estudiante', how='left')
)
print(f"Registros en df_master: {df_master.shape[0]}")
```

### 3.2 Limpieza de datos

```python
# 1. Eliminar duplicados exactos
df_master = df_master.drop_duplicates()

# 2. Tratar valores faltantes
# - Variables numéricas: imputar con mediana (robusta a outliers)
# - Variables categóricas: imputar con moda o crear categoría 'Desconocido'
from sklearn.impute import SimpleImputer

# 3. Corregir tipos de datos (ej: fechas como string → datetime)
# 4. Estandarizar categorías (ej: 'M', 'Masculino', 'masculino' → 'M')
# 5. Detectar y tratar outliers (IQR o Z-score)
```

### 3.3 Ingeniería de características

Para cada pregunta se construyen features específicas:

**Features globales del estudiante (para preguntas a, b, c):**
```python
# - promedio_acumulado (ya existente o calculado)
# - num_materias_reprobadas
# - num_semestres_cursados
# - tasa_aprobacion = materias_aprobadas / materias_cursadas
# - genero (codificado: 0/1)
# - nivel_edu_padre (ordinal: 0=ninguno, 1=primaria, ..., 5=posgrado)
# - nivel_edu_madre (ídem)
# - repitio_escolar (binario: 0/1)
# - estado_final (target para gradúa: 0=no graduado, 1=graduado)
# - rendimiento_bajo (target para rendimiento: 0=normal, 1=bajo)
```

**Features por materia (para pregunta d):**
```python
# - promedio_materia_actual
# - promedio_materias_previas_correlacionadas
# - num_veces_cursada
# - semestre_en_que_la_cursa
# - target: reprobo_materia (0/1)
```

### 3.4 Codificación y escalado

```python
from sklearn.preprocessing import LabelEncoder, StandardScaler, OrdinalEncoder
from sklearn.pipeline import Pipeline

# Variables categóricas nominales: OneHotEncoder
# Variables ordinales: OrdinalEncoder con orden explícito
# Variables numéricas para modelos sensibles a escala: StandardScaler
# Nota: Árbol de decisión y Random Forest no requieren escalado,
#       pero se aplica de forma uniforme en el pipeline para consistencia
```

### 3.5 División train/test

```python
from sklearn.model_selection import train_test_split, StratifiedKFold

# Dado el tamaño pequeño de la cohorte, usar:
# - 80% train, 20% test
# - Stratify por la variable target
# - Validación cruzada estratificada k=5 en entrenamiento

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

### 3.6 Criterio de éxito de la fase

- [ ] `df_master` construido sin pérdida inesperada de registros
- [ ] Valores faltantes tratados (< 5% restante o justificado)
- [ ] Variables target definidas para cada pregunta
- [ ] Dataset listo para modelado con tipos correctos
- [ ] Sin data leakage (variables que "ven el futuro" excluidas del train)

> **⚠️ PAUSA:** Verificar criterios antes de pasar a modelado.

---

## FASE 4: Modelado

### 4.1 Configuración base

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    classification_report, confusion_matrix
)
import joblib

SEED = 42
CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
```

### 4.2 Modelos candidatos y sus hiperparámetros

#### Árbol de Decisión
```python
dt = DecisionTreeClassifier(random_state=SEED)
param_grid_dt = {
    'max_depth': [3, 5, 7, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'criterion': ['gini', 'entropy']
}
gs_dt = GridSearchCV(dt, param_grid_dt, cv=CV, scoring='f1_weighted', n_jobs=-1)
gs_dt.fit(X_train, y_train)
```

#### Random Forest
```python
rf = RandomForestClassifier(random_state=SEED)
param_grid_rf = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7, None],
    'min_samples_split': [2, 5],
    'max_features': ['sqrt', 'log2']
}
gs_rf = GridSearchCV(rf, param_grid_rf, cv=CV, scoring='f1_weighted', n_jobs=-1)
gs_rf.fit(X_train, y_train)
```

#### XGBoost
```python
xgb = XGBClassifier(random_state=SEED, eval_metric='logloss', use_label_encoder=False)
param_grid_xgb = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}
gs_xgb = GridSearchCV(xgb, param_grid_xgb, cv=CV, scoring='f1_weighted', n_jobs=-1)
gs_xgb.fit(X_train, y_train)
```

### 4.3 Evaluación y comparación

```python
modelos = {
    'Árbol de Decisión': gs_dt.best_estimator_,
    'Random Forest': gs_rf.best_estimator_,
    'XGBoost': gs_xgb.best_estimator_
}

resultados = []
for nombre, modelo in modelos.items():
    y_pred = modelo.predict(X_test)
    y_prob = modelo.predict_proba(X_test)[:, 1]
    resultados.append({
        'Modelo': nombre,
        'Accuracy': accuracy_score(y_test, y_pred),
        'F1-Score (weighted)': f1_score(y_test, y_pred, average='weighted'),
        'AUC-ROC': roc_auc_score(y_test, y_prob)
    })

df_resultados = pd.DataFrame(resultados).sort_values('F1-Score (weighted)', ascending=False)
print(df_resultados)

# El modelo ganador es el de mayor F1-Score ponderado
mejor_modelo = modelos[df_resultados.iloc[0]['Modelo']]
joblib.dump(mejor_modelo, 'src/mejor_modelo.pkl')
```

### 4.4 Importancia de variables

```python
import plotly.express as px

# Para el modelo ganador, extraer importancia de features
importancias = pd.Series(
    mejor_modelo.feature_importances_,
    index=X_train.columns
).sort_values(ascending=False)

fig = px.bar(importancias.head(15), orientation='h',
             title='Top 15 Variables más importantes')
fig.show()
```

### 4.5 Manejo del desbalance de clases

```python
# Si hay desbalance significativo en el target:
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=SEED)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)
# Reentrenar el modelo ganador con datos balanceados y comparar métricas
```

### 4.6 Criterio de éxito de la fase

- [ ] Los 3 modelos entrenados y optimizados con GridSearchCV
- [ ] Tabla comparativa de métricas generada
- [ ] Modelo ganador identificado con F1-Score ≥ 0.65 (mínimo aceptable para datos pequeños)
- [ ] Importancia de variables documentada
- [ ] Modelo guardado en disco (`mejor_modelo.pkl`)

> **⚠️ PAUSA:** Si ningún modelo supera el umbral mínimo, revisar Fase 3 (preparación de datos y features).

---

## FASE 5: Evaluación

### 5.1 Validación del modelo frente a los objetivos del negocio

```python
# Para cada pregunta problema, verificar que el modelo o análisis la responde:

# a. Género → ¿El modelo incluye género como variable? ¿Cuál es su importancia?
#             ¿El resultado del test estadístico (Mann-Whitney) fue significativo?

# b. Nivel educativo → ¿Las variables nivel_edu_padre/madre aparecen en el top de importancia?
#                      ¿La correlación de Spearman fue significativa?

# c. Repitencia → ¿repitio_escolar es un predictor relevante?
#                 ¿El modelo distingue correctamente entre grupos?

# d. Materias críticas → ¿Se identificaron las 5 materias? 
#                        ¿El sub-modelo por materia tiene AUC-ROC > 0.7?
```

### 5.2 Análisis de errores

```python
# Matriz de confusión del modelo ganador
import plotly.figure_factory as ff

cm = confusion_matrix(y_test, mejor_modelo.predict(X_test))
fig = ff.create_annotated_heatmap(
    cm, colorscale='Blues',
    x=['Pred. Negativo', 'Pred. Positivo'],
    y=['Real Negativo', 'Real Positivo']
)
fig.show()

# Curva ROC
from sklearn.metrics import RocCurveDisplay
RocCurveDisplay.from_estimator(mejor_modelo, X_test, y_test)
```

### 5.3 Criterio de éxito de la fase

- [ ] Las 4 preguntas problema respondidas con evidencia cuantitativa
- [ ] Modelo valida resultados coherentes con análisis exploratorio
- [ ] Falsos positivos y falsos negativos analizados y sus implicaciones explicadas
- [ ] Conclusiones documentadas para el storytelling del dashboard

> **⚠️ PAUSA:** Solo si todos los criterios están satisfechos, proceder al despliegue.

---

## FASE 6: Despliegue — Aplicación Dash

### 6.1 Arquitectura de la aplicación

La app tendrá **5 secciones narrativas** (data storytelling):

| Sección | Título narrativo | Contenido |
|---|---|---|
| 0 | Portada / Introducción | Contexto del proyecto, cohorte analizada |
| 1 | ¿Quiénes son los estudiantes? | Perfil sociodemográfico, distribución género, nivel educativo padres |
| 2 | ¿Cómo es su rendimiento? | Promedios, evolución semestral, comparativas |
| 3 | ¿Qué factores importan? | Resultados por pregunta a, b, c — brecha género, padres, repitencia |
| 4 | Las materias más difíciles | Ranking de materias críticas, análisis de repitencia |
| 5 | Predictor Interactivo | Formulario → predicción del modelo en tiempo real |

### 6.2 Estructura del archivo `app.py`

```python
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import joblib
import numpy as np

# --- Configuración ---
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    title="Rendimiento Académico — Unillanos 2017-2"
)
server = app.server

# --- Cargar datos y modelo ---
df_master = pd.read_csv('src/df_master_limpio.csv')       # generado en Fase 3
mejor_modelo = joblib.load('src/mejor_modelo.pkl')
feature_names = joblib.load('src/feature_names.pkl')

# --- Layout principal con Tabs ---
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H1("📊 Rendimiento Académico — Ingeniería de Sistemas",
                        className="text-primary mt-4"), width=10),
        dbc.Col(html.Img(src='/assets/logo_unillanos.png', height='60px',
                         className="mt-4"), width=2)
    ]),
    html.P("Cohorte 2017-2 | Estudio longitudinal trayectoria estudiantil STEM",
           className="text-muted"),
    html.Hr(),

    # Tabs de navegación
    dbc.Tabs([
        dbc.Tab(label="👥 Perfil estudiantil",    tab_id="tab-perfil"),
        dbc.Tab(label="📈 Rendimiento",           tab_id="tab-rendimiento"),
        dbc.Tab(label="🔍 Factores predictivos",  tab_id="tab-factores"),
        dbc.Tab(label="📚 Materias críticas",     tab_id="tab-materias"),
        dbc.Tab(label="🤖 Predictor",             tab_id="tab-predictor"),
    ], id="tabs", active_tab="tab-perfil"),

    html.Div(id="tab-content", className="mt-3"),

], fluid=True)
```

### 6.3 Sección: Perfil estudiantil (Tab 1)

```python
# Gráficos requeridos:
# 1. Pie chart: distribución por género
# 2. Bar chart: nivel educativo del padre (categorías)
# 3. Bar chart: nivel educativo de la madre
# 4. KPI cards: total estudiantes, % hombres, % mujeres, % con padres universitarios

layout_perfil = dbc.Container([
    html.H3("¿Quiénes son los estudiantes de la cohorte 2017-2?"),
    html.P("""En esta sección exploramos el perfil sociodemográfico de los 
             estudiantes que ingresaron al programa de Ingeniería de Sistemas 
             en el segundo semestre de 2017..."""),
    dbc.Row([
        dbc.Col(dcc.Graph(id='fig-genero'), width=4),
        dbc.Col(dcc.Graph(id='fig-edu-padre'), width=4),
        dbc.Col(dcc.Graph(id='fig-edu-madre'), width=4),
    ])
])
```

### 6.4 Sección: Predictor interactivo (Tab 5)

```python
# Formulario con los inputs del modelo
layout_predictor = dbc.Container([
    html.H3("🤖 Predictor de Rendimiento Académico"),
    html.P("""Complete el perfil del estudiante para obtener una predicción 
             sobre su rendimiento basada en patrones históricos de la cohorte."""),
    dbc.Row([
        dbc.Col([
            dbc.Label("Género"),
            dcc.Dropdown(['Masculino', 'Femenino'], id='input-genero'),

            dbc.Label("Nivel educativo del padre", className="mt-2"),
            dcc.Dropdown(['Ninguno', 'Primaria', 'Secundaria',
                          'Técnico', 'Universitario', 'Posgrado'],
                         id='input-edu-padre'),

            dbc.Label("Nivel educativo de la madre", className="mt-2"),
            dcc.Dropdown(['Ninguno', 'Primaria', 'Secundaria',
                          'Técnico', 'Universitario', 'Posgrado'],
                         id='input-edu-madre'),

            dbc.Label("¿Repitió algún grado escolar?", className="mt-2"),
            dcc.RadioItems(['Sí', 'No'], 'No', id='input-repitencia',
                           inline=True),

            dbc.Label("Promedio del 1er semestre", className="mt-2"),
            dcc.Slider(0, 5, 0.1, value=3.5, id='input-prom1',
                       marks={i: str(i) for i in range(6)}),

        ], width=6),
        dbc.Col([
            html.Div(id='output-prediccion', className="mt-4")
        ], width=6)
    ]),
    dbc.Button("Predecir", id='btn-predecir', color='primary',
               className='mt-3', n_clicks=0),
])

# Callback del predictor
@app.callback(
    Output('output-prediccion', 'children'),
    Input('btn-predecir', 'n_clicks'),
    State('input-genero', 'value'),
    State('input-edu-padre', 'value'),
    State('input-edu-madre', 'value'),
    State('input-repitencia', 'value'),
    State('input-prom1', 'value'),
    prevent_initial_call=True
)
def predecir(n, genero, edu_padre, edu_madre, repitencia, prom1):
    # Construir vector de features
    # Transformar inputs con el mismo pipeline de la Fase 3
    # Realizar predicción
    # Mostrar resultado con gauge chart y explicación narrativa
    pass
```

### 6.5 Requisitos de instalación (`requirements.txt`)

```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
imbalanced-learn>=0.11.0
plotly>=5.18.0
dash>=2.14.0
dash-bootstrap-components>=1.5.0
openpyxl>=3.1.0
joblib>=1.3.0
scipy>=1.11.0
```

### 6.6 Ejecución

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
# → Abrir http://127.0.0.1:8050/ en el navegador
```

### 6.7 Criterio de éxito de la fase

- [ ] App ejecuta sin errores en `localhost`
- [ ] Los 5 tabs cargan correctamente con sus gráficos
- [ ] El predictor devuelve una predicción coherente al ingresar datos
- [ ] Los gráficos tienen títulos, ejes y tooltips informativos
- [ ] El narrativo de data storytelling es coherente y explica los hallazgos

---

## Resumen de entregables

| Entregable | Descripción |
|---|---|
| `notebooks/` | 5 notebooks documentados, uno por fase CRISP-DM |
| `src/df_master_limpio.csv` | Dataset integrado y limpio |
| `src/mejor_modelo.pkl` | Modelo ganador serializado |
| `app.py` | Aplicación Dash completa |
| `assets/styles.css` | Estilos personalizados |
| `requirements.txt` | Dependencias del proyecto |
| Informe PDF (opcional) | Síntesis ejecutiva del análisis |

---

## Orden de ejecución para el agente de código

```
1. Leer y comprender este plan completo
2. Ejecutar Fase 2: exploración de datos → verificar criterios → documentar hallazgos
3. Ejecutar Fase 3: preparación → verificar criterios → guardar df_master
4. Ejecutar Fase 4: modelado → comparar modelos → guardar mejor_modelo.pkl
5. Ejecutar Fase 5: evaluación → responder preguntas problema → documentar
6. Ejecutar Fase 6: construir app.py con Dash → probar → ajustar narrativo
```

> **Regla general:** Si un criterio de éxito no se cumple, el agente debe depurar la fase actual antes de avanzar. Nunca saltar fases.

---

*Plan elaborado siguiendo la metodología CRISP-DM (Cross-Industry Standard Process for Data Mining). Versión 1.0 — Universidad de los Llanos, Facultad de Ciencias Básicas e Ingeniería.*
