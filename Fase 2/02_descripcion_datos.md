# Reporte de Descripción de Datos
## CRISP-DM Fase 2 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

> **Poblaciones:** análisis descriptivo sobre **n=95** (caracterización, ambas cohortes). El **modelado** (Fases 3-5) usa una submuestra de **89** con features académicas completas (se excluyen 6 estudiantes sin actividad o sin promedio).

---

## 1. `caracterización.xlsx` — Variables analíticas (cohorte filtrada: n=95)

### Tipos de datos

| Tipo | Columnas | Ejemplos |
|---|---|---|
| Numérico continuo | 16 | `INGRESOS`, `PMATN`, `PINGN`, `PCRIN`, `PCIUN`, `PNATN`, `PUNTAJE_SISBEN` |
| Numérico ordinal | 4 | `ESTRATO_ACTUAL`, `NIVEL_ED_PADRE`, `NIVEL_ED_MADRE`, `URBANA_SISBEN` |
| Categórico | 22 | `SEXO`, `TIPO_PLANTEL`, `ZONA_LUGAR_RESIDENCIA`, `ANOS_REPITIO`, `SISBEN`… |
| Fecha | 1 | `FECHA_NAC` |
| Texto libre (excluidas) | ~30 | Nombres, direcciones, teléfonos |
| 100 % nulos (excluidas) | 5 | `LUGAR_VIVIRA_ESTUDIANTE`, `MEDIO_ESTUDIO`, `SIT_LABORAL_ASPIRANTE`… |

### Estadísticas descriptivas — Variables numéricas clave

| Variable | N válidos | Media | Desv. est. | Mín | Mediana | Máx | Nulos |
|---|---|---|---|---|---|---|---|
| `ESTRATO_ACTUAL` | 95 | 1.94 | 0.86 | 1 | 2.0 | 4 | 0 |
| `INGRESOS` (COP) | 95 | 14 424 094 | 10 743 494 | 3 000 000 | 9 600 000 | 62 720 415 | 0 |
| `PMATN` (Matemáticas) | 94 | 65.62 | 5.20 | 56 | 65.0 | 89 | 1 (1.1 %) |
| `PINGN` (Inglés) | 94 | 63.10 | 8.63 | 45 | 63.0 | 88 | 1 (1.1 %) |
| `PCRIN` (Lectura Crítica) | 94 | 62.72 | 6.35 | 49 | 63.0 | 100 | 1 (1.1 %) |
| `PCIUN` (Soc. y Ciudadanas) | 94 | 62.34 | 6.74 | 45 | 63.0 | 79 | 1 (1.1 %) |
| `PNATN` (Ciencias Naturales) | 94 | 63.91 | 5.98 | 47 | 64.0 | 100 | 1 (1.1 %) |
| `NIVEL_ED_PADRE` | 74 | 6.70 | 4.13 | 1 | 5.0 | 14 | 21 (22.1 %) |
| `NIVEL_ED_MADRE` | 91 | 7.45 | 3.71 | 2 | 5.0 | 14 | 4 (4.2 %) |

> El puntaje total Saber 11 (suma de los 5 componentes nuevos) presenta media ≈ 317.7 / 500 puntos para la población combinada.

### Distribución de variables categóricas clave

| Variable | Distribución |
|---|---|
| `SEXO` | M: 80 (84.2 %) · F: 15 (15.8 %) |
| `TIPO_PLANTEL` | Público (G): 74 (77.9 %) · Privado (P): 21 (22.1 %) |
| `ZONA_LUGAR_RESIDENCIA` | Urbana (U): 77 (81.1 %) · Rural (R): 18 (18.9 %) |
| `ANOS_REPITIO` | No (N): 78 (82.1 %) · Sí (S): 17 (17.9 %) |
| `SISBEN` | Tiene SISBEN (S): 62 (65.3 %) · No (N): 33 (34.7 %) |

### Valores nulos

- Solo `NIVEL_ED_PADRE` tiene nulos significativos (21 = 22.1 %). **Estrategia:** imputar con la moda o el valor máximo parental.
- Los 5 componentes Saber 11 tienen 1 nulo. **Estrategia:** imputar con la mediana del grupo.
- No hay duplicados en los identificadores de estudiante.

---

## 2. `detalle_materias.xlsx` — Cohorte filtrada (n=2 725 registros · 90 estudiantes)

### Tipos de datos

| Tipo | Columnas |
|---|---|
| Numérico continuo | `DEFINITIVA` |
| Numérico entero | `SEMESTRE`, `CREDITOS`, `CODIGO_MATERIA` |
| Categórico/texto | `MATERIA`, `OBSERVACION`, `PROGRAMA`, `COHORTE` |

> `SEMESTRE` es el nivel del *pénsum* de la materia (1–10), **no** el período calendario. Para medir la actividad cronológica se usa `PERIODO_INSCRIPCION`.

### Estadísticas descriptivas

| Variable | N válidos | Media | Desv. est. | Mín | Mediana | Máx | Nulos |
|---|---|---|---|---|---|---|---|
| `DEFINITIVA` | 2 643 | 3.54 | 0.93 | 0.00 | 3.70 | 5.00 | 82 (3.0 %) |

### Distribución de `OBSERVACION`

| Código | Significado | N | % |
|---|---|---|---|
| N | Normal | 2 338 | 85.8 % |
| O | Homologada | 118 | 4.3 % |
| H | Habilitación | 110 | 4.0 % |
| TG | Trabajo de Grado | 78 | 2.9 % |
| NaN | Sin registro | 65 | 2.4 % |
| C | Cancelada | 15 | 0.6 % |
| V | Vacía | 1 | 0.0 % |

---

## 3. `historial_estados_.xlsx` — Cohorte filtrada (n=579 registros · 97 estudiantes)

### Tipos de datos

Todos los campos son texto/categórico excepto `PERIODO_ESTADO` (string tipo `AAAA-S`).

> **Limitación importante:** el historial **no conserva todos los estados `MATRICULADO`** de los primeros períodos. Por eso la actividad académica real se mide con `detalle_materias.xlsx` y no con este archivo (ver Fase 2 · sección 1.1).

### Distribución de estados

| Estado | N registros | % |
|---|---|---|
| MATRICULADO | 390 | 67.4 % |
| NO REALIZO PAGO | 83 | 14.3 % |
| BAJO RENDIMIENTO | 36 | 6.2 % |
| GRADUADO | 35 | 6.0 % |
| RETIRADO BR | 17 | 2.9 % |
| RETIRO DEFINITIVO VOLUNTARIO | 9 | 1.6 % |
| CANCELADO | 4 | 0.7 % |
| RETIRO POR NO RENOVACION | 4 | 0.7 % |
| RETIRO DEFINITIVO BR | 1 | 0.2 % |

### Estado final por estudiante (clasificación por recencia, n=95)

| Estado final | N | % |
|---|---|---|
| Graduado | 35 | 36.8 % |
| Desertor (con o sin acta formal) | 59 | 62.1 % |
| En formación (activo en 2024-1+) | 1 | 1.1 % |

> Solo 30 de los 59 desertores tienen acta formal de retiro; los otros 29 abandonaron sin acta (rastro único `NO REALIZO PAGO`).

---

## 4. `PROMEDIOS_DE_CARRERA.xlsx` — Cohorte filtrada (n=90)

| Variable | N válidos | Media | Desv. est. | Mín | Mediana | Máx | Nulos |
|---|---|---|---|---|---|---|---|
| `PROMEDIO_CARRERA` | 90 | 3.08 | 0.86 | 0.8 | 3.40 | 4.40 | 0 |

- 38 estudiantes (42.2 %) tienen `PROMEDIO_CARRERA` < 3.0. Sobre la muestra de modelado (89), el target `rendimiento_bajo` queda en 37 positivos (41.6 %).

---

## 5. `promedios_semestre.xlsx` — Cohorte filtrada (n=593 registros · 90 estudiantes)

| Variable | N válidos | Media | Desv. est. | Mín | Mediana | Máx | Nulos |
|---|---|---|---|---|---|---|---|
| `PROMEDIO_SEMESTRE` | 514 | 3.50 | 0.78 | 0.00 | 3.60 | 4.70 | 79 (13.3 %) |

- Los 79 nulos corresponden a periodos de inactividad académica o sin matrícula financiera finalizada.

---

## 6. Resumen global de calidad

| Indicador | Valor |
|---|---|
| Total registros procesados | ≈ 4 082 filas combinadas entre los 5 archivos |
| Filas duplicadas | 0 en los datasets de nivel estudiante |
| Columnas con nulos significativos (> 5 %) | `NIVEL_ED_PADRE` (22.1 %), `PROMEDIO_SEMESTRE` (13.3 %) |
| Integridad del historial | ⚠️ `historial_estados_` no conserva todos los `MATRICULADO`; actividad medida con `detalle_materias` |
| Variables inutilizables (> 95 % nulos) | 5 columnas socioeconómicas de `caracterización` |
| Outliers en notas | Ninguno fuera del rango institucional [0.0, 5.0] |
| Cruce de llaves | Población descriptiva n=95; modelado n=89 (exclusión de 6 estudiantes sin features académicas completas). |
