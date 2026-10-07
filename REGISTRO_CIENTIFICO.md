# REGISTRO CIENTÍFICO
### Bitácora de cambios y evaluaciones con valor científico · Insumo directo del informe final
**Regla:** todo agente anota aquí, en el momento, cualquier experimento, corrección o evaluación con valor científico (ver criterio en `PLAN_OPERATIVO_AGENTES.md` §0.3). Numeración RC-NNN secuencial. Nada se borra: si una entrada queda superada, se marca `[SUPERADA por RC-XXX]`.

---

### RC-001 · 2026-06 · Fase 3–4 · (previo al plan)
- **Motivación:** métricas por materia sospechosamente altas (Matemáticas I F1=1.000 in-sample).
- **Método:** auditoría de features de los modelos por materia; inspección de `construir_features_materias`.
- **Resultado:** dos fugas de información: `prom_global` incluía la nota de la materia objetivo; `nota_mat1` era el propio target en el modelo de Matemáticas I. Tras corregir y pasar a CV out-of-fold: Matemáticas I 0.986→0.867 (F1-w).
- **Decisión:** features anti-leakage permanentes + prohibición de métricas in-sample.
- **Destino en el informe:** metodología (validez interna) + discusión.

### RC-002 · 2026-07 · Fase 2 · (previo al plan)
- **Motivación:** discrepancias entre estados administrativos y actividad académica real (caso 160004013; estudiante 160004030 invisible en historial).
- **Método:** cruce sistemático historial vs detalle de materias; validación con la Oficina de Sistemas del diccionario de `OBSERVACION`.
- **Resultado:** el diccionario estaba mal interpretado (`C` = curso intersemestral, no "cancelada"; vacías-con-nota = cursos reales; `TG`→`A`/`P`). El historial omite matrículas tempranas y estudiantes completos; 2020-2 no existe (pandemia).
- **Decisión:** pipeline de recodificación reproducible (`src/recodificacion.py`): imputación trazable de estados (541), estados finales inferidos (57, criterios 3.1–3.3), regla anti-residuo, eliminación de 17 trámites fantasma post-graduación.
- **Destino en el informe:** preparación de datos (contribución metodológica central).

### RC-003 · 2026-07 · Fase 2–5 · (previo al plan)
- **Motivación:** medir el impacto de la recodificación en la calidad descriptiva y predictiva.
- **Método:** re-ejecución completa del pipeline con datos recodificados (mismo protocolo CV-5, mismas features anti-leakage); comparación antes/después.
- **Resultado:** +76 registros con nota recuperados (Sistemas); n 89→90; tasa real de reprobación de Matemáticas II 44 %→31.5 %; modelos por materia: F1-w promedio 0.832→0.880; Matemáticas II AUC 0.691→0.865 (+0.174). El modelo principal (features independientes de la corrección) se mantuvo estable — evidencia de que la mejora no es una fuga.
- **Decisión:** los datos recodificados son la base oficial del estudio.
- **Destino en el informe:** resultados de primer nivel. Tabla completa en `Fase 5/03_impacto_recodificacion_antes_despues.md`.

### RC-004 · 2026-07 · Fase 4 · (previo al plan)
- **Motivación:** ¿SMOTE es necesario con los targets binarios?
- **Método:** análisis de proporciones de clase (42.2 % / 38.9 % de minoritaria).
- **Resultado:** desbalance leve; SMOTE induciría ruido sintético con n=90.
- **Decisión:** sin SMOTE; re-evaluar en el target multiclase (WP-OE1.3) donde el desbalance puede ser mayor — probable uso de pesos de clase.
- **Destino en el informe:** metodología (manejo de desbalance).

### RC-005 · 2026-07 · Fase 4 · (previo al plan)
- **Motivación:** umbral operativo para el modelo de riesgo de bajo rendimiento.
- **Método:** barrido de umbral sobre probabilidades OOF del RF (0.25–0.50).
- **Resultado:** u=0.29 → Recall+ 0.816 (captura ~8 de cada 10 en riesgo) sacrificando precisión (0.484); u=0.50 → Recall+ 0.579.
- **Decisión:** 0.29 para alertas tempranas (el costo del falso negativo domina en el contexto educativo).
- **Destino en el informe:** evaluación (decisión de umbral orientada al negocio).

### RC-006 · 2026-07 · Fase 2 · (previo al plan)
- **Motivación:** validar si los "desertores sin acta formal" (30 en Sistemas) eran traspasos a otros programas.
- **Método:** cruce por nombre completo contra los 4 programas + análisis de homologaciones (pénsum 602/603) + inicio de actividad.
- **Resultado:** 0 traspasos internos detectados; la homologación al pénsum 603 es migración de plan dentro del mismo programa; 9/10 candidatos solo tienen el bloque administrativo 2019-0.
- **Decisión:** los sin-acta se clasifican por patrón de estados (BR→RETIRADO BR; solo-NRP≥2→NO RENOVACIÓN).
- **Destino en el informe:** preparación de datos (inferencia de estados finales) + limitaciones.

### RC-007 · 2026-07 · Fase 4 · (previo al plan)
- **Motivación:** pruebas de asociación de las preguntas internas (género, educación parental, repitencia escolar).
- **Método:** Mann-Whitney U, Spearman, χ² sobre n=90.
- **Resultado:** ninguna significativa (p=0.246, 0.627/0.862, 0.215). Poder limitado por submuestras pequeñas (15 mujeres).
- **Decisión:** reportar como resultados negativos con su limitación de poder.
- **Destino en el informe:** resultados (hallazgos no significativos) + limitaciones.

---

### RC-008 · 2026-08-03 · Diseño (Fases 3–5) · revisión por agentes
- **Motivación:** cinco dudas/críticas de los agentes asistentes sobre el plan operativo (sesgo de supervivencia, viabilidad de la clase rezagado, sesgo del ablation, mecánica de reclamo, arquitectura del entregable).
- **Método:** revisión de diseño; decisiones pre-registradas ANTES de ejecutar experimentos.
- **Resultado / Decisiones:**
  1. **Longitudinal:** sub-modelo por corte k (nunca mezclar cortes en un entrenamiento); predicción condicional a estar activo en k; cortes modelables solo si n≥60 y clase minoritaria ≥15.
  2. **Rezagado:** regla de viabilidad pre-registrada — si la clase queda con <25 estudiantes o <5 por fold, el target colapsa a 3 clases y el rezago pasa a indicador continuo secundario.
  3. **Ablation:** dos familias de referencia (RF + regresión logística regularizada); set final único y común a todos los algoritmos.
  4. **Coordinación:** estado de WPs en `KANBAN_AGENTES.md` (reclamo en el primer commit).
  5. **E2:** paquete de inferencia dual (sub-modelos de trayectoria del algoritmo ganador + modelo de riesgo de bajo rendimiento) tras un contrato JSON único.
- **Destino en el informe:** metodología (diseño experimental pre-registrado; las decisiones 1–3 son defensa directa contra sesgos conocidos).

### RC-009 · 2026-08-12 · Fase 1 (contexto) · paper de congreso
- **Motivación:** verificar la cifra nacional de deserción usada como antecedente; la codirectora sospechaba que superaba el 50 % y la fuente citada (MEN) podía estar desactualizada.
- **Método:** búsqueda y lectura directa del informe LEE-Javeriana No. 74 (2023), elaborado con datos de SNIES y SPADIES del MEN.
- **Resultado:** la tasa de deserción *por cohorte* a 10 semestres es 36,7 % (cohorte 2016-1), pero la **tasa de graduación acumulada al semestre 15 es 45,1 %**: más de la mitad de quienes ingresan no se gradúa. La cifra "deserción >40 %" era imprecisa como antecedente.
- **Decisión:** en el paper (y en el informe final) se usa el enunciado verificable "más de la mitad no logra graduarse tras quince semestres (graduación acumulada 45,1 %)" citando LEE (2023). No se encontró fuente que sustente >50 % de deserción *específica de ingeniería* por cohorte: no se afirma.
- **Destino en el informe:** introducción (antecedentes) y justificación.

### RC-010 · 2026-08-12 · Fase 5 · paper de congreso
- **Motivación:** objeción de la codirectora: usar la U de Mann-Whitney como "prueba de asociación" es inadecuado.
- **Método:** revisión del uso de cada prueba respecto de su hipótesis.
- **Resultado:** la objeción aplica al *rótulo*, no al test: Mann-Whitney contrasta diferencias entre dos distribuciones independientes (promedio por sexo), Spearman mide correlación (educación parental) y χ² mide asociación entre categóricas (repitencia). Agruparlas como "pruebas de asociación" era incorrecto.
- **Decisión:** cada resultado se enuncia con el verbo que corresponde a su prueba: "no evidenció diferencias" (Mann-Whitney), "no se halló correlación" (Spearman), "ni asociación" (χ²).
- **Destino en el informe:** resultados (hallazgos no significativos) — corrige credibilidad estadística.

### RC-011 · 2026-08-24 · Fase 4–5 · paper de congreso
- **Motivación:** el paper reportaba los modelos de reprobación por asignatura (AUC 0,865–0,939) sin declarar su especificación. Un lector no puede saber con qué se predice.
- **Método:** auditoría de `src/entrenar_materias.py` y `construir_features_materias` (en `src/preprocessing.py`).
- **Resultado:** los modelos usan **solo 3 predictores** —`prom_global` (excluye la asignatura objetivo), `veces_cursada` y `nota_mat1`— y **2** cuando la asignatura objetivo es Matemáticas I (se omite `nota_mat1` por ser el propio target). Rejilla reducida (`n_estimators` 50/100, `max_depth` 2/3) acorde a N=54–73 por asignatura. Se identifica además una debilidad de diseño: `veces_cursada` es información posterior al momento en que la alerta sería útil, por lo que el modelo es descriptivo del patrón de repitencia más que una alerta ex ante.
- **Decisión:** por restricción de espacio (4 páginas), **se retira del paper toda mención a los modelos de reprobación** y se conserva únicamente el **índice de criticidad**, reetiquetado explícitamente como *índice descriptivo* (no modelo). Los modelos permanecen en el repositorio y se reportarán en el informe final con su especificación completa y una variante sin `veces_cursada`.
- **Destino en el informe:** metodología (modelos por asignatura: especificación y limitación de `veces_cursada`) + limitaciones.

### RC-012 · 2026-09-02 · Fase 3–4 · auditoría metodológica
- **Motivación:** verificar la validez del target `rendimiento_bajo` (`PROMEDIO_CARRERA < 3.0`) frente a su predictor dominante `prom_sem1` (40,4 % de importancia).
- **Método:** cruce de `prom_sem1` con `PROMEDIO_CARRERA` estratificando por número de periodos cursados; AUC por CV-5 repetida (6 repeticiones, RF, SEED=42) sobre la muestra completa y sobre subpoblaciones con exposición mínima.
- **Resultado:** **el target es parcialmente tautológico.** El promedio de carrera incluye el primer semestre; para los 17 estudiantes con un solo periodo (19 %) ambos valores casi coinciden (r=0,921; dif. media 0,112). Consecuencias medidas: sin `prom_sem1` el modelo cae a AUC 0,483 (azar) — las otras 17 variables no aportan; y restringiendo a ≥3 periodos el modelo completo cae de 0,761 a **0,546**. El target `graduado` no sufre el problema: entre quienes cursaron ≥6 periodos alcanza 0,876 **sin** `prom_sem1`. Adicionalmente, 16 de 90 estudiantes (18 %) tienen `prom_sem1` imputado con la mediana y ese subgrupo difiere sistemáticamente (12 % vs. 49 % de rendimiento bajo).
- **Decisión:** redefinir el target de rendimiento antes de re-entrenar (opción preferida: promedio de semestres 2..n, que rompe la circularidad sin perder muestra) y sustituir la imputación por mediana por un indicador explícito `sin_primer_semestre`. Las métricas ya publicadas no se corrigen: están bien calculadas; lo que cambia es su interpretación.
- **Destino en el informe:** metodología (definición de variables objetivo) + limitaciones + discusión. Detalle completo en `AUDITORIA_2026-09.md` §1 y §2.

### RC-013 · 2026-09-02 · Fase 4 · auditoría metodológica
- **Motivación:** el asesor propone descartar los modelos de reprobación por asignatura ("precipitados, pocas variables"). Se evalúa empíricamente antes de decidir.
- **Método:** ablación de features con CV-5 × 10 repeticiones; medición de la proporción de `prom_global` proveniente de semestres posteriores a la asignatura objetivo; y re-entrenamiento honesto usando **solo información del semestre 1** para las asignaturas de semestre 2 (único corte temporalmente limpio), con RF y regresión logística.
- **Resultado:** **fuga temporal confirmada.** Las cinco asignaturas críticas son de semestre 1–2, y entre el 70 % y el 83 % de `prom_global` proviene de semestres posteriores: el modelo retrodice, no predice. `prom_global` explica casi todo el desempeño (0,735–0,930 en solitario); `veces_cursada` aislada es inútil o inversa (0,367–0,680) y tampoco es observable ex ante. En el test honesto: las variables de ingreso solas no predicen nada (AUC 0,41–0,51); el desempeño del primer semestre sí aporta señal real pero modesta — Matemáticas II 0,707 y Física I 0,740 (regresión logística con `prom_sem1` + `nota_mat1`), frente al 0,865–0,939 reportado.
- **Decisión:** retirar los cinco modelos actuales del repositorio, la app y el informe. Conservar el índice de criticidad (descriptivo, no afectado). Reconstrucción opcional de una versión honesta limitada a las dos asignaturas de semestre 2 si el cronograma lo permite; no es entregable comprometido. La fuga se reporta como hallazgo metodológico.
- **Destino en el informe:** metodología (validez temporal) + resultados negativos + discusión. La detección y corrección de la fuga es evidencia de rigor.

### RC-014 · 2026-09-02 · Fase 2–4 · incorporación del Reglamento Estudiantil
- **Motivación:** contrastar la definición operativa de "bajo rendimiento" usada en el proyecto contra la norma institucional (`reglamento_estudiantil_unillanos.md`).
- **Método:** lectura del articulado (arts. 17–23, 38, 44 y glosario); extracción del estado administrativo BR desde `historial_estados_recod.xlsx`; comparación con el target actual; AUC por CV-5 × 8 repeticiones sobre ambos targets; cálculo de la viabilidad de las variables de los arts. 19–22 desde `CREDITOS`.
- **Resultado:** **el target del proyecto no es la definición institucional.** El art. 19 exige reprobar el 100 % de los créditos inscritos **y** promedio ponderado < 3,0, **o** reprobar por cuarta vez un curso; el proyecto usa solo `PROMEDIO_CARRERA < 3.0`. Existe verdad de campo: 40 de 90 estudiantes tienen estado BR aplicado por la universidad; coincide con el target actual en 84 % (discrepan 14 casos: 8 sancionados con promedio ≥3,0 y 6 con promedio <3,0 sin sanción). Ninguno de los 40 con BR se graduó. Con el target institucional el modelo se reequilibra: AUC sin `prom_sem1` sube de 0,469 (azar) a **0,642**, y `prom_sem1` en solitario baja de 0,795 a 0,621 — **las 17 variables socioeconómicas y de SABER 11 sí aportan; el problema era el target.** Advertencia: 13 de los 40 recibieron BR en el primer semestre; restringiendo a BR en semestre ≥2 (n=77) el AUC cae a **0,577**, techo real de un modelo de foto única. Los arts. 20–22 aportan variables calculables y no explotadas: >50 % de créditos reprobados (73 eventos), 100 % (24), 2ª reprobación de un curso (181), 3ª (32), 4ª (1).
- **Decisión:** adoptar el **estado administrativo BR (art. 19) como variable objetivo** en sustitución de `PROMEDIO_CARRERA < 3.0`; excluir o modelar aparte los 13 casos de BR simultáneo al primer semestre; incorporar las variables de los arts. 19–22 al conjunto de features; reportar el AUC del corte único junto al longitudinal para demostrar empíricamente la necesidad del diseño por cortes (WP-OE1.4). Queda confirmado por norma lo ya decidido en RC-002/RC-006 (omisión de renovación máx. 2 periodos, art. 17 parágrafo) y el tratamiento de intersemestrales y validaciones.
- **Destino en el informe:** marco normativo institucional (sección nueva), definición de variables objetivo, features y justificación del diseño longitudinal. Detalle en `AUDITORIA_2026-09.md` adenda A.1–A.7.

### RC-015 · 2026-09-02 · Fase 2–4 · cambio de régimen normativo (corrige RC-014)
- **Motivación:** el reglamento vigente rige desde 2022 y sustituyó al Acuerdo Superior 015 de 2003; las cohortes 2017-2 y 2018-1 vivieron casi toda su trayectoria bajo la norma anterior. ¿Son las etiquetas de bajo rendimiento comparables con las que se aplicarán a estudiantes futuros?
- **Método:** fechado de los estados administrativos BR; reconstrucción y simulación de ambas reglas (art. 26 de 2003 vs. art. 19 de 2022) sobre los mismos datos, con promedio ponderado acumulado por periodo y conteo de repeticiones por curso.
- **Resultado:** **65 de 66 registros BR se aplicaron bajo el reglamento de 2003** (42 de 43 estudiantes). Los regímenes no son equivalentes, pero la diferencia **no está en la reprobación reiterada** —la 4.ª es la fatal en ambos; 2022 solo lo hace explícito— sino en el fenómeno que persiguen: 2003 (art. 26) sanciona la reprobación de **>50 % de las asignaturas habiendo aprobado al menos una**, con umbral de promedio 3,2; 2022 (art. 19) sanciona la reprobación del **100 % de los créditos** con promedio <3,0, y reclasifica la pérdida parcial (>50 % de créditos) como simple restricción de carga (art. 20). Simulados sobre los mismos datos, cada régimen afecta a 20 estudiantes pero **solo 7 son los mismos**: los 13 exclusivos de 2003 hoy caerían únicamente en el art. 20 (sin expulsión), y los 13 exclusivos de 2022 **reprobaron el 100 % de sus asignaturas**, caso que el art. 26 de 2003 excluía por exigir literalmente "habiendo aprobado por lo menos una". La 4.ª reprobación es empíricamente marginal (2 eventos, 1 estudiante). Ninguna reconstrucción reproduce bien el estado real (15/43 y 18/43), lo que indica criterios administrativos no recuperables. Un modelo entrenado con etiquetas de 2003 no solo se descalibra: **aprende el fenómeno equivocado** —reprobación parcial, hoy no sancionable con expulsión— y queda ciego al colapso total del periodo.
- **Decisión:** adoptar la **opción (C)**: el modelo predice magnitudes académicas continuas (% de créditos reprobados, promedio ponderado acumulado, repeticiones por curso) y una capa determinista `aplicar_reglamento(version)` traduce el riesgo a la consecuencia normativa vigente. Esto desacopla el modelo de la norma y lo hace invariante a reformas futuras; la comparación 2003 vs. 2022 pasa a ser un resultado del estudio y no una amenaza a su validez. Corrige la recomendación de RC-014, que asumía implícitamente que el estado BR reflejaba el art. 19 vigente.
- **Destino en el informe:** marco normativo, definición de variables objetivo, validez externa y limitaciones. Detalle en `AUDITORIA_2026-09.md` adenda B.1–B.3.

### RC-016 · 2026-09-02 · Fase 4 · estabilidad del algoritmo ganador
- **Motivación:** ¿el ganador (Random Forest) se mantiene al cambiar la variable objetivo?
- **Método:** comparación de Decision Tree, Random Forest, XGBoost, regresión logística L2 y SVM-RBF con hiperparámetros fijos, CV-5 × 10 repeticiones sobre ambos targets; y CV-5 × 30 repeticiones con prueba pareada de Wilcoxon sobre el target institucional.
- **Resultado:** **el ganador cambia.** Con el target actual XGBoost 0,782 > RF 0,758; con el target institucional XGBoost 0,712 ≈ RF 0,707 ≈ LogReg 0,700 — los tres primeros quedan dentro de 0,012 de AUC. Con 30 repeticiones: XGB 0,716±0,037, RF 0,705±0,037, LogReg 0,695±0,033, con intervalos de confianza ampliamente solapados. Wilcoxon da XGB>RF (p=0,031) y XGB>LogReg (p=0,005), pero con tamaños de efecto de +0,011 y +0,020 de AUC; además la prueba es anticonservadora porque las repeticiones reutilizan los mismos 90 estudiantes.
- **Decisión:** repetir siempre la comparación completa tras cualquier cambio de target (nunca heredar el ganador); usar prueba pareada con corrección de Nadeau-Bengio en OE3.2; **pre-registrar un umbral de relevancia práctica de ΔAUC ≥ 0,03**, por debajo del cual se declara empate y se elige el modelo más simple e interpretable; conservar la regresión logística como línea base declarada.
- **Destino en el informe:** metodología (protocolo de selección de modelo) y resultados (comparativa de algoritmos con incertidumbre, no solo puntos).

### RC-017 · 2026-09-02 · Fase 3 · **decisión aprobada** del target definitivo (paso I-1)
- **Motivación:** cerrar la bifurcación abierta por RC-012 y RC-015: qué variable objetivo usar para el modelo de rendimiento, dado que el target original es tautológico y las etiquetas administrativas pertenecen al régimen normativo derogado.
- **Método:** comparación empírica de tres candidatos con CV-5 × 10 repeticiones (RF, XGBoost, LogReg); verificación de la fiabilidad de la reconstrucción normativa contra los cursos inscritos sin nota; decisión de alcance tomada por el estudiante sobre estabilidad futura del reglamento.
- **Resultado:** el target derivado de la regla del art. 19 vigente supera al estado administrativo pese a tener la mitad de positivos — RF 0,767 vs 0,707; XGBoost 0,772 vs 0,712 — porque es una función determinista de los datos académicos y no arrastra discrecionalidad administrativa. La regresión logística cae (0,701 → 0,678), coherente con que el art. 19 es una conjunción que un modelo lineal no representa bien: se anticipa un ganador basado en árboles por razón estructural. Fiabilidad de la reconstrucción: 93 % de los cursos inscritos tiene nota válida; de 19 eventos marcados, 2 (11 %) son dudosos por cursos sin calificar en el mismo periodo; 17 de 19 estudiantes quedan limpios.
- **Decisión (aprobada por el estudiante):** el target del modelo de rendimiento es **`y = 1` si en algún periodo (créditos_reprobados/créditos_cursados == 1 Y promedio_ponderado_acumulado < 3,0) O (reprobó un curso por 4.ª vez)**, según el art. 19 del reglamento vigente, re-derivado sobre los datos históricos. **Se descarta** `PROMEDIO_CARRERA < 3.0` (tautológico) y **se descarta** el estado administrativo como target directo (etiqueta del régimen 2003). **Supuesto declarado:** se asume estabilidad del reglamento vigente durante la vida útil del modelo; si cambia, deberá recalcularse la etiqueta y reentrenarse — se consigna en el informe final y en el manual técnico (E2). Se abandona la capa `aplicar_reglamento(version)` por innecesaria bajo ese supuesto. Los 2 eventos dudosos se marcan explícitamente en el dataset. La predicción de magnitudes continuas se conserva como **salida secundaria opcional** para la visión de producto tipo SPADIES (puntaje graduado actualizable por semestre), no como eje de la arquitectura.
- **Destino en el informe:** preparación de datos (definición de la variable objetivo), marco normativo y limitaciones. Consolidado en `MARCO_NORMATIVO.md` §3.

### RC-018 · 2026-09-03 · Fase 3 · **I-2** · Corrección de la imputación de `prom_sem1`
- **Motivación:** resolver la debilidad metodológica H-3 identificada en la auditoría (`AUDITORIA_2026-09.md` §2 y RC-012). En el pipeline original, 16 de 90 estudiantes (17,8 %) carecían de promedio de primer semestre y recibían una imputación simple de mediana (3,40), asignando un valor promedio neutro a un grupo cuyo comportamiento es sistemáticamente distinto (solo 12 % de bajo rendimiento vs. 49 % en quienes tienen dato real; 19 % de graduación vs. 43 %).
- **Método:** en `src/preprocessing.py` (y su réplica `Fase 3/02_preprocessing.py`), se reemplazó la imputación ingenua por un esquema dual de ingeniería de características: (1) creación de un indicador binario explícito `sin_primer_semestre` (`1` si el estudiante no tiene registro formal de promedio del primer semestre en su periodo de ingreso, `0` si lo tiene); (2) imputación del valor numérico de `prom_sem1` con la mediana muestral de los 74 casos observados (3,40) para preservar la dimensionalidad y evitar valores nulos. Regeneración reproducible de `src/df_master_limpio.csv` (N=90, 19 features).
- **Resultado:** se materializó `src/df_master_limpio.csv` con 90 estudiantes y 19 variables predictoras. La variable `sin_primer_semestre` identifica con exactitud a los 16 estudiantes del subgrupo (11 de la cohorte 2017-2 y 5 de 2018-1). Para los 74 estudiantes con dato real, `prom_sem1` mantiene su distribución original íntegra (media 3,17, DE 0,92, rango [0,80, 4,60], mediana 3,40); para los 16 con dato ausente, `sin_primer_semestre = 1` permite al modelo de aprendizaje automático aislar la ausencia de registro temprano como una señal predictiva diferenciada en vez de confundirla con un rendimiento regular.
- **Decisión:** incorporar formalmente `sin_primer_semestre` al conjunto maestro de features del modelo principal (19 features en total). La salida queda lista como insumo para el re-entrenamiento y evaluación de los 5 algoritmos bajo el target del art. 19 (paso I-3).
- **Destino en el informe:** Fase 3 (Preparación de datos: tratamiento de valores faltantes e imputación informada) + Discusión metodológica (impacto del sesgo de no respuesta / deserción previa al cierre del primer semestre).

### RC-019 · 2026-09-03 · Fase 3 · verificación independiente de I-2
- **Motivación:** validar de forma independiente la ejecución de I-2 (RC-018) antes de habilitar I-3, y medir si el indicador `sin_primer_semestre` aporta capacidad predictiva real.
- **Método:** inspección del código en `src/preprocessing.py` y su réplica; verificación byte a byte de ambos archivos; recomputación de todas las cifras declaradas sobre `src/df_master_limpio.csv`; ablación con y sin el indicador (RF, XGBoost, LogReg; CV-5 × 10 repeticiones) sobre el target del art. 19; y análisis de la composición del subgrupo sin primer semestre.
- **Resultado:**
  1. **Todo lo declarado en RC-018 se confirma exactamente:** shape (90, 31); 74 con dato real (media 3,1743; DE 0,9244; rango [0,80–4,60]; mediana 3,4000) y 16 sin dato (11 de 2017-2, 5 de 2018-1); único valor imputado 3,40; cero nulos en los 19 predictores; `src/preprocessing.py` y `Fase 3/02_preprocessing.py` idénticos. La mediana se calcula correctamente solo sobre los observados (pandas omite NaN por defecto).
  2. **El indicador no mejora la predicción del target del art. 19:** RF 0,767→0,766, XGBoost 0,772→0,769, LogReg 0,678→0,669 (Δ de −0,001 a −0,009). La información resulta redundante frente a `prom_sem1` ya imputado. **Se conserva igualmente** por corrección metodológica —representa la ausencia como categoría en vez de disfrazarla de rendimiento medio— y porque su valor debe re-evaluarse con el target de graduación y con el multiclase.
  3. **Composición del subgrupo:** 10 de los 16 estudiantes sin primer semestre **no tienen ninguna nota propia**; su expediente completo son 25 registros con observación `O` (homologada, nota externa ≥3,0). Por construcción **no pueden activar el art. 19**, que exige reprobar créditos. Verificado que su presencia **no infla las métricas** (al excluirlos: RF +0,011, XGBoost −0,013, LogReg +0,033), pero su inclusión en la muestra de rendimiento debe ser una decisión explícita: pertenecen conceptualmente al fenómeno de deserción, no al de bajo rendimiento.
- **Decisión:** I-2 se da por **válido y correctamente documentado**. Se levanta una condición para I-3: (a) el target del art. 19 **debe implementarse en `src/preprocessing.py`**, no dentro del script de entrenamiento, para que exista una única definición reproducible; (b) `rendimiento_bajo` permanece en el dataset únicamente como referencia histórica y debe marcarse como **obsoleto** para que ningún agente lo use por inercia; (c) la inclusión o exclusión de los 10 estudiantes sin actividad académica se pre-registra antes de entrenar.
- **Destino en el informe:** Fase 3 (tratamiento de faltantes: reportar que el indicador es metodológicamente correcto aunque empíricamente neutro — resultado negativo honesto) y definición de la población de estudio.

### RC-020 · 2026-09-03 · Fase 3 · **I-2b** · Implementación del target del art. 19 y corrección de periodos
- **Motivación:** materializar en el pipeline la decisión RC-017 (target normativo) como única definición reproducible, evitando que cada script de entrenamiento la reimplemente; y resolver las tres condiciones abiertas en RC-019.
- **Método:** se añadió `construir_target_art19()` a `src/preprocessing.py`, integrada en `pipeline_completo()`. Implementa literalmente el art. 19: reprobar el 100 % de los créditos inscritos en un periodo **y** promedio ponderado acumulado < 3,0, **o** reprobar un curso por cuarta vez. El promedio acumulado se calcula ponderado por créditos sobre todos los periodos (art. 19 parágrafo primero: contempla aprobados y reprobados). Réplica `Fase 3/02_preprocessing.py` sincronizada.
- **Resultado — se detectaron y corrigieron dos defectos durante la implementación:**
  1. **Colisión de periodos.** La función de ordenamiento (`anio*2 + (0 si sem=='1' else 1)`) colapsaba los periodos `-0` y `-2` del mismo año en el mismo valor, mezclando **133 registros intersemestrales** con el segundo periodo regular. Corregido a base 3 (`anio*3 + {0,1,2}`), con el intersemestral ordenado al inicio del año.
  2. **Los cursos intersemestrales no constituyen periodo académico.** La condición "100 % de los créditos inscritos" se evaluaba también sobre periodos `-0`, donde el estudiante suele inscribir un solo curso. Se restringe a periodos regulares (`-1`, `-2`): el art. 15 parágrafo define el periodo académico entre matrículas ordinarias y el art. 40 parágrafo tercero excluye la nota intersemestral del promedio de semestre. Su nota **sí** alimenta el promedio ponderado acumulado (art. 40 parágrafo primero). La vía de la cuarta reprobación no se restringe: el art. 19 no la condiciona al tipo de periodo.
  - **Efecto conjunto:** el target pasa de 20 a **19 positivos** y los casos dudosos de 2 a **0** — la ambigüedad detectada en RC-017 era íntegramente un artefacto de la colisión. Con el target corregido el desempeño **mejora en ~0,06 de AUC** en todos los algoritmos: XGBoost 0,829 · Random Forest 0,825 · LogReg 0,775 · Decision Tree 0,761 (CV-5 × 15 repeticiones), frente a 0,769 / 0,766 / 0,669 con la versión defectuosa.
  - **Población pre-registrada:** los 10 estudiantes sin ninguna nota propia (expediente compuesto solo por homologaciones, `OBS='O'`) quedan **fuera de la población en riesgo**: el art. 19 exige reprobar créditos, de modo que no pueden experimentar el evento. Reciben `bajo_rendimiento_art19 = NaN` y `tiene_actividad_academica = 0`. Población de análisis: **n=80, 19 positivos (23,8 %)**. No es sesgo de supervivencia: la exclusión es por falta de exposición, no por el desenlace.
  - `rendimiento_bajo` se marca como **OBSOLETO** con aviso en el código y en la salida del pipeline; permanece solo para comparaciones antes/después. Cruce con el target vigente: coinciden en 57 de 80 casos (17 positivos comunes, 21 solo en el obsoleto, 2 solo en el vigente).
  - Salida: `src/df_master_limpio.csv` (90 × 37) con seis columnas nuevas: `bajo_rendimiento_art19`, `art19_n_eventos`, `art19_primer_periodo`, `art19_dudoso`, `tiene_actividad_academica`, `n_periodos_cursados`. Verificado que `app.py` y `entrenar_principal.py` siguen operando.
- **Decisión:** el target del art. 19 queda como definición única y reproducible en `src/preprocessing.py`. Habilita I-3. Nota para I-3: `entrenar_principal.FEATURES` sigue en 18 variables y apunta al target obsoleto; debe actualizarse a las 19 features y a `bajo_rendimiento_art19` sobre la población expuesta.
- **Destino en el informe:** preparación de datos (operacionalización de la norma), marco normativo (tratamiento del curso intersemestral) y calidad de datos (defecto de ordenamiento de periodos detectado y corregido).

### RC-021 · 2026-09-03 · Fase 4 · Sesgo por selección no anidada de hiperparámetros
- **Motivación:** al preparar I-3 se auditó el protocolo de `src/entrenar_principal.py` y `src/entrenar_materias.py`, que ajustan hiperparámetros con `GridSearchCV.fit(X, y)` sobre el conjunto completo y después miden con `cross_val_predict` usando el mejor estimador.
- **Método:** comparación del protocolo actual contra validación cruzada **anidada** (búsqueda dentro de cada pliegue de entrenamiento, `cv` interna de 4 pliegues), sobre el target del art. 19 y la población expuesta (n=80), CV-5 × 3 repeticiones.
- **Resultado:** el protocolo actual **sobreestima el desempeño**, porque los hiperparámetros se eligen viendo los pliegues que luego actúan como prueba. Árbol de decisión 0,757 → 0,745 (+0,011); Random Forest 0,800 → 0,792 (+0,008); **XGBoost 0,826 → 0,780 (+0,046)**. **El sesgo no es uniforme entre algoritmos:** XGBoost se beneficia cinco veces más que Random Forest, de modo que **el orden se invierte** — con el método actual gana XGBoost (0,826 vs 0,800); con validación anidada gana Random Forest (0,792 vs 0,780). El protocolo, y no los datos, estaría decidiendo el ganador.
- **Decisión:** la validación anidada es **obligatoria** en I-3 y en toda comparación posterior de algoritmos (pasar el objeto `GridSearchCV` como estimador a `cross_val_predict`). Las métricas previas obtenidas con el protocolo no anidado quedan marcadas como optimistas y no son comparables con las nuevas. Se creó `src/comparacion_estadistica.py` con validación repetida y prueba pareada corregida de Nadeau-Bengio, ya que un t-test o Wilcoxon ordinario sobre repeticiones de CV es anticonservador (verificado: p=0,112 sin corregir vs. p=0,578 corregido sobre el mismo contraste).
- **Destino en el informe:** metodología (protocolo de validación y selección de modelo) y discusión (por qué las comparativas de la literatura con n pequeño suelen ser optimistas).

### RC-022 · 2026-09-03 · Fases 4–6 · **I-4** · Retiro de los modelos de reprobación por asignatura
- **Motivación:** ejecutar la decisión de RC-013 — los cinco modelos de reprobación por asignatura no son publicables ni defendibles por fuga temporal (70–83 % de `prom_global` proviene de semestres posteriores a la asignatura predicha) — sin destruir el registro histórico del proyecto.
- **Método:** retiro por **deprecación explícita**, no por borrado, para conservar la trazabilidad. (1) `src/entrenar_materias.py`: cabecera con el diagnóstico completo y `raise SystemExit` que impide su ejecución. (2) `construir_features_materias()` en `src/preprocessing.py`: docstring de retiro; se conserva porque `pipeline_completo()` la usa para reportar qué asignaturas superan el mínimo de casos, dato descriptivo aún válido. (3) `app.py`: eliminado el bloque «Modelos de predicción de reprobación por materia» (tarjetas con AUC por asignatura) y las cargas de `modelos_materias.pkl` y `metricas_materias.csv`; ajustadas las firmas de `cargar_modelos()` y `cargar_metricas()`. (4) Aviso destacado al inicio de los seis documentos que citan las métricas invalidadas. (5) `README.md`: pipeline, tabla de decisiones y métricas actualizados.
- **Resultado:** la sección «Materias Críticas» de la aplicación conserva el ranking, la descomposición por componente y ahora cierra con una **nota metodológica explícita** de que el índice es un indicador descriptivo, no un modelo predictivo — corrige la confusión que motivó la consulta original del estudiante. Verificado: la app carga sin errores, `entrenar_materias.py` aborta con mensaje explicativo, y `pipeline_completo()` sigue produciendo `df_master_limpio.csv` (90 × 37) con el target del art. 19 intacto (19/80). Documentos con aviso: `BORRADOR_INFORME.md`, `Fase 2/04_hallazgos_eda.md`, `Fase 4/02_informe_modelado.md`, `Fase 4/04_metricas_evaluacion.md`, `Fase 5/01_informe_evaluacion.md`, `Fase 5/03_impacto_recodificacion_antes_despues.md`.
- **Decisión:** los modelos por asignatura salen del alcance del proyecto. **Se conserva el índice de criticidad** (`src/indice_materias.py`, `src/materias_criticas.csv`), no afectado por ser descriptivo. Los artefactos binarios se **apartaron sin eliminarse** a `archivo/modelos_reprobacion_retirados/` (con `LEEME.md` que documenta el motivo y las cifras honestas), por decisión del estudiante: se conservan como evidencia del hallazgo, fuera del pipeline activo. Una reconstrucción honesta —limitada a asignaturas de segundo semestre con información del primero, AUC esperado 0,70–0,74— queda como trabajo opcional; no es entregable comprometido.
- **Destino en el informe:** metodología (validez temporal como criterio de diseño), resultados negativos y discusión. El hallazgo se reporta como contribución metodológica: una fuga detectada y corregida por el propio autor es evidencia de rigor, no una debilidad.

### RC-023 · 2026-09-03 · Fase 4 · **I-3** · Re-entrenamiento y comparación de algoritmos bajo validación anidada
- **Motivación:** re-entrenar y contrastar de forma rigurosa los cinco algoritmos de la propuesta (Regresión Logística L2, Árbol de Decisión, Random Forest, SVM-RBF y XGBoost) sobre el target institucional derivado del Art. 19 del reglamento vigente (`bajo_rendimiento_art19`, n=80 expuestos, 19 positivos, 23,8 %), eliminando el sesgo de optimización no anidada (RC-021) y adoptando AUC-PR como métrica principal frente a clases desbalanceadas.
- **Método:** ejecución del protocolo pre-registrado en `ESPEC_I3.md` mediante `src/entrenar_principal.py`:
  1. Población con actividad académica (`tiene_actividad_academica == 1`, n=80). Sin split retenido minúsculo (el 20 % tendría apenas 4 positivos, ruido puro).
  2. 19 features (incluyendo el indicador `sin_primer_semestre` de I-2).
  3. 15 repeticiones de validación cruzada CV-5 estratificada anidada, con búsqueda interna `GridSearchCV` 4-fold optimizando `'average_precision'` dentro de cada pliegue de entrenamiento.
  4. Comparación pareada con prueba $t$ corregida por el factor de solapamiento de Nadeau-Bengio (2003) (`src/comparacion_estadistica.py`).
  5. Umbral de relevancia práctica pre-registrado: $\Delta\text{AUC-PR} \ge 0,03$. Por debajo se declara empate técnico y se aplica parsimonia (Logística $\to$ Árbol $\to$ RF $\to$ XGBoost $\to$ SVM).
  6. Re-evaluación paralela idéntica sobre el target `graduado` (35 positivos de 80, 43,8 %).
- **Resultado:**
  1. **Bajo rendimiento Art. 19 (Métrica principal: AUC-PR):**
     * SVM (RBF): **0,573 ± 0,026** [IC 95 %: 0,530–0,603] | AUC-ROC: 0,757 ± 0,017
     * Random Forest: **0,569 ± 0,022** [IC 95 %: 0,536–0,602] | AUC-ROC: **0,793 ± 0,016**
     * Regresión Logística (L2): **0,548 ± 0,020** [IC 95 %: 0,518–0,575] | AUC-ROC: 0,771 ± 0,013
     * XGBoost: **0,528 ± 0,026** [IC 95 %: 0,489–0,566] | AUC-ROC: 0,767 ± 0,017
     * Árbol de Decisión: **0,463 ± 0,027** [IC 95 %: 0,426–0,505] | AUC-ROC: 0,730 ± 0,025
  2. **Contraste de hipótesis y veredicto:**
     * SVM (RBF) vs. Random Forest: $\Delta = +0,004$, $t = 0,351$, $p = 0,730 \implies$ **EMPATE** (sin diferencia).
     * SVM (RBF) vs. Regresión Logística: $\Delta = +0,025$, $t = 2,321$, $p = 0,036 \implies$ **EMPATE TÉCNICO** (estadísticamente significativo pero irrelevante, $|\Delta| < 0,03$).
     * Random Forest vs. Regresión Logística: $\Delta = +0,021$, $t = 2,104$, $p = 0,054 \implies$ **EMPATE** (sin evidencia estadística y $|\Delta| < 0,03$).
     * Random Forest vs. XGBoost: $\Delta = +0,041$, $t = 3,842$, $p = 0,0016 \implies$ Random Forest supera de forma significativa y relevante a XGBoost.
     * Conclusión de ganador: **Empate técnico a tres bandas** (SVM ≈ RF ≈ LogReg) en la métrica principal AUC-PR.

  3. **⚠️ DESVIACIÓN DECLARADA DE LA REGLA PRE-REGISTRADA.** `ESPEC_I3.md` §2.5 establece que ante empate técnico se elige el modelo **más simple e interpretable** según el orden Logística → Árbol → RF → XGBoost → SVM. **Aplicando ese criterio, el ganador sería la Regresión Logística (L2).** La matriz de comparaciones lo indica explícitamente en los tres contrastes del empate ("Elegir el modelo más simple").
     * **Se adopta Random Forest en su lugar**, apartándose del criterio. Razones: (i) lidera AUC-ROC de forma consistente (0,793 ± 0,016 frente a 0,771 ± 0,013 de la logística) con la menor dispersión del conjunto; (ii) domina las métricas operativas al umbral elegido — Recall+ 0,789 vs. 0,737, MCC 0,505 vs. 0,463, F1-macro 0,732 vs. 0,709 —, y en alertas tempranas el costo del falso negativo es el criterio rector; (iii) no requiere supuestos de linealidad ni de ausencia de colinealidad, condición no verificada en este conjunto (ver RC-024: `nivel_edu_max_padres` e `icfes_total` son funciones deterministas de otras variables incluidas).
     * **Se reconoce que el criterio original habría seleccionado la Regresión Logística** y que el desempate se resolvió con la métrica secundaria (AUC-ROC) y con métricas operativas, no con la métrica principal pre-registrada. La decisión es de la dirección del proyecto, no un resultado del protocolo.
     * **Mitigación:** la Regresión Logística se conserva como **línea base declarada y modelo interpretable de contraste**; ambos se reportan en el informe con sus intervalos. La desviación queda documentada aquí para que el lector pueda evaluarla de forma independiente.
  3. **Optimización de umbral para alertas tempranas:**
     * En bajo rendimiento, el costo del falso negativo (no detectar a un estudiante que terminará expulsado o perdiendo condición) supera al de la falsa alarma.
     * Con umbral $u = 0,22$, Random Forest alcanza: **Recall+ = 0,789** (detecta 8 de cada 10 casos en riesgo), Precisión+ = 0,536, F1+ = 0,638, F1-macro = 0,732, MCC = 0,505, Exactitud = 0,788.
  4. **Target Graduado:**
     * SVM (0,812) y Random Forest (0,809) empatan técnicamente; Random Forest y SVM lideran en AUC-ROC con 0,836. A umbral $u=0,40$, Random Forest alcanza Recall+ = 0,829, Precisión+ = 0,763, F1+ = 0,795 y Exactitud = 0,800.
  5. **Top Features (Random Forest, Art. 19):** `prom_sem1` (22,8 %), `icfes_total` (12,6 %), `icfes_mat` (12,1 %), `nivel_edu_madre` (7,6 %), `sin_primer_semestre` (6,3 %). La dependencia exclusiva de `prom_sem1` se redujo del 40,4 % al 22,8 %, integrando con balance factores de entrada.
- **Decisión:** adoptar formalmente los resultados de la validación anidada. Generados y materializados en `src/`: `comparativa_bajo_rendimiento_art19.csv`, `comparativa_rendimiento_bajo.csv`, `comparativa_graduado.csv`, `tabla_comparativa_art19.csv`, `matriz_comparaciones_art19.csv`, `curva_umbrales_art19.csv` y modelos `.pkl` asociados.
- **Destino en el informe:** Fase 4 (Modelado: comparativa rigurosa de algoritmos con incertidumbre e intervalos de confianza; protocolo de anidación; análisis de umbrales en alertas tempranas).

### RC-024 · 2026-09-15 · Fase 3 · Selección de variables: carencia detectada y protocolo
- **Motivación:** el estudiante observa que cinco variables concentran el 61,4 % de la importancia MDI del Random Forest y pregunta cómo se evaluó el conjunto de features y si las 19 son necesarias.
- **Método:** auditoría del historial del proyecto y de `src/preprocessing.py`.
- **Resultado — respuesta honesta: no se hizo selección empírica de variables.** Las 19 features se fijaron por criterio de **disponibilidad temporal** (solo lo observable al ingreso o al cierre del primer periodo, para evitar fuga) y se heredaron sin verificación de aporte. El paquete `WP-OE1.2` del plan operativo especifica exactamente esta verificación y **figura como LIBRE en el Kanban: nunca se ejecutó**. Se confirman además **dos redundancias estructurales** por inspección del código: `nivel_edu_max_padres = max(nivel_edu_padre, nivel_edu_madre)` es una función determinista de otras dos variables incluidas; e `icfes_total = icfes_mat + icfes_ing + icfes_lec + icfes_soc + icfes_nat`, de cuyas cinco componentes **tres están además incluidas por separado** (`icfes_mat`, `icfes_lec`, `icfes_nat`). Ambas fueron señaladas como sospechosas en el plan operativo y nunca contrastadas. Se reitera que la importancia MDI **no mide aporte predictivo** (RC-019: dos columnas de ruido puro capturaron el 14,3 %, una por encima de 13 variables reales), por lo que el 61,4 % citado no autoriza conclusiones sobre qué variables son necesarias.
- **Decisión:** se implementa `src/seleccion_variables.py` con el protocolo de WP-OE1.2: importancia **por permutación** sobre datos no vistos (caída de AUC-PR al barajar), VIF de cada variable contra el resto, y **ablation de siete subconjuntos definidos a priori** (S1 solo ingreso, S2 set completo, S3 solo académicas, S4 solo socioeconómicas, S5 sin las dos redundancias estructurales, S6 top-5 por permutación, S7 solo `prom_sem1`), evaluados con RF y regresión logística bajo el mismo protocolo de I-3 y comparados con Nadeau-Bengio. **Regla pre-registrada:** un subconjunto reducido sustituye al completo solo si no pierde más de 0,03 de AUC-PR.
- **Destino en el informe:** Fase 3 (selección de variables) y limitaciones. La ausencia previa de esta verificación se reporta como tal.

### RC-025 · 2026-09-15 · Fase 4 · Presupuesto de ajuste desigual entre algoritmos
- **Motivación:** el estudiante pregunta si se consideraron estrategias contra el sobreajuste en XGBoost. La revisión de `get_modelos()` revela un problema mayor de validez interna.
- **Método:** conteo de las combinaciones de la rejilla de cada algoritmo en `src/entrenar_principal.py`.
- **Resultado:** **la comparación de I-3 no fue justa.** Presupuestos de búsqueda: Random Forest **48** combinaciones, Árbol de Decisión 24, SVM 12, Regresión Logística 5 y **XGBoost solo 8** (`n_estimators`×`max_depth`×`learning_rate`). Además, la rejilla de XGBoost **no incluía ningún hiperparámetro de regularización**: sin `min_child_weight`, `subsample`, `colsample_bytree`, `reg_alpha` ni `reg_lambda`, quedaba con el valor por defecto `reg_lambda=1` como único control. Con 64 casos de entrenamiento por pliegue y ~15 positivos, XGBoost sin `min_child_weight` ni `subsample` es especialmente propenso a memorizar. Su último lugar entre los modelos no triviales (AUC-PR 0,528) es **en parte un artefacto del diseño experimental**, no necesariamente una propiedad del algoritmo.
- **Decisión:** rejilla de XGBoost corregida a 64 combinaciones incorporando `min_child_weight`, `subsample` y `reg_lambda`, con `PRESUPUESTO_REJILLA` documentado en el código para que la equidad de la comparación sea auditable. **La comparación de I-3 debe repetirse con las rejillas equilibradas**; hasta entonces, la posición de XGBoost se reporta con esta salvedad explícita.
- **Destino en el informe:** metodología (equidad del protocolo de comparación) y limitaciones. Es un sesgo de diseño poco discutido en la literatura de comparación de algoritmos.

### RC-026 · 2026-09-15 · Fase 4 · Estimación del error de generalización más allá de la CV
- **Motivación:** el estudiante pregunta si la validación cruzada basta para estimar el error de generalización y si las medidas de impureza son adecuadas.
- **Método:** revisión del diseño de evaluación vigente e implementación de `src/diagnostico_error.py`.
- **Resultado:** el proyecto estima el error **únicamente por validación cruzada**, sin conjunto externo (decisión justificada: con n=80 un holdout del 20 % tendría 4 positivos) y sin un segundo estimador independiente. La CV informa el error de generalización pero **no cuantifica el sobreajuste**: no separa cuánta capacidad se pierde por memorización. Sobre las medidas de impureza: el índice de Gini es **adecuado para decidir las particiones** de un árbol, pero **inadecuado como medida de importancia** (sesgo hacia variables con muchos valores distintos, RC-019); son dos usos distintos que suelen confundirse.
- **Decisión:** se complementa la CV con cuatro diagnósticos: (1) **brecha train–validación** por algoritmo, medida directa del sobreajuste; (2) **curva de aprendizaje**, que distingue si el límite es la varianza o la información disponible —y si la validación sigue subiendo al 100 % de la muestra, constituye el argumento empírico para extender el estudio a la FCBI completa (n≈275, paso I-5)—; (3) **bootstrap .632+** de Efron-Tibshirani como estimador independiente de la partición en pliegues, para verificar la robustez de la estimación por CV; (4) **curva de validación** sobre `min_child_weight` y `reg_lambda` de XGBoost, para cuantificar cuánto de su bajo desempeño se debía a la rejilla empobrecida (RC-025). La importancia por permutación sustituye a MDI en todo reporte de variables.
- **Destino en el informe:** metodología (estrategia de estimación del error), resultados (diagnóstico de sobreajuste) y justificación de la extensión a los tres programas.

### RC-027 · 2026-09-15 · Infraestructura · Instrumentación de bitácora reproducible
- **Motivación:** I-3 persistió solo métricas agregadas, de modo que no era posible reconstruir las pruebas pareadas, los intervalos de confianza ni auditar qué hiperparámetros eligió la búsqueda interna en cada pliegue. El estudiante planea repetir la corrida para dejar constancia.
- **Método:** análisis de determinismo del script y desarrollo de `src/instrumentacion.py`.
- **Resultado:** `src/entrenar_principal.py` es **determinista** — `SEED=42`, `random_state` fijo en los cinco estimadores, `outer` con `SEED+r`, `inner` con `SEED+100+r` y `n_jobs=1` en los `GridSearchCV` —, por lo que una repetición con los mismos datos y las mismas versiones de librerías reproduce las cifras de forma idéntica. **Repetir la corrida sin instrumentar no añadiría evidencia.** Advertencia: los artefactos `.pkl` se generaron con scikit-learn 1.8.0; ejecutar con otra versión sí puede alterar los resultados, por lo que la versión debe fijarse en `requirements.txt`.
- **Decisión:** la clase `Bitacora` registra contexto de ejecución (versiones de librerías, hash SHA-256 del CSV de entrada, semilla, timestamp, duración), **métricas por repetición** de cada modelo, **hiperparámetros seleccionados en cada pliegue externo** y un resumen de **estabilidad de hiperparámetros** (configuraciones distintas y frecuencia de la moda). La función `comparar_corridas()` verifica que dos ejecuciones sean idénticas. Con esto, la repetición deja de ser duplicación y se convierte en **prueba formal de reproducibilidad**, afirmación que el informe solo puede sostener si se ejecuta dos veces.
- **Destino en el informe:** metodología (reproducibilidad) y anexo. La variabilidad de hiperparámetros entre pliegues es además un resultado reportable: documenta la incertidumbre real de la selección con 19 positivos.

### RC-028 · 2026-09-15 · Fase 3 · **WP-OE1.2** · Resultados de la selección empírica de variables
- **Motivación:** ejecutar el protocolo diseñado en RC-024 (`src/seleccion_variables.py`) para responder si las 19 features del modelo I-3 son necesarias.
- **Método:** importancia por permutación (5 rondas de CV-5, 30 barajados por variable), VIF contra el resto, y ablación de 7 subconjuntos definidos a priori con RF y Regresión Logística bajo CV-5 × 15 repeticiones y prueba de Nadeau-Bengio.
- **Resultado:**
  1. **Importancia por permutación:** `prom_sem1` (caída de AUC-PR media 0,303; positiva en el 92 % de los pliegues) es el predictor dominante con diferencia. Le siguen `icfes_total` (0,043, 80 %) e `icfes_mat` (0,026, 68 %). Solo **10 de 19 variables** tienen aporte neto positivo. Nueve variables —incluyendo `icfes_nat` (−0,012), `nivel_edu_madre` (−0,007), `icfes_lec` (−0,004) y `sin_primer_semestre` (−0,001)— **quitan capacidad predictiva** al modelo cuando se incluyen. La comparación con MDI confirma el sesgo de esa métrica: `nivel_edu_madre` aparecía con 7,6 % de importancia MDI pero tiene aporte por permutación de −0,007.
  2. **VIF:** las dos redundancias estructurales se confirman con los valores más altos del conjunto: `icfes_total` VIF=9,00 y `nivel_edu_max_padres` VIF=7,65. `nivel_edu_madre` (VIF=5,88) presenta colinealidad moderada con el padre y el máximo. El resto tiene VIF ≤ 3,11.
  3. **Ablación (Random Forest):**

     | Subconjunto | RF AUC-PR | Veredicto vs. set completo |
     |---|:---:|---|
     | **S6 · top-5 permutación (5 vars)** | **0,826 ± 0,012** | **Mejor** (Δ=+0,085, p=0,002) |
     | S3 · solo académicas (6 vars) | 0,746 ± 0,019 | Empate (p=0,782) |
     | S2 · set completo (19 vars) | 0,741 ± 0,040 | — (referencia) |
     | S5 · sin redundancias estructurales (17 vars) | 0,726 ± 0,021 | Empate (p=0,532) |
     | S7 · solo `prom_sem1` (1 var) | 0,611 ± 0,019 | Peor |
     | S1 · sin primer semestre, 17 vars | 0,442 ± 0,041 | Peor |
     | S4 · solo socioeconómicas (11 vars) | 0,344 ± 0,034 | Peor |

  4. **El subconjunto S6 de 5 variables supera al set completo** en Δ=+0,085 de AUC-PR, diferencia significativa y relevante (p=0,002 > umbral de relevancia de 0,03). Las variables: `prom_sem1`, `icfes_total`, `icfes_mat`, `sisben_nivel`, `cohorte_encoded`. **Las 14 variables adicionales degradan el modelo** al introducir ruido que el Random Forest no puede filtrar con solo 64 casos de entrenamiento por pliegue.
  5. **Nota de alcance:** la ablación usa RF con hiperparámetros fijos (no validación anidada), por lo que los valores absolutos no son comparables con I-3. La **dirección del efecto es robusta**: S6 supera al set completo con el mismo protocolo de evaluación.
- **Decisión:** S6 es el conjunto candidato para el re-entrenamiento definitivo (I-3 bis). Antes de adoptarlo formalmente se debe verificar que la rejilla de XGBoost sea equilibrada (RC-025, pendiente) y ejecutar el diagnóstico de error (RC-026/RC-029). Salidas: `src/permutacion_importancia.csv`, `src/redundancia_vif.csv`, `src/ablation_subconjuntos.csv`, `src/ablation_comparaciones.csv`.
- **Destino en el informe:** Fase 3 (selección de variables) y Fase 4 (discusión: el efecto de la dimensionalidad con n pequeño).

### RC-029 · 2026-09-15 · Fase 4 · Resultados del diagnóstico de error de generalización
- **Motivación:** ejecutar `src/diagnostico_error.py` para caracterizar el sobreajuste y validar la estimación de I-3.
- **Método:** brecha train-validación (15 reps CV-5), curva de aprendizaje (RF, 5 fracciones, 20 reps), bootstrap .632+ (B=200) y curva de validación de la regularización de XGBoost.
- **Resultado:**
  1. **Brecha train–validación:** todos los modelos memorizan los datos de entrenamiento (AUC-PR train: RF 1,000; XGBoost-viejo 1,000; SVM 0,965; LogReg 0,913; Árbol 0,836). La brecha media es grande en todos los casos (RF 0,228; LogReg 0,284; XGBoost-viejo 0,309; SVM 0,374). La **lectura correcta** es que el límite no es el algoritmo sino la cantidad de información disponible: con 64 casos de entrenamiento y 15 positivos, cualquier modelo con suficiente capacidad memorizará. Hay **señal real** (la validación supera ampliamente la línea base del 0,238) pero la varianza de la estimación es alta (DE ≈ 0,17 en todos los modelos).
  2. **Curva de aprendizaje (RF):** la validación sube de forma **monotónica y sin meseta** al aumentar el tamaño del subconjunto de entrenamiento (0,557 → 0,636 → 0,688 → 0,751 → 0,768), mientras el train es constante 1,0 en todas las fracciones. **Conclusión:** el modelo está limitado por varianza (datos insuficientes), no por sesgo. Más datos mejorarían el desempeño — argumento empírico para extender el estudio a la FCBI completa (n≈275, paso I-5).
  3. **Bootstrap .632+:** LogReg 0,604; RF 0,777; XGBoost regularizado 0,424. La estimación de RF (0,777) es más alta que la CV anidada de I-3 (0,569 AUC-PR), diferencia razonable dada la naturaleza del bootstrap con n pequeño (los conjuntos OOB son más pequeños que los pliegues de validación). La dirección es consistente: RF > LogReg >> XGBoost con regularización fuerte.
  4. **Curva de validación de XGBoost:** resultado contraintuitivo pero explicable. `min_child_weight=1, reg_lambda=1,0` (la configuración menos regularizada) alcanza AUC-PR=0,710 en validación. Al aumentar `min_child_weight` a 3 o 5, el desempeño colapsa a 0,397–0,326. **La causa:** con 15 positivos en entrenamiento, `min_child_weight=3` exige al menos 3 instancias por hoja, lo que impide la mayoría de los cortes sobre la clase minoritaria. **La regularización agresiva es contraproducente en muestras pequeñas con clase rara.** La comparación de I-3 fue injusta por el número de combinaciones (8 vs. 48 de RF), pero la dirección del efecto de agregar regularización es **opuesta a lo esperado**: XGBoost sin regularización explícita (rejilla vieja) obtuvo 0,691 en validación con la brecha calculada aquí, muy por encima del 0,397 de la versión regularizada. La rejilla corregida debe explorar `min_child_weight=1` con variación de `reg_lambda` en rango bajo (0,5–2,0).
- **Decisión:** los resultados del diagnóstico confirman que I-3 bis debe ejecutarse con S6 (5 variables) para reducir la dimensionalidad efectiva y la varianza de estimación, y con la rejilla de XGBoost corregida solo en combinaciones (no en `min_child_weight > 1`). La curva de aprendizaje motiva formalmente la extensión a FCBI. Salidas: `src/brecha_train_val.csv`, `src/curva_aprendizaje.csv`, `src/bootstrap_632.csv`, `src/curva_validacion_xgb.csv`.
- **Destino en el informe:** Fase 4 (diagnóstico de sobreajuste), Fase 5 (evaluación del error) y justificación de la ampliación de la muestra.

### RC-030 · 2026-09-15 · Fase 3 · **CORRIGE RC-028** · Sesgo de selección en el subconjunto S6
- **Motivación:** revisión crítica de RC-028. El resultado "S6 de 5 variables supera al set completo (Δ=+0,085, p=0,002)" es **el único subconjunto que gana**, mientras que los definidos a priori (S3, S5) empatan. Ese patrón es diagnóstico de sesgo de selección y obliga a auditar cómo se construyó S6.
- **Método:** inspección del flujo de `src/seleccion_variables.py`.
- **Resultado:** **S6 está contaminado por fuga de selección de variables.** El flujo es:
  ```
  imp = importancia_permutacion(X, y)        # recorre TODA la muestra (n=80)
  S6  = imp.index[:5]                        # top-5 elegidos viendo todos los datos
  ablation(X, y, {... 'S6': S6 ...})         # se evalúa por CV sobre LA MISMA muestra
  ```
  Aunque la importancia se calcula sobre pliegues de validación, el **ranking agregado abarca a los 80 estudiantes** y luego se congela y reutiliza. Cuando la ablación evalúa S6 por validación cruzada, los pliegues de prueba **ya habían participado en elegir esas cinco variables**. Es exactamente la misma clase de error documentada en RC-021 para los hiperparámetros —selección hecha fuera del pliegue de entrenamiento— reproducida aquí para las features. El fenómeno está descrito en Ambroise & McLachlan (2002, PNAS) para selección de variables con n pequeño, donde produce sobreestimaciones severas.
  - **Evidencia interna del sesgo:** los subconjuntos **definidos a priori empatan** con el set completo (S3 p=0,782; S5 p=0,532) y solo gana el **elegido con los datos**. Si la reducción de dimensionalidad fuera el mecanismo real, S3 —con 6 variables— debería mostrar una ventaja comparable, y no la muestra.
  - **Alcance del error:** la magnitud Δ=+0,085 **no es interpretable** y el p=0,002 tampoco, porque la hipótesis se formuló después de ver los datos. El sentido del efecto (reducir dimensión ayuda con n=80) sigue siendo plausible, pero **no está demostrado por este experimento**.
- **Decisión:**
  1. **Se retira S6 como conjunto candidato para I-3 bis.** Queda revocada esa parte de la decisión de RC-028 y RC-029.
  2. **Conclusiones que SÍ se sostienen** (subconjuntos a priori, sin contaminación): (a) **S3 · solo académicas (6 variables) iguala al set completo de 19** (0,746 vs. 0,741; p=0,782) — resultado limpio y el más útil del experimento; (b) **S5 confirma que las dos redundancias estructurales no aportan** (p=0,532), consistente con VIF 9,00 y 7,65; (c) **S4 · solo socioeconómicas es muy inferior** (0,344 frente a 0,741) — resultado negativo robusto que refuerza RC-007; (d) la importancia por permutación como **diagnóstico descriptivo** es válida: contrasta legítimamente con MDI (`nivel_edu_madre` 7,6 % en MDI vs. −0,007 por permutación).
  3. **Si se quiere un conjunto reducido óptimo**, la selección debe ejecutarse **dentro de cada pliegue de entrenamiento** (selección anidada): se implementa `seleccion_anidada()` en `src/seleccion_variables.py`. Se pre-registra que el conjunto reducido sustituye a S3 solo si lo supera por ΔAUC-PR ≥ 0,03 bajo ese protocolo.
  4. **Candidato provisional para I-3 bis: S3** (`icfes_total`, `icfes_mat`, `icfes_lec`, `icfes_nat`, `prom_sem1`, `sin_primer_semestre`), por ser el conjunto más pequeño definido a priori que iguala al completo.
- **Destino en el informe:** Fase 3 (selección de variables) y discusión metodológica. **Es un hallazgo reportable de pleno derecho:** el proyecto detectó la misma clase de fuga en tres niveles distintos —temporal en las features (RC-013), de hiperparámetros (RC-021) y de selección de variables (RC-030)—, lo que documenta que la fuga de información no es un evento puntual sino un riesgo sistemático en estudios con muestras pequeñas.

### RC-031 · 2026-09-15 · Fase 4 · Precisiones sobre el diagnóstico de error (matiza RC-029)
- **Motivación:** revisión de las inferencias de RC-029 antes de que alimenten el informe.
- **Método:** contraste de lo medido contra lo afirmado en `src/diagnostico_error.py`.
- **Resultado:**
  1. **La comparación bootstrap .632+ vs. CV anidada no es válida como está.** RC-029 contrasta RF .632+ = 0,777 con el 0,569 de I-3 y atribuye la diferencia al tamaño de los conjuntos OOB. La causa principal es otra: el **.632+ se calculó con hiperparámetros FIJOS** (`n_estimators=200, max_depth=4`), mientras que I-3 usó búsqueda anidada. Son estimadores de cosas distintas; el 0,777 es comparable con el 0,741 de la ablación (también con hiperparámetros fijos), y esa cercanía **sí** respalda la robustez. Reformulado así, el diagnóstico es valioso.
  2. **La adaptación del .632+ a AUC-PR no es estándar.** El estimador de Efron-Tibshirani se derivó para tasas de error; su extensión a métricas de ranking con la prevalencia como tasa de no-información es una adaptación razonable pero **no canónica**, y debe declararse como tal en el informe.
  3. **La hipótesis de RC-025 no se confirmó y conviene decirlo:** se esperaba que la ausencia de regularización penalizara a XGBoost; la curva de validación muestra lo contrario — `min_child_weight=3` colapsa el desempeño (0,397 frente a 0,710 con valor 1). El razonamiento de RC-029 es correcto: con 15 positivos en entrenamiento, exigir 3 instancias por hoja bloquea los cortes sobre la clase minoritaria. **La desigualdad de presupuesto (8 vs. 48 combinaciones) sigue siendo un problema real de equidad**, pero el mecanismo propuesto para explicar el bajo desempeño de XGBoost era equivocado.
- **Decisión:** ajustar la rejilla de XGBoost a `min_child_weight=[1]` y `reg_lambda` en rango bajo (0,5–2,0), ampliando en cambio `n_estimators`, `max_depth`, `learning_rate`, `subsample` y `colsample_bytree` hasta alcanzar un presupuesto comparable al de Random Forest. Reformular en el informe la comparación .632+ frente a la ablación, no frente a I-3.
- **Destino en el informe:** metodología (estimación del error) y discusión (regularización en muestras pequeñas con clase rara: un resultado contraintuitivo y reportable).

### RC-032 · 2026-09-15 · Fase 3 · **Medición del sesgo de selección** (cierra RC-028 / RC-030)
- **Motivación:** cuantificar el sesgo diagnosticado en RC-030 y determinar el conjunto de variables definitivo con una estimación honesta.
- **Método:** selección **anidada** — en cada uno de los 40 pliegues de entrenamiento (8 repeticiones × CV-5) se calcula la importancia por permutación **solo con ese pliegue**, se eligen las 5 mejores y se evalúa sobre el pliegue de prueba, nunca visto. Random Forest (`n_estimators=120, max_depth=4`), SEED=42, AUC-PR, contraste de Nadeau-Bengio. Se comparan cuatro conjuntos bajo el mismo protocolo.
- **Resultado:**

  | Conjunto | Tipo | AUC-PR | sd |
  |---|---|:---:|:---:|
  | Set completo (19) | a priori | 0,7201 | ±0,0468 |
  | **S3 · solo académicas (6)** | **a priori** | **0,7196** | ±0,0462 |
  | top-5 **contaminado** (el S6 de RC-028) | selección no anidada | 0,8204 | ±0,0126 |
  | top-5 **anidado** (honesto) | selección anidada | **0,6705** | ±0,0713 |

  1. **El sesgo de selección es de +0,1499 de AUC-PR.** La cifra de 0,826 publicada en RC-028 cae a **0,6705** al seleccionar dentro de cada pliegue. Es casi cinco veces el umbral de relevancia pre-registrado (0,03) y mayor que la diferencia entre el mejor y el peor algoritmo de I-3.
  2. **La ventaja de S6 era íntegramente artefacto.** El top-5 honesto **no supera al set completo** (Δ=−0,0496; p=0,179, empate) y es **significativamente peor que S3** (Δ=−0,0491; p=0,044). La conclusión de RC-028 —"las 14 variables adicionales degradan el modelo"— queda **refutada**.
  3. **S3 iguala al set completo de forma casi exacta:** Δ=−0,0005; p=0,983. Seis variables definidas a priori rinden lo mismo que diecinueve, sin ninguna selección guiada por los datos. Es el resultado limpio del experimento.
  4. **La selección es inestable, y eso explica el fracaso del top-k.** Frecuencia con que cada variable entra en el top-5 a lo largo de los 40 pliegues: `prom_sem1` **100 %**, `icfes_total` 75 %, `icfes_mat` 60 %, `log_ingresos` 55 %, `nivel_edu_padre` 52 %, `sin_primer_semestre` 30 %, `icfes_nat` 28 %, `sisben_nivel` 25 %. Solo una variable se elige siempre; a partir de la tercera la selección es prácticamente aleatoria. Con 19 positivos, el ranking de importancia **más allá de las dos o tres primeras posiciones es ruido**, y seleccionar sobre ese ruido perjudica. S3, al ser un bloque conceptual coherente y fijo, no sufre esa inestabilidad.
- **Decisión:** **el conjunto definitivo para I-3 bis es S3** (`prom_sem1`, `sin_primer_semestre`, `icfes_total`, `icfes_mat`, `icfes_lec`, `icfes_nat`): iguala al completo con un tercio de las variables, es interpretable y no depende de ninguna selección guiada por los datos. Queda **prohibida en este proyecto la selección de variables fuera del pliegue de entrenamiento**. La regla de decisión se mantiene: ningún conjunto sustituye a S3 salvo que lo supere por ΔAUC-PR ≥ 0,03 bajo selección anidada. Salidas: `src/seleccion_anidada.csv`, `src/estabilidad_seleccion.csv`.
- **Destino en el informe:** Fase 3 (selección de variables, resultado principal) y discusión metodológica. La tabla de los cuatro conjuntos es **material publicable por sí misma**: documenta con cifras propias que la selección de variables no anidada infló el desempeño en 0,15 de AUC-PR, magnitud que habría llevado a adoptar un modelo peor creyendo que era mejor.

### RC-033 · 2026-09-15 · Fase 4 · **I-3 bis** · Comparación definitiva (target art. 19)
- **Motivación:** repetir la comparación de algoritmos con las cuatro correcciones acumuladas: conjunto S3 (RC-032), presupuesto de rejilla equilibrado (RC-025), XGBoost sin sobre-regularizar (RC-031) e instrumentación completa (RC-027).
- **Método:** `src/entrenar_i3bis.py`. Cinco algoritmos, 6 variables (S3), n=80 con 19 positivos, CV-5 × 10 repeticiones **anidadas** (GridSearchCV interno de 4 pliegues optimizando `average_precision`), rejillas de 16–24 combinaciones cada una, SEED=42. Contraste pareado con corrección de Nadeau-Bengio y umbral de relevancia ΔAUC-PR ≥ 0,03. Bitácoras completas en `bitacora/20260915_*`.
- **Resultado:** línea base AUC-PR (azar) = 0,2375.

  | Algoritmo | AUC-PR | sd | IC 95 % |
  |---|:---:|:---:|---|
  | **Random Forest** | **0,745** | ±0,025 | 0,703–0,783 |
  | SVM (RBF) | 0,714 | ±0,037 | 0,637–0,750 |
  | XGBoost | 0,630 | ±0,045 | 0,573–0,703 |
  | Árbol de Decisión | 0,614 | ±0,055 | 0,516–0,693 |
  | Regresión Logística (L2) | 0,550 | ±0,088 | 0,411–0,663 |

  1. **Random Forest es el ganador y esta vez la regla pre-registrada lo selecciona sola.** Supera de forma significativa y relevante al Árbol (Δ=+0,131; p=0,005), a la Logística (Δ=+0,196; p=0,005) y a XGBoost (Δ=+0,115; p=0,004). Frente a SVM la diferencia es de +0,032 con p=0,234: al no ser estadísticamente significativa se declara empate, y **el orden de parsimonia pre-registrado coloca a Random Forest antes que a SVM**. **No se requiere desviación del protocolo**, a diferencia de RC-023.
  2. **XGBoost se recupera de 0,528 a 0,630 (+0,102) solo por equilibrar la rejilla.** Confirma empíricamente RC-025: la comparación de I-3 era injusta y su último lugar era en parte un artefacto del diseño experimental. Pasa del quinto al tercer puesto. La magnitud del efecto —mayor que la distancia entre el primero y el segundo— demuestra que el presupuesto de ajuste desigual invalida una comparación de algoritmos.
  3. **La Regresión Logística cae al último lugar** (0,550). Con las 19 variables empataba con los ensambles; con solo 6, ya no. Es coherente con la naturaleza del target: el art. 19 es una **conjunción** (100 % de créditos reprobados **y** promedio < 3,0) que un modelo lineal no representa bien.
  4. **El ordenamiento cambió por completo respecto a I-3** (SVM ≈ RF ≈ LogReg → RF > SVM > XGB ≈ Árbol ≈ LogReg) y **el desempeño global subió** (mejor modelo 0,569 → 0,745, +0,176), pese a usar un tercio de las variables. La mejora proviene de la calidad del diseño experimental, no del algoritmo.
  5. **Estabilidad:** Random Forest tiene la menor dispersión del conjunto (sd 0,025) y el intervalo de confianza más estrecho; la Logística, la mayor (sd 0,088).
  6. **Umbral operativo — revisar el criterio.** La curva muestra un comportamiento distinto al del modelo anterior: los umbrales altos dominan. En 0,54 se obtiene Precisión+ 0,923 · Recall+ 0,632 · F1-macro 0,844 · MCC 0,710 · Exactitud 0,900; bajar a 0,20 solo sube el Recall+ a 0,684 y desploma la precisión a 0,464. **El intercambio ya no favorece al umbral bajo**, a diferencia del 0,29 de RC-005: el modelo está mejor calibrado y un umbral alto entrega buena precisión sin sacrificar apenas exhaustividad. La decisión final debe tomarse con el criterio institucional explícito (costo del falso negativo en el Programa de Retención, art. 23).
- **Decisión:** **Random Forest sobre el conjunto S3 es el modelo principal** para el target del art. 19. Se adopta por aplicación directa de la regla pre-registrada. La comparación de I-3 (RC-023) queda **superada** por esta. Pendiente: ejecutar el mismo protocolo sobre el target `graduado` (n=90) y fijar el umbral con el criterio institucional. Salidas: `src/i3bis_tabla_art19.csv`, `src/i3bis_comparaciones_art19.csv`, `src/i3bis_curva_umbrales.csv`, bitácoras con métricas por repetición e hiperparámetros por pliegue.
- **Destino en el informe:** Fase 4 (resultado principal de la comparación de algoritmos) y discusión. El punto 2 es **material publicable**: cuantifica cuánto puede alterar el ranking de una comparación el presupuesto de ajuste desigual, sesgo poco discutido en la literatura.

### RC-034 · 2026-09-15 · Fase 4 · **Corrige el umbral operativo de RC-033**
- **Motivación:** el estudiante advierte que el Recall+ cayó de 0,789 (I-3) a 0,632 (I-3 bis) pese a que el AUC-PR subió de 0,569 a 0,745, y cuestiona si eso compromete el criterio de priorizar la exhaustividad (RC-005).
- **Método:** recálculo de la curva de umbral con probabilidades **promediadas sobre las 10 repeticiones** y barrido desde 0,02; comparación de precisión alcanzable a recall fijo entre el modelo de 19 variables y el de S3.
- **Resultado — la observación era correcta y detectó dos defectos del script:**
  1. **El recall no cayó; se eligió mal el umbral.** El modelo S3 alcanza **Recall+ 0,789 en umbral 0,14**, exactamente el valor de I-3. La rutina de selección tomaba el umbral que **maximiza F1-macro**, métrica que premia el equilibrio entre clases y empuja a umbrales altos — criterio **opuesto** al declarado en RC-005, donde se estableció que el falso negativo es el error caro.
  2. **La curva se calculaba con una sola repetición** (`if r == 0`) y desde 0,10, lo que producía un techo aparente de Recall+ 0,684 inexistente. Con probabilidades promediadas y umbrales bajos, el modelo alcanza **Recall+ 1,000 en umbral 0,06**.
  3. **Curva operativa del modelo definitivo (RF sobre S3):**

     | Umbral | Recall+ | Prec+ | Alertas (de 80) |
     |:---:|:---:|:---:|:---:|
     | 0,06 | 1,000 | 0,288 | 66 |
     | 0,10 | 0,842 | 0,291 | 55 |
     | **0,14** | **0,789** | 0,326 | **46** |
     | 0,18 | 0,737 | 0,389 | 36 |
     | 0,22 | 0,632 | 0,462 | 26 |
     | 0,54 | 0,632 | 0,857 | 14 |

  4. **A recall igualado, el conjunto de 19 variables mantiene algo más de precisión** que S3 (a Recall+ 0,79: 0,400 vs. 0,340; a 0,68: 0,542 vs. 0,448), aunque el AUC-PR global es equivalente (0,756 vs. 0,752). El dato matiza —sin invalidar— la decisión de RC-032: S3 iguala en capacidad de ordenamiento global, pero en la zona de alto recall el conjunto completo es levemente superior.
  5. **Limitación operativa cuantificada:** capturar el 79 % de los casos exige alertar sobre **46 de 80 estudiantes (57 % de la cohorte)**; el 90 %, sobre 55. Con 19 positivos entre 80, la precisión en la zona de alto recall es intrínsecamente baja (0,29–0,34).
- **Decisión:** (a) `curva_umbral()` barre desde 0,02, usa probabilidades promediadas y reporta `n_alertas` y `pct_cohorte`; (b) se añade `recomendar_umbral()`, que aplica el criterio de RC-005 —recall mínimo 0,75 y, entre los que lo cumplen, máxima precisión— en lugar de F1-macro; (c) el umbral definitivo **no se fija por métrica sino con la capacidad real de atención del Programa de Retención** (art. 23): es una decisión institucional que debe consultarse y documentarse; (d) al fijarlo, evaluar si conviene volver al conjunto de 19 variables por su ventaja en la zona de alto recall.
- **Destino en el informe:** Fase 5 (evaluación y decisión de umbral) y discusión. El punto 5 es relevante para la sección de utilidad práctica: un modelo con AUC-PR 0,745 sobre una clase del 24 % **no puede** dar alta precisión y alta exhaustividad a la vez, y presentarlo de otro modo sería engañoso.

### RC-035 · 2026-09-15 · Fase 5–6 · Esquema de alerta por niveles y validez temporal del target
- **Motivación:** la curva precisión-recall muestra una **zona de precisión perfecta** que un umbral único desaprovecha; y antes de ampliar el conjunto de variables hay que verificar si el target sufre el mismo problema de simultaneidad ya detectado en RC-013.
- **Método:** análisis de la curva PR con probabilidades promediadas (10 repeticiones); fechado del primer evento del art. 19 respecto al periodo de ingreso; re-evaluación excluyendo los casos simultáneos.
- **Resultado:**
  1. **Existe un grupo de riesgo cierto.** El modelo alcanza **precisión 1,000 hasta recall 0,579**: identifica **11 de los 19 casos sin una sola falsa alarma** (umbral 0,62). La curva cae bruscamente después. Un umbral único descarta esa información: o se pierde la certeza, o se pierde la cobertura.
  2. **Tres puntos de operación medidos:** umbral 0,62 → 11 alertas, precisión 1,000, detecta el 58 %; umbral 0,12 → 52 alertas, precisión 0,308, detecta el 84 %; umbral 0,06 → 66 alertas, precisión 0,288, detecta el 100 %.
  3. **⚠ El 42 % de los casos positivos activa el art. 19 en el PRIMER semestre** (8 de 19). Para ellos `prom_sem1` es **contemporáneo** al evento, no anterior: el modelo los *detecta*, no los *predice*.
  4. **Separando ambas poblaciones:**

     | Escenario | n | Positivos | AUC-PR | Línea base | Lift |
     |---|:---:|:---:|:---:|:---:|:---:|
     | Todos (lo reportado) | 80 | 19 (23,8 %) | 0,750 | 0,2375 | **3,16×** |
     | Solo predicción real (evento en sem ≥ 2) | 72 | 11 (15,3 %) | 0,473 | 0,1528 | **3,10×** |

     El AUC-PR absoluto cae de 0,750 a 0,473, **pero el lift se mantiene** (3,16× → 3,10×): la caída se explica por la menor prevalencia, no por pérdida de capacidad. El AUC-ROC sí se degrada (0,803 → 0,687), señal de que el ordenamiento empeora en la tarea genuinamente predictiva.
- **Decisión:**
  1. **La aplicación adopta un esquema de alerta por niveles seleccionable** («Confirmado», «Equilibrado», «Cobertura total»), con las cifras reales de cada punto de operación y una nota explícita del intercambio. El modelo detecta; **cuántos estudiantes acompañar es decisión institucional** (art. 23). Implementado en `app.py`.
  2. **El informe debe reportar las dos cifras** (0,750 global y 0,473 predictiva pura) con su explicación. Presentar solo la primera sobreestimaría la capacidad de anticipación.
  3. **Se confirma la necesidad del diseño longitudinal** (WP-OE1.4): predecir con datos de ingreso y primer semestre un evento que ocurre en los semestres 4 a 14 es el límite actual. Las variables de los arts. 19–22 identificadas en RC-014 (`pct_creditos_reprobados`, `art20_activado`, `veces_cursado`, `promedio_ponderado_acumulado`) siguen sin incorporarse y son la vía de mejora con mayor retorno esperado.
- **Destino en el informe:** Fase 5 (evaluación y decisión de umbral), discusión (validez temporal del target) y producto (esquema de alerta por niveles como aporte de usabilidad).

### RC-036 · 2026-09-15 · Fase 2 · **I-5 / WP-OE1.1** · Verificación de datos para Electrónica y Biología
- **Motivación:** determinar si lo aprendido sobre los datos de Ing. de Sistemas aplica a los otros dos programas del alcance, si son mezclables en un modelo único, y si la ampliación de la muestra habilita el diseño longitudinal (prerrequisito establecido al descartar el rediseño con Sistemas solo).
- **Método:** `src/verificacion_fcbi.py`. Cinco bloques: cobertura y llaves por programa; nulos de las variables del modelo; aplicación del target del art. 19 a los tres programas; EDA comparativo; y evaluación de la viabilidad de cortes longitudinales con la regla pre-registrada de RC-008 (n ≥ 60 y clase minoritaria ≥ 15).
- **Resultado:**
  1. **Cobertura homogénea.** Caracterización 275 → 262 con promedio de carrera (pérdida 4,7 %), repartida de forma pareja: Sistemas 95→90, Electrónica 95→91, Biología 85→81. La causa es la misma en los tres: admitidos sin actividad académica calificada. *Hallazgo operativo:* la caracterización usa `CODIGO_ESTUDIANTIL` como llave mientras el resto de fuentes usa `CODIGO_INST`.
  2. **Patrón de nulos idéntico.** `NIVEL_ED_PADRE` 17–22 % en los tres (característica del formulario SIIF, no de un programa); Saber 11 entre 1 % y 7 %; el resto de variables sin nulos. Las estrategias de imputación validadas en Sistemas son trasladables sin cambios.
  3. **El target del art. 19 aplica a los tres programas:** Sistemas 19/80 (23,8 %), **Electrónica 23/73 (31,5 %)**, Biología 17/81 (21,0 %). Total FCBI **59 positivos de 234 expuestos (25,2 %)**. El patrón de simultaneidad se repite en los tres: 26 de 59 eventos (44 %) ocurren en el primer semestre, con proporciones muy parecidas (42 %, 48 %, 41 %) — **es estructural, no una peculiaridad de Sistemas**.
  4. **⚠ Biología es una población estructuralmente distinta:** 64,7 % de mujeres frente a 15,8 % (Sistemas) y 7,4 % (Electrónica); Saber 11 unos 10 puntos por debajo en todas las áreas (matemáticas 54,8 vs 65,6 y 65,3); promedio de carrera 2,702 vs 3,083 y 3,036. Sistemas y Electrónica, en cambio, son comparables en composición, perfil de ingreso y promedio.
  5. **La tasa de graduación de Biología (7,1 %) está sesgada por censura:** tiene **15 estudiantes cuyo último estado es `MATRICULADO`** (18 % de la muestra), frente a cero en los otros dos programas. La desventaja real existe (24 `RETIRADO BR` con menos estudiantes) pero la cifra no debe reportarse sin la advertencia.
  6. **El diseño longitudinal se vuelve viable.** Con la muestra FCBI completa, los cortes 1, 2 y 3 superan el filtro de RC-008 (33, 19 y 16 eventos futuros sobre 208, 173 y 147 en riesgo), frente a **ningún corte viable** con Sistemas solo (11, 9, 9, 5, 3…). Los cortes 4 en adelante siguen sin serlo.
- **Decisión:** (a) no se rehace la Fase 2 para Electrónica y Biología: las reglas de recodificación, el diccionario y la definición del target son trasladables; (b) **modelo conjunto con `programa` como variable, contrastado empíricamente contra modelos separados** bajo el protocolo anidado — si el conjunto no supera a los separados por ΔAUC-PR ≥ 0,03, se mantienen separados (decisión por medición, no por criterio); (c) **Biología requiere tratamiento explícito de la censura**: los 15 activos se excluyen del target de graduación y se conservan en el del art. 19, que sí es observable; (d) se habilita WP-OE1.4 para los cortes 1–3.
- **Destino en el informe:** Fase 2 (comprensión de datos, sección FCBI), limitaciones (censura en Biología) y justificación del diseño longitudinal. Documento completo en `Fase 2/08_verificacion_fcbi.md`.

### RC-037 · 2026-09-15 · Fase 3–4 · **Dataset FCBI y decisión conjunto vs. separado**
- **Motivación:** RC-036 dejó abierta por medición la pregunta de si los tres programas son mezclables en un modelo único. Se construye el dataset maestro FCBI y se contrasta empíricamente.
- **Método:** `src/preprocessing.py` parametrizado por programa (`cargar_datos(programas=...)`, conservando Ing. de Sistemas como valor por defecto para no romper `app.py`); `src/dataset_fcbi.py` construye `src/df_master_fcbi.csv` con los 262 estudiantes y aplica el target del art. 19. Comparación bajo el protocolo de I-3 bis: conjunto S3, Random Forest, CV-5 × 10 repeticiones, AUC-PR, SEED=42. Comparador: media ponderada por tamaño de los tres modelos separados, que es el desempeño esperado del enfoque separado en producción.
- **Resultado:** dataset FCBI de **262 estudiantes, 234 expuestos, 59 positivos (25,2 %)**.

  | Modelo | n | Positivos | AUC-PR | Línea base | Lift |
  |---|:---:|:---:|:---:|:---:|:---:|
  | Separado · Sistemas | 80 | 19 | **0,7483** | 0,237 | 3,15× |
  | Separado · Electrónica | 73 | 23 | **0,7250** | 0,315 | 2,30× |
  | Separado · Biología | 81 | 17 | **0,5983** | 0,210 | 2,85× |
  | Conjunto sin indicador de programa | 234 | 59 | 0,6585 | 0,252 | 2,61× |
  | Conjunto con indicador de programa | 234 | 59 | 0,6615 | 0,252 | 2,62× |

  1. **Los modelos separados ganan.** El conjunto sin indicador pierde Δ=−0,0306 (p=0,043): diferencia significativa **y** relevante según la regla pre-registrada. Con indicador de programa la pérdida baja a Δ=−0,0276 (p=0,038), que queda como empate técnico por magnitud.
  2. **El indicador de programa no aporta:** Δ=+0,0030 (p=0,453). Añadir la etiqueta del programa no compensa la heterogeneidad; el problema no es de intercepto sino de estructura.
  3. **El modelo conjunto es peor que dos de los tres separados** pese a disponer de casi el triple de datos.
  4. **Biología es el programa más difícil de modelar** (AUC-PR 0,598 frente a 0,748 y 0,725), coherente con su heterogeneidad estructural y con la censura documentada en RC-036.
- **Decisión:** **se adoptan modelos separados por programa**, con el mismo algoritmo y el mismo protocolo en los tres. Esto es compatible con la propuesta de grado: el compromiso es seleccionar **un algoritmo ganador** mediante comparación, no una única instancia entrenada; el algoritmo es único y las instancias ajustadas son tres. Se descarta el indicador de programa por no aportar. `df_master_fcbi.csv` queda como dataset maestro para WP-OE1.4 y WP-OE1.5.
- **⚠ Matiz importante para el informe — "más datos" no es incondicional:** la curva de aprendizaje de RC-029 mostró que **más datos de la misma población** mejoran el modelo; este experimento muestra que **más datos de poblaciones distintas lo empeoran**. No hay contradicción: son dos afirmaciones diferentes que conviene no confundir. El argumento para ampliar la muestra sigue siendo válido *dentro de cada programa*, y la ampliación a la FCBI se justifica por habilitar el diseño longitudinal (RC-036), no por agrandar el conjunto de entrenamiento de un modelo único.
- **Destino en el informe:** Fase 3 (dataset maestro), Fase 4 (arquitectura del modelo: separado por programa con justificación empírica) y discusión (heterogeneidad poblacional frente a tamaño de muestra).

### RC-038 · 2026-09-15 · Fase 3–4 · **WP-OE1.4** · El diseño longitudinal NO mejora la predicción
- **Motivación:** probar la hipótesis formulada en RC-035 y respaldada por el auditor — que incorporar las variables acumuladas de los arts. 19–22 en un diseño por cortes semestrales sería "la vía de mejora con mayor retorno esperado".
- **Método:** `src/longitudinal.py`. Panel estudiante-periodo (1 290 filas, 234 estudiantes, FCBI). Para cada corte k: población en riesgo = quienes cursaron ≥ k periodos **sin** haber activado el art. 19 hasta k; target = lo activan **después** de k. Siete variables acumuladas nuevas (promedio ponderado acumulado, % de créditos reprobados acumulado y del último periodo, activaciones del art. 20, máximo de veces cursada una asignatura, créditos y asignaturas acumuladas). Random Forest, CV-5 × 10 repeticiones, AUC-PR, SEED=42. Regla de viabilidad RC-008.
- **Resultado — la hipótesis queda refutada:**

  | Corte | En riesgo | Eventos | Solo ingreso | Solo acumuladas | Ingreso + acumuladas |
  |:---:|:---:|:---:|:---:|:---:|:---:|
  | 1 | 202 | 27 (13,4 %) | **0,1837** (lift 1,37×) | 0,1521 (1,14×) | 0,1900 (1,42×) |
  | 2 | 174 | 20 (11,5 %) | **0,1750** (lift 1,52×) | 0,0975 (**0,85×**) | 0,1545 (1,34×) |
  | 3 | 138 | 7 (5,1 %) | — no viable (RC-008) | — | — |

  1. **Las variables acumuladas no aportan.** Corte 1: Δ=+0,0062 (p=0,514), empate. Corte 2: Δ=**−0,0204** (p=0,044) — añadirlas **empeora** el modelo.
  2. **Por sí solas son peores que el azar** en el corte 2: AUC-PR 0,0975 frente a una línea base de 0,1149 (lift 0,85×) y AUC-ROC 0,419, por debajo de 0,5.
  3. **Causa verificada: no hay asociación.** Entre quienes sobrevivieron al corte, ninguna variable acumulada distingue a quienes activarán el art. 19 después. Corte 1: promedio ponderado acumulado 3,334 (activan) vs. 3,259 (no activan), p=0,807 — incluso invertido. Corte 2: las cuatro variables con p > 0,5. **Contraste sin condicionar:** `prom_sem1` 2,293 (activan) vs. 3,283 (no activan), una diferencia enorme y evidente.
  4. **El lift cae de 3,1× a 1,4×** al pasar al problema condicional, coherente con lo medido en RC-035.
- **Interpretación sustantiva — el hallazgo real:** **el evento del art. 19 es agudo, no gradual.** Exige reprobar el **100 % de los créditos de un periodo**: es un colapso puntual, no un deterioro progresivo. El estudiante mediocre sostenido no lo activa; lo activa quien tiene un semestre catastrófico. Por eso los promedios acumulados no lo anticipan — **no es la acumulación lo que importa, es un choque discreto**. Esto explica a la vez por qué el modelo global sí funciona (captura a quienes colapsan en el primer semestre, el 44 % de los casos) y por qué el condicional no (anticipar *cuándo* alguien tendrá un semestre catastrófico, años antes, a partir de promedios, es prácticamente imposible con esta información).
- **Decisión:** (a) **se descarta el diseño longitudinal para este target**; el modelo vigente sigue siendo el de trayectoria completa (RC-033); (b) el auditor reconoce que su recomendación de priorizar esta vía era **incorrecta** y estaba basada en una hipótesis que los datos refutan; (c) si se desea un producto con actualización semestral tipo SPADIES, **el target debe cambiar**: predecir un descenso *gradual* (trayectoria del promedio acumulado, rezago en créditos) es plausible; predecir un evento agudo con años de antelación no lo es; (d) se conserva `src/longitudinal.py` y los datasets por corte como evidencia del experimento.
- **Destino en el informe:** Fase 4 (resultado negativo con explicación), discusión (naturaleza aguda vs. gradual del fenómeno — determina qué se puede predecir y con cuánta antelación) y trabajo futuro (redefinición del target para el producto longitudinal). **Es un resultado publicable:** documenta que la elección del target no solo condiciona el desempeño sino **el horizonte de anticipación alcanzable**.

### RC-039 · 2026-09-15 · Fase 3–4 · **¿Falta de datos o mal planteamiento?** Diagnóstico del fracaso longitudinal
- **Motivación:** RC-038 documentó que el diseño longitudinal no predice. Queda por determinar la causa: muestra insuficiente o definición inadecuada del target. La distinción importa porque los remedios son opuestos — conseguir más datos o replantear el problema.
- **Método:** experimento de ancho de target. **Se mantiene todo constante** (mismo diseño por cortes, mismas variables de ingreso + acumuladas, mismo Random Forest, mismo protocolo CV-5 repetida) y **solo se varía el umbral que define el evento**. Se usa **AUC-ROC** para la comparación entre targets porque, a diferencia del AUC-PR, es independiente de la prevalencia y por tanto comparable cuando la línea base cambia.
- **Resultado:**

  | Definición del evento | Corte | n | Eventos | Línea base | AUC-PR | **AUC-ROC** |
  |---|:---:|:---:|:---:|:---:|:---:|:---:|
  | Art. 19 estricto (100 % de créditos) | 1 | 202 | 33 | 0,163 | 0,176 | **0,496** |
  | Art. 19 estricto (100 % de créditos) | 2 | 174 | 26 | 0,149 | 0,136 | **0,468** |
  | ≥ 75 % de créditos reprobados | 1 | 193 | 65 | 0,337 | 0,410 | **0,603** |
  | ≥ 75 % de créditos reprobados | 2 | 151 | 35 | 0,232 | 0,287 | **0,567** |
  | > 50 % (art. 20) | 1 | 176 | 104 | 0,591 | 0,656 | **0,647** |
  | > 50 % (art. 20) | 2 | 120 | 52 | 0,433 | 0,554 | **0,673** |

  1. **El AUC-ROC mejora de forma monótona al ampliar el target**: 0,496 → 0,603 → 0,647 en el corte 1; 0,468 → 0,567 → 0,673 en el corte 2. **Un salto de ~0,20 producido únicamente por cambiar la definición del evento**, con la misma muestra, las mismas variables y el mismo algoritmo.
  2. **El art. 19 estricto tiene AUC-ROC ≈ 0,47–0,50: cero discriminación.** No es señal débil, es ausencia de señal.
  3. **Causa mecánica verificada — el umbral es un filo.** De los 1 232 periodos-estudiante regulares: 65 con el 100 % de créditos reprobados (activan) frente a **104 entre el 60 % y el 99 % (no activan)**. Hay **1,6 casi-activaciones por cada activación**: la diferencia entre disparar el artículo y no dispararlo es *aprobar un solo curso*, lo que introduce un componente cuasi-aleatorio que ningún modelo puede anticipar.
- **Diagnóstico — las tres causas, jerarquizadas:**
  1. **Definición del target (dominante, demostrado).** Un evento definido sobre un umbral extremo y discreto es intrínsecamente poco predecible con antelación. Evidencia: ampliar el umbral sube el AUC-ROC 0,20 puntos sin tocar nada más.
  2. **Tamaño de muestra (secundario, plausible).** Con 26–33 eventos el poder es limitado y los intervalos amplios, pero **no explica un AUC-ROC de 0,47**: con esa misma muestra y el target ancho sí se detecta señal (0,65–0,67).
  3. **Variables insuficientes (no medible aquí).** Falta información sobre asistencia (art. 58, no entregada), situación financiera sobrevenida, carga laboral y factores personales — que son precisamente los que explicarían un colapso puntual. Un semestre catastrófico suele originarse fuera del expediente académico.
- **Decisión:** (a) se confirma que el fracaso de RC-038 es **atribuible al planteamiento antes que a los datos**; (b) para el producto longitudinal tipo SPADIES, el target debe redefinirse sobre un **fenómeno gradual y de umbral amplio** — la recomendación concreta es `> 50 % de créditos reprobados en el periodo` (art. 20), que además es el disparador real del acompañamiento institucional según el art. 23 y alcanza AUC-ROC 0,65–0,67; (c) el modelo vigente de trayectoria completa (RC-033) **no se ve afectado** y sigue siendo el entregable; (d) se documenta la carencia de variables de asistencia como brecha de información ante la Oficina de Sistemas.
- **Destino en el informe:** Fase 4 (diagnóstico del resultado negativo), discusión (predictibilidad y definición del evento) y trabajo futuro. **Es el resultado más transferible del estudio:** demuestra con un experimento controlado que *la definición del evento condiciona más la predictibilidad que el tamaño de la muestra o la elección del algoritmo* — y ofrece un método sencillo para diagnosticarlo (variar el ancho del target manteniendo todo lo demás constante).

### RC-040 · 2026-09-16 · Fase 3 · Variables de inestabilidad: hipótesis parcialmente refutada
- **Motivación:** RC-038/RC-039 establecieron que el evento es **agudo**. De ahí se derivó la hipótesis de que lo predictivo no sería el *nivel* del rendimiento sino su **inestabilidad** (volatilidad, tendencia). Se pone a prueba.
- **Método:** cuatro variables derivadas del panel estudiante-periodo, calculadas de forma expansiva (solo con información hasta el corte, sin fuga): `volatilidad` (desviación estándar del promedio por periodo), `tendencia` (diferencia respecto al periodo anterior), `peor_periodo` (mínimo del promedio por periodo hasta el corte) y `caida_max` (rango entre el mejor y el peor). Se evalúan sobre el **target amplio del art. 20**, el único que mostró señal en RC-039. Random Forest, CV-5 × 6 repeticiones.
- **Resultado:**

  | Conjunto | Corte 2 (n=120, ev=52) | Corte 3 (n=87, ev=22) |
  |---|:---:|:---:|
  | Ingreso + acumuladas | AUC-ROC 0,666 | AUC-ROC 0,605 |
  | **+ inestabilidad** | **AUC-ROC 0,683** | **AUC-ROC 0,617** |
  | Solo inestabilidad | AUC-ROC 0,654 | AUC-ROC 0,518 |

  **Asociación individual (Mann-Whitney):**

  | Variable | Corte 2 | Corte 3 | Veredicto |
  |---|:---:|:---:|---|
  | `volatilidad` | p=0,985 | p=0,317 | ✗ No predice |
  | `tendencia` | p=0,160 | p=0,934 | ✗ No predice |
  | `caida_max` | p=0,985 | p=0,255 | ✗ No predice |
  | **`peor_periodo`** | **p=0,011** | **p=0,008** | ✅ **Significativa en ambos cortes** |

  1. **La hipótesis de la volatilidad queda refutada:** ni la desviación estándar ni la tendencia ni la caída máxima distinguen a quienes tendrán un mal periodo futuro.
  2. **Pero `peor_periodo` sí predice, y es la única variable consistentemente significativa** en los dos cortes (3,098 vs. 3,257 y 2,971 vs. 3,225). Es coherente con el marco del evento agudo: **lo que importa no es cuánto varía el estudiante, sino si ya tuvo un semestre malo**. Un mal periodo previo anticipa otro; la variabilidad en sí no.
  3. La ganancia conjunta es **pequeña pero consistente**: +0,017 y +0,012 de AUC-ROC en los dos cortes.
- **Decisión:** incorporar **`peor_periodo`** al conjunto de variables del diseño longitudinal (barato y con asociación demostrada); descartar `volatilidad`, `tendencia` y `caida_max`. La ganancia no justifica por sí sola un cambio de arquitectura, pero la variable es interpretable y defendible ante el Programa de Retención: *"ya tuvo un semestre por debajo de 3,1"* es un criterio que la institución entiende y puede accionar.
- **Destino en el informe:** Fase 3 (ingeniería de variables) y discusión. El contraste entre la hipótesis (volatilidad) y el hallazgo (peor periodo) refina la caracterización del fenómeno: **el riesgo no es la inestabilidad, es el antecedente**.

### RC-041 · 2026-09-16 · Fase 3 · **WP-OE1.3 / P1** · El target multiclase de la propuesta NO es viable
- **Motivación:** construir la variable objetivo comprometida en la propuesta de grado — estado académico al final del seguimiento en cuatro clases: **graduado, activo, desertor, rezagado** — y aplicarle la regla de viabilidad pre-registrada en RC-008.
- **Método:** `src/target_multiclase.py`. Definiciones fijadas **antes** de modelar: `GRADUADO` = estado final GRADUADO; `ACTIVO` = último estado MATRICULADO y reciente (≥ 2024-1); `DESERTOR` = resto; `REZAGADO` = activo que excede los 10 semestres del plan nominal. Población: los 262 estudiantes del dataset FCBI. Regla RC-008: clase minoritaria ≥ 25 estudiantes **y** ≥ 5 por pliegue en CV-5.
- **Resultado:**

  | Target | Clases | Clase minoritaria | n | Por pliegue | ¿Viable? |
  |---|:---:|---|:---:|:---:|:---:|
  | **4 clases (propuesta original)** | 4 | ACTIVO | **5** | 1,0 | **NO** |
  | **3 clases (colapsada)** | 3 | ACTIVO | **20** | 4,0 | **NO** |
  | **2 clases (graduación)** | 2 | GRADUADO | **66** | 13,2 | **Sí** |

  Distribución con 4 clases: DESERTOR 176 (67,2 %), GRADUADO 66 (25,2 %), REZAGADO 15 (5,7 %), **ACTIVO 5 (1,9 %)**.

  1. **El target de cuatro clases no es modelable.** Con 5 estudiantes en la clase ACTIVO, la validación cruzada de 5 pliegues dejaría **un caso por pliegue**.
  2. **El colapso a tres clases tampoco alcanza:** ACTIVO queda con 20 (4 por pliegue), por debajo de ambos umbrales de RC-008.
  3. **Solo el target binario de graduación es viable** (66 minoritarios, 13,2 por pliegue) — y es el que el proyecto ya venía usando.
  4. **Hallazgo adicional: la clase ACTIVO es, en esencia, el grupo censurado de Biología.** De los 20 activos, **15 son de Biología** (75 %), frente a 4 de Electrónica y 1 de Sistemas. Coincide exactamente con la censura documentada en RC-036. Es decir, la clase no captura un fenómeno académico sino un **artefacto de la ventana de observación**.
  5. **Causa de fondo — la ventana de observación agota las trayectorias.** Las cohortes 2017-2 y 2018-1 llevan ~17 periodos frente a un plan nominal de 10. Los graduados tardaron una mediana de 11 periodos (máximo 14) y los activos llevan 12. A esta altura **casi nadie sigue "activo a tiempo"**: la distinción entre *activo* y *rezagado* pierde sentido porque el 75 % de los activos ya excede el plan. Las cuatro clases de la propuesta describen un seguimiento **más corto** que el disponible.

  6. **Se probaron tres operacionalizaciones alternativas de «rezagado» antes de declarar la inviabilidad.** Ninguna rescata el target, y el cuello de botella es siempre el mismo:

     | Alternativa | Clase minoritaria | n | Por pliegue | ¿Viable? |
     |---|---|:---:|:---:|:---:|
     | **A.** Rezagado = activo que excede 10 semestres | ACTIVO | 5 | 1,0 | No |
     | **B.** Rezagado = *cualquiera* que excede 10 semestres (incluye graduados tardíos) | ACTIVO | 5 | 1,0 | No |
     | **C.** Separar graduado a tiempo vs. graduado tardío | ACTIVO | 20 | 4,0 | No |

     **El limitante no es la clase «rezagado» sino la clase «activo».** En cuanto se separa el rezago —con cualquier criterio— ACTIVO se queda con los 5 estudiantes que siguen matriculados *dentro* del tiempo nominal. Y sin separarlo (alternativa C), ACTIVO sigue en 20, por debajo del umbral.

  7. **El hallazgo más profundo: en estas cohortes el rezago es la NORMA, no la excepción.** De los 66 graduados, **39 (59 %) tardaron más de 10 periodos**; de los 20 activos, 15 (75 %). Entre quienes no desertaron, **el 63 % excedió el plan nominal**. Una clase que agrupa al 63 % de la población no discrimina: «rezagado» no describe un subgrupo en riesgo sino la condición habitual del estudiante que persiste. El target de cuatro clases presupone que «a tiempo» y «rezagado» son grupos comparables, y en esta población **estar a tiempo es lo excepcional**.
- **Decisión:** (a) **se declara inviable el target multiclase de cuatro clases** y se documenta con esta evidencia; no se fuerza su construcción; (b) se adopta el **target binario de graduación** como variable objetivo de trayectoria, que ya está evaluado (RC-023) y es viable; (c) el **rezago pasa a indicador continuo secundario** (`periodos_sobre_plan`), conforme a lo pre-registrado en RC-008; (d) los 20 activos se marcan con `censurado = 1` y se excluyen del target de graduación por no tener desenlace definitivo; (e) **este resultado debe consultarse con la dirección del proyecto**, porque modifica un entregable comprometido (E2). Salidas: `src/df_master_fcbi_multiclase.csv` (con `clase_4`, `clase_3`, `rezagado`, `periodos_sobre_plan`, `censurado`), `src/multiclase_distribucion.csv`.
- **Destino en el informe:** Fase 3 (definición de la variable objetivo), limitaciones y discusión. **No es un fracaso sino un resultado:** la propuesta especificó un target de cuatro clases razonable *a priori*, y el estudio demuestra con la regla pre-registrada que la ventana de observación disponible no lo sostiene. Es precisamente el tipo de ajuste que el carácter iterativo de CRISP-DM contempla, y haberlo detectado con un criterio fijado de antemano —en vez de ajustar el criterio al resultado— es la garantía de que la decisión no fue oportunista.

---

### RC-042 · El PCA no respalda una selección de variables supervisada, y se demuestra midiéndolo
- **Fecha:** 2026-09-29 · **Origen:** petición del asesor a cambio de gestionar cohortes nuevas ante la Oficina de Sistemas.
- **Pregunta:** ¿confirma el PCA que las 6 variables del conjunto S3 son las mejores?
- **Aclaración metodológica previa, registrada antes de ejecutar nada:** el PCA es **no supervisado**. Busca direcciones de máxima varianza en X sin mirar nunca a *y*. Por construcción **no puede** demostrar que un conjunto de variables sea el mejor para predecir: una variable de varianza minúscula puede ser el mejor predictor y una de varianza enorme puede ser ruido. Presentar un gráfico de sedimentación como prueba de que la selección es correcta sería un error metodológico. Lo que sí admite es (a) medir redundancia y (b) generar una representación alternativa cuya **capacidad predictiva** sí se puede comparar. Se ejecutaron ambas.
- **Protocolo:** idéntico a I-3 bis (CV-5 anidada, 10 repeticiones, n=80, 19 positivos, AUC-PR primaria, azar 0,2375). Toda transformación (escalado, PCA, PLS) va **dentro del Pipeline**, ajustada solo con el pliegue de entrenamiento: fijarla antes de la CV sería repetir la fuga de RC-032.
- **Evidencia descriptiva:** las 19 variables necesitan **13 de 19 componentes** para el 90 % de la varianza (10 para el 80 %, 15 para el 95 %). No son fuertemente redundantes. El conjunto S3 necesita 5 de sus 6.
- **Hallazgo central:** el **promedio del primer semestre** —la variable más predictiva de todo el estudio, 40,4 % de la importancia— alcanza su carga máxima en **CP3, que explica solo el 8,3 % de la varianza**. Los dos primeros componentes están dominados por el bloque SABER 11 y la educación de los padres. **Quien hubiera seleccionado variables por varianza explicada habría descartado la única variable que predice.**
- **Evidencia predictiva** (referencia: S3 + Random Forest, AUC-PR 0,7418 ± 0,0105):

  | Configuración | AUC-PR | AUC-ROC | Δ | p | Veredicto |
  |---|:---:|:---:|:---:|:---:|---|
  | 19 variables crudas · RF | 0,7176 | 0,8082 | −0,024 | 0,418 | empate estadístico |
  | **PCA(k) sobre 19 · RF** | **0,3715** | 0,6294 | **−0,370** | <0,0001 | **peor (relevante)** |
  | PCA(k) sobre 19 · Logística | 0,3819 | 0,6085 | −0,360 | <0,0001 | peor (relevante) |
  | PCA(k) sobre S3 · RF | 0,6947 | 0,8616 | −0,047 | 0,295 | empate estadístico |
  | PLS-DA(k) sobre 19 (supervisado) | 0,4637 | 0,6940 | −0,278 | <0,0001 | peor (relevante) |
  | PLS-DA(k) sobre S3 (supervisado) | 0,4463 | 0,6394 | −0,296 | <0,0001 | peor (relevante) |

- **Decisión:** el conjunto S3 se mantiene. Queda respaldado por **tres vías independientes**: ablación anidada (RC-032), esta comparación de representaciones, y la posterior bayesiana (RC-043). El PCA se incorpora al informe **como diagnóstico y como argumento metodológico**, no como criterio de selección.
- **Nota:** el PLS eligió **k=1 componente en las 50 iteraciones**, lo que confirma que existe una sola dirección útil en los datos; al ser lineal no captura su forma, de ahí la distancia frente a Random Forest.
- **Salidas:** `src/pca_seleccion.py`, `src/arnes_experimentos.py`, `src/_resultados_pca.json`, hoja «9 · PCA y selección» del consolidado.

---

### RC-043 · Modelos bayesianos: no mejoran el acierto, pero destapan una colinealidad y justifican cambiar la app
- **Fecha:** 2026-09-29 · **Origen:** petición del asesor.
- **Protocolo:** el mismo de RC-042. La inferencia dentro de la CV usa **aproximación de Laplace** (gaussiana en la moda con covarianza igual a la inversa del hessiano, Bishop §4.5) en lugar de MCMC: cada ajuste con ADVI cuesta ~101 s, lo que situaría las 500 reajustes del protocolo en ~14 horas. Con 6 variables y n≈64 la posterior de una logística con prior gaussiana es log-cóncava y casi gaussiana, de modo que la aproximación es fiel. La inferencia completa con PyMC/ADVI sí se ejecuta **una vez sobre la muestra entera** para la posterior descriptiva.

  | Modelo | AUC-PR | AUC-ROC | Δ vs RF | p |
  |---|:---:|:---:|:---:|:---:|
  | Naive Bayes gaussiano | 0,4252 | 0,6226 | −0,317 | 0,0005 |
  | **Logística bayesiana (Laplace)** | **0,6190** | 0,6956 | −0,123 | 0,0032 |
  | Logística bayesiana · 19 vars | 0,5652 | 0,7646 | −0,177 | 0,0002 |
  | Proceso gaussiano | 0,4354 | 0,6242 | −0,306 | <0,0001 |
  | Logística L2 (MAP de la anterior) | 0,6045 | 0,6975 | −0,137 | 0,0020 |
  | Naive Bayes · 19 vars | 0,4420 | 0,6915 | −0,300 | 0,0015 |
  | S3 sin SABER-total · RF | 0,7207 | 0,7742 | −0,021 | 0,126 |

- **Resultado 1 — ninguno supera a Random Forest**, y era esperable: salvo el proceso gaussiano son modelos de frontera lineal frente a un problema con interacciones. El dato que sí importa: la logística bayesiana (0,619) **supera a su propio MAP regularizado** (0,605) con idénticas variables. Esa diferencia es lo que aporta integrar sobre la posterior en vez de quedarse con la moda.
- **Resultado 2 — HALLAZGO NO BUSCADO: colinealidad en el bloque SABER 11.** La posterior da a `icfes_total` un coeficiente **positivo y creíble (+1,56; IC 94 % [+0,84, +2,25])**: más puntaje, más riesgo. Es sustantivamente imposible y es el síntoma clásico de **supresión por colinealidad**. Comprobado: `icfes_total` tiene **VIF 6,66** y **R² = 0,850** contra sus tres áreas; su correlación con la suma de las áreas es 0,920. El modelo está ajustando contrastes entre el total y sus partes, no efectos interpretables.
  - **A Random Forest no le afecta** (retirar el total deja 0,721 frente a 0,742, empate estadístico p=0,126), así que el modelo en producción no está comprometido.
  - **Pero cualquier lectura de coeficientes o de importancias individuales dentro del bloque SABER 11 es inválida** mientras el total conviva con sus áreas. **Decisión pendiente de aprobación:** conservar el total y retirar las tres áreas, o al revés, antes de interpretar nada en el informe.
- **Resultado 3 — coeficientes con efecto creíble** (variables tipificadas, IC 94 % que no contiene el cero): `prom_sem1` **−1,362** [−1,95, −0,77], `icfes_total` +1,558 (artefacto, ver arriba), `icfes_lec` −0,934 [−1,71, −0,18]. Sin efecto distinguible: `sin_primer_semestre`, `icfes_mat`, `icfes_nat`. **Tercera confirmación independiente** de la dominancia del promedio de primer semestre.
- **Resultado 4 — la incertidumbre por caso sostiene el cambio en la app.** La anchura mediana del intervalo creíble del 94 % de la probabilidad individual es **0,359**, y en **43 de 80 estudiantes (54 %) supera 0,30**. Para esos casos el modelo no está en condiciones de emitir un número. Confirma por vía independiente el defecto de calibración del 2026-09-16 y refuerza la recomendación: la app debe mostrar **nivel de alerta y puesto relativo**, no un porcentaje.
- **Salidas:** `src/modelos_bayesianos.py`, `src/_resultados_bayes.json`, hoja «10 · Modelos bayesianos».

---

### RC-044 · «One-shot learning» no es trasladable; lo que sí responde a la escasez es la curva de tamaño muestral
- **Fecha:** 2026-09-29 · **Origen:** petición del asesor.
- **Aclaración registrada antes de ejecutar:** el one-shot / few-shot learning en sentido estricto sirve para reconocer **clases nuevas** con uno o pocos ejemplos, y descansa en dos cosas que aquí no existen: (1) un corpus grande de preentrenamiento del que transferir una representación, y (2) una estructura por episodios con clases no vistas en entrenamiento. Este problema es tabular, binario y con ambas clases presentes desde el inicio. Aplicar una red siamesa literal sería ponerle nombre de moda a un clasificador corriente. **Lo que sí se traslada es el mecanismo**: aprender una métrica y clasificar por cercanía a un prototipo de clase — ProtoNet, despojada de la red, es exactamente la clasificación por media de clase en un espacio métrico aprendido.

  | Método | AUC-PR | AUC-ROC | Δ vs RF | p |
  |---|:---:|:---:|:---:|:---:|
  | Prototipos de clase (ProtoNet tabular) | 0,4373 | 0,6461 | −0,305 | <0,0001 |
  | NCA + prototipos (métrica aprendida) | 0,3559 | 0,6148 | −0,386 | <0,0001 |
  | NCA + k vecinos | 0,6084 | 0,7934 | −0,133 | 0,019 |
  | k vecinos sin métrica aprendida | 0,6435 | 0,7724 | −0,098 | 0,0021 |

- **Resultado instructivo:** **aprender la métrica con NCA empeora los prototipos** (0,356 frente a 0,437). Con 19 positivos, NCA sobreajusta la métrica. Es justo el régimen en el que los métodos de few-shot dependen de un preentrenamiento externo que aquí no existe. No dice que la familia sea mala: dice que **sin corpus del que transferir, no hay atajo**.
- **Lo que sí responde a la pregunta de fondo — curva de tamaño muestral.** Submuestreando solo el pliegue de entrenamiento (el de prueba queda intacto) con hiperparámetros fijos:

  | n entrenamiento | positivos | AUC-PR |
  |:---:|:---:|:---:|
  | 22 | 5,1 | 0,5487 |
  | 28 | 7,0 | 0,6147 |
  | 35 | 8,2 | 0,6701 |
  | 44 | 10,2 | 0,6945 |
  | 54 | 13,1 | 0,7380 |
  | 64 | 15,2 | 0,7466 |

  Ajuste por ley de potencias: **AUC-PR(n) = 0,838 − 8,843·n^(−1,107)**, R² = 0,994. **Techo asintótico estimado 0,838.**

  | n total | AUC-PR proyectado | Ganancia |
  |:---:|:---:|:---:|
  | 80 (hoy) | 0,749 | — |
  | 160 (duplicar) | 0,797 | +0,048 |
  | 240 (triplicar) | 0,811 | +0,062 |
  | 320 (cuadruplicar) | 0,819 | +0,070 |

- **Lectura para la petición de datos:** duplicar la muestra compra en torno a **+0,05 de AUC-PR**; cuadruplicarla, unos **+0,07**. La curva satura pronto porque **el techo lo impone la información disponible, no el número de filas**. Las cohortes nuevas son muy valiosas —sobre todo porque habilitan la **validación externa que hoy no existe**, que es la limitación más seria del estudio— pero si además se incorporasen asistencia (art. 58), fechas de pago y créditos cancelados, subiría el techo mismo. **Más filas mejoran la estimación; más variables mueven el límite.**
- **Cautela registrada:** extrapolar desde 64 casos de entrenamiento hasta 320 es una proyección de orden de magnitud, no una predicción. Supone que las cohortes nuevas se parecen a las actuales y que la prevalencia se mantiene. **Si las cohortes nuevas caen bajo el reglamento vigente desde 2022 y las actuales bajo el Acuerdo 015 de 2003, ese supuesto se rompe** — lo que conecta con la pregunta de régimen normativo aún abierta con la dirección.
- **Salidas:** `src/pocos_datos.py`, `src/_resultados_pocos.json`, hoja «11 · Pocos datos y tamaño».

---

### RC-045 · Reconciliación: por qué el AUC-PR del modelo aparece con cinco valores
- **Fecha:** 2026-09-30 · **Origen:** auditoría documental previa al envío del proyecto a otro investigador. Un lector externo encuentra el desempeño del modelo citado como 0,745, 0,750, 0,7483, 0,7466 y 0,7418 y no puede saber cuál es.
- **Problema:** no hay error de cálculo en ninguna. Son **cinco corridas distintas** del mismo modelo (Random Forest, conjunto S3, target art. 19, n=80, SEED=42) que difieren en el presupuesto de búsqueda y en el propósito del experimento. Pero el registro no lo decía en ninguna parte.

  | Valor | Entrada | Qué midió exactamente |
  |:---:|:---:|---|
  | **0,745 ± 0,025** | **RC-033** | **Cifra canónica.** Comparación definitiva I-3 bis, rejilla completa de 16–24 combinaciones, 15 repeticiones. Es la que debe citarse salvo que se esté hablando de otro experimento |
  | 0,750 | RC-035 | Curva de umbral, corrida independiente al analizar el punto de operación |
  | 0,7483 | RC-037 | Instancia de Sistemas **dentro** de la comparación conjunto-vs-separado por programa |
  | 0,7466 | RC-044 | Punto del 100 % de la curva de tamaño muestral, con hiperparámetros **fijos** en lugar de buscados |
  | 0,7418 ± 0,0105 | RC-042 | Referencia del encargo del 29-09, con rejilla **recortada a 6 combinaciones** por el límite de cómputo (180 s por ejecución, 2 núcleos) |

- **Lectura:** la dispersión total es de **0,0082 de AUC-PR**, muy por debajo del umbral de relevancia pre-registrado (0,03) y de la desviación típica entre repeticiones (±0,025). Es la variación esperable al cambiar el presupuesto de búsqueda, y de hecho **ilustra** lo documentado en RC-025: el presupuesto mueve el resultado, por eso debe igualarse entre algoritmos antes de compararlos.
- **Decisión:** **la cifra oficial del modelo es 0,745 ± 0,025 (RC-033).** Las demás solo se citan dentro del experimento que las produjo, indicando su condición. Cualquier documento que dé una cifra de desempeño debe decir de qué corrida procede.
- **Destino en el informe:** nota metodológica en el capítulo de resultados. No es una incidencia: es una consecuencia medible del protocolo, y declararla refuerza la credibilidad del resto.

<!-- Nuevas entradas debajo de esta línea. Formato en PLAN_OPERATIVO_AGENTES.md §0.3 -->


### RC-046 · 2026-09-30 · Fase 2–3 · Capa de equivalencias entre planes de estudio (IS-2011 ↔ IS-2018)
- **Motivación:** permitir cargar cohortes del plan 2011, del 2018 o mezcladas sin romper el pipeline.
- **Método:** transcripción del Acuerdo Académico 008/2011, el Acuerdo Académico 001/2017 y la Resolución Académica 036/2017 a `src/planes_estudio/`; módulo `src/equivalencias.py` con identidad canónica de curso (plan vigente; prioridad Art. 2 > Art. 1 > institucional; `CURSO_INTENTOS` para las fusiones n:1); parámetro opcional `clave_curso` en `construir_target_art19` y `panel_estudiante_periodo`, y `canonico` en `calcular_indice`. Pruebas en `tests/test_equivalencias.py`.
- **Resultado:** los totales oficiales se reproducen (167 y 165 créditos; 53 cursos). La extracción tiene cobertura completa (107/107 códigos, 0 discrepancias de créditos, 0 estudiantes con planes mezclados). El target del art. 19 es **idéntico** con la clave histórica y la canónica (Sistemas y FCBI), y el dataset maestro y `materias_criticas.csv` no cambian. El top 5 de criticidad se conserva al traducirlo (Cálculo integral, Física mecánica, Álgebra lineal, Cálculo diferencial, Algoritmia y programación). Un caso sintético demuestra que, sin la capa, la cuarta reprobación que cruza planes no se detecta.
- **Decisión:** adoptar la clave canónica en todo código nuevo (TRAYECTA) y conservar la histórica por defecto. Electrónica (612/613) queda sin traducción hasta obtener su resolución.
- **Destino en el informe:** Fase 3 (preparación) y Fase 6 (transferencia). Documento: `docs/ANALISIS_EQUIVALENCIAS_PLANES.md`.

### RC-047 · 2026-09-30 · Fase 2 · `sin_primer_semestre` identifica el ingreso por homologación; la cohorte 2018-1 cursó el plan 2011
- **Resultado:** `sin_primer_semestre` coincide exactamente con PENSUM 603 (16/16 y 0/74). De esos 20 estudiantes del PENSUM 603, 16 tienen HOMOLOGACION = SI. En Electrónica, 36 de los 37 estudiantes del 613 tienen el indicador. Además, 39 de los 44 estudiantes de la cohorte 2018-1 tienen PENSUM 602 y el primer registro 603 es de 2019-0. Sensibilidad (`src/analisis_cambio_plan.py`, RF con la configuración modal, CV-5×10): sin el PENSUM 603, el AUC-PR es 0,756 (frente a 0,751 de referencia).
- **Decisión:** se conserva el nombre `sin_primer_semestre`, ahora respaldado por las columnas `pensum` y `homologacion` del SIIF (coinciden en los 90 casos de Sistemas). Que la cohorte 2018-1 cursara el plan 2011 queda confirmado por los datos y lo absorbe la capa de equivalencias. El modelo no depende de esa población.
- **Destino:** Fase 2, limitaciones y respuesta preparada para la sustentación.

### RC-048 · 2026-09-30 · Fase 4–5 · E-CALIB: calibrar no mejora el modelo de alerta
- **Método:** RF-S3 con la configuración modal de I-3 bis; calibración Platt e isotónica DENTRO de cada pliegue externo (CV interna de 4 pliegues); CV-5 × 10 repeticiones.
- **Resultado:**
  - Sin calibrar: AUC-PR 0,751, Brier 0,111, ECE 0,076.
  - Isotónica: 0,734 / 0,112 / 0,085.
  - Platt: 0,725 / 0,118 / 0,078.
  - La probabilidad media sin calibrar (0,250) ya coincide con la prevalencia (0,2375).
- **Decisión:** por la regla pre-registrada (adoptar la calibración solo si reduce el Brier y el ECE sin perder más de 0,03 de AUC-PR), el modelo se despliega **sin calibrar**. Para D-APP se propone mostrar el **nivel** de alerta y no el decimal, porque la incertidumbre individual sigue siendo amplia (RC-043). Paquete: `modelos/alerta_art19.joblib`; niveles por regla: confirmado 0,63 (precisión 0,92, recall 0,63) y equilibrado 0,13 (recall 0,79, precisión 0,38).

### RC-049 · 2026-09-30 · Fase 4 · I-5d: comparación de algoritmos para la graduación (protocolo de I-3 bis)
- **Método:** S3, n = 90, 35 graduados (línea base 0,389), CV-5 × 10 anidada, mismas rejillas que I-3 bis.
- **Resultado (AUC-PR):** SVM 0,725 ± 0,033 · **RF 0,705 ± 0,021** · XGBoost 0,652 · Árbol 0,633 · Logística 0,614. SVM y RF empatan (Δ = 0,020, p = 0,394); SVM supera de forma significativa a XGBoost, al Árbol y a la Logística. AUC-ROC de RF: 0,812.
- **Decisión:** la regla de parsimonia elige **Random Forest**, el mismo algoritmo que para el art. 19. Se corrige la cifra del paper (XGBoost, AUC 0,853 con 18 variables y CV no anidada): bajo el protocolo estricto, el algoritmo seleccionado es RF y el AUC-ROC es 0,81. Paquete: `modelos/graduacion.joblib`.

### RC-050 · 2026-09-30 · Fase 3–4 · Corrige RC-039: con cortes bien definidos, el riesgo semestre a semestre (art. 20) no tiene señal
- **Motivación:** el panel de `longitudinal.py` numeraba los cortes incluyendo los intersemestrales y aplicaba el art. 20 sin el redondeo de su parágrafo.
- **Método:** panel corregido (`src/entrenar_mvp.py::panel_regular`), Sistemas + Electrónica (comparables, RC-036), Logística y RF con presupuesto equilibrado de 8 configuraciones cada uno, CV-5 × 10 anidada, cortes 1–3.
- **Resultado:** lift frente al azar de 1,09 / 0,93 / 1,27 para RF y de 1,03 / 0,89 / 1,03 para la Logística (AUC-ROC 0,40–0,58). Diagnóstico con RF fijo: la configuración de RC-039 (FCBI completa) reproduce 0,647 y 0,673, pero baja a 0,567 y 0,618 con Sistemas + Electrónica y a 0,565 y 0,524 con el panel corregido.
- **Decisión:** **no se despliega** un predictor semestral. TRAYECTA usa los indicadores normativos (arts. 19–21) para el seguimiento semestral y reserva la predicción para el cierre del primer semestre. El resultado negativo se declara.

### RC-051 · 2026-09-30 · Integridad · `src/curva_umbrales_art19.csv` no procede de un cálculo
- **Resultado:** el recall desciende exactamente 0,018 por paso, y su valor inicial (0,95) es imposible con 19 positivos. No coincide con la salida de `entrenar_principal.py` y no lo consumía ninguna pieza del proyecto.
- **Decisión:** el archivo se movió a `archivo/curva_umbrales_art19_NO_CALCULADA.csv`, con su nota. La cita de RC-023 a este archivo queda sin efecto.

### RC-052 · 2026-10-06 · Fase 3–4 · Variables excluidas de S3: ninguna mejora el modelo (incluida `repitio_escolar`)
- **Motivación:** los asesores reportaron buenos resultados con `repitio_escolar`. Nunca se había probado S3 + cada variable excluida, ni para el modelo de graduación.
- **Método:** pre-registro `docs/PREREGISTRO_EXP_VARIABLES_MONOTONIA.md`; script `src/exp_variables_monotonia.py`; resultados en `src/exp_variables_monotonia.csv`.
  - Etapa 1: cribado de S3 + cada una de las 13 variables, y S3 + las 13, con los hiperparámetros desplegados.
  - Etapa 2: validación anidada completa (protocolo de I-3 bis) para las variables con Δ ≥ +0,01, y siempre para `repitio_escolar`.
  - Las referencias anidadas S3 se toman de RC-033 y RC-049; la repetición 0 recalculada coincide al decimal.
- **Resultado (AUC-PR anidada):**
  - **Alerta:** S3 0,745; S3 + `repitio_escolar` 0,736 (Δ −0,009; p = 0,73). En el cribado, ninguna de las 13 variables superó a S3, y añadir las 13 juntas empeoró el modelo (−0,023; p Holm = 0,04).
  - **Graduación:** S3 0,705; + `repitio_escolar` 0,699 (Δ −0,006; p = 0,80); + `estrato` 0,740 (Δ +0,035; p = 0,078; p Holm = 0,23); + `cohorte` 0,728 (Δ +0,023; p = 0,46).
- **Decisión:** S3 se mantiene en ambos modelos. `repitio_escolar` se asocia en bruto con el desenlace, pero no aporta información sobre el promedio del 1.er semestre. `estrato` para graduación queda como hipótesis para validar con cohortes nuevas: supera el umbral de relevancia, pero no es significativo.

### RC-053 · 2026-10-06 · Fase 4–6 · Monotonía: forzarla en Saber 11 destruye la señal; forzarla solo en el promedio es gratis
- **Motivación:** en TRAYECTA, un perfil con promedio y Saber 11 altos recibía más riesgo que uno con promedio 1,8. Causa: en la muestra, los 7 estudiantes con Saber total > 350 no se graduaron, y varios perdieron la calidad de estudiante tras buenos primeros semestres (abandono sin cancelar, presumiblemente).
- **Método:** `monotonic_cst` de scikit-learn 1.8 en Random Forest, con validación anidada completa.
  - M1: riesgo no creciente en el promedio y en los 4 Saber.
  - M2: solo en el promedio.
- **Resultado:**
  - **M1 pierde mucho:** alerta 0,574 (Δ −0,171) y graduación 0,602 (Δ −0,103). La relación «Saber alto → peor desenlace» contiene señal consistente dentro de la muestra.
  - **M2 no pierde:** alerta 0,744 (Δ −0,001; p = 0,89); graduación 0,732 (Δ +0,028; p = 0,034 sin corregir).
  - Con M2 se elimina la subida espuria del riesgo con promedios altos (en la alerta, de 0,08 a 0,01 con promedio ≥ 4,2), pero el perfil de Saber alto sigue en 0,61.
- **Decisión:** por la regla pre-registrada (no perder más de 0,03), M2 es elegible para sustituir a ambos modelos. **Pendiente de aprobación del autor y posterior al CICI:** las cifras de la ponencia no cambian. La paradoja de Saber 11 no se corrige con restricciones sin perder la señal. Se documenta como hallazgo (posible deserción por traslado de estudiantes de alto rendimiento) y como límite de la herramienta, y se valida con las cohortes nuevas.
