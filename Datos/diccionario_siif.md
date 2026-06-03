# Diccionario de Datos — Formulario SIIF

---

## Paso 1: Identificación Personal

### Tipo de Documento de Identificación
| Campo | Valor |
|---|---|
| `TIPO_IDENTIFICACION` | |
| Cédula de Ciudadanía | `C` |
| Cédula de Extranjería | `E` |
| Tarjeta de Identidad | `T` |

### Datos de Contacto

| Campo | Descripción |
|---|---|
| `APELLIDO_1` | Primer apellido (ingreso de datos) |
| `APELLIDO_2` | Segundo apellido (ingreso de datos) |
| `NOMBRE` | Nombre (ingreso de datos) |
| `TELEFONOS` | Número de teléfono fijo (ingreso de datos) |
| `CELULAR` | Número de celular (ingreso de datos) |
| `E_MAIL` | Correo electrónico principal (ingreso de datos) |
| `E_MAIL_SECUNDARIO` | Correo electrónico secundario (ingreso de datos) |
| `SNP_ICFES` | Código SNP (ingreso de datos) |

### ICFES

| Campo | Valor |
|---|---|
| `TIPO_PRESENTO_ICFES` | Tipo de documento con el que presentó el ICFES |
| Cédula de Ciudadanía | `C` |
| Cédula de Extranjería | `E` |
| Tarjeta de Identidad | `T` |
| `FECHA_ICFES` | Año de presentación (ingreso de datos) |

---

## Paso 2: Información Personal y de Residencia

### Expedición del Documento

| Campo | Valor |
|---|---|
| `PAIS_EXPEDICION` | País de expedición |
| Colombia | `Colombia` |
| Venezuela | `Venezuela` |
| Ecuador | `Ecuador` |
| `DEPARTAMENTO_EXPEDICION` | Departamento de expedición (valor variable) |
| `MUNICIPIO` | Municipio de expedición (valor variable) |

### Datos Personales

| Campo | Valor |
|---|---|
| `RH` | Tipo sanguíneo (valor variable) |
| `SEXO` | Género |
| Femenino | `F` |
| Masculino | `M` |
| `Libreta Militar` | Número de libreta militar (ingreso de datos) |
| `Distrito Militar` | Distrito militar (ingreso de datos) |
| `FECHA_NAC` | Fecha de nacimiento (ingreso de datos) |

### Nacimiento

| Campo | Valor |
|---|---|
| `PAIS_NACIMIENTO` | País de nacimiento |
| Colombia | `Colombia` |
| Venezuela | `Venezuela` |
| Ecuador | `Ecuador` |
| `DEPARTAMENTO_NACIMIENTO` | Departamento de nacimiento (valor variable) |
| `MPIO_NACIM` | Municipio de nacimiento (valor variable) |

### Estado Civil

| Campo | Valor |
|---|---|
| `ESTADO_CIVIL` | |
| Soltero(a) | `S` |
| Casado(a) | `C` |
| Unión libre | `U` |
| Viudo(a) | `V` |
| Divorciado(a) | `P` |

### Domicilio

| Campo | Valor |
|---|---|
| `PAIS_DOMICILIO` | País de domicilio |
| Colombia | `Colombia` |
| Venezuela | `Venezuela` |
| Ecuador | `Ecuador` |
| `DEPARTAMENTO_DOMICILIO` | Departamento de domicilio (valor variable) |
| `MUNICIPIO_DOMICILIO` | Municipio de domicilio (valor variable) |
| `DIRECCION` | Dirección (ingreso de datos) |
| `BARRIO` | Barrio (ingreso de datos) |
| `ZONA_LUGAR_RESIDENCIA` | Zona de residencia |
| Rural | `R` |
| Urbana | `U` |

### Estrato

| Campo | Valor |
|---|---|
| `ESTRATO` | |
| 1 | `1` |
| 2 | `2` |
| 3 | `3` |
| 4 | `4` |
| 5 | `5` |

### Seguridad Social y SISBEN

| Campo | Valor |
|---|---|
| `TIPO_AFILIACION` | Afiliación al Sistema de Seguridad Social (Salud) |
| Cotizante | `C` |
| Beneficiario | `B` |
| No estoy afiliado | `0` |
| `SISBEN` | Afiliado al SISBEN |
| Sí | `S` |
| No | `N` |
| `PUNTAJE_SISBEN` | Tipo de puntaje SISBEN |
| Rural | `R` |
| Urbana | `U` |

#### Nivel SISBEN Rural

| Campo | Valor |
|---|---|
| `RURAL_SISBEN` | |
| 01 – 11.00 → nivel 1 | `1` |
| 11.01 – 22.00 → nivel 2 | `2` |
| 22.01 – 43.00 → nivel 3 | `3` |
| 43.01 – 65.00 → nivel 4 | `4` |
| 65.01 – 79.00 → nivel 5 | `5` |
| 79.01 – 100.00 → nivel 6 | `6` |

#### Nivel SISBEN Urbana

| Campo | Valor |
|---|---|
| `URBANA_SISBEN` | |
| 0 – 17.50 → nivel 1 | `1` |
| 17.51 – 32.00 → nivel 2 | `2` |
| 32.01 – 51.00 → nivel 3 | `3` |
| 51.01 – 100.00 → niveles 4 a 6 | `4` |

---

## Paso 3: Educación Previa

| Campo | Valor |
|---|---|
| `COLEGIO` | Código ICFES de la institución donde se graduó (ingreso de datos) |
| `ANO_GRADO` | Año de graduación (ingreso de datos) |

### Modalidad de grado en educación media

| Campo | Valor |
|---|---|
| `ESPECIALIDAD` | |
| Bachillerato académico | `A` |
| Bachillerato técnico | `T` |
| Bachiller normalista | `M` |
| Bachiller pedagógico | `P` |

### Colegio

| Campo | Valor |
|---|---|
| `PAIS_COLEGIO` | País del colegio |
| Colombia | `Colombia` |
| Venezuela | `Venezuela` |
| Ecuador | `Ecuador` |
| `DEPTO_COLEGIO` | Departamento del colegio (valor variable) |
| `MPIO_COLEGIO` | Municipio del colegio (valor variable) |

### Tipología y jornada

| Campo | Valor |
|---|---|
| `TIPO_PLANTEL` | Tipología del plantel |
| Privado | `P` |
| Público | `G` |
| `MODALIDAD` | Jornada de graduación |
| Diurna | `D` |
| Nocturna | `N` |

### Repitencia escolar

| Campo | Valor |
|---|---|
| `ANOS_REPITIO` | ¿Repitió algún año en el colegio? |
| Sí | `S` |
| No | `N` |
| `VECES` | Cuántas veces repitió |
| 1 | `1` |
| 2 | `2` |
| 3 | `3` |
| Más de 3 | `4` |
| `RAZON` | Razón principal de la repitencia |
| Dificultades de tipo académico | `1` |
| Dificultades de tipo personal | `2` |
| Dificultades de tipo familiar | `3` |

### Estudios anteriores

| Campo | Valor |
|---|---|
| `ESTUDIOS_ANTES` | Estudios realizados después del bachillerato |
| Técnico | `T` |
| Tecnológico | `G` |
| Universitario | `U` |
| No | `N` |
| `PROGRAMA_ESTUDIO_ANTERIOR` | Nombre de la carrera o programa (ingreso de datos) |
| `GRADUADO_ESTUDIO_ANTERIOR` | ¿Se graduó? |
| Sí | `S` |
| No | `N` |
| `RAZON_ANT` | Razón por la que no se graduó |
| Dificultades de tipo académico | `1` |
| Dificultades de tipo personal | `2` |
| Dificultades de tipo familiar | `3` |
| Dificultades de tipo económico | `4` |
| `NUM_SEM_ANTERIORES` | Cuántos semestres cursó (1 a 10) |

---

## Paso 4: Condiciones Especiales y Población

### Necesidades Educativas Especiales (NEE)

| Campo | Valor |
|---|---|
| `TIPO_DISCAPACIDAD` | |
| Ninguna | `9` |
| Diversidad sensorial | `5` |
| Diversidad motriz | `6` |
| Diversidad cognitiva | `7` |

#### Tipo sensorial (`SENSORIAL_TIPO`)

| Valor | Código |
|---|---|
| Auditiva | `1` |
| Visual | `2` |
| Mixta | `3` |

#### Auditiva (`AUDITIVA`)

| Valor | Código |
|---|---|
| Sordo | `1` |
| Hipoacúsico | `2` |

#### Visual (`VISUAL`)

| Valor | Código |
|---|---|
| Ceguera | `1` |
| Baja visión | `2` |

#### Mixta (`MIXTA`)

| Valor | Código |
|---|---|
| Sordo–Ciego | `1` |
| Discapacidad cognitiva–Ceguera | `2` |
| Otros | `3` |

#### Motriz (`MOTRIZ`)

| Valor | Código |
|---|---|
| Monoplejia | `1` |
| Diplejia | `2` |
| Triplejia | `3` |
| Hemiplejia | `4` |
| Cuadriplejia | `5` |

#### Cognitiva (`COGNITIVA`)

| Valor | Código |
|---|---|
| En condición de discapacidad cognitiva | `1` |
| Con capacidades y/o talentos excepcionales | `2` |

### Grupo Poblacional

| Campo | Valor |
|---|---|
| `POBLACION` | |
| Ninguna | `1` |
| Madres gestantes | `2` |
| Madres/padres cabeza de familia | `3` |
| Hijos de madre/padre cabeza de familia | `4` |
| Grupos étnicos | `5` |
| Población víctima del conflicto armado | `6` |

#### Condición étnica (`CONDICION_ETNICA`)

| Valor | Código |
|---|---|
| Afrocolombiano o Afrodescendiente | `1` |
| Indígena | `2` |
| Raizal (Archipiélago de San Andrés y Providencia) | `3` |
| Gitano o Romano | `4` |

#### Tipo de victimización (`VICTIMA`)

| Valor | Código |
|---|---|
| Víctimas de asesinatos | `1` |
| Víctimas de masacres | `2` |
| Secuestros | `3` |
| Desaparición forzada | `4` |
| Tortura | `5` |
| Delitos contra la libertad e integridad sexual | `6` |
| Minas antipersonales, municiones sin explotar | `7` |
| Vinculación forzada a actividades del conflicto | `8` |
| Actos terroristas | `9` |
| Atentados | `10` |
| Combates, enfrentamientos y hostigamientos | `11` |
| Abandono o despojo forzado de tierras | `12` |
| Población en situación de desplazamiento forzado | `13` |

### Condiciones territoriales y deportivas

| Campo | Valor |
|---|---|
| `DEPTO_NO_IES` | ¿Proviene de depto. sin IES? Sí `S` / No `N` |
| `MPIO_DIFICIL_ACCESO` | ¿Proviene de municipio de difícil acceso? Sí `S` / No `N` |
| `MPIO_PROBLEMA` | ¿Proviene de municipio con problemas de orden público? Sí `S` / No `N` |
| `DEPORTE` | ¿Practica disciplina deportiva competitiva? Sí `S` / No `N` |

#### Disciplina deportiva (`CUAL_DEPORTE`)

| Valor | Código |
|---|---|
| Fútbol | `1` |
| Baloncesto | `2` |
| Voleibol | `3` |
| Natación | `4` |
| Otro | `5` |

### Arte y lectura

| Campo | Valor |
|---|---|
| `ARTE` | ¿Practica disciplina artística competitiva? Sí `S` / No `N` |

#### Disciplina artística (`CUAL_ARTE`)

| Valor | Código |
|---|---|
| Música | `1` |
| Danza | `2` |
| Teatro | `3` |
| Artes Plásticas | `4` |
| Otro | `5` |
| Especificar otro | ingreso de datos |

| Campo | Valor |
|---|---|
| `LECTURA` | ¿Practica el hábito de la lectura? Sí `S` / No `N` |
| `CUANTOS_LIBROS` | Cuántos libros (ingreso de datos) |

---

## Paso 5: Situación Económica y Laboral

| Campo | Valor |
|---|---|
| `INGRESOS_PROPIOS` | ¿Depende de ingresos propios? Sí `S` / No `N` |
| `LABORANDO` | ¿Se encuentra laborando? Sí `S` / No `N` |

### Tipo de empleo (`EMPLEO`)

| Valor | Código |
|---|---|
| Empleado de planta | `1` |
| Empleado con contrato a término fijo | `2` |
| Empleado por prestación de servicios | `3` |
| Empresario independiente o dueño de negocio | `4` |
| Trabajo informal | `5` |
| Otro | `6` |
| Especificar otro (`OTRO_EMPLEO`) | ingreso de datos |

### Dependencia económica (`INGRESOS_QUIEN_DEPENDE`)

| Valor | Código |
|---|---|
| Padre | `1` |
| Madre | `2` |
| Ambos padres | `3` |
| Pareja | `4` |
| Ingresos propios | `5` |
| Otros | `6` |

### Apoyo financiero

| Campo | Valor |
|---|---|
| `APOYO_FINANCIERO` | ¿Requiere apoyo económico para matrícula? Sí `S` / No `N` |
| `TRANSPORTE` | Requiere apoyo en transporte (checkbox) |
| `ALIMENTACION` | Requiere apoyo en alimentación (checkbox) |
| `COSTO` | Requiere apoyo en costos (checkbox) |
| `OTRO_TIPO_APOYO` | Otro tipo de apoyo (checkbox) |
| `CUAL_APOYO` | Especificar otro apoyo (ingreso de datos) |

---

## Paso 6: Información Familiar

| Campo | Valor |
|---|---|
| `ACUDIENTE` | Nombre del acudiente (ingreso de datos) |
| `TELEFONO_ACU` | Teléfono de contacto del acudiente (ingreso de datos) |
| `NOMBRE_PADRE` | Nombre del padre (ingreso de datos) |

### Padre

| Campo | Valor |
|---|---|
| `TIPO_IDENTIFICACION_PADRE` | Tipo de documento del padre |
| Cédula de Ciudadanía | `C` |
| Cédula de Extranjería | `E` |
| Tarjeta de Identidad | `T` |
| `CEDULA_PADRE` | Número de documento del padre (ingreso de datos) |

#### Ocupación del padre (`OCUPACION_PADRE`)

| Valor | Código |
|---|---|
| Empleado de planta | `1` |
| Empleado con contrato a término fijo | `2` |
| Empleado por prestación de servicios | `3` |
| Empresario independiente o dueño de negocio | `4` |
| Trabajo informal | `5` |
| Estudiante | `7` |

#### Nivel educativo del padre (`NIVEL_EDUC_PADRE`)

| Valor | Código |
|---|---|
| Analfabeta | `1` |
| Primaria incompleta | `2` |
| Primaria completa | `3` |
| Bachillerato incompleto | `4` |
| Bachillerato completo | `5` |
| Técnico incompleto | `7` |
| Técnico completo | `8` |
| Tecnólogo incompleto | `9` |
| Tecnólogo completo | `10` |
| Universitario incompleto | `11` |
| Universitario completo | `12` |
| Posgrado incompleto | `13` |
| Posgrado completo | `14` |

| Campo | Valor |
|---|---|
| `PADRE_VIVO` | ¿El padre vive actualmente? Sí `S` / No `N` |

### Madre

| Campo | Valor |
|---|---|
| `NOMBRE_MADRE` | Nombre de la madre (ingreso de datos) |
| `TIPO_IDENTIFICACION_MADRE` | Tipo de documento de la madre |
| Cédula de Ciudadanía | `C` |
| Cédula de Extranjería | `E` |
| Tarjeta de Identidad | `T` |
| `CEDULA_MADRE` | Número de documento de la madre (ingreso de datos) |

#### Ocupación de la madre (`OCUPACION_MADRE`)

| Valor | Código |
|---|---|
| Empleado de planta | `1` |
| Empleado con contrato a término fijo | `2` |
| Empleado por prestación de servicios | `3` |
| Empresario independiente o dueño de negocio | `4` |
| Trabajo informal | `5` |
| Estudiante | `7` |

#### Nivel educativo de la madre (`NIVEL_ED_MADRE`)

| Valor | Código |
|---|---|
| Analfabeta | `1` |
| Primaria incompleta | `2` |
| Primaria completa | `3` |
| Bachillerato incompleto | `4` |
| Bachillerato completo | `5` |
| Técnico incompleto | `7` |
| Técnico completo | `8` |
| Tecnólogo incompleto | `9` |
| Tecnólogo completo | `10` |
| Universitario incompleto | `11` |
| Universitario completo | `12` |
| Posgrado incompleto | `13` |
| Posgrado completo | `14` |

| Campo | Valor |
|---|---|
| `MADRE_VIVA` | ¿La madre vive actualmente? Sí `S` / No `N` |

### Situación de los padres (`SITUACION_PADRES`)

| Valor | Código |
|---|---|
| Separados / Divorciados | `1` |
| Conviven / Conforman hogar | `2` |
| Conformó un nuevo hogar (algún fallecido) | `3` |

### Información adicional del hogar

| Campo | Valor |
|---|---|
| `TIENE_HIJOS` | ¿Tiene hijos actualmente? Sí `S` / No `2` |
| `CUANTOS_HIJOS` | Cantidad de hijos: 1 `1` / 2 `2` / 3 `3` / Más de 3 `4` |
| `H_UNILLANOS` | ¿Tiene hermano(a) matriculado en Unillanos? Sí `S` / No `2` |
| `PARE_UNILLANOS` | ¿Su pareja está matriculada en Unillanos? Sí `S` / No `N` |
| `HIJO_FUNCIONARIO` | ¿Es hijo de funcionario de Unillanos? Sí `S` / No `N` |

### Relación familiar y vivienda

| Campo | Valor |
|---|---|
| `RELA_FAMILIA` | Percepción de la relación familiar |
| Buena | `B` |
| Regular | `R` |
| Mala | `M` |
| `TIPO VIVIENDA` | Tipo de vivienda |
| Propia | `1` |
| Arrendada | `2` |
| Familiar | `3` |

---

## Fórmula de Puntaje

$$Puntaje = 0.238 \cdot f_1 + 0.345 \cdot f_2 - 1.439 \cdot f_3 + 0.728 \cdot f_4 - 0.982 \cdot f_5$$
