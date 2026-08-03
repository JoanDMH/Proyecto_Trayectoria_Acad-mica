# PLAN OPERATIVO MULTIAGENTE — Ejecución detallada por objetivo
### Complemento operativo de `PLAN_DE_TRABAJO.md` (documento rector). Alineado a la propuesta de grado.
**Propósito:** permitir que múltiples agentes (humanos o de código) trabajen en paralelo y colaboren hasta culminar la propuesta. Cada paquete de trabajo (WP) tiene entradas, salidas, criterios de aceptación y dependencias explícitas.

---

## 0. PROTOCOLO DE COLABORACIÓN (leer antes de tocar nada)

### 0.1 Arranque obligatorio de todo agente
1. Leer `PLAN_DE_TRABAJO.md` (contexto, objetivos, visión SPADIES, brechas) y `README.md` (estructura, pipeline).
2. Leer este documento y reclamar UN paquete de trabajo (WP) libre respetando dependencias. **El reclamo se registra en `KANBAN_AGENTES.md`** (única fuente de estado): el agente pone su identificador, fecha y estado `EN CURSO` en la fila del WP **en su primer commit**. Un WP con agente asignado no se toca; si un WP lleva >7 días sin commits, cualquier agente puede liberarlo anotándolo.
3. Revisar `REGISTRO_CIENTIFICO.md` para no repetir experimentos ya realizados.

### 0.2 Reglas innegociables (heredadas de `PLAN_DE_TRABAJO.md` §7)
- Originales de `Datos/` intocables; correcciones solo vía `src/recodificacion.py` → `*_recod.xlsx` (respaldo: `Datos.zip`).
- SEED=42; métricas reportadas SIEMPRE por validación cruzada out-of-fold; nada de métricas in-sample.
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

```
OE1.1 (verif. datos E/B) ──┐
OE1.2 (verif. variables)  ─┼──> OE1.3 (target multiclase) ──> OE1.4 (snapshots) ──> OE1.5 (dataset FCBI final)
OE2.1 (auditoría modelos) ─┘                                                            │
OE2.2 (framework algoritmos) ────────────────────────────────────────────────┬──────────┘
                                                                             v
                                            OE2.3 (modelo principal) ──> OE3.1–OE3.5 (evaluación)
E4.1 (guía de redacción, arranca YA) ─── E4.2 (redacción por secciones, consume REGISTRO) ── E4.3 (cierre)
```
Paralelizables desde el día 1: OE1.1, OE1.2, OE2.1, OE2.2, E4.1.

---

## OBJETIVO ESPECÍFICO 1 — Caracterizar las trayectorias (CRISP-DM Fases 1–3)

> **Verificación explícita de las fases:** las Fases 1–3 están completas SOLO para Ing. de Sistemas y con targets binarios. Los WP siguientes verifican si hace falta más entendimiento/preprocesamiento y lo ejecutan. Nada se da por bueno sin re-verificación sobre los 3 programas.

### WP-OE1.1 — Verificación de comprensión de datos para Electrónica y Biología
- **Pregunta:** ¿lo aprendido sobre los datos de Sistemas (calidad, huecos, semántica) aplica igual a los otros 2 programas?
- **Tareas:**
  1. Auditar cobertura por programa: ¿caracterización tiene las mismas 147 columnas pobladas para E (95) y B (85)? Tasas de nulos por variable y por programa (tabla comparativa).
  2. Verificar llaves: cruce caracterización ∩ historial ∩ promedios por programa (¿cuántos se pierden y por qué?). Equivalente del caso 160004030 (invisibles en historial) en E/B.
  3. Verificar la clasificación de estado final por recencia en E/B (graduados/desertores/en formación por programa) y validar los 42 estados inferidos ya imputados.
  4. EDA comparativo entre programas: distribución de promedios, deserción, Saber 11, estrato — ¿los programas son mezclables en un modelo general o hay heterogeneidad fuerte?
  5. Revisar materias críticas por programa con `indice_materias.py` parametrizado (hallazgo de valor para el informe).
- **Salidas:** `Fase 2/08_verificacion_fcbi.md` + tablas CSV; entradas RC.
- **Aceptación:** decisión documentada "mezclables / no mezclables" con evidencia; inventario de exclusiones por programa con causa.

### WP-OE1.2 — Verificación del sentido de las variables (¿las 18 features son las correctas?)
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
- **Tareas:**
  1. Definición formal de las 4 clases (regla determinista sobre `historial_estados_recod` + recencia): `graduado`, `desertor` (formal o inferido), `activo`, `rezagado`.
  2. **Definir "rezagado" con la codirectora** (propuestas a evaluar empíricamente: (a) activo con > tiempo nominal sin graduarse; (b) avance de créditos < X % del esperado a su semestre; (c) graduado en > 12 semestres). Documentar la elegida y las descartadas.
  2-bis. **Regla de viabilidad pre-registrada (cierra la duda B):** tras construir la etiqueta se mide el tamaño de la clase `rezagado`. Si tiene **< 25 estudiantes en total o < 5 por fold esperado**, el target oficial **colapsa a 3 clases** (`graduado` / `desertor` / `activo`) y el rezago se maneja como **indicador secundario continuo** (avance de créditos vs. esperado, tarea de regresión o score descriptivo), manteniendo el modelo de riesgo de bajo rendimiento como señal operativa asociada. La decisión (4 vs 3 clases) se toma con esta regla ANTES de ver métricas de modelos, se valida con la codirectora y se registra en RC.
  3. Construir `trayectoria` para los 3 programas; tabla de distribución de clases por programa; análisis de desbalance y estrategia (pesos de clase preferible a SMOTE con n pequeño — decidir con evidencia).
- **Salidas:** función en `src/preprocessing.py`; columna en dataset maestro; `Fase 3/06_target_trayectoria.md`; entradas RC.
- **Aceptación:** cada estudiante del alcance tiene exactamente una clase; la regla es determinista y auditada contra 10 casos manuales.

### WP-OE1.4 — Diseño longitudinal (snapshots estudiante-semestre, visión SPADIES)
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
- **Tareas:** consolidar 3 programas + target multiclase + snapshots; imputaciones documentadas; split final (agrupado por estudiante); **versión anonimizada** (sin nombres, códigos hasheados) + diccionario de datos actualizado → paquete de entrega para el equipo investigador.
- **Salidas:** `src/df_master_fcbi.csv`, paquete `entrega_datos/` anonimizado, diccionario.
- **Aceptación:** E3 cerrado; un tercero entiende cada columna sin leer código.

---

## OBJETIVO ESPECÍFICO 2 — Implementar algoritmos de ML (CRISP-DM Fase 4)

### WP-OE2.1 — Revisión de los modelos actuales (verificación de Fase 4 existente)
- **Pregunta:** ¿los modelos preliminares (binarios + por materia) son correctos, reproducibles y qué papel juegan? (ya definido en `PLAN_DE_TRABAJO.md` §4.2-bis: preliminares/componentes, no E2).
- **Tareas:**
  1. Re-ejecutar `entrenar_materias.py` y `entrenar_principal.py` desde cero y confirmar que las métricas publicadas se reproducen exactamente (SEED).
  2. Auditoría anti-leakage independiente (agente distinto al que los construyó).
  3. Confirmar/refutar decisiones heredadas con los datos vigentes: sin SMOTE vs pesos de clase; umbral 0.29; grids de hiperparámetros (¿suficientemente amplios?).
  4. Documentar su rol final en el informe (preliminares que validaron pipeline + componente de riesgo de bajo rendimiento de la app).
- **Salidas:** acta de auditoría en `Fase 4/05_auditoria_modelos_preliminares.md`; entradas RC.
- **Aceptación:** reproducción exacta o discrepancias explicadas y corregidas.

### WP-OE2.2 — Framework de comparación completo (algoritmos de la propuesta)
- **Tareas:**
  1. Extender `entrenar_principal.py` (o `src/comparativa_algoritmos.py`) a los 5–6 candidatos de la propuesta: **regresión logística (baseline)**, árbol de decisión, Random Forest, **SVM**, XGBoost, MLP opcional.
  2. Pipelines correctos por familia: LogReg/SVM/MLP requieren `StandardScaler` DENTRO del pipeline de CV (los árboles no); SVM con `probability=True` o calibración para salidas probabilísticas.
  3. Soporte multiclase (nativo/softmax/OvR según algoritmo) y por-snapshot; grids documentados en `Fase 4/03_hiperparametros_seleccion.md`.
- **Salidas:** framework único que recibe (dataset, target) y produce la comparativa CSV estandarizada.
- **Aceptación:** correr el framework sobre el target binario actual reproduce los resultados conocidos de DT/RF/XGB (prueba de regresión) y añade LogReg/SVM.

### WP-OE2.3 — Modelo principal de trayectoria (candidato a E2)
- **Depende de:** OE1.3, OE1.4, OE1.5, OE2.2.
- **Tareas:**
  1. Entrenar los candidatos sobre el target multiclase FCBI (modelo general con `programa` como feature; variantes por programa como análisis de sensibilidad).
  2. Entrenar sobre snapshots (predicción al ingreso y por semestre).
  3. Modelo complementario de riesgo de bajo rendimiento extendido a FCBI (salida (c) de la visión SPADIES).
  4. Registrar TODOS los experimentos en RC (configuración → métricas), incluidos los perdedores.
- **Salidas:** `src/comparativa_trayectoria.csv` (algoritmo × clase × métrica × corte), modelos serializados.
- **Aceptación:** todos los candidatos evaluados con el mismo protocolo; ninguna configuración sin registrar.

---

## OBJETIVO ESPECÍFICO 3 — Evaluar, comparar y seleccionar (CRISP-DM Fase 5)

### WP-OE3.1 — Protocolo de evaluación
- Métricas por clase: Accuracy, Precision, Recall, F1 (por clase y macro), AUC-ROC (OvR por clase), matriz de confusión multiclase. **Calibración de probabilidades** (Brier score + curvas de calibración): imprescindible porque el producto entrega probabilidades (visión SPADIES) — una probabilidad mal calibrada es un producto engañoso.
- Variabilidad: media ± desviación entre folds; CV repetida (5×5) si el presupuesto de cómputo lo permite.
- **Salida:** `Fase 5/04_protocolo_evaluacion.md` (escrito ANTES de mirar resultados finales, para evitar sesgo de selección).

### WP-OE3.2 — Comparativa final y selección del ganador único
- Tabla única algoritmo × métricas; diferencias evaluadas con test apropiado (p. ej. McNemar sobre predicciones OOF o comparación por folds).
- Selección del **algoritmo ganador único** con criterio explícito declarado a priori (propuesto: F1-macro como primario por desbalance multiclase; AUC-OvR y calibración como desempate; interpretabilidad como criterio cualitativo final).
- **Selección con el diseño por cortes (WP-OE1.4):** la comparativa se ejecuta en cada corte modelable y el ganador se elige por **rango promedio entre cortes** (mejor posición media en F1-macro). Si hay empate o inversiones fuertes entre cortes, decide el **corte primario declarado a priori: fin de semestre 1** (máximo valor institucional — primera alerta accionable).
- **Salida:** decisión documentada → responde la pregunta problema. Entrada RC de máxima prioridad para el informe.

### WP-OE3.3 — Interpretación institucional
- Importancias + SHAP del ganador: factores asociados a permanencia, deserción y rezago (el "para qué" del OG).
- Curva de desempeño por corte semestral: ¿cuánto mejora la predicción con cada semestre de historia? (hallazgo central estilo SPADIES; ya sabemos que `prom_sem1` domina — verificar si se sostiene en multiclase).
- Validación con el equipo de investigación (codirectora): coherencia de los patrones con el conocimiento experto de la FCBI. Acta breve.
- **Salida:** `Fase 5/05_interpretacion_institucional.md`; figuras para el informe.

### WP-OE3.4 — Empaquetado del ganador y app (E2 + visión de producto)
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
   - Selección de variables: salida de WP-OE1.2 (ablation)
   - Target multiclase y rezago: salida de WP-OE1.3
   - Protocolo de evaluación y anti-leakage: `Fase 4/`, `Fase 5/04`
   - Experimentos: `REGISTRO_CIENTIFICO.md` (cada entrada RC con destino asignado DEBE aparecer en el informe)
2. Documentar la **naturaleza iterativa** de CRISP-DM con honestidad: el proyecto volvió de la Fase 4 a las Fases 2–3 (corrección del diccionario, recodificación) y eso mejoró los modelos — es un resultado metodológico valioso, no un desvío que ocultar.
3. Reproducibilidad explícita: semillas, particiones, scripts, versiones de librerías (una tabla), y la regla de originales intactos + transformaciones por script.

### E4.3 Redacción de resultados (el "qué" — justificado)
1. Cada resultado se presenta en tres tiempos: **hecho** (la cifra y su tabla/figura), **contexto** (frente a qué se compara: baseline, estado previo, literatura de la propuesta) y **lectura** (qué significa para la pregunta problema). Prohibido el "data dumping" de tablas sin lectura.
2. Reportar variabilidad siempre (± desviación entre folds); no afirmar superioridad de un algoritmo sin el respaldo del test de comparación (WP-OE3.2).
3. **Resultados negativos se publican:** pruebas no significativas (género, educación parental), configuraciones perdedoras, el AUC 0.69 previo de Matemáticas II y su corrección — construyen la credibilidad del trabajo.
4. El hallazgo "la calidad de los datos determinó el desempeño predictivo" (antes/después de la recodificación) se redacta como resultado de primer nivel, con su tabla comparativa.
5. Interpretación institucional en términos de gestión (factores de riesgo accionables), no solo métricas.

### E4.4 Redacción de conclusiones
1. **Responder literalmente la pregunta problema** (¿cuál algoritmo ofrece el mejor desempeño?) con el ganador, sus cifras y su margen sobre los demás.
2. Una conclusión por objetivo específico (OE1, OE2, OE3), verificable contra lo escrito en resultados — sin introducir información nueva.
3. Limitaciones honestas y concretas: tamaño muestral (~275), solo 2 cohortes, desbalance de género, estados imputados/inferidos (proporción exacta), validez externa limitada a la FCBI.
4. Trabajo futuro anclado en hechos del proyecto: integración con la plataforma del proyecto longitudinal (co-investigador), nuevas cohortes, monitoreo de deriva del modelo.
5. Cierre con la contribución: modelo + evidencia de factores + lección metodológica de calidad de datos.

### E4.5 Flujo de trabajo del agente redactor
1. Esperar la plantilla LaTeX del estudiante (no crear estructura propia).
2. Redactar por secciones consumiendo las fuentes del §E4.2; compilar localmente sin errores ni warnings de referencias.
3. Tablas generadas por script (CSV → LaTeX con booktabs) en `informe/tablas/`; figuras desde `figuras/`.
4. Revisión cruzada: otro agente verifica cifra por cifra contra los CSV fuente antes de dar por cerrada cada sección.

---

## CIERRE GLOBAL (criterio de culminación de la propuesta)

| Verificación | Evidencia |
|---|---|
| OE1 cumplido | Dataset FCBI (3 programas) con target de trayectoria + snapshots, variables justificadas empíricamente, E3 entregado anonimizado |
| OE2 cumplido | 5–6 algoritmos implementados con hiperparámetros configurados sobre el target de trayectoria |
| OE3 cumplido | Comparativa con métricas estándar + ganador único seleccionado y justificado + variables interpretadas |
| Pregunta problema respondida | Sección de conclusiones del informe |
| E1–E5 | Artículo sometido · modelo empaquetado + manual · dataset entregado · informe avalado · ponencia certificada |
| App (visión SPADIES) | Probabilidades de graduación/deserción/rezago + riesgo de bajo rendimiento, al ingreso y por semestre |
