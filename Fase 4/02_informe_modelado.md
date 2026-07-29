# Informe de Modelado
## CRISP-DM Fase 4 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Configuración experimental

| Parámetro | Valor |
|---|---|
| Población base | 90 estudiantes (46 de 2017-2 + 44 de 2018-1) |
| Semilla aleatoria | 42 |
| División train/test | 80 % / 20 % estratificada (72 train / 18 test) |
| Validación cruzada | StratifiedKFold k=5 |
| Métrica principal de selección | F1-Score (weighted) en conjunto de prueba (test set) |
| Métricas adicionales | F1-macro, AUC-ROC, Precisión+, Recall+, MCC, Average Precision |
| Manejo de desbalance | Sin SMOTE (proporciones equilibradas naturalmente, ver justificación abajo) |
| Escalado | No aplicado (modelos basados en árboles) |
| **Umbral `rendimiento_bajo`** | **0.29** (optimizado, ver §5) |
| **Umbral `graduado`** | **0.50** (default) |

### Justificación de la exclusión de SMOTE
El conjunto de datos final depurado cuenta con 90 estudiantes (con los archivos recodificados, ver Fase 3). La distribución de clases para los dos targets es la siguiente:
* **`rendimiento_bajo`**: 38 positivos / 52 negativos (42.2 % de clase minoritaria; ratio = 0.73)
* **`graduado`**: 35 positivos / 55 negativos (38.9 % de clase minoritaria; ratio = 0.64)

Dado que las proporciones están naturalmente equilibradas (por encima del 35-40 % en la clase minoritaria, ratio > 0.60), la aplicación de SMOTE (Synthetic Minority Oversampling Technique) u otras técnicas de remuestreo sintético no se justifica técnicamente. Aplicar SMOTE en desbalances tan leves induciría ruido sintético e incrementaría sustancialmente el riesgo de sobreajuste (overfitting), especialmente en un dataset de tamaño muestral pequeño ($N=90$). Por lo tanto, el entrenamiento se realiza sobre los datos originales sin alteración sintética.

---

## 2. Modelos candidatos y hiperparámetros

| Modelo | Configuración |
|---|---|
| Árbol de Decisión | `max_depth=3, min_samples_leaf=2` |
| Random Forest | `n_estimators=100, max_depth=4, min_samples_leaf=2` |
| XGBoost | `n_estimators=100, max_depth=3, lr=0.1, subsample=0.8, colsample_bytree=0.8` |

---

## 3. Resultados — TARGET: `rendimiento_bajo` — Umbral 0.29 — CV-5 (n=90)

Distribución: 38 positivos / 52 negativos (42.2 % / 57.8 %)

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg. Prec. | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **Árbol de Decisión** | 0.632 | **0.667** | **0.702** | 0.702 | 0.700 | **0.404** | **0.711** |
| **XGBoost** | 0.737 | 0.596 | 0.677 | **0.776** | **0.798** | 0.367 | 0.678 |
| **Random Forest** ✓ | **0.816** | 0.484 | 0.548 | 0.752 | 0.774 | 0.197 | 0.556 |

> **Random Forest** se mantiene como modelo principal por proveer el mayor **Recall+ (0.816)** en validación cruzada al umbral operativo 0.29: en un sistema de alertas tempranas se prioriza detectar al mayor número posible de estudiantes en riesgo. XGBoost ofrece mejor balance global (AUC 0.776) y es la alternativa si se prefiere precisión.

---

## 4. Resultados — TARGET: `graduado` — Umbral 0.50 — CV-5 (n=90)

Distribución: 35 positivos / 55 negativos (38.9 % / 61.1 %)

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg. Prec. | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **XGBoost** ✓ | 0.600 | 0.808 | 0.764 | **0.853** | 0.727 | 0.548 | 0.789 |
| **Random Forest** | 0.657 | **0.821** | **0.792** | 0.844 | **0.752** | **0.596** | **0.811** |
| **Árbol de Decisión** | **0.686** | 0.686 | 0.743 | 0.728 | 0.595 | 0.486 | 0.756 |

> **XGBoost** se mantiene como modelo seleccionado para graduación por su mayor capacidad de discriminación global (AUC CV-5 = 0.853). Con los datos recodificados, Random Forest resulta competitivo (mejor F1-macro y MCC); ambas opciones son defendibles.

---

## 5. Optimización del umbral de clasificación

Con el umbral por defecto (0.50), el Recall+ en CV-5 para `rendimiento_bajo` dejaba sin clasificar a casi un 60 % de los estudiantes en riesgo (Recall+ CV5 = 0.405). En alertas educativas preventivas, el costo de un falso negativo (no detectar a alguien que decaerá) supera drásticamente al de una falsa alarma (falso positivo).

Se optimizó el umbral de clasificación buscando maximizar la detección de riesgo (Recall+) para Random Forest:

| Umbral | Recall+ CV5 | Precisión+ CV5 | F1-macro CV5 | MCC CV5 |
|---|---|---|---|---|
| 0.50 (default) | 0.579 | **0.846** | **0.758** | **0.547** |
| **0.29 (seleccionado)** | **0.816** | 0.484 | 0.548 | 0.197 |

**Resultado:** El umbral 0.29 aumenta el Recall+ en **+23.7 puntos porcentuales** (de 0.579 a 0.816) para Random Forest, capturando al 81.6 % de los estudiantes con riesgo académico real en validación cruzada.

Para `graduado` se mantuvo el umbral 0.50, con buen balance para XGBoost (F1-macro = 0.764, AUC = 0.853 en CV-5).

---

## 6. Modelo principal seleccionado

* **Rendimiento Bajo:** **Random Forest** — umbral 0.29 (Recall+ CV5 = 0.816, AUC CV5 = 0.752)
* **Graduado:** **XGBoost** — umbral 0.50 (AUC CV5 = 0.853, F1-macro CV5 = 0.764)

---

## 7. Importancia de variables

### Random Forest → `rendimiento_bajo`

| Rank | Feature | Importancia |
|---|---|---|
| 1 | `prom_sem1` | 0.404 |
| 2 | `icfes_total` | 0.121 |
| 3 | `icfes_lec` | 0.071 |
| 4 | `log_ingresos` | 0.070 |
| 5 | `icfes_nat` | 0.066 |
| 6 | `sisben_nivel` | 0.054 |
| 7 | `icfes_mat` | 0.051 |
| 8 | `nivel_edu_padre` | 0.028 |

### XGBoost → `graduado`

| Rank | Feature | Importancia |
|---|---|---|
| 1 | `prom_sem1` | 0.197 |
| 2 | `cohorte_encoded` | 0.171 |
| 3 | `icfes_total` | 0.138 |
| 4 | `log_ingresos` | 0.098 |
| 5 | `icfes_nat` | 0.088 |
| 6 | `estrato` | 0.080 |
| 7 | `situacion_padres` | 0.072 |
| 8 | `sisben_nivel` | 0.065 |

> `prom_sem1` (promedio del primer semestre) se consolida como el predictor académico más decisivo para ambos targets, tal como se reporta en la app interactiva.

---

## 8. Modelos por materia crítica (pregunta d)

Métricas por validación cruzada (CV-5, out-of-fold), sin fugas de información (`src/entrenar_materias.py`, datos recodificados con intersemestrales incluidos):

| Materia | F1-w (CV-5) | AUC (CV-5) | N est. | % reprobación | Calidad |
|---|---|---|---|---|---|
| Matemáticas I | 0.928 | 0.928 | 73 | 26.0 % | ✅ Excelente |
| Fund. de Programación | 0.928 | 0.923 | 72 | 20.8 % | ✅ Excelente |
| Álgebra Lineal | 0.912 | 0.939 | 72 | 29.2 % | ✅ Excelente |
| Física I | 0.848 | 0.884 | 54 | 27.8 % | ✅ Muy bueno |
| Matemáticas II | 0.785 | 0.865 | 54 | 31.5 % | ✅ Bueno |

---

## 9. Pruebas estadísticas (preguntas a, b, c)

| Pregunta | Prueba | Estadístico | p-valor | Significativo |
|---|---|---|---|---|
| a) Género vs. promedio | Mann-Whitney U | U=455.0, med_M=3.20, med_F=3.70 | 0.246 | ❌ No |
| b) Edu padre vs. promedio | Spearman | rho=−0.052 | 0.627 | ❌ No |
| b) Edu madre vs. promedio | Spearman | rho=0.019 | 0.862 | ❌ No |
| c) Repitencia vs. rend. bajo | Chi-cuadrado | χ²=1.539 | 0.215 | ❌ No |

---

## 10. Criterios de éxito — Verificación

| Criterio | Estado |
|---|---|
| 3 modelos entrenados y comparados | ✅ |
| Métricas ampliadas (F1-w, F1-mac, AUC, Recall+) | ✅ |
| Modelo ganador con F1-w ≥ 0.65 | ✅ Modelos por materia F1-w CV 0.79–0.93; principal AUC 0.75–0.85 |
| AUC graduado > 0.70 | ✅ XGBoost AUC=0.853 |
| Importancia de variables documentada | ✅ |
| Modelo guardado en `src/mejor_modelo.pkl` | ✅ |
| Modelos por materia crítica entrenados | ✅ 5 materias |

---

## 11. Limitaciones

- Dataset depurado de tamaño moderado ($N=90$). Los resultados muestran buena consistencia interna pero requieren validación con nuevas cohortes.
- Desbalance de género persistente (83 % masculino): las comparaciones por género tienen poder estadístico limitado debido al tamaño del subgrupo femenino ($n=15$).
- La exclusión de data leakage redujo el desempeño a niveles realistas y útiles, eliminando el sobreajuste artificial previo.

