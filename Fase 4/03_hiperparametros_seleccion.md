# Hiperparámetros Finales y Selección de Modelo
## CRISP-DM Fase 4 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Modelo principal — Random Forest → `rendimiento_bajo`

### Hiperparámetros finales

| Hiperparámetro | Valor | Justificación |
|---|---|---|
| `n_estimators` | 100 | Suficiente para robustez en dataset pequeño; evita alta varianza |
| `max_depth` | 4 | Árboles poco profundos evitan sobreajuste con n=89 |
| `min_samples_leaf` | 2 | Regularización para generalizar mejor en hojas pequeñas |
| `random_state` | 42 | Reproducibilidad |
| **`umbral de clasificación`** | **0.29** | Optimizado para maximizar Recall+ en la detección de riesgo |

### Justificación del umbral 0.29

El umbral fue optimizado usando el criterio de negocio de priorizar la detección de riesgo (Recall+). Esto refleja que en educación, un falso negativo (estudiante en riesgo no detectado) es mucho más grave que una falsa alarma.

| Umbral | Recall+ CV5 | Precisión+ CV5 | F1-macro CV5 | MCC CV5 | Decisión |
|---|---|---|---|---|---|
| 0.50 (default) | 0.568 | **0.750** | **0.721** | **0.460** | Mayor precisión, pero deja escapar un 43.2 % de alumnos en riesgo |
| **0.29 (seleccionado)** | **0.811** | 0.545 | 0.640 | 0.335 | Recall incrementado a 81.1 %, óptimo para intervención temprana |

---

## 2. Modelo secundario — XGBoost → `graduado`

### Hiperparámetros finales

| Hiperparámetro | Valor | Justificación |
|---|---|---|
| `n_estimators` | 100 | Estándar para boosting en muestras pequeñas |
| `max_depth` | 3 | Profundidad baja para controlar sobreajuste en XGBoost |
| `learning_rate` | 0.1 | Tasa de aprendizaje moderada para convergencia estable |
| `subsample` | 0.8 | Controla la varianza submuestreando las filas |
| `colsample_bytree` | 0.8 | Controla la varianza submuestreando columnas |
| **`umbral de clasificación`** | **0.50** | Umbral óptimo para predecir graduación |

### Justificación del umbral 0.50 para `graduado`

Para la predicción de graduados, el umbral de 0.50 arrojó el mejor desempeño de clasificación en CV-5 (F1-macro = 0.807, AUC = 0.870) y test (F1-weighted = 0.781). Bajar el umbral degrada la precisión sin aportar ganancias significativas en recall.

---

## 3. Modelos por materia crítica — Random Forest

### Hiperparámetros

| Hiperparámetro | Valor | Justificación |
|---|---|---|
| `n_estimators` | 100 | Estándar para estabilidad |
| `max_depth` | 3 | Controla sobreajuste en predicciones específicas de materias |
| `random_state` | 42 | Reproducibilidad |
| `umbral de clasificación` | 0.50 | Default |

---

## 4. Justificación de la selección de algoritmo

### Comparativa de algoritmos en Validación Cruzada (CV-5, n=89)

#### Target: `rendimiento_bajo`

| Criterio | Árbol de Decisión | Random Forest | XGBoost |
|---|---|---|---|
| F1-macro CV5 | **0.738** | 0.640 | 0.682 |
| AUC CV5 | 0.736 | 0.775 | **0.785** |
| MCC CV5 | **0.481** | 0.335 | 0.371 |
| Acc CV5 | **0.742** | 0.640 | 0.685 |

**Random Forest** es seleccionado como el modelo final para producción. Aunque Árbol de Decisión y XGBoost muestran mejor F1-macro promedio en validación cruzada debido a su mayor precisión, Random Forest ofrece el Recall más alto (**0.811** con umbral 0.29) y, crucialmente, demuestra una capacidad de generalización superior en el conjunto de prueba independiente (F1-weighted de 0.605 vs. 0.505 de XGBoost y 0.451 de Árbol de Decisión), previniendo el sobreajuste.

#### Target: `graduado`

| Criterio | Árbol de Decisión | Random Forest | XGBoost |
|---|---|---|---|
| F1-macro CV5 | **0.819** | 0.734 | 0.807 |
| AUC CV5 | 0.879 | 0.836 | **0.870** |
| MCC CV5 | **0.669** | 0.496 | 0.618 |
| Acc CV5 | 0.820 | 0.764 | **0.820** |

**XGBoost** es el modelo seleccionado para el target de graduación por mostrar mayor estabilidad de generalización en el conjunto de prueba (F1-weighted de 0.78 vs 0.67 de RF).

---

## 5. Proceso de entrenamiento

```
1. División estratificada: 80% train (71 est.) / 20% test (18 est.)
   Estratificación por: rendimiento_bajo
   
2. Manejo de desbalance:
   - rendimiento_bajo: ratio = 0.71 (52 negativos, 37 positivos) → no requiere SMOTE.
   - graduado: ratio = 0.65 (54 negativos, 35 positivos) → no requiere SMOTE.
   
   *Justificación Técnica:* Las proporciones de la clase minoritaria (~41.6 % y ~39.3 % respectivamente) son estables y equilibradas (ratio > 0.60). En estas condiciones, la aplicación de SMOTE u otras técnicas de remuestreo sintético no está justificada y es desaconsejada. Su uso induciría ruido sintético e incrementaría significativamente el riesgo de sobreajuste (overfitting), particularmente dado el tamaño de muestra limitado ($N=89$). El entrenamiento se realiza sobre los datos reales para preservar la veracidad estadística de la muestra.

3. Entrenamiento del modelo sobre train

4. Evaluación por validación cruzada: StratifiedKFold CV-5 sobre los 89 estudiantes
   (indicador principal de estabilidad)

5. Evaluación secundaria: conjunto test (18 estudiantes, nunca vistos)

6. Refitting final: modelo entrenado sobre los 89 estudiantes completos
   para maximizar información disponible en producción
```
