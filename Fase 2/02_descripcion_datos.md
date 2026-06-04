# Reporte de Descripción de Datos
## CRISP-DM Fase 2 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. `caracterización.xlsx` — Variables analíticas (cohorte filtrada: n=89)

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
| `ESTRATO_ACTUAL` | 89 | 1.92 | 0.86 | 1 | 2.0 | 4 | 0 |
| `INGRESOS` (COP) | 89 | 14 211 639 | 10 723 621 | 3 000 000 | 9 600 000 | 62 720 415 | 0 |
| `PMATN` (Matemáticas) | 88 | 65.88 | 5.23 | 56 | 65.0 | 89 | 1 (1.1 %) |
| `PINGN` (Inglés) | 88 | 63.14 | 8.82 | 45 | 63.0 | 88 | 1 (1.1 %) |
| `PCRIN` (Lectura Crítica) | 88 | 62.75 | 6.50 | 49 | 63.0 | 100 | 1 (1.1 %) |
| `PCIUN` (Soc. y Ciudadanas) | 88 | 62.18 | 6.78 | 45 | 63.0 | 79 | 1 (1.1 %) |
| `PNATN` (Ciencias Naturales) | 88 | 63.88 | 6.17 | 47 | 63.5 | 100 | 1 (1.1 %) |
| `NIVEL_ED_PADRE` | 70 | 6.81 | 4.13 | 1 | 5.0 | 14 | 19 (21.3 %) |
| `NIVEL_ED_MADRE` | 85 | 7.44 | 3.71 | 2 | 5.0 | 14 | 4 (4.5 %) |

> El puntaje total Saber 11 (suma de los 5 componentes) presenta media ≈ 317.8 / 500 puntos para la muestra combinada.

### Distribución de variables categóricas clave

| Variable | Distribución |
|---|---|
| `SEXO` | M: 74 (83.1 %) · F: 15 (16.9 %) |
| `TIPO_PLANTEL` | Público (G): 70 (78.7 %) · Privado (P): 19 (21.3 %) |
| `ZONA_LUGAR_RESIDENCIA` | Urbana (U): 72 (80.9 %) · Rural (R): 17 (19.1 %) |
| `ANOS_REPITIO` | No (N): 74 (83.1 %) · Sí (S): 15 (16.9 %) |
| `SISBEN` | Tiene SISBEN (S): 58 (65.2 %) · No (N): 31 (34.8 %) |

### Valores nulos

- Solo `NIVEL_ED_PADRE` tiene nulos significativos (19 = 21.3 %). **Estrategia:** imputar con la moda o el valor máximo parental.
- Los 5 componentes Saber 11 tienen 1 nulo. **Estrategia:** imputar con la mediana del grupo.
- No hay duplicados en los identificadores de estudiante.

---

## 2. `detalle_materias.xlsx` — Cohorte filtrada (n=2 719 registros)

### Tipos de datos

| Tipo | Columnas |
|---|---|
| Numérico continuo | `DEFINITIVA` |
| Numérico entero | `SEMESTRE`, `CREDITOS`, `CODIGO_MATERIA` |
| Categórico/texto | `MATERIA`, `OBSERVACION`, `PROGRAMA`, `COHORTE` |

### Estadísticas descriptivas

| Variable | N válidos | Media | Desv. est. | Mín | Mediana | Máx | Nulos |
|---|---|---|---|---|---|---|---|
| `DEFINITIVA` | 2 637 | 3.54 | 0.93 | 0.00 | 3.70 | 5.00 | 82 (3.0 %) |

### Distribución de `OBSERVACION`

| Código | Significado | N | % |
|---|---|---|---|
| N | Normal | 2 332 | 85.8 % |
| O | Homologada | 118 | 4.3 % |
| H | Habilitación | 110 | 4.0 % |
| TG | Trabajo de Grado | 78 | 2.9 % |
| NaN | Sin registro | 65 | 2.4 % |
| C | Cancelada | 15 | 0.6 % |
| V | Vacía | 1 | 0.0 % |

---

## 3. `historial_estados_.xlsx` — Cohorte filtrada (n=561 registros)

### Tipos de datos

Todos los campos son texto/categórico excepto `PERIODO_ESTADO` (string tipo `AAAA-S`).

### Distribución de estados

| Estado | N registros | % |
|---|---|---|
| MATRICULADO | 390 | 69.5 % |
| NO REALIZO PAGO | 69 | 12.3 % |
| GRADUADO | 35 | 6.2 % |
| BAJO RENDIMIENTO | 33 | 5.9 % |
| RETIRADO BR | 17 | 3.0 % |
| RETIRO DEFINITIVO VOLUNTARIO | 8 | 1.4 % |
| CANCELADO | 4 | 0.7 % |
| RETIRO POR NO RENOVACION | 4 | 0.7 % |
| RETIRO DEFINITIVO BR | 1 | 0.2 % |

### Estado final por estudiante (último registro por estudiante)

| Estado final | N | % |
|---|---|---|
| Graduado | 35 | 39.3 % |
| Retirado / Inactivo (diversas causas) | 54 | 60.7 % |

---

## 4. `PROMEDIOS_DE_CARRERA.xlsx` — Cohorte filtrada (n=89)

| Variable | N válidos | Media | Desv. est. | Mín | Mediana | Máx | Nulos |
|---|---|---|---|---|---|---|---|
| `PROMEDIO_CARRERA` | 89 | 3.09 | 0.86 | 0.8 | 3.40 | 4.40 | 0 |

- 37 estudiantes (41.6 %) tienen `PROMEDIO_CARRERA` < 3.0 → definidos como **rendimiento bajo** (target).

---

## 5. `promedios_semestre.xlsx` — Cohorte filtrada (n=592 registros)

| Variable | N válidos | Media | Desv. est. | Mín | Mediana | Máx | Nulos |
|---|---|---|---|---|---|---|---|
| `PROMEDIO_SEMESTRE` | 513 | 3.50 | 0.78 | 0.00 | 3.60 | 4.70 | 79 (13.3 %) |

- Los 79 nulos corresponden a periodos de inactividad académica o sin matrícula financiera finalizada.

---

## 6. Resumen global de calidad (n=89)

| Indicador | Valor |
|---|---|
| Total registros procesados | 3 961 filas combinadas entre los 5 archivos |
| Filas duplicadas | 0 en los datasets de nivel estudiante |
| Columnas con nulos significativos (> 5 %) | `NIVEL_ED_PADRE` (21.3 %), `PROMEDIO_SEMESTRE` (13.3 %) |
| Variables inutilizables (> 95 % nulos) | 5 columnas socioeconómicas de `caracterización` |
| Outliers en notas | Ninguno fuera del rango institucional [0.0, 5.0] |
| Cruce de llaves | Exclusión metodológica exitosa de 5 estudiantes con promedio acumulado nulo. |
