# PLAN OPERATIVO MULTIAGENTE — Ejecución detallada por objetivo
### Complemento operativo de `PLAN_DE_TRABAJO.md` (documento rector). Alineado a la propuesta de grado.
**Propósito:** permitir que múltiples agentes (humanos o de código) trabajen en paralelo y colaboren hasta culminar la propuesta. Cada paquete de trabajo (WP) tiene entradas, salidas, criterios de aceptación y dependencias explícitas.

---

## 0. PROTOCOLO DE COLABORACIÓN (leer antes de tocar nada)

> ### ⚠️ ACTUALIZACIÓN OBLIGATORIA — estado a 2026-09-30
> Antes de reclamar cualquier WP, leer **`AUDITORIA_2026-09.md`** y **`MARCO_NORMATIVO.md`**. Decisiones vinculantes que sustituyen instrucciones previas de este documento:
> - **Variable objetivo de rendimiento:** ya no es `PROMEDIO_CARRERA < 3.0` sino el target derivado del **art. 19 del reglamento vigente** (RC-017). Definición formal en `MARCO_NORMATIVO.md` §3. La elección del régimen normativo sigue siendo **decisión abierta de la dirección (D-REGIMEN)**.
> - **Modelos de reprobación por asignatura:** retirados por fuga temporal (RC-013). No reincorporar sin rediseño ex ante.
> - **Algoritmo ganador:** no se hereda. La comparación se repitió con las cuatro correcciones acumuladas y la gana **Random Forest con AUC-PR 0,745 ± 0,025** (AUC-ROC 0,794), esta vez sin desviar la regla pre-registrada (RC-033). Tras cualquier cambio de target hay que repetirla completa, con prueba pareada corregida (Nadeau-Bengio) y umbral de relevancia práctica **ΔAUC-PR ≥ 0,03** (RC-016, RC-021).
> - **Conjunto de variables:** **6 variables, conjunto S3** (`prom_sem1`, `sin_primer_semestre`, `icfes_total`, `icfes_mat`, `icfes_lec`, `icfes_nat`), fijado por selección **anidada** (RC-032). No son 18 ni 19.
> - **Target multiclase de trayectoria:** declarado **INVIABLE** con la regla pre-registrada (RC-041). Se adopta el binario; falta el acto formal de la dirección (D-MULTI).
> - **Features de los arts. 19–22** (`pct_creditos_reprobados`, `art20_activado`, `veces_cursado`, `promedio_ponderado_acumulado`): ver `MARCO_NORMATIVO.md` §5. El diseño longitudinal con el art. 19 está refutado (RC-038); la vía viva es el **art. 20** (+0,20 de AUC-ROC medido, RC-039 → WP `E-ART20`).
> - **Supuesto declarado:** estabilidad del reglamento vigente. Debe constar en el informe final y en el manual técnico (E2).
>
> ### ⚠️ SCRIPTS VIGENTES Y SCRIPTS APARTADOS
> | Vía | Estado |
> |---|---|
> | `src/entrenar_i3bis.py` | **VIGENTE** — comparación de los cinco algoritmos sobre el target del art. 19 y el conjunto S3 (RC-033) |
> | `src/arnes_experimentos.py` | **VIGENTE** — arnés común que fija el protocolo; todo experimento nuevo se construye sobre él |
> | `src/pca_seleccion.py` · `src/modelos_bayesianos.py` · `src/pocos_datos.py` | **VIGENTES** — encargo de la dirección del 29-09 (RC-042, RC-043, RC-044), ejecutados sobre el arnés |
> | `src/entrenar_principal.py` | **APARTADO** — es el script de I-3, superado por I-3 bis: usa las 19 variables heredadas en vez de S3, con rejillas de presupuesto desigual (RF 48 combinaciones frente a 8 de XGBoost, RC-025) y su resultado exigió una **desviación declarada** de la regla pre-registrada (RC-023 §3). Sus cifras no son comparables con las vigentes |
> | `src/entrenar_materias.py` | **APARTADO** — modelos de reprobación por asignatura retirados por fuga temporal (RC-022); aborta al ejecutarse |
> | `src/models.py` | **APARTADO** — construido sobre el target antiguo `rendimiento_bajo`, descartado por tautológico (RC-012); además selecciona por F1-ponderado y usa `train_test_split`, protocolo superado |
> | `save_evaluation_plots.py` | **APARTADO** — generaba las figuras de evaluación del target antiguo sobre el holdout de n=89. Ya no está en el repositorio; solo queda su rastro en `archivo/control_correcciones.md` |
>
> ### ⚠️ REGLAS METODOLÓGICAS INNEGOCIABLES (salidas de la auditoría)
> Se aplican a **todo** WP que entrene o evalúe un modelo. Incumplirlas invalida el resultado:
> 1. **Validación cruzada anidada obligatoria** — la búsqueda de hiperparámetros va dentro de cada pliegue de entrenamiento. El protocolo no anidado sobreestima y **no lo hace por igual entre algoritmos**: invierte el ranking (RC-021).
> 2. **Todo preprocesado dentro del `Pipeline`** — escalado, imputación, PCA, PLS y selección de variables se ajustan solo con el pliegue de entrenamiento. Fijar una transformación antes de la validación cruzada es fuga: la selección no anidada infló el desempeño en **+0,150 de AUC-PR** (RC-032).
> 3. **Presupuesto de búsqueda equilibrado entre algoritmos** — el número de combinaciones de la rejilla se documenta y se iguala. Con rejillas desiguales XGBoost quedaba último (0,528) y al equilibrarlas recupera **+0,102** y sube al tercer puesto (RC-025, RC-033).
> 4. **AUC-PR como métrica principal, siempre con su línea base explícita** — la del azar es **0,2375** (prevalencia de los 19 positivos sobre 80). Un AUC-PR sin su línea base no es interpretable (RC-033).
> 5. **Pre-registro de las reglas de decisión** — umbral de relevancia, criterio de desempate, orden de parsimonia y reglas de viabilidad se escriben **antes** de ver los resultados. Cualquier desviación se declara como tal (RC-023 §3 es el precedente).
> 6. **La importancia por impureza (MDI) no es fiable** — sesgada hacia variables con muchos valores distintos: dos columnas de ruido puro capturaron el 14,3 % (RC-019), y `nivel_edu_madre` aparecía con 7,6 % de MDI teniendo aporte por permutación de −0,007 (RC-028). **La importancia por permutación sobre datos no vistos sustituye a MDI en todo reporte de variables** (RC-026). Gini sigue siendo adecuado para *decidir las particiones*: son dos usos distintos.

### 0.1 Arranque obligatorio de todo agente
1. Leer `_VERDAD_DE_REFERENCIA.md` (estado real del proyecto; qué cifras están vigentes y cuáles ya no) y después `PLAN_DE_TRABAJO.md` (contexto, objetivos, visión SPADIES, brechas) y `README.md` (estructura, pipeline).
2. Leer este documento y reclamar UN paquete de trabajo (WP) libre respetando dependencias. **El reclamo se registra en `KANBAN_AGENTES.md`** (única fuente de estado; tablero revisado el 2026-09-29 contra la realidad del proyecto): el agente pone su identificador, fecha y estado `EN CURSO` en la fila del WP **en su primer commit**. Un WP con agente asignado no se toca; si un WP lleva >7 días sin commits, cualquier agente puede liberarlo anotándolo.
3. Revisar `REGISTRO_CIENTIFICO.md` (RC-001 … RC-044) para no repetir experimentos ya realizados. Varios WP de este documento **ya están ejecutados**: el estado de cada uno figura al inicio de su ficha y manda el Kanban.
4. **Lo que hoy bloquea el cierre del proyecto no es código, son cinco decisiones de la dirección** (`D-REGIMEN`, `D-MULTI`, `D-ALCANCE`, `D-COLIN`, `D-APP`). Ningún agente las resuelve por su cuenta. Ver `PROBLEMAS_DETECTADOS.txt`, bloque 5.

### 0.2 Reglas innegociables (heredadas de `PLAN_DE_TRABAJO.md` §7)
- Originales de `Datos/` intocables; correcciones solo vía `src/recodificacion.py` → `*_recod.xlsx` (respaldo: `Datos.zip`).
- SEED=42; métricas reportadas SIEMPRE por validación cruzada **anidada** out-of-fold; nada de métricas in-sample. Toda transformación (escalado, imputación, selección, reducción de dimensión) va **dentro del `Pipeline`** y se ajusta solo con el pliegue de entrenamiento.
- Anti-leakage: ninguna feature puede contener información posterior al momento de predicción; `PROMEDIO_CARRERA` solo en targets. En datos longitudinales (estudiante-semestre), la CV se agrupa por estudiante (`GroupKFold`/`StratifiedGroupKFold`) — un mismo estudiante jamás queda en train y test a la vez.
- Alcance: Ing. de Sistemas, Ing. Electrónica, Biología. Lic. en Matemáticas se ignora.
- La app lee métricas desde `src/*.csv`: nunca escribir cifras a mano en `app.py` ni en informes (generar tablas desde los CSV).

### 0.3 Registro científico (obligatorio — insumo del informe final)
**Todo cambio o evaluación con valor científico se anota en `REGISTRO_CIENTIFICO.md`** en el momento en que ocurre, con este formato:

```
### RC-NNN · [fecha] · [Fase CRISP-DM] · [WP]
- Motivación: qué pregunta se quería responder
- Método: qué se hizo exactamente (script/parámetros/datos)
- Resultado: cifras concretas (tabla si aplica)
- Decisión: qué se adoptó y por qué
- Destino en el informe: sección sugerida (o "sin valor para informe" si resulta trivial)
```

Criterio de "valor científico": cambia una decisión metodológica, produce una métrica comparable, revela una propiedad de los datos, o refuta/confirma una hipótesis. Los experimentos fallidos también se registran: son evidencia.

### 0.4 Definición de HECHO (DoD) para cualquier WP
1. Código reproducible en `src/` (o notebook re-ejecutable) con SEED fija.
2. Salidas materializadas (CSV/figura/documento) y referenciadas.
3. Entrada(s) en `REGISTRO_CIENTIFICO.md` si hubo hallazgos.
4. Documento de fase CRISP-DM correspondiente actualizado.
5. `git commit` con mensaje descriptivo. Sin cifras huérfanas (todo número citado debe poder regenerarse).

### 0.5 Mapa de dependencias y paralelización

**El mapa original quedó obsoleto el 2026-09-16.** La cadena que lo articulaba —OE1.3 (target multiclase) → OE1.4 (snapshots) → OE2.3 (modelo principal por cortes)— se rompió por dos resultados: el target multiclase es **inviable** (RC-041) y el diseño por cortes **fracasa con el art. 19** porque el evento es agudo, no gradual (RC-038). El mapa vigente es:

```
[CERRADO]  OE1.1 ─ OE1.2 ─ OE2.1 ─ OE2.2 ─ OE3.1 ─ A-PCA ─ B-BAYES ─ C-POCOS
[CERRADO]  OE1.3 (INVIABLE, RC-041) · OE1.4 (refutado, RC-038)
[PARCIAL]  OE1.5 (df_master_fcbi.csv hecho; falta el paquete anonimizado E3)

D-REGIMEN ──┬──> D-MULTI ──> cierre del capítulo de la variable objetivo
            ├──> D-ALCANCE ─┐
            └──> E-ART20 ───┴──> OE2.3 ──> OE3.2 ──> OE3.3 (requiere además D-COLIN)
                                                └──> OE3.4 (requiere además E-CALIB ← D-APP)
F-EXTERNA · F-ANOMAL ──> bloqueados por la Oficina de Sistemas (petición cursada el 29-09)
E4.1 (espera plantilla LaTeX) ── E4.2 ── E4.3
```
**Ejecutables sin esperar decisión:** `E-SIMULT`, `E-EMBUDO`, `E-PEOR`, `I-5d`, y el paquete anonimizado de OE1.5. Todo lo demás cuelga de `D-REGIMEN`, que es la decisión a resolver primero porque condiciona a las otras cuatro.

---

## OBJETIVO ESPECÍFICO 1 — Caracterizar las trayectorias (CRISP-DM Fases 1–3)

> **Verificación explícita de las fases:** las Fases 1–3 están completas y **re-verificadas sobre los tres programas** (RC-036: dataset FCBI de **262** estudiantes, 234 expuestos, 59 positivos = 25,2 %). Las fichas que siguen se conservan porque documentan el diseño de cada verificación; su estado real figura en la cabecera de cada una.

### WP-OE1.1 — Verificación de comprensión de datos para Electrónica y Biología
> **Estado: HECHO (RC-036).** Salida materializada en `Fase 2/08_verificacion_fcbi.md` y `src/verificacion_fcbi.py`. Veredicto: los programas son **mezclables** (coinciden en género, estrato, Saber 11 y promedio de carrera; difieren en tasa de graduación, 36,8 % frente a 26,3 %), pero medido después se comprobó que los **modelos separados por programa superan al conjunto** (Δ=−0,0306; p=0,043, RC-037). La forma del entregable es decisión abierta `D-ALCANCE`.
- **Pregunta:** ¿lo aprendido sobre los datos de Sistemas (calidad, huecos, semántica) aplica igual a los otros 2 programas?
- **Tareas:**
  1. Auditar cobertura por programa: ¿caracterización tiene las mismas 147 columnas pobladas para E (95) y B (85)? Tasas de nulos por variable y por programa (tabla comparativa).
  2. Verificar llaves: cruce caracterización ∩ historial ∩ promedios por programa (¿cuántos se pierden y por qué?). Equivalente del caso 160004030 (invisibles en historial) en E/B.
  3. Verificar la clasificación de estado final por recencia en E/B (graduados/desertores/en formación por programa) y validar los 42 estados inferidos ya imputados.
  4. EDA comparativo entre programas: distribución de promedios, deserción, Saber 11, estrato — ¿los programas son mezclables en un modelo general o hay heterogeneidad fuerte?
  5. Revisar materias críticas por programa con `indice_materias.py` parametrizado (hallazgo de valor para el informe).
- **Salidas:** `Fase 2/08_verificacion_fcbi.md` + tablas CSV; entradas RC.
- **Aceptación:** decisión documentada "mezclables / no mezclables" con evidencia; inventario de exclusiones por programa con causa.

### WP-OE1.2 — Verificación del sentido de las variables (¿las 19 features heredadas son las correctas?)
> **Estado: HECHO (RC-028, RC-032, RC-042).** Resultado: **no eran las correctas**. La ablación no anidada apuntaba a un top-5 por permutación, pero al repetir la selección **dentro de cada pliegue** el desempeño cayó de 0,826 a 0,6705: el **sesgo de selección era de +0,1499 de AUC-PR**, casi cinco veces el umbral de relevancia pre-registrado (RC-032). El conjunto definitivo es **S3, 6 variables académicas** (`prom_sem1`, `sin_primer_semestre`, `icfes_total`, `icfes_mat`, `icfes_lec`, `icfes_nat`). El PCA se añadió como respaldo a petición de la dirección y **no valida una selección supervisada**: medido bajo el mismo protocolo destruye la señal (0,3715 frente a 0,7418; p<0,0001) y la variable más predictiva vive en CP3, que explica el 8,3 % de la varianza (RC-042). Queda abierta la decisión `D-COLIN`: `icfes_total` tiene **VIF 6,66** y R²=0,850 contra sus áreas, de modo que ninguna lectura de coeficientes ni de SHAP en el bloque SABER 11 es defendible hasta resolverla (RC-043, P16). Las subsecciones que siguen se conservan como registro del diseño; los subconjuntos realmente evaluados son los siete de RC-024/RC-028, no los seis de abajo.
- **Pregunta:** ¿las variables escogidas realmente tienen sentido y aportan? ¿Qué combinación es la mejor?
- **Tareas:**
  1. **Análisis univariado vs target:** cada feature contra el target (tests apropiados: Mann-Whitney/χ²/Spearman) + tamaño de efecto, no solo p-valor.
  2. **Redundancia:** matriz de correlación + VIF. Sospechosos conocidos: `icfes_total` vs sus componentes; `nivel_edu_padre/madre/max`; `sisben_nivel` vs `estrato`.
  3. **Combinaciones de features (ablation):** entrenar con subconjuntos definidos a priori y comparar. **Se usan DOS algoritmos de referencia de familias distintas (cierra la duda C):** Random Forest **y** regresión logística con regularización (L2; L1 como sensibilidad), ambos SEED=42, CV-5, con `StandardScaler` dentro del pipeline para la logística. Una variable solo entra al set final si muestra aporte estable en AMBAS familias (o su exclusión no daña a ninguna); así el set no queda sesgado hacia árboles. Los subconjuntos:
     - S1: solo variables de ingreso (socioeconómicas + Saber 11)
     - S2: S1 + `prom_sem1`
     - S3: solo académicas (`prom_sem1`, Saber 11)
     - S4: solo socioeconómicas
     - S5: set actual completo (18)
     - S6: set reducido por selección automática (RFE / permutation importance / SHAP, umbral por estabilidad entre folds)
  4. **Variables candidatas nuevas:** evaluar incorporar lo hoy descartado con potencial: `icfes_ing`/`icfes_soc` (hoy fuera del set de 18), edad al ingreso (`FECHA_NAC`), `TIPO_AFILIACION`, nº materias 1er semestre, % créditos aprobados 1er semestre (del recod). Justificar inclusión/exclusión con las mismas pruebas.
  5. Conclusión: **set de features definitivo ÚNICO y común a todas las familias** con justificación empírica (no por herencia). La comparación de algoritmos exige que todos vean la misma información; la colinealidad residual se mitiga dentro de cada pipeline (regularización en LogReg/SVM), y si el VIF es extremo se decide con evidencia qué variable fusionar/retirar (p. ej. `icfes_total` vs. componentes) para TODOS los modelos por igual.
- **Salidas:** `Fase 3/05_seleccion_variables.md` con la tabla de ablation (subset × métricas); entradas RC (este WP es de alto valor para el informe: sección de selección de variables).
- **Aceptación:** cada feature del set final tiene evidencia a favor; cada descartada tiene causa; la tabla de ablation es reproducible por script (`src/ablation_features.py`).

### WP-OE1.3 — Target multiclase de trayectoria
> **Estado: HECHO (RC-041) — el target se declara INVIABLE.** La regla de viabilidad pre-registrada del punto 2-bis se aplicó y disparó: con cuatro clases la minoritaria **ACTIVO queda en n=5**, y con tres en n=20. El hallazgo de fondo es que la ventana de observación (~17 periodos frente a un plan nominal de 10) agotó las trayectorias: entre quienes no desertaron, **el 63 % excedió el plan nominal**, de modo que «rezagado» no describe un subgrupo en riesgo sino la condición habitual de quien persiste. Además, **15 de los 20 activos son de Biología**: la clase captura la censura del programa, no un fenómeno académico. Se adopta el **target binario de graduación**, el rezago pasa a indicador continuo secundario (`periodos_sobre_plan`) y los 20 activos se marcan `censurado = 1`. Esto **modifica el entregable E2**, por lo que requiere el acto formal de la dirección: decisión abierta `D-MULTI`. Salidas: `src/target_multiclase.py`, `src/df_master_fcbi_multiclase.csv`, `src/multiclase_distribucion.csv`. No es un fracaso sino un resultado: la regla se fijó de antemano y no se ajustó al resultado.
- **Tareas:**
  1. Definición formal de las 4 clases (regla determinista sobre `historial_estados_recod` + recencia): `graduado`, `desertor` (formal o inferido), `activo`, `rezagado`.
  2. **Definir "rezagado" con la codirectora** (propuestas a evaluar empíricamente: (a) activo con > tiempo nominal sin graduarse; (b) avance de créditos < X % del esperado a su semestre; (c) graduado en > 12 semestres). Documentar la elegida y las descartadas.
  2-bis. **Regla de viabilidad pre-registrada (cierra la duda B):** tras construir la etiqueta se mide el tamaño de la clase `rezagado`. Si tiene **< 25 estudiantes en total o < 5 por fold esperado**, el target oficial **colapsa a 3 clases** (`graduado` / `desertor` / `activo`) y el rezago se maneja como **indicador secundario continuo** (avance de créditos vs. esperado, tarea de regresión o score descriptivo), manteniendo el modelo de riesgo de bajo rendimiento como señal operativa asociada. La decisión (4 vs 3 clases) se toma con esta regla ANTES de ver métricas de modelos, se valida con la codirectora y se registra en RC.
  3. Construir `trayectoria` para los 3 programas; tabla de distribución de clases por programa; análisis de desbalance y estrategia (pesos de clase preferible a SMOTE con n pequeño — decidir con evidencia).
- **Salidas:** función en `src/preprocessing.py`; columna en dataset maestro; `Fase 3/06_target_trayectoria.md`; entradas RC.
- **Aceptación:** cada estudiante del alcance tiene exactamente una clase; la regla es determinista y auditada contra 10 casos manuales.

### WP-OE1.4 — Diseño longitudinal (snapshots estudiante-semestre, visión SPADIES)
> **Estado: HECHO (RC-038, RC-039) — el diseño por cortes queda CERRADO para el art. 19.** Se construyó (`src/longitudinal.py`, `src/longitudinal_dataset_k1..k3.csv`, `src/longitudinal_panel.csv`) y se refutó la hipótesis: las variables acumuladas no aportan en el corte 1 (p=0,514) y **empeoran** en el corte 2 (Δ=−0,0204; p=0,044). La causa está verificada y es sustantiva: **el evento del art. 19 es agudo, no gradual** —exige reprobar el 100 % de los créditos de un periodo, un colapso puntual y no un deterioro progresivo—, con **1,6 casi-activaciones por cada activación real**. Entre quienes sobreviven a un corte, ninguna variable acumulada distingue a quienes lo activarán después. **La vía viva es el art. 20**, que sí es gradual, es el disparador real del acompañamiento del art. 23 y daría **+0,20 de AUC-ROC** frente al art. 19 en este diseño (RC-039). Esa redefinición es el WP `E-ART20`, y de ella cuelga WP-OE2.3. Las reglas de diseño que siguen **siguen siendo vinculantes** cuando se retome el longitudinal con el art. 20.
- **DECISIÓN DE DISEÑO (cierra la duda A — sesgo de supervivencia):** se entrena **un sub-modelo por corte** (al ingreso, fin de sem 1, fin de sem 2, …), **NUNCA un único modelo que mezcle todos los k**. Mezclar cortes convierte la exposición temporal en un proxy masivo de supervivencia (quien llega a k=9 casi siempre se gradúa) que opaca los factores tempranos. Reglas derivadas:
  1. La población del corte k son SOLO los estudiantes activos al inicio de k; la predicción es **condicional a estar activo en k** (se declara así en el informe y en la app).
  2. "Semestre actual"/nº de periodos cursados NO es feature dentro de un corte (es constante o proxy de exposición).
  3. Solo se modelan los cortes con muestra y clases suficientes (regla: n_corte ≥ 60 y clase minoritaria ≥ 15; se espera cubrir del ingreso a ~fin de sem 4). Los cortes tardíos se reportan solo descriptivamente.
  4. La curva "desempeño vs corte" (OE3.3) se construye con estos sub-modelos comparables.
- **Tareas:**
  1. Construir dataset estudiante-semestre: para cada corte k, features acumuladas SOLO con información disponible hasta k (promedios, créditos, reprobaciones, repitencias acumuladas + las de ingreso).
  2. Verificación anti-leakage por corte (checklist automatizado: ninguna columna usa periodos > k).
  3. Tabla de tamaños muestrales y distribución de clases por corte (insumo de la regla del punto 3).
  4. Nota metodológica: CV agrupada por estudiante obligatoria si algún análisis combina cortes.
- **Salidas:** `src/snapshots.py` + `df_snapshots.csv`; `Fase 3/07_snapshots_longitudinales.md`; entradas RC.
- **Aceptación:** para un estudiante de prueba, los valores de cada corte se verifican a mano contra sus registros; el checklist anti-leakage pasa; ningún experimento mezcla cortes en un solo entrenamiento.

### WP-OE1.5 — Dataset maestro FCBI final (entregable E3)
> **Estado: PARCIAL (RC-037).** `src/df_master_fcbi.csv` ya está construido con los tres programas (262 estudiantes). Lo que falta es el **paquete anonimizado** y el diccionario actualizado; es ejecutable sin esperar ninguna decisión. El target multiclase que la ficha daba por supuesto no existe (ver WP-OE1.3) y los snapshots solo cubren los cortes 1–3 (ver WP-OE1.4). Pendiente también documentar el **embudo de poblaciones** 275 → 262 → 234 → 80 y qué población usa cada target (WP `E-EMBUDO`).
- **Tareas:** consolidar 3 programas + target multiclase + snapshots; imputaciones documentadas; split final (agrupado por estudiante); **versión anonimizada** (sin nombres, códigos hasheados) + diccionario de datos actualizado → paquete de entrega para el equipo investigador.
- **Salidas:** `src/df_master_fcbi.csv`, paquete `entrega_datos/` anonimizado, diccionario.
- **Aceptación:** E3 cerrado; un tercero entiende cada columna sin leer código.

---

## OBJETIVO ESPECÍFICO 2 — Implementar algoritmos de ML (CRISP-DM Fase 4)

### WP-OE2.1 — Revisión de los modelos actuales (verificación de Fase 4 existente)
> **Estado: HECHO (`AUDITORIA_2026-09.md`, RC-012 … RC-022).** Resultado: los modelos preliminares **no eran correctos**. El target era tautológico (RC-012), los cinco modelos de reprobación por asignatura tenían fuga temporal y se retiraron (RC-013, RC-022), y el protocolo de selección de hiperparámetros no era anidado (RC-021). Ninguna de las decisiones heredadas que la ficha pedía «confirmar o refutar» sobrevivió: el umbral único 0,29 se sustituyó por un **esquema de tres niveles seleccionable** —0,62 (11 alertas, precisión 1,000), 0,12 (52 alertas) y 0,06 (66 alertas, detecta el 100 %)— (RC-034), y las rejillas de hiperparámetros **no eran suficientemente amplias ni equilibradas** (RC-025).
- **Pregunta:** ¿los modelos preliminares (binarios + por materia) son correctos, reproducibles y qué papel juegan? (ya definido en `PLAN_DE_TRABAJO.md` §4.2-bis: preliminares/componentes, no E2).
- **Tareas:**
  1. Re-ejecutar `entrenar_i3bis.py` desde cero y confirmar que las métricas publicadas se reproducen exactamente (SEED). ⚠ `entrenar_materias.py` está apartado: los modelos de reprobación por asignatura se retiraron en RC-022.
  2. Auditoría anti-leakage independiente (agente distinto al que los construyó).
  3. Confirmar/refutar decisiones heredadas con los datos vigentes: sin SMOTE vs pesos de clase; umbral 0.29; grids de hiperparámetros (¿suficientemente amplios?).
  4. Documentar su rol final en el informe (preliminares que validaron pipeline + componente de riesgo de bajo rendimiento de la app).
- **Salidas:** acta de auditoría en `Fase 4/05_auditoria_modelos_preliminares.md`; entradas RC.
- **Aceptación:** reproducción exacta o discrepancias explicadas y corregidas.

### WP-OE2.2 — Framework de comparación completo (algoritmos de la propuesta)
> **Estado: HECHO (RC-033).** El framework vigente es **`src/entrenar_i3bis.py`**, apoyado en `src/comparacion_estadistica.py` (Nadeau-Bengio) y `src/instrumentacion.py` (bitácora reproducible). Cubre los cinco algoritmos de la propuesta sobre el conjunto S3 y el target del art. 19 (n=80, 19 positivos), con CV-5 anidada × 10 repeticiones, rejillas de 16–24 combinaciones equilibradas y SEED=42. Resultado: **Random Forest 0,745 ± 0,025** de AUC-PR (línea base del azar 0,2375), superando de forma significativa y relevante al Árbol (Δ=+0,131; p=0,005), a la Logística (Δ=+0,196; p=0,005) y a XGBoost (Δ=+0,115; p=0,004); frente a SVM la diferencia es +0,032 con p=0,234, de modo que se declara empate y el orden de parsimonia pre-registrado coloca a Random Forest antes. **Esta vez la regla pre-registrada selecciona sola al ganador, sin desviación de protocolo.** El arnés común para experimentos nuevos es `src/arnes_experimentos.py`.
- **Tareas:**
  1. ~~Extender `entrenar_principal.py`~~ → ejecutado en `src/entrenar_i3bis.py` con los 5 candidatos de la propuesta: **regresión logística (baseline)**, árbol de decisión, Random Forest, **SVM**, XGBoost. El MLP opcional no se incorporó. ⚠ `entrenar_principal.py` está apartado (protocolo no anidado, RC-021): no extenderlo.
  2. Pipelines correctos por familia: LogReg/SVM/MLP requieren `StandardScaler` DENTRO del pipeline de CV (los árboles no); SVM con `probability=True` o calibración para salidas probabilísticas.
  3. ~~Soporte multiclase~~ — innecesario: el target multiclase es inviable (RC-041). Rejillas documentadas en `Fase 4/03_hiperparametros_seleccion.md`, con el presupuesto de búsqueda igualado y auditable (RC-025).
- **Salidas:** framework único que recibe (dataset, target) y produce la comparativa CSV estandarizada.
- **Aceptación:** correr el framework sobre el target binario actual reproduce los resultados conocidos de DT/RF/XGB (prueba de regresión) y añade LogReg/SVM.

### WP-OE2.3 — Modelo principal de trayectoria (candidato a E2)
> **Estado: BLOQUEADO.** El diseño por cortes fracasa con el art. 19 (RC-038), de modo que este WP requiere antes `D-REGIMEN` y `E-ART20`. La ficha describe el modelo multiclase comprometido en la propuesta, que **ya no es el entregable**: el target es binario (RC-041). No reclamar hasta que la dirección resuelva.
- **Depende de:** `D-REGIMEN`, `E-ART20`, OE1.5, OE2.2 *(OE1.3 y OE1.4 quedaron cerrados en negativo)*.
- **Tareas:**
  1. ~~Entrenar los candidatos sobre el target multiclase FCBI~~ → **anulado** (RC-041). Lo que corresponde es entrenar sobre el target **binario** del artículo que se decida (`D-REGIMEN`, §5.1 de `MARCO_NORMATIVO.md`), y la variante por programa **no es un análisis de sensibilidad sino la candidata ganadora** (Δ=−0,0306; p=0,043, RC-037): decidirlo es `D-ALCANCE`.
  2. Entrenar sobre snapshots (predicción al ingreso y por semestre).
  3. Modelo complementario de riesgo de bajo rendimiento extendido a FCBI (salida (c) de la visión SPADIES).
  4. Registrar TODOS los experimentos en RC (configuración → métricas), incluidos los perdedores.
- **Salidas:** `src/comparativa_trayectoria.csv` (algoritmo × clase × métrica × corte), modelos serializados.
- **Aceptación:** todos los candidatos evaluados con el mismo protocolo; ninguna configuración sin registrar.

### Encargo de la dirección del 2026-09-29 — tres bloques, todos CERRADOS

Se ejecutaron a cambio de que la dirección gestionara las cohortes nuevas ante la Oficina de Sistemas. Los tres se construyeron sobre **`src/arnes_experimentos.py`**, que fija el protocolo de I-3 bis (CV-5 anidada × 10 repeticiones, n=80, 19 positivos, AUC-PR primaria, línea base 0,2375) y obliga a que toda transformación vaya dentro del `Pipeline`.

| WP | Script | Resultado | RC |
|---|---|---|---|
| **A-PCA** | `src/pca_seleccion.py` | El PCA **no puede** validar una selección supervisada —es no supervisado— y medido **destruye la señal**: 0,3715 frente a 0,7418 (p<0,0001). La variable más predictiva alcanza su carga máxima en **CP3, que explica el 8,3 % de la varianza**: seleccionar por varianza explicada la habría descartado | RC-042 |
| **B-BAYES** | `src/modelos_bayesianos.py` | Ningún modelo bayesiano supera a Random Forest, pero la posterior destapa **colinealidad** en SABER 11 (`icfes_total` con **VIF 6,66** y R²=0,850 contra sus áreas) y que el **54 %** de los estudiantes tiene un intervalo creíble más ancho de 0,30 → abre `D-COLIN` y `D-APP` | RC-043 |
| **C-POCOS** | `src/pocos_datos.py` | El *few-shot* no es trasladable sin corpus de preentrenamiento. La curva de tamaño muestral es AUC-PR(n) = **0,838 − 8,843·n^(−1,107)**, R²=0,994: duplicar la muestra compra ≈ **+0,048**. **El techo lo impone la información disponible, no el número de filas** (P21) | RC-044 |

> **Lectura operativa para cualquier agente:** más filas mejoran la estimación; más **variables** mueven el límite. De ahí que la petición a la Oficina de Sistemas incluya **asistencia** (obligatoria por el art. 58, luego debe registrarse), fechas de pago y créditos inscritos frente a cancelados. Ver `MARCO_NORMATIVO.md` §6 y §7.

---

## OBJETIVO ESPECÍFICO 3 — Evaluar, comparar y seleccionar (CRISP-DM Fase 5)

### WP-OE3.1 — Protocolo de evaluación
> **Estado: HECHO (RC-021, `ESPEC_I3.md`).** El protocolo quedó pre-registrado antes de ejecutar los experimentos, como exigía la ficha. Diferencias con lo previsto aquí: la métrica principal es **AUC-PR con su línea base del azar declarada (0,2375)**, no las métricas multiclase —el target es binario (RC-041)—; la CV es **5 × 10 repeticiones anidada**, no 5×5; y la **calibración sigue pendiente**: el 54 % de los estudiantes tiene un intervalo creíble más ancho de 0,30 (RC-043), de modo que la app publica hoy un número que el modelo no sostiene (P17). Está abierto como `E-CALIB`, dependiente de la decisión `D-APP`.
- Métricas por clase: Accuracy, Precision, Recall, F1 (por clase y macro), AUC-ROC (OvR por clase), matriz de confusión multiclase. **Calibración de probabilidades** (Brier score + curvas de calibración): imprescindible porque el producto entrega probabilidades (visión SPADIES) — una probabilidad mal calibrada es un producto engañoso.
- Variabilidad: media ± desviación entre folds; CV repetida (5×5) si el presupuesto de cómputo lo permite.
- **Salida:** `Fase 5/04_protocolo_evaluacion.md` (escrito ANTES de mirar resultados finales, para evitar sesgo de selección).

### WP-OE3.2 — Comparativa final y selección del ganador único
> **Estado: BLOQUEADO (depende de WP-OE2.3).** La comparativa **transversal** ya está hecha y la gana Random Forest (RC-033); lo que falta es la comparativa **entre cortes** que describe esta ficha, y no puede ejecutarse hasta redefinir el target longitudinal al art. 20 (`E-ART20`). El criterio primario declarado aquí (F1-macro por desbalance multiclase) **ya no aplica**: con target binario y clases desbalanceadas la métrica primaria es AUC-PR, y el desempate es el orden de parsimonia pre-registrado.
- Tabla única algoritmo × métricas; diferencias evaluadas con test apropiado (p. ej. McNemar sobre predicciones OOF o comparación por folds).
- Selección del **algoritmo ganador único** con criterio explícito declarado a priori (propuesto: F1-macro como primario por desbalance multiclase; AUC-OvR y calibración como desempate; interpretabilidad como criterio cualitativo final).
- **Selección con el diseño por cortes (WP-OE1.4):** la comparativa se ejecuta en cada corte modelable y el ganador se elige por **rango promedio entre cortes** (mejor posición media en F1-macro). Si hay empate o inversiones fuertes entre cortes, decide el **corte primario declarado a priori: fin de semestre 1** (máximo valor institucional — primera alerta accionable).
- **Salida:** decisión documentada → responde la pregunta problema. Entrada RC de máxima prioridad para el informe.

### WP-OE3.3 — Interpretación institucional
> **Estado: BLOQUEADO (WP-OE3.2 + `D-COLIN`).** **El SHAP no es interpretable hasta resolver la colinealidad de SABER 11** (`icfes_total` con VIF 6,66 y R²=0,850 contra sus áreas, RC-043 / P16): con ambos bloques presentes, ninguna atribución por variable en ese bloque es defendible. El acierto del modelo no cambia; su interpretabilidad sí.
- Importancias **por permutación** + SHAP del ganador: factores asociados a permanencia, deserción y rezago (el "para qué" del OG). ⚠ **Nunca reportar importancia MDI** (RC-019, RC-026).
- Curva de desempeño por corte semestral: ¿cuánto mejora la predicción con cada semestre de historia? (hallazgo central estilo SPADIES; ya sabemos que `prom_sem1` domina — verificar si se sostiene en multiclase).
- Validación con el equipo de investigación (codirectora): coherencia de los patrones con el conocimiento experto de la FCBI. Acta breve.
- **Salida:** `Fase 5/05_interpretacion_institucional.md`; figuras para el informe.

### WP-OE3.4 — Empaquetado del ganador y app (E2 + visión de producto)
> **Estado: BLOQUEADO (WP-OE3.2 + `E-CALIB`).** Dos premisas de la ficha cayeron: las probabilidades de trayectoria multiclase (`p_graduado`, `p_desertor`, `p_rezagado`) no existen —el target es binario (RC-041)— y los sub-modelos por corte tampoco, porque el diseño longitudinal con el art. 19 está refutado (RC-038). Pendiente además la decisión `D-ALCANCE`: los **modelos separados por programa** superan al conjunto (Δ=−0,0306; p=0,043, RC-037), lo que cambia qué carga el paquete. El contrato de entrada/salida se redacta cuando esas tres decisiones estén tomadas, no antes.
- **ACLARACIÓN DE ARQUITECTURA (cierra la duda E):** "UN modelo ganador" es la respuesta científica (un algoritmo para el target de trayectoria). El artefacto entregable E2 es un **paquete de inferencia** (bundle) que bajo el capó carga **varios `.pkl`**: los sub-modelos de trayectoria por corte (todos del algoritmo ganador) + el modelo binario de riesgo de bajo rendimiento. El contrato JSON lo declara explícitamente: entrada = features del estudiante + corte k; salida = `{p_graduado, p_desertor, p_activo[, p_rezagado], riesgo_bajo_rendimiento, corte_usado, version_modelo}`. Una clase `PaqueteTrayectoria` (predict unificado) esconde la orquestación.
- Serialización versionada (joblib) + contrato de entrada/salida (JSON schema) + `MANUAL_TECNICO_INTEGRACION.md`.
- Actualizar la aplicación al modelo ganador: vista por estudiante con probabilidad de graduación/deserción/rezago, riesgo de bajo rendimiento, y evolución por semestre. (Tecnología final se decide aquí; Streamlit afinado es el default salvo decisión en contra.)
- **Aceptación:** un tercero predice con el modelo sin leer el código; la app muestra las 4 salidas de la visión SPADIES.

---

## E4 — REDACCIÓN DEL INFORME FINAL (LaTeX)

> La estructura del documento la define la plantilla que aportará el estudiante — **no inventar estructura**. Lo que sigue son las instrucciones de redacción, procedimiento, resultados y conclusiones que cualquier agente redactor debe seguir.

### E4.1 Reglas de redacción (estilo)
1. **Voz y tiempo:** impersonal formal ("se entrenaron los modelos", nunca "entrenamos"); pasado para el procedimiento, presente para hechos y conclusiones vigentes.
2. **Prosa argumentativa:** párrafos completos con hilo lógico (afirmación → evidencia → implicación). Las listas solo para enumeraciones genuinas (p. ej. criterios); jamás como sustituto de la argumentación.
3. **Terminología estable:** un solo término por concepto en todo el documento (deserción — no "abandono" intercambiado; rezago; trayectoria; reprobación). Definir cada término y sigla en su primera aparición (FCBI, CRISP-DM, CV, AUC, SPADIES...). Mantener un glosario de trabajo.
4. **Cifras:** métricas con 3 decimales; porcentajes con 1 decimal; consistencia total entre texto, tablas y figuras. **Ningún número escrito a mano**: toda cifra proviene de un CSV/script del repo (citar el archivo fuente en comentario LaTeX `% fuente: src/...`). Si una cifra cambia al re-entrenar, debe poder localizarse y actualizarse.
5. **Español técnico correcto**, sin anglicismos innecesarios (usar "validación cruzada", no "cross-validation", salvo primera mención con paréntesis). Los nombres de algoritmos se mantienen en inglés (Random Forest, XGBoost).
6. **Tablas y figuras:** todas numeradas, con título autoexplicativo, referenciadas desde el texto ANTES de aparecer, y con fuente. Nada de figuras decorativas: cada una debe soportar una afirmación del texto.
7. **Citas:** reutilizar la bibliografía de la propuesta (BibTeX); toda afirmación no derivada de este estudio lleva cita.

### E4.2 Redacción del procedimiento (el "cómo")
1. Narrar por fases CRISP-DM, y en cada fase: **qué se hizo → por qué así (justificación frente a alternativas) → con qué resultado**. Las decisiones importantes ya están documentadas; fuentes obligatorias por tema:
   - Recodificación y calidad de datos: `Fase 5/03_impacto_recodificacion_antes_despues.md` + `Fase 2/03_diccionario_datos.md`
   - Selección de variables: RC-028 (ablación) y **RC-032 (selección anidada, resultado principal)**. La tabla de los cuatro conjuntos de RC-032 es material publicable por sí misma: documenta con cifras propias que la selección no anidada infló el desempeño en 0,15 de AUC-PR
   - Target de trayectoria y rezago: RC-041 (inviabilidad del multiclase, con la regla pre-registrada de RC-008)
   - Protocolo de evaluación, validación anidada y anti-leakage: `ESPEC_I3.md`, RC-021, RC-032, `Fase 4/`
   - Equidad del protocolo de comparación (presupuesto de rejilla): RC-025 y RC-033, punto 2 — material publicable
   - Encargo de la dirección del 29-09: RC-042 (PCA), RC-043 (bayesianos y colinealidad), RC-044 (curva de tamaño muestral)
   - Experimentos: `REGISTRO_CIENTIFICO.md` (cada entrada RC con destino asignado DEBE aparecer en el informe)
2. Documentar la **naturaleza iterativa** de CRISP-DM con honestidad: el proyecto volvió de la Fase 4 a las Fases 2–3 (corrección del diccionario, recodificación) y eso mejoró los modelos — es un resultado metodológico valioso, no un desvío que ocultar.
3. Reproducibilidad explícita: semillas, particiones, scripts, versiones de librerías (una tabla), y la regla de originales intactos + transformaciones por script.

### E4.3 Redacción de resultados (el "qué" — justificado)
1. Cada resultado se presenta en tres tiempos: **hecho** (la cifra y su tabla/figura), **contexto** (frente a qué se compara: baseline, estado previo, literatura de la propuesta) y **lectura** (qué significa para la pregunta problema). Prohibido el "data dumping" de tablas sin lectura.
2. Reportar variabilidad siempre (± desviación entre folds); no afirmar superioridad de un algoritmo sin el respaldo del test de comparación (WP-OE3.2).
3. **Resultados negativos se publican:** pruebas no significativas (género, educación parental), configuraciones perdedoras, la fuga temporal detectada en los modelos por asignatura y su retiro (RC-013, RC-022), la inviabilidad del target multiclase (RC-041), el fracaso del diseño por cortes con el art. 19 (RC-038) y el PCA que destruye la señal (RC-042) — construyen la credibilidad del trabajo. Los cuatro se detectaron con reglas fijadas de antemano, y eso es precisamente lo que hay que hacer explícito al redactarlos.
4. El hallazgo "la calidad de los datos determinó el desempeño predictivo" (antes/después de la recodificación) se redacta como resultado de primer nivel, con su tabla comparativa.
5. Interpretación institucional en términos de gestión (factores de riesgo accionables), no solo métricas.

### E4.4 Redacción de conclusiones
1. **Responder literalmente la pregunta problema** (¿cuál algoritmo ofrece el mejor desempeño?) con el ganador, sus cifras y su margen sobre los demás.
2. Una conclusión por objetivo específico (OE1, OE2, OE3), verificable contra lo escrito en resultados — sin introducir información nueva.
3. Limitaciones honestas y concretas: tamaño muestral (**262** estudiantes en la FCBI, de los que 234 están expuestos y solo **80** entran en la población de modelado del art. 19), solo 2 cohortes, desbalance de género, estados imputados/inferidos (proporción exacta), **ausencia de validación externa** —la limitación más seria del trabajo, P18, con cohortes solicitadas el 29-09— y el **44 % de eventos simultáneos, no predichos** (restringido a los predichos: AUC-PR 0,473, lift 3,10×, P19). El **desfase de régimen normativo** (`D-REGIMEN`) se declara como limitación de primer nivel: ver `MARCO_NORMATIVO.md` §1 y §7.
4. Trabajo futuro anclado en hechos del proyecto: integración con la plataforma del proyecto longitudinal (co-investigador), nuevas cohortes, monitoreo de deriva del modelo.
5. Cierre con la contribución: modelo + evidencia de factores + lección metodológica de calidad de datos.

### E4.5 Flujo de trabajo del agente redactor
1. Esperar la plantilla LaTeX del estudiante (no crear estructura propia).
2. Redactar por secciones consumiendo las fuentes del §E4.2; compilar localmente sin errores ni warnings de referencias.
3. Tablas generadas por script (CSV → LaTeX con booktabs) en `informe/tablas/`; figuras desde `figuras/`.
4. Revisión cruzada: otro agente verifica cifra por cifra contra los CSV fuente antes de dar por cerrada cada sección.

---

## CIERRE GLOBAL (criterio de culminación de la propuesta)

| Verificación | Evidencia | Estado a 2026-09-30 |
|---|---|---|
| OE1 cumplido | Dataset FCBI (3 programas, 262 estudiantes) con target **binario** del art. 19 y variables justificadas empíricamente (S3, 6 variables, selección anidada) | **Casi.** Falta el paquete anonimizado E3. El target de trayectoria multiclase y los snapshots no forman parte del entregable: se cerraron en negativo (RC-041, RC-038) y requieren `D-MULTI` |
| OE2 cumplido | 5 algoritmos implementados con rejillas equilibradas y auditables sobre el target del art. 19 (`src/entrenar_i3bis.py`) | **Cumplido** (RC-033) |
| OE3 cumplido | Comparativa con AUC-PR y su línea base + ganador único justificado por la regla pre-registrada + variables interpretadas por permutación | **Parcial.** El ganador está (Random Forest 0,745 ± 0,025) y la regla lo selecciona sola; la interpretación queda bloqueada por `D-COLIN` |
| Pregunta problema respondida | Sección de conclusiones del informe | Pendiente de redacción (E4 espera plantilla) |
| E1–E5 | Artículo sometido · modelo empaquetado + manual · dataset entregado · informe avalado · ponencia certificada | **Ponencia aceptada**: CICI 2026, ID 129, 7–9 de octubre de 2026. E2 y E3 pendientes; E4 bloqueado |
| App (visión SPADIES) | Riesgo de bajo rendimiento con esquema de **tres niveles de umbral** seleccionable (0,62 · 0,12 · 0,06) | **Replanteada.** No hay probabilidades de graduación/deserción/rezago porque el target multiclase es inviable, y el porcentaje que la app muestra hoy no está calibrado: decisión `D-APP` + WP `E-CALIB` |
