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

<!-- Nuevas entradas debajo de esta línea. Formato en PLAN_OPERATIVO_AGENTES.md §0.3 -->
