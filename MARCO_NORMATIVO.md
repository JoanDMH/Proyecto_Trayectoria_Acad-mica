# MARCO NORMATIVO INSTITUCIONAL
### Reglamento Estudiantil de la Universidad de los Llanos aplicado al modelo predictivo de trayectoria académica
**Propósito:** consolidar las disposiciones del reglamento que condicionan la definición de variables, la construcción de targets y la validez del modelo. Es insumo directo de la sección de marco normativo del informe final (E4).
**Última actualización:** 2026-09-30 · Entradas asociadas: RC-014, RC-015, RC-016, RC-017, RC-020, RC-039, RC-044.

> ## ⚠️ DECISIÓN ABIERTA — clave **D-REGIMEN**
> **La elección del régimen normativo con el que se construyen las etiquetas NO está cerrada.** Este documento adopta la regla del **art. 19 del reglamento vigente (2022)** y documenta por qué (§3), pero esa adopción es una **propuesta técnica pendiente de ratificación por la dirección del proyecto**, no un hecho consumado. La alternativa es etiquetar bajo el **Acuerdo Superior 015 de 2003**, que es el que efectivamente regía para las cohortes 2017-2 y 2018-1.
>
> **Por qué importa y por qué no la resuelve el estudiante:** es una elección normativa, no estadística. **65 de los 66** estados de bajo rendimiento registrados se aplicaron bajo la norma derogada (§1), y simulados sobre los mismos estudiantes **cada régimen afecta a 20 personas pero solo 7 son las mismas** (§2.4). No hay criterio empírico que decida entre dos reglas que persiguen fenómenos distintos: hay que elegir cuál es el fenómeno de interés institucional.
>
> **Es el punto más atacable del trabajo en sustentación.** Cualquier jurado puede preguntar por qué se etiqueta con una norma que no regía para la población estudiada, y la respuesta tiene que ser una decisión declarada de la dirección, no una preferencia del autor. De `D-REGIMEN` dependen además las otras cuatro decisiones abiertas (`D-MULTI`, `D-ALCANCE`, `D-COLIN`, `D-APP`) y el valor de las cohortes nuevas solicitadas el 29-09: si caen bajo el reglamento de 2022 mientras las actuales caen bajo el Acuerdo 015, el supuesto de comparabilidad se rompe (RC-044).
>
> Estado en el tablero: `KANBAN_AGENTES.md` → **D-REGIMEN · LIBRE ⚠ crítico**. Detalle en `PROBLEMAS_DETECTADOS.txt` P6 y en `RESUMEN_ASESOR_2026-09.md` §5.

---

## 1. Dos regímenes, no uno

| | **Acuerdo Superior N.º 015 de 2003** | **Reglamento vigente** (aprobado dic-2021) |
|---|---|---|
| Vigencia | Hasta 2021-2 | Desde 2022-1 |
| Cobertura de las cohortes 2017-2 y 2018-1 | Semestres 1 a ~9 | Semestre ~10 en adelante |
| Estados de bajo rendimiento registrados | **65 de 66** | **1 de 66** |

Las cohortes estudiadas cursaron prácticamente toda su trayectoria bajo el régimen de 2003, mientras que el modelo se desplegará sobre estudiantes regidos por el de 2022. **Este desfase es la restricción metodológica central del proyecto, y la decisión de qué régimen usar para etiquetar sigue abierta: clave `D-REGIMEN`** (ver el aviso de cabecera).

> **Nota sobre las fuentes.** El reglamento vigente se transcribió íntegro en `reglamento_estudiantil_unillanos.md`. Del Acuerdo 015 de 2003 solo se dispone de los fragmentos fotografiados de las páginas 5 a 9 (arts. 15 a 31), aportados por el estudiante. Las afirmaciones sobre el régimen anterior se limitan a esos artículos; no se extrapola más allá de ellos.

---

## 2. Bajo rendimiento académico: la definición cambia de objeto

### 2.1 Régimen 2003 (arts. 25–26)

- **Art. 25.** Quien haya perdido **hasta el 50 %** de las asignaturas podrá renovar matrícula.
- **Art. 26.** Quien haya perdido **más del 50 % de las asignaturas habiendo aprobado por lo menos una**, *o* haya perdido una asignatura **por tercera vez**, podrá renovar matrícula **solo si su promedio de carrera es ≥ 3,2**.
  - *Parágrafo tercero:* quien no cumpla **pierde el derecho a renovar matrícula** y solo puede reingresar transcurrido un periodo académico.
  - *Último inciso:* quien haya perdido una asignatura **por segunda vez** deberá inscribirla por tercera vez, siempre que su promedio sea ≥ 3,2 y no haya sido sancionado disciplinariamente.

### 2.2 Régimen 2022 (arts. 19–23)

- **Art. 19.** Pierde la condición de estudiante quien repruebe el **100 % de los créditos inscritos** *y* tenga promedio ponderado **< 3,0**, *o* quien repruebe **por cuarta vez** un curso.
  - *Parágrafo primero:* el promedio ponderado de carrera contempla los cursos **aprobados y reprobados**.
- **Art. 20.** Quien repruebe **más del 50 % de los créditos** y apruebe al menos un curso puede matricularse inscribiendo **únicamente los cursos reprobados**. No pierde la condición.
- **Art. 21.** Quien repruebe un curso o más **por segunda vez** puede matricularse inscribiendo prioritariamente los reprobados más atrasados, hasta **máximo cuatro cursos**.
- **Art. 22.** Quien repruebe **por tercera vez** puede matricularse inscribiendo **únicamente** esos cursos.
- **Art. 23.** El **Programa de Retención Estudiantil** debe establecer protocolo de acompañamiento para quienes se acojan a los arts. 19, 20 y 21.

### 2.3 Comparación correcta

| Criterio | 2003 | 2022 |
|---|---|---|
| Unidad de medida | Asignaturas | **Créditos** |
| Disparador de pérdida | > 50 % de asignaturas, **habiendo aprobado al menos una** | **100 %** de los créditos |
| Umbral de promedio | Renueva solo si ≥ **3,2** | Pierde condición si < **3,0** |
| Reprobación reiterada fatal | **4.ª vez** (implícita en la progresión de los arts. 25–26) | **4.ª vez** (explícita, art. 19) |
| Pérdida parcial > 50 % | Riesgo de perder la renovación | **Solo restricción de carga** (art. 20) |

**La reprobación reiterada no distingue a los regímenes:** la cuarta es la fatal en ambos; el reglamento de 2022 se limita a hacerlo explícito. Empíricamente es además marginal — 2 eventos en 1 estudiante de los 90.

### 2.4 Simulación sobre las cohortes disponibles

Reconstruidas ambas reglas con `CREDITOS`, notas y conteo de repeticiones:

| Situación | Eventos periodo-estudiante |
|---|---|
| 2003 art. 26 — pierde la renovación | 25 |
| 2003 art. 26 — disparado pero salvado por promedio ≥ 3,2 | 10 |
| 2022 art. 19 — pierde la condición | 21 |
| 2022 art. 20 — solo restricción de carga | 49 |

| Estudiantes distintos (de 90) | n |
|---|---|
| Afectados bajo 2003 | 20 |
| Afectados bajo 2022 | 20 |
| **Coincidentes** | **7** |
| Solo bajo 2003 | 13 |
| Solo bajo 2022 | 13 |

**Causa verificada de la divergencia:**

- Los **13 exclusivos de 2003** hoy caerían únicamente en el **art. 20** (restricción de carga). El régimen actual los conserva como estudiantes.
- Los **13 exclusivos de 2022 reprobaron el 100 % de sus asignaturas**. El art. 26 de 2003 exigía literalmente *"habiendo aprobado por lo menos una"*, de modo que **la reprobación total quedaba fuera de su alcance**; el art. 19 de 2022 cierra ese vacío.

**Conclusión:** los regímenes no se ordenan por severidad — persiguen fenómenos distintos. El de 2003 sancionaba la reprobación *parcial* con promedio bajo; el de 2022 sanciona el *colapso total* del periodo y la reincidencia.

---

## 3. Variable objetivo adoptada (paso I-1) — **sujeta a `D-REGIMEN`**

> El contenido de esta sección describe la regla implementada y su justificación empírica. **Lo que queda abierto no es la correcta implementación del art. 19 —está verificada— sino la pregunta previa de si el art. 19 es el artículo con el que debe etiquetarse esta población** (`D-REGIMEN`). Si la dirección opta por el Acuerdo 015 de 2003, la etiqueta debe reconstruirse con el art. 26 y toda la cadena posterior se repite.

**Se descarta** `PROMEDIO_CARRERA < 3.0` (definición *ad hoc*, tautológica — ver `AUDITORIA_2026-09.md` §1).

**Se descarta** el estado administrativo BR como target directo: es una etiqueta del régimen 2003 y entrenar sobre ella enseñaría al modelo el fenómeno equivocado.

**Se adopta** el **target derivado de la regla del art. 19 del reglamento vigente**, re-calculado sobre los datos históricos:

```
y = 1  si en algún periodo académico REGULAR (-1 o -2):
       (créditos_reprobados / créditos_cursados == 1  Y  promedio_ponderado_acumulado < 3,0)
    O  si en cualquier periodo reprobó un curso por 4.ª vez
```

**Implementado en** `src/preprocessing.py :: construir_target_art19()` (RC-020), como definición única y reproducible.

**Tratamiento del curso intersemestral (`-0`).** La condición de reprobar el 100 % de los créditos se evalúa solo sobre periodos regulares: el art. 15 parágrafo define el periodo académico como el lapso entre matrículas ordinarias, y el art. 40 parágrafo tercero excluye la nota intersemestral del promedio de semestre. En un intersemestral el estudiante suele inscribir un único curso, por lo que reprobarlo activaría la condición del 100 % de forma espuria. Su nota **sí** alimenta el promedio ponderado acumulado, conforme al art. 40 parágrafo primero. La vía de la cuarta reprobación no se restringe por tipo de periodo, porque el art. 19 no la condiciona.

**Población en riesgo: n = 80.** Diez estudiantes cuyo expediente se compone únicamente de homologaciones (`OBSERVACION = 'O'`) quedan fuera: el art. 19 exige reprobar créditos, de modo que no pueden experimentar el evento. La exclusión es por falta de exposición, no por el desenlace, y por tanto no introduce sesgo de supervivencia. Positivos: **19 de 80 (23,8 %)**, sin casos ambiguos.

### Justificación empírica

| Target | n | Positivos | RF | XGBoost | LogReg |
|---|---|---|---|---|---|
| Estado administrativo (régimen 2003) | 90 | 40 | 0,707 | 0,712 | 0,701 |
| Regla art. 19 — implementación inicial | 90 | 20 | 0,766 | 0,769 | 0,669 |
| **Regla art. 19 — corregida (RC-020)** | **80** | **19** | **0,825** | **0,829** | **0,775** |

El target normativo es más predecible pese a tener la mitad de positivos, porque es una función determinista de los datos académicos, mientras que el estado administrativo arrastra discrecionalidad de la oficina que ningún modelo puede aprender. La tercera fila incorpora la corrección del ordenamiento de periodos y la exclusión del intersemestral (RC-020), que aportan ~0,06 de AUC adicional y eliminan los 2 casos ambiguos.

La caída de la regresión logística (0,701 → 0,678) es coherente con la forma del art. 19: es una **conjunción** (100 % de créditos **y** promedio < 3,0), que un modelo lineal no representa bien. Se anticipa por tanto un ganador basado en árboles, por razón estructural y no por azar.

### Supuesto declarado

> Se asume que el reglamento vigente **no volverá a cambiar** durante la vida útil del modelo. Si cambia, deberá recalcularse la etiqueta y reentrenarse. Este supuesto se consigna en el informe final y en el manual técnico de integración (E2).

### Fiabilidad de la reconstrucción

- El **93 %** de los cursos inscritos tiene nota válida (`N`, `C`, `H`); el 7 % restante es invisible para la regla.
- De los **19 eventos** marcados como "100 % de créditos reprobados", **2 (11 %)** tienen algún curso sin calificar en el mismo periodo que podría romper la condición.
- **17 de 19 estudiantes** quedan sin ambigüedad. Los 2 casos dudosos se marcan explícitamente en el dataset.

---

## 4. Artículos que validan decisiones ya tomadas del pipeline

| Decisión del proyecto | Artículo que la respalda | Estado |
|---|---|---|
| Nota mínima aprobatoria 3,0 en toda la recodificación | **Art. 51** — escala 0,0–5,0; 0,0–2,9 Reprobado | ✅ Correcto |
| Regla NO RENOVACIÓN ≥ 2 periodos (RC-002, RC-006) | **Art. 17 parágrafo** — se puede omitir la renovación máximo por dos periodos consecutivos. Coincide con el **art. 28 parágrafo primero de 2003** (transcurridos 2 semestres completos se pierde el derecho a reintegro) | ✅ Confirmado por ambos regímenes |
| Cursos intersemestrales (`C`) incluidos en el análisis de reprobación y en el promedio de carrera | **Art. 40 parágrafos primero y tercero** — la nota intersemestral **cuenta** para el promedio de carrera pero **no** para el promedio de semestre | ✅ Correcto: `PROMEDIO_CARRERA` y `prom_sem1` provienen de archivos institucionales que ya aplican esta distinción |
| Validaciones (`V`) tratadas como nota válida | **Art. 50 parágrafo cuarto** — la validación cuenta para el promedio de semestre y de carrera | ✅ Correcto |
| Promedio de carrera incluye reprobados | **Art. 19 parágrafo primero** y glosario ("PROMEDIO DE NOTAS DE CARRERA: promedio ponderado de asignaturas cursadas") | ✅ Correcto |
| Trámite de grado recodificado a `A`/`P` sin afectar el promedio | **Art. 18 parágrafo cuarto** — la nota del curso de actualización **no hace parte** del promedio general de carrera | ✅ Coherente |

---

## 5. Variables nuevas habilitadas por el reglamento

Calculables con los datos disponibles (`CREDITOS` sin nulos) y **institucionalmente significativas**, a diferencia de las socioeconómicas:

| Variable | Base normativa | Eventos observados |
|---|---|---|
| `pct_creditos_reprobados` por periodo | Arts. 19–20 | continua |
| `art20_activado` (> 50 % de créditos reprobados) | Art. 20 | 49 periodos-estudiante |
| `art19_activado` (100 % de créditos reprobados) | Art. 19 | 24 periodos-estudiante |
| `veces_cursado` por asignatura (2.ª, 3.ª, 4.ª) | Arts. 21, 22, 19 | 181 / 32 / 1 |
| `promedio_ponderado_acumulado` al cierre de cada periodo | Art. 19 parágrafo primero | continua |
| `carga_creditos` inscrita | **Art. 20 parágrafo segundo de 2003**: mínimo 8, máximo 20 créditos · **Reglamento 2022**: máximo 18, o 20 si el promedio ≥ 4,0 | continua |

**El art. 23 identifica al destinatario del modelo:** el Programa de Retención Estudiantil está obligado a acompañar a quienes caen en los arts. 19, 20 y 21. Ese es el disparador operativo real que el sistema debe anticipar, y sustituye a cualquier umbral inventado por el estudio.

### 5.1 El art. 20 es predecible y el art. 19 no: hallazgo medido (RC-038, RC-039)

Al construir el diseño longitudinal por cortes se comprobó que **el art. 19 no se puede anticipar**: las variables acumuladas no aportan en el corte 1 (p=0,514) y **empeoran** en el corte 2 (Δ=−0,0204; p=0,044). La causa es normativa, no estadística: el art. 19 exige reprobar el **100 %** de los créditos de un periodo, de modo que describe un **colapso puntual y no un deterioro progresivo**. Es un filo, no una pendiente — hay **1,6 casi-activaciones por cada activación real**, y la diferencia entre disparar el artículo y no dispararlo es aprobar un solo curso.

El **art. 20** no tiene ese problema. Al exigir solo **más del 50 % de los créditos reprobados**, es un fenómeno gradual, y medido sobre los mismos datos, variables y algoritmo **daría +0,20 de AUC-ROC** frente al art. 19 en el diseño por cortes (el art. 19 se mueve en 0,47–0,50, que no es señal débil sino ausencia de señal). A eso se añade el argumento institucional: **el art. 20 acumula 49 eventos periodo-estudiante frente a los 21 del art. 19** (§2.4) y, vía art. 23, **es el disparador real del acompañamiento** del Programa de Retención.

> **Consecuencia normativa para el proyecto.** Redefinir el target longitudinal al art. 20 es la mejora de mayor retorno ya medida (WP `E-ART20`). Obsérvese que la elección entre art. 19 y art. 20 **no es la misma pregunta que `D-REGIMEN`**: aquella decide entre dos reglamentos, esta decide qué artículo del reglamento vigente se modela. Las dos están abiertas y la segunda depende de la primera.

---

## 6. Restricciones y matices que condicionan la interpretación de los datos

| Tema | Disposición | Implicación para el modelo |
|---|---|---|
| Redondeo de notas | **Art. 52 parágrafo** — unidades y un decimal; centésimas ≥5 se aproximan | Las notas son discretas con un decimal; no asumir continuidad fina |
| No presentarse sin excusa | **Art. 53** — se califica con 0,0 | Un 0,0 puede indicar ausencia, no desempeño. Afecta a la media del periodo |
| Cancelación de cursos | **Art. 38** (2022) hasta la 4.ª semana por fuerza mayor · **Art. 22** (2003) primeras 3 semanas, **excepto los que se están repitiendo** | Explica cursos inscritos sin nota; sesga a la baja el denominador de "créditos inscritos" |
| Cancelación de semestre | **Art. 38 parágrafo segundo** — hasta la semana quince | Genera periodos sin actividad que **no** son deserción |
| Inscripción de oficio en primer semestre | **Art. 20 parágrafo tercero de 2003** — los admitidos a primer semestre son inscritos **de oficio** en todos los cursos del nivel | El primer semestre no refleja elección del estudiante: la carga es homogénea por diseño. Refuerza la comparabilidad de `prom_sem1` entre estudiantes |
| Obligación de reinscribir lo perdido | **Art. 21 de 2003** y **art. 24 literal d** (registro de oficio) | La repitencia no siempre es voluntaria; `veces_cursada` mide obligación normativa, no motivación |
| Homologación | **Art. 44** — cinco casos; el caso 2 exige **no haber perdido la condición por bajo rendimiento**. **Art. 46**: nota mínima **3,5** para homologar o convalidar | ⚠ **11 de los 25 registros de homologación del extracto incumplen el art. 46** (aparecen notas de 3,0, 3,1 y 3,4). Ver §6.1 |
| Validación | **Art. 50 parágrafos quinto y sexto** — los cursos perdidos **no son validables**; máximo 10 por carrera, 1 por curso | Acota el uso de la observación `V` (2 registros en el dataset) |
| Simultaneidad | **Art. 24** (2022) y **art. 19** (2003, promedio ≥ 3,5 y 60 % aprobado) | Posible explicación de trayectorias atípicas; no observada en la muestra |
| Plazo de grado | **Art. 18** (2022): 4 periodos tras aprobar todos los cursos · **Art. 30** (2003): 4 semestres | Delimita cuándo un estudiante sin graduar aún está "en trámite" y no es desertor. Sustenta la regla de recencia de RC-002 |
| Asistencia | **Art. 58** — mínimos de 50 % a 90 % según tipo de curso | Variable potencialmente predictiva **no disponible** en los datos entregados. **El art. 58 la hace obligatoria, luego la institución debe registrarla**: es una de las variables pedidas a la Oficina de Sistemas. Ver §6.2 |

### 6.1 Homologaciones por debajo del mínimo normativo (P20)

El art. 46 exige nota **≥ 3,5** para homologar o convalidar. En el extracto entregado, **11 de los 25 registros de homologación la incumplen**: aparecen notas de 3,0, 3,1 y 3,4. O son errores de registro, o son excepciones autorizadas que el reglamento no contempla; **desde los datos no se puede saber**, y la consulta queda cursada a la Oficina de Sistemas (WP `F-ANOMAL`, bloqueado).

Esto **rectifica** lo que este documento afirmaba hasta el 2026-09-29, que las homologaciones observadas tenían «todas nota ≥ 3,0, la mayoría ≥ 3,5». La primera parte se sostiene; la segunda no, y la discrepancia es normativamente relevante porque afecta a la fiabilidad de las notas homologadas.

El efecto colateral sobre el modelo **ya está verificado y es coherente con la exclusión de §3**: los 10 estudiantes cuyo expediente se compone solo de homologaciones —todos de la cohorte 2017-2, todos en el periodo 2019-0— tienen un `PROMEDIO_CARRERA` medio de **3,71** frente al **3,01** de los 80 expuestos, precisamente porque ese promedio deriva de notas externas homologadas y **no es comparable**. Con el target antiguo (`PROMEDIO_CARRERA < 3,0`) ninguno de los 10 habría sido marcado como bajo rendimiento.

En la misma consulta se incluye el **estudiante 160004036**, que figura con estado final «retiro definitivo del programa con bajo rendimiento» sin tener **ni una sola nota reprobada** en los datos entregados —sus únicas observaciones son dos homologaciones aprobadas (3,7 y 3,4)— y arrastra un estado de bajo rendimiento en 2018-1, anterior a todo su bloque de registros de 2019-0. La lectura más simple es que el extracto no contiene toda su actividad; si ocurre en un caso, puede ocurrir en otros y algunas etiquetas estarían mal puestas.

### 6.2 Variables que el reglamento obliga a registrar y no fueron entregadas

El techo del modelo lo impone la **información disponible**, no el número de filas: la curva de tamaño muestral satura en **0,838 de AUC-PR** y duplicar la muestra compra solo unos **+0,048** (RC-044, P21). Más filas mejoran la estimación; **más variables mueven el límite**. De ahí que la petición cursada a la Oficina de Sistemas el 29-09 pida, además de las cohortes nuevas:

| Variable | Base normativa que obliga a registrarla | Por qué subiría el techo |
|---|---|---|
| **Asistencia** por curso y periodo | **Art. 58** — mínimos de 50 % a 90 % según tipo de curso; es causal de pérdida | Predictor natural del abandono, conductual y anterior a la nota. Es la brecha de información más citada del estudio |
| Fechas de pago de matrícula | **Art. 17 parágrafo** — la renovación se puede omitir máximo dos periodos consecutivos | Separaría el abandono económico del académico, hoy indistinguibles en los 29 desertores sin acta formal |
| Créditos inscritos frente a cancelados | **Art. 38** (2022) y **art. 22** (2003) — ventanas de cancelación | Corregiría el denominador de «créditos inscritos» del art. 19, hoy sesgado a la baja, y los cursos inscritos sin nota (7 % del total) |

---

## 7. Limitaciones declaradas derivadas del marco normativo

1. **Desfase de régimen — limitación de primer nivel y decisión abierta `D-REGIMEN`.** El modelo se entrena con trayectorias regidas por el Acuerdo 015 de 2003 y se desplegará bajo el reglamento de 2022. Se mitiga re-derivando la etiqueta con la regla vigente, pero **el comportamiento de los estudiantes también estuvo condicionado por las reglas antiguas** (p. ej., el umbral 3,2 del art. 26 pudo inducir esfuerzo diferencial). Este efecto no es corregible con los datos disponibles. **Mientras la dirección no ratifique el régimen, esta limitación no está mitigada sino solo documentada**, y es el punto que con más probabilidad se discutirá en la sustentación.
2. **Reconstrucción parcial de la regla.** El 7 % de los cursos inscritos carece de nota, por lo que la condición "100 % de los créditos inscritos" se aproxima por defecto. 2 de 19 eventos quedan marcados como dudosos.
3. **Discrecionalidad administrativa no recuperable.** Ninguna reconstrucción reproduce el estado administrativo real (15/43 con la regla de 2003, 18/43 con la de 2022), lo que indica criterios adicionales de la Oficina de Admisiones no documentados en el reglamento.
4. **Fuente parcial del régimen anterior.** Solo se dispone de los arts. 15–31 del Acuerdo 015 de 2003. Disposiciones anteriores o posteriores de ese acuerdo podrían matizar el análisis.
5. **Variable de asistencia ausente.** El art. 58 la hace obligatoria y sería un predictor natural del abandono, pero no fue entregada por la Oficina de Sistemas. Está incluida en la petición del 29-09 (§6.2): el techo del modelo lo impone la información disponible, no el tamaño muestral (RC-044).
6. **Registros de homologación que incumplen el art. 46.** 11 de 25 tienen nota inferior a 3,5 (§6.1). No se puede determinar desde los datos si son errores de registro o excepciones autorizadas, de modo que la fiabilidad de las notas homologadas queda declarada como incierta.
7. **El artículo modelado no es el que dispara el acompañamiento.** El art. 19, que es el que se etiqueta, no se puede anticipar porque es un evento agudo; el art. 20, que sí es predecible (+0,20 de AUC-ROC) y es el disparador real del art. 23, no está modelado todavía (§5.1). Mientras eso no se resuelva, el producto predice un evento distinto del que la institución necesita anticipar.

---

## 8. Trazabilidad

| Entrada | Contenido |
|---|---|
| **RC-014** | Primera incorporación del reglamento; detección de que el target del proyecto no era la definición institucional |
| **RC-015** | Corrección: las etiquetas provienen del régimen 2003; simulación comparada de ambos regímenes |
| **RC-016** | Inestabilidad del algoritmo ganador al cambiar el target; protocolo de selección con umbral de relevancia |
| **RC-017** | Target definitivo propuesto (regla art. 19 re-derivada) y supuesto de estabilidad normativa. **Pendiente de ratificación: `D-REGIMEN`** |
| **RC-020** | Implementación en `src/preprocessing.py :: construir_target_art19()`; población expuesta n=80, 19 positivos (23,8 %), exclusión pre-registrada de los 10 expedientes solo homologados |
| **RC-038** | El diseño longitudinal con el art. 19 no predice: el evento es agudo, no gradual |
| **RC-039** | El art. 20 daría +0,20 de AUC-ROC en el diseño por cortes y es el disparador real del art. 23 (§5.1) |
| **RC-044** | El techo lo impone la información disponible, no el tamaño muestral: fundamenta la petición de asistencia (art. 58), fechas de pago y créditos cancelados (§6.2) |

Documento fuente: `reglamento_estudiantil_unillanos.md`. Análisis completo en `AUDITORIA_2026-09.md`, adendas A y B. Anomalías del extracto en `PROBLEMAS_DETECTADOS.txt` P20; decisiones abiertas en `KANBAN_AGENTES.md` y `RESUMEN_ASESOR_2026-09.md` §5.
