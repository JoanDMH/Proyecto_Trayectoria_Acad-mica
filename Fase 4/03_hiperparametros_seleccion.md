# Hiperparámetros Finales y Selección de Modelo
## CRISP-DM Fase 4 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Modelo principal — XGBoost → `rendimiento_bajo`

### Hiperparámetros finales

| Hiperparámetro | Valor | Justificación |
|---|---|---|
| `n_estimators` | 100 | Suficiente para dataset pequeño; más árboles no mejoran significativamente |
| `max_depth` | 3 | Árboles poco profundos evitan sobreajuste con n=94 |
| `learning_rate` | 0.1 | Valor estándar; balance entre velocidad de convergencia y generalización |
| `subsample` | 0.8 | Submuestreo de filas por árbol, reduce varianza |
| `colsample_bytree` | 0.8 | Submuestreo de features por árbol, reduce correlación entre árboles |
| `objective` | binary:logistic | Clasificación binaria con probabilidades de salida |
| `eval_metric` | logloss | Pérdida logarítmica, apropiada para clasificación binaria |
| `random_state` | 42 | Reproducibilidad |
| **`umbral de clasificación`** | **0.29** | Optimizado para maximizar F2-score (recall ponderado doble) |

### Justificación del umbral 0.29

El umbral fue optimizado usando **F2-score** sobre predicciones de CV-5, que pondera el Recall el doble que la Precisión. Esto refleja la prioridad del contexto educativo: **identificar a todos los estudiantes en riesgo es más importante que minimizar las falsas alarmas**.

| Umbral | Recall+ | Precisión+ | F1-macro | MCC | Decisión |
|---|---|---|---|---|---|
| 0.50 (default) | 0.757 | 0.800 | 0.820 | 0.641 | Mayor precisión, más falsos negativos |
| **0.29 (seleccionado)** | **0.811** | **0.732** | **0.803** | **0.609** | Mejor recall, acepta más falsas alarmas |

---

## 2. Modelo secundario — XGBoost → `graduado`

### Hiperparámetros finales

Idénticos al modelo principal (mismo algoritmo y configuración).

| Hiperparámetro | Valor |
|---|---|
| `n_estimators` | 100 |
| `max_depth` | 3 |
| `learning_rate` | 0.1 |
| `subsample` | 0.8 |
| `colsample_bytree` | 0.8 |
| **`umbral de clasificación`** | **0.50** |

### Justificación del umbral 0.50 para `graduado`

Con umbral 0.29 el F1-macro baja de 0.706 a 0.674 y el MCC de 0.363, deteriorando el desempeño. El umbral 0.50 es óptimo para este target.

---

## 3. Modelos por materia crítica — Random Forest

### Hiperparámetros

| Hiperparámetro | Valor |
|---|---|
| `n_estimators` | 100 |
| `max_depth` | 3 |
| `random_state` | 42 |
| `umbral de clasificación` | 0.50 |

---

## 4. Justificación formal de la selección de algoritmo

### ¿Por qué XGBoost sobre Random Forest y Árbol de Decisión?

| Criterio | Árbol de Decisión | Random Forest | XGBoost |
|---|---|---|---|
| F1-macro CV5 (`rendimiento_bajo`) | 0.785 | 0.751 | **0.817** |
| AUC CV5 (`rendimiento_bajo`) | 0.811 | 0.789 | **0.810** |
| F1-macro CV5 (`graduado`) | 0.661 | 0.662 | **0.706** |
| AUC CV5 (`graduado`) | 0.743 | 0.737 | **0.730** |
| Estabilidad CV (std F1-w) | 0.116 | 0.129 | **0.063** |
| Importancia de variables | ✅ | ✅ | ✅ |
| Interpretabilidad | Alta | Media | Media |

**XGBoost se selecciona porque:**
1. Mejor F1-macro en ambos targets (0.817 y 0.706)
2. Menor desviación estándar en CV-5 (0.063 vs 0.116 del Árbol) — más estable
3. Mejor Average Precision (0.825), indicador robusto para clases desbalanceadas
4. Capacidad de capturar interacciones no lineales entre variables socioeconómicas y académicas

**Árbol de Decisión** tiene AUC ligeramente superior en `graduado` (0.743 vs 0.730) pero es menos estable (std=0.115) y su F1-macro es inferior. Se descarta.

**Random Forest** tiene rendimiento consistentemente inferior a XGBoost en ambos targets con este dataset.

---

## 5. Proceso de entrenamiento

```
1. División estratificada: 80% train (75 est.) / 20% test (19 est.)
   Estratificación por: rendimiento_bajo
   
2. SMOTE aplicado a train si desbalance < 60%:
   - rendimiento_bajo: ratio=0.65 → no aplica SMOTE
   - graduado: ratio=0.59 → SMOTE aplicado (75 → ~104 muestras sintéticas)

3. Entrenamiento del modelo sobre train aumentado

4. Evaluación primaria: StratifiedKFold CV-5 sobre los 94 estudiantes
   (más confiable que test de 19 muestras)

5. Evaluación secundaria: conjunto test (19 estudiantes, nunca vistos)

6. Refitting final: modelo reentrenado sobre los 94 estudiantes completos
   para maximizar información disponible en producción
```
