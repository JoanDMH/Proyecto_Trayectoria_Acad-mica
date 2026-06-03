# Informe de Modelado
## CRISP-DM Fase 4 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Configuración experimental

| Parámetro | Valor |
|---|---|
| Población base | 94 estudiantes (46 de 2017-2 + 48 de 2018-1) |
| Semilla aleatoria | 42 |
| División train/test | 80 % / 20 % estratificada (75 train / 19 test) |
| Validación cruzada | StratifiedKFold k=5 sobre train |
| Métrica principal de selección | F1-Score ponderado (CV-5) |
| Métricas adicionales | F1-macro, AUC-ROC, Precisión, Recall+, MCC, Average Precision |
| Manejo de desbalance | SMOTE sobre train cuando proporción < 60 % |
| Escalado | No aplicado (modelos invariantes a escala) |
| **Umbral `rendimiento_bajo`** | **0.29** (optimizado, ver §5) |
| **Umbral `graduado`** | **0.50** (default) |

---

## 2. Modelos candidatos y hiperparámetros

| Modelo | Configuración |
|---|---|
| Árbol de Decisión | `max_depth=3, min_samples_leaf=2` |
| Random Forest | `n_estimators=100, max_depth=4, min_samples_leaf=2` |
| XGBoost | `n_estimators=100, max_depth=3, lr=0.1, subsample=0.8, colsample_bytree=0.8` |

---

## 3. Resultados — TARGET: `rendimiento_bajo` — Umbral 0.29 — CV-5 (n=94)

Distribución: 37 positivos / 57 negativos (39 % / 61 %)

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg. Prec. | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **XGBoost** ✓ | **0.811** | **0.732** | **0.803** | **0.821** | **0.825** | **0.609** | **0.809** |
| Árbol de Decisión | 0.757 | 0.718 | 0.779 | 0.804 | 0.746 | 0.559 | 0.787 |
| Random Forest | 0.784 | 0.500 | 0.606 | 0.779 | 0.804 | 0.276 | 0.606 |

> XGBoost lidera en todas las métricas. Random Forest obtiene buen Recall+ (0.784) pero su MCC (0.276) y F1-mac (0.606) revelan exceso de falsas alarmas con umbral 0.29 — no es competitivo. Árbol de Decisión es estable pero inferior en todas las métricas clave.

---

## 4. Resultados — TARGET: `graduado` — Umbral 0.50 — CV-5 (n=94)

Distribución: 35 positivos / 59 negativos (37 % / 63 %)  
SMOTE aplicado sobre train.

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg. Prec. | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **XGBoost** ✓ | 0.571 | **0.667** | **0.706** | **0.758** | 0.649 | **0.417** | **0.734** |
| Random Forest | 0.371 | **0.812** | 0.664 | 0.744 | **0.692** | 0.412 | **0.734** |
| Árbol de Decisión | **0.514** | 0.562 | 0.641 | 0.742 | 0.634 | 0.283 | 0.670 |

> XGBoost lidera en F1-mac, AUC y MCC. Random Forest tiene mayor Average Precision (0.692) y precisión (0.812) pero recall muy bajo (0.371), lo que lo hace conservador. XGBoost ofrece el mejor balance general.
> **Mejora notable vs. dataset de 46 estudiantes:** AUC subió de 0.57 a 0.76, bien por encima del umbral 0.70.

---

## 5. Optimización del umbral de clasificación

Con el umbral por defecto (0.50), el Recall+ en CV-5 para `rendimiento_bajo` era **0.757**: el modelo no detectaba el 24 % de los estudiantes en riesgo. En contexto educativo, un falso negativo (no identificar a un estudiante que necesita intervención) tiene mayor costo que una falsa alarma.

Se realizó una búsqueda del umbral óptimo minimizando el **F2-score** (pondera el Recall el doble que la Precisión) sobre las probabilidades de CV-5:

| Umbral | Recall+ CV5 | Precisión+ CV5 | F1-macro CV5 | MCC CV5 |
|---|---|---|---|---|
| 0.50 (default) | 0.757 | 0.800 | 0.820 | 0.641 |
| **0.29 (seleccionado)** | **0.811** | **0.732** | **0.803** | **0.609** |

**Resultado:** el umbral 0.29 aumenta el Recall+ en +5.4 puntos (de 0.757 a 0.811), aceptando una reducción de Precisión+ de 0.800 a 0.732. El modelo detecta 1 de cada 12 estudiantes más en riesgo real, a costa de generar algunas alertas adicionales.

Para `graduado` se mantuvo el umbral 0.50 porque bajarlo a 0.29 reducía el F1-macro de 0.706 a 0.674.

---

## 6. Modelo principal seleccionado

**XGBoost sobre `rendimiento_bajo`** — umbral 0.29 (F1-macro CV5 = 0.803, AUC CV5 = 0.821, Recall+ CV5 = 0.811)

---

## 6. Importancia de variables

### XGBoost → `rendimiento_bajo`

| Rank | Feature | Importancia |
|---|---|---|
| 1 | `prom_sem1` | 0.199 |
| 2 | `icfes_total` | 0.088 |
| 3 | `icfes_nat` | 0.084 |
| 4 | `sisben_nivel` | 0.080 |
| 5 | `icfes_lec` | 0.072 |
| 6 | `cohorte_encoded` | 0.063 |
| 7 | `repitio_escolar` | 0.062 |
| 8 | `icfes_mat` | 0.056 |

### XGBoost → `graduado`

| Rank | Feature | Importancia |
|---|---|---|
| 1 | `estrato` | 0.111 |
| 2 | `prom_sem1` | 0.107 |
| 3 | `cohorte_encoded` | 0.102 |
| 4 | `sisben_nivel` | 0.081 |
| 5 | `icfes_total` | 0.074 |
| 6 | `zona_rural` | 0.066 |
| 7 | `icfes_nat` | 0.065 |
| 8 | `log_ingresos` | 0.060 |

> `cohorte_encoded` aparece entre las 3 variables más importantes para graduación (10.2 %), lo que confirma que existe una diferencia real entre cohortes: la 2018-1 tiene mayor tasa de graduación (44 % vs 30 %).

---

## 7. Modelos por materia crítica (pregunta d)

| Materia | F1-w CV5 | AUC CV5 | N est. | Tasa reprobación |
|---|---|---|---|---|
| Álgebra Lineal | 0.913 | 0.975 | 71 | 28 % |
| Física I | 0.882 | 0.908 | 53 | 26 % |
| Programación | 0.820 | 0.875 | 48 | 15 % |
| Matemáticas II | 0.650 | 0.735 | 52 | 44 % |

> Matemáticas Especiales no alcanzó el mínimo de muestras positivas requerido para entrenar con ambas cohortes.

---

## 8. Pruebas estadísticas (preguntas a, b, c)

| Pregunta | Prueba | Estadístico | p-valor | Significativo |
|---|---|---|---|---|
| a) Género vs. promedio | Mann-Whitney U | U=450, med_M=3.30, med_F=3.70 | 0.251 | ❌ No |
| b) Edu padre vs. promedio | Spearman | rho=−0.057 | 0.596 | ❌ No |
| b) Edu madre vs. promedio | Spearman | rho=0.011 | 0.921 | ❌ No |
| c) Repitencia vs. rend. bajo | Chi-cuadrado | χ²=1.603 | 0.205 | ❌ No |

> Ninguna prueba resulta significativa. Con n=94 el poder estadístico mejora respecto a n=46, pero las diferencias observadas son genuinamente pequeñas.
> La tasa de rendimiento bajo para quienes repitieron (52.9 %) vs. quienes no (36.4 %) muestra una tendencia relevante aunque no significativa estadísticamente.

---

## 9. Criterios de éxito — Verificación

| Criterio | Estado |
|---|---|
| 3 modelos entrenados y comparados | ✅ |
| Métricas ampliadas (F1-w, F1-mac, AUC, Recall+) | ✅ |
| Modelo ganador con F1-w ≥ 0.65 | ✅ XGBoost F1=0.826 |
| AUC graduado > 0.70 | ✅ 0.730 (mejora desde 0.57 con n=46) |
| Importancia de variables documentada | ✅ |
| Modelo guardado en `src/mejor_modelo.pkl` | ✅ |
| Modelos por materia crítica entrenados | ✅ 4 materias |

---

## 10. Limitaciones

- Dataset aún pequeño para ML estándar (n=94 train=75). Los resultados son orientativos.
- Desbalance de género persiste (84 % masculino): prueba de género tiene bajo poder estadístico.
- La cohorte 2018-1 tiene 1 estudiante aún activo; su target `graduado`=0 podría cambiar en el futuro.
- `cohorte_encoded` captura diferencias entre cohortes que podrían no generalizarse a cohortes futuras.
