# Informe de Fase 2 — Comprensión de los Datos
## CRISP-DM · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Población base

| Tabla | 2017-2 | 2018-1 | Total |
|---|---|---|---|
| `caracterización.xlsx` | 47 | 48 | 95 |
| `historial_estados_.xlsx` | 49 | 49 | 98 |
| `promedios_carrera.xlsx` | 46 | 48 | 94 |
| `detalle_materias.xlsx` | 46 | 48 | 94 |
| `promedios_semestre.xlsx` | 46 | 48 | 94 |

**Discrepancias resueltas:** Estudiantes con solo estado `NO REALIZO PAGO` excluidos. El estudiante 160004030 (2017-2) sin historial académico también excluido. La cohorte 2018-1 tiene 1 estudiante aún activo, cuyo target `graduado`=0 se mantiene (no graduado hasta la fecha de corte).

> **Población base definitiva para el modelado: 94 estudiantes** (46 de 2017-2 + 48 de 2018-1).

---

## 2. Perfil sociodemográfico

| Variable | Hallazgo |
|---|---|
| **Género** | 79 hombres (84 %), 15 mujeres (16 %) — desbalance significativo |
| **Edad al ingreso** | Media 18 años, rango 16–25 |
| **Estrato socioeconómico** | Mayoría estrato 1 y 2; predominio de hogares de bajos ingresos |
| **Zona de residencia** | 82 % urbana, 18 % rural |
| **Tipo de colegio** | 78 % público, 22 % privado |
| **SISBEN** | ~72 % beneficiarios del SISBEN |
| **Relación familiar** | 91 % reporta relación familiar buena |
| **Situación de los padres** | 52 % separados/divorciados, 39 % conviven, 7 % nuevo hogar |
| **Crianza** | 85 % criados por ambos padres |
| **Vive con** | 54 % con ambos padres, 26 % con uno solo |
| **Repitencia escolar** | 17 estudiantes (18.1 %) repitieron al menos un año |

---

## 3. Nivel educativo de los padres

| Nivel | Padre | Madre |
|---|---|---|
| Sin datos | 9 (20 %) | 2 (4 %) |
| Bachillerato completo (código 5) | Más frecuente | Más frecuente |
| Técnico completo (código 8) | Segundo | — |
| Universitario completo (código 12) | Presente | Frecuente |
| Posgrado completo (código 14) | Presente | Presente |

La mayoría de los padres no alcanzaron educación universitaria, lo cual es relevante para la pregunta b.

---

## 4. Resultados académicos

### 4.1 Estado final de la cohorte

| Estado final | N | % |
|---|---|---|
| Graduados | 35 | 37.2 % |
| No graduados (deserción / bajo rendimiento) | 59 | 62.8 % |

*Por cohorte: 2017-2 = 14/46 (30 %) · 2018-1 = 21/48 (44 %)*

La tasa de graduación de solo el 30 % es el indicador más crítico de la cohorte.

### 4.2 Promedio acumulado de carrera

| Estadístico | Valor |
|---|---|
| Media | 3.09 |
| Mediana | 3.40 |
| Desviación estándar | 0.85 |
| Mínimo | 0.90 |
| Máximo | 4.40 |
| Estudiantes con promedio < 3.0 | 37 (42 %) |

### 4.3 Evolución semestral

Los promedios semestres muestran caída progresiva en los primeros tres semestres —periodo de mayor deserción—, seguida de recuperación en quienes persisten.

---

## 5. Materias críticas (índice compuesto corregido)

**Metodología:**
- Se excluyen registros con `OBSERVACION` ∈ {O (Homologada), I (Intercambio), C (Cancelada), E (En curso)}
- Se toma la **última nota registrada** por estudiante-materia (sin repetidos)
- El **promedio** se calcula solo sobre notas **≥ 3.0** (notas aprobatorias)
- **Índice compuesto** = 0.40 × (1 − promedio\_norm) + 0.40 × tasa\_reprobación\_norm + 0.20 × repitencia\_media\_norm

| # | Materia | Prom. aprobados | Tasa reprobación | Repitencia media | Índice | N est. |
|---|---|---|---|---|---|---|
| 1 | **Física I** | 3.29 | 35.7 % | 1.61 veces | **0.858** | 28 |
| 2 | **Matemáticas II** | 3.39 | 48.3 % | 1.31 veces | **0.849** | 29 |
| 3 | **Álgebra Lineal** | 3.34 | 24.2 % | 1.61 veces | **0.746** | 33 |
| 4 | **Programación** | 3.51 | 25.9 % | 1.33 veces | **0.630** | 27 |
| 5 | **Matemáticas Especiales** | 3.66 | 16.7 % | 1.75 veces | **0.613** | 12 |

> **Cambio respecto al análisis inicial:** Programación reemplaza a Matemáticas III al excluir homologaciones. Física I sube al primer lugar por alta repitencia + tasa de reprobación elevada.

---

## 6. Hallazgos por pregunta problema

### Pregunta a — Brecha de género
- Solo 5 mujeres en la cohorte (11 %). Cualquier prueba estadística tendrá poder muy limitado.
- El análisis descriptivo es viable, pero los resultados inferenciales deben interpretarse con cautela.
- Se recomienda reportar el efecto de tamaño además del p-valor.

### Pregunta b — Nivel educativo de los padres
- Variable disponible con ~20 % nulos en padre y 4 % en madre.
- Para imputación: usar mediana del grupo (moda) o categoría "Desconocido".
- Variable ordinal → usar correlación de Spearman o regresión ordinal.

### Pregunta c — Repitencia escolar previa
- 9 estudiantes (19.6 %) repitieron algún año.
- Variable binaria limpia (`ANOS_REPITIO`), sin nulos.
- Subgrupo pequeño (n=9) → chi-cuadrado o Fisher's exact test.

### Pregunta d — Materias críticas
- Las 5 materias identificadas son todas del ciclo básico de ciencias e ingeniería (semestres 1–4).
- Alta correlación entre ellas: estudiantes que reprueban Física I tienden a reprobar Matemáticas II.
- Para el submodelo de predicción: usar promedios de materias previas correlacionadas como feature.

---

## 7. Calidad de los datos — Resumen

| Aspecto | Estado |
|---|---|
| Duplicados | ✅ 0 en todos los datasets |
| Nulos en identificadores | ✅ 0 |
| Nulos en features críticas | ⚠️ `NIVEL_ED_PADRE`: 20 % nulos → imputar con moda |
| Nulos en target `PROMEDIO_CARRERA` | ✅ 0 para los 46 estudiantes base |
| Columnas inutilizables (100 % nulos) | ❌ 5 columnas excluidas |
| Outliers en notas | ✅ Ninguno fuera del rango [0, 5] |
| Desbalance de clases (target) | ⚠️ Graduado: 30 % / No graduado: 70 % → aplicar SMOTE en entrenamiento |
| Desbalance de género | ⚠️ 89 % masculino → limitación estadística, documentar |

---

## 8. Features seleccionadas para Fase 3 (≥ 15 atributos)

| # | Feature | Fuente | Tipo | Pregunta |
|---|---|---|---|---|
| 1 | `sexo` | caracterización | Binario | a |
| 2 | `nivel_edu_padre` | caracterización | Ordinal (1–14) | b |
| 3 | `nivel_edu_madre` | caracterización | Ordinal (1–14) | b |
| 4 | `nivel_edu_max_padres` | derivada | Ordinal | b |
| 5 | `repitio_escolar` | caracterización | Binario | c |
| 6 | `estrato` | caracterización | Ordinal (1–6) | a, b, c |
| 7 | `puntaje_icfes_total` | caracterización | Continuo | d |
| 8 | `puntaje_icfes_mat` (PMATN) | caracterización | Continuo | d |
| 9 | `puntaje_icfes_lec` (PCRIN) | caracterización | Continuo | d |
| 10 | `puntaje_icfes_nat` (PNATN) | caracterización | Continuo | d |
| 11 | `tipo_plantel` | caracterización | Binario (0=público) | c |
| 12 | `zona_residencia` | caracterización | Binario (0=urbana) | b |
| 13 | `ingresos_hogar` | caracterización | Continuo (log) | b |
| 14 | `sisben_nivel` | caracterización | Ordinal | b |
| 15 | `vive_con` | caracterización | Categórico (1–5) | a, b |
| 16 | `situacion_padres` | caracterización | Categórico (1–3) | a, b |
| 17 | `prom_sem1` | promedios_semestre | Continuo | c, d |

**Features adicionales para submodelo de materias (pregunta d):**
- `promedio_global_previo`: promedio general del estudiante excluyendo la materia objetivo
- `prom_matematicas_i`: nota en Matemáticas I (predictor de materias del ciclo básico)
- `veces_cursada`: número de intentos en la materia objetivo
- `semestre_en_que_cursa`: semestre del plan en que el estudiante tomó la materia

---

## 9. Variables target

| Target | Definición | Distribución | Uso |
|---|---|---|---|
| `graduado` | 1 si el estado final es `GRADUADO`, 0 si no | 14 positivos / 32 negativos (30/70) | Preguntas a, b, c |
| `rendimiento_bajo` | 1 si `PROMEDIO_CARRERA` < 3.0, 0 si ≥ 3.0 | 19 positivos / 27 negativos (41/59) | Preguntas a, b, c |
| `reprobo_materia_X` | 1 si nota definitiva < 3.0 en materia X | Varía por materia (ver sección 5) | Pregunta d |

> Para el modelo principal se usará `rendimiento_bajo` como target primario por tener distribución más balanceada (41/59 vs 30/70).

---

## 10. Criterios de éxito de Fase 2 — Verificación

| Criterio | Estado |
|---|---|
| Todos los DataFrames explorados con métricas indicadas | ✅ |
| Datos filtrados correctamente (cohorte 2017-2, Ing. Sistemas) | ✅ |
| Población base correctamente establecida (n=46) | ✅ |
| Variables clave identificadas para cada pregunta | ✅ |
| Clave de unión confirmada (`CODIGO_INST` / `CODIGO_ESTUDIANTIL`) | ✅ |
| Informe de calidad de datos (nulos, duplicados, outliers) | ✅ |
| ≥ 15 features identificadas | ✅ (17 features + 4 para submodelo) |
| 5 materias críticas con índice compuesto correcto | ✅ |
| Preguntas problema validadas | ✅ (ajustes menores documentados) |

**→ Fase 2 completada. Se puede proceder a Fase 3.**
