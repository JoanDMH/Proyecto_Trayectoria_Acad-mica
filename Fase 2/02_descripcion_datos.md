# Reporte de Descripción de Datos
## CRISP-DM Fase 2 · Universidad de los Llanos · Cohorte 2017-2 · Ingeniería de Sistemas

---

## 1. `caracterización.xlsx` — Variables analíticas (cohorte filtrada: n=47)

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
| `ESTRATO_ACTUAL` | 47 | 1.94 | 0.86 | 1 | 2 | 4 | 0 |
| `INGRESOS` (COP) | 47 | 14 424 094 | 10 743 494 | 3 000 000 | 9 600 000 | 62 720 415 | 0 |
| `PMATN` (Matemáticas) | 46 | 65.62 | 5.20 | 56 | 65 | 89 | 1 |
| `PINGN` (Inglés) | 46 | 63.10 | 8.63 | 45 | 63 | 88 | 1 |
| `PCRIN` (Lectura Crítica) | 46 | 62.72 | 6.35 | 49 | 63 | 100 | 1 |
| `PCIUN` (Soc. y Ciudadanas) | 46 | 62.34 | 6.74 | 45 | 63 | 79 | 1 |
| `PNATN` (Ciencias Naturales) | 46 | 63.91 | 5.98 | 47 | 64 | 100 | 1 |
| `NIVEL_ED_PADRE` | 38 | — | — | 2 | 5 | 14 | 9 (19.1 %) |
| `NIVEL_ED_MADRE` | 45 | — | — | 2 | 5 | 14 | 2 (4.3 %) |

> El puntaje total Saber 11 (suma de los 5 componentes) presenta media ≈ 317.7 / 500 puntos para la cohorte.

### Distribución de variables categóricas clave

| Variable | Distribución |
|---|---|
| `SEXO` | M: 41 (87 %) · F: 6 (13 %) |
| `TIPO_PLANTEL` | Público (G): 37 (79 %) · Privado (P): 10 (21 %) |
| `ZONA_LUGAR_RESIDENCIA` | Urbana (U): 39 (83 %) · Rural (R): 8 (17 %) |
| `ANOS_REPITIO` | No: 38 (81 %) · Sí: 9 (19 %) |
| `SISBEN` | Tiene SISBEN: 34 (72 %) · No: 13 (28 %) |
| `SITUACION_PADRES` | Separados: 24 (52 %) · Conviven: 18 (39 %) · Nuevo hogar: 3 (6 %) |
| `RELA_FAMILIA` | Buena (B): 42 (91 %) · Regular (R): 5 (9 %) |
| `INGRESOS_PROPIOS` | No: 39 (83 %) · Sí: 8 (17 %) |

### Valores nulos

- Solo `NIVEL_ED_PADRE` tiene nulos significativos (9 = 19.1 %). **Estrategia:** imputar con la moda de la variable (bachillerato completo, código 5).
- Los 5 componentes Saber 11 tienen 1 nulo (estudiante con formato antiguo). **Estrategia:** imputar con la mediana del grupo.
- No hay duplicados.

---

## 2. `detalle_materias.xlsx` — Cohorte filtrada (n=1 183 registros)

### Tipos de datos

| Tipo | Columnas |
|---|---|
| Numérico continuo | `DEFINITIVA` |
| Numérico entero | `SEMESTRE`, `CREDITOS`, `CODIGO_MATERIA` |
| Categórico/texto | `MATERIA`, `OBSERVACION`, `PROGRAMA`, `COHORTE`, nombres |

### Estadísticas descriptivas

| Variable | N válidos | Media | Desv. est. | Mín | Mediana | Máx | Nulos |
|---|---|---|---|---|---|---|---|
| `DEFINITIVA` | 1 150 | 3.46 | 1.01 | 0.00 | 3.70 | 5.00 | 33 (2.8 %) |
| `SEMESTRE` | 1 183 | 4.26 | 2.91 | 1 | 4 | 10 | 0 |
| `CREDITOS` | 1 183 | 3.17 | 0.91 | 0 | 3 | 4 | 0 |

### Distribución de `OBSERVACION`

| Código | Significado | N | % |
|---|---|---|---|
| N | Normal | 1 002 | 84.7 % |
| O | Homologada | 54 | 4.6 % |
| H | Habilitación | 48 | 4.1 % |
| NaN | Sin registro | 35 | 3.0 % |
| TG | Trabajo de Grado | 33 | 2.8 % |
| C | Cancelada | 11 | 0.9 % |

> Los 33 nulos en `DEFINITIVA` corresponden mayoritariamente a registros `NaN` en `OBSERVACION` (materias sin nota aún registrada).

---

## 3. `historial_estados_.xlsx` — Cohorte filtrada (n=248 registros, 49 estudiantes)

### Tipos de datos

Todos los campos son texto/categórico excepto `PERIODO_ESTADO` (string tipo `AAAA-S`).

### Distribución de estados

| Estado | N registros | % |
|---|---|---|
| MATRICULADO | 147 | 59.3 % |
| NO REALIZO PAGO | 49 | 19.8 % |
| BAJO RENDIMIENTO | 21 | 8.5 % |
| GRADUADO | 14 | 5.6 % |
| RETIRADO BR | 10 | 4.0 % |
| CANCELADO | 3 | 1.2 % |
| RETIRO POR NO RENOVACION | 2 | 0.8 % |
| RETIRO DEFINITIVO VOLUNTARIO | 1 | 0.4 % |
| RETIRO DEFINITIVO BR | 1 | 0.4 % |

### Estado final por estudiante (último registro)

| Estado final | N | % |
|---|---|---|
| Graduado | 14 | 28.6 % |
| Retirado (diversas causas) | 35 | 71.4 % |

- 0 nulos en todos los campos de este dataset.

---

## 4. `PROMEDIOS_DE_CARRERA.xlsx` — Cohorte filtrada (n=46)

| Variable | N válidos | Media | Desv. est. | Mín | P25 | Mediana | P75 | Máx | Nulos |
|---|---|---|---|---|---|---|---|---|---|
| `PROMEDIO_CARRERA` | 46 | 3.09 | 0.85 | 0.90 | 2.60 | 3.40 | 3.70 | 4.40 | 0 |

- 19 estudiantes (41 %) tienen `PROMEDIO_CARRERA` < 3.0 → definidos como **rendimiento bajo**.
- Distribución ligeramente sesgada a la izquierda; la mediana (3.40) supera la media (3.09) por los casos extremos bajos.

---

## 5. `promedios_semestre.xlsx` — Cohorte filtrada (n=262 registros, 46 estudiantes)

| Variable | N válidos | Media | Desv. est. | Mín | Mediana | Máx | Nulos |
|---|---|---|---|---|---|---|---|
| `PROMEDIO_SEMESTRE` | 229 | 3.42 | 0.83 | 0.30 | 3.60 | 4.70 | 33 (12.6 %) |

- Los 33 nulos corresponden a semestres donde el estudiante no estuvo matriculado activo (estado `NO REALIZO PAGO` o similar).
- Rango de períodos cubiertos: 2017-2 a 2022-2.

---

## 6. Resumen global de calidad

| Indicador | Valor |
|---|---|
| Total registros analizados (cohorte filtrada) | 2 150 filas entre los 5 archivos |
| Filas duplicadas | 0 en todos los datasets |
| Columnas con nulos significativos (> 5 %) | `NIVEL_ED_PADRE` (19 %), `PROMEDIO_SEMESTRE` (12.6 %) |
| Variables inutilizables (> 95 % nulos) | 5 columnas de `caracterización` |
| Outliers en notas | Ninguno fuera del rango institucional [0, 5] |
| Inconsistencias de clave | 3 estudiantes extra en historial (resuelto: excluidos de población base) |
