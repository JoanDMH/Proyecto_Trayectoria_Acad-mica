# Control de Correcciones y Pendientes (CRISP-DM)
**Proyecto Trayectoria Académica · Universidad de los Llanos · Ingeniería de Sistemas**

Este archivo contiene el estado actual de las correcciones técnicas aplicadas sobre el proyecto y detalla los pendientes e inconsistencias que restan entre la implementación real y los informes/guías documentados.

---

## ✅ Errores Corregidos (Estabilización y Lógica)

### 1. Fase 3: Exclusión de Estudiantes con Promedio Nulo
* **Problema:** Se incluían 5 estudiantes con promedio acumulado nulo (NaN) en la población base de modelado. Esto provocaba que Python los catalogara con `rendimiento_bajo = 0` (exitoso) y que su promedio de primer semestre se imputara artificialmente a `3.5`.
* **Solución:** Se modificó [preprocessing.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/src/preprocessing.py) para excluirlos de la población inicial (reduciendo la muestra a **89 estudiantes**). Se reentrenaron todos los modelos con esta muestra depurada, eliminando el sesgo en el predictor.

### 2. Fase 3: Código de Preprocesamiento Truncado
* **Problema:** El archivo [02_preprocessing.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/Fase%203/02_preprocessing.py) estaba físicamente cortado a la mitad (línea 208), impidiendo su ejecución e inspección completa.
* **Solución:** Se copió de forma íntegra la versión corregida y funcional al directorio de la Fase 3.

### 3. Fase 6: KeyError en la Sección Perfil Estudiantil (Streamlit)
* **Problema:** Al cargar el perfil, la app arrojaba `KeyError: 'TIPO_PLANTEL'` porque el pipeline del preprocesamiento eliminaba del CSV definitivo las columnas socioeconómicas originales en mayúsculas `'TIPO_PLANTEL'` y `'ZONA_LUGAR_RESIDENCIA'`.
* **Solución:** Se agregaron ambas columnas a la lista `info_cols` en [preprocessing.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/src/preprocessing.py), se regeneró el CSV y se resolvió la caída inicial del dashboard.

### 4. Fase 6: ValueError de Plotly en "Tipo de colegio y zona"
* **Problema:** Se arrojaba el error `ValueError: Value of 'color' is not the name of a column in 'data_frame'` al renderizar el gráfico. Al hacer `melt()` sobre la tabla cruzada (`crosstab`), pandas asignaba automáticamente el nombre del índice (`"Zona"`) como nombre de la columna derretida en lugar de `"variable"`.
* **Solución:** Se especificó explícitamente `var_name="Zona"` y `value_name="Estudiantes"` en el `melt()` de [app.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/app.py) y se adaptaron las variables del gráfico.

### 5. Fase 6: KeyError en Pruebas Estadísticas (Streamlit)
* **Problema:** Al cambiar de pestaña en "Factores Predictivos", la app se caía por un KeyError. Buscaba llaves como `p` o `mediana_M` en `pruebas_estadisticas.pkl`, pero el entrenamiento guardaba el diccionario con llaves como `p_value` o `media_M`.
* **Solución:** Se modificó [models.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/src/models.py) para que guarde un set de llaves compatibles y redundantes, estabilizando la navegación de la app.

### 6. Fase 6: Gráficos de Importancia de Variables Vacíos
* **Problema:** Los gráficos de importancia de características aparecían vacíos porque la app buscaba las llaves `imp_rb` e `imp_gr` en un diccionario consolidado que no se estaba guardando en el script.
* **Solución:** Se modificó el guardado en [models.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/src/models.py) para exportar el diccionario estructurado con las llaves de importancia bajo el nombre de `resultados_completos.pkl`.

### 7. Fase 6: Crash de Dimensiones en el Predictor Interactivo
* **Problema:** La UI recogía 18 variables y las pasaba a `.predict()`, pero el modelo de XGBoost fue entrenado con un vector de 9 variables, lo que causaba un crash de dimensiones en la predicción.
* **Solución:** Se modificó [app.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/app.py) para que filtre y mapee dinámicamente el vector del formulario según los nombres de características del modelo presentes en `feature_names.pkl`.

### 8. Fase 2: Análisis Exploratorio Limitado (Notebook e Informes)
* **Problema:** El notebook [05_eda_notebook.ipynb](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/Fase%202/05_eda_notebook.ipynb) y los reportes [02_descripcion_datos.md](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/Fase%202/02_descripcion_datos.md) y [04_hallazgos_eda.md](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/Fase%202/04_hallazgos_eda.md) describían y analizaban únicamente a la cohorte **2017-2** ($N=46$).
* **Solución:** Se actualizaron todos los archivos de la Fase 2 para integrar de manera formal los datos de la cohorte **2018-1** ($N=43$), describiendo y analizando la población combinada de **89 estudiantes**. Se ejecutó nbconvert de principio a fin de forma estable.

### 9. Fase 4: Sincronización de Informes de Modelado y SMOTE
* **Problema:** Los archivos [02_informe_modelado.md](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/Fase%204/02_informe_modelado.md), [03_hiperparametros_seleccion.md](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/Fase%204/03_hiperparametros_seleccion.md) y [04_metricas_evaluacion.md](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/Fase%204/04_metricas_evaluacion.md) se basaban en la muestra antigua de 94 estudiantes y describían el uso de SMOTE sobre un desbalanceo inexistente en la población final.
* **Solución:** Se reescribieron los tres informes para alinearlos formalmente con la población real de **89 estudiantes** y el entrenamiento con **18 características** (incluyendo `prom_sem1` en concordancia con el predictor de Streamlit). Se documentó que el desbalanceo no requirió SMOTE al superar el ratio de balanceo el umbral mínimo (ratio > 0.60 para ambas targets).

### 10. Fase 5: Métricas del Informe de Evaluación y Gráficos Físicos
* **Problema:** El informe [01_informe_evaluacion.md](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/Fase%205/01_informe_evaluacion.md) tenía métricas antiguas y desalineadas, y las imágenes físicas (`fig1_matrices_confusion.png` y `fig2_curvas_roc_pr.png`) no existían en el directorio de la Fase 5.
* **Solución:** Se creó [save_evaluation_plots.py](file:///c:/Users/Admin/OneDrive/Escritorio/proyecto_rendimiento_academico/src/save_evaluation_plots.py) para evaluar el clasificador en el conjunto de prueba (N=89) y guardar físicamente los tres archivos PNG en la carpeta de la Fase 5 y en `assets/`. Se actualizó el informe para reflejar las métricas honestas y reales resultantes tras la eliminación del data leakage.

---

## ⏳ Pendientes por Corregir (Discrepancias de Metodología y Reportes)

### 1. Fase 3: Integración de Variables del Plan de Negocios
* **Estado:** **Descartado por decisión del usuario.** Las variables actuales construidas son suficientes para los objetivos del negocio actuales.
