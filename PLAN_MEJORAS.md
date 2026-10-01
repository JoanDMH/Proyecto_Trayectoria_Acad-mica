# Plan de mejoras — propuesta priorizada
**Fecha:** 2026-09-30 · **Base:** RC-033 a RC-044 · **Estado:** propuesta, pendiente de aprobación

Todo lo que sigue está respaldado por mediciones propias, no por criterio. Se ordena por
**relación entre valor esperado y esfuerzo**, y se separa lo que el proyecto *debe* hacer
(compromiso) de lo que *puede* hacer (mejora).

> **Qué ha cambiado respecto a la versión del 16-09.** La prioridad P1 de entonces —construir el
> target multiclase— **ya no es una tarea**: se construyó, se le aplicó la regla de viabilidad
> pre-registrada y se declaró **inviable** (RC-041). Se recoloca más abajo, entre las decisiones
> cerradas. En su lugar entran tres mejoras surgidas del encargo de la dirección del 29-09
> (**P16**, **P17**, **P18**), y la ampliación del extracto de datos deja de ser «fuera de
> alcance»: **el asesor cursó la petición el 29-09**.

---

## Antes de mejorar: qué falta del compromiso

| Entregable | Estado |
|---|---|
| E2 · Modelo empaquetado | 🟡 Modelo binario del art. 19 cerrado (RF, AUC-PR 0,745 ± 0,025, 6 variables, n=80); falta empaquetado `joblib` y manual técnico, condicionados a **P16** y **P17** |
| ~~E2 · Target multiclase de trayectoria~~ | ⛔ **Cerrado como INVIABLE** (RC-041). Sustituido por el target binario de graduación. Requiere ratificación formal de la dirección (**D-MULTI**), no trabajo técnico |
| E3 · Dataset procesado | 🟡 `df_master_fcbi.csv` listo (262 estudiantes); falta paquete anonimizado |
| E4 · Informe final | 🟡 Borrador actualizado; espera plantilla LaTeX |
| E5 · Ponencia | 🟢 **Cerrada.** CICI 2026, ID 129, Springer LNCS, 7–9 de octubre de 2026 |

> **El hueco del compromiso ya no es de modelado sino de validez y de empaquetado.** El modelo
> existe y está medido; lo que le falta es una validación externa que hoy no tiene (**P18**) y dos
> defectos que impiden interpretarlo y publicarlo tal cual (**P16**, **P17**).

---

## P18 · Validación externa con las cohortes nuevas  ← *ahora es posible*

**Por qué primero:** es **la limitación más seria del estudio**. Todo lo reportado —AUC-PR 0,745
incluido— proviene de validación cruzada sobre las mismas dos cohortes (2017-2 y 2018-1). Sin un
conjunto independiente, no hay evidencia de que el modelo generalice. En la versión anterior de
este plan no se proponía porque no había datos que pedir; **el asesor cursó la petición ante la
Oficina de Sistemas el 29-09**, de modo que la vía está abierta.

**Qué hacer:** cuando lleguen las cohortes, evaluar el modelo **ya entrenado y congelado** sobre
ellas, sin reajustar hiperparámetros ni reseleccionar variables. Reportar AUC-PR, AUC-ROC y lift
frente a la línea base de la nueva muestra, y comparar la caída contra lo estimado por validación
cruzada.

**Aviso registrado (RC-044) — hay que verificarlo antes de comparar:** si las cohortes nuevas
cursan bajo el reglamento vigente desde 2022 y las actuales bajo el Acuerdo 015 de 2003, las
etiquetas no son comparables y la validación mediría dos fenómenos distintos. **Esto depende de
D-REGIMEN y debe resolverse antes de recibir los datos, no después.**

**Esfuerzo:** bajo una vez lleguen los datos · **Valor:** el más alto de todo el plan — convierte
una limitación declarada en evidencia.

---

## P17 · Calibrar las probabilidades o retirar el porcentaje de la app

**Evidencia (RC-043):** la anchura mediana del intervalo creíble del 94 % de la probabilidad
individual es **0,359**, y en **43 de 80 estudiantes (54 %) supera 0,30**. Para más de la mitad de
la cohorte el modelo **no está en condiciones de emitir un número**. Confirma por vía independiente
el defecto de calibración detectado el 16-09.

**Dos opciones, no tres:**
1. **Calibrar** (isotónica o Platt, ajustada dentro de cada pliegue de entrenamiento para no
   repetir la fuga de RC-032) y publicar el número con su intervalo.
2. **Retirar el porcentaje** y mostrar **nivel de alerta y puesto relativo**, apoyándose en el
   esquema de tres niveles ya implementado (0,62 → 11 alertas con precisión 1,000 · 0,12 → 52 ·
   0,06 → 66, detecta el 100 %).

**Recomendación:** la opción 2. El esquema por niveles ya existe, comunica el intercambio de forma
honesta y no promete una precisión que la muestra no sostiene. La calibración puede añadirse
después sin rehacer nada.

**Esfuerzo:** bajo · **Valor:** desbloquea la entrega de E2 y elimina un riesgo de mala lectura
institucional. **Decisión de la dirección: D-APP.**

---

## P16 · Resolver la colinealidad del bloque SABER 11

**Evidencia (RC-043):** la posterior bayesiana asigna a `icfes_total` un coeficiente **positivo y
creíble** (+1,558; IC 94 % [+0,84, +2,25]) —más puntaje, más riesgo—, sustantivamente imposible y
síntoma clásico de supresión por colinealidad. Comprobado: **VIF 6,66** y **R² = 0,850** contra sus
tres áreas, con correlación 0,920 frente a su suma.

**Qué está y qué no está en riesgo:**

| Ámbito | Efecto |
|---|---|
| Acierto del modelo en producción | **No afectado.** Retirar el total deja AUC-PR 0,7207 frente a 0,7418 (p=0,126, empate) |
| Lectura de coeficientes e importancias en el bloque SABER 11 | **Inválida** mientras el total conviva con sus áreas |

**Qué hacer:** elegir una de las dos parametrizaciones —conservar `icfes_total` y retirar las tres
áreas, o al revés— **antes de interpretar nada en el informe**, y reejecutar el protocolo con la
elegida para reportar importancias defendibles.

**Esfuerzo:** trivial en cómputo · **Valor:** condición necesaria para el capítulo de
interpretación. **Decisión de la dirección: D-COLIN.**

---

## P2 · Redefinir el target del producto longitudinal al art. 20

**Evidencia (RC-039):** manteniendo todo constante y cambiando solo el umbral del evento:

| Definición | AUC-ROC corte 1 | AUC-ROC corte 2 |
|---|:---:|:---:|
| Art. 19 (100 % de créditos) | 0,496 | 0,468 |
| ≥ 75 % de créditos reprobados | 0,603 | 0,567 |
| **Art. 20 (> 50 % de créditos)** | **0,647** | **0,673** |

Un salto de ~0,20 sin tocar muestra, variables ni algoritmo.

**Tres razones convergen:**
1. Es un fenómeno gradual, no un filo — el art. 19 tiene 1,6 casi-activaciones por activación
2. Es el **disparador real del acompañamiento** institucional (art. 23)
3. Es el único target con señal en el diseño por cortes: con el art. 19 las variables acumuladas
   no aportan en el corte 1 (Δ=+0,0062; p=0,514) y **empeoran** el modelo en el corte 2
   (Δ=−0,0204; p=0,044), donde por sí solas rinden por debajo del azar (RC-038)

**Esfuerzo:** bajo — el código ya existe (`src/longitudinal.py`, `src/experimento_ancho_target.py`).
**Valor:** habilita el producto tipo SPADIES que la visión del proyecto exige.

**Expectativa honesta:** AUC-ROC 0,65–0,68 es una herramienta de **cribado**, no de precisión.
Sirve para priorizar a quién mirar, no para decidir automáticamente.

---

## P3 · Incorporar `peor_periodo` al conjunto de variables

**Evidencia (RC-040):** de cuatro variables de inestabilidad probadas, solo el **mínimo del
promedio por periodo** resulta significativo, y en los dos cortes (p=0,011 y p=0,008). La
volatilidad, la tendencia y la caída máxima **no predicen**.

Ganancia: +0,017 y +0,012 de AUC-ROC. Pequeña pero consistente.

**Valor adicional — interpretabilidad:** *"ya tuvo un semestre por debajo de 3,1"* es un criterio
que el Programa de Retención entiende y puede accionar de inmediato, a diferencia de una
probabilidad abstracta.

**Esfuerzo:** trivial · **Valor:** pequeño en métrica, alto en comunicación.

---

## P4 · Análisis de supervivencia para la censura

**Problema real:** Biología tiene 15 estudiantes activos sin desenlace conocido (18 % de su
muestra). Hoy se excluyen o se tratan como negativos, y ambas opciones sesgan. RC-041 añadió un
argumento: esos mismos 15 son **el 75 % de la clase ACTIVO** que hizo inviable el target
multiclase, de modo que la censura no es un detalle marginal sino la causa de un entregable caído.

**Propuesta:** modelar *tiempo hasta el evento* en lugar de *si ocurre*, con Kaplan-Meier para
la descriptiva y Cox o Random Survival Forest para la predicción. Es el marco estadísticamente
correcto cuando hay censura a la derecha.

**Valor para la tesis:** alto en rigor metodológico — responde de raíz una limitación que hoy
solo se declara. Y encaja con la pregunta institucional real, que no es *si* un estudiante caerá
sino *cuándo*.

**Esfuerzo:** medio-alto · **Valor:** metodológico más que predictivo.

---

## Decisiones cerradas: lo que ya no es una tarea

### ~~P1 · Construir el target multiclase de trayectoria (WP-OE1.3)~~ — respuesta negativa

Era la prioridad 1 de la versión anterior. Se ejecutó (`src/target_multiclase.py`) y **la regla de
viabilidad pre-registrada en RC-008 la rechaza** (RC-041):

| Target | Clase minoritaria | n | Por pliegue | ¿Viable? |
|---|---|:---:|:---:|:---:|
| 4 clases (propuesta original) | ACTIVO | **5** | 1,0 | **No** |
| 3 clases (colapsada) | ACTIVO | **20** | 4,0 | **No** |
| 2 clases (graduación) | GRADUADO | 66 | 13,2 | **Sí** |

Se probaron **tres operacionalizaciones alternativas** de «rezagado» antes de declararlo, y el
cuello de botella es siempre la clase ACTIVO, no la de rezago. Dos causas de fondo: los 20 activos
son en esencia el grupo censurado de Biología (15 de 20), un artefacto de la ventana de observación
y no un fenómeno académico; y **en estas cohortes el rezago es la norma** —el 63 % de quienes no
desertaron excedió el plan nominal de 10 semestres—, así que una clase que agrupa a dos tercios de
la población no discrimina.

**Queda:** el **target binario de graduación** (ya evaluado y viable), el rezago como indicador
continuo `periodos_sobre_plan`, y los activos marcados como censurados. Lo pendiente es **formal,
no técnico**: ratificar la sustitución ante la dirección (**D-MULTI**), porque modifica un
entregable comprometido.

### ~~Diseño longitudinal con el target del art. 19~~ — descartado

RC-038 refutó la hipótesis del propio auditor. El evento del art. 19 es **agudo, no gradual**: exige
reprobar el 100 % de los créditos de un periodo, y entre quienes sobreviven a un corte ninguna
variable acumulada distingue a quienes lo activarán después. Sobrevive **P2**, que es la misma vía
con otro target.

---

## Lo que NO propongo, y por qué

| Descartado | Motivo | Evidencia |
|---|---|---|
| Probar más algoritmos | Los cinco de la propuesta están medidos; las diferencias son de ~0,03 | RC-033 |
| Ensamblados | Ninguno supera a Random Forest solo | Medido |
| Afinar hiperparámetros | Con rejillas equilibradas y CV anidada, el margen está agotado | RC-033 |
| Más variables socioeconómicas | Por sí solas apenas superan el azar (0,344 vs. 0,238) | RC-037 |
| Unir los tres programas | Los modelos separados ganan (Δ=−0,031; p=0,043), y el indicador de programa no aporta (Δ=+0,003; p=0,453) | RC-037 |
| Volatilidad y tendencia | No predicen (p > 0,3) | RC-040 |
| **PCA como criterio de selección** | Es no supervisado: por construcción no puede validar una selección supervisada. Y medido, **destruye la señal**: AUC-PR **0,3715** frente a 0,7418 (p<0,0001). La variable más predictiva (40,4 % de la importancia) carga al máximo en **CP3, el 8,3 % de la varianza** | RC-042 |
| **PLS-DA** | Supervisado y aun así muy por debajo: 0,4637 sobre las 19 variables, 0,4463 sobre S3 (ambos p<0,0001). Elige **k=1 componente en las 50 iteraciones**: hay una sola dirección útil y, siendo lineal, no captura su forma | RC-042 |
| **Modelos bayesianos como modelo de producción** | Ninguno supera a Random Forest. El mejor es la logística bayesiana con aproximación de Laplace (0,6190; Δ=−0,123; p=0,0032); Naive Bayes 0,4252 y proceso gaussiano 0,4354. Son fronteras lineales frente a un problema con interacciones. **Sí se conservan como diagnóstico**: de ahí salen P16 y P17 | RC-043 |
| **One-shot / few-shot learning** | No es trasladable: exige un corpus de preentrenamiento y una estructura por episodios que aquí no existen. Trasladado el mecanismo, todo queda por debajo (prototipos 0,4373; NCA+prototipos 0,3559; k vecinos 0,6435), y **aprender la métrica empeora los prototipos** porque con 19 positivos NCA sobreajusta | RC-044 |

**El margen de mejora ya no está en el modelado.** Cuatro familias distintas —representaciones
latentes, métodos lineales supervisados, inferencia bayesiana y aprendizaje métrico— se midieron
bajo el mismo protocolo y **todas rinden peor que Random Forest sobre el conjunto S3**. Lo que queda
está en la validez (**P18**), en la interpretabilidad (**P16**), en la honestidad del producto
(**P17**) y en el target (**P2**).

---

## Prioridad real: ampliar el extracto de datos

**Esta sección ya no está «fuera de alcance».** En la versión del 16-09 se documentaba como
limitación porque no era posible solicitar datos; **el asesor cursó la petición el 29-09**, de modo
que pasa a ser una vía accionable y es la base de **P18**.

**Cuánto compra cada cosa (RC-044).** Submuestreando solo el pliegue de entrenamiento, la curva de
tamaño muestral ajusta a **AUC-PR(n) = 0,838 − 8,843·n^(−1,107)** con R² = 0,994, y da un **techo
asintótico estimado de 0,838**:

| n total | AUC-PR proyectado | Ganancia |
|:---:|:---:|:---:|
| 80 (hoy) | 0,749 | — |
| 160 (duplicar) | 0,797 | **+0,048** |
| 240 (triplicar) | 0,811 | +0,062 |
| 320 (cuadruplicar) | 0,819 | +0,070 |

**Esto cambia el argumento de la petición.** Duplicar la muestra compra ≈**+0,048** de AUC-PR y
cuadruplicarla ≈+0,070: la curva **satura pronto**, porque el techo lo impone la información
disponible y no el número de filas. Dicho en una línea: **más filas afinan la estimación; más
variables mueven el techo.** Las cohortes nuevas siguen siendo muy valiosas, pero su valor
principal **no es agrandar el entrenamiento sino habilitar la validación externa** (P18).

**Matiz que conviene no confundir** (RC-037): más datos *de la misma población* mejoran el modelo;
más datos *de poblaciones distintas* lo empeoran. El argumento de ampliar la muestra vale **dentro
de cada programa**.

El resultado de RC-039 apunta a que un colapso puntual suele originarse **fuera del expediente
académico**. Los datos que lo explicarían —y que sí moverían el techo— no están en el extracto
entregado:

| Dato | Por qué importaría | ¿Existe institucionalmente? |
|---|---|---|
| **Asistencia** | El **art. 58** la hace obligatoria con mínimos del 50–90 % según el tipo de curso | Sí — es un requisito normativo, luego se registra |
| Fechas de pago y renovación | Una dificultad económica sobrevenida precede al abandono | Probablemente, en el sistema financiero |
| Créditos inscritos vs. cancelados | El art. 38 regula la cancelación; cancelar señala dificultad | Sí, ya está en el sistema |
| Situación laboral o cambios de residencia | Explicarían colapsos puntuales | Poco probable |

**Cómo aprovecharlo igualmente:** este es probablemente **el techo real del estudio**, y decirlo
con evidencia es más valioso que ocultarlo. El informe puede afirmar, con respaldo empírico y con
la curva ajustada como cuantificación, que *el desempeño alcanzable está limitado por la
información disponible y no por la técnica*. Es una contribución del trabajo, no una carencia de
éste — y ahora, además, una petición concreta ya cursada.

---

## Resumen ejecutivo

| # | Propuesta | Esfuerzo | Valor | ¿Medido? |
|---|---|---|---|---|
| **P18** | Validación externa con las cohortes nuevas | Bajo (tras recibir datos) | **Cierra la limitación más seria** | ✅ RC-044 (motivación) |
| **P17** | Calibrar o retirar el porcentaje de la app | Bajo | Desbloquea E2; 54 % de casos con IC > 0,30 | ✅ RC-043 |
| **P16** | Resolver la colinealidad de SABER 11 | Trivial | Habilita el capítulo de interpretación | ✅ RC-043 |
| **P2** | Target del art. 20 para el longitudinal | Bajo | **+0,20 AUC-ROC** | ✅ RC-039 |
| **P3** | Variable `peor_periodo` | Trivial | +0,015 AUC-ROC + interpretabilidad | ✅ RC-040 |
| **P4** | Análisis de supervivencia | Medio-alto | Rigor metodológico | — |
| ~~P1~~ | ~~Target multiclase~~ | — | ⛔ **Inviable — decisión cerrada** | ✅ RC-041 |

**Orden sugerido:** **P16 y P17 primero**, porque son de esfuerzo trivial o bajo, dependen de una
decisión de la dirección más que de cómputo y desbloquean E2 y el capítulo de interpretación.
**P18 en paralelo**, preparando el protocolo de validación congelado para aplicarlo el día que
lleguen las cohortes — con **D-REGIMEN resuelta antes**, o la comparación no será válida. Después
**P2 + P3 juntos**, porque comparten el mismo código y se miden en la misma corrida. **P4** solo
si el calendario lo permite: aporta rigor metodológico, no desempeño.

La ampliación del extracto de datos **ya no es solo una recomendación del informe**: la petición
está cursada desde el 29-09 y de ella depende P18.
