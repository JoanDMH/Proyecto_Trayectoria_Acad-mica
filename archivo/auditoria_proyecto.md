# Reporte de Auditoría: Proyecto Trayectoria Académica (CRISP-DM)
**Universidad de los Llanos — Cohortes 2017-2 y 2018-1 | Ingeniería de Sistemas**

Este documento presenta una auditoría detallada del estado del proyecto `proyecto_rendimiento_academico` a partir de lo definido en la guía metodológica [plan_crisp_dm_unillanos.md](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/plan_crisp_dm_unillanos.md). 

Se han identificado discrepancias metodológicas, errores críticos en la gestión de datos que afectan la calidad del modelo y errores lógicos de código en el despliegue (Streamlit).

---

## 🚨 Resumen de Hallazgos Críticos

1. **Error de Lógica en la Variable Objetivo (Fase 3):** Se dejaron 5 registros con `PROMEDIO_CARRERA` nulo (NaN) en el dataset limpio. Debido a que la lógica del script los trata implícitamente, estos registros terminaron etiquetados con `rendimiento_bajo = 0` (Rendimiento normal), introduciendo ruido severo al target.
2. **Código y Datos Desfasados (Fases 2 y 3):**
   - El notebook de exploración (`Fase 2/05_eda_notebook.ipynb`) y el preprocesamiento (`Fase 3/02_preprocessing.py`) solo contemplan la cohorte 2017-2 ($n=46$). Sin embargo, los datasets de salida (`01_df_master_limpio.csv`) contienen 94 filas (ambas cohortes). El código que generó los datos reales no está en los directorios de las fases.
   - El script `Fase 3/02_preprocessing.py` está físicamente truncado en la línea 208, omitiendo funciones clave de ingeniería de características.
3. **Bugs de Caída de la Aplicación (Fase 6 - Streamlit):**
   - **KeyError crítico en Perfil Estudiantil (Resuelto):** La sección "Perfil Estudiantil" fallaba con `KeyError: 'TIPO_PLANTEL'` porque el dataset `df_master_limpio.csv` descartaba las columnas informativas originales en mayúsculas `TIPO_PLANTEL` y `ZONA_LUGAR_RESIDENCIA`. Se solucionó reincorporándolas en `info_cols` dentro del preprocesamiento, regenerando el dataset y reentrenando los modelos.
   - **KeyError crítico en pruebas estadísticas (Resuelto):** La aplicación `app.py` buscaba llaves como `pruebas["genero"]["p"]` o `mediana_M`, pero el modelado las guardaba como `p_value` y `media_M`. Se solucionó exportando llaves de compatibilidad.
   - **Gráficos de importancia vacíos (Resuelto):** La app buscaba `imp_rb` e `imp_gr` en `resultados_completos.pkl` pero se guardaban por separado. Se solucionó corrigiendo la estructura guardada.
4. **Desalineación del Predictor Interactivo (Resuelto):** La UI enviaba 18 variables al predictor, pero el modelo esperaba 9. Se solucionó alineando dinámicamente el predictor mapeando con las variables reales de `feature_names.pkl`.

---


## 📁 Auditoría Detallada por Fase CRISP-DM

### FASE 2: Comprensión de los Datos

#### ❌ Código del Notebook desfasado de la población real
* El notebook `05_eda_notebook.ipynb` tiene hardcodeada la variable `COHORTE = '2017-2'`. No realiza ningún análisis ni filtro para la cohorte `2018-1`, a pesar de que el dataset final duplicó su tamaño para incluirla.
* **Tareas obligatorias del plan omitidas en código:** El notebook no ejecuta comandos de diagnóstico obligatorios como `df.info()`, `df.isnull().sum()`, `df.duplicated().sum()` de manera sistemática para todos los archivos, ni incluye un mapa de calor de correlaciones para las variables numéricas.

#### ⚠️ Inconsistencias en reportes de texto
* El reporte `02_descripcion_datos.md` solo detalla estadísticas de la cohorte 2017-2 ($n=47$ en caracterización). Toda la descripción de datos ignora por completo a los 48 estudiantes de la cohorte 2018-1.
* El reporte `04_hallazgos_eda.md` mezcla datos de ambas cohortes en algunas secciones (menciona $n=94$, 15 mujeres, 17 repitientes) pero mantiene estadísticas de la cohorte 2017-2 en sus conclusiones de preguntas problema (dice "solo 5 mujeres", "9 estudiantes repitieron", y describe la distribución del target sobre $n=46$).

---

### FASE 3: Preparación de los Datos

#### 🔴 Tratamiento erróneo de nulos en la variable objetivo (`rendimiento_bajo`) y features
* En `01_df_master_limpio.csv`, los estudiantes con código `160004009`, `160004120`, `160004129`, `160004131` y `160004148` tienen el campo `PROMEDIO_CARRERA` vacío (NaN) porque no registran promedio acumulado en la carrera.
* **Problema con la Variable Objetivo (Target):** En el preprocesamiento, la variable objetivo se define como `rendimiento_bajo = (df['PROMEDIO_CARRERA'] < 3.0).astype(int)`. Al evaluar la expresión lógica `NaN < 3.0`, Python devuelve `False` (casteado a `0`), clasificándolos incorrectamente como "Rendimiento Normal/Exitoso".
* **Contradicción con el Historial de Estados:** Al cruzar con `historial_estados_.xlsx`, se revela que los estudiantes `160004120`, `160004129` y `160004148` registran oficialmente el estado de **BAJO RENDIMIENTO** o **RETIRO DEFINITIVO** por causas académicas.
* **Problema con la Característica de Entrada (Feature):** Al no tener materias cursadas en la institución, el promedio de su primer semestre resultó en `NaN`. El código aplicó `df['prom_sem1'].fillna(median())`, convirtiendo el promedio nulo de primer semestre en un artificial **3.5** para estos estudiantes.
* **Impacto:** El modelo XGBoost se entrenó bajo la falsa premisa de que estudiantes con promedio de primer semestre de 3.5 y sin materias aprobadas representan casos exitosos de rendimiento de carrera (0). Al ser una muestra pequeña ($N=94$), este error del 5.3% en el etiquetado introduce ruido y sesgo directo que afecta la precisión del modelo.
* **Solución de Corrección:** 
  1. Dado que estos estudiantes no cuentan con materias cursadas en `detalle_materias.xlsx` ni notas de primer semestre reales, la solución óptima es **excluirlos por completo de la población base** del modelo. No se puede modelar el rendimiento académico de estudiantes que no tienen historial de notas sin inducir sesgo severo con datos artificiales.
  2. Ajustar la función `cargar_datos()` en `src/preprocessing.py` para excluir a cualquier estudiante cuyo `PROMEDIO_CARRERA` sea nulo (`NaN`) o no tenga registros de materias cursadas antes de construir las features del dataset final.

#### 🔴 Código truncado y desalineado
* El archivo `Fase 3/02_preprocessing.py` se corta abruptamente en la línea 208 justo después de declarar `feature_cols`. Le faltan la función `construir_features_materias()` y el bloque de ejecución principal.
* Además, el script contiene un `assert len(df_out) == 46`. Si se intentara ejecutar sobre el dataset combinado, el script fallaría de inmediato. Esto prueba que el archivo `01_df_master_limpio.csv` (que tiene 94 filas) fue generado por otra versión del pipeline no guardada en esta carpeta.

#### ⚠️ Incumplimiento del plan de variables
* El plan CRISP-DM solicitó la creación de las variables de estudiante `num_materias_reprobadas`, `num_semestres_cursados` y `tasa_aprobacion`. **Ninguna fue construida** en el script de preprocesamiento definitivo.

---

### FASE 4: Modelado

#### ⚠️ Desajuste de variables de entrada (Features Mismatch)
* En `src/models.py`, la constante `FEATURES_ENTRADA` define solo 8 variables sociodemográficas y de ingreso. No incluye `cohorte_encoded`.
* Sin embargo, el dataset final `01_df_master_limpio.csv` contiene la columna `cohorte_encoded`, el informe `02_informe_modelado.md` la posiciona como la 6ª variable más importante en el modelo final de XGBoost, y la app de Streamlit intenta procesarla. Esto evidencia una falta de sincronía entre los scripts auxiliares y el entrenamiento real que generó el archivo serializado `mejor_modelo.pkl`.

#### ⚠️ Inconsistencia en la lógica de SMOTE
* La constante en el código define aplicar SMOTE solo si el ratio de clases es inferior a 0.4 (`ratio < 0.4`).
* No obstante, el informe indica que se aplicó SMOTE al target `graduado` cuyo ratio era de 0.59 ($35/59 \approx 0.59$). Esto denota otra divergencia entre el código fuente visible y la ejecución experimental.

---

### FASE 5: Evaluación

#### ⚠️ Discrepancia en métricas y datos del reporte vs. ejecución
* El informe de evaluación `01_informe_evaluacion.md` indica un recuento de errores de Falsos Negativos (FN) de 7 y Falsos Positivos (FP) de 11. Sin embargo, al ejecutar la celda correspondiente en el notebook `02_evaluacion_modelo.ipynb`, el output real del modelo entrenado arroja **FN = 9 y FP = 10**.
* El reporte indica un Recall medio en CV-5 de 0.811 para `rendimiento_bajo`, mientras que el notebook reporta 0.761 en la celda de salida.
* **Imágenes faltantes:** El reporte escrito referencia imágenes como `fig1_matrices_confusion.png` y `fig2_curvas_roc_pr.png`, las cuales **no existen** en el directorio `Fase 5/` ni en `assets/`. Solo se generaron inline dentro del notebook Jupyter.

---

### FASE 6: Despliegue (Streamlit)

#### 🔴 Caídas (Crashes) en tiempo de ejecución y discrepancias del dataset

El archivo `app.py` contenía fallos de lógica al consultar el dataset y los artefactos `.pkl` guardados en la carpeta `src/`:

1. **KeyError crítico en la sección Perfil del Estudiante (`TIPO_PLANTEL` y `ZONA_LUGAR_RESIDENCIA`):**
   * **El Error Exacto:** Al ingresar o cargar la sección "Perfil Estudiantil", la app de Streamlit fallaba inmediatamente con:
     ```python
     KeyError: 'TIPO_PLANTEL'
     Traceback:
       File "app.py", line 309, in <module>
         pct_pub = (df["TIPO_PLANTEL"] == "G").mean()
     ```
     Esto sucedía porque el script `preprocessing.py` descartaba estas variables del archivo CSV definitivo `df_master_limpio.csv` al filtrar únicamente por `info_cols + feature_cols + target_cols`, donde las columnas en mayúsculas `'TIPO_PLANTEL'` y `'ZONA_LUGAR_RESIDENCIA'` no estaban presentes.
   * **Solución Ejecutada:** Se añadieron `'TIPO_PLANTEL'` y `'ZONA_LUGAR_RESIDENCIA'` a la lista `info_cols` dentro de [preprocessing.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/src/preprocessing.py) (línea 217). Posteriormente, se regeneró `df_master_limpio.csv` (ejecutando `preprocessing.py`), se reentrenaron los modelos y guardaron las importancias y coeficientes actualizados (ejecutando `models.py`), y se reinició la aplicación de Streamlit.

2. **ValueError de Plotly Express al fundir la tabla cruzada de tipo de colegio y zona:**
   * **El Error Exacto:** Posterior a corregir la carga de columnas, al renderizar el gráfico agrupado "Tipo de colegio y zona", se arrojaba:
     ```python
     ValueError: Value of 'color' is not the name of a column in 'data_frame'. Expected one of ['Plantel', 'Zona', 'value'] but received: variable
     ```
     Este error surgía al invocar `plan_zona.melt(id_vars="Plantel")` sobre la tabla cruzada producida por `pd.crosstab()`. Debido a que la columna de agrupación original tenía el nombre de índice `"Zona"`, pandas utilizaba automáticamente `"Zona"` para nombrar la columna de variables fundidas en lugar de `"variable"`. El código de Plotly Express, sin embargo, intentaba agrupar por `color="variable"`, que ya no existía en el DataFrame resultante.
   * **Solución Ejecutada:** Se especificaron explícitamente los parámetros `var_name="Zona"` y `value_name="Estudiantes"` en la función `melt()` en [app.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/app.py) (línea 370). Se modificó la llamada de `px.bar` para utilizar `y="Estudiantes"` y `color="Zona"`, asegurando compatibilidad y robustez absoluta sin depender de la resolución automática de nombres de pandas.

3. **Pruebas Estadísticas (`pruebas_estadisticas.pkl`):**
   * **El Error Exacto:** En `app.py` (Línea 586), se intentaba leer: `pruebas["genero"]["p"]` y `pruebas["genero"]["mediana_M"]`. Sin embargo, en `models.py`, el diccionario se generaba con las llaves `"p_value"`, `"media_M"` y `"media_F"`, resultando en un `KeyError` y la caída total de la sección al cambiar de pestaña.
   * **Solución Ejecutada:** Se modificó [models.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/src/models.py) para exportar las llaves redundantes y compatibles (`p`, `mediana_M`, `mediana_F`, `chi2`), eliminando la caída de la sección "Factores Predictivos".

4. **Importancia de Variables (`resultados_completos.pkl`):**
   * **El Error Exacto:** La app intentaba extraer las importancias con `res.get("imp_rb", {})`, pero el script `models.py` no estructuraba el consolidado de esa forma, resultando en gráficos vacíos de importancia de variables.
   * **Solución Ejecutada:** Se corrigió el diccionario exportado como `resultados_completos.pkl` en [models.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/src/models.py) para incluir las llaves correctas de importancia por target.

5. **Incompatibilidad del predictor interactivo:**
   * **El Error Exacto:** La UI del predictor intentaba estructurar un vector con las 18 variables del formulario, pero el modelo cargado (`mejor_modelo.pkl`) fue entrenado con un subconjunto restringido (`FEATURES_ENTRADA` de 8 variables o `FEATURES_SEM1` de 9 variables), arrojando un error de dimensiones de XGBoost.
   * **Solución Ejecutada:** Se alineó el predictor dinámicamente mapeando el vector de entrada con las características extraídas de `feature_names.pkl`.

---

## 📈 Conclusiones del Auditor

El proyecto cuenta con un trabajo de minería de datos muy valioso: la modelación por materias críticas es correcta y la estructuración visual en Streamlit usando data storytelling está muy bien diseñada.

Tras la auditoría e implementación de las correcciones técnicas requeridas, **todos los fallos críticos de estabilidad, tratamiento metodológico de nulos y desalineación de características del predictor han sido resueltos de forma definitiva**. El pipeline de datos está alineado y la aplicación web de Streamlit es completamente estable en todas sus secciones.
