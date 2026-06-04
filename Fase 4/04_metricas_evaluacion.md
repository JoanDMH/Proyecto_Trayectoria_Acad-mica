# Métricas de Evaluación — Modelos Finales
## CRISP-DM Fase 4 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

> Las métricas de CV-5 (89 estudiantes) son la referencia principal por su mayor confiabilidad estadística.  
> Las métricas de test (18 estudiantes) son indicativas — el tamaño limita su precisión.

---

## 1. Random Forest → `rendimiento_bajo` — Umbral 0.29

### CV-5 (n=89, referencia principal)

| Métrica | Valor | Interpretación |
|---|---|---|
| **Recall+ (clase en riesgo)** | **0.811** | El modelo detecta el 81.1 % de los estudiantes con bajo rendimiento real |
| Precisión+ | 0.545 | De los estudiantes marcados en riesgo, el 54.5 % efectivamente lo tiene |
| F1+ (binario) | 0.652 | Balance Recall/Precisión para la clase positiva |
| **F1-macro** | **0.640** | Desempeño equilibrado entre ambas clases |
| F1-weighted | 0.668 | F1 promedio ponderado por soporte |
| **AUC-ROC** | **0.775** | Buena capacidad discriminativa general |
| Average Precision | 0.791 | Área bajo curva Precision-Recall |
| **MCC** | **0.335** | Correlación de Matthews para clasificación binaria |
| Accuracy | 0.640 | 64.0 % de clasificaciones correctas en CV-5 |

### Test (n=18, indicativo)

| Métrica | Valor |
|---|---|
| Recall+ | 0.429 |
| Precisión+ | 0.500 |
| F1-macro | 0.580 |
| AUC-ROC | 0.591 |
| MCC | 0.161 |
| Accuracy | 0.611 |

### Matriz de confusión — Test

|  | Pred. Normal | Pred. Riesgo |
|---|---|---|
| **Real Normal** (n=11) | 8 ✅ | 3 ❌ falsas alarmas |
| **Real Riesgo** (n=7) | 4 ❌ no detectados | 3 ✅ |

> **Interpretación práctica:** De 7 estudiantes en riesgo real, el modelo detecta 3 (43 %). Genera 3 falsas alarmas. En contexto de intervención temprana, el modelo provee una primera alerta útil aunque moderada en el conjunto de prueba pequeño.

---

## 2. XGBoost → `graduado` — Umbral 0.50

### CV-5 (n=89, referencia principal)

| Métrica | Valor |
|---|---|
| **Recall+ (graduados)** | **0.714** |
| Precisión+ | 0.806 |
| **F1-macro** | **0.807** |
| F1-weighted | 0.820 |
| **AUC-ROC** | **0.870** |
| Average Precision | 0.823 |
| MCC | 0.618 |
| Accuracy | 0.820 |

### Test (n=18, indicativo)

| Métrica | Valor |
|---|---|
| Recall+ | 0.857 |
| Precisión+ | 0.667 |
| F1-macro | 0.775 |
| AUC-ROC | 0.922 |
| MCC | 0.570 |
| Accuracy | 0.778 |

### Matriz de confusión — Test

|  | Pred. No graduado | Pred. Graduado |
|---|---|---|
| **Real No graduado** (n=11) | 8 ✅ | 3 ❌ |
| **Real Graduado** (n=7) | 1 ❌ | 6 ✅ |

---


## 3. Modelos por materia crítica — Random Forest, umbral 0.50

| Materia | N | Tasa rep. | F1-w (in-sample)* | Calidad |
|---|---|---|---|---|
| Álgebra Lineal | 71 | 28 % | **0.971** | ✅ Excelente |
| Matemáticas Especiales | 32 | 16 % | **0.964** | ✅ Excelente |
| Física I | 53 | 26 % | **0.962** | ✅ Excelente |
| Programación | 48 | 15 % | **0.870** | ✅ Excelente |
| Matemáticas II | 52 | 44 % | **0.784** | ✅ Bueno |

\* Nota: Debido al bajo volumen muestral por materia (N entre 12 y 71), las métricas se evalúan in-sample tras la optimización de hiperparámetros.

---

## 4. Comparativa de algoritmos — `rendimiento_bajo` (umbral 0.29, CV-5)

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg.Prec | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **Árbol de Decisión** | 0.757 | **0.667** | **0.738** | 0.736 | 0.626 | **0.481** | **0.742** |
| **XGBoost** | 0.703 | 0.605 | 0.682 | **0.785** | 0.774 | 0.371 | 0.685 |
| **Random Forest** ✓ | **0.811** | 0.545 | 0.640 | 0.775 | **0.791** | 0.335 | 0.640 |

## 4b. Comparativa de algoritmos — `graduado` (umbral 0.50, CV-5)

| Modelo | Recall+ | Prec+ | F1-mac | AUC | Avg.Prec | MCC | Acc |
|---|---|---|---|---|---|---|---|
| **XGBoost** ✓ | 0.714 | **0.806** | 0.807 | 0.870 | **0.823** | 0.618 | **0.820** |
| **Random Forest** | 0.543 | 0.792 | 0.734 | 0.836 | 0.784 | 0.496 | 0.764 |
| **Árbol de Decisión** | **0.943** | 0.702 | **0.819** | **0.879** | 0.784 | **0.669** | 0.820 |

---

## 5. Resumen ejecutivo

| Modelo | Target | Umbral | F1-macro CV5 | AUC CV5 | Recall+ CV5 | Veredicto |
|---|---|---|---|---|---|---|
| Random Forest | rendimiento_bajo | **0.29** | **0.640** | **0.775** | **0.811** | ✅ Seleccionado principal |
| XGBoost | graduado | 0.50 | **0.807** | **0.870** | **0.714** | ✅ Seleccionado secundario |
| RF (×5) | materias críticas | 0.50 | 0.910 prom. | — | — | ✅ Seleccionados |

