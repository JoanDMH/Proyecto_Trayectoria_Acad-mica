# Informe de Fase 2 — Comprensión de los Datos
## CRISP-DM · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Población base

Se distinguen dos poblaciones a lo largo del estudio:

- **Población descriptiva (n=95):** todos los estudiantes de Ingeniería de Sistemas de las cohortes 2017-2 y 2018-1 presentes en `caracterización.xlsx`. Es la base del análisis exploratorio (perfil, estado final, deserción).
- **Muestra de modelado (n=89):** subconjunto con *features* académicas completas. Se excluyen **6 estudiantes**: 5 sin ninguna actividad académica (nunca cursaron materias) y 1 con un único período inscrito y sin promedio de carrera.

| Tabla | Registros (cohortes 2017-2 / 2018-1) | Estudiantes |
|---|---|---|
| `caracterización.xlsx` | 95 filas | 95 |
| `historial_estados_.xlsx` | 579 registros | 97* |
| `detalle_materias.xlsx` | 2 725 registros | 90 |
| `PROMEDIOS_DE_CARRERA.xlsx` | 90 filas | 90 |
| `promedios_semestre.xlsx` | 593 registros | 90 |

> \* El historial contiene 3 códigos que no están en `caracterización` (solo aparecen con estado `NO REALIZO PAGO`); no forman parte de la población de 95.

---

## 1.1 Nota metodológica — Limitación de `historial_estados_`

`historial_estados_.xlsx` **no conserva todos los estados `MATRICULADO`** de los primeros períodos de muchos estudiantes. Un estudiante puede aparecer solo con `RETIRADO BR` y/o `NO REALIZO PAGO`, dando la falsa impresión de que nunca tuvo actividad académica (caso verificado: estudiante `160004013`, que cursó 16 materias en 3 períodos pero en el historial solo figura el retiro y un impago posterior).

Para evitar este sesgo se adoptaron tres criterios:

1. **Actividad académica real** (cuántos períodos estuvo activo): se mide con `detalle_materias.xlsx` (número de `PERIODO_INSCRIPCION` distintos), **no** con el historial.
2. **Tiempo hasta la graduación:** se calcula como *período de graduación − período de ingreso* (cohorte de `caracterización`), **no** con el primer `MATRICULADO` del historial, que está incompleto y subestimaba el tiempo en 29 de 35 graduados.
3. **Clasificación del estado final por recencia** (ver sección 4.1).

---

## 2. Perfil sociodemográfico (n=95)

| Variable | Hallazgo |
|---|---|
| **Género** | 80 hombres (84.2 %), 15 mujeres (15.8 %) — desbalance significativo |
| **Edad al ingreso** | Media 18 años, rango 16–25 |
| **Estrato socioeconómico** | Media 1.94; estratos 1 y 2 = 72.6 % (35 + 34); predominio de hogares de bajos ingresos |
| **Zona de residencia** | 77 urbana (81.1 %), 18 rural (18.9 %) |
| **Tipo de colegio** | 74 público/oficial (77.9 %), 21 privado (22.1 %) |
| **SISBEN** | 62 estudiantes (65.3 %) beneficiarios del SISBEN |
| **Repitencia escolar** | 17 estudiantes (17.9 %) repitieron al menos un año escolar antes del ingreso |

---

## 3. Nivel educativo de los padres (n=95)

| Nivel | Padre | Madre |
|---|---|---|
| Sin datos | 21 (22.1 %) | 4 (4.2 %) |
| Bachillerato completo (código 5) | Más frecuente (Moda) | Más frecuente (Moda) |
| Técnico completo (código 8) | Frecuente | Frecuente |
| Universitario completo (código 12) | Presente | Frecuente |
| Posgrado completo (código 14) | Presente | Presente |

La mayoría de los padres no alcanzaron educación universitaria, lo cual es relevante para analizar la influencia parental sobre el rendimiento académico.

---

## 4. Resultados académicos

### 4.1 Estado final de la cohorte (n=95) — clasificación por recencia

Cada estudiante se clasifica en tres estados, en este orden:

1. **Graduado** — alcanzó el estado `GRADUADO`.
2. **En formación** — sin graduarse, pero con matrícula o materias en **2024-1 o después** (sigue activo).
3. **Desertor** — el resto que no se graduó, **tenga o no acta formal de retiro**. Un último estado `NO REALIZO PAGO` de hace varios años no es "estar en formación".

| Estado final | N | % |
|---|---|---|
| Graduados | 35 | 36.8 % |
| Desertores | 59 | 62.1 % |
| En formación | 1 | 1.1 % |

*Por cohorte: 2017-2 = 14 graduados (30 %), 33 desertores, 0 en formación (n=47) · 2018-1 = 21 graduados (44 %), 26 desertores, 1 en formación (n=48).*

La **deserción real (62.1 %)** es muy superior a los 30 retiros con acta formal: 29 de los 59 desertores abandonaron sin acta (ver 4.3). La tasa de graduación acumulada de solo 36.8 % es el indicador de mayor interés institucional.

### 4.2 Tiempo hasta la graduación (35 graduados)

| Estadístico | Valor |
|---|---|
| Media | 6.4 años |
| Mediana | 6.0 años |
| Mínimo | 5.0 años |
| Máximo | 8.0 años |

Casi ningún estudiante se gradúa en los 5 años nominales del plan; la moda es 6 años (12 semestres).

### 4.3 Causa de abandono (59 desertores)

| Causa | N |
|---|---|
| Sin acta formal (abandono / impago) | 29 |
| RETIRADO BR (bajo rendimiento) | 17 |
| Retiro definitivo voluntario | 8 |
| Retiro por no renovación de matrícula | 4 |
| Retiro definitivo con bajo rendimiento | 1 |

Solo **30 de 59** desertores tienen un acta formal de retiro; los otros **29** simplemente dejaron de pagar/cursar. No se les atribuye una causa de retiro inexistente.

### 4.4 Duración en la carrera de los desertores (59)

Períodos académicos con actividad real (`detalle_materias`) antes de abandonar:

| Períodos activos | 0 | 1 | 2 | 3 | 4 | 6 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| Estudiantes | 5 | 25 | 8 | 12 | 5 | 1 | 2 | 1 |

- Mediana 1 período · media 2.2 períodos.
- **5 desertores** nunca tuvieron actividad académica (inscritos sin materias).
- **38 de 59 (64 %)** abandonan con 2 períodos activos o menos → la deserción se concentra en el primer año.

### 4.5 Promedio acumulado de carrera (muestra de modelado, n=89)

| Estadístico | Valor |
|---|---|
| Media | 3.09 |
| Mediana | 3.40 |
| Desviación estándar | 0.86 |
| Mínimo | 0.80 |
| Máximo | 4.40 |
| Estudiantes con promedio < 3.0 | 37 (41.6 %) |

> El promedio de carrera y el target `rendimiento_bajo` se definen sobre la muestra de modelado (89), que es la que alimenta el modelo.

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

> **Nota de calidad:** en `detalle_materias` la asignatura "Matemáticas Especiales" aparece con dos grafías (`MATEMATICAS ESPECIALES` y `MATEMÁTICAS ESPECIALES`, con semestre 4 y 5). Conviene unificar el nombre antes de consolidar resultados por materia.

---

## 6. Hallazgos por pregunta problema

### Pregunta a — Brecha de género
- 15 mujeres en la población (15.8 %). Cualquier prueba estadística de comparación tiene poder limitado.
- El análisis descriptivo muestra diferencias en el promedio a favor de las mujeres, pero no es significativo estadísticamente.

### Pregunta b — Nivel educativo de los padres
- Variable disponible con 22.1 % nulos en padre y 4.2 % en madre.
- Imputación a realizar con moda o el valor máximo parental.
- Al tratarse de variables ordinales, se aplican pruebas Spearman y modelos de árboles para capturar efectos no lineales.

### Pregunta c — Repitencia escolar previa
- 17 estudiantes (17.9 %) repitieron algún año.
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
| Nulos en features críticas | ⚠️ `NIVEL_ED_PADRE`: 22.1 % nulos → imputar con moda |
| Integridad del historial de estados | ⚠️ `historial_estados_` no conserva todos los `MATRICULADO`; la actividad se mide con `detalle_materias` (ver 1.1) |
| Columnas inutilizables (100 % nulos) | ❌ 5 columnas excluidas |
| Outliers en notas | ✅ Ninguno fuera del rango [0.0, 5.0] |
| Desbalance de clases (target `graduado`, n=89) | ⚠️ Graduado 39.3 % / No graduado 60.7 % → aplicar SMOTE en entrenamiento |
| Desbalance de género | ⚠️ 84.2 % masculino → limitación estadística de comparación |

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
| 7 | `icfes_total` | caracterización | Continuo | d |
| 8 | `icfes_mat` (PMATN) | caracterización | Continuo | d |
| 9 | `icfes_lec` (PCRIN) | caracterización | Continuo | d |
| 10 | `icfes_nat` (PNATN) | caracterización | Continuo | d |
| 11 | `tipo_plantel` | caracterización | Binario (0=público) | c |
| 12 | `zona_rural` | caracterización | Binario (1=rural) | b |
| 13 | `log_ingresos` | caracterización | Continuo (log) | b |
| 14 | `sisben_nivel` | caracterización | Ordinal | b |
| 15 | `vive_con` | caracterización | Categórico (1–5) | a, b |
| 16 | `situacion_padres` | caracterización | Categórico (1–3) | a, b |
| 17 | `prom_sem1` | promedios_semestre | Continuo | c, d |
| 18 | `cohorte_encoded` | caracterización | Binario (0=2017-2) | a, b, c |

---

## 9. Variables target (muestra de modelado, n=89)

| Target | Definición | Distribución | Uso |
|---|---|---|---|
| `graduado` | 1 si el estado final es `GRADUADO`, 0 si no | 35 positivos / 54 negativos (39/61) | Preguntas a, b, c |
| `rendimiento_bajo` | 1 si `PROMEDIO_CARRERA` < 3.0, 0 si ≥ 3.0 | 37 positivos / 52 negativos (42/58) | Preguntas a, b, c |
| `reprobo_materia_X` | 1 si nota definitiva < 3.0 en materia X | Varía por materia (ver sección 5) | Pregunta d |

> **Coherencia con la sección 4.1:** el target binario `graduado` se construye sobre los 89 de modelado y agrupa como "no graduado" tanto a los desertores como al único estudiante en formación. Los 59 desertores descriptivos (sobre 95) y los 54 "no graduados" del modelo difieren por la población usada; la identidad de los 35 graduados no cambia.

---

## 10. Criterios de éxito de Fase 2 — Verificación

| Criterio | Estado |
|---|---|
| Todos los DataFrames explorados con métricas indicadas | ✅ |
| Datos filtrados correctamente (cohortes combinadas, Ing. Sistemas) | ✅ |
| Población establecida (descriptiva n=95 · modelado n=89) | ✅ |
| Variables clave identificadas para cada pregunta | ✅ |
| Clave de unión confirmada (`CODIGO_INST` / `CODIGO_ESTUDIANTIL`) | ✅ |
| Informe de calidad de datos (nulos, duplicados, outliers, integridad del historial) | ✅ |
| ≥ 15 features identificadas | ✅ (18 features) |
| 5 materias críticas con índice compuesto correcto | ✅ |
| Preguntas problema validadas | ✅ (ajustes menores documentados) |

**Fase 2 completada y sincronizada con el pipeline multi-cohorte actual.**
