# AUDITORÍA METODOLÓGICA — septiembre 2026

> ## ⚠️ DOCUMENTO DE DIAGNÓSTICO — cita cifras antiguas porque es lo que audita
>
> Esta auditoría (3 de septiembre de 2026) es **el documento que detectó** los problemas del
> target antiguo y de los modelos por asignatura. Que cite `PROMEDIO_CARRERA < 3,0`,
> Recall+ 0,816 o AUC 0,865–0,939 **no es un desfase: es su objeto de estudio**.
>
> Lo que vino después y este documento todavía no podía recoger: el target del art. 19 ya
> implementado (RC-017, RC-020), la comparación definitiva de los cinco algoritmos
> (RC-033), la medición de la fuga por selección de variables en +0,1499 (RC-032), la
> inviabilidad del target multiclase (RC-041), el fracaso del diseño longitudinal
> (RC-038) y los tres bloques del encargo de la dirección del 29-09 (RC-042 a RC-044).
>
> **No se reescribe.** Para el estado vigente: `PLAN_DE_TRABAJO.md` y `PROBLEMAS_DETECTADOS.txt`.

### Revisión exhaustiva previa a la construcción del modelo comprometido (E2) y del informe final (E4)
**Alcance:** arquitectura del proyecto, coherencia documental, validez del diseño experimental y dictamen sobre el modelo de reprobación por asignatura.
**Método:** re-ejecución del pipeline con los datos vigentes; experimentos de ablación y de validez temporal con validación cruzada repetida (5 pliegues × 6–15 repeticiones, SEED=42). Todas las cifras de este documento son reproducibles.

---

## 0. Resumen ejecutivo

La auditoría confirma que **la recodificación, la trazabilidad de los datos y la infraestructura del proyecto son sólidas**. No se encontraron errores de implementación ni cifras inventadas: todo número publicado se regenera desde el código.

Sin embargo, se detectaron **tres problemas de validez** que afectan la interpretación de los resultados y que deben resolverse antes de construir el modelo comprometido:

| # | Hallazgo | Severidad | Afecta a |
|---|---|---|---|
| H-1 | El target `rendimiento_bajo` es parcialmente tautológico: para el 26 % de la muestra el promedio de carrera *es* el primer semestre | **Alta** | Modelo principal, paper, informe |
| H-2 | Los modelos por asignatura usan información posterior a la asignatura que predicen (70–83 %) | **Alta** | Modelo de reprobación |
| H-3 | El 18 % de la muestra tiene `prom_sem1` imputado con la mediana, y ese subgrupo no es comparable | Media | Modelo principal |

**Dictamen sobre la propuesta del asesor:** tiene razón en descartar el modelo de reprobación, pero *por una razón distinta* a la que plantea. Ver §3.

---

## 1. H-1 · El target `rendimiento_bajo` está contaminado

### Qué se encontró

`rendimiento_bajo` se define como `PROMEDIO_CARRERA < 3.0`. `PROMEDIO_CARRERA` es el promedio acumulado institucional, que **incluye el primer semestre**. La variable predictora dominante es `prom_sem1`.

Cuando un estudiante cursa un solo periodo y se retira, su promedio de carrera es aritméticamente su primer semestre:

| Subgrupo | n | % muestra | correlación `prom_sem1` ~ `PROMEDIO_CARRERA` | dif. media absoluta |
|---|---|---|---|---|
| 1 periodo cursado | 17 | 19 % | **0,921** | 0,112 |
| ≤2 periodos | 23 | 26 % | 0,906 | 0,217 |
| ≤3 periodos | 35 | 39 % | 0,858 | 0,389 |
| ≥6 periodos | 40 | 44 % | **0,324** | 0,300 |

La correlación global (0,823) está inflada por los desertores tempranos. En la población donde la predicción tiene sentido (≥6 periodos) la relación es débil.

### Consecuencia medida

AUC por validación cruzada repetida (RF, 5 pliegues × 6 repeticiones):

| Población | 18 variables | SIN `prom_sem1` | SOLO `prom_sem1` |
|---|---|---|---|
| Todos (n=90) | 0,761 | **0,483** | 0,797 |
| ≥3 periodos (n=57) | **0,546** | 0,516 | 0,533 |

Dos lecturas, ambas incómodas:

1. **Sin `prom_sem1` el modelo es una moneda al aire (AUC 0,483).** Las otras 17 variables —socioeconómicas, familiares, SABER 11— no aportan capacidad predictiva sobre este target.
2. **Al excluir a los desertores tempranos el modelo se desploma a 0,546.** Es decir: el modelo no predice rendimiento académico; en buena medida *detecta a quien ya se fue*, porque en ese caso el target y la variable predictora son casi el mismo número.

### Qué NO significa

Las métricas publicadas (Recall+ 0,816, AUC 0,752) **están correctamente calculadas**. No hay error de código ni de validación cruzada. El problema es de **construcción del target**, y cambia lo que las métricas significan, no su valor numérico.

### Contraste con `graduado`

El target de graduación se comporta mejor y de forma más creíble:

| Población | 18 variables | SIN `prom_sem1` |
|---|---|---|
| Todos (n=90) | 0,809 | 0,651 |
| ≥6 periodos (n=40) | 0,870 | **0,876** |

Entre quienes persistieron, las variables de ingreso **sí** predicen la graduación sin necesidad de `prom_sem1`. Este target es defendible tal como está. *(Cautela: el subgrupo ≥6 periodos tiene 35 graduados de 40 — muy desbalanceado, la cifra es orientativa.)*

### Recomendación

Redefinir el target de rendimiento con una de estas opciones, **decidida antes de volver a entrenar**:

- **(a) Exposición mínima:** exigir ≥2 periodos cursados para entrar al target de rendimiento. Reduce n pero elimina la tautología. Los excluidos pasan al modelo de deserción, donde su información sí es válida.
- **(b) Target sin el primer semestre:** `promedio de semestres 2..n < 3.0`. Rompe la circularidad de raíz y mantiene a `prom_sem1` como predictor legítimo.
- **(c) Renombrar y reencuadrar:** aceptar que el modelo detecta "trayectoria corta con bajo desempeño inicial" y reportarlo como tal, no como predicción de rendimiento.

La opción **(b) es la técnicamente más limpia** y es compatible con el objetivo del proyecto. La (a) introduce sesgo de supervivencia que ya está advertido en RC-008.

---

## 2. H-3 · Imputación de `prom_sem1` en el 18 % de la muestra

16 de 90 estudiantes no tienen registro de promedio del primer semestre y reciben la **mediana (3,4)**. Ese subgrupo no es comparable con el resto:

| | imputados (n=16) | con dato real (n=74) |
|---|---|---|
| `rendimiento_bajo` | 12 % | 49 % |
| `graduado` | 19 % | 43 % |

Se está insertando un valor "neutro" en la variable más influyente del modelo, para un grupo cuyo comportamiento es marcadamente distinto. Los datos no faltan al azar: faltan porque esos estudiantes no completaron un primer semestre evaluable.

**Recomendación:** sustituir la imputación por mediana por (i) indicador explícito `sin_primer_semestre` + imputación, o (ii) exclusión razonada de esos 16 casos del modelo de rendimiento, documentando el criterio. La opción (i) conserva la muestra y deja que el modelo aprenda que "no tener primer semestre" es en sí una señal.

---

## 3. H-2 · Dictamen sobre el modelo de reprobación por asignatura

### La objeción del asesor

Que el modelo es precipitado y usa pocas variables. **Confirmo que debe descartarse en su forma actual, pero el motivo es más grave que el número de variables.**

### El problema real: las variables no existen en el momento de predecir

Las cinco asignaturas críticas son de **primer y segundo semestre**. La variable dominante, `prom_global`, es el promedio del estudiante en *todas las demás asignaturas de la carrera*:

| Asignatura | Semestre | % de `prom_global` que proviene de semestres POSTERIORES |
|---|---|---|
| Matemáticas I | 1 | **83 %** |
| Fundamentos de Programación | 1 | **83 %** |
| Álgebra Lineal | 1 | **83 %** |
| Matemáticas II | 2 | **70 %** |
| Física I | 2 | **70 %** |

Para "predecir" que un estudiante reprueba Matemáticas I (semestre 1) el modelo usa su desempeño en los semestres 2 a 10. **Eso no es predicción, es retrodicción.** El AUC de 0,865–0,939 mide una correlación contemporánea trivial: quien tiene mal promedio general reprueba materias.

### Verificación por ablación

AUC media (5 pliegues × 10 repeticiones):

| Asignatura | Completo | Sin `veces_cursada` | Solo `prom_global` | Solo `veces_cursada` |
|---|---|---|---|---|
| Álgebra Lineal | 0,932 | 0,934 | 0,892 | 0,367 |
| Física I | 0,869 | 0,863 | 0,871 | 0,487 |
| Fund. Programación | 0,968 | 0,958 | 0,930 | 0,551 |
| Matemáticas I | 0,953 | 0,791 | 0,791 | 0,613 |
| Matemáticas II | 0,846 | 0,776 | 0,735 | 0,680 |

`prom_global` sostiene el modelo casi por sí solo. `veces_cursada` por separado es inútil o inverso (0,367–0,680) y, además, tampoco está disponible antes de cursar la asignatura.

### La prueba decisiva: ¿queda algo si se respeta el tiempo?

Para las asignaturas de **semestre 2** se puede hacer un test limpio: predecir con información observada **únicamente en el semestre 1**.

| Predictores (todos del semestre 1) | Matemáticas II | Física I |
|---|---|---|
| Solo variables de ingreso (SABER 11 + socioeconómicas) | 0,414 | 0,506 |
| `prom_sem1` real | 0,542 / 0,696\* | 0,545 / 0,679\* |
| `prom_sem1` + `nota_mat1` | 0,658 / **0,707**\* | 0,687 / **0,740**\* |
| Todo el semestre 1 (+ nº asignaturas) | **0,732** / 0,702\* | 0,553 / 0,648\* |

\* RF / Regresión logística. Con n=54 la logística resulta más estable que el bosque.

**Hallazgos:**

1. Las variables de **ingreso por sí solas no predicen nada** (AUC 0,41–0,51 = azar). Resultado negativo valioso para el informe.
2. Existe una señal **real pero modesta**: AUC ≈ 0,70–0,74 usando el desempeño del primer semestre para anticipar la reprobación en el segundo.
3. Esa señal está **muy lejos** del 0,865–0,939 reportado. La diferencia es exactamente el tamaño de la fuga temporal.

### Dictamen

**Descartar el modelo de reprobación en su forma actual: sí.** No es publicable ni defendible; un jurado que revise las features lo desmonta en dos preguntas.

**Descartarlo por completo del proyecto: no necesariamente.** Existe una versión honesta y pedagógicamente interesante —*predecir la reprobación de Matemáticas II y Física I con el desempeño del primer semestre*— con AUC ≈ 0,70–0,74. Es un resultado modesto pero **temporalmente válido y accionable**: la alerta llega antes de que el estudiante curse la asignatura.

Mi recomendación concreta:

- **Retirar** los cinco modelos actuales del repositorio, la app y el informe. Están inutilizables.
- **Conservar el índice de criticidad** como resultado descriptivo (ya está así en el paper; es correcto).
- **Reconstruir opcionalmente** una versión reducida y honesta limitada a las dos asignaturas de semestre 2, si el cronograma lo permite. Si no lo permite, **omitirla sin pérdida**: no es un entregable comprometido en la propuesta.
- **Reportar la fuga como hallazgo metodológico** en el informe final. Una fuga temporal detectada y corregida por el propio autor es un punto a favor, no en contra.

---

## 4. Estado de la documentación

**Coherente y actualizada.** Verificado: `README.md`, `PLAN_DE_TRABAJO.md`, `PLAN_OPERATIVO_AGENTES.md`, `REGISTRO_CIENTIFICO.md` (RC-001…RC-011) y `KANBAN_AGENTES.md` describen el estado real del pipeline. Las cifras citadas (n=90, 35 graduados, 38 en rendimiento bajo, 2 566 filas de historial, 8 486 de detalle) se regeneran correctamente.

**Sin desfases pendientes.** El estado 🔴 de E5 es correcto: la ponencia se realiza el próximo mes.

**Ajuste aplicado:** `paper_congreso/` queda registrado en el README y se adopta como **base fundamental del informe final** (E4), según decisión del estudiante.

**Duplicación advertida (sin acción):** 16 artefactos están duplicados byte a byte entre `src/` y `Fase 3/`–`Fase 4/`. Hoy son idénticos; al re-entrenar quedarán desincronizados en silencio. Conviene decidir si las carpetas de fase guardan artefactos o solo los documentan.

---

## 5. Impacto sobre el paper del congreso

El paper **no contiene errores de cálculo** y ya no menciona los modelos de reprobación (decisión RC-011), lo que resultó afortunado: el problema H-2 no lo alcanza.

Sí lo alcanza H-1, en una afirmación: *"Random Forest con umbral 0,29 obtuvo la mayor exhaustividad (0,816), detectando 8 de cada 10 estudiantes en riesgo"*. Parte de esa detección corresponde a estudiantes que ya habían abandonado.

No propongo modificar el paper —está cerrado y la ponencia es el próximo mes—, pero **conviene llevar preparada la respuesta** si alguien pregunta por la definición del target. La respuesta honesta y sólida es: *"el promedio de carrera incluye el primer semestre; en la muestra hay desertores tempranos donde ambos coinciden, y por eso el informe final redefine el target excluyendo el primer periodo"*. Eso demuestra dominio del problema.

---

## 6. Plan incremental propuesto

Cada paso se entrega y se aprueba por separado antes de continuar.

| Paso | Acción | Entregable | Depende de |
|---|---|---|---|
| **I-1** | Decidir la redefinición del target de rendimiento (opciones a/b/c de §1) | Entrada RC + criterio pre-registrado | **Decisión del estudiante** |
| **I-2** | Corregir la imputación de `prom_sem1` (indicador `sin_primer_semestre`) | `src/preprocessing.py` + RC | I-1 |
| **I-3** | Re-entrenar el modelo principal con target corregido y comparar honestamente contra el actual | Tabla antes/después + RC | I-1, I-2 |
| **I-4** | Retirar los modelos de reprobación de `src/`, `app.py` y documentos | Repo limpio + RC de la fuga | — (independiente) |
| **I-5** | Ejecutar WP-OE1.1 (verificación de Electrónica y Biología) | `Fase 2/08_verificacion_fcbi.md` | I-3 |
| **I-6** | Target multiclase de trayectoria (WP-OE1.3) con la regla de viabilidad de RC-008 | Dataset + RC | I-5 |

**El paso I-1 requiere tu decisión antes de que yo avance.** Es la bifurcación que condiciona todo lo demás.

---

# ADENDA · Revisión a la luz del Reglamento Estudiantil

Incorporado `reglamento_estudiantil_unillanos.md`. **Cambia la respuesta al problema H-1** y aporta la definición que faltaba.

## A.1 · La universidad ya define "bajo rendimiento", y no es lo que usamos

> **ARTÍCULO 19°. BAJO RENDIMIENTO ACADÉMICO.** Pierde la condición de estudiante quien repruebe el **100 % de los créditos inscritos** *y* su promedio ponderado de asignaturas cursadas sea inferior a **3,0**, *o* quien repruebe **por cuarta vez** un curso.

El target del proyecto es `PROMEDIO_CARRERA < 3.0`: **solo la mitad de una conjunción**. La definición institucional exige, además, haber reprobado la totalidad de los créditos del periodo — y añade una vía alterna (cuarta reprobación) que hoy se ignora por completo.

Esto explica H-1 desde otro ángulo: el target no estaba solo mal *medido*, estaba mal *definido*.

## A.2 · Existe verdad de campo en los datos

`historial_estados_recod.xlsx` contiene el estado administrativo que la universidad aplicó realmente:

| Estado | Registros |
|---|---|
| BAJO RENDIMIENTO | 36 |
| RETIRADO BR | 29 |
| RETIRO DEFINITIVO DEL PROGRAMA CON BAJO RENDIMIENTO | 1 |
| **Estudiantes únicos afectados** | **40 de 90** |

Comparado con el target actual:

| | estado BR = 0 | estado BR = 1 |
|---|---|---|
| `PROMEDIO_CARRERA` ≥ 3,0 | 44 | **8** |
| `PROMEDIO_CARRERA` < 3,0 | **6** | 32 |

Coinciden en el 84 % de los casos, pero **discrepan en 14 estudiantes**: 8 fueron sancionados por la universidad pese a tener promedio ≥ 3,0 (vía "cuarta reprobación" o reprobación total de un periodo puntual), y 6 tienen promedio < 3,0 sin que la universidad los sancionara.

Dato adicional: **ninguno de los 40 estudiantes con estado BR se graduó.** El estado es casi terminal.

## A.3 · Con el target institucional, las 17 variables sí aportan

Esta es la corrección más importante a lo que te reporté antes:

| Target | 18 variables | **sin `prom_sem1`** | solo `prom_sem1` |
|---|---|---|---|
| `PROMEDIO_CARRERA < 3,0` (actual) | 0,752 | **0,469** ← azar | 0,795 |
| Estado BR institucional (art. 19) | 0,710 | **0,642** ← señal | 0,621 |

Con el target institucional, las variables socioeconómicas y de SABER 11 **dejan de ser ruido** (0,469 → 0,642) y `prom_sem1` deja de dominar (0,795 → 0,621). El modelo se vuelve equilibrado en lugar de depender de una sola variable circular.

Conclusión: **las 17 variables nunca fueron el problema. El target lo era.**

## A.4 · Advertencia honesta sobre lo que sí es difícil

De los 40 estudiantes con estado BR, **13 lo recibieron ya en el primer semestre**. Predecirlos con datos del primer semestre no es predicción.

Al restringir a los 27 casos donde el BR aparece en semestre ≥ 2 (única tarea genuinamente predictiva):

| Escenario | 18 variables |
|---|---|
| BR institucional, todos (n=90) | 0,710 |
| **BR institucional solo si ocurre en semestre ≥ 2 (n=77)** | **0,577** |

Anticipar el bajo rendimiento *futuro* con información de ingreso y primer semestre es **difícil**: AUC 0,577. Ese es el techo real de un modelo de foto única.

**No es un fracaso: es el argumento empírico que justifica el diseño longitudinal ya previsto** (WP-OE1.4). Un corte único al primer semestre no alcanza; el modelo debe reevaluar al estudiante cada periodo con la información acumulada. Ahora tenemos la evidencia que lo demuestra.

## A.5 · El reglamento aporta variables nuevas y mejores

Los artículos 20–22 definen una escalera institucional de riesgo, hoy no explotada, **calculable con los datos disponibles** (`CREDITOS` sin nulos):

| Artículo | Condición | Eventos detectados |
|---|---|---|
| Art. 20 | Reprueba > 50 % de los créditos del periodo | 73 periodos-estudiante (15 %) |
| Art. 19 | Reprueba el 100 % de los créditos del periodo | 24 periodos-estudiante (5 %) |
| Art. 21 | Reprueba un curso por 2ª vez | 181 casos |
| Art. 22 | Reprueba un curso por 3ª vez | 32 casos |
| Art. 19 (vía alterna) | Reprueba un curso por 4ª vez | 1 caso |

Estas variables son **institucionalmente significativas y accionables**, a diferencia del estrato o el puntaje SABER. Además, el **artículo 23** obliga al Programa de Retención Estudiantil a acompañar a quienes caen en los artículos 19, 20 y 21: **ese es el disparador operativo real que el modelo debería anticipar**, y le da al proyecto un destinatario institucional concreto.

## A.6 · Decisiones previas que el reglamento respalda

- **Regla NO RENOVACIÓN ≥ 2 periodos** (RC-002, RC-006): el parágrafo del art. 17 establece que se puede omitir la renovación **máximo por dos periodos consecutivos**. La regla inferida coincide con la norma.
- **Cursos intersemestrales (`C`)**: el art. sobre intersemestrales confirma que **cuentan para el promedio ponderado de carrera pero no para el promedio de semestre**. Como `prom_sem1` y `PROMEDIO_CARRERA` provienen de los archivos institucionales, el tratamiento actual es correcto.
- **Validaciones (`V`)**: cuentan para ambos promedios. Correcto en el pipeline.
- **Nota mínima aprobatoria 3,0**: confirma el umbral usado en toda la recodificación.

## A.7 · Recomendación revisada para el paso I-1

Sustituyo mi recomendación anterior (opción b) por esta, mejor fundamentada:

> **Adoptar el estado administrativo de bajo rendimiento (art. 19) como variable objetivo**, en lugar de `PROMEDIO_CARRERA < 3.0`.

Motivos: es la definición oficial, es verdad de campo aplicada por la universidad, no arrastra circularidad, hace que las 17 variables recuperen valor, y es el evento que dispara la intervención institucional (art. 23).

Con dos condiciones de diseño, pre-registradas:

1. **Excluir del entrenamiento los 13 casos con BR en el primer semestre** cuando se prediga desde datos del primer semestre (o modelarlos aparte). No se puede anticipar lo simultáneo.
2. **Reportar el AUC honesto (~0,58) del corte único** junto al longitudinal, para que la mejora del diseño por cortes quede demostrada y no asumida.

---

# ADENDA B · Cambio de régimen normativo y comparación de algoritmos

## B.1 · Las etiquetas provienen del reglamento anterior

El reglamento vigente es de diciembre de 2021 y rige desde 2022; sustituyó al **Acuerdo Superior N.º 015 de 2003**. Las cohortes estudiadas (2017-2 y 2018-1) vivieron casi toda su trayectoria bajo el régimen antiguo.

Verificación sobre los estados administrativos de bajo rendimiento:

| Periodo del estado BR | Registros |
|---|---|
| 2017-2 a 2021-2 (**reglamento 2003**) | **65** |
| 2022-1 en adelante (**reglamento 2022**) | **1** |

De los 43 estudiantes con estado BR, **42 lo recibieron bajo la norma anterior**. Esto corrige la adenda A: el target institucional es válido como verdad de campo, pero **no es la aplicación del art. 19 vigente**.

## B.2 · Los dos regímenes no son equivalentes

| Criterio | **Acuerdo 015 de 2003** (arts. 25–26) | **Reglamento 2022** (arts. 19–21) |
|---|---|---|
| Unidad de medida | **Asignaturas** | **Créditos** |
| Disparador de riesgo | Pierde **> 50 %** de las asignaturas **habiendo aprobado al menos una** | Reprueba el **100 %** de los créditos |
| Umbral de promedio | Renueva solo si promedio **≥ 3,2** | Pierde la condición si promedio **< 3,0** |
| Reprobación reiterada | 3.ª pérdida de una asignatura → renovación condicionada al promedio 3,2 | 4.ª reprobación → pérdida de la condición, **sin condición de promedio** |
| Pérdida > 50 % de créditos | No contemplada como categoría propia | **Art. 20:** solo restricción de carga (inscribir únicamente los reprobados) |
| Segunda reprobación | Debe inscribirla por 3.ª vez si promedio ≥ 3,2 | **Art. 21:** máximo 4 cursos |
| Consecuencia máxima | Pierde el derecho a renovar; reingreso tras 1 periodo | Pierde la condición de estudiante |

**La 4.ª reprobación es la fatal en ambos regímenes**; el reglamento de 2022 se limita a hacerlo explícito, mientras que el de 2003 lo dejaba implícito en la progresión de los artículos 25–26. La diferencia real está en otra parte.

### La diferencia real: capturan poblaciones casi disjuntas

Reconstruyendo ambas reglas sobre las mismas cohortes:

| Situación | Eventos periodo-estudiante |
|---|---|
| 2003 art. 26 — pierde la renovación | 25 |
| 2003 art. 26 — disparado pero salvado por promedio ≥ 3,2 | 10 |
| 2022 art. 19 — pierde la condición | 21 |
| 2022 art. 20 — solo restricción de carga (sin expulsión) | 49 |

| Estudiantes distintos (de 90) | n |
|---|---|
| Pierden condición bajo **2003** | 20 |
| Pierden condición bajo **2022** | 20 |
| **En ambos regímenes** | **7** |
| Solo bajo 2003 | 13 |
| Solo bajo 2022 | 13 |

Mismo número de afectados, **pero solo 7 son las mismas personas**. La causa es precisa y verificada:

- **Los 13 que solo caen bajo 2003** hoy caerían únicamente en el **art. 20**: reprobación parcial que ahora se sanciona con restricción de carga, no con expulsión. El régimen actual los conserva.
- **Los 13 que solo caen bajo 2022 reprobaron el 100 % de sus asignaturas.** El art. 26 de 2003 exigía literalmente *"habiendo aprobado por lo menos una"*, de modo que **la reprobación total quedaba fuera de su alcance**. El art. 19 de 2022 cierra ese vacío.

Los dos regímenes no son uno más estricto que el otro: **apuntan a fenómenos distintos**. El de 2003 perseguía la reprobación parcial con promedio bajo; el de 2022 persigue el colapso total del periodo y la reincidencia en un mismo curso.

*(La 4.ª reprobación es empíricamente marginal: 2 eventos en 1 estudiante. La reconstrucción es además una cota inferior —solo ve cursos con nota registrada— y reproduce 15/43 y 18/43 de los estados administrativos reales, lo que indica criterios o discrecionalidad de la oficina no recuperables desde los datos.)*

### Consecuencia para el modelo

Un modelo entrenado con etiquetas del régimen 2003 y aplicado bajo el régimen 2022 **no solo se descalibra: aprende el fenómeno equivocado**. Aprendería a detectar reprobación parcial con promedio bajo —hoy apenas una restricción de carga— y quedaría ciego al colapso total del periodo, que es lo que hoy cuesta la condición de estudiante.

## B.3 · Tres salidas posibles

| Opción | Descripción | Riesgo |
|---|---|---|
| **(A)** Usar el estado administrativo tal cual y documentar el cambio de régimen como limitación de validez externa | Simple y honesto | El modelo queda calibrado a una norma derogada |
| **(B)** Re-derivar la etiqueta aplicando las reglas 2022 sobre los datos crudos | Modelo alineado al presente | La reconstrucción es imperfecta; se pierde la verdad de campo |
| **(C)** Predecir magnitudes académicas continuas y aplicar encima la regla vigente como capa determinista `aplicar_reglamento(version)` | Invariante al régimen | Más trabajo de ingeniería |

### ✅ DECISIÓN ADOPTADA (aprobada por el estudiante, 2026-09-02): opción **(B)**

El estudiante define el alcance: **se asume que el reglamento vigente no volverá a cambiar** durante la vida útil del modelo; si cambia, un ingeniero posterior deberá adaptarlo.

Esa decisión elimina la motivación de la capa de versiones, de modo que **(C) colapsa en (B)**. Conviene precisar qué resuelve y qué no:

- **Sí resuelve** el riesgo hacia adelante: la capa `aplicar_reglamento(version)` se descarta por innecesaria.
- **No resuelve** el desajuste ya ocurrido: las etiquetas históricas son del régimen 2003 y el despliegue es bajo el de 2022. Ese desfase está en los datos, no en el futuro. Por tanto **sigue siendo obligatorio re-derivar el target con la regla vigente**; entrenar sobre el estado administrativo permanece inválido.

### La opción (B) además resulta empíricamente superior

| Target | Positivos | RF | XGBoost | LogReg |
|---|---|---|---|---|
| Estado administrativo (régimen 2003) | 40 | 0,707 | 0,712 | 0,701 |
| **Regla art. 19 de 2022 re-derivada** | 20 | **0,767** | **0,772** | 0,678 |

Mejora de ~0,06 de AUC **con la mitad de positivos**. La razón: la regla normativa es una función determinista de los datos académicos, mientras que el estado administrativo arrastra discrecionalidad de la oficina — ruido no aprendible.

La caída de la regresión logística es informativa: el art. 19 es una **conjunción** (100 % de créditos **y** promedio < 3,0), que un modelo lineal representa mal. Se anticipa un ganador basado en árboles **por razón estructural**, no por azar.

### Fiabilidad de la reconstrucción

| Verificación | Resultado |
|---|---|
| Cursos inscritos con nota válida | **93 %** (2 524 de 2 711) |
| Eventos marcados "100 % de créditos reprobados" | 19 |
| De ellos, con algún curso sin calificar en el mismo periodo | **2 (11 %)** |
| Estudiantes sin ambigüedad | **17 de 19** |

Los 2 casos dudosos se marcan explícitamente en el dataset. Limitación documentable, no impedimento.

### Qué se conserva de la opción (C)

La predicción de magnitudes continuas se mantiene como **salida secundaria opcional** — no por invarianza normativa, sino por la visión de producto: la app debe entregar *"la probabilidad general al ingreso y actualizarla semestre a semestre"*, y un target binario da un sí/no donde se necesita un puntaje graduado. Empíricamente compite bien: predecir "reprobó > 50 % de créditos en algún periodo" alcanza **AUC 0,795 con regresión logística**, la mejor cifra de toda la auditoría.

### Precaución obligatoria

El supuesto de estabilidad normativa debe quedar **escrito de forma explícita** en el informe final y en el manual técnico de integración (E2):

> *"Modelo calibrado para el reglamento estudiantil vigente desde 2022; entrenado sobre las cohortes 2017-2 y 2018-1 mediante re-derivación de la regla del art. 19 sobre datos regidos por el Acuerdo 015 de 2003."*

Cuesta un párrafo, le dice al futuro ingeniero exactamente qué debe tocar, y anticipa la pregunta que un jurado hará sobre el cambio de reglamento.

## B.4 · ¿Cambia el algoritmo ganador al cambiar el target?

**Sí, ya cambió.** Comparación con hiperparámetros fijos, CV-5 × 10 repeticiones:

| Algoritmo | Target actual (`PROM_CARRERA<3,0`) | Target institucional (estado BR) |
|---|---|---|
| XGBoost | **0,782** | **0,712** |
| Random Forest | 0,758 | 0,707 |
| LogReg (L2) | 0,726 | 0,700 |
| Decision Tree | 0,741 | 0,643 |
| SVM (RBF) | 0,648 | 0,520 |

Con el target actual RF y XGB se separan claramente del resto; con el institucional **los tres primeros se juntan en 0,012 de AUC**.

### Pero el "ganador" puede ser ruido

Con 30 repeticiones de CV-5 sobre el target institucional:

| Algoritmo | AUC | sd | IC 95 % aprox. |
|---|---|---|---|
| XGBoost | 0,716 | 0,037 | 0,636 – 0,776 |
| Random Forest | 0,705 | 0,037 | 0,633 – 0,758 |
| LogReg (L2) | 0,695 | 0,033 | 0,636 – 0,746 |

Los intervalos se solapan casi por completo. La prueba pareada de Wilcoxon da XGB > RF (p=0,031) y XGB > LogReg (p=0,005), pero **con tamaños de efecto de +0,011 y +0,020 de AUC** — irrelevantes en la práctica. Además, esa prueba es **anticonservadora**: las 30 repeticiones reutilizan los mismos 90 estudiantes, así que no son independientes y el p-valor está inflado.

### Recomendaciones para OE3.2 (selección del ganador)

1. **Repetir la comparación con el target definitivo**, no heredar el ganador anterior.
2. **Usar prueba pareada con corrección de Nadeau-Bengio** (t corregido para CV repetida), no Wilcoxon simple.
3. **Pre-registrar un umbral de relevancia práctica** (p. ej. ΔAUC ≥ 0,03) por debajo del cual se declara empate y se elige el modelo **más simple e interpretable**.
4. **Incluir la regresión logística regularizada como línea base**: queda a 0,02 de AUC de los ensambles, con un modelo lineal e interpretable. En un estudio con n=90 ese es un resultado a favor de la simplicidad, no una derrota.
5. Reportar **rango entre cortes** en el diseño longitudinal: es plausible que distintos algoritmos ganen en distintos semestres, y forzar un único ganador global oculte esa estructura.
