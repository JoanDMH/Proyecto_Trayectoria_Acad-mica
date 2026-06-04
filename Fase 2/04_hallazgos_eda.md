# Informe de Fase 2 — Comprensión de los Datos
## CRISP-DM · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Población base

| Tabla | 2017-2 / 2018-1 (Muestra combinada) |
|---|---|
| `caracterización.xlsx` | 89 |
| `historial_estados_.xlsx` | 561 registros |
| `PROMEDIOS_DE_CARRERA.xlsx` | 89 |
| `detalle_materias.xlsx` | 2 719 registros |
| `promedios_semestre.xlsx` | 592 registros |

**Discrepancias resueltas:** Se realizó una exclusión metodológica de 5 estudiantes que presentaban promedios nulos y carecían de historial de materias inscritas. La muestra final limpia de población base para el modelado y análisis es de **89 estudiantes** pertenecientes a Ingeniería de Sistemas de ambas cohortes.

---

## 2. Perfil sociodemográfico (n=89)

| Variable | Hallazgo |
|---|---|
| **Género** | 74 hombres (83.1 %), 15 mujeres (16.9 %) — desbalance significativo |
| **Edad al ingreso** | Media 18 años, rango 16–25 |
| **Estrato socioeconómico** | Mayoría de estratos 1 y 2 (media 1.92); predominio de hogares de bajos ingresos |
| **Zona de residencia** | 72 urbana (80.9 %), 17 rural (19.1 %) |
| **Tipo de colegio** | 70 público (78.7 %), 19 privado (21.3 %) |
| **SISBEN** | 58 estudiantes (65.2 %) beneficiarios del SISBEN |
| **Repitencia escolar** | 15 estudiantes (16.9 %) repitieron al menos un año escolar antes del ingreso |

---

## 3. Nivel educativo de los padres

| Nivel | Padre | Madre |
|---|---|---|
| Sin datos | 19 (21.3 %) | 4 (4.5 %) |
| Bachillerato completo (código 5) | Más frecuente (Moda) | Más frecuente (Moda) |
| Técnico completo (código 8) | Frecuente | Frecuente |
| Universitario completo (código 12) | Presente | Frecuente |
| Posgrado completo (código 14) | Presente | Presente |

La mayoría de los padres no alcanzaron educación universitaria, lo cual es relevante para analizar la influencia parental sobre el rendimiento académico.

---

## 4. Resultados académicos

### 4.1 Estado final de la cohorte

| Estado final | N | % |
|---|---|---|
| Graduados | 35 | 39.3 % |
| No graduados (deserción / bajo rendimiento) | 54 | 60.7 % |

*Por cohorte: 2017-2 = 14 graduados (30 %) · 2018-1 = 21 graduados (44 %)*

La tasa de graduación acumulada de solo el 39.3 % es uno de los indicadores de mayor interés institucional.

### 4.2 Promedio acumulado de carrera

| Estadístico | Valor |
|---|---|
| Media | 3.09 |
| Mediana | 3.40 |
| Desviación estándar | 0.86 |
| Mínimo | 0.80 |
| Máximo | 4.40 |
| Estudiantes con promedio < 3.0 | 37 (41.6 %) |

---

## 5. Materias críticas (índice compuesto corregido)

**Metodología:**
- Se excluyen registros con `OBSERVACION` ∈ {O (Homologada), I (Intercambio), C (Cancelada), E (En curso)}
- Se toma la **última nota registrada** por estudiante-materia (sin repetidos)
- El **promedio** se calcula solo sobre notas **≥ 3.0** (notas aprobatorias)
- **Índice compuesto** = 0.40 × (1 − promedio\_norm) + 0.40 × tasa\_reprobación\_norm + 0.20 × repitencia\_media\_norm

| # | Materia | Prom. aprobados | Tasa reprobación | Repitencia media | Índice | N est. |
|---|---|---|---|---|---|---|
| 1 | **Física I** | 3.32 | 35.7 % | 1.60 veces | **0.858** | 53 |
| 2 | **Matemáticas II** | 3.36 | 48.3 % | 1.31 veces | **0.849** | 52 |
| 3 | **Álgebra Lineal** | 3.61 | 24.2 % | 1.54 veces | **0.743** | 71 |
| 4 | **Programación** | 3.64 | 25.9 % | 1.33 veces | **0.630** | 48 |
| 5 | **Matemáticas Especiales** | 3.75 | 16.7 % | 1.75 veces | **0.613** | 12 |

---

## 6. Hallazgos por pregunta problema

### Pregunta a — Brecha de género
- 15 mujeres en la cohorte (16.9 %). Cualquier prueba estadística de comparación tiene poder limitado.
- El análisis descriptivo muestra diferencias en el promedio a favor de las mujeres, pero no es significativo estadísticamente.

### Pregunta b — Nivel educativo de los padres
- Variable disponible con 21.3 % nulos en padre y 4.5 % en madre.
- Imputación a realizar con moda o el valor máximo parental.
- Al tratarse de variables ordinales, se aplican pruebas Spearman y modelos de árboles para capturar efectos no lineales.

### Pregunta c — Repitencia escolar previa
- 15 estudiantes (16.9 %) repitieron algún año.
- Variable binaria limpia (`ANOS_REPITIO`), sin nulos.
- Se evalúa la asociación con la tasa de bajo rendimiento mediante pruebas Chi-cuadrado y diagramas de contingencia.

### Pregunta d — Materias críticas
- Las 5 materias identificadas son del ciclo básico común de ciencias e ingeniería (semestres 1–4).
- Alta correlación académica: se entrenan submodelos para predecir reprobación en base al promedio acumulado previo y la nota en Matemáticas I.

---

## 7. Calidad de los datos — Resumen

| Aspecto | Estado |
|---|---|
| Duplicados | ✅ 0 en todos los datasets a nivel de registros de estudiantes |
| Nulos en identificadores | ✅ 0 |
| Nulos en features críticas | ⚠️ `NIVEL_ED_PADRE`: 21.3 % nulos → imputar con moda |
| Nulos en target `PROMEDIO_CARRERA` | ✅ Excluidos metodológicamente de la población base |
| Columnas inutilizables (100 % nulos) | ❌ 5 columnas excluidas |
| Outliers en notas | ✅ Ninguno fuera del rango [0.0, 5.0] |
| Desbalance de clases (target) | ⚠️ Graduado: 39.3 % / No graduado: 60.7 % → aplicar SMOTE en entrenamiento |
| Desbalance de género | ⚠️ 83.1 % masculino → limitación estadística de comparación |

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
| 18 | `cohorte_encoded` | caracterización | Binario (0=2017-2) | a, b, c |

---

## 9. Variables target

| Target | Definición | Distribución | Uso |
|---|---|---|---|
| `graduado` | 1 si el estado final es `GRADUADO`, 0 si no | 35 positivos / 54 negativos (39/61) | Preguntas a, b, c |
| `rendimiento_bajo` | 1 si `PROMEDIO_CARRERA` < 3.0, 0 si ≥ 3.0 | 37 positivos / 52 negativos (42/58) | Preguntas a, b, c |
| `reprobo_materia_X` | 1 si nota definitiva < 3.0 en materia X | Varía por materia (ver sección 5) | Pregunta d |

---

## 10. Criterios de éxito de Fase 2 — Verificación

| Criterio | Estado |
|---|---|
| Todos los DataFrames explorados con métricas indicadas | ✅ |
| Datos filtrados correctamente (cohortes combinadas, Ing. Sistemas) | ✅ |
| Población base correctamente establecida (n=89) | ✅ |
| Variables clave identificadas para cada pregunta | ✅ |
| Clave de unión confirmada (`CODIGO_INST` / `CODIGO_ESTUDIANTIL`) | ✅ |
| Informe de calidad de datos (nulos, duplicados, outliers) | ✅ |
| ≥ 15 features identificadas | ✅ (18 features) |
| 5 materias críticas con índice compuesto correcto | ✅ |
| Preguntas problema validadas | ✅ (ajustes menores documentados) |

**Fase 2 completada y sincronizada con el pipeline multi-cohorte actual.**
