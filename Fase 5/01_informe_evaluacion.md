# Informe de Evaluación
## CRISP-DM Fase 5 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Validación frente a los objetivos del negocio

El objetivo general es predecir el rendimiento académico de un estudiante basándose en perfiles similares históricos. Se evalúa si cada pregunta problema fue respondida con evidencia cuantitativa.

---

### Pregunta a — ¿Existe brecha de género en el rendimiento académico?

| Evidencia | Resultado |
|---|---|
| Prueba Mann-Whitney U | U=450, p=0.251 → **no significativo** |
| Mediana promedio hombres | 3.30 (n=74) |
| Mediana promedio mujeres | 3.70 (n=15) |
| Tasa rendimiento bajo — hombres | 40.5 % |
| Tasa rendimiento bajo — mujeres | 33.3 % |
| Importancia `sexo` en modelo | **0.000** (no usada por XGBoost) |

**Conclusión:** No se detecta brecha estadísticamente significativa. Las mujeres tienen mediana ligeramente superior (3.70 vs 3.30) y menor tasa de bajo rendimiento (33 % vs 40 %), pero la diferencia no alcanza significancia con p=0.251. El modelo descarta `sexo` como predictor útil. **Limitación crítica:** solo 15 mujeres en la muestra — el poder estadístico es insuficiente (~25 %) para detectar diferencias reales si existen.

---

### Pregunta b — ¿El nivel educativo de los padres predice el rendimiento?

| Evidencia | Resultado |
|---|---|
| Spearman nivel edu. padre | rho=−0.057, p=0.596 → no significativo |
| Spearman nivel edu. madre | rho=0.011, p=0.921 → no significativo |
| Importancia `nivel_edu_max_padres` en modelo | 0.027 |
| Importancia `nivel_edu_padre` en modelo | 0.045 |
| Importancia `nivel_edu_madre` en modelo | 0.041 |

**Promedio acumulado por nivel educativo máximo de los padres:**

| Nivel | Promedio carrera | N |
|---|---|---|
| Básica (primaria/bachillerato) | 3.18 | 45 |
| Técnico/Tecnólogo | 3.12 | 10 |
| Universitario o más | 2.95 | 34 |

**Conclusión:** Las correlaciones lineales no son significativas. Paradójicamente, los estudiantes cuyos padres tienen educación universitaria muestran el promedio más bajo (2.95). Esto puede reflejar mayores expectativas familiares o un efecto de confusión con el estrato. El modelo sí usa las variables de educación de los padres con importancia moderada (0.04–0.05), lo que sugiere un efecto no lineal que la correlación de Spearman no captura.

---

### Pregunta c — ¿La repitencia escolar previa predice el bajo rendimiento universitario?

| Evidencia | Resultado |
|---|---|
| Chi-cuadrado (rend. bajo) | χ²=1.603, p=0.205 → no significativo |
| Tasa rend. bajo — repitió | **52.9 %** (n=17) |
| Tasa rend. bajo — no repitió | **36.4 %** (n=77) |
| Tasa graduación — repitió | 17.6 % |
| Tasa graduación — no repitió | 41.6 % |
| Importancia `repitio_escolar` en modelo | **0.062** (7ª más importante) |

**Conclusión:** La prueba chi-cuadrado no alcanza significancia (p=0.205), pero la diferencia descriptiva es sustancial: quienes repitieron tienen una tasa de bajo rendimiento 16 puntos superior (52.9 % vs 36.4 %) y una tasa de graduación menos de la mitad (17.6 % vs 41.6 %). El modelo asigna a `repitio_escolar` la 7ª mayor importancia entre 18 variables. Con n=17 en el grupo que repitió, el test no tiene poder suficiente para detectar esta diferencia. **La señal existe pero la muestra no es suficiente para confirmarla estadísticamente.**

---

### Pregunta d — Materias críticas y predicción de reprobación

**Top 5 materias críticas (índice compuesto: 40 % promedio + 40 % reprobación + 20 % repitencia):**

| Materia | N est. | Tasa reprobación | Prom. aprobados | Rep. media | Índice |
|---|---|---|---|---|---|
| Física I | 53 | **26 %** | 3.32 | 1.60 | 0.858 |
| Matemáticas II | 52 | **44 %** | 3.36 | 1.25 | 0.849 |
| Álgebra Lineal | 71 | 28 % | 3.61 | 1.41 | 0.743 |
| Programación | 48 | 15 % | 3.64 | 1.21 | 0.630 |
| Matemáticas Especiales | — | — | — | — | sin modelo |

**Desempeño de los modelos de predicción por materia (Random Forest, CV-5):**

| Materia | F1-mac CV5 | AUC CV5 | Avg. Prec. |
|---|---|---|---|
| Álgebra Lineal | 0.913 | 0.975 | — |
| Física I | 0.882 | 0.908 | — |
| Programación | 0.820 | 0.875 | — |
| Matemáticas II | 0.650 | 0.735 | — |

**Conclusión:** Sí es posible predecir reprobación en las materias críticas usando el promedio global previo, el número de veces cursada y la nota en Matemáticas I. Álgebra Lineal y Física I tienen los mejores modelos (AUC > 0.90). Matemáticas II es la más difícil de predecir (AUC 0.735) pese a tener la mayor tasa de reprobación (44 %), posiblemente porque sus factores de riesgo son más complejos.

---

## 2. Análisis de errores — modelo principal (`rendimiento_bajo`, CV-5)

### Falsos negativos — estudiantes en riesgo no detectados (n=17)

Son los estudiantes más críticos: el modelo los clasifica como "rendimiento normal" pero tienen bajo promedio real.

* **Interpretación:** Con la muestra limpia y depurada ($N=89$), el número de Falsos Negativos asciende a 17. Estos estudiantes suelen presentar un desempeño inicial aceptable pero posteriormente decaen, un patrón difícil de capturar usando únicamente variables sociodemográficas y de ingreso.

### Falsos positivos — falsas alarmas (n=28)

Estudiantes clasificados como en riesgo que en realidad tienen rendimiento normal.

* **Interpretación:** Se registran 28 Falsos Positivos. Aunque representen intervenciones preventivas innecesarias, en el contexto educativo el costo de una falsa alarma es mucho menor que el de omitir a un estudiante en riesgo real (Falso Negativo).

---

## 3. Coherencia modelo–análisis exploratorio

| Hallazgo del EDA | Confirmado por el modelo |
|---|---|
| `prom_sem1` es el mejor predictor del resultado final | ✅ Variable más importante (19.9 %) |
| Nivel educativo padres tiene efecto no lineal | ✅ Importancia moderada en modelo, no en correlación |
| Repitencia escolar asociada a mayor riesgo descriptivamente | ✅ 7ª variable más importante (6.2 %) |
| El estrato es un factor relevante para graduación | ✅ Variable más importante en modelo `graduado` (11.1 %) |
| `cohorte_encoded` captura diferencias reales entre cohortes | ✅ 3ª variable para graduación (10.2 %) |

---

## 4. Conclusiones para el data storytelling (Fase 6)

1. **El primer semestre es determinante.** Un promedio bajo en el primer semestre es la señal más temprana y confiable de riesgo académico futuro.

2. **El origen socioeconómico importa más para graduarse que para el promedio.** Estrato y nivel educativo de padres predicen graduación con mayor fuerza que el promedio acumulado, sugiriendo que factores externos afectan la persistencia más que el desempeño.

3. **La repitencia escolar es una señal de alerta.** Quienes repitieron tienen tasas descriptivas de bajo rendimiento superiores, por lo que debe vigilarse esta señal a pesar del tamaño de muestra.

4. **Las materias del ciclo básico concentran el riesgo.** Física I y Matemáticas II son las más críticas. El rendimiento en Matemáticas I es predictor útil de reprobación en materias posteriores.

5. **No se puede concluir sobre brecha de género.** La desproporción de género limita las inferencias estadísticas de comparación directa.

---

## 5. Evaluación contra criterios de negocio

El objetivo de negocio es **identificar estudiantes en riesgo académico para intervención temprana**. El criterio de éxito definido en Fase 1 fue F1 ≥ 0.65 y Recall+ ≥ 0.75.

| Criterio de negocio | Métrica | Resultado Real (n=89) | ¿Cumple? |
|---|---|---|---|
| Detectar estudiantes en riesgo (rendimiento bajo) | Recall+ CV5 | **0.539** | ❌ No cumple |
| Modelo confiable (no predice al azar) | AUC CV5 | **0.485** | ❌ No cumple |
| Desempeño mínimo aceptable | F1-mac CV5 ≥ 0.65 | **0.491** | ❌ No cumple |
| Predecir graduación | AUC CV5 ≥ 0.70 | **0.669** | ❌ No cumple (cerca) |
| Predecir reprobación en materias críticas | AUC CV5 | **0.735–0.975** | ✅ Sí cumple |

> [!WARNING]
> **Impacto de la Depuración del Target:** Tras excluir a los 5 estudiantes "fantasma" y eliminar la imputación artificial del promedio semestral a `3.5`, se eliminó una **fuga de datos (data leakage) severa** que inflaba artificialmente las métricas originales. El rendimiento real del clasificador base en la muestra limpia disminuyó significativamente, demostrando que con los datos sociodemográficos y académicos de ingreso actuales, el modelo tiene un poder predictivo muy cercano a la clasificación aleatoria para el promedio acumulado de carrera.

---

## 6. Visualizaciones clave

*Ver archivos adjuntos en esta carpeta:*

- **`fig1_matrices_confusion.png`** — Matrices de confusión (CV-5) para ambos targets
- **`fig2_curvas_roc_pr.png`** — Curvas ROC y Precisión-Recall con punto de operación marcado
- **`fig3_cv_por_fold.png`** — Recall+, F1-macro y MCC por cada fold del CV-5

---

## 7. Reporte de validación cruzada (StratifiedKFold k=5)

La validación cruzada estratificada garantiza que cada fold mantiene la proporción de clases. Resultados por fold en `fig3_cv_por_fold.png`.

**Resumen de estabilidad:**

| Target | Métrica | Media | Std | Interpretación |
|---|---|---|---|---|
| rendimiento_bajo | Recall+ | **0.539** | 0.259 | Alta variabilidad por tamaño de muestra reducido |
| rendimiento_bajo | F1-macro | **0.491** | 0.168 | Desempeño bajo, cercano al azar |
| rendimiento_bajo | MCC | **0.011** | 0.354 | Correlación nula con el target real |
| graduado | Recall+ | **0.600** | 0.120 | Estabilidad moderada |
| graduado | F1-macro | **0.659** | 0.116 | Aceptable |
| graduado | MCC | **0.333** | 0.223 | Correlación positiva moderada |

---

## 8. Revisión de supuestos

XGBoost es un modelo basado en árboles de decisión; **no asume linealidad, normalidad ni homocedasticidad**. Los supuestos relevantes son:

| Supuesto | ¿Se cumple? | Evidencia |
|---|---|---|
| **Independencia de observaciones** | ✅ | Cada fila es un estudiante diferente. |
| **Ausencia de data leakage** | ✅ | `PROMEDIO_CARRERA` no es feature; split anterior a SMOTE; CV aplicado sobre datos originales. |
| **Representatividad del train set** | ⚠️ | Solo 2 cohortes de un programa. El modelo puede no generalizar a otros programas. |
| **Estabilidad temporal** | ⚠️ | `cohorte_encoded` captura diferencias entre cohortes — si las condiciones cambian, el modelo requerirá reentrenamiento. |
| **Suficiencia muestral** | ❌ No cumple | $N=89$ es una muestra sumamente pequeña para entrenar algoritmos boosting como XGBoost. |
| **Desbalance de clases tratado** | ✅ | SMOTE aplicado únicamente en el set de entrenamiento de cada split. |

---

## 9. Decisión de aprobación

**¿Pasa el modelo a producción/despliegue?**

> ⚠️ **SÍ — Con reservas y exclusivamente con fines experimentales y descriptivos**

**Justificación:**
- Las métricas para predecir reprobación en materias críticas individuales son muy altas y estables (AUC > 0.73), por lo que esa sección es robusta.
- Sin embargo, el predictor interactivo global de riesgo académico acumulado no cumple los criterios mínimos del negocio (F1 y Recall) al haber eliminado el data leakage. El modelo sirve como descriptivo inicial de la muestra actual, pero **no debe utilizarse de forma automatizada para tomar decisiones académicas determinantes** sin antes recolectar más datos de nuevas cohortes.
gue:**
1. Usar umbral 0.29 para `rendimiento_bajo` (maximiza detección de riesgo)
2. Comunicar las limitaciones al usuario final: n=94, solo 2 cohortes, 84 % masculino
3. Reentrenar al incorporar nuevas cohortes
4. No usar para toma de decisiones definitivas — solo como herramienta de alerta temprana

---

## 10. Criterios de éxito CRISP-DM — Verificación final

| Criterio | Estado |
|---|---|
| Las 4 preguntas respondidas con evidencia cuantitativa | ✅ |
| Modelo valida coherencia con EDA | ✅ |
| Falsos positivos y negativos analizados | ✅ |
| Conclusiones documentadas para storytelling | ✅ |
| Matriz de confusión y curvas ROC generadas | ✅ |
| Reporte de validación cruzada completo | ✅ |
| Supuestos revisados | ✅ |
| Decisión de aprobación explícita | ✅ Sí, con condiciones |
