# KANBAN DE AGENTES — Estado de los paquetes de trabajo
### Única fuente de verdad sobre quién trabaja en qué. Ver protocolo en `PLAN_OPERATIVO_AGENTES.md` §0.1

**Cómo reclamar un WP:** edita tu fila poniendo tu identificador de agente, la fecha y estado `EN CURSO`, e inclúyelo en tu **primer commit** del WP. Un WP con agente asignado no se toca. Si un WP lleva **>7 días sin commits**, cualquier agente puede liberarlo (estado `LIBRE` + nota en Historial).

> **Estado a 2026-09-29.** Revisado contra la realidad del proyecto: se cerraron siete WP que figuraban como LIBRE pero ya estaban ejecutados (I-5a, I-5b, WP-OE1.2, WP-OE2.1, WP-OE2.2, WP-OE3.1), y se abrieron los que salieron de la auditoría de septiembre. **Lo que bloquea el avance no es código: son cinco decisiones de la dirección.** Ver `PROBLEMAS_DETECTADOS.txt`, bloque 5.

**Estados válidos:** `LIBRE` · `EN CURSO` · `EN REVISIÓN` (espera verificación cruzada de otro agente) · `BLOQUEADO(motivo)` · `HECHO(commit)`

| WP | Descripción corta | Depende de | Estado | Agente | Fecha reclamo | Último commit |
|---|---|---|---|---|---|---|
| **— CERRADOS —** | | | | | | |
| I-1 | Definir target de rendimiento (art. 19 re-derivado) | — | **HECHO(RC-017)** | auditor | 2026-09-02 | — |
| I-2 | Corregir imputación de `prom_sem1` (indicador `sin_primer_semestre`) | I-1 | **HECHO(RC-018)** | agente-preprocesamiento | 2026-09-03 | — |
| I-2b | Implementar el target del art. 19 + marcar `rendimiento_bajo` obsoleto | I-2 | **HECHO(RC-020)** | auditor | 2026-09-03 | — |
| I-3 | Comparar los 5 algoritmos con el target nuevo | I-1, I-2, I-2b | **HECHO(RC-023)** | Joan | 2026-09-03 | — |
| I-4 | Retirar modelos de reprobación de `src/`, `app.py` y documentos | — | **HECHO(RC-022)** | auditor | 2026-09-03 | — |
| I-5a | Selección de variables (permutación + VIF + ablación) | I-3 | **HECHO(RC-030)** | Joan | 2026-09-15 | — |
| I-5a2 | Selección **anidada**: sesgo medido en +0,150 AUC-PR; conjunto definitivo S3 | I-5a | **HECHO(RC-032)** | auditor | 2026-09-15 | — |
| I-5b | Diagnóstico del error (brecha, curva de aprendizaje, .632+, regularización) | I-3 | **HECHO(RC-026…RC-029)** | Joan | 2026-09-15 | — |
| I-5c | I-3 bis · art. 19: 5 de 5 modelos. Gana Random Forest 0,745 sin desviar el protocolo | I-5a2, I-5b | **HECHO(RC-033)** | Joan | 2026-09-15 | — |
| I-5e | Verificación FCBI: 3 programas, target aplicable, cortes 1-3 viables | I-5c | **HECHO(RC-036)** | auditor | 2026-09-15 | — |
| WP-OE1.1 | Verificación de datos Electrónica/Biología | — | **HECHO(RC-036)** | auditor | 2026-09-15 | — |
| WP-OE1.2 | Verificación de variables + ablación | — | **HECHO(RC-032, RC-042)** | auditor | 2026-09-29 | — |
| WP-OE1.3 | Target multiclase — **INVIABLE por RC-008** (ACTIVO n=5 / n=20). Se adopta binario | OE1.1 | **HECHO(RC-041)** | auditor | 2026-09-16 | — |
| WP-OE1.4 | Snapshots longitudinales — **CERRADO**: el art. 19 es agudo, los acumulados no lo anticipan | OE1.1 | **HECHO(RC-038)** | auditor | 2026-09-15 | — |
| WP-OE2.1 | Auditoría de modelos preliminares | — | **HECHO(AUDITORIA_2026-09)** | auditor | 2026-09-02 | — |
| WP-OE2.2 | Framework de comparación (LogReg, DT, RF, SVM, XGB) | — | **HECHO(RC-033)** | Joan | 2026-09-15 | — |
| WP-OE3.1 | Protocolo de evaluación pre-registrado | — | **HECHO(RC-021, ESPEC_I3)** | auditor | 2026-09-03 | — |
| A-PCA | PCA como respaldo de la selección (encargo del asesor) | I-5a2 | **HECHO(RC-042)** | auditor | 2026-09-29 | — |
| B-BAYES | Modelos bayesianos + posterior de coeficientes (encargo del asesor) | I-5c | **HECHO(RC-043)** | auditor | 2026-09-29 | — |
| C-POCOS | Few-shot tabular y curva de tamaño muestral (encargo del asesor) | I-5c | **HECHO(RC-044)** | auditor | 2026-09-29 | — |
| **— ABIERTOS: decisión de la dirección —** | | | | | | |
| D-REGIMEN | **Decidir el régimen normativo de las etiquetas** (Acuerdo 015/2003 vs reglamento 2022) — P6 | — | **LIBRE** ⚠ crítico | — | — | — |
| D-MULTI | Formalizar la sustitución del target multiclase comprometido (modifica E2) — P7 | WP-OE1.3 | **LIBRE** ⚠ | — | — | — |
| D-ALCANCE | Decidir: un modelo FCBI o tres por programa (modifica E2) — P15 | WP-OE1.5 | **LIBRE** ⚠ | — | — | — |
| D-COLIN | Decidir tratamiento de la colinealidad SABER-total (VIF 6,7) — P16 | B-BAYES | **LIBRE** ⚠ | — | — | — |
| D-APP | Decidir qué muestra la app: calibrar o retirar el porcentaje — P17 | B-BAYES | **LIBRE** ⚠ | — | — | — |
| **— ABIERTOS: ejecutables ya —** | | | | | | |
| E-CALIB | Calibrar las probabilidades (isotónica/Platt dentro del pliegue externo) — P17 | D-APP | **HECHO(RC-048)** · calibrar no mejora | Claude | 2026-09-30 | — |
| E-SIMULT | Declarar en el informe el 42 % de eventos simultáneos (44 % en la FCBI) y reportar 0,745 y 0,473 — P19 | — | **LIBRE** | — | — | — |
| E-EMBUDO | Documentar el embudo de poblaciones (275 → 262 → 234 → 80) y qué población usa cada target | — | **LIBRE** | — | — | — |
| E-ART20 | Redefinir el target longitudinal al art. 20 (+0,20 AUC-ROC medido) — PLAN_MEJORAS P2 | WP-OE1.4 | **HECHO(RC-050)** · negativo: sin señal con cortes corregidos | Claude | 2026-09-30 | — |
| E-PEOR | Incorporar la variable `peor_periodo` (p=0,011 / 0,008) — PLAN_MEJORAS P3 | — | **LIBRE** | — | — | — |
| I-5d | I-3 bis sobre el target `graduado` (n=90) con el mismo protocolo | I-5c | **HECHO(RC-049)** · RF por parsimonia (empata con SVM) | Claude | 2026-09-30 | — |
| WP-OE1.5 | Paquete anonimizado del dataset (E3). El `df_master_fcbi.csv` ya está | OE1.2–OE1.4 | **PARCIAL(RC-037)** | — | 2026-09-15 | — |
| EQ-PLANES | Capa de equivalencias plan 2011 ↔ 2018 + pruebas | — | **HECHO(RC-046)** | Claude | 2026-09-30 | — |
| MVP-E5 | TRAYECTA (software de trayectoria) + modelos empaquetados + ponencia CICI | RC-046…RC-050 | **HECHO** (`trayecta/`, `modelos/`) | Claude | 2026-09-30 | — |
| F-ELEC-EQ | Solicitar la resolución de equivalencias de Electrónica (planes 612/613) | — | **LIBRE** | — | — | — |
| **— BLOQUEADOS —** | | | | | | |
| F-EXTERNA | **Validación externa en cohortes nuevas** — P18, la limitación más seria | datos nuevos | **BLOQUEADO(petición cursada 29-09 a la Of. de Sistemas)** | — | — | — |
| F-ANOMAL | Consultar las anomalías del extracto (estudiante 160004036; art. 46) — P20 | Of. de Sistemas | **BLOQUEADO(misma petición)** | — | — | — |
| WP-OE2.3 | Modelo principal de trayectoria por corte | E-ART20 | **BLOQUEADO(el diseño por cortes fracasa con el art. 19; requiere D-REGIMEN + E-ART20)** | — | — | — |
| WP-OE3.2 | Comparativa final + ganador único entre cortes | WP-OE2.3 | **BLOQUEADO** | — | — | — |
| WP-OE3.3 | Interpretación institucional (SHAP, curva por corte) | WP-OE3.2, D-COLIN | **BLOQUEADO(SHAP no es interpretable hasta resolver P16)** | — | — | — |
| WP-OE3.4 | Paquete de inferencia + manual + app (E2) | WP-OE3.2, E-CALIB | **BLOQUEADO** | — | — | — |
| E4.1 | Guía de estilo aplicada / preparación del informe | plantilla del estudiante | **BLOQUEADO(esperando plantilla LaTeX)** | — | — | — |
| E4.2 | Redacción por secciones (consume REGISTRO_CIENTIFICO) | E4.1 + WPs fuente | **BLOQUEADO** | — | — | — |
| E4.3 | Cierre: verificación cifra por cifra + compilación limpia | E4.2 | **BLOQUEADO** | — | — | — |

## Historial de cambios de estado

| Fecha | WP | Cambio | Agente | Nota |
|---|---|---|---|---|
| 2026-09-29 | — | **REVISIÓN DEL TABLERO** — 7 WP cerrados que figuraban LIBRE sin estarlo; 12 abiertos nuevos desde la auditoría; identificadas 5 decisiones de dirección como cuello de botella real | auditor | Preparación del envío a otro investigador |
| 2026-09-29 | A-PCA | **HECHO** — el PCA no respalda la selección y se demuestra: destruye 0,37 de AUC-PR; la variable más predictiva vive en CP3 (8,3 % de varianza) | auditor | RC-042 |
| 2026-09-29 | B-BAYES | **HECHO** — ningún bayesiano supera a RF, pero la posterior destapa colinealidad en SABER 11 (VIF 6,7) y el 54 % de casos con IC > 0,30 | auditor | RC-043 |
| 2026-09-29 | C-POCOS | **HECHO** — few-shot no trasladable sin corpus; curva de tamaño: duplicar la muestra ≈ +0,05 AUC-PR, techo 0,838 | auditor | RC-044 |
| 2026-08-03 | — | Tablero creado; todos los WP en LIBRE salvo E4.1 (espera plantilla) | coordinador | — |
| 2026-09-02 | — | Auditoría metodológica (`AUDITORIA_2026-09.md`); RC-012 a RC-017 | auditor | Target de rendimiento sustituido; modelos por asignatura retirados |
| 2026-09-02 | I-1 | **HECHO** — target definitivo aprobado (art. 19 del reglamento vigente, re-derivado) | auditor | RC-017 |
| 2026-09-03 | I-2 | **HECHO** — esquema dual: indicador `sin_primer_semestre` + imputación mediana | agente-preprocesamiento | RC-018 (`df_master_limpio.csv` 90x31) |
| 2026-09-03 | I-2 | **VERIFICADO** — cifras confirmadas; indicador empíricamente neutro; abre I-2b | auditor | RC-019 |
| 2026-09-03 | I-2b | **HECHO** — target art. 19 en el pipeline; corregida colisión de periodos `-0`/`-2`; población n=80 | auditor | RC-020 (19 positivos, 0 dudosos) |
| 2026-09-03 | I-3 | **PREPARADO** — `ESPEC_I3.md` + `src/comparacion_estadistica.py`; detectado sesgo por CV no anidada | auditor | RC-021 (protocolo anidado obligatorio) |
| 2026-09-03 | I-4 | **HECHO** — modelos por asignatura retirados de código, app y documentos; índice de criticidad conservado | auditor | RC-022 (artefactos apartados en archivo/) |
| 2026-09-15 | I-5c | **HECHO** — I-3 bis art.19: RF 0,745 gana sin desviar el protocolo; XGBoost recupera +0,102 al equilibrar rejillas | Joan | RC-033 |
| 2026-09-15 | WP-OE1.1 | **HECHO** — FCBI verificada: 59 positivos de 234; Biología distinta y censurada; cortes 1-3 habilitados | auditor | RC-036 |
| 2026-09-15 | WP-OE1.5 | **PARCIAL** — dataset FCBI construido; modelos SEPARADOS por programa superan al conjunto (Δ=-0,031) | auditor | RC-037 |
| 2026-09-15 | WP-OE1.4 | **HECHO** — diseño longitudinal refutado: el art. 19 es un evento AGUDO; los promedios acumulados no lo anticipan | auditor | RC-038 |
| 2026-09-15 | — | **DIAGNÓSTICO** — el fracaso es del TARGET, no de los datos: ampliar el umbral sube AUC-ROC de 0,47 a 0,67 | auditor | RC-039 |
| 2026-09-16 | WP-OE1.3 | **HECHO** — target multiclase declarado INVIABLE con la regla pre-registrada; requiere consulta con la dirección | auditor | RC-041 |
| 2026-09-03 | I-3 | **HECHO** — CV-5 anidada (15 reps); empate técnico a 3 bandas (SVM ≈ RF ≈ LogReg); Random Forest retenido | Joan | RC-023 (comparativa y matrices en `src/`) |
