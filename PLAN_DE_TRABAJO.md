# PLAN DE TRABAJO — Modelo Predictivo de Trayectoria Académica FCBI
### Documento rector del proyecto de grado · Sustituye a "Propuesta de Proyecto de Grado.pdf" para consulta rápida
**Última actualización:** 2026-09-30 · **Respaldo:** `REGISTRO_CIENTIFICO.md` (RC-001 … RC-044)

> ### Estado global en tres frases
>
> El **modelo binario de bajo rendimiento según el art. 19 está terminado y es defendible**: Random Forest, AUC-PR 0,745 sobre una línea base de azar de 0,2375, con 6 variables y protocolo anidado. La **ponencia está cerrada y aceptada** (CICI 2026, ID 129, 7–9 de octubre). Lo que bloquea el avance **no es código sino cinco decisiones de la dirección** (§9), y la limitación más seria del trabajo —la ausencia de validación externa— depende de las cohortes nuevas solicitadas a la Oficina de Sistemas el 29-09.

> ### ⚠️ Antes de usar cualquier cifra de este documento
>
> 1. **El target `rendimiento_bajo` (`PROMEDIO_CARRERA < 3,0`) está descartado** por tautológico: el promedio de carrera incluye el primer semestre y para el 26 % de la muestra coincide con `prom_sem1`. Sustituido por el derivado del **art. 19** del reglamento vigente (RC-017). Ver `MARCO_NORMATIVO.md` §3.
> 2. **Los cinco modelos de reprobación por asignatura están retirados** (RC-013, RC-022): usaban `prom_global`, del que entre el 70 % y el 83 % procedía de semestres posteriores a la asignatura predicha. Sobrevive únicamente el **índice descriptivo de criticidad**, que no es un modelo.
> 3. **El target multiclase comprometido en la propuesta no es viable** (RC-041). Ver §4.4.
> 4. **Las cohortes 2017-2 y 2018-1 se rigieron por el Acuerdo 015 de 2003**, derogado en 2022, mientras que las etiquetas usan el reglamento vigente. Decisión pendiente (§9).
>
> **Lo abierto está en `PROBLEMAS_DETECTADOS.txt`, bloque 5.** El tablero operativo, en `KANBAN_AGENTES.md`.

---

## 1. Identificación

| Campo | Valor |
|---|---|
| Título | Modelo predictivo de trayectoria académica estudiantil en programas de la FCBI de la Universidad de los Llanos mediante aprendizaje automático |
| Estudiante | Joan David Martínez Hernández (160004716, joan.martinez@unillanos.edu.co) |
| Directora | Ing. Diana Marcela Cardona Román, M.Sc., Ph.D. |
| Codirectora | Sara Cristina Guerrero, Ph.D. (proyecto longitudinal FCBI C07-02-2026-027) |
| Metodología | CRISP-DM (6 fases), proceso iterativo, 5 etapas de desarrollo |
| Duración propuesta | 6 meses |
| Repositorio | https://github.com/JoanDMH/Proyecto_Trayectoria_Acad-mica |

## 2. Problema y objetivos (de la propuesta — texto original, no se modifica)

**Pregunta problema:** ¿Cuál algoritmo de aprendizaje automático ofrece el mejor desempeño predictivo de la trayectoria académica de los estudiantes de la FCBI?

**Objetivo general (OG):** Comparar algoritmos de aprendizaje automático para la predicción de la trayectoria académica de los estudiantes de la FCBI, con el fin de apoyar la identificación de factores asociados a la permanencia, el riesgo de deserción y el rezago.

**Objetivos específicos:**

- **OE1 — Caracterizar** las trayectorias consolidando un conjunto de datos académicos y sociodemográficos de las cohortes 2017-2 y 2018-1 de la FCBI.
- **OE2 — Implementar** algoritmos de ML para modelar la trayectoria, configurando hiperparámetros.
- **OE3 — Evaluar y comparar** los modelos con métricas estándar, seleccionar el de mayor capacidad predictiva e interpretar las variables más relevantes para la gestión institucional.

**Definiciones de la propuesta:**

- **Variable objetivo propuesta:** estado académico al final del seguimiento — **graduado, activo, desertor, rezagado** (multiclase), con salidas probabilísticas. → ⚠️ **Declarada inviable, ver §4.4.**
- **Visión de producto (jul-2026, referencia SPADIES):** para un estudiante dado, la aplicación debe dar (a) probabilidad de graduarse y de desertar, (b) probabilidad de rezago, (c) riesgo de bajo rendimiento, y (d) probabilidad al ingreso actualizada semestre a semestre. → ⚠️ **(d) refutada empíricamente para el art. 19, ver §4.5.**
- **Algoritmos candidatos:** regresión logística, árbol de decisión, Random Forest, SVM, XGBoost; redes neuronales opcional. → ✅ **Los cinco evaluados** (RC-033).
- **Alcance:** Ing. de Sistemas, Ing. Electrónica y Biología. Lic. en Matemáticas fuera del alcance.
- **Despliegue:** este proyecto entrega el modelo empaquetado + manual técnico. La app Streamlit es un prototipo provisional.

## 3. Entregables comprometidos (Tabla 7 de la propuesta)

| # | Producto | Estado a 2026-09-30 |
|---|---|---|
| E1 | Artículo en revista indexada Cat. B/C | 🔴 **No iniciado.** Insumo sobrado: la auditoría metodológica (21 problemas, 3 fugas medidas) es publicable por sí misma. |
| E2 | Modelo entrenado, validado y **empaquetado** + manual técnico | 🟡 **Modelo funcionando, empaquetado pendiente.** El binario del art. 19 está terminado (RF, AUC-PR 0,745). Falta: resolver la calibración (§9), el empaquetado `joblib` y el manual. **El target multiclase comprometido es inviable (§4.4): requiere decisión formal.** |
| E3 | Dataset procesado + diccionario | 🟡 `df_master_limpio.csv` (Sistemas, n=90) y `df_master_fcbi.csv` (262) listos con diccionario. **Falta el paquete anonimizado**, que ahora es urgente: los datos crudos llevan nombres, fechas de nacimiento, direcciones y teléfonos. |
| E4 | Informe final EPI avalado | 🟡 `BORRADOR_INFORME.md` actualizado con todos los hallazgos. **Bloqueado esperando la plantilla LaTeX** de la EPI. |
| E5 | Ponencia en evento científico | 🟢 **CERRADO.** Resumen extenso aceptado en **CICI 2026** (ID 129), Springer LNCS, 4 páginas. Presentación construida sobre la plantilla oficial. Evento: 7–9 de octubre de 2026, Villavicencio. |

## 4. Estado actual (qué está HECHO)

### 4.1 Datos y preparación (OE1)

- **Fuentes:** 6 archivos de la Oficina de Sistemas en `Datos/` (caracterización 337×147, detalle_materias 8 503, historial_estados 1 968, promedios, homologaciones). Respaldo prístino en `Datos.zip`. **Los originales nunca se modifican.**
- **Recodificación reproducible** (`src/recodificacion.py`, validada con la Oficina de Sistemas):
  - Diccionario `OBSERVACION` corregido: `C`=curso intersemestral (antes se creía "cancelada"), `A`/`P`=trámite de grado, `R`/`E`=vacías, `V`=validada. Notas válidas: {N, C, H}.
  - `historial_estados_recod.xlsx`: 2 566 filas = 1 968 originales intactas + 541 imputaciones trazables + 57 estados finales inferidos. Nada se imputa tras un estado terminal original.
  - `detalle_materias_recod.xlsx`: 8 486 filas (−17 trámites fantasma post-graduación, +76 registros con nota recuperados).
- **Dataset de modelado (Sistemas):** `src/df_master_limpio.csv`, 90 estudiantes con actividad académica, 19 variables candidatas.
- **Dataset FCBI:** `src/df_master_fcbi.csv`, **262 estudiantes**, 234 expuestos, 59 positivos (RC-036).

**Embudo de poblaciones — atención, se confunde con facilidad:**

| Población | n | Qué es |
|---|:---:|---|
| Admitidos en ambas cohortes (Sistemas) | 95 | Universo de partida |
| Con actividad académica | 90 | Se excluyen 5 sin ninguna actividad |
| **Expuestos al art. 19** | **80** | Se excluyen 10 más: solo tienen observaciones homologadas, no pueden activar el artículo |
| Positivos del art. 19 | 19 | Prevalencia 23,8 % → **línea base de AUC-PR = 0,2375** |
| FCBI completa (3 programas) | 262 | 234 expuestos, 59 positivos (25,2 %) |

Los 10 excluidos merecen una nota: todos son cohorte 2017-2, todas sus observaciones están en el periodo 2019-0 y son homologaciones. Su `PROMEDIO_CARRERA` medio es 3,71 frente al 3,01 de los 80 expuestos, porque deriva de notas externas y **no es comparable**. Con el target antiguo ninguno habría sido marcado: confirmación independiente de que aquel target era defectuoso.

### 4.2 Modelo vigente (OE2/OE3)

**Protocolo:** CV-5 estratificada **anidada** (búsqueda de hiperparámetros dentro de cada pliegue externo, 4 pliegues internos), 10 repeticiones, SEED=42, sin SMOTE. Métrica primaria **AUC-PR** (la línea base es la prevalencia, no 0,5); AUC-ROC secundaria por ser comparable entre targets. Comparaciones con **t pareada corregida de Nadeau-Bengio**.

| Target | Algoritmo | n | Variables | AUC-PR | AUC-ROC |
|---|---|:---:|:---:|:---:|:---:|
| **Bajo rendimiento (art. 19)** | **Random Forest** | 80 | 6 | **0,745 ± 0,025** | 0,794 |
| Graduación | XGBoost | 90 | 18 | — | 0,853 |

El conjunto de 6 variables (**S3**) es: promedio de primer semestre, indicador de ausencia de primer semestre, y SABER 11 total / matemáticas / lectura / naturales. Se llegó a él por ablación **anidada** tras medir que la selección no anidada inflaba el resultado en **+0,1499 AUC-PR** (RC-032).

**El desempeño pasó de 0,569 a 0,745 usando un tercio de las variables.** La mejora no vino del algoritmo sino de la calidad del diseño experimental.

- Variable dominante: `prom_sem1`, 40,4 % de la importancia → la alerta puede emitirse al cierre del primer periodo.
- Índice descriptivo de criticidad por asignatura (0,70·reprobación + 0,30·repitencia, ambas normalizadas): Matemáticas II (0,983), Física I (0,918), Álgebra Lineal (0,835), Matemáticas I (0,623), Fund. de Programación (0,534). **Es descriptivo, no predictivo.**
- Factores sin efecto detectable: género (Mann-Whitney p=0,246), educación de los padres (Spearman p>0,6), repitencia escolar previa (χ² p=0,215).

### 4.3 Verificaciones adicionales (encargo de la dirección, 29-09)

| Bloque | Resultado | RC |
|---|---|:---:|
| **PCA** como respaldo de la selección | El PCA **no puede** validar una selección supervisada y se demostró midiéndolo: destruye la señal (0,372 frente a 0,742, p<0,0001). La variable más predictiva vive en CP3, que explica el 8,3 % de la varianza | RC-042 |
| **Modelos bayesianos** | Ninguno supera a Random Forest, pero la posterior destapó una **colinealidad** (`icfes_total`, VIF 6,66) y midió que el **54 %** de los estudiantes tiene un intervalo creíble más ancho que 0,30 | RC-043 |
| **Pocos datos / few-shot** | No trasladable sin corpus de preentrenamiento. La curva de tamaño muestral se ajusta a AUC-PR(n)=0,838−8,843·n^(−1,107), R²=0,994: duplicar la muestra compra ≈ **+0,05** | RC-044 |

### 4.4 El target multiclase comprometido es inviable — RC-041

La propuesta compromete un target de cuatro clases (graduado / activo / desertor / rezagado). Aplicando la regla de viabilidad **pre-registrada en RC-008** (clase minoritaria ≥ 25 casos y ≥ 5 por pliegue):

| Operacionalización | Clase minoritaria | n | Por pliegue | ¿Viable? |
|---|---|:---:|:---:|:---:|
| 4 clases (propuesta) | ACTIVO | **5** | 1,0 | No |
| 3 clases (colapsada) | ACTIVO | **20** | 4,0 | No |
| Tres alternativas más de «rezagado» | ACTIVO | 5 / 5 / 20 | — | No |

**El cuello de botella no es «rezagado» sino «activo».** Y hay un hallazgo de fondo: la ventana de observación (~17 periodos frente a un plan nominal de 10) agotó las trayectorias. De los no desertores, **el 63 % excedió el plan nominal**: «rezagado» no describe un subgrupo en riesgo, describe la condición habitual de quien persiste. Además, 15 de los 20 activos son de Biología, es decir, la clase captura la **censura** del programa, no un fenómeno académico.

**No es un fracaso: es un resultado.** La propuesta especificó un target razonable *a priori* y el estudio demuestra, con un criterio fijado de antemano, que la ventana disponible no lo sostiene.

### 4.5 El diseño longitudinal fracasa con el art. 19 — RC-038, RC-039

La visión SPADIES exige probabilidades que se actualicen semestre a semestre. Se construyó el panel y los cortes, y **no funciona para el art. 19**: las variables acumuladas no anticipan el evento.

La causa se aisló variando **únicamente el umbral del evento**, sin tocar muestra, variables ni algoritmo:

| Definición del evento | AUC-ROC corte 1 | AUC-ROC corte 2 |
|---|:---:|:---:|
| Art. 19 (100 % de créditos reprobados) | 0,496 | 0,468 |
| **Art. 20 (> 50 % de créditos)** | **0,647** | **0,673** |

El art. 19 es un **evento agudo**, no gradual: hay 1,6 casi-activaciones por cada activación real. El art. 20, en cambio, es gradual, es el disparador real del acompañamiento institucional (art. 23) y es el único con señal en el diseño por cortes. **Redefinir el producto longitudinal al art. 20 es la mejora medida de mayor retorno.**

### 4.6 Los tres programas no son mezclables — RC-036, RC-037

Biología es una población distinta: 64,7 % de mujeres (frente a 15,8 % y 7,4 %), SABER 11 unos 10 puntos por debajo, promedio de carrera 2,702 (frente a 3,083 y 3,036), y **15 estudiantes aún matriculados** cuyo desenlace se desconoce (censura del 18 %). Los modelos **separados por programa superan al conjunto** (Δ = −0,0306, p=0,043). Sistemas y Electrónica sí son comparables entre sí.

### 4.7 Prototipo de despliegue

`app.py` (Streamlit): perfil del estudiante, factores predictivos, índice de criticidad por asignatura y predictor interactivo. Implementa un **esquema de alerta de tres niveles seleccionable**, porque la capacidad de atención la decide la universidad, no el modelo:

| Nivel | Umbral | Detecta | Precisión | Alertas |
|---|:---:|:---:|:---:|:---:|
| Confirmado | 0,62 | 57,9 % | **1,000** | 11 |
| Equilibrado | 0,12 | 84,2 % | 0,308 | 52 |
| Cobertura total | 0,06 | **100 %** | 0,288 | 66 |

⚠️ La app **sigue mostrando un porcentaje de probabilidad que no está calibrado** (§9, decisión D-APP).

## 5. Brechas frente a la propuesta (qué FALTA)

| # | Brecha | Estado a 2026-09-30 |
|---|---|---|
| B1 | Alcance FCBI | 🟡 **Verificado, no modelado.** Los tres programas tienen el target aplicable y el dataset está construido (262). Falta entrenar los modelos definitivos por programa (bloqueado por D-ALCANCE). |
| B2 | Target de trayectoria multiclase | ✅ **Cerrado con respuesta negativa** (§4.4). Requiere formalización con la dirección. |
| B3 | Algoritmos baseline | ✅ **Cerrado.** Los cinco de la propuesta evaluados con presupuesto de búsqueda equilibrado (RC-033). |
| B4 | Informe final (E4) | 🟡 `BORRADOR_INFORME.md` actualizado; **bloqueado esperando la plantilla LaTeX de la EPI**. |
| B5 | Artículo científico (E1) | 🔴 No iniciado. |
| B6 | Ponencia (E5) | ✅ **Cerrada.** CICI 2026, ID 129. |
| B7 | Manual técnico de integración (E2) | 🔴 No iniciado. Depende de resolver la calibración. |
| B8 | Paquete anonimizado del dataset (E3) | 🔴 **Urgente.** Los datos crudos llevan `NOMBRE`, `FECHA_NAC`, `DIRECCION_ACTUAL`, `BARRIO`, `TELEFONO_ACU`, `IDENTIFICACION_VICTIMA`. |
| B9 | Exploración Power BI | 🟡 Sustituida por Python/Streamlit; documentar la sustitución. |
| B10 | Notebooks desactualizados | 🟡 `Fase 2/05` y `Fase 5/02` tienen salidas previas a la recodificación. Las figuras del target antiguo **no se regeneran**: hay que rehacerlas contra el art. 19. |
| **B11** | **Validación externa** | 🔴 **La limitación más seria.** Todo el desempeño procede de remuestreo sobre una sola muestra de 80. Petición de cohortes nuevas cursada el 29-09. |
| **B12** | **Calibración de probabilidades** | 🔴 La app publica un número que el modelo no sostiene (§9, D-APP). |
| **B13** | **Colinealidad en SABER 11** | 🔴 `icfes_total` tiene VIF 6,66 e invalida toda lectura de coeficientes, importancias o SHAP en ese bloque (§9, D-COLIN). |

## 6. Ejecución operativa

> El tablero con el estado de cada paquete está en **`KANBAN_AGENTES.md`** (revisado contra la realidad el 29-09). El desglose por objetivo y el protocolo multiagente, en **`PLAN_OPERATIVO_AGENTES.md`**. Los hallazgos con valor científico, en **`REGISTRO_CIENTIFICO.md`**, que es la fuente de verdad e insumo directo del informe.

## 7. Plan incremental revisado (hitos)

### H1 — Desbloquear las decisiones de dirección — *prerrequisito de todo lo demás*
Las cinco decisiones de §9. Ninguna se resuelve programando, y tres de ellas (régimen normativo, target multiclase, alcance por programa) modifican entregables comprometidos, así que deben quedar en acta.
- **Criterio de cierre:** las cinco decisiones registradas por escrito con fecha.

### H2 — Saneamiento del modelo vigente — *corto, ya ejecutable*
1. Resolver la colinealidad de SABER 11 (D-COLIN) antes de interpretar nada.
2. Calibrar las probabilidades (isotónica o Platt, **dentro del pliegue externo**) o retirar el porcentaje de la app.
3. Incorporar `peor_periodo` (+0,015 AUC-ROC, p=0,011 y 0,008; y es un criterio que el Programa de Retención entiende: *«ya tuvo un semestre por debajo de 3,1»*).
4. Declarar en la documentación el embudo de poblaciones y el 42 % de eventos simultáneos de Sistemas (44 % en el conjunto de la FCBI).
- **Criterio de cierre:** ninguna cifra publicada sin su matiz.

### H3 — Producto longitudinal sobre el art. 20 — *mayor retorno medido*
1. Redefinir el target del diseño por cortes al art. 20 (+0,20 AUC-ROC ya medido).
2. Re-ejecutar `longitudinal.py` con el target nuevo sobre la FCBI completa (los cortes 1–3 son viables con 262 estudiantes; con Sistemas solo, ninguno lo era).
3. Modelos separados por programa si D-ALCANCE así se resuelve.
- **Criterio de cierre:** probabilidad por estudiante actualizable por corte, con su intervalo.
- **Expectativa honesta:** AUC-ROC 0,65–0,68 es cribado, no precisión. Sirve para priorizar a quién mirar, no para decidir automáticamente.

### H4 — Validación externa — *bloqueado, máxima prioridad al desbloquearse*
En cuanto lleguen las cohortes nuevas: validar el modelo actual sobre ellas **sin reajustar nada**. Es lo único que convierte el estudio de exploratorio en validado.
- ⚠️ Comprobar antes bajo qué reglamento cursaron: si caen bajo el de 2022 y las actuales bajo el Acuerdo 015 de 2003, las etiquetas no son comparables (§9, D-REGIMEN).
- **Criterio de cierre:** AUC-PR sobre cohorte no vista, reportado sin retoques.

### H5 — Empaquetado y transferencia (E2+E3)
1. Modelo en `joblib` versionado + `predict()` de referencia + contrato JSON + versiones de dependencias.
2. `MANUAL_TECNICO_INTEGRACION.md`.
3. **Paquete de datos anonimizado** + diccionario (B8, urgente).
4. Aplicación de despliegue sucesora del prototipo.
- **Criterio de cierre:** un tercero carga el modelo y predice sin leer el código.

### H6 — Informe final (E4) y divulgación (E1)
1. Consolidar el informe EPI en cuanto llegue la plantilla, integrando los 21 problemas documentados y las limitaciones declaradas.
2. Artículo: el ángulo más fuerte no es el modelo sino la auditoría — *tres formas de fuga de información medidas en un estudio real de minería de datos educativos, y cómo el diseño experimental pesa más que la elección de algoritmo*.
- **Criterio de cierre:** documento avalado + artículo sometido.

## 8. Convenciones técnicas obligatorias (para cualquiera que retome)

1. **Nunca modificar los `.xlsx` originales de `Datos/`** (respaldo en `Datos.zip`). Toda corrección va en `src/recodificacion.py`.
2. **Reproducibilidad:** SEED=42 en todo.
3. **Validación anidada, siempre.** La búsqueda de hiperparámetros va DENTRO de cada pliegue externo. Elegirlos fuera infla el resultado (RC-021).
4. **Toda transformación que aprenda de los datos va dentro del `Pipeline`** — escalado, PCA, PLS, selección. Ajustarla antes de la CV es fuga; se midió en **+0,1499 AUC-PR** (RC-032).
5. **Anti-leakage temporal:** nada del futuro del estudiante en las variables. `PROMEDIO_CARRERA` solo en el target y solo en el target antiguo.
6. **Presupuesto de búsqueda equilibrado** entre algoritmos. XGBoost recuperó **+0,102** solo al igualar su rejilla con la de Random Forest: presupuestos desiguales reordenan la tabla entera (RC-025, RC-033).
7. **AUC-PR es la métrica primaria** y su línea base es la prevalencia (0,2375), no 0,5. Reportar siempre la línea base junto a la cifra.
8. **Comparaciones con t corregida de Nadeau-Bengio.** La t clásica es anticonservadora con CV repetida porque los pliegues comparten datos de entrenamiento.
9. **Las reglas de decisión se pre-registran** antes de ver los resultados (umbral, criterio de selección, viabilidad de clases). Es lo que impide que la decisión sea oportunista.
10. **La importancia por impureza (MDI) no es fiable:** se le inyectó ruido puro y capturó el 14,3 % de la importancia. Usar permutación (RC-019).
11. La app lee métricas de `src/*.csv` — tras re-entrenar, **no** editar métricas a mano en `app.py`.
12. Flujo de ejecución completo: ver `README.md`.

## 9. Las cinco decisiones que bloquean el proyecto

Ninguna se resuelve programando. Tres modifican entregables comprometidos y deben quedar en acta.

| # | Decisión | Evidencia | Consecuencia si no se toma |
|---|---|---|---|
| **D-REGIMEN** | ¿Se defienden las etiquetas como *definición operativa actual aplicada retrospectivamente*, o se etiqueta con el Acuerdo 015 de 2003 que regía para esas cohortes? | RC-015, `MARCO_NORMATIVO.md` | Es el punto más atacable en sustentación. Si se decide lo segundo, el target cambia otra vez |
| **D-MULTI** | Formalizar la sustitución del target multiclase por el binario | RC-041, §4.4 | El entregable E2 no puede cerrarse |
| **D-ALCANCE** | ¿Un modelo FCBI o tres por programa? | RC-037, Δ=−0,031 | Bloquea el modelado definitivo y la estructura del informe |
| **D-COLIN** | ¿Se conserva `icfes_total` o sus tres áreas? | RC-043, VIF 6,66, R²=0,850 | Toda interpretación del bloque SABER 11 queda inválida |
| **D-APP** | ¿Calibrar las probabilidades o retirar el porcentaje? | RC-043, 54 % con IC > 0,30 | La app publica un número que el modelo no sostiene |

## 10. Riesgos y mitigaciones

| Riesgo | Estado | Mitigación |
|---|---|---|
| Muestra pequeña | **Cuantificado** | La curva de tamaño da un techo de 0,838 y +0,05 al duplicar. El límite lo impone la información disponible, no el número de filas: **más variables mueven el techo, más filas solo afinan la estimación** |
| Ausencia de validación externa | **Activo, el más grave** | Cohortes nuevas solicitadas 29-09. Mientras tanto, declarar el estudio como exploratorio |
| Clase «rezagado» ambigua | **Resuelto** | No es ambigua: es mayoritaria (63 %), y por eso no discrimina |
| Censura a la derecha en Biología | **Activo** | 15 activos sin desenlace. Marcados con `censurado=1`. El marco correcto sería análisis de supervivencia |
| Datos personales | **Activo y agudo** | Nombres, fechas de nacimiento, direcciones y teléfonos en los archivos. Construir el paquete anonimizado (B8) antes de cualquier difusión |
| Cambio de reglamento entre cohortes | **Activo** | Si las cohortes nuevas caen bajo otro régimen, las etiquetas no son comparables (D-REGIMEN) |
| Corrupción de archivos xlsx (ocurrió 2 veces) | Mitigado | `Datos.zip` intacto + todo regenerable por script |
| Cifras desactualizadas entre documentos | Mitigado | Fuente única: `REGISTRO_CIENTIFICO.md` y los CSV de `src/`. Este plan es el documento rector |
