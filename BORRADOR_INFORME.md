# BORRADOR PARA EL INFORME FINAL — Bitácora consolidada de hallazgos
### Insumo de redacción (E4). No es el informe: es el inventario completo de cifras, grupos, decisiones y lecciones, con su fuente.
**Corte de la información:** 2026-09-30 · Complementa `REGISTRO_CIENTIFICO.md` (RC-001…RC-044). Toda cifra es regenerable con los scripts de `src/`.

> ## Estado de este borrador tras la auditoría de septiembre
>
> La auditoría metodológica (`AUDITORIA_2026-09.md`, RC-012 a RC-045) y el trabajo
> posterior recogido en **RC-033 a RC-044** reescribieron partes sustanciales del estudio.
> Las secciones **§6, §7, §8, §9.2, §9.3, §9.6, §9.7, §10 y §11** están actualizadas a esa
> revisión. Se conservan visibles, marcadas como **[SUPERADO]** o **[TARGET SUSTITUIDO]**,
> las cifras anteriores que un lector podría encontrar en documentos de fase previos:
> forman parte de la trazabilidad y de la discusión metodológica, y el informe debe narrar
> la iteración CRISP-DM, no esconderla. **Ninguna cifra así marcada es vigente.**
>
> **Cambios de fondo:**
>
> 1. La variable objetivo pasó a derivarse del **art. 19** del Reglamento Estudiantil, en
>    lugar de `PROMEDIO_CARRERA < 3,0`, que era tautológico.
> 2. El conjunto de variables se redujo de 19 a **6** (conjunto S3).
> 3. Los modelos de reprobación por asignatura fueron **retirados** por fuga temporal.
> 4. El protocolo de comparación se rehízo con **validación cruzada anidada**.
> 5. **Modelo definitivo (RC-033):** Random Forest sobre S3, **AUC-PR 0,745 ± 0,025**
>    (AUC-ROC 0,794), con n = 80, 19 positivos y línea base de azar 0,2375.
> 6. El **umbral único de 0,29 quedó sustituido** por un esquema de tres niveles
>    seleccionable (RC-034, RC-035).
> 7. El **target multiclase de cuatro clases se declaró inviable** (RC-041).
> 8. La arquitectura pasa a **modelos separados por programa** (RC-037).
> 9. El **diseño longitudinal fracasa** con el art. 19, y el diagnóstico apunta a la
>    definición del evento, no a la muestra (RC-038, RC-039).
> 10. Se incorporan los tres bloques del encargo de la dirección del 29-09: PCA (RC-042),
>     modelos bayesianos (RC-043) y aprendizaje con pocos datos (RC-044).
>
> **Producto ya conseguido:** el resumen extenso fue **aceptado en CICI 2026** (ID 129,
> Springer LNCS, 4 páginas; evento del 7 al 9 de octubre de 2026, Villavicencio). Reporta
> el target antiguo porque así se sometió y aceptó, y **no se reescribe**; el informe debe
> señalar esa diferencia de forma explícita (§14).

---

## 1. Contexto y fuentes de datos

Datos suministrados por la Oficina de Sistemas de la Universidad de los Llanos (extracción may-2026), en el marco del proyecto longitudinal de trayectoria estudiantil FCBI (codirectora S. Guerrero). Cohortes de ingreso **2017-2 y 2018-1**; ventana de observación hasta **2026-1** (~8–9 años de trayectoria).

| Archivo | Dimensiones | Contenido | Llave |
|---|---|---|---|
| `caracterización.xlsx` | 337 × 147 | Formulario SIIF al ingreso: sociodemográficas, familiares, Saber 11 | `CODIGO_ESTUDIANTIL` |
| `detalle_materias.xlsx` | 8 503 × 14 | Materia × intento: nota definitiva, periodo, observación | `CODIGO_INST` |
| `historial_estados_.xlsx` | 1 968 × 9 | Estado académico-administrativo por semestre | `CODIGO_INST` |
| `PROMEDIOS_DE_CARRERA.xlsx` | 323 × 10 | Promedio acumulado final | `CODIGO_INST` |
| `promedios_semestre.xlsx` | 1 903 × 9 | Promedio por semestre cursado | `CODIGO_INST` |
| `homologaciones.xlsx` | 343 × 10 | Pénsum y marca de homologación | `CODIGO_INST` |

Calendario real de los datos: 17 periodos regulares (2017-2 → 2026-1). **2020-2 no existe en ningún archivo** (suspensión por pandemia). Los periodos `AAAA-0` son cortes administrativos de inicio de año donde se asientan homologaciones (`O`) y cursos intersemestrales (`C`); no contienen cursos "normales".

## 2. Población por programa

| Programa | n caracterización | Graduados | Retiro formal | Sin acta (no grad.) | Activos 2024-1+ | Sin actividad académica |
|---|---|---|---|---|---|---|
| Ing. de Sistemas | 95 | 35 (36.8 %) | 30 | 30 | 1 | 15* |
| Ing. Electrónica | 95 | 25 (26.3 %) | 32 | 38 | 4 | 22* |
| Biología | 85 | 6 (7.1 %) | 33 | 46 | 15 | 4 |
| *(Lic. en Matemáticas — fuera del alcance)* | 62 | 14 | 14 | 34 | 5 | 2 |
| **Total FCBI (alcance)** | **275** | **66 (24.0 %)** | 95 | 114 | 20 | 41 |

\* "Sin actividad" = sin cursos en periodos regulares; incluye a quienes solo tienen bloque de homologación en periodos `-0` (Sistemas: 10 de los 15).

**Hallazgo de heterogeneidad (clave para el modelo general vs. por programa):** la tasa de graduación de Biología (7.1 %) es radicalmente inferior, con 15 estudiantes aún activos a 2026 — su trayectoria típica es más larga y su deserción/permanencia se comporta distinto. Esto debe pesarse en WP-OE1.1 antes de mezclar programas.

## 3. Semántica de los datos: lo que hubo que corregir (diccionario real)

La columna `OBSERVACION` de `detalle_materias` estaba mal interpretada. Diccionario validado con la Oficina de Sistemas (jul-2026):

| Código | Significado real | Interpretación errónea previa | Registros (global) |
|---|---|---|---|
| `N` | Curso normal | ✓ | 6 961 |
| `O` | Homologada (nota externa, siempre ≥3.0) | ✓ | 628 |
| `H` | Habilitada | ✓ | 324 |
| `TG` | Trámite de grado (sin nota) → se recodifica `A`/`P` | categoría única | 207 |
| (vacía) | **209 con nota = cursos reales** → `N`; sin nota → `R`/`E` | "sin registro" (se excluían) | 301 |
| `C` | **Curso intersemestral** (nota real, 17/79 reprobados) | **"Cancelada" (se excluían)** | 79 |
| `V` | Validada | "Vacía" | 2 |
| `I` | Intercambio | ✓ | 1 |

Otras propiedades verificadas: las homologadas (`O`) **nunca** tienen nota <3.0 (no se homologa lo reprobado); el historial de estados **no conserva** matrículas tempranas de muchos estudiantes e **omite estudiantes completos** (caso 160004030: 6 materias cursadas en 2017-2, cero filas de estado); tras un `RETIRADO BR` el sistema deja residuos administrativos (`NO REALIZO PAGO` un periodo después, 5 casos verificados) — los graduados en cambio cierran limpio (35/35 con `GRADUADO` como último estado, sin residuos).

## 4. Recodificación reproducible (la contribución metodológica central)

Todos los originales permanecen intactos (respaldo `Datos.zip`); las correcciones viven en `src/recodificacion.py` que genera:

**`detalle_materias_recod.xlsx`** (8 486 filas): elimina 17 trámites de grado fantasma posteriores a la graduación; recodifica `OBSERVACION` (vacías-con-nota→`N` 209; trámites→`A` 75/`P` 183 con regla "último trámite y periodo ≤ graduación"; vacías sin nota→`E` 24). Notas válidas para análisis: {N, C, H}.

**`historial_estados_recod.xlsx`** (2 566 filas): 1 968 originales intactas (columna `ORIGEN`) + 541 imputaciones trazables + 57 estados finales inferidos:

| Imputación | N | Regla |
|---|---|---|
| MATRICULADO | 256 | Periodo con cursos reales pero sin estado |
| NO MATRICULADO | 184 | Hueco truncado (sin actividad ni estado) dentro de la ventana |
| NO REALIZO PAGO (2020-2) | 101 | Pandemia; solo si hay actividad posterior a 2020-1 |
| Estado final inferido | 57 | Ver §5; **regla anti-residuo:** nada se imputa después de un estado terminal original |

## 5. Grupos de trayectoria identificados (detalle Ing. de Sistemas, n=95)

Clasificación por **regla de recencia** (en formación solo si hay actividad/matrícula en 2024-1+):

- **Graduados: 35 (36.8 %).** Tiempo a la graduación: media 6.4 años, mediana 6.0, rango 5.0–8.0 (plan nominal: 5). Cierre administrativo limpio en el 100 %.
- **Desertores: 59 (62.1 %).** Solo 30 con acta formal (17 RETIRADO BR, 8 voluntario, 4 no renovación, 1 definitivo BR); 29 sin acta. Duración antes de abandonar: mediana 1 periodo activo, media 2.2; **64 % deserta con ≤2 periodos** (concentración en el primer año); 5 nunca tuvieron actividad.
- **En formación: 1 (1.1 %)** (160004146, activo hasta 2026-1).

Subgrupos con valor analítico:

| Subgrupo | N | Evidencia |
|---|---|---|
| Sin acta con patrón `BAJO RENDIMIENTO→NO REALIZO PAGO` | 12 | Idéntico a los RETIRADO BR confirmados → estado final inferido RETIRADO BR |
| Sin acta con solo `NO REALIZO PAGO` (×2–3) | 3 | → inferido RETIRO POR NO RENOVACIÓN |
| Solo homologación (bloque 2019-0, pénsum 603) | 9 | Homologaron plan y desaparecieron; **0 traspasos internos** verificados por cruce de nombres en los 4 programas |
| Semestres truncados con reingreso | 12 | Hueco real de 1–3 periodos y retorno (10 con acta posterior, 2 graduados) |
| Invisibles en historial | 1 (160004030) | Recuperado vía imputación; entró a la muestra de modelado |

Predictor administrativo notable: **`BAJO RENDIMIENTO` es terminal en la práctica — 0 de 36 estudiantes que lo recibieron se graduaron.** Estados finales inferidos en total FCBI: 57 (Sistemas 15, Electrónica 15, Biología 27; mapeo BR≥1→RETIRADO BR 44, NRP≥2→NO RENOVACIÓN 13).

## 6. Variable objetivo y variables predictoras

### 6.1 La variable objetivo se deriva del Reglamento Estudiantil (RC-017)

El target original, `rendimiento_bajo = PROMEDIO_CARRERA < 3.0`, **fue descartado por tautológico**: el promedio de carrera incluye el primer semestre, que era precisamente su predictor dominante. Para los 17 estudiantes que cursaron un solo periodo (19 % de la muestra) ambos valores casi coinciden (r = 0,921). Sin `prom_sem1` el modelo caía a AUC 0,483 — azar puro — y al excluir a los desertores tempranos bajaba de 0,761 a 0,546.

En su lugar se adopta la definición institucional del **artículo 19**:

> `y = 1` si en algún periodo académico **regular** el estudiante reprobó el 100 % de los créditos cursados y su promedio ponderado acumulado era inferior a 3,0; **o** si reprobó un curso por cuarta vez.

Implementada en `src/preprocessing.py :: construir_target_art19()`. Detalle normativo en `MARCO_NORMATIVO.md`.

**Población en riesgo: n = 80, 19 positivos (23,8 %).** Se excluyen 10 estudiantes cuyo expediente se compone únicamente de homologaciones: sin créditos cursados no pueden activar el artículo. La exclusión es por falta de exposición, no por el desenlace, de modo que no introduce sesgo de supervivencia.

Para el target `graduado` se conserva la población completa (**n = 90**, 35 positivos, 38,9 %): los 10 sin actividad académica son negativos legítimos — ninguno se graduó.

**Sin conjunto de prueba retenido.** Con n = 80 y 19 positivos, un holdout del 20 % tendría ~4 positivos: cualquier métrica sobre él sería ruido. Se reporta únicamente validación cruzada repetida.

### 6.2 El conjunto de variables se redujo de 19 a 6 (RC-032)

Las 19 variables iniciales se habían fijado por **disponibilidad temporal** —solo lo observable al ingreso o al cierre del primer periodo— y se heredaron sin verificar su aporte. La verificación empírica (WP-OE1.2) arrojó:

| Subconjunto | Variables | AUC-PR | vs. set completo |
|---|:---:|:---:|---|
| Set completo | 19 | 0,7201 | referencia |
| **S3 · solo académicas** | **6** | **0,7196** | **Empate** (Δ=−0,0005; p=0,983) |
| S5 · sin redundancias estructurales | 17 | 0,726 | Empate (p=0,532) |
| S4 · solo socioeconómicas | 11 | 0,344 | Muy inferior |

**Conjunto definitivo (S3):** `prom_sem1`, `sin_primer_semestre`, `icfes_total`, `icfes_mat`, `icfes_lec`, `icfes_nat`.

Seis variables rinden lo mismo que diecinueve. Y las socioeconómicas por sí solas apenas superan el azar (0,344 frente a una línea base de 0,238), resultado coherente con las pruebas estadísticas no significativas de §9.4: dos métodos independientes apuntando a lo mismo.

**Dos redundancias estructurales confirmadas** (VIF): `icfes_total` = suma de cinco componentes, de las cuales tres están además incluidas por separado (VIF 9,00); y `nivel_edu_max_padres` = max(padre, madre), función determinista de otras dos variables incluidas (VIF 7,65).

**La importancia por permutación desmiente a la importancia por impureza (MDI).** `nivel_edu_madre` aparecía con 7,6 % de importancia MDI y por permutación **resta** capacidad predictiva (−0,007). Verificado inyectando dos columnas de ruido aleatorio puro: capturaron el **14,3 %** de la importancia MDI, una de ellas por encima de trece variables reales. En todo el informe se reporta permutación, no MDI.

Transformaciones documentadas: log1p en ingresos (asimetría fuerte: media 14,4 M, máx 62,7 M COP); mapeo ordinal de educación parental (códigos DANE sin el 6). Los 16 estudiantes sin promedio de primer semestre reciben un **indicador explícito** `sin_primer_semestre` además de la imputación, en lugar de una mediana ciega (RC-018).

### 6.3 El target multiclase comprometido en la propuesta es inviable (RC-041)

La propuesta de grado comprometía una variable objetivo de trayectoria en **cuatro clases** —graduado, activo, desertor, rezagado— evaluada al final del seguimiento. Se construyó (`src/target_multiclase.py`) con las definiciones fijadas **antes** de modelar y se le aplicó la regla de viabilidad pre-registrada en RC-008: clase minoritaria ≥ 25 estudiantes **y** ≥ 5 casos por pliegue en CV-5. No la supera.

| Target | Clases | Clase minoritaria | n | Por pliegue | ¿Viable? |
|---|:---:|---|:---:|:---:|:---:|
| 4 clases (propuesta original) | 4 | ACTIVO | **5** | 1,0 | **No** |
| 3 clases (colapsada) | 3 | ACTIVO | **20** | 4,0 | **No** |
| 2 clases (graduación) | 2 | GRADUADO | **66** | 13,2 | **Sí** |

Distribución con cuatro clases sobre los 262 estudiantes de la FCBI: DESERTOR 176 (67,2 %), GRADUADO 66 (25,2 %), REZAGADO 15 (5,7 %), **ACTIVO 5 (1,9 %)**.

Antes de declarar la inviabilidad se probaron **tres operacionalizaciones alternativas** de «rezagado», y ninguna rescata el target porque el cuello de botella es siempre el mismo:

| Alternativa | Clase minoritaria | n | Por pliegue | ¿Viable? |
|---|---|:---:|:---:|:---:|
| A. Rezagado = activo que excede 10 semestres | ACTIVO | 5 | 1,0 | No |
| B. Rezagado = cualquiera que excede 10 semestres (incluidos graduados tardíos) | ACTIVO | 5 | 1,0 | No |
| C. Separar graduado a tiempo de graduado tardío | ACTIVO | 20 | 4,0 | No |

**El limitante no es «rezagado» sino «activo».** En cuanto se separa el rezago con cualquier criterio, ACTIVO se queda con los cinco estudiantes que siguen matriculados dentro del tiempo nominal; y sin separarlo, se queda en veinte.

Dos hallazgos sustantivos explican el resultado, y valen por sí mismos:

- **La clase ACTIVO es, en esencia, el grupo censurado de Biología.** De los 20 activos, **15 son de Biología** (75 %), frente a 4 de Electrónica y 1 de Sistemas. La clase no captura un fenómeno académico sino un artefacto de la ventana de observación (coincide con la censura de RC-036).
- **En estas cohortes el rezago es la norma, no la excepción.** De los 66 graduados, **39 (59 %) tardaron más de 10 periodos**; de los 20 activos, 15 (75 %). Entre quienes no desertaron, **el 63 % excedió el plan nominal**. Una clase que agrupa al 63 % de la población no discrimina: el target de cuatro clases presupone que «a tiempo» y «rezagado» son grupos comparables, y aquí **estar a tiempo es lo excepcional**. Las cohortes 2017-2 y 2018-1 llevan ~17 periodos frente a un plan nominal de 10: la propuesta describía un seguimiento más corto que el disponible.

**Decisiones:** se adopta el **target binario de graduación** como variable objetivo de trayectoria (66 minoritarios, viable); el rezago pasa a **indicador continuo secundario** (`periodos_sobre_plan`), conforme a lo pre-registrado en RC-008; los 20 activos se marcan con `censurado = 1` y se excluyen del target de graduación, no del art. 19, que sí es observable para ellos.

No es un fracaso sino un resultado: la propuesta especificó un target razonable *a priori* y el estudio demuestra, **con un criterio fijado de antemano en vez de ajustado al resultado**, que la ventana de observación no lo sostiene. Es el tipo de ajuste que el carácter iterativo de CRISP-DM contempla. Modifica, eso sí, un entregable comprometido (E2), por lo que la sustitución debe formalizarse con la dirección del proyecto (decisión abierta **D-MULTI**).

## 7. Fuga de información: el hallazgo metodológico central

> **Esta es la contribución metodológica del trabajo.** El estudio detectó la misma clase
> de error —usar en el entrenamiento información que el modelo no tendría disponible al
> predecir— en **tres niveles independientes**, y midió el efecto de cada uno con datos
> propios. La fuga no resultó ser un accidente puntual sino un **riesgo sistemático** en
> estudios con muestras pequeñas.

| Nivel | Qué se filtraba | Efecto medido |
|---|---|---|
| **1 · Temporal**, en las variables | `prom_global` era el promedio del estudiante en el *resto de la carrera*; entre el 70 % y el 83 % procedía de semestres **posteriores** a la asignatura predicha | AUC reportado 0,865–0,939 → honesto **0,70–0,74** |
| **2 · Hiperparámetros** | La búsqueda en malla se hacía sobre la muestra completa y luego se medía por validación cruzada: los pliegues de prueba ya habían intervenido en elegir la configuración | Sesgo **+0,046** en XGBoost, +0,008 en Random Forest |
| **3 · Selección de variables** | El "top-5 por importancia" se elegía viendo toda la muestra y se evaluaba sobre esa misma muestra | Sesgo **+0,150 de AUC-PR** |

### 7.1 Fuga temporal (RC-013)

Las cinco asignaturas críticas son de primer y segundo semestre. Predecir la reprobación de Matemáticas I usando el desempeño del estudiante en los semestres 2 a 10 **no es predicción, es retrodicción**. Al reconstruir un modelo temporalmente válido —predecir la reprobación de segundo semestre con información observada únicamente en el primero— el desempeño real resultó ser AUC 0,707 (Matemáticas II) y 0,740 (Física I). Las variables de ingreso por sí solas no predicen nada (0,41–0,51).

Los cinco modelos fueron **retirados** del repositorio, la aplicación y el informe (RC-022). El índice de criticidad se conserva: es un indicador descriptivo, no un modelo, y no está afectado.

### 7.2 Fuga de hiperparámetros (RC-021)

El patrón `GridSearchCV.fit(X, y)` seguido de `cross_val_predict(mejor_estimador)` sobreestima el desempeño. Lo grave no es el sesgo en sí, sino que **no es uniforme entre algoritmos**: XGBoost se beneficiaba cinco veces más que Random Forest, de modo que **el orden del ganador se invertía** según el protocolo. El protocolo, y no los datos, estaría decidiendo el resultado. La validación anidada pasó a ser obligatoria.

### 7.3 Fuga de selección de variables (RC-030, RC-032)

El error más costoso, y cometido **después** de haber documentado los dos anteriores:

| Conjunto | Tipo de selección | AUC-PR |
|---|---|:---:|
| Set completo (19) | a priori | 0,7201 |
| S3 · solo académicas (6) | a priori | 0,7196 |
| top-5 **contaminado** | fuera del pliegue | **0,8204** |
| top-5 **anidado** | dentro del pliegue | **0,6705** |

**Sesgo: +0,150 de AUC-PR** — cinco veces el umbral de relevancia pre-registrado y mayor que la distancia entre el mejor y el peor algoritmo del estudio. Habría llevado a adoptar un conjunto peor creyéndolo mejor.

**Por qué ocurre, con evidencia:** la selección es inestable. A lo largo de 40 pliegues, solo `prom_sem1` entra en el top-5 el 100 % de las veces; `icfes_total` el 75 %, `icfes_mat` el 60 %, y a partir de la tercera posición la elección es prácticamente azar. Con 19 positivos, **el ranking de importancia más allá del top-2 o top-3 es ruido**, y seleccionar sobre ruido perjudica.

*Referencia externa para la discusión:* Ambroise & McLachlan (2002, PNAS) documentan este mismo fenómeno en selección de variables con muestras pequeñas.

## 7-bis. Otros errores corregidos durante el estudio

Se documentan porque son parte del método (CRISP-DM iterativo) y de la discusión del informe:

1. **Fugas de información en los modelos por materia** (RC-001): `prom_global` incluía la nota objetivo y `nota_mat1` era el target del modelo de Matemáticas I → métricas infladas (Matemáticas I F1 in-sample = 1.000). Corregido: features anti-leakage + CV out-of-fold obligatoria.
2. **Métricas in-sample reportadas al inicio** para los modelos por materia → sustituidas en su totalidad por CV-5 out-of-fold.
3. **Diccionario mal interpretado** (RC-002): `C` leída como "cancelada" y vacías-con-nota descartadas → se excluían 76 registros reales solo en Sistemas; tasa de reprobación de Matemáticas II sobreestimada (44 % aparente vs. 31.5 % real).
4. **Cifra obsoleta arrastrada** ("N=12" en materias críticas) detectada en revisión cruzada: el pipeline reproducible por script eliminó la clase de errores "número editado a mano".
5. **Imputación con residuos post-terminales** (fila 1216): un trámite fantasma post-graduación generó un `MATRICULADO` imputado después del `GRADUADO`; se detectaron y borraron 17 registros fuente y se instauró la regla anti-residuo (43 imputaciones post-retiro también eliminadas).
6. **Riesgo del periodo "-0" y del 2020-2**: al inicio se trató 2020-2 como hueco individual (producía ~40 falsos "semestres truncados"); corregido al descubrir que el periodo no existe institucionalmente (pandemia).
7. **Incidencias operativas**: corrupción de archivos xlsx en disco (2 veces) y una alteración accidental del original `detalle_materias.xlsx` (1 nota borrada) — recuperado todo desde `Datos.zip`; motivó la regla "todo regenerable por script".
8. **Colisión en el ordenamiento de periodos** (RC-020): la función que ordena periodos académicos colapsaba `AAAA-0` (curso intersemestral) con `AAAA-2` del mismo año, mezclando **133 registros**. Al corregirlo —y al excluir el intersemestral de la condición del "100 % de los créditos", conforme a los arts. 15 y 40— el target pasó de 20 a 19 positivos, **desaparecieron los 2 casos ambiguos** y el desempeño subió ~0,06 de AUC en todos los algoritmos.
9. **Presupuesto de ajuste desigual entre algoritmos** (RC-025): las rejillas de búsqueda iban de 8 combinaciones (XGBoost) a 48 (Random Forest), una desventaja de 6:1, y la de XGBoost **no incluía ningún hiperparámetro de regularización**. Su último lugar era en parte un artefacto del diseño. Corregido a un rango de 16–24 combinaciones para todos.
10. **Hipótesis propia refutada por los datos** (RC-031): se esperaba que añadir regularización mejorara a XGBoost. La curva de validación mostró lo contrario — `min_child_weight = 3` hunde el AUC-PR de 0,710 a 0,397. Con 15 positivos en entrenamiento, exigir tres instancias por hoja bloquea los cortes sobre la clase minoritaria. **Regularizar agresivamente es contraproducente en muestras pequeñas con clase rara**, resultado contraintuitivo y reportable.

## 8. Decisiones estratégicas tomadas (con justificación corta)

| # | Decisión | Justificación |
|---|---|---|
| D1 | Clasificación del estado final por **recencia** (activo solo si 2024-1+) | Un `NO REALIZO PAGO` de hace 5 años no es "en formación" |
| D2 | **Originales intactos + recodificación por script** | Reproducibilidad y defensa ante auditoría |
| D3 | Estados originales = norma; imputaciones trazables (`ORIGEN`) | No se sobreescribe evidencia administrativa |
| D4 | Estados finales **inferidos** solo con criterios 3.1–3.3 | Evita imputar sin evidencia (excluidos: activos, sin actividad, señal insuficiente) |
| D5 | Índice de materias críticas **centrado en reprobación** (0.70/0.30) | Mide dificultad de aprobar; el promedio penalizaba materias fáciles con notas bajas |
| D6 | **Sin SMOTE** en binarios (42/39 % minoritaria) | Desbalance leve; ruido sintético con n=90 (RC-004) |
| D7 | ~~Umbral 0.29 en riesgo de bajo rendimiento~~ **[SUPERADA por D20]** | Priorizaba Recall+ (0.816) sobre el **target sustituido**; el criterio de fondo —el falso negativo es el error caro en alertas (RC-005)— se conserva, pero el umbral único no (RC-034, RC-035) |
| D8 | n=89→**90** al recuperar a 160004030 | Su exclusión era un defecto del archivo, no metodológica; features reales |
| D9 | Alcance: Sistemas + Electrónica + Biología (**sin** Lic. Matemáticas) | Decisión del estudiante |
| D10 | ~~Target de trayectoria multiclase con **sub-modelos por corte** semestral~~ **[SUPERADA por D21 y D22]** | La intención (evitar el sesgo de supervivencia, RC-008) era correcta, pero el target multiclase es inviable (RC-041) y el diseño por cortes no predice el art. 19 (RC-038) |
| D11 | Regla de viabilidad pre-registrada para la clase "rezagado" | <25 casos → colapso a 3 clases (RC-008). **Se aplicó y el target no la superó** (RC-041) |
| D12 | E2 = paquete de inferencia dual (trayectoria + bajo rendimiento) | Visión de producto SPADIES |
| **D13** | **Target derivado del art. 19** del Reglamento vigente, no `PROMEDIO_CARRERA<3.0` | Definición institucional, verdad de campo, sin circularidad (RC-017) |
| **D14** | Población en riesgo **n=80** para art. 19; **n=90** para graduación | Quien nunca cursó no puede reprobar créditos, pero sí puede no graduarse |
| **D15** | Conjunto de variables **S3 (6)**, definido a priori | Iguala al completo (p=0,983) sin selección guiada por los datos (RC-032) |
| **D16** | **Validación anidada obligatoria**; prohibida toda selección fuera del pliegue | El protocolo no puede decidir el ganador (RC-021, RC-030) |
| **D17** | **AUC-PR** como métrica principal; línea base = prevalencia (0,2375) | Con 24 % de positivos el AUC-ROC es optimista |
| **D18** | Umbral de relevancia práctica **ΔAUC ≥ 0,03**; por debajo, empate técnico | Con n=80 declarar ganador por la tercera decimal es reportar ruido (RC-016) |
| **D19** | Se asume **estabilidad del reglamento vigente** durante la vida útil del modelo | Alcance declarado; si cambia, hay que recalcular la etiqueta (RC-015) |
| **D20** | **Esquema de alerta de tres niveles** seleccionable, en lugar del umbral único | La curva PR tiene una zona de precisión perfecta que un umbral único desaprovecha; el modelo detecta y **cuántos estudiantes acompañar es decisión institucional** (art. 23) (RC-034, RC-035) |
| **D21** | **Target binario de graduación** en lugar del multiclase de cuatro clases | La clase ACTIVO tiene 5 casos (1 por pliegue); ninguna reoperacionalización la rescata (RC-041) |
| **D22** | **Se descarta el diseño longitudinal por cortes** para el target del art. 19 | Las variables acumuladas no aportan (corte 1 p=0,514) y en el corte 2 empeoran (Δ=−0,0204; p=0,044): el evento es agudo, no gradual (RC-038, RC-039) |
| **D23** | **Modelos separados por programa**, mismo algoritmo y mismo protocolo en los tres | El modelo conjunto pierde Δ=−0,0306 (p=0,043), significativo y relevante, pese a triplicar los datos (RC-037) |
| **D24** | **El PCA se usa como diagnóstico, no como criterio de selección** | Es no supervisado: no puede validar una selección supervisada, y medido destruye la señal (0,3715 frente a 0,7418; p<0,0001) (RC-042) |
| **D25** | La aplicación debe mostrar **nivel de alerta y puesto relativo**, no un porcentaje | El 54 % de los estudiantes tiene un intervalo creíble del 94 % más ancho de 0,30: para ellos el modelo no está en condiciones de emitir un número (RC-043). *Pendiente de aprobación: decisión abierta **D-APP*** |

**Cinco decisiones abiertas que requieren pronunciamiento de la dirección** (no son resultados, son puntos de bloqueo del cierre): **D-REGIMEN** (¿etiquetar bajo el reglamento de 2022 o bajo el Acuerdo 015 de 2003, que regía para estas cohortes?), **D-MULTI** (formalizar la sustitución del target multiclase por el binario), **D-ALCANCE** (¿un modelo FCBI o tres por programa? — la medición apoya tres), **D-COLIN** (¿se conserva `icfes_total` o sus tres áreas?) y **D-APP** (¿calibrar las probabilidades o retirar el porcentaje?).

### 8-bis. Desviación declarada del protocolo

En I-3 la regla pre-registrada (empate técnico → modelo más simple) habría seleccionado la **Regresión Logística**. Se adoptó **Random Forest** por su liderazgo en AUC-ROC y en las métricas operativas al umbral elegido. **La desviación se declara explícitamente** (RC-023): el desempate se resolvió con la métrica secundaria, no con la principal, y es una decisión de dirección del proyecto, no un resultado del protocolo. La Regresión Logística se conserva como línea base declarada e interpretable.

## 9. Resultados de la muestra de Ing. de Sistemas (estudios preliminares)

### 9.1 Materias críticas (índice, datos recodificados)

| # | Materia | Tasa reprobación | Repitencia media | Índice | N |
|---|---|---|---|---|---|
| 1 | Matemáticas II | 31.5 % | 1.61 | 0.983 | 54 |
| 2 | Física I | 27.8 % | 1.65 | 0.918 | 54 |
| 3 | Álgebra Lineal | 29.2 % | 1.40 | 0.835 | 72 |
| 4 | Matemáticas I | 26.0 % | 1.10 | 0.623 | 73 |
| 5 | Fund. de Programación | 20.8 % | 1.15 | 0.534 | 72 |

Las 5 son de los primeros semestres y de énfasis matemático — coherente con la literatura STEM citada en la propuesta.

### 9.2 Comparativa de algoritmos

> **Línea base de AUC-PR = prevalencia = 0,2375.** No se compara contra 0,5.

#### 9.2.a Resultado definitivo — I-3 bis (RC-033)

Cinco algoritmos · conjunto S3 (6 variables) · n=80, 19 positivos · CV-5 × 10 repeticiones **anidadas** · rejillas equilibradas de 16–24 combinaciones. **Línea base AUC-PR (azar) = 0,2375.**

| Algoritmo | AUC-PR | sd | IC 95 % |
|---|:---:|:---:|---|
| **Random Forest** ✓ | **0,745** | ±0,025 | 0,703–0,783 |
| SVM (RBF) | 0,714 | ±0,037 | 0,637–0,750 |
| XGBoost | 0,630 | ±0,045 | 0,573–0,703 |
| Árbol de Decisión | 0,614 | ±0,055 | 0,516–0,693 |
| Regresión Logística (L2) | 0,550 | ±0,088 | 0,411–0,663 |

**Random Forest gana, y esta vez por aplicación directa de la regla pre-registrada.** Supera de forma significativa y relevante al Árbol (Δ=+0,131; p=0,005), a la Logística (Δ=+0,196; p=0,005) y a XGBoost (Δ=+0,115; p=0,004). Frente a SVM la diferencia (+0,032) no es estadísticamente significativa (p=0,234), de modo que se declara empate y el orden de parsimonia coloca a Random Forest por delante. **No se requiere desviación del protocolo.**

Tiene además la menor dispersión del conjunto (sd 0,025) y el intervalo más estrecho.

**Modelo definitivo del informe:** Random Forest sobre el conjunto S3 (6 variables), target del art. 19, n = 80 con 19 positivos, **AUC-PR 0,745 ± 0,025** frente a una línea base de azar de **0,2375** (lift ≈ 3,16×) y AUC-ROC 0,794.

#### 9.2.a-bis Umbral operativo: esquema de tres niveles (RC-034, RC-035)

La primera lectura de la curva de umbral fue **defectuosa y se corrigió**. La rutina elegía el umbral que maximiza F1-macro —criterio que premia el equilibrio entre clases y empuja a umbrales altos, **opuesto** al declarado en RC-005— y calculaba la curva con una sola repetición y desde 0,10, lo que producía un techo aparente de Recall+ 0,684 que no existe. Con probabilidades promediadas sobre las 10 repeticiones y barrido desde 0,02:

| Umbral | Recall+ | Prec+ | Alertas (de 80) |
|:---:|:---:|:---:|:---:|
| 0,06 | 1,000 | 0,288 | 66 |
| 0,10 | 0,842 | 0,291 | 55 |
| **0,14** | **0,789** | 0,326 | **46** |
| 0,18 | 0,737 | 0,389 | 36 |
| 0,22 | 0,632 | 0,462 | 26 |
| 0,54 | 0,632 | 0,857 | 14 |

El recall no había caído: el modelo S3 alcanza **Recall+ 0,789 en umbral 0,14**, el mismo valor de la iteración anterior, y **Recall+ 1,000 en umbral 0,06**.

La curva también revela una **zona de precisión perfecta** que un umbral único desaprovecha: el modelo mantiene precisión 1,000 hasta recall 0,579, es decir, **identifica 11 de los 19 casos sin una sola falsa alarma**. De ahí el esquema adoptado (D20), con tres puntos de operación medidos:

| Nivel | Umbral | Alertas | Precisión+ | Casos detectados |
|---|:---:|:---:|:---:|---|
| **Confirmado** | 0,62 | 11 | **1,000** | 58 % (11 de 19) |
| **Equilibrado** | 0,12 | 52 | 0,308 | 84 % |
| **Cobertura total** | 0,06 | 66 | 0,288 | **100 %** |

**El umbral definitivo no se fija por métrica sino con la capacidad real de atención del Programa de Retención** (art. 23): es una decisión institucional que debe consultarse y documentarse. El intercambio debe presentarse sin adornos: capturar el 79 % de los casos exige alertar sobre **46 de 80 estudiantes (57 % de la cohorte)**, y el 100 %, sobre 66. Con 19 positivos entre 80, la precisión en la zona de alto recall es intrínsecamente baja (0,29–0,34): un modelo con AUC-PR 0,745 sobre una clase del 24 % **no puede** dar alta precisión y alta exhaustividad a la vez, y presentarlo de otro modo sería engañoso.

*Matiz registrado:* a recall igualado, el conjunto de 19 variables conserva algo más de precisión que S3 (a Recall+ 0,79: 0,400 frente a 0,340; a 0,68: 0,542 frente a 0,448), aunque el AUC-PR global es equivalente. El dato matiza, sin invalidar, la decisión D15.

#### 9.2.a-ter Qué produjo la mejora

El mejor modelo pasó de **0,569 a 0,745 (+0,176)** usando **un tercio de las variables**. La ganancia no vino del algoritmo sino de la calidad del diseño experimental:

| Cambio | Efecto observado |
|---|---|
| Equilibrar el presupuesto de rejilla | XGBoost **0,528 → 0,630 (+0,102)**, del quinto al tercer puesto |
| Reducir a S3 (6 variables) | Mejora general; la Logística cae al último lugar |
| Validación anidada | Elimina el sesgo optimista no uniforme entre algoritmos |

**El ordenamiento cambió por completo:** de *SVM ≈ RF ≈ LogReg* a *RF > SVM > XGB ≈ Árbol ≈ LogReg*. La recuperación de XGBoost (+0,102) es **mayor que la distancia entre el primero y el segundo** (+0,032): un presupuesto de ajuste desigual no solo penaliza a un algoritmo, **reordena la tabla completa**.

La caída de la Regresión Logística es coherente con la naturaleza del target: el art. 19 es una **conjunción** (100 % de créditos reprobados **y** promedio < 3,0), forma que un modelo lineal no representa bien. Con 19 variables el ruido igualaba a todos; con 6 variables informativas, la estructura del problema se impone.

> ⏳ Falta el mismo protocolo sobre el target `graduado` (n=90).

#### 9.2.b [SUPERADO] Modelos prototipo con el target descartado (agosto 2026)

*Se conservan para la discusión sobre el efecto de la definición del target y para documentar la iteración CRISP-DM. **Ninguna cifra de este apartado es vigente.** El target `rendimiento_bajo` fue descartado por tautológico (§6.1) y sustituido por el del art. 19; el modelo vigente es el de §9.2.a (AUC-PR 0,745).*

> ⚠ **[TARGET SUSTITUIDO]** La tabla siguiente corresponde al target **antiguo**
> `rendimiento_bajo = PROMEDIO_CARRERA < 3,0`, con umbral único 0,29, 19 variables y
> partición fija. **No debe leerse como desempeño del modelo del informe.** En particular,
> el Recall+ 0,816 y el AUC 0,752 de Random Forest **no son las cifras vigentes**: la
> comparación válida es la de §9.2.a, con AUC-PR y validación anidada, donde Random Forest
> obtiene 0,745 sobre una línea base de 0,2375.

**Target antiguo `rendimiento_bajo` (umbral 0.29) — [TARGET SUSTITUIDO, cifras no vigentes]:**

| Modelo | Recall+ | Prec+ | F1-mac | AUC | MCC | Acc |
|---|---|---|---|---|---|---|
| Árbol de Decisión | 0.632 | 0.667 | 0.702 | 0.702 | 0.404 | 0.711 |
| Random Forest *(ganador del target antiguo)* | 0.816 | 0.484 | 0.548 | 0.752 | 0.197 | 0.556 |
| XGBoost | 0.737 | 0.596 | 0.677 | 0.776 | 0.367 | 0.678 |

Merece atención el MCC de 0,197 y la exactitud de 0,556 de aquella configuración: con el umbral bajo, el modelo del target antiguo apenas se distinguía de alertar a media cohorte. Es parte del argumento por el que se rehízo el diseño.

**Target `graduado` (umbral 0.50) — [SUPERADO: partición fija, 19 variables; pendiente de rehacer con el protocolo anidado]:**

| Modelo | Recall+ | Prec+ | F1-mac | AUC | MCC | Acc |
|---|---|---|---|---|---|---|
| Árbol de Decisión | 0.686 | 0.686 | 0.743 | 0.728 | 0.486 | 0.756 |
| Random Forest | 0.657 | 0.821 | **0.792** | 0.844 | **0.596** | 0.811 |
| **XGBoost** ✓ | 0.600 | 0.808 | 0.764 | **0.853** | 0.548 | 0.789 |

**[RETIRADO] Modelos de reprobación por materia** — AUC 0,865–0,939 reportado, invalidado por fuga temporal (§7.1). Desempeño honesto: 0,70–0,74. No se reportan como resultado.

### 9.3 Importancia de variables

#### 9.3.a Vigente — importancia por permutación (caída de AUC-PR al barajar)

| Variable | Caída AUC-PR | Positiva en |
|---|:---:|:---:|
| `prom_sem1` | **0,303** | 92 % de los pliegues |
| `icfes_total` | 0,043 | 80 % |
| `icfes_mat` | 0,026 | 68 % |
| `sisben_nivel` | 0,019 | 64 % |
| `cohorte_encoded` | 0,018 | 76 % |
| `icfes_nat`, `nivel_edu_madre`, `icfes_lec` | **negativa** | < 36 % |

*Nota de lectura: la tabla se calculó sobre el conjunto de 19 variables —de ahí que aparezcan `sisben_nivel` y `cohorte_encoded`, que no pertenecen a S3—. Se conserva porque es lo que justifica empíricamente la reducción a S3.*

**Solo 10 de las 19 variables tienen aporte neto positivo.** El promedio del primer semestre domina con un orden de magnitud de diferencia sobre la segunda: es la señal de alerta más temprana y accionable, y el hallazgo se sostiene con el target corregido.

**Tres confirmaciones independientes de esa dominancia.** Además de la permutación, (a) la selección anidada elige `prom_sem1` en el **100 % de los 40 pliegues**, la única variable que lo consigue (§7.3), y (b) la posterior bayesiana le asigna el único coeficiente grande, negativo y creíble: **−1,362**, IC 94 % [−1,95, −0,77] (§9.7.b). Tres métodos con supuestos distintos apuntando a lo mismo.

⚠ **Cautela obligatoria sobre el bloque SABER 11.** Cualquier lectura de importancias o coeficientes *individuales* dentro de ese bloque es inválida mientras `icfes_total` conviva con sus tres áreas: la colinealidad documentada en §9.7.b (VIF 6,66; R² = 0,850) hace que el modelo esté ajustando contrastes entre el total y sus partes, no efectos interpretables. La decisión de conservar el total o las áreas está abierta (**D-COLIN**) y debe resolverse **antes** de interpretar este bloque en el informe.

#### 9.3.b [SUPERADO] Importancia por impureza (MDI)

> ⚠ **Doblemente no vigente.** La tabla siguiente (a) se calculó sobre el **target antiguo
> y sustituido** `rendimiento_bajo`, y (b) usa la importancia por **impureza (MDI)**, que
> este mismo estudio demostró que no mide relevancia predictiva. Se conserva únicamente
> como objeto de la discusión metodológica. La importancia vigente es la de §9.3.a, por
> permutación y sobre el target del art. 19.

| Rank | RF → `rendimiento_bajo` **[target sustituido]** | Imp. MDI **[medida no fiable]** |
|---|---|---|
| 1 | `prom_sem1` | 0.404 |
| 2 | `icfes_total` | 0.121 |
| 3 | `icfes_lec` | 0.071 |
| 4 | `log_ingresos` | 0.070 |
| 5 | `icfes_nat` | 0.066 |

**Por qué no se usa.** La MDI mide cuántas veces el árbol usó la variable para partir, no cuánto aporta a predecir: favorece a las variables con muchos valores distintos. Prueba directa: al inyectar **dos columnas de ruido aleatorio puro**, capturaron el **14,3 %** de la importancia MDI total, una de ellas por encima de trece variables reales. Y `nivel_edu_madre`, con 7,6 % de MDI, **resta** capacidad predictiva por permutación (−0,007).

*Este contraste es material publicable: documenta con datos propios por qué la importancia MDI —de uso muy extendido en la literatura de EDM— no debe interpretarse como relevancia predictiva.*

### 9.4 Pruebas estadísticas (n=90) — resultados negativos que se publican

Ninguna asociación significativa: género vs. promedio (Mann-Whitney p=0.246; medianas 3.20 M / 3.70 F), educación del padre/madre vs. promedio (Spearman p=0.627 / 0.862), repitencia escolar vs. rendimiento bajo (χ² p=0.215). Poder limitado (15 mujeres; 15 repitentes).

### 9.5 Impacto de la calidad de datos (antes → después de la recodificación)

| Indicador | Antes | Después |
|---|---|---|
| Registros con nota válidos (Sistemas) | 2 448 | 2 524 (+76) |
| n modelado *(cifra de entonces; hoy n = 90 con actividad y **n = 80** expuestos al art. 19)* | 89 | 90 |
| Tasa reprobación Matemáticas II | 44 % | 31.5 % |
| F1-w promedio (modelos por materia) — **[RETIRADO]** | 0.832 | 0.880 |
| AUC Matemáticas II — **[RETIRADO]** | 0.691 | 0.865 (+0.174) |
| Modelo principal (features independientes) | — | estable (validación de que no hubo fuga) |

> ⚠ **[RETIRADO]** Las dos filas marcadas proceden de los **modelos de reprobación por
> asignatura, que están retirados** por fuga temporal (§7.1): el 0,865 de Matemáticas II
> era un AUC inflado. Al reconstruir el modelo de forma temporalmente válida, el
> desempeño honesto resulta **0,707** (Matemáticas II) y 0,740 (Física I). Las cifras de la
> tabla se conservan solo para documentar el efecto de la recodificación sobre la calidad
> del dato, que es real e independiente de la fuga, **no como resultado predictivo**.

Las dos conclusiones que sí se sostienen son: la tasa de reprobación de Matemáticas II estaba **sobreestimada** (44 % aparente frente a 31,5 % real), y la calidad del dato tuvo un efecto grande sin tocar una línea de modelado. La afirmación previa "Matemáticas II es impredecible" no puede declararse ni refutada ni confirmada desde esta tabla, porque la comparación 0,691 → 0,865 se hizo entre dos modelos con fuga. Tabla completa: `Fase 5/03_impacto_recodificacion_antes_despues.md`.

### 9.6 Extensión a la FCBI y arquitectura del modelo: separado por programa (RC-036, RC-037)

#### 9.6.a Lo aprendido en Sistemas se traslada a los otros dos programas

La verificación de Electrónica y Biología (`src/verificacion_fcbi.py`) concluye que las reglas de recodificación, el diccionario y la definición del target son **trasladables sin cambios**:

- **Cobertura homogénea:** de 275 estudiantes de la caracterización quedan **262** con promedio de carrera (pérdida del 4,7 %), repartida de forma pareja: Sistemas 95→90, Electrónica 95→91, Biología 85→81. La causa es la misma en los tres: admitidos sin actividad académica calificada.
- **Patrón de nulos idéntico:** `NIVEL_ED_PADRE` 17–22 % en los tres programas (es característica del formulario SIIF, no de un programa); Saber 11 entre el 1 % y el 7 %; el resto sin nulos.
- **El target del art. 19 aplica a los tres:** Sistemas 19/80 (23,8 %), **Electrónica 23/73 (31,5 %)**, Biología 17/81 (21,0 %). Total FCBI: **59 positivos de 234 expuestos (25,2 %)**, sobre un dataset maestro de **262 estudiantes** (`src/df_master_fcbi.csv`).
- *Hallazgo operativo:* la caracterización usa `CODIGO_ESTUDIANTIL` como llave mientras el resto de las fuentes usa `CODIGO_INST`.

**Pero Biología es una población estructuralmente distinta:** 64,7 % de mujeres frente al 15,8 % de Sistemas y el 7,4 % de Electrónica; Saber 11 unos 10 puntos por debajo en todas las áreas (matemáticas 54,8 frente a 65,6 y 65,3); promedio de carrera 2,702 frente a 3,083 y 3,036. Sistemas y Electrónica, en cambio, son comparables en composición, perfil de ingreso y promedio.

#### 9.6.b Los modelos separados ganan al modelo conjunto

La pregunta se dejó abierta **por medición**: modelo único con `programa` como variable frente a tres modelos separados, bajo el protocolo de I-3 bis (S3, Random Forest, CV-5 × 10 repeticiones, AUC-PR, SEED = 42). El comparador del enfoque separado es la media ponderada por tamaño de los tres modelos, que es su desempeño esperado en producción.

| Modelo | n | Positivos | AUC-PR | Línea base | Lift |
|---|:---:|:---:|:---:|:---:|:---:|
| Separado · Sistemas | 80 | 19 | **0,7483** | 0,237 | 3,15× |
| Separado · Electrónica | 73 | 23 | **0,7250** | 0,315 | 2,30× |
| Separado · Biología | 81 | 17 | **0,5983** | 0,210 | 2,85× |
| Conjunto sin indicador de programa | 234 | 59 | 0,6585 | 0,252 | 2,61× |
| Conjunto con indicador de programa | 234 | 59 | 0,6615 | 0,252 | 2,62× |

1. **Los modelos separados ganan.** El conjunto sin indicador pierde Δ = −0,0306 (p = 0,043): diferencia significativa **y** relevante según la regla pre-registrada. Con indicador la pérdida baja a Δ = −0,0276 (p = 0,038), que por magnitud queda como empate técnico.
2. **El indicador de programa no aporta:** Δ = +0,0030 (p = 0,453). El problema no es de intercepto sino de **estructura**: añadir la etiqueta no compensa la heterogeneidad.
3. **El modelo conjunto es peor que dos de los tres separados** pese a disponer de casi el triple de datos.
4. **Biología es el programa más difícil de modelar** (0,598 frente a 0,748 y 0,725), coherente con su heterogeneidad estructural y con su censura.

**Decisión (D23):** se adoptan **modelos separados por programa**, con el mismo algoritmo y el mismo protocolo en los tres, y se descarta el indicador de programa. Esto es compatible con la propuesta de grado: el compromiso es seleccionar **un algoritmo ganador** mediante comparación, no una única instancia entrenada. El algoritmo es único; las instancias ajustadas son tres. Queda pendiente el pronunciamiento formal de la dirección (**D-ALCANCE**).

> ⚠ **Matiz importante que conviene no confundir: «más datos» no es incondicional.** La
> curva de aprendizaje muestra que **más datos de la misma población** mejoran el modelo
> (§9.7.c); este experimento muestra que **más datos de poblaciones distintas lo empeoran**.
> No hay contradicción: son dos afirmaciones diferentes. El argumento para ampliar la
> muestra sigue siendo válido *dentro de cada programa*, y la ampliación a la FCBI se
> justifica por otras razones, no por agrandar el conjunto de entrenamiento de un modelo
> único.

### 9.7 Encargo de la dirección del 29-09: tres bloques metodológicos

Los tres bloques se ejecutaron bajo el **mismo protocolo que I-3 bis** (CV-5 anidada, 10 repeticiones, n = 80, 19 positivos, AUC-PR primaria, azar 0,2375), con toda transformación **dentro del Pipeline** y ajustada solo con el pliegue de entrenamiento: fijarla antes de la validación cruzada habría repetido la fuga de §7.3.

#### 9.7.a El PCA no puede respaldar una selección supervisada, y se demuestra midiéndolo (RC-042)

La pregunta planteada fue si el PCA confirma que las 6 variables de S3 son las mejores. **La respuesta metodológica se registró antes de ejecutar nada:** el PCA es **no supervisado**; busca direcciones de máxima varianza en X sin mirar nunca a *y*, y por construcción **no puede** demostrar que un conjunto de variables sea el mejor para predecir. Una variable de varianza minúscula puede ser el mejor predictor, y una de varianza enorme puede ser ruido. Presentar un gráfico de sedimentación como prueba de que la selección es correcta sería un error. Lo que sí admite es (a) medir redundancia y (b) generar una representación alternativa cuya **capacidad predictiva** sí se puede comparar. Se ejecutaron ambas.

**Redundancia:** las 19 variables necesitan **13 de 19 componentes** para explicar el 90 % de la varianza (10 para el 80 %, 15 para el 95 %). No son fuertemente redundantes. S3 necesita 5 de sus 6.

**Hallazgo central:** el promedio del primer semestre —la variable más predictiva del estudio— alcanza su carga máxima en **CP3, que explica solo el 8,3 % de la varianza**. Los dos primeros componentes están dominados por el bloque SABER 11 y la educación de los padres. **Quien hubiera seleccionado variables por varianza explicada habría descartado la única variable que predice.**

**Comparación predictiva** (referencia: S3 + Random Forest, AUC-PR 0,7418 ± 0,0105):

| Configuración | AUC-PR | AUC-ROC | Δ | p | Veredicto |
|---|:---:|:---:|:---:|:---:|---|
| 19 variables crudas · RF | 0,7176 | 0,8082 | −0,024 | 0,418 | empate estadístico |
| **PCA(k) sobre 19 · RF** | **0,3715** | 0,6294 | **−0,370** | <0,0001 | **peor (relevante)** |
| PCA(k) sobre 19 · Logística | 0,3819 | 0,6085 | −0,360 | <0,0001 | peor (relevante) |
| PCA(k) sobre S3 · RF | 0,6947 | 0,8616 | −0,047 | 0,295 | empate estadístico |
| PLS-DA(k) sobre 19 (supervisado) | 0,4637 | 0,6940 | −0,278 | <0,0001 | peor (relevante) |
| PLS-DA(k) sobre S3 (supervisado) | 0,4463 | 0,6394 | −0,296 | <0,0001 | peor (relevante) |

El PCA sobre las 19 variables **destruye la señal**: de 0,7418 a 0,3715. El PLS eligió **k = 1 componente en las 50 iteraciones**, lo que confirma que existe una sola dirección útil en los datos; al ser lineal no captura su forma, de ahí la distancia frente a Random Forest.

**Conclusión:** S3 se mantiene, y queda respaldado por **tres vías independientes**: la ablación anidada (§6.2), esta comparación de representaciones y la posterior bayesiana (§9.7.b). El PCA entra en el informe **como diagnóstico y como argumento metodológico**, no como criterio de selección (D24). Salidas: `src/pca_seleccion.py`, `src/_resultados_pca.json`.

#### 9.7.b Modelos bayesianos: no mejoran el acierto, pero destapan una colinealidad (RC-043)

La inferencia dentro de la validación cruzada usa **aproximación de Laplace** (gaussiana en la moda, con covarianza igual a la inversa del hessiano) en lugar de MCMC: cada ajuste con ADVI cuesta unos 101 s, lo que situaría los 500 reajustes del protocolo en unas 14 horas. Con 6 variables y n ≈ 64, la posterior de una logística con prior gaussiana es log-cóncava y casi gaussiana, de modo que la aproximación es fiel. La inferencia completa con PyMC/ADVI sí se ejecuta **una vez sobre la muestra entera**, para la posterior descriptiva.

| Modelo | AUC-PR | AUC-ROC | Δ vs. RF | p |
|---|:---:|:---:|:---:|:---:|
| Naive Bayes gaussiano | 0,4252 | 0,6226 | −0,317 | 0,0005 |
| **Logística bayesiana (Laplace)** | **0,6190** | 0,6956 | −0,123 | 0,0032 |
| Logística bayesiana · 19 variables | 0,5652 | 0,7646 | −0,177 | 0,0002 |
| Proceso gaussiano | 0,4354 | 0,6242 | −0,306 | <0,0001 |
| Logística L2 (MAP de la anterior) | 0,6045 | 0,6975 | −0,137 | 0,0020 |
| Naive Bayes · 19 variables | 0,4420 | 0,6915 | −0,300 | 0,0015 |
| S3 sin SABER-total · RF | 0,7207 | 0,7742 | −0,021 | 0,126 |

**Resultado 1 — ninguno supera a Random Forest**, y era esperable: salvo el proceso gaussiano son modelos de frontera lineal frente a un problema con interacciones. El dato que sí importa es otro: la logística bayesiana (0,619) **supera a su propio MAP regularizado** (0,605) con idénticas variables. Esa diferencia es exactamente lo que aporta integrar sobre la posterior en lugar de quedarse con la moda.

**Resultado 2 — hallazgo no buscado: colinealidad en el bloque SABER 11.** La posterior asigna a `icfes_total` un coeficiente **positivo y creíble: +1,558**, IC 94 % [+0,84, +2,25]. Leído literalmente significa que a mayor puntaje SABER 11, mayor riesgo académico: es sustantivamente imposible y es el síntoma clásico de **supresión por colinealidad**. Comprobado: `icfes_total` tiene **VIF 6,66** y **R² = 0,850** al regresarla sobre sus tres áreas, con correlación 0,920 frente a su suma. El modelo no estima un efecto: estima el contraste entre el total y sus partes.

- **A Random Forest no le afecta:** retirar el total deja 0,7207 frente a 0,7418 (empate estadístico, p = 0,126), así que **el modelo en producción no está comprometido**.
- **Pero cualquier lectura de coeficientes o importancias individuales dentro del bloque SABER 11 es inválida** mientras el total conviva con sus áreas. Hay que resolver **D-COLIN** antes de interpretar nada de ese bloque en el informe.

**Resultado 3 — coeficientes con efecto creíble** (variables tipificadas, IC 94 % que no contiene el cero): `prom_sem1` **−1,362** [−1,95, −0,77]; `icfes_total` +1,558 (artefacto, véase arriba); `icfes_lec` −0,934 [−1,71, −0,18]. Sin efecto distinguible: `sin_primer_semestre`, `icfes_mat`, `icfes_nat`. Es la tercera confirmación independiente de la dominancia del promedio de primer semestre.

**Resultado 4 — la incertidumbre por caso sostiene el cambio en la aplicación.** La anchura mediana del intervalo creíble del 94 % de la probabilidad individual es **0,359**, y en **43 de 80 estudiantes (54 %) supera 0,30**. Para más de la mitad de la población el modelo no está en condiciones de emitir un número. Confirma por vía independiente el defecto de calibración y refuerza D25: la aplicación debe mostrar **nivel de alerta y puesto relativo**, no un porcentaje. Salidas: `src/modelos_bayesianos.py`, `src/_resultados_bayes.json`.

#### 9.7.c Aprendizaje con pocos datos y curva de tamaño muestral (RC-044)

**Aclaración registrada antes de ejecutar:** el *one-shot / few-shot learning* en sentido estricto sirve para reconocer **clases nuevas** con uno o pocos ejemplos, y descansa en dos condiciones que aquí no se dan: un corpus grande de preentrenamiento del que transferir una representación, y una estructura por episodios con clases no vistas en entrenamiento. Este problema es tabular, binario y con ambas clases presentes desde el inicio. Aplicar una red siamesa literal sería ponerle un nombre de moda a un clasificador corriente. Lo que sí se traslada es el **mecanismo**: aprender una métrica y clasificar por cercanía a un prototipo de clase.

| Método | AUC-PR | AUC-ROC | Δ vs. RF | p |
|---|:---:|:---:|:---:|:---:|
| Prototipos de clase (ProtoNet tabular) | 0,4373 | 0,6461 | −0,305 | <0,0001 |
| NCA + prototipos (métrica aprendida) | 0,3559 | 0,6148 | −0,386 | <0,0001 |
| NCA + k vecinos | 0,6084 | 0,7934 | −0,133 | 0,019 |
| k vecinos sin métrica aprendida | 0,6435 | 0,7724 | −0,098 | 0,0021 |

**Resultado instructivo:** aprender la métrica con NCA **empeora** los prototipos (0,3559 frente a 0,4373). Con 19 positivos, NCA sobreajusta la métrica. Es justo el régimen en el que los métodos de few-shot dependen de un preentrenamiento externo que aquí no existe. No dice que la familia sea mala: dice que **sin corpus del que transferir, no hay atajo**.

**Lo que sí responde a la pregunta de fondo: la curva de tamaño muestral.** Submuestreando solo el pliegue de entrenamiento —el de prueba queda intacto— con hiperparámetros fijos:

| n entrenamiento | positivos | AUC-PR |
|:---:|:---:|:---:|
| 22 | 5,1 | 0,5487 |
| 28 | 7,0 | 0,6147 |
| 35 | 8,2 | 0,6701 |
| 44 | 10,2 | 0,6945 |
| 54 | 13,1 | 0,7380 |
| 64 | 15,2 | 0,7466 |

Ajuste por ley de potencias: **AUC-PR(n) = 0,838 − 8,843 · n^(−1,107)**, con R² = 0,994. **Techo asintótico estimado: 0,838.**

| n total | AUC-PR proyectado | Ganancia |
|:---:|:---:|:---:|
| 80 (hoy) | 0,749 | — |
| 160 (duplicar) | 0,797 | **+0,048** |
| 240 (triplicar) | 0,811 | +0,062 |
| 320 (cuadruplicar) | 0,819 | +0,070 |

**Lectura para la petición de datos a la Oficina de Sistemas:** duplicar la muestra compra en torno a **+0,05 de AUC-PR**; cuadruplicarla, unos +0,07. La curva satura pronto porque **el techo lo impone la información disponible, no el número de filas**. Las cohortes nuevas son muy valiosas —sobre todo porque habilitan la **validación externa que hoy no existe**, la limitación más seria del estudio—, pero si además se incorporasen asistencia (art. 58), fechas de pago y créditos inscritos frente a cancelados, subiría el techo mismo. **Más filas mejoran la estimación; más variables mueven el límite.**

**Cautela registrada:** extrapolar desde 64 casos de entrenamiento hasta 320 es una proyección de orden de magnitud, no una predicción. Supone que las cohortes nuevas se parecen a las actuales y que la prevalencia se mantiene. **Si las cohortes nuevas caen bajo el reglamento vigente desde 2022 y las actuales bajo el Acuerdo 015 de 2003, ese supuesto se rompe** — lo que conecta directamente con la decisión de régimen normativo aún abierta (**D-REGIMEN**). Salidas: `src/pocos_datos.py`, `src/_resultados_pocos.json`.

### 9.8 Validez temporal del target: el diseño longitudinal fracasa, y por qué

#### 9.8.a El 44 % de los eventos es simultáneo, no predicho (RC-035, RC-036)

**El 42 % de los casos positivos de Sistemas activa el art. 19 en el primer semestre** (8 de 19). Para ellos `prom_sem1` es **contemporáneo** al evento, no anterior: el modelo los **detecta**, no los **predice**. El patrón se repite en los tres programas con proporciones muy parecidas (42 %, 48 %, 41 %) — **26 de 59 eventos de la FCBI, el 44 %** —, de modo que es **estructural y no una peculiaridad de Sistemas**.

| Escenario | n | Positivos | AUC-PR | Línea base | Lift |
|---|:---:|:---:|:---:|:---:|:---:|
| Todos (lo reportado) | 80 | 19 (23,8 %) | 0,750 | 0,2375 | **3,16×** |
| Solo predicción real (evento en semestre ≥ 2) | 72 | 11 (15,3 %) | 0,473 | 0,1528 | **3,10×** |

El AUC-PR absoluto cae de 0,750 a 0,473, **pero el lift se mantiene** (3,16× → 3,10×): la caída se explica por la menor prevalencia, no por una pérdida de capacidad. El AUC-ROC sí se degrada (0,803 → 0,687), señal de que el ordenamiento empeora en la tarea genuinamente predictiva.

**El informe debe reportar las dos cifras con su explicación.** Presentar solo la primera sobreestimaría la capacidad de anticipación del modelo.

#### 9.8.b Las variables acumuladas no aportan (RC-038)

Se puso a prueba la hipótesis de que incorporar las variables acumuladas de los arts. 19–22 en un diseño por cortes semestrales sería «la vía de mejora con mayor retorno esperado». Método (`src/longitudinal.py`): panel estudiante-periodo de 1 290 filas y 234 estudiantes de la FCBI; para cada corte *k*, población en riesgo = quienes cursaron ≥ *k* periodos **sin** haber activado el art. 19 hasta *k*, y target = lo activan **después** de *k*. Siete variables acumuladas nuevas. Random Forest, CV-5 × 10 repeticiones, SEED = 42.

| Corte | En riesgo | Eventos | Solo ingreso | Solo acumuladas | Ingreso + acumuladas |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 202 | 27 (13,4 %) | **0,1837** (lift 1,37×) | 0,1521 (1,14×) | 0,1900 (1,42×) |
| 2 | 174 | 20 (11,5 %) | **0,1750** (lift 1,52×) | 0,0975 (**0,85×**) | 0,1545 (1,34×) |
| 3 | 138 | 7 (5,1 %) | — no viable (RC-008) | — | — |

1. **Las variables acumuladas no aportan.** Corte 1: Δ = +0,0062 (p = 0,514), empate. Corte 2: Δ = **−0,0204** (p = 0,044) — añadirlas **empeora** el modelo.
2. **Por sí solas son peores que el azar** en el corte 2: AUC-PR 0,0975 frente a una línea base de 0,1149 (lift 0,85×) y AUC-ROC 0,419, por debajo de 0,5.
3. **Causa verificada: no hay asociación.** Entre quienes sobrevivieron al corte, ninguna variable acumulada distingue a quienes activarán el art. 19 después. Corte 1: promedio ponderado acumulado 3,334 (activan) frente a 3,259 (no activan), p = 0,807 — incluso invertido. Corte 2: las cuatro variables con p > 0,5. El contraste sin condicionar es, en cambio, enorme: `prom_sem1` 2,293 frente a 3,283.
4. **El lift cae de 3,1× a 1,4×** al pasar al problema condicional.

**El hallazgo real es sustantivo: el evento del art. 19 es agudo, no gradual.** Exige reprobar el **100 % de los créditos de un periodo**: es un colapso puntual, no un deterioro progresivo. El estudiante mediocre sostenido no lo activa; lo activa quien tiene un semestre catastrófico. Por eso los promedios acumulados no lo anticipan — no es la acumulación lo que importa, es **un choque discreto**. Esto explica a la vez por qué el modelo de trayectoria completa sí funciona (captura a quienes colapsan en el primer semestre, el 44 % de los casos) y por qué el condicional no.

**Decisión (D22):** se descarta el diseño longitudinal para este target; el modelo vigente sigue siendo el de trayectoria completa (§9.2.a). Si se desea un producto con actualización semestral tipo SPADIES, **el target debe cambiar**. Conviene registrar que la recomendación de priorizar esta vía, formulada tanto por el estudio como por la auditoría, **era incorrecta**, y que los datos la refutaron.

#### 9.8.c ¿Falta de datos o mal planteamiento? El art. 20 daría +0,20 de AUC-ROC (RC-039)

La distinción importa porque los remedios son opuestos: conseguir más datos o replantear el problema. Experimento de **ancho de target**: se mantiene todo constante (mismo diseño por cortes, mismas variables, mismo Random Forest, mismo protocolo) y **solo se varía el umbral que define el evento**. Se compara con **AUC-ROC** porque, a diferencia del AUC-PR, es independiente de la prevalencia y por tanto comparable cuando la línea base cambia.

| Definición del evento | Corte | n | Eventos | Línea base | AUC-PR | **AUC-ROC** |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Art. 19 estricto (100 % de créditos) | 1 | 202 | 33 | 0,163 | 0,176 | **0,496** |
| Art. 19 estricto (100 % de créditos) | 2 | 174 | 26 | 0,149 | 0,136 | **0,468** |
| ≥ 75 % de créditos reprobados | 1 | 193 | 65 | 0,337 | 0,410 | **0,603** |
| ≥ 75 % de créditos reprobados | 2 | 151 | 35 | 0,232 | 0,287 | **0,567** |
| > 50 % (art. 20) | 1 | 176 | 104 | 0,591 | 0,656 | **0,647** |
| > 50 % (art. 20) | 2 | 120 | 52 | 0,433 | 0,554 | **0,673** |

1. **El AUC-ROC mejora de forma monótona al ampliar el target:** 0,496 → 0,603 → 0,647 en el corte 1; 0,468 → 0,567 → 0,673 en el corte 2. **Un salto de unos 0,20 producido únicamente por cambiar la definición del evento**, con la misma muestra, las mismas variables y el mismo algoritmo.
2. **El art. 19 estricto tiene AUC-ROC ≈ 0,47–0,50 en el problema condicional: cero discriminación.** No es señal débil, es ausencia de señal.
3. **Causa mecánica verificada — el umbral es un filo.** De los 1 232 periodos-estudiante regulares, 65 tienen el 100 % de los créditos reprobados (activan) frente a **104 entre el 60 % y el 99 % (no activan)**: hay **1,6 casi-activaciones por cada activación**. La diferencia entre disparar el artículo y no dispararlo es *aprobar un solo curso*, lo que introduce un componente cuasi-aleatorio que ningún modelo puede anticipar.

**Diagnóstico, con las tres causas jerarquizadas:**

1. **Definición del target (dominante, demostrado).** Un evento definido sobre un umbral extremo y discreto es intrínsecamente poco predecible con antelación.
2. **Tamaño de muestra (secundario, plausible).** Con 26–33 eventos el poder es limitado y los intervalos amplios, pero **no explica un AUC-ROC de 0,47**: con esa misma muestra y el target ancho sí se detecta señal (0,65–0,67).
3. **Variables insuficientes (no medible aquí).** Falta información sobre asistencia (art. 58, no entregada), situación financiera sobrevenida, carga laboral y factores personales — precisamente los que explicarían un colapso puntual. Un semestre catastrófico suele originarse fuera del expediente académico.

**Recomendación para el producto longitudinal:** redefinir el target sobre un fenómeno **gradual y de umbral amplio**, concretamente `> 50 % de créditos reprobados en el periodo` (**art. 20**), que además es el disparador real del acompañamiento institucional según el art. 23 y alcanza AUC-ROC 0,65–0,67. El modelo vigente de trayectoria completa **no se ve afectado** y sigue siendo el entregable.

#### 9.8.d Lo que sí predice un mal periodo futuro es haber tenido uno (RC-040)

Del carácter agudo del evento se derivó la hipótesis de que lo predictivo no sería el *nivel* del rendimiento sino su **inestabilidad**. Se probaron cuatro variables derivadas del panel, calculadas de forma expansiva y sin fuga, sobre el **target amplio del art. 20** —el único con señal—: `volatilidad`, `tendencia`, `peor_periodo` y `caida_max`.

| Conjunto | Corte 2 (n=120, ev=52) | Corte 3 (n=87, ev=22) |
|---|:---:|:---:|
| Ingreso + acumuladas | AUC-ROC 0,666 | AUC-ROC 0,605 |
| **+ inestabilidad** | **AUC-ROC 0,683** | **AUC-ROC 0,617** |
| Solo inestabilidad | AUC-ROC 0,654 | AUC-ROC 0,518 |

Asociación individual (Mann-Whitney):

| Variable | Corte 2 | Corte 3 | Veredicto |
|---|:---:|:---:|---|
| `volatilidad` | p=0,985 | p=0,317 | No predice |
| `tendencia` | p=0,160 | p=0,934 | No predice |
| `caida_max` | p=0,985 | p=0,255 | No predice |
| **`peor_periodo`** | **p=0,011** | **p=0,008** | **Significativa en ambos cortes** |

**La hipótesis de la volatilidad queda refutada**, pero `peor_periodo` sí predice y es la única variable consistentemente significativa en los dos cortes (3,098 frente a 3,257; 2,971 frente a 3,225). Es coherente con el marco del evento agudo: **lo que importa no es cuánto varía el estudiante, sino si ya tuvo un semestre malo**. La ganancia conjunta es pequeña pero consistente (+0,017 y +0,012 de AUC-ROC) y no justifica por sí sola un cambio de arquitectura, pero la variable es interpretable y accionable ante el Programa de Retención: *«ya tuvo un semestre por debajo de 3,1»* es un criterio que la institución entiende. Se incorpora `peor_periodo` al conjunto del diseño longitudinal y se descartan las otras tres. **El riesgo no es la inestabilidad: es el antecedente.**

## 10. Comportamiento cualitativo de los modelos prototipo (lecciones para el modelo principal)

> *Las lecciones de esta sección se formularon con los modelos prototipo del target
> antiguo. Se mantienen las que el trabajo posterior confirmó y se marcan las que quedaron
> desfasadas.*

1. **El intercambio Recall/Precisión es la decisión de producto.** La lección se confirma y se agudiza con el modelo vigente: no hay un punto que dé a la vez alta precisión y alta cobertura, y por eso se adoptó el esquema de tres niveles (§9.2.a-bis). Las cifras concretas que se citaban aquí —*«RF a umbral 0,29 detecta 8 de cada 10»*— **corresponden al target sustituido y no son vigentes**. Con el modelo del art. 19, cubrir el 79 % de los casos exige alertar sobre 46 de 80 estudiantes, y el 100 %, sobre 66. El informe debe presentarlo como decisión institucional, no como defecto del modelo.
2. **~~Ningún algoritmo domina en todo~~ [SUPERADA].** Era cierto con rejillas de búsqueda desiguales y partición fija. Bajo el protocolo anidado y con presupuesto de ajuste equilibrado, **Random Forest domina de forma clara y significativa** en el target del art. 19 (§9.2.a): supera al Árbol, a la Logística y a XGBoost con p ≤ 0,005, y empata con SVM. El test de comparación formal que esta lección pedía **ya se ejecutó** y sí permitió declarar un ganador. La parte que se sostiene es la causa: con muestras pequeñas, lo que parecía paridad entre familias era en buena medida ruido y artefacto del diseño experimental.
3. **La señal académica temprana aplasta a la socioeconómica** en estas cohortes (40.4 % vs. ≤12 % por variable): las socioeconómicas aportan en conjunto pero ninguna individualmente es decisiva (consistente con las pruebas no significativas §9.4).
4. **La preparación del dato importó más que el algoritmo.** La lección se sostiene, pero **hay que cambiarle la prueba**: el *+0,174 de AUC en Matemáticas II* que se citaba aquí procede de los modelos por asignatura **retirados** (§9.5) y no sirve como evidencia. La evidencia vigente es doble: (a) rehacer el diseño experimental —target, conjunto de variables, rejillas y validación anidada— llevó el mejor modelo de 0,569 a **0,745 de AUC-PR** sin cambiar de algoritmo (§9.2.a-ter), y (b) la recodificación corrigió la tasa de reprobación de Matemáticas II del 44 % aparente al 31,5 % real y recuperó 76 registros reales en Sistemas.
5. **~~Los modelos por materia funcionan con features mínimas~~ [RETIRADA].** La observación —que bastaba con el promedio global sin la materia, las veces cursada y la nota de Matemáticas I— era precisamente el síntoma de la fuga temporal: ese «promedio global» incluía semestres **posteriores** a la asignatura predicha (§7.1). Los cinco modelos están retirados. Lo que se conserva es el fenómeno descriptivo: la reprobación está fuertemente autocorrelacionada con el desempeño general, pero **medido en el pasado** no alcanza para predecirla (0,70–0,74 honesto frente a 0,865–0,939 inflado).
6. **El evento es agudo, no gradual, y eso fija el horizonte de anticipación alcanzable** (§9.8). Es la lección más transferible del estudio: la definición del evento condiciona la predictibilidad más que el tamaño de la muestra o la elección del algoritmo.
7. **Más datos de la misma población ayudan; más datos de poblaciones distintas no** (§9.6.b, §9.7.c). Duplicar la muestra dentro de un programa vale unos +0,05 de AUC-PR; fundir los tres programas en un modelo único cuesta −0,031.

## 11. Limitaciones vigentes (para el capítulo de limitaciones)

> Esta sección está pensada para trasladarse casi literalmente al capítulo de limitaciones
> del informe. El criterio es declarar lo que el trabajo **no** sostiene con la misma
> claridad con que se declara lo que sí sostiene, y cuantificarlo siempre que se haya
> medido. Las limitaciones se ordenan por gravedad, no por orden de descubrimiento.

### 11.0 Las cinco limitaciones de primer orden

#### 1. No existe validación externa ni temporal — la limitación más seria (P18)

**Todo el desempeño reportado proviene de remuestreo** (validación cruzada repetida) sobre **una sola muestra de 80 estudiantes de dos cohortes contiguas**. No hay conjunto de prueba externo, ni cohorte posterior, ni validación temporal. Las cifras del informe —incluida la principal, AUC-PR 0,745— son estimaciones de desempeño **interno**.

Ninguna técnica resuelve esto: hace falta otra cohorte. Se intentó mitigar con bootstrap .632+ y curvas de aprendizaje, pero son correcciones del mismo remuestreo, no una validación independiente; además, la adaptación del .632+ a AUC-PR **no es canónica** y se declara como tal. Con 19 positivos los intervalos son anchos por construcción.

La formulación honesta es: **este es un estudio exploratorio bien ejecutado, no una validación de un modelo desplegable.** Se solicitaron cohortes adicionales a la Oficina de Sistemas el 29-09; mientras no lleguen, el informe no puede afirmar capacidad de generalización.

#### 2. El 44 % de los eventos es simultáneo, no predicho (P19)

De los 19 positivos de Sistemas, **8 activan el art. 19 en el primer semestre**. En esos casos `prom_sem1` —la variable dominante— es **contemporánea** al evento, no anterior: el modelo no predice, **detecta**. El patrón es estructural en los tres programas (26 de 59 eventos de la FCBI, el 44 %).

Restringiendo a los casos genuinamente predictivos (evento en semestre ≥ 2), **el AUC-PR cae de 0,745 a 0,473** y el AUC-ROC de 0,803 a 0,687. Lo que sostiene la utilidad es que **el lift sobre el azar se mantiene en 3,10×**: la caída del valor absoluto se explica por la menor prevalencia. Aun así, **el informe debe reportar ambas cifras**; presentar solo la global sobreestimaría la capacidad de anticipación (§9.8.a).

#### 3. Las probabilidades que publica la aplicación no están calibradas (P17)

La aplicación Streamlit muestra una «probabilidad estimada» en porcentaje. **Ese número no significa lo que dice**, y dos vías independientes coinciden:

| Tramo mostrado | n | Dice | Ocurre realmente | Sesgo |
|---|:---:|:---:|:---:|:---:|
| 0,20 – 0,30 | 15 | 23,7 % | 6,7 % | +0,171 |
| 0,30 – 0,40 | 2 | 35,0 % | 0,0 % | +0,350 |
| 0,60 – 1,00 | 12 | 71,7 % | 91,7 % | −0,200 |

El Brier es 0,111 frente a 0,181 de la predicción trivial: **el modelo aporta, pero el número concreto no es interpretable como probabilidad.** La incertidumbre bayesiana por caso lo confirma por otra vía: la anchura mediana del intervalo creíble del 94 % es **0,359** y en **43 de 80 estudiantes (54 %) supera 0,30** (§9.7.b).

**Qué sí es sólido:** el **ordenamiento** de riesgo es estable — correlación de Spearman 0,894 entre repeticiones, y cada estudiante se mueve en promedio 6,2 puestos de 80. De ahí la recomendación: o se calibra (isotónica o Platt, dentro del pliegue externo) o **la aplicación deja de mostrar el porcentaje y muestra nivel de alerta y puesto relativo**. Hoy publica un número que el modelo no puede sostener. Decisión abierta **D-APP**.

#### 4. Colinealidad en el bloque SABER 11: los coeficientes de ese bloque no son interpretables (P16)

`icfes_total` tiene **VIF 6,66** y **R² = 0,850** al regresarla sobre sus tres áreas, con correlación 0,920 frente a su suma. La posterior bayesiana le asigna un coeficiente **positivo y creíble (+1,558)**, que leído literalmente diría que más puntaje SABER 11 implica más riesgo: es imposible, y es el síntoma clásico de supresión por colinealidad.

**El alcance exacto de la limitación importa:** a Random Forest **no le afecta** —retirar el total deja 0,7207 frente a 0,7418, empate estadístico (p = 0,126)—, así que **el modelo no está comprometido**. Lo que queda invalidado es **cualquier lectura de coeficientes, importancias o valores SHAP individuales dentro del bloque SABER 11** mientras el total conviva con sus áreas. Hay que resolver **D-COLIN** antes de interpretar ese bloque en el informe.

#### 5. Cambio de régimen normativo entre el Acuerdo 015 de 2003 y el reglamento de 2022

Las cohortes 2017-2 y 2018-1 se rigieron por el **Acuerdo 015 de 2003** (65 de 66 etiquetas de bajo rendimiento) y el modelo se desplegaría bajo el **reglamento de 2022**. Se mitiga re-derivando la etiqueta con la regla vigente, pero **el comportamiento de los estudiantes también estuvo condicionado por las reglas antiguas** —el umbral de 3,2 del art. 26 pudo inducir un esfuerzo diferencial—, y eso no es corregible con los datos disponibles.

La magnitud está medida: simulados sobre los mismos estudiantes, **ambos regímenes afectan a 20 personas pero solo 7 coinciden**. Es decir, la norma de 2022 habría señalado a otras 13 personas. No es un detalle de redacción: es una diferencia de identidad en dos tercios de los casos etiquetados.

El problema se extiende al futuro del estudio: la proyección de la curva de tamaño muestral (§9.7.c) supone que las cohortes nuevas se parecen a las actuales, y **si las nuevas caen bajo el reglamento de 2022 y las actuales bajo el Acuerdo 015, ese supuesto se rompe**. La elección de régimen de etiquetado (**D-REGIMEN**) está abierta y condiciona el resto.

### 11.1 Limitaciones de la muestra y del alcance

- **Muestra pequeña:** 80 expuestos y 19 positivos en Sistemas; 234 y 59 en la FCBI. Dos cohortes de una misma ventana histórica, que además **incluye la disrupción de la pandemia** (el periodo 2020-2 no existe institucionalmente).
- **Sin conjunto de prueba retenido**, decisión justificada y declarada: con 19 positivos, un holdout del 20 % tendría unos 4 positivos y cualquier métrica sobre él sería ruido.
- **Censura en Biología.** Biología tiene **15 estudiantes cuyo último estado es `MATRICULADO`** (18 % de su muestra), frente a **cero** en los otros dos programas. Su tasa de graduación del 7,1 % **no debe reportarse sin esa advertencia**: la desventaja real existe (24 `RETIRADO BR` con menos estudiantes), pero la cifra está sesgada por truncamiento de observación. Los 15 activos se excluyen del target de graduación y se conservan en el del art. 19, que sí es observable para ellos. Esa censura es también la que hizo inviable el target multiclase: **15 de los 20 estudiantes de la clase ACTIVO son de Biología** (§6.3).
- **Validez externa restringida a la FCBI de la Universidad de los Llanos**, y —dentro de ella— a cada programa por separado, dado que los modelos son separados (§9.6.b).
- **Desbalance de género** (84 % masculino en Sistemas) que limita cualquier análisis por género; las pruebas de §9.4 tienen poder muy bajo (15 mujeres, 15 repitentes).
- **Biología es el programa con peor desempeño del modelo** (AUC-PR 0,598 frente a 0,748 y 0,725): es, a la vez, el más heterogéneo y el más censurado.

### 11.2 Limitaciones de la información disponible

- **El techo lo impone la información, no el tamaño muestral (P21).** La curva ajustada —AUC-PR(n) = 0,838 − 8,843·n^(−1,107), R² = 0,994— sitúa el **techo asintótico en 0,838**: duplicar la muestra compra unos +0,048 y cuadruplicarla unos +0,070. Más filas mejoran la estimación; solo más variables mueven el límite. La extrapolación desde 64 casos de entrenamiento es una proyección de orden de magnitud, no una predicción.
- **Variable de asistencia ausente.** El art. 58 la hace obligatoria, luego debe registrarse, y sería el predictor natural del abandono. No fue entregada por la Oficina de Sistemas. Faltan igualmente situación financiera sobrevenida, carga laboral, fechas de pago y créditos inscritos frente a cancelados — precisamente el tipo de información que explicaría un colapso puntual, que suele originarse fuera del expediente académico.
- **Sin variables de desempeño psicosocial.** El formulario SIIF tiene unas 30 columnas inutilizables (más del 95 % de nulos).
- **Reconstrucción parcial de la regla del art. 19.** El **7 % de los cursos inscritos carece de nota**, por lo que la condición «100 % de los créditos inscritos» se aproxima por defecto.
- **Discrecionalidad administrativa no recuperable.** Ninguna reconstrucción reproduce el estado administrativo real (15/43 y 18/43 de acierto según el régimen aplicado): la oficina aplicó criterios no documentados en el reglamento.
- **Anomalías del extracto que solo la institución puede resolver (P20).** El estudiante **160004036** figura con estado final «retiro definitivo del programa con bajo rendimiento» y **ninguna nota reprobada** en los datos entregados —sus únicas observaciones son dos homologaciones aprobadas (3,7 y 3,4)—, además de arrastrar un «BAJO RENDIMIENTO» en 2018-1, anterior a todo el bloque de registros de 2019-0. La lectura más simple es que **el extracto no contiene toda su actividad**; si ocurre en un caso puede ocurrir en otros, y entonces algunas etiquetas serían incompletas. Por separado, **11 de 25 homologaciones incumplen el art. 46**.
- **57 estados finales inferidos** (20,7 % de los no graduados de la FCBI) y **541 estados imputados**: son trazables mediante la columna `ORIGEN`, pero **son inferencias, no registros administrativos**.

### 11.3 Limitaciones del diseño y de la estimación

- **El diseño longitudinal no funciona con este target**, y está documentado por qué: el evento del art. 19 es agudo y su umbral es un filo (1,6 casi-activaciones por activación). En el problema condicional el AUC-ROC es 0,47–0,50, es decir, **ausencia de señal, no señal débil** (§9.8.b, §9.8.c). El producto con actualización semestral tipo SPADIES **no es viable con el art. 19** y exigiría redefinir el target sobre el art. 20.
- **El target multiclase comprometido en la propuesta (E2) es inviable** y se sustituye por el binario de graduación (§6.3). Es un cambio de entregable y debe formalizarse con la dirección (**D-MULTI**).
- **La selección de hiperparámetros es inestable** con 19 positivos: la configuración ganadora varía entre pliegues. Se reporta esa variabilidad en lugar de ocultarla.
- **La selección de variables guiada por datos es inviable aquí**, y está cuantificado: el sesgo de selección fuera del pliegue es de **+0,150 de AUC-PR**, cinco veces el umbral de relevancia pre-registrado. Más allá de las dos o tres primeras posiciones, el ranking de importancia es ruido (§7.3).
- **Desviación de protocolo declarada** en la comparación anterior (I-3), donde el desempate se resolvió con la métrica secundaria. En la comparación vigente (I-3 bis) **no fue necesaria** ninguna desviación.
- **Supuesto de estabilidad normativa.** Se asume que el reglamento vigente no cambiará durante la vida útil del modelo. Si cambia, hay que recalcular la etiqueta y reentrenar.
- **El modelo está limitado por datos, no por sesgo** en el sentido estricto: la curva de aprendizaje sube de forma monótona y sin meseta (0,557 → 0,768). Esto justifica ampliar la muestra **dentro de cada programa**, no fundir programas (§9.6.b).

### 11.4 Lo que el informe no puede afirmar

Conviene cerrar el capítulo con una lista explícita de lo que queda fuera de alcance:

1. Que el modelo generalice a otras cohortes, programas o universidades.
2. Que las probabilidades mostradas sean interpretables como tales.
3. Que ninguna variable del bloque SABER 11 tenga un efecto individual determinado.
4. Que el art. 19 pueda anticiparse con semestres de antelación.
5. Que las etiquetas reflejen el régimen normativo bajo el que se desplegaría el modelo.
6. Que las variables socioeconómicas carezcan de relación con el rendimiento —solo que **en esta muestra y con este poder estadístico** no se detecta.

### 11.5 Correspondencia con el registro de problemas abiertos

Para no duplicar texto, la trazabilidad entre este capítulo y `PROBLEMAS_DETECTADOS.txt`:

| Problema | Dónde se trata | Estado |
|---|---|---|
| **P16** Colinealidad en SABER 11 | §11.0.4, §9.7.b | Abierto (**D-COLIN**) |
| **P17** Probabilidades sin calibrar | §11.0.3 | Abierto (**D-APP**) |
| **P18** Sin validación externa | §11.0.1 | Abierto; cohortes solicitadas el 29-09 |
| **P19** 44 % de eventos simultáneos | §11.0.2, §9.8.a | Medido y declarado |
| **P20** Anomalías del extracto | §11.2 | Abierto; solo la institución puede resolverlo |
| **P21** El techo lo impone la información | §11.2, §9.7.c | Medido y declarado |
| Régimen normativo | §11.0.5 | Abierto (**D-REGIMEN**) |

## 12. Pendientes que alimentarán este borrador

**Cerrado desde el corte anterior:** I-3 bis quedó **ejecutado** y es el resultado principal de §9.2.a (ya no está «en ejecución»). También se cerraron la extensión a Electrónica y Biología (WP-OE1.1 → §9.6), el target multiclase y su distribución (WP-OE1.3 → §6.3, con resultado de inviabilidad), los sub-modelos por corte (WP-OE1.4 → §9.8, con resultado negativo), la verificación formal de variables (WP-OE1.2 → §6.2), la comparativa con LogReg y SVM (WP-OE2.2 → §9.2.a) y la selección del ganador único (WP-OE3.2 → §9.2.a, sin desviación de protocolo). La **ponencia (E5)** está cerrada y aceptada (§14).

**Pendientes reales, por orden de prioridad:**

1. **Decidir las cinco cuestiones abiertas con la dirección** (§8): D-REGIMEN, D-MULTI, D-ALCANCE, D-COLIN y D-APP. Son bloqueantes para el cierre del informe: dos de ellas (D-COLIN y D-REGIMEN) afectan a cifras que irían impresas.
2. **Resolver la calibración o retirar el porcentaje de la aplicación** (WP-OE3.1): calibración isotónica o de Platt **dentro del pliegue externo**, o sustitución por nivel de alerta y puesto relativo.
3. **Conseguir cohortes adicionales** para la validación externa (P18), gestión iniciada el 29-09, y pedir en el mismo acto asistencia (art. 58), fechas de pago y créditos inscritos frente a cancelados, que son los que moverían el techo.
4. **Fijar el punto de operación** con el Programa de Retención, con su capacidad real de atención (art. 23).
5. **Aplicar el protocolo anidado al target `graduado`** (n = 90), hoy la única tabla del borrador que sigue con partición fija (§9.2.b).
6. **Si se retoma el producto longitudinal**, redefinir el target sobre el art. 20 (§9.8.c).

Cada avance añadirá su sección aquí vía `REGISTRO_CIENTIFICO.md`.

---

## 13. Ángulos de publicación que abrió la auditoría

Material con valor propio, más allá de los resultados predictivos:

1. **La fuga de información como riesgo sistemático** (§7). Tres niveles independientes, cada uno cuantificado: temporal, de hiperparámetros y de selección de variables. El más costoso —la selección— apareció *después* de haber documentado los otros dos, lo que ilustra lo difícil que es evitarla incluso estando advertido.
2. **La importancia MDI no mide relevancia predictiva** (§9.3.b). Demostrado con ruido aleatorio inyectado. Es de uso muy extendido en la literatura de minería de datos educativos.
3. **La definición del target pesa más que la elección del algoritmo, y se puede demostrar con un experimento controlado** (§9.8.c). Manteniendo constantes muestra, variables, algoritmo y protocolo, y variando **solo el ancho del evento**, el AUC-ROC sube unos **0,20 puntos**. Cambiar de algoritmo mueve unas 0,03. El método es sencillo y transferible: variar el ancho del target dejando todo lo demás fijo diagnostica si un problema es poco predecible por planteamiento o por falta de datos.
4. **Regularizar agresivamente es contraproducente con clase rara** (§7-bis.10). Resultado contraintuitivo, explicado por el bloqueo de cortes sobre la clase minoritaria.
5. **Comparar algoritmos con presupuestos de ajuste desiguales invalida la comparación** (§7-bis.9). Sesgo poco discutido: favorece a los algoritmos con más hiperparámetros. Medido aquí, la recuperación de XGBoost (+0,102) fue **mayor que la distancia entre el primero y el segundo** (+0,032).
6. **Dos regímenes normativos que persiguen fenómenos distintos** (§11.0.5). Con los mismos estudiantes, ambos afectan a 20 personas pero solo 7 coinciden: la norma de 2022 habría señalado a otras 13. Hallazgo con valor institucional propio, independiente del modelo.
7. **El PCA no puede respaldar una selección de variables supervisada, y se demuestra midiéndolo** (§9.7.a). El caso es particularmente nítido: la variable más predictiva del estudio carga en CP3, que explica el 8,3 % de la varianza. Quien hubiera seleccionado por varianza explicada habría descartado la única variable que predice.
8. **«Más datos» es una recomendación que hay que cualificar** (§9.6.b). Más datos de la misma población mejoran el modelo; más datos de poblaciones distintas lo empeoran (−0,031 al fundir tres programas con el triple de muestra). Y la curva de tamaño muestral permite poner cifras a la negociación de datos con la institución: duplicar la muestra vale +0,048, con techo asintótico en 0,838.
9. **Los métodos de pocos datos no ayudan sin un corpus del que transferir** (§9.7.c). Aprender la métrica con NCA **empeora** los prototipos. Es un resultado útil frente a la expectativa de que el few-shot resuelva muestras pequeñas en datos tabulares.
10. **Una clase minoritaria puede ser un artefacto de la ventana de observación, no un fenómeno** (§6.3). La clase ACTIVO del target multiclase era, en el 75 % de los casos, el grupo censurado de Biología. Y en estas cohortes el rezago afecta al 63 % de quienes no desertan: una clase que agrupa a dos tercios de la población no discrimina.

---

## 14. Productos ya conseguidos

### 14.1 Ponencia en evento científico (entregable E5) — cerrado

El resumen extenso derivado del trabajo fue **aceptado en el CICI 2026** (ID 129), con publicación en **Springer LNCS** en formato de 4 páginas. El evento se celebra del **7 al 9 de octubre de 2026 en Villavicencio**, y la presentación está construida sobre la plantilla oficial del congreso. El entregable E5 queda cerrado.

**Advertencia obligatoria de coherencia.** La ponencia **reporta el target antiguo**, porque así se sometió y así se aceptó, y **no se reescribe**: modificar un trabajo ya aceptado no sería legítimo. El informe final debe por tanto:

1. Citar la ponencia como producto del proyecto, no como fuente de cifras vigentes.
2. Señalar de forma explícita que sus resultados corresponden a la iteración anterior del target, y remitir a §9.2.a para las cifras definitivas.
3. Llevar preparada la respuesta a la pregunta previsible en la sesión: **por qué cambió la definición de la variable objetivo** — la respuesta corta es que el target original era tautológico (§6.1), y que el cambio es exactamente el tipo de iteración que CRISP-DM contempla.

El material de la ponencia vive en `paper_congreso/` y tiene **régimen de documento publicado**: no se toca.

### 14.2 Otros productos

- **Aplicación Streamlit** con el esquema de alerta de tres niveles (`app.py`), pendiente de la decisión sobre qué cifra muestra (**D-APP**, §11.0.3).
- **Pipeline reproducible** en `src/`: toda cifra del informe es regenerable por script, con SEED = 42. Es la contribución metodológica que elimina de raíz la clase de errores «número editado a mano».
- **`REGISTRO_CIENTIFICO.md`** (RC-001 a RC-044) como bitácora de decisiones con fecha, método, resultado y destino en el informe. Es lo que permite defender la trazabilidad de cada afirmación ante un jurado.
