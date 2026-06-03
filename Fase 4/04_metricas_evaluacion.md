# Métricas de Evaluación — Modelos Finales
## CRISP-DM Fase 4 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

> Las métricas de CV-5 (94 estudiantes) son la referencia principal por su mayor confiabilidad estadística.  
> Las métricas de test (19 estudiantes) son indicativas — el tamaño limita su precisión.

---

## 1. XGBoost → `rendimiento_bajo` — Umbral 0.29

### CV-5 (n=94, referencia principal)

| Métrica | Valor | Interpretación |
|---|---|---|
| **Recall+ (clase en riesgo)** | **0.811** | El modelo detecta el 81 % de los estudiantes con bajo rendimiento |
| Precisión+ | 0.732 | De los estudiantes marcados en riesgo, el 73 % efectivamente lo tiene |
| F1+ (binario) | 0.769 | Balance Recall/Precisión para la clase positiva |
| **F1-macro** | **0.803** | Desempeño equilibrado entre ambas clases |
| F1-weighted | 0.810 | F1 ponderado por soporte de cada clase |
| **AUC-ROC** | **0.821** | Alta capacidad discriminativa |
| Average Precision | 0.825 | Área bajo curva Precision-Recall |
| **MCC** | **0.609** | Correlación de Matthews — métrica robusta para desbalance |
| Accuracy | 0.809 | 80.9 % de clasificaciones correctas |

### Test (n=19, indicativo)

| Métrica | Valor |
|---|---|
| Recall+ | 0.714 |
| Precisión+ | 0.625 |
| F1-macro | 0.725 |
| AUC-ROC | 0.738 |
| MCC | 0.454 |
| Accuracy | 0.737 |

### Matriz de confusión — Test

|  | Pred. Normal | Pred. Riesgo |
|---|---|---|
| **Real Normal** (n=12) | 9 ✅ | 3 ❌ falsas alarmas |
| **Real Riesgo** (n=7) | 2 ❌ no detectados | 5 ✅ |

> **Interpretación práctica:** De 7 estudiantes en riesgo real, el modelo detecta 5 (71 %). Genera 3 falsas alarmas (estudiantes normales etiquetados como en riesgo). En contexto de intervención educativa temprana, este balance es aceptable.

---

## 2. XGBoost → `graduado` — Umbral 0.50

### CV-5 (n=94, referencia principal)

| Métrica | Valor |
|---|---|
| **Recall+ (graduados)** | **0.833** |
| Precisión+ | — |
| **F1-macro** | **0.706** |
| F1-weighted | 0.728 |
| **AUC-ROC** | **0.730** |
| Average Precision | 0.649 |
| MCC | — |
| Accuracy | — |

### Matriz de confusión — Test

|  | Pred. No graduado | Pred. Graduado |
|---|---|---|
| **Real No graduado** (n=13) | — | — |
| **Real Graduado** (n=6) | 1 ❌ | 5 ✅ |

---

## 3. Modelos por materia crítica — Random Forest, umbral 0.50

| Materia | N | Tasa rep. | F1-w CV5 | AUC CV5 | Calidad |
|---|---|---|---|---|---|
| Álgebra Lineal | 71 | 28 % | 0.913 | 0.975 | ✅ Excelente |
| Física I | 53 | 26 % | 0.882 | 0.908 | ✅ Muy bueno |
| Programación | 48 | 15 % | 0.820 | 0.875 | ✅ Bueno |
| Matemáticas II | 52 | 44 % | 0.650 | 0.735 | ⚠️ Aceptable |

> Matemáticas Especiales no tiene suficientes positivos para estimar con CV-5.

---

## 4. Comparativa de algoritmos — `rendimiento_bajo` (umbral 0.29, CV-5)

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg.Prec | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **XGBoost** ✓ | **0.811** | **0.732** | **0.803** | **0.821** | **0.825** | **0.609** | **0.809** |
| Árbol de Decisión | 0.757 | 0.718 | 0.779 | 0.804 | 0.746 | 0.559 | 0.787 |
| Random Forest | 0.784 | 0.500 | 0.606 | 0.779 | 0.804 | 0.276 | 0.606 |

## 4b. Comparativa de algoritmos — `graduado` (umbral 0.50, CV-5)

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg.Prec | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **XGBoost** ✓ | 0.571 | **0.667** | **0.706** | **0.758** | 0.649 | **0.417** | **0.734** |
| Random Forest | 0.371 | **0.812** | 0.664 | 0.744 | **0.692** | 0.412 | **0.734** |
| Árbol de Decisión | **0.514** | 0.562 | 0.641 | 0.742 | 0.634 | 0.283 | 0.670 |

---

## 5. Resumen ejecutivo

| Modelo | Target | Umbral | F1-macro CV5 | AUC CV5 | Recall+ CV5 | Veredicto |
|---|---|---|---|---|---|---|
| XGBoost | rendimiento_bajo | **0.29** | **0.803** | **0.821** | **0.811** | ✅ Seleccionado principal |
| XGBoost | graduado | 0.50 | 0.706 | 0.730 | 0.833 | ✅ Seleccionado secundario |
| RF (×4) | materias críticas | 0.50 | 0.766 prom. | 0.873 prom. | — | ✅ Seleccionados |
