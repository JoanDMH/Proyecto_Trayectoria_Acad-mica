# Métricas de Evaluación — Modelos Finales

> ## ⚠️ DOCUMENTO DE FASE — sus cifras corresponden al target SUSTITUIDO
>
> Este informe documenta lo que se hizo y se midió **en su momento**, con la variable
> objetivo `rendimiento_bajo` (`PROMEDIO_CARRERA < 3,0`) y, donde aparezcan, con los
> modelos de reprobación por asignatura. **Ambos fueron retirados después:**
>
> | Lo que dice este documento | Estado actual |
> |---|---|
> | Target `PROMEDIO_CARRERA < 3,0` | **Descartado por tautológico** (RC-012, RC-017). Sustituido por el derivado del **artículo 19** |
> | Recall+ 0,816 · AUC 0,752 | El modelo vigente es Random Forest con **AUC-PR 0,745 ± 0,025** sobre n=80 (RC-033, RC-045) |
> | Modelos de reprobación por asignatura (AUC 0,865–0,939) | **Retirados por fuga temporal** (RC-013, RC-022). Solo sobrevive el índice descriptivo de criticidad |
> | 18 variables · umbral único 0,29 · CV-5 simple | 6 variables (S3) · esquema de tres niveles · **CV-5 anidada** × 10 repeticiones |
>
> **No se reescribe**: narra la iteración de CRISP-DM y es parte del expediente del trabajo.
> Para el estado vigente: `PLAN_DE_TRABAJO.md`, `PROBLEMAS_DETECTADOS.txt` y `REGISTRO_CIENTIFICO.md`.

## CRISP-DM Fase 4 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

> ## ⛔ AVISO — MODELOS POR ASIGNATURA RETIRADOS (I-4 · RC-013 / RC-022)
> Las métricas de los **modelos de reprobación por asignatura** que aparecen en este
> documento (AUC 0,865–0,939, F1-w 0,79–0,93) **quedan invalidadas por fuga temporal**:
> el predictor `prom_global` es el promedio del estudiante en el resto de la carrera y
> entre el 70 % y el 83 % de esa información proviene de semestres **posteriores** a la
> asignatura que se predice. El desempeño honesto es AUC 0,70–0,74.
>
> El **índice de criticidad** (ranking de asignaturas) **no está afectado**: es un
> indicador descriptivo, no un modelo. Sigue siendo válido.
>
> Este documento se conserva como registro histórico de la fase. Ver
> `AUDITORIA_2026-09.md` §3 antes de reutilizar cualquier cifra.

> Las métricas de CV-5 (89 estudiantes) son la referencia principal por su mayor confiabilidad estadística.  
> Las métricas de test (18 estudiantes) son indicativas — el tamaño limita su precisión.

---

## 1. Random Forest → `rendimiento_bajo` — Umbral 0.29

### CV-5 (n=90, referencia principal)

| Métrica | Valor | Interpretación |
|---|---|---|
| **Recall+ (clase en riesgo)** | **0.816** | El modelo detecta el 81.6 % de los estudiantes con bajo rendimiento real |
| Precisión+ | 0.484 | De los estudiantes marcados en riesgo, el 48.4 % efectivamente lo tiene |
| F1+ (binario) | 0.608 | Balance Recall/Precisión para la clase positiva |
| **F1-macro** | **0.548** | Desempeño equilibrado entre ambas clases |
| F1-weighted | 0.538 | F1 promedio ponderado por soporte |
| **AUC-ROC** | **0.752** | Buena capacidad discriminativa general |
| Average Precision | 0.774 | Área bajo curva Precision-Recall |
| **MCC** | **0.197** | Correlación de Matthews para clasificación binaria |
| Accuracy | 0.556 | 55.6 % de clasificaciones correctas en CV-5 (umbral agresivo pro-Recall) |

### Test (n=18, indicativo)

| Métrica | Valor |
|---|---|
| Recall+ | 0.875 |
| Precisión+ | 0.538 |
| F1-macro | 0.600 |
| AUC-ROC | 0.713 |
| MCC | 0.305 |
| Accuracy | 0.611 |

### Matriz de confusión — Test

|  | Pred. Normal | Pred. Riesgo |
|---|---|---|
| **Real Normal** (n=10) | 4 ✅ | 6 ❌ falsas alarmas |
| **Real Riesgo** (n=8) | 1 ❌ no detectado | 7 ✅ |

> **Interpretación práctica:** De 8 estudiantes en riesgo real, el modelo detecta 7 (87.5 %) a costa de 6 falsas alarmas. Consistente con el objetivo de alerta temprana: máxima cobertura del riesgo con revisión manual de las alarmas.

---

## 2. XGBoost → `graduado` — Umbral 0.50

### CV-5 (n=90, referencia principal)

| Métrica | Valor |
|---|---|
| **Recall+ (graduados)** | **0.600** |
| Precisión+ | 0.808 |
| **F1-macro** | **0.764** |
| F1-weighted | 0.781 |
| **AUC-ROC** | **0.853** |
| Average Precision | 0.727 |
| MCC | 0.548 |
| Accuracy | 0.789 |

### Test (n=18, indicativo)

| Métrica | Valor |
|---|---|
| Recall+ | 0.400 |
| Precisión+ | 0.400 |
| F1-macro | 0.585 |
| AUC-ROC | 0.600 |
| MCC | 0.169 |
| Accuracy | 0.667 |

### Matriz de confusión — Test

|  | Pred. No graduado | Pred. Graduado |
|---|---|---|
| **Real No graduado** (n=13) | 10 ✅ | 3 ❌ |
| **Real Graduado** (n=5) | 3 ❌ | 2 ✅ |

---


## 3. Modelos por materia crítica — Random Forest, umbral 0.50

Métricas por validación cruzada (CV-5, out-of-fold), sin fugas, sobre datos recodificados:

| Materia | N | Tasa rep. | F1-w (CV-5) | AUC (CV-5) | Calidad |
|---|---|---|---|---|---|
| Matemáticas I | 73 | 26.0 % | **0.928** | 0.928 | ✅ Excelente |
| Fund. de Programación | 72 | 20.8 % | **0.928** | 0.923 | ✅ Excelente |
| Álgebra Lineal | 72 | 29.2 % | **0.912** | 0.939 | ✅ Excelente |
| Física I | 54 | 27.8 % | **0.848** | 0.884 | ✅ Muy bueno |
| Matemáticas II | 54 | 31.5 % | **0.785** | 0.865 | ✅ Bueno |

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

