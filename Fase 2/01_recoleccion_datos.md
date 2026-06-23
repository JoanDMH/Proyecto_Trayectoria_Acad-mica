# Informe de Recolección de Datos
## CRISP-DM Fase 2 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Origen de los datos

Los datos fueron suministrados por la **Oficina de Sistemas de la Universidad de los Llanos** como parte del proyecto de investigación *"Estudio longitudinal de la trayectoria estudiantil en los programas de la Facultad de Ciencias Básicas e Ingeniería"*. La solicitud formal fue tramitada internamente y los archivos entregados en formato `.xlsx`.

No se usaron APIs, scraping ni fuentes externas. Los datos son de carácter institucional y de uso exclusivo para investigación.

---

## 2. Fuentes y archivos recibidos

| # | Archivo | Descripción | Origen |
|---|---|---|---|
| 1 | `caracterización.xlsx` | Formulario SIIF diligenciado por el estudiante al ingreso | Sistema de Información Institucional (SIIF) |
| 2 | `detalle_materias.xlsx` | Historial de materias cursadas con notas definitivas | Sistema Académico Institucional |
| 3 | `historial_estados_.xlsx` | Estado académico-administrativo por semestre | Sistema Académico Institucional |
| 4 | `PROMEDIOS_DE_CARRERA.xlsx` | Promedio acumulado de carrera por estudiante | Sistema Académico Institucional |
| 5 | `promedios_semestre.xlsx` | Promedio por semestre cursado | Sistema Académico Institucional |

---

## 3. Cobertura temporal

| Aspecto | Valor |
|---|---|
| Cohortes de ingreso | 2017-2 y 2018-1 |
| Período académico más antiguo en los datos | 2017-2 |
| Período académico más reciente en los datos | 2026-1 |
| Duración cubierta | Trayectoria observada de ~8–9 años (hasta 2026) |

El corte de los datos corresponde al momento de la extracción solicitada a la Oficina de Sistemas. La ventana de observación hasta 2026 permite clasificar el estado final (graduado / desertor / en formación) con la regla de recencia.

---

## 4. Volumen de datos — Cohortes 2017-2 y 2018-1 / Ingeniería de Sistemas

| Archivo | Registros totales | Filtrados (ambas cohortes) | Estudiantes únicos |
|---|---|---|---|
| `caracterización.xlsx` | 337 filas · 147 columnas | 95 filas | 95 |
| `detalle_materias.xlsx` | 8 503 filas · 14 columnas | 2 725 filas | 90 |
| `historial_estados_.xlsx` | 1 968 filas · 9 columnas | 579 filas | 97* |
| `PROMEDIOS_DE_CARRERA.xlsx` | 323 filas · 10 columnas | 90 filas | 90 |
| `promedios_semestre.xlsx` | 1 903 filas · 9 columnas | 593 filas | 90 |

> \* El historial incluye 3 códigos que no están en `caracterización` (solo aparecen con estado `NO REALIZO PAGO`); no forman parte de la población.
> **Población descriptiva: 95 estudiantes** (47 de 2017-2 + 48 de 2018-1). **Muestra de modelado: 89** (se excluyen 6 sin features académicas completas: 5 sin ninguna actividad y 1 con un único período sin promedio de carrera).

---

## 5. Alcance del análisis

| Dimensión | Valor |
|---|---|
| Programa | Ingeniería de Sistemas |
| Cohortes | **2017-2 y 2018-1** |
| Facultad | Ciencias Básicas e Ingeniería |
| Población descriptiva | **95 estudiantes** |
| Muestra de modelado | **89 estudiantes** |
| Formato de entrega | Archivos `.xlsx` locales |
| Restricciones de privacidad | Los datos contienen identificadores estudiantiles; el análisis no publica datos nominales |

---

## 6. Observaciones sobre la recolección

- El archivo `homologaciones.xlsx` fue recibido adicionalmente pero no se incorpora al modelo, ya que la información de materias homologadas ya está identificable en `detalle_materias.xlsx` mediante `OBSERVACION = 'O'`.
- El archivo `diccionario_siif.md` fue proporcionado por el investigador para documentar los códigos del formulario SIIF.
- Varios campos del formulario SIIF quedaron vacíos para esta cohorte (`LUGAR_VIVIRA_ESTUDIANTE`, `MEDIO_ESTUDIO`, `SIT_LABORAL_ASPIRANTE`, entre otros), posiblemente por versiones del formulario en uso en 2017.
- `historial_estados_.xlsx` no conserva la actividad académica completa de los primeros períodos de varios estudiantes; la actividad real se reconstruye con `detalle_materias.xlsx` (ver informe de hallazgos, sección 1.1).
