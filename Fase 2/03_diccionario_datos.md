# Diccionario de Datos — Proyecto Rendimiento Académico
## Universidad de los Llanos · Cohorte 2017-2 · Ingeniería de Sistemas

> Basado en el formulario SIIF y el sistema académico institucional.
> Alcance: variables relevantes para el análisis. Se omiten campos de libre ingreso (nombres, direcciones, teléfonos) y columnas con ≥ 95 % de valores nulos para esta cohorte.

---

## 1. `caracterización.xlsx`

Registro de caracterización socioeconómica y académica previa al ingreso. Fuente: formulario SIIF diligenciado por el aspirante.

**Identificadores**

| Campo | Tipo | Descripción |
|---|---|---|
| `PERIODO_INGRESO` | string | Semestre de ingreso al programa (ej. `2017-2`) |
| `CODIGO_ESTUDIANTIL` | int | Código único del estudiante en el sistema institucional |
| `PROGRAMA` | string | Nombre del programa académico |
| `FACULTAD` | string | Facultad a la que pertenece el programa |

**Datos personales**

| Campo | Tipo | Valores / Descripción |
|---|---|---|
| `SEXO` | categórico | `M` = Masculino · `F` = Femenino |
| `FECHA_NAC` | fecha | Fecha de nacimiento |
| `ESTADO_CIVIL` | categórico | `S`=Soltero · `C`=Casado · `U`=Unión libre · `V`=Viudo · `P`=Divorciado |

**Residencia**

| Campo | Tipo | Valores / Descripción |
|---|---|---|
| `ZONA_LUGAR_RESIDENCIA` | categórico | `U`=Urbana · `R`=Rural |
| `ESTRATO_ACTUAL` | ordinal (1–6) | Estrato socioeconómico de la vivienda |
| `MPIO_ACTUAL` | int | Código DANE del municipio de residencia |

**Educación media**

| Campo | Tipo | Valores / Descripción |
|---|---|---|
| `TIPO_PLANTEL` | categórico | `G`=Público (Gubernamental) · `P`=Privado |
| `ANOS_REPITIO` | categórico | `S`=Sí repitió algún año escolar · `N`=No |
| `VECES` | ordinal | Cuántas veces repitió: `1`=1 · `2`=2 · `3`=3 · `4`=más de 3 |
| `RAZON` | categórico | Razón de repitencia: `1`=Académica · `2`=Personal · `3`=Familiar |

**Prueba Saber 11 — Formato nuevo (desde 2014, escala 0–500 por componente)**

| Campo | Tipo | Descripción |
|---|---|---|
| `PMATN` | numérico | Puntaje Matemáticas |
| `PINGN` | numérico | Puntaje Inglés |
| `PCRIN` | numérico | Puntaje Lectura Crítica |
| `PCIUN` | numérico | Puntaje Sociales y Ciudadanas |
| `PNATN` | numérico | Puntaje Ciencias Naturales |

**Prueba Saber 11 — Formato antiguo (hasta 2013, escala 0–100 por componente)**

| Campo | Descripción |
|---|---|
| `PBIO` | Biología |
| `PMAT` | Matemáticas |
| `PFIL` | Filosofía |
| `PFIS` | Física |
| `PQUI` | Química |
| `PLEN` | Lenguaje |
| `PING` | Inglés |
| `PSOC` | Sociales |

> En la cohorte 2017-2 Ing. Sistemas: 46 estudiantes con formato nuevo, 1 con formato antiguo.

**Seguridad social y SISBEN**

| Campo | Tipo | Valores / Descripción |
|---|---|---|
| `TIPO_AFILIACION` | categórico | `C`=Cotizante · `B`=Beneficiario · `0`=No afiliado |
| `SISBEN` | binario | `S`=Tiene SISBEN · `N`=No tiene |
| `PUNTAJE_SISBEN` | categórico | Tipo de puntaje: `U`=Urbano · `R`=Rural |
| `URBANA_SISBEN` | ordinal (1–4) | Nivel SISBEN urbano: 1 (0–17.5) a 4 (51.01–100) |
| `RURAL_SISBEN` | ordinal (1–6) | Nivel SISBEN rural: 1 (0–11) a 6 (79.01–100) |

**Situación económica y laboral**

| Campo | Tipo | Valores / Descripción |
|---|---|---|
| `INGRESOS` | numérico | Ingresos anuales del hogar en pesos COP |
| `INGRESOS_PROPIOS` | binario | `S`=Tiene ingresos propios · `N`=Depende de terceros |
| `INGRESOS_QUIEN_DEPENDE` | categórico | De quién depende: `1`=Padre · `2`=Madre · `3`=Ambos padres · `4`=Pareja · `5`=Ingresos propios · `6`=Otros |
| `TRANSPORTE` | binario | Requiere apoyo en transporte (checkbox del formulario) |
| `ALIMENTACION` | binario | Requiere apoyo en alimentación |

**Situación familiar**

| Campo | Tipo | Valores / Descripción |
|---|---|---|
| `SITUACION_PADRES` | categórico | `1`=Separados/Divorciados · `2`=Conviven/Conforman hogar · `3`=Conformó nuevo hogar (alguno fallecido) |
| `VIVE_CON` | categórico | Con quién vive actualmente *(inferido)*: `1`=Con ambos padres · `2`=Con uno de los padres · `3`=Con pareja/cónyuge · `4`=Con otros familiares · `5`=Solo/Pensión/Residencia |
| `CRIANZA` | categórico | Quién estuvo a cargo de la crianza *(inferido)*: `1`=Solo padre · `2`=Solo madre · `3`=Otro familiar · `4`=Ambos padres |
| `RELA_FAMILIA` | categórico | Percepción relación familiar: `B`=Buena · `R`=Regular · `M`=Mala |
| `TIENE_HIJOS` | binario | `S`=Sí tiene hijos · `N`=No |
| `PADRE_VIVO` | binario | `S`=Sí · `N`=No |
| `MADRE_VIVA` | binario | `S`=Sí · `N`=No |

**Nivel educativo de los padres** *(escala ordinal, código DANE)*

| Código | Significado |
|---|---|
| `1` | Analfabeta |
| `2` | Primaria incompleta |
| `3` | Primaria completa |
| `4` | Bachillerato incompleto |
| `5` | Bachillerato completo |
| `7` | Técnico incompleto *(código 6 no existe en el sistema)* |
| `8` | Técnico completo |
| `9` | Tecnólogo incompleto |
| `10` | Tecnólogo completo |
| `11` | Universitario incompleto |
| `12` | Universitario completo |
| `13` | Posgrado incompleto |
| `14` | Posgrado completo |

> Aplica a `NIVEL_ED_PADRE` y `NIVEL_ED_MADRE`.

**Ocupación de los padres**

| Código | Significado |
|---|---|
| `1` | Empleado de planta |
| `2` | Empleado contrato a término fijo |
| `3` | Prestación de servicios |
| `4` | Empresario/dueño de negocio |
| `5` | Trabajo informal |
| `7` | Estudiante |

> Aplica a `OCUPACION_PADRE` y `OCUPACION_MADRE`.

**Grupos de vulnerabilidad y condición especial**

| Campo | Tipo | Valores / Descripción |
|---|---|---|
| `INDIGENA` | binario | `S`=Sí · `N`=No |
| `AFRODESCENDIENTE` | binario | `S`=Sí · `N`=No |
| `VICTIMA` | binario | `S`=Víctima del conflicto armado · `N`=No |
| `TIPO_DISCAPACIDAD` | categórico | `9`=Ninguna · `5`=Sensorial · `6`=Motriz · `7`=Cognitiva |
| `POBLACION` | categórico | `1`=Ninguna · `2`=Madre gestante · `3`=Cabeza de familia · `4`=Hijo cabeza fam. · `5`=Grupo étnico · `6`=Víctima conflicto |

**Actividades extracurriculares**

| Campo | Tipo | Descripción |
|---|---|---|
| `DEPORTE` | binario | `S`=Practica deporte competitivo · `N`=No |
| `ARTE` | binario | `S`=Practica arte competitivo · `N`=No |
| `LECTURA` | binario | `S`=Hábito de lectura · `N`=No |
| `CUANTOS_LIBROS` | numérico | Libros leídos en el último año |

---

## 2. `detalle_materias.xlsx`

Registro de todas las materias cursadas por los estudiantes, con su calificación definitiva.

| Campo | Tipo | Descripción |
|---|---|---|
| `COHORTE` | string | Semestre de ingreso del estudiante (ej. `2017-2`) |
| `CODIGO_INST` | int | Código del estudiante |
| `PROGRAMA` | string | Programa académico |
| `PERIODO_INSCRIPCION` | string | Semestre en que cursó la materia (ej. `2018-1`) |
| `CODIGO_MATERIA` | int | Código institucional de la materia |
| `MATERIA` | string | Nombre de la materia |
| `SEMESTRE` | int | Semestre del plan de estudios al que pertenece la materia (1–10) |
| `CREDITOS` | int | Número de créditos académicos |
| `DEFINITIVA` | numérico (0–5) | Nota definitiva obtenida |
| `OBSERVACION` | categórico | Tipo de registro académico — ver tabla abajo |

**Valores de `OBSERVACION`**

| Código | Significado | Incluir en análisis de notas |
|---|---|---|
| `N` | Normal (primera vez o repetición estándar) | ✅ Sí |
| `H` | Habilitación (examen de recuperación) | ✅ Sí |
| `F` | Pérdida por fallas (inasistencia) | ✅ Sí |
| `R` | No aprobada (sin habilitación) | ✅ Sí |
| `TG` | Trabajo de Grado | ✅ Sí (si aplica) |
| `O` | Homologada (convalidada de otro programa) | ❌ No (excluir) |
| `I` | Intercambio académico | ❌ No (excluir) |
| `C` | Cancelada | ❌ No (sin nota válida) |
| `E` | En curso actualmente | ❌ No (sin nota definitiva) |

> **Nota de procesamiento:** Para calcular promedios por materia se toma la **última nota registrada** por estudiante-materia (ordenado por `PERIODO_INSCRIPCION` descendente) y se excluyen los registros con `OBSERVACION` ∈ {O, I, C, E}.

---

## 3. `historial_estados_.xlsx`

Registro del estado académico-administrativo del estudiante por cada semestre.

| Campo | Tipo | Descripción |
|---|---|---|
| `COHORTE` | string | Semestre de ingreso |
| `CODIGO_INST` | int | Código del estudiante |
| `PROGRAMA` | string | Programa académico |
| `PERIODO_ESTADO` | string | Semestre al que corresponde el estado |
| `ESTADO` | categórico | Estado en ese período — ver tabla abajo |

**Valores de `ESTADO`**

| Estado | Significado | Categoría |
|---|---|---|
| `MATRICULADO` | Matriculado activo | Activo |
| `GRADUADO` | Grado obtenido | Egreso exitoso |
| `NO REALIZO PAGO` | No pagó matrícula | Inactividad |
| `BAJO RENDIMIENTO` | Sanción académica por bajo promedio | Riesgo |
| `RETIRADO BR` | Retirado por bajo rendimiento | Deserción |
| `CANCELADO` | Cancelación de matrícula | Inactividad |
| `RETIRO POR NO RENOVACION DE MATRICULA` | No renovó matrícula | Deserción |
| `RETIRO DEFINITIVO VOLUNTARIO DEL PROGRAMA` | Retiro voluntario | Deserción |
| `RETIRO DEFINITIVO DEL PROGRAMA CON BAJO RENDIMIENTO` | Retiro por rendimiento | Deserción |

> **Nota:** 3 estudiantes (160004097, 160004098, 160004099) aparecen solo en este archivo con único estado `NO REALIZO PAGO`. No forman parte de la **población** de análisis (n=95).

---

## 4. `PROMEDIOS_DE_CARRERA.xlsx`

Promedio acumulado de toda la carrera por estudiante, calculado por el sistema institucional.

| Campo | Tipo | Descripción |
|---|---|---|
| `COHORTE` | string | Semestre de ingreso |
| `CODIGO_INST` | int | Código del estudiante |
| `PROGRAMA` | string | Programa académico |
| `PENSUM` | int | Código del plan de estudios vigente |
| `FACULTAD` | string | Facultad |
| `PROMEDIO_CARRERA` | numérico (0–5) | Promedio ponderado acumulado de todas las materias cursadas |

> En la cohorte 2017-2 Ing. Sistemas: media = 3.09, mediana = 3.40, rango [0.90 – 4.40].

---

## 5. `promedios_semestre.xlsx`

Promedio por semestre cursado para cada estudiante.

| Campo | Tipo | Descripción |
|---|---|---|
| `COHORTE` | string | Semestre de ingreso |
| `CODIGO_INST` | int | Código del estudiante |
| `PROGRAMA` | string | Programa académico |
| `PERIODO_INSCRIPCION` | string | Semestre al que corresponde el promedio |
| `PROMEDIO_SEMESTRE` | numérico (0–5) | Promedio de ese semestre en particular |

> `PROMEDIO_SEMESTRE` tiene 12 % de valores nulos globalmente, correspondientes a semestres donde el estudiante no estuvo matriculado activo.

---

## Notas generales de calidad de datos

| Aspecto | Detalle |
|---|---|
| Duplicados | 0 filas duplicadas en todos los datasets |
| Nulos en identificadores | 0 — todos los registros tienen código y programa |
| `NOMBRE2` / `APELLIDO2` | ~13 % nulos en todos los archivos (segundo nombre/apellido opcional) |
| Columnas 100 % nulas para esta cohorte | `LUGAR_VIVIRA_ESTUDIANTE`, `TIPO_DEPENDIENTE_ASPIRANTE`, `MEDIO_ESTUDIO`, `SIT_LABORAL_ASPIRANTE`, `DEPENDE_ECONOMICAMENTE` — no utilizables |
| Escala de notas | 0.0 a 5.0; umbral de aprobación institucional: **3.0** |
| Código 6 nivel educativo | No existe en el sistema (salto de 5 a 7) |
| Campos inferidos | `VIVE_CON` y `CRIANZA` no están documentados en el SIIF; sus etiquetas se infieren por contexto |
