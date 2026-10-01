# Resumen de auditoría metodológica y decisiones adoptadas
**Proyecto:** Modelo predictivo de trayectoria académica FCBI · **Fecha:** 30 de septiembre de 2026
**Para:** Ing. Diana Marcela Cardona Román (directora) · Sara Cristina Guerrero, Ph.D. (codirectora)

---

## 1. Qué se hizo

Se realizó una revisión completa del diseño experimental antes de construir el modelo comprometido (E2). Se re-ejecutó el pipeline y se corrieron experimentos de ablación y de validez temporal con validación cruzada repetida. La documentación, la trazabilidad de los datos y el código resultaron correctos: **no se hallaron errores de cálculo**. Los hallazgos son de **validez**, no de implementación.

Desde entonces se ha cerrado el modelo definitivo, se ha verificado la ampliación a los tres programas de la FCBI, se ha resuelto por medición la arquitectura del modelo, se han cerrado en negativo dos vías (el target multiclase y el diseño longitudinal con el art. 19) y se ha atendido el encargo de la dirección del 29 de septiembre (PCA, modelos bayesianos, aprendizaje con pocos datos). **La ponencia está cerrada y aceptada.** Los puntos 2, 3 y 6 de este documento recogen la auditoría de septiembre y se conservan sin cambios; los puntos 3 bis, 4, 5 y 7 reflejan el estado a 30 de septiembre.

---

## 2. Tres hallazgos y sus decisiones

### 2.1 La variable objetivo de rendimiento era tautológica

`rendimiento_bajo` se definía como `PROMEDIO_CARRERA < 3,0`, pero el promedio de carrera **incluye el primer semestre**, que era justamente la variable predictora dominante. Para los 17 estudiantes que cursaron un solo periodo (19 % de la muestra), ambos valores casi coinciden (r = 0,921).

Consecuencia medida: sin `prom_sem1` el modelo cae a **AUC 0,483** (azar), y al excluir a los desertores tempranos cae de 0,761 a **0,546**. El modelo no predecía rendimiento: en buena medida detectaba a quien ya había abandonado.

**Decisión:** se sustituye la variable objetivo (ver punto 3).

### 2.2 Los modelos de reprobación por asignatura usaban información del futuro

Se confirma la observación de la asesoría, aunque por una razón distinta a la planteada. Las cinco asignaturas críticas son de primer y segundo semestre, pero el predictor principal (`prom_global`) es el promedio del estudiante en el resto de la carrera: **entre el 70 % y el 83 % procede de semestres posteriores a la asignatura que se predice**. No era predicción, sino retrodicción.

Al reconstruir un modelo temporalmente válido (predecir la reprobación de segundo semestre con información del primero), el desempeño real es **AUC 0,70–0,74**, no el 0,865–0,939 reportado. Las variables de ingreso por sí solas no predicen nada (0,41–0,51).

**Decisión:** se retiran los cinco modelos del repositorio, de la aplicación y del informe. Se conserva el **índice de criticidad**, que es descriptivo y no está afectado. La fuga se reporta como hallazgo metodológico.

### 2.3 Las cohortes se rigieron por un reglamento derogado

Las cohortes 2017-2 y 2018-1 cursaron casi toda su trayectoria bajo el **Acuerdo Superior 015 de 2003**, sustituido por el reglamento vigente desde 2022: **65 de 66 estados de bajo rendimiento se aplicaron bajo la norma anterior**.

Los dos regímenes no se ordenan por severidad; persiguen fenómenos distintos. El de 2003 sancionaba la reprobación de más del 50 % de las asignaturas *habiendo aprobado al menos una*, con umbral de promedio 3,2. El vigente (art. 19) sanciona la reprobación del **100 % de los créditos** con promedio inferior a 3,0, y reclasifica la pérdida parcial como simple restricción de carga (art. 20).

Simulados sobre los mismos estudiantes, cada régimen afecta a 20 personas **pero solo 7 son las mismas**. Un modelo entrenado con etiquetas antiguas aprendería el fenómeno equivocado.

**Decisión:** ver punto 3.

---

## 3. Decisión principal: nueva variable objetivo

Se adopta el target derivado del **artículo 19 del reglamento vigente**, re-calculado sobre los datos históricos:

> `y = 1` si en algún periodo el estudiante reprobó el 100 % de los créditos cursados con promedio ponderado acumulado inferior a 3,0, o reprobó un curso por cuarta vez.

**Justificación empírica** (validación cruzada de 5 pliegues, repetida):

| Variable objetivo | n | Positivos | Random Forest | XGBoost |
|---|---|---|---|---|
| Estado administrativo (régimen 2003) | 90 | 40 | 0,707 | 0,712 |
| **Art. 19 del reglamento vigente** | **80** | **19** | **0,825** | **0,829** |

El target normativo predice mejor pese a tener menos de la mitad de casos positivos, porque es una función determinista de los datos académicos y no arrastra la discrecionalidad administrativa.

**Población de análisis: n = 80.** Diez estudiantes cuyo expediente se compone únicamente de homologaciones quedan fuera: el art. 19 exige reprobar créditos, de modo que no pueden experimentar el evento. La exclusión es por falta de exposición, no por el desenlace, y por tanto no introduce sesgo de supervivencia.

**Supuesto declarado:** se asume estabilidad del reglamento vigente durante la vida útil del modelo. Quedará consignado en el informe final y en el manual técnico de integración.

---

## 3 bis. El modelo definitivo (cerrado)

| Concepto | Valor | RC |
|---|---|---|
| Variable objetivo | Bajo rendimiento, art. 19 del reglamento vigente | RC-017 |
| Población | **80** expuestos (de 90 con actividad académica) · **19 positivos (23,8 %)** | RC-020 |
| Variables | **6** (conjunto S3): `prom_sem1`, `sin_primer_semestre`, `icfes_total`, `icfes_mat`, `icfes_lec`, `icfes_nat` | RC-032 |
| Algoritmo | **Random Forest**, **AUC-PR 0,745 ± 0,025** · AUC-ROC 0,794 · línea base 0,2375 (lift 3,16×) | RC-033 |
| Protocolo | CV-5 estratificada **anidada** × 10 repeticiones, SEED=42 | RC-021 |
| Umbral | **Esquema de tres niveles seleccionable:** 0,62 → 11 alertas con precisión 1,000 (detecta el 58 %) · 0,12 → 52 alertas (84 %) · 0,06 → 66 alertas (100 %) | RC-034, RC-035 |
| Arquitectura | **Modelos separados por programa** | RC-037 |

Random Forest gana esta vez **por aplicación directa de la regla pre-registrada**, sin desviación del protocolo: supera de forma significativa y relevante al Árbol, a la Logística y a XGBoost, y frente a SVM (Δ=+0,032; p=0,234) se declara empate y decide el orden de parsimonia. Corrige lo anticipado el 2 de septiembre, cuando con el target recién cambiado el ganador aún no estaba resuelto.

**Dos cifras que el informe debe reportar juntas:** el **44 % de los eventos del art. 19 ocurre en el primer semestre**, de forma simultánea a la variable predictora dominante. Restringido a la predicción genuina (evento en semestre ≥ 2), el AUC-PR cae de 0,750 a **0,473**, pero el lift se mantiene (3,16× → 3,10×): la caída es de prevalencia, no de capacidad. El patrón se repite en los tres programas (42 %, 48 %, 41 %): es estructural.

### Ampliación a la FCBI y arquitectura

Dataset maestro `df_master_fcbi.csv`: **262 estudiantes, 234 expuestos, 59 positivos (25,2 %)**. El target del art. 19 aplica a los tres programas (Sistemas 19/80, Electrónica 23/73, Biología 17/81).

| Modelo | n | AUC-PR |
|---|:---:|:---:|
| Separado · Sistemas | 80 | **0,7483** |
| Separado · Electrónica | 73 | **0,7250** |
| Separado · Biología | 81 | 0,5983 |
| Conjunto sin indicador de programa | 234 | 0,6585 |
| Conjunto con indicador de programa | 234 | 0,6615 |

**Los modelos separados ganan** (Δ=−0,0306; p=0,043: significativo y relevante según la regla pre-registrada), y el indicador de programa no aporta (Δ=+0,0030; p=0,453). El conjunto es peor que dos de los tres separados **pese a triplicar los datos**: el problema no es de intercepto sino de estructura poblacional. Es compatible con la propuesta, que compromete seleccionar *un algoritmo* por comparación —único— no una única instancia entrenada. **Requiere decisión de la dirección (D-ALCANCE).**

---

## 3 ter. Dos vías cerradas en negativo

### El target multiclase comprometido es INVIABLE (RC-041)

Se construyó la variable de cuatro clases de la propuesta (graduado / activo / desertor / rezagado) y se le aplicó la regla de viabilidad **pre-registrada en RC-008** (clase minoritaria ≥ 25 y ≥ 5 por pliegue):

| Target | Clase minoritaria | n | Por pliegue | ¿Viable? |
|---|---|:---:|:---:|:---:|
| 4 clases (propuesta original) | ACTIVO | **5** | 1,0 | **No** |
| 3 clases (colapsada) | ACTIVO | **20** | 4,0 | **No** |
| 2 clases (graduación) | GRADUADO | 66 | 13,2 | **Sí** |

Se probaron **tres operacionalizaciones alternativas** de «rezagado» antes de declarar la inviabilidad; ninguna rescata el target, y el cuello de botella es siempre la clase ACTIVO, no la de rezago. Dos causas de fondo: (a) los 20 activos son, en esencia, **el grupo censurado de Biología** (15 de 20), es decir un artefacto de la ventana de observación, no un fenómeno académico; (b) **en estas cohortes el rezago es la norma**: el 63 % de quienes no desertaron excedió el plan nominal de 10 semestres, de modo que una clase que agrupa a dos tercios de la población no discrimina.

**Decisión adoptada:** se sustituye por el **target binario de graduación**, ya evaluado y viable; el rezago pasa a indicador continuo (`periodos_sobre_plan`); los activos se marcan como censurados. **Modifica un entregable comprometido (E2) y necesita ratificación formal de la dirección (D-MULTI).** No es un fracaso sino un resultado: el criterio se fijó *antes* de medir, no después.

### El diseño longitudinal con el art. 19 no predice; el art. 20 daría +0,20 (RC-038, RC-039)

La hipótesis —que incorporar las variables acumuladas de los arts. 19–22 en un diseño por cortes semestrales era la vía de mayor retorno— **queda refutada**. Las variables acumuladas no aportan en el corte 1 (Δ=+0,0062; p=0,514) y **empeoran** el modelo en el corte 2 (Δ=−0,0204; p=0,044), donde por sí solas rinden peor que el azar (lift 0,85×).

La causa está verificada y es sustantiva: **el evento del art. 19 es agudo, no gradual.** Exige reprobar el 100 % de los créditos de un periodo: es un colapso puntual, no un deterioro progresivo. Entre quienes sobreviven a un corte, ninguna variable acumulada distingue a quienes lo activarán después.

Manteniendo todo constante y variando **solo el ancho del target**:

| Definición del evento | AUC-ROC corte 1 | AUC-ROC corte 2 |
|---|:---:|:---:|
| Art. 19 (100 % de créditos) | 0,496 | 0,468 |
| ≥ 75 % de créditos reprobados | 0,603 | 0,567 |
| **Art. 20 (> 50 % de créditos)** | **0,647** | **0,673** |

**Un salto de ~0,20 de AUC-ROC sin tocar muestra, variables ni algoritmo.** El art. 19 tiene 0,47–0,50: no es señal débil, es ausencia de señal, porque el umbral es un filo (hay **1,6 casi-activaciones por cada activación**; la diferencia entre disparar el artículo y no dispararlo es aprobar un solo curso). El art. 20 es además el disparador real del acompañamiento institucional (art. 23).

**Recomendación:** si se quiere un producto con actualización semestral, el target del longitudinal debe redefinirse sobre el art. 20. El modelo vigente de trayectoria completa **no se ve afectado**. Es el resultado más transferible del estudio: demuestra con un experimento controlado que *la definición del evento condiciona la predictibilidad más que el tamaño de muestra o el algoritmo*.

---

## 3 quater. Encargo de la dirección del 29 de septiembre

Los tres bloques solicitados se ejecutaron bajo el mismo protocolo del modelo definitivo (CV-5 anidada, 10 repeticiones, n=80, AUC-PR primaria). **Ninguno mejora a Random Forest; los tres aportan hallazgos que sí cambian decisiones.**

**A · PCA (RC-042).** Aclaración registrada antes de ejecutar: el PCA es no supervisado y por construcción **no puede** demostrar que un conjunto de variables sea el mejor para predecir. Se midió lo que sí admite. Resultado: el PCA **destruye la señal** (AUC-PR **0,3715** frente a 0,7418; p<0,0001), y el PLS supervisado tampoco alcanza (0,4637). Las 19 variables necesitan 13 de 19 componentes para el 90 % de la varianza: no son fuertemente redundantes. **Hallazgo central:** el promedio del primer semestre —40,4 % de la importancia— carga al máximo en **CP3, que explica solo el 8,3 % de la varianza**. Quien hubiera seleccionado por varianza explicada habría descartado la única variable que predice. El conjunto S3 queda respaldado por tres vías independientes.

**B · Modelos bayesianos (RC-043).** Ninguno supera a Random Forest (el mejor, la logística bayesiana con aproximación de Laplace, 0,6190), lo esperable frente a un problema con interacciones. Dos hallazgos no buscados:
- **Colinealidad en el bloque SABER 11.** La posterior asigna a `icfes_total` un coeficiente **positivo y creíble** (+1,56; IC 94 % [+0,84, +2,25]) —más puntaje, más riesgo—, imposible sustantivamente y síntoma clásico de supresión: **VIF 6,66** y **R² = 0,850** contra sus tres áreas. A Random Forest no le afecta (retirar el total deja 0,721 frente a 0,742; p=0,126), así que **el modelo en producción no está comprometido**, pero **toda lectura de coeficientes o importancias dentro de ese bloque es inválida** mientras el total conviva con sus áreas. **Requiere decisión (D-COLIN).**
- **Incertidumbre por caso.** La anchura mediana del intervalo creíble del 94 % de la probabilidad individual es **0,359**, y en **43 de 80 estudiantes (54 %) supera 0,30**. Para esos casos el modelo no está en condiciones de emitir un número. **La app debe mostrar nivel de alerta y puesto relativo, no un porcentaje. Requiere decisión (D-APP).**

**C · Pocos datos (RC-044).** El one-shot / few-shot en sentido estricto **no es trasladable**: descansa en un corpus de preentrenamiento y una estructura por episodios que aquí no existen. Trasladado el mecanismo (prototipos de clase, métrica aprendida), todo queda por debajo de Random Forest, y **aprender la métrica empeora los prototipos** (0,356 frente a 0,437): con 19 positivos, NCA sobreajusta. Lo que sí responde a la pregunta de fondo es la **curva de tamaño muestral**: AUC-PR(n) = **0,838 − 8,843·n^(−1,107)**, R² = 0,994, **techo asintótico estimado 0,838**.

| n total | AUC-PR proyectado | Ganancia |
|:---:|:---:|:---:|
| 80 (hoy) | 0,749 | — |
| 160 (duplicar) | 0,797 | **+0,048** |
| 320 (cuadruplicar) | 0,819 | +0,070 |

**Lectura para la petición de datos:** la curva satura pronto porque el techo lo impone la información disponible, no el número de filas. **Más filas afinan la estimación; más variables mueven el límite.** Las cohortes nuevas son muy valiosas sobre todo porque habilitan la **validación externa que hoy no existe**, la limitación más seria del estudio. Cautela registrada: extrapolar desde 64 casos de entrenamiento es una proyección de orden de magnitud, y **si las cohortes nuevas caen bajo el reglamento de 2022 y las actuales bajo el Acuerdo 015 de 2003, el supuesto se rompe** — lo que enlaza con la primera decisión pendiente.

---

## 4. Implicaciones

| Ámbito | Implicación |
|---|---|
| **Paper del congreso** | **No requiere cambios.** Sus cifras están bien calculadas y ya no menciona los modelos de reprobación. **Cerrado y aceptado:** CICI 2026 (ID 129), Springer LNCS, 4 páginas; evento del **7 al 9 de octubre de 2026** en Villavicencio, presentación construida sobre la plantilla oficial. Reporta el target antiguo porque así se aceptó y **no se reescribe**; conviene llevar preparada la respuesta sobre la definición del target si surge la pregunta. |
| **Informe final (E4)** | Debe incorporar una sección de **marco normativo** y reportar los tres hallazgos. Una fuga detectada y corregida por el propio autor es evidencia de rigor. |
| **Modelo comprometido (E2)** | **Resuelto** (punto 3 bis): reentrenado con el target nuevo bajo validación anidada, **Random Forest sí gana** y lo hace por aplicación directa de la regla pre-registrada (umbral de relevancia práctica ΔAUC ≥ 0,03; por debajo, empate y se prefiere el modelo más simple). Queda pendiente el **empaquetado** `joblib` y el manual técnico. |
| **Variables** | **Resuelto** (RC-032): de las 19 candidatas quedan **6** (conjunto S3) por ablación anidada; el conjunto completo empata sin superarlo (0,7176; p=0,418). Las variables normativas de los arts. 19–22 se incorporaron y **no aportaron** (RC-038). |
| **Diseño longitudinal** | **Corregido** (punto 3 ter): el diseño por cortes **no funciona con el art. 19**, que es un evento agudo. La intuición era acertada en la forma y equivocada en el target: con el art. 20 el AUC-ROC sube a 0,65–0,67. |

---

## 5. Estado y próximos pasos

| Paso | Estado |
|---|---|
| I-1 · Definir la variable objetivo | ✅ Aprobado |
| I-2 · Corregir la imputación de `prom_sem1` (afecta al 18 % de la muestra) | ✅ Completado |
| I-2b · Implementar el target del art. 19 en el pipeline | ✅ Completado |
| I-3 · Reentrenar y comparar los cinco algoritmos | ✅ Completado (RC-023), **superado por I-3 bis** |
| I-3 bis · Comparación definitiva con validación anidada y conjunto S3 | ✅ Completado (RC-033) — **Random Forest, AUC-PR 0,745** |
| I-4 · Retirar los modelos de reprobación | ✅ Completado (RC-022) |
| I-5 · Verificación de Electrónica y Biología | ✅ Completado (RC-036, RC-037) |
| I-6 · Target multiclase de trayectoria | ⛔ **Cerrado como INVIABLE** (RC-041) — no es una tarea pendiente, es un resultado |
| WP-OE1.4 · Diseño longitudinal por cortes | ⛔ **Descartado para el art. 19** (RC-038/RC-039); viable solo con el art. 20 |
| Encargo de la dirección del 29-09 (PCA, bayesianos, pocos datos) | ✅ Completado (RC-042, RC-043, RC-044) |
| E5 · Ponencia | 🟢 **Cerrada.** CICI 2026, ID 129, 7–9 de octubre de 2026 |
| E2 · Empaquetado `joblib` + manual técnico | 🟡 Pendiente, condicionado a **D-COLIN** y **D-APP** |
| E3 · Paquete de datos anonimizado | 🟡 Pendiente y **urgente**: los datos crudos llevan nombres, fechas de nacimiento, direcciones y teléfonos |
| E4 · Informe final | 🟡 Borrador al día; **bloqueado esperando la plantilla LaTeX** de la EPI |
| Validación externa con cohortes nuevas | 🟡 Petición cursada por el asesor el **29-09** ante la Oficina de Sistemas |

### Las cinco decisiones que la dirección debe tomar

Es lo que hoy bloquea el cierre. Ninguna es técnica: todas requieren criterio de la dirección.

| Clave | Decisión | Por qué no puede resolverla el estudiante | Qué desbloquea |
|---|---|---|---|
| **D-REGIMEN** | ¿Las etiquetas se construyen bajo el reglamento vigente (2022) o bajo el **Acuerdo Superior 015 de 2003**, que regía para estas cohortes? | Es una elección normativa, no estadística: **65 de 66 estados de bajo rendimiento se aplicaron bajo la norma anterior**, y simulados sobre los mismos estudiantes cada régimen afecta a 20 personas **pero solo 7 son las mismas** (punto 2.3). | La validez del target y la comparabilidad con las cohortes nuevas (RC-044) |
| **D-MULTI** | Ratificar formalmente la **sustitución del target multiclase por el binario** | Modifica un entregable comprometido en la propuesta (E2 / WP-OE1.3). La evidencia de inviabilidad está cerrada (RC-041); falta el acto formal. | El cierre de E2 y del capítulo de la variable objetivo |
| **D-ALCANCE** | ¿Se entrega **un modelo FCBI o tres modelos por programa**? | La medición favorece a los separados (Δ=−0,0306; p=0,043), pero la forma del entregable y su lectura ante la Facultad es decisión de la dirección. | El empaquetado de E2 y la redacción de la Fase 4 |
| **D-COLIN** | ¿Se conserva `icfes_total` **o** sus tres áreas? | Con ambos presentes (VIF 6,66; R²=0,850) **ninguna interpretación de coeficientes ni de SHAP en el bloque SABER 11 es defendible**. El acierto no cambia; la interpretabilidad sí. | El capítulo de interpretación del informe |
| **D-APP** | ¿Se **calibran** las probabilidades o se **retira el porcentaje** de la aplicación? | El 54 % de los estudiantes tiene un intervalo creíble más ancho que 0,30: la app publica hoy un número que el modelo no sostiene. Es una decisión de riesgo institucional. | La entrega del prototipo y el manual técnico |

**Recomendación del estudiante:** resolver **D-REGIMEN** primero, porque condiciona a las otras cuatro y también el valor de las cohortes nuevas ya solicitadas.

---

## 6. Dos defectos técnicos detectados al implementar

Ambos surgieron durante la ejecución de los pasos correctivos y quedan documentados:

1. **Colisión en el ordenamiento de periodos** (RC-020). La función que ordena periodos académicos colapsaba `AAAA-0` (curso intersemestral) con `AAAA-2` del mismo año, mezclando 133 registros. Al corregirlo —y al excluir el intersemestral de la condición del "100 % de los créditos", conforme a los arts. 15 y 40— el target pasó de 20 a 19 positivos, desaparecieron los 2 casos ambiguos y el desempeño **mejoró ~0,06 de AUC** en todos los algoritmos.

2. **Selección de hiperparámetros no anidada** (RC-021). El protocolo ajustaba hiperparámetros sobre el conjunto completo y luego medía por validación cruzada, lo que sobreestima el desempeño. El sesgo medido es de +0,008 en Random Forest pero **+0,046 en XGBoost**: al no ser uniforme, **invierte el orden entre ambos**. Con validación anidada Random Forest queda por delante. La validación anidada pasa a ser obligatoria.

El segundo hallazgo es relevante para la literatura del área: comparativas de algoritmos con muestras pequeñas que no anidan la búsqueda de hiperparámetros tienden a favorecer a los modelos con más hiperparámetros.

---

## 7. Problemas abiertos declarados

| # | Problema |
|---|---|
| **P16** | Colinealidad en SABER 11 — invalida toda lectura de coeficientes y de SHAP en ese bloque (D-COLIN) |
| **P17** | Probabilidades sin calibrar — la app publica un número que el modelo no sostiene (D-APP) |
| **P18** | **Sin validación externa** — la limitación más seria del estudio. Cohortes solicitadas el 29-09 |
| **P19** | El 44 % de los eventos es simultáneo, no predicho (restringido: AUC-PR 0,473, lift 3,10×) |
| **P20** | Anomalías del extracto: estudiante 160004036; 11 de 25 homologaciones incumplen el art. 46 |
| **P21** | El techo lo impone la información disponible, no el tamaño muestral |

---

**Documentación de respaldo:** `AUDITORIA_2026-09.md` (análisis completo), `MARCO_NORMATIVO.md` (reglamento aplicado al modelo), `ESPEC_I3.md` (protocolo pre-registrado), `PLAN_MEJORAS.md` (priorización vigente), `PLAN_DE_TRABAJO.md` (estado de los entregables) y `REGISTRO_CIENTIFICO.md`, entradas **RC-012 a RC-044** (bitácora reproducible).
