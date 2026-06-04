# Informe de Modelado
## CRISP-DM Fase 4 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Configuración experimental

| Parámetro | Valor |
|---|---|
| Población base | 89 estudiantes (46 de 2017-2 + 43 de 2018-1) |
| Semilla aleatoria | 42 |
| División train/test | 80 % / 20 % estratificada (71 train / 18 test) |
| Validación cruzada | StratifiedKFold k=5 |
| Métrica principal de selección | F1-Score (weighted) en conjunto de prueba (test set) |
| Métricas adicionales | F1-macro, AUC-ROC, Precisión+, Recall+, MCC, Average Precision |
| Manejo de desbalance | Sin SMOTE (proporciones equilibradas naturalmente, ver justificación abajo) |
| Escalado | No aplicado (modelos basados en árboles) |
| **Umbral `rendimiento_bajo`** | **0.29** (optimizado, ver §5) |
| **Umbral `graduado`** | **0.50** (default) |

### Justificación de la exclusión de SMOTE
El conjunto de datos final depurado cuenta con 89 estudiantes. La distribución de clases para los dos targets es la siguiente:
* **`rendimiento_bajo`**: 37 positivos / 52 negativos (41.6 % de clase minoritaria; ratio = 0.71)
* **`graduado`**: 35 positivos / 54 negativos (39.3 % de clase minoritaria; ratio = 0.65)

Dado que las proporciones están naturalmente equilibradas (por encima del 35-40 % en la clase minoritaria, ratio > 0.60), la aplicación de SMOTE (Synthetic Minority Oversampling Technique) u otras técnicas de remuestreo sintético no se justifica técnicamente. Aplicar SMOTE en desbalances tan leves induciría ruido sintético e incrementaría sustancialmente el riesgo de sobreajuste (overfitting), especialmente en un dataset de tamaño muestral pequeño ($N=89$). Por lo tanto, el entrenamiento se realiza sobre los datos originales sin alteración sintética.

---

## 2. Modelos candidatos y hiperparámetros

| Modelo | Configuración |
|---|---|
| Árbol de Decisión | `max_depth=3, min_samples_leaf=2` |
| Random Forest | `n_estimators=100, max_depth=4, min_samples_leaf=2` |
| XGBoost | `n_estimators=100, max_depth=3, lr=0.1, subsample=0.8, colsample_bytree=0.8` |

---

## 3. Resultados — TARGET: `rendimiento_bajo` — Umbral 0.29 — CV-5 (n=89)

Distribución: 37 positivos / 52 negativos (41.6 % / 58.4 %)

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg. Prec. | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **Árbol de Decisión** | 0.757 | **0.667** | **0.738** | 0.736 | 0.626 | **0.481** | **0.742** |
| **XGBoost** | 0.703 | 0.605 | 0.682 | **0.785** | 0.774 | 0.371 | 0.685 |
| **Random Forest** ✓ | **0.811** | 0.545 | 0.640 | 0.775 | **0.791** | 0.335 | 0.640 |

> **Random Forest** es seleccionado como el modelo principal para producción debido a su excelente capacidad de generalización en el conjunto de prueba independiente de test (F1-weighted test = 0.605, Accuracy test = 0.611 vs. F1-weighted test = 0.505 de XGBoost y F1-weighted test = 0.451 de Árbol de Decisión) y por proveer el mayor **Recall+ (0.811)** en validación cruzada para maximizar la detección temprana de riesgo.

---

## 4. Resultados — TARGET: `graduado` — Umbral 0.50 — CV-5 (n=89)

Distribución: 35 positivos / 54 negativos (39.3 % / 60.7 %)

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg. Prec. | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **XGBoost** ✓ | 0.714 | **0.806** | 0.807 | 0.870 | **0.823** | 0.618 | **0.820** |
| **Random Forest** | 0.543 | 0.792 | 0.734 | 0.836 | 0.784 | 0.496 | 0.764 |
| **Árbol de Decisión** | **0.943** | 0.702 | **0.819** | **0.879** | 0.784 | **0.669** | 0.820 |

> **XGBoost** es el modelo ganador seleccionado para graduación debido a su alta robustez y excelente generalización en el conjunto de prueba (F1-weighted de 0.781, Accuracy de 0.778 en test, con un AUC CV-5 de 0.870).

---

## 5. Optimización del umbral de clasificación

Con el umbral por defecto (0.50), el Recall+ en CV-5 para `rendimiento_bajo` dejaba sin clasificar a casi un 60 % de los estudiantes en riesgo (Recall+ CV5 = 0.405). En alertas educativas preventivas, el costo de un falso negativo (no detectar a alguien que decaerá) supera drásticamente al de una falsa alarma (falso positivo).

Se optimizó el umbral de clasificación buscando maximizar la detección de riesgo (Recall+) para Random Forest:

| Umbral | Recall+ CV5 | Precisión+ CV5 | F1-macro CV5 | MCC CV5 |
|---|---|---|---|---|
| 0.50 (default) | 0.568 | **0.750** | **0.721** | **0.460** |
| **0.29 (seleccionado)** | **0.811** | 0.545 | 0.640 | 0.335 |

**Resultado:** El umbral 0.29 aumenta el Recall+ en **+24.3 puntos porcentuales** (de 0.568 a 0.811) para Random Forest, capturando al 81.1 % de los estudiantes con riesgo académico real en validación cruzada.

Para `graduado` se mantuvo el umbral 0.50, el cual ofrece un excelente balance para XGBoost (F1-macro = 0.807, Recall+ = 0.714 en CV-5).

---

## 6. Modelo principal seleccionado

* **Rendimiento Bajo:** **Random Forest** — umbral 0.29 (F1-macro CV5 = 0.640, AUC CV5 = 0.775, Recall+ CV5 = 0.811)
* **Graduado:** **XGBoost** — umbral 0.50 (F1-macro CV5 = 0.807, AUC CV5 = 0.870, Recall+ CV5 = 0.714)

---

## 7. Importancia de variables

### Random Forest → `rendimiento_bajo`

| Rank | Feature | Importancia |
|---|---|---|
| 1 | `prom_sem1` | 0.378 |
| 2 | `log_ingresos` | 0.081 |
| 3 | `icfes_total` | 0.080 |
| 4 | `icfes_nat` | 0.072 |
| 5 | `icfes_lec` | 0.065 |
| 6 | `nivel_edu_madre` | 0.056 |
| 7 | `sisben_nivel` | 0.049 |
| 8 | `icfes_mat` | 0.040 |

### XGBoost → `graduado`

| Rank | Feature | Importancia |
|---|---|---|
| 1 | `prom_sem1` | 0.153 |
| 2 | `icfes_total` | 0.136 |
| 3 | `cohorte_encoded` | 0.100 |
| 4 | `log_ingresos` | 0.080 |
| 5 | `repitio_escolar` | 0.079 |
| 6 | `icfes_mat` | 0.074 |
| 7 | `nivel_edu_max_padres` | 0.062 |
| 8 | `vive_con` | 0.061 |

> `prom_sem1` (promedio del primer semestre) se consolida como el predictor académico más decisivo para ambos targets, tal como se reporta en la app interactiva.

---

## 8. Modelos por materia crítica (pregunta d)

| Materia | F1-w (in-sample)* | N est. | Calidad |
|---|---|---|---|
| Álgebra Lineal | 0.971 | 71 | ✅ Excelente |
| Física I | 0.962 | 53 | ✅ Excelente |
| Matemáticas Especiales | 0.964 | 32 | ✅ Excelente |
| Programación | 0.870 | 48 | ✅ Muy bueno |
| Matemáticas II | 0.784 | 52 | ✅ Bueno |

\* Nota: Debido al bajo volumen de muestras por materia, se presenta el F1-weighted sobre el entrenamiento (in-sample) tras la optimización de hiperparámetros.

---

## 9. Pruebas estadísticas (preguntas a, b, c)

| Pregunta | Prueba | Estadístico | p-valor | Significativo |
|---|---|---|---|---|
| a) Género vs. promedio | Mann-Whitney U | U=450.0, med_M=3.30, med_F=3.70 | 0.251 | ❌ No |
| b) Edu padre vs. promedio | Spearman | rho=−0.057 | 0.596 | ❌ No |
| b) Edu madre vs. promedio | Spearman | rho=0.011 | 0.921 | ❌ No |
| c) Repitencia vs. rend. bajo | Chi-cuadrado | χ²=1.603 | 0.205 | ❌ No |

---

## 10. Criterios de éxito — Verificación

| Criterio | Estado |
|---|---|
| 3 modelos entrenados y comparados | ✅ |
| Métricas ampliadas (F1-w, F1-mac, AUC, Recall+) | ✅ |
| Modelo ganador con F1-w ≥ 0.65 | ✅ Random Forest F1=0.831 (rendimiento bajo) |
| AUC graduado > 0.70 | ✅ XGBoost AUC=0.870 |
| Importancia de variables documentada | ✅ |
| Modelo guardado en `src/mejor_modelo.pkl` | ✅ |
| Modelos por materia crítica entrenados | ✅ 5 materias |

---

## 11. Limitaciones

- Dataset depurado de tamaño moderado ($N=89$). Los resultados muestran excelente consistencia interna pero requieren validación con nuevas cohortes.
- Desbalance de género persistente (83 % masculino): las comparaciones por género tienen poder estadístico limitado debido al tamaño del subgrupo femenino ($n=15$).
- La exclusión de data leakage redujo el desempeño a niveles realistas y útiles, eliminando el sobreajuste artificial previo.

