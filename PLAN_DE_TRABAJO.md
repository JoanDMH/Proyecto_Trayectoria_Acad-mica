# PLAN DE TRABAJO — Modelo Predictivo de Trayectoria Académica FCBI
### Documento rector del proyecto de grado · Sustituye a "Propuesta de Proyecto de Grado.pdf" para consulta rápida
**Última actualización:** 2026-07-29 · **Estado global:** núcleo técnico completo para Ing. de Sistemas; pendiente extensión FCBI, target de trayectoria unificado, algoritmos baseline y entregables formales.

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

## 2. Problema y objetivos (de la propuesta)

**Pregunta problema:** ¿Cuál algoritmo de aprendizaje automático ofrece el mejor desempeño predictivo de la trayectoria académica de los estudiantes de la FCBI?

**Objetivo general (OG):** Comparar algoritmos de aprendizaje automático para la predicción de la trayectoria académica de los estudiantes de la FCBI, con el fin de apoyar la identificación de factores asociados a la permanencia, el riesgo de deserción y el rezago.

**Objetivos específicos:**

- **OE1 — Caracterizar** las trayectorias consolidando un conjunto de datos académicos y sociodemográficos de las cohortes 2017-2 y 2018-1 de la FCBI (comprensión, integración, limpieza, transformación).
- **OE2 — Implementar** algoritmos de ML para modelar la trayectoria, configurando hiperparámetros.
- **OE3 — Evaluar y comparar** los modelos con métricas estándar de clasificación, seleccionar el de mayor capacidad predictiva e interpretar las variables más relevantes para la gestión institucional.

**Definiciones de la propuesta a tener presentes:**

- **Variable objetivo propuesta:** estado académico al final del seguimiento — **graduado, activo, desertor, rezagado** (multiclase).
- **Algoritmos candidatos propuestos:** regresión logística (línea base), árbol de decisión, Random Forest, SVM, XGBoost; redes neuronales opcional.
- **Alcance:** programas de la FCBI (los datos disponibles cubren Ing. de Sistemas, Ing. Electrónica, Biología y Lic. en Matemáticas).
- **Despliegue:** la integración completa en la plataforma del proyecto longitudinal es *trabajo futuro*; este proyecto entrega el modelo empaquetado + manual técnico de integración. La app Streamlit actual es un **prototipo provisional**.

## 3. Entregables comprometidos (Tabla 7 de la propuesta)

| # | Producto | Meta | Estado |
|---|---|---|---|
| E1 | Artículo académico (revista indexada Cat. B/C, estilo revista BI) | 1 | 🔴 No iniciado |
| E2 | Modelo ML entrenado, validado y **empaquetado** + pipeline documentado e integrable (repo GitHub + **manual técnico de integración**) | 1 | 🟡 Modelos y repo listos; falta manual técnico formal |
| E3 | Conjunto de datos procesado y listo para modelado (archivo + **diccionario documentado**) | 1 | 🟢 Casi completo (df_master + recod + diccionario Fase 2; falta empaquetado formal de entrega) |
| E4 | Documento final del trabajo de grado (informe final EPI) avalado | 1 | 🟡 Informes por fase listos; falta consolidar informe final (existía Informe.tex IEEE, hoy fuera del repo) |
| E5 | Ponencia en evento científico nacional/internacional | 1 | 🔴 No iniciado |

## 4. Estado actual del proyecto (qué está HECHO)

### 4.1 Datos y preparación (OE1 — ~90 % para Sistemas, base lista para FCBI)

- **Fuentes:** 6 archivos de la Oficina de Sistemas en `Datos/` (caracterización 337×147, detalle_materias 8 503, historial_estados 1 968, promedios, homologaciones). Respaldo prístino en `Datos.zip`. **Los originales nunca se modifican.**
- **Recodificación reproducible** (`src/recodificacion.py`, validada con la Oficina de Sistemas y auditada):
  - Diccionario `OBSERVACION` corregido: `C`=curso intersemestral (antes se creía "cancelada"), `A`/`P`=trámite de grado aprobado/no aprobado, `R`/`E`=vacías no recientes/en curso, `V`=validada. Notas válidas: {N, C, H}.
  - `historial_estados_recod.xlsx`: 2 566 filas = 1 968 originales intactas + 541 imputaciones trazables (MATRICULADO donde hubo cursos sin estado; NO MATRICULADO en truncamientos; 2020-2→NO REALIZO PAGO por pandemia) + **57 estados finales inferidos** (criterios 3.1 actividad real, 3.2 sin actividad ≥2024-1, 3.3 BR≥1→RETIRADO BR / NRP≥2→NO RENOVACIÓN; Sistemas 15, Electrónica 15, Biología 27). Regla anti-residuo: nada se imputa tras un estado terminal original.
  - `detalle_materias_recod.xlsx`: 8 486 filas (se eliminan 17 trámites fantasma post-graduación; +76 registros con nota recuperados para el análisis).
- **Dataset de modelado (Sistemas):** `src/df_master_limpio.csv`, n=90, 18 features, targets `rendimiento_bajo` (38/90) y `graduado` (35/90). Split 72/18 estratificado (`train_test_split.json`, SEED=42).
- **EDA completo** (Fase 2): perfil sociodemográfico, clasificación por recencia (35 graduados / 59 desertores / 1 en formación; deserción 62.1 %), semestres truncados, homologaciones/traspasos, materias críticas.

### 4.2 Modelado y evaluación (OE2/OE3 — completo para Sistemas, targets binarios)

Todo por **CV-5 estratificada out-of-fold, SEED=42, sin SMOTE, sin fugas** (anti-leakage documentado):

| Modelo | Algoritmo ganador | Métricas clave (CV-5, n=90) |
|---|---|---|
| Rendimiento bajo | Random Forest (umbral 0.29 pro-Recall) | **Recall+ 0.816**, AUC 0.752 |
| Graduación | XGBoost (umbral 0.50) | **AUC 0.853**, F1-mac 0.764 |
| Reprobación por materia (5 críticas) | Random Forest | F1-w 0.785–0.928, AUC 0.865–0.939 |

- Materias críticas (índice 0.70·reprobación + 0.30·repitencia): Matemáticas II, Física I, Álgebra Lineal, Matemáticas I, Fund. de Programación.
- Variable dominante: `prom_sem1` (40.4 % en RF) → alerta temprana al primer semestre.
- Comparativa DT/RF/XGB documentada (`Fase 4/`), pruebas estadísticas (género, edu. padres, repitencia: no significativas), impacto antes/después de la recodificación (`Fase 5/03`).

### 4.3 Prototipo de despliegue

- `app.py` (Streamlit, desplegada en Streamlit Cloud): KPIs, EDA interactivo, comparativa de modelos, gauge Recall+, modelos por materia, predictor interactivo. Lee métricas dinámicamente de los CSVs de `src/`.

## 5. Brechas frente a la propuesta (qué FALTA)

| # | Brecha | Detalle |
|---|---|---|
| B1 | **Alcance FCBI incompleto** | Todo el modelado es de Ing. de Sistemas. Faltan Electrónica y Biología (y decidir si Lic. Matemáticas): modelos por programa o modelo general FCBI. La recodificación ya cubre los 4 programas (parametrizada). |
| B2 | **Target de trayectoria multiclase** | La propuesta define el target como estado final: *graduado / activo / desertor / rezagado*. Hoy existen dos binarios. El historial recodificado + estados inferidos + regla de recencia ya permiten construir la etiqueta multiclase (falta definir "rezagado": p. ej. activo con avance < créditos esperados, o graduado en > tiempo nominal). |
| B3 | **Algoritmos baseline faltantes** | La propuesta compara: regresión logística (baseline), DT, RF, SVM, XGBoost (+NN opcional). Faltan **regresión logística y SVM** en la comparativa (y decidir NN). |
| B4 | **Informe final (E4)** | Consolidar el informe EPI. El `Informe.tex` (IEEE) salió del repo; recuperarlo o reconstruirlo con las cifras vigentes (las de este documento). |
| B5 | **Artículo científico (E1)** | No iniciado. Estilo revista BI, categoría B/C. Insumo listo: hallazgo del impacto de la calidad de datos (Fase 5/03) + comparativa de algoritmos. |
| B6 | **Ponencia (E5)** | No iniciada. Existe presentación .pptx (v2) con cifras parcialmente desactualizadas — usarla de base. |
| B7 | **Manual técnico de integración (E2)** | Falta documento formal: contrato de entrada/salida del modelo, serialización (joblib), versiones, ejemplo de integración para la plataforma del proyecto longitudinal. |
| B8 | **Empaquetado formal del dataset (E3)** | Falta paquete de entrega: dataset procesado + diccionario + licencia/anonimización para el equipo investigador. **Atención privacidad:** los archivos actuales contienen nombres; el paquete de entrega debe anonimizarse. |
| B9 | **Exploración Power BI** | La propuesta menciona Power BI en la Etapa 1. Se cubrió con Python/Streamlit; documentar la sustitución justificada (o generar un tablero PBI mínimo si los evaluadores lo exigen). |
| B10 | **Notebooks desactualizados** | `Fase 2/05_eda_notebook.ipynb` y `Fase 5/02_evaluacion_modelo.ipynb` tienen salidas previas a la recodificación (n=89); re-ejecutar. Igual `src/save_evaluation_plots.py` para regenerar figuras con n=90. |

## 6. Plan incremental (hitos)

> Orden diseñado para que cada hito deje el proyecto en estado defendible. Los hitos H1–H3 cierran el núcleo científico (OG/OE); H4–H6 cierran los entregables formales.

### H1 — Consolidar la base actual (deuda técnica) — *corto*
1. Re-ejecutar notebooks de Fase 2 y Fase 5 con datos recodificados (n=90) y regenerar figuras (`save_evaluation_plots.py`).
2. Commit/push de toda la recodificación + reboot de la app en Streamlit Cloud.
3. Actualizar `Presentacion_..._v2.pptx` con métricas vigentes (tabla §4.2).
- **Criterio de cierre:** cero cifras desactualizadas en repo y app.

### H2 — Target de trayectoria unificado (B2) — *núcleo conceptual*
1. Definir formalmente las 4 clases con las reglas ya validadas: `graduado` (estado GRADUADO), `desertor` (retiro formal o inferido / sin actividad reciente), `activo` (actividad ≥2024-1), `rezagado` (definir umbral: sin graduarse dentro del tiempo nominal +X semestres, o avance de créditos < esperado).
2. Construir la etiqueta para los 4 programas desde `historial_estados_recod` + `detalle_materias_recod` (función nueva en `preprocessing.py`).
3. Documentar distribución de clases por programa y decidir estrategia de desbalance.
- **Criterio de cierre:** columna `trayectoria` en el dataset maestro FCBI, documentada en Fase 3.

### H3 — Comparativa completa de algoritmos a escala FCBI (B1+B3) — *responde la pregunta problema*
1. Extender `preprocessing.py` a los 4 programas (features comunes; validar disponibilidad de caracterización por programa).
2. Añadir **regresión logística** (baseline) y **SVM** a `entrenar_principal.py`; opcional MLP. Mantener CV-5 OOF, SEED=42.
3. Entrenar: (a) modelo general FCBI (target multiclase de H2, con `programa` como feature) y (b) modelos por programa si el general no discrimina bien.
4. Comparativa final de 5–6 algoritmos × métricas (Accuracy, Precision, Recall, F1 por clase, AUC-ROC por clase) + interpretación de variables (importancias/SHAP).
- **Criterio de cierre:** tabla comparativa que responde explícitamente "¿cuál algoritmo ofrece el mejor desempeño?" — el corazón del OG.

### H4 — Empaquetado y manual técnico (B7+B8 → E2+E3) — *transferencia*
1. Paquete del modelo: `joblib` versionado + `predict()` de referencia + contrato JSON de entrada/salida + versiones de dependencias.
2. `MANUAL_TECNICO_INTEGRACION.md`: pipeline, artefactos, ejemplo de consumo (para la plataforma del co-investigador).
3. Paquete de datos para el equipo investigador: dataset procesado **anonimizado** + diccionario.
- **Criterio de cierre:** un tercero puede cargar el modelo y predecir sin leer el código fuente.

### H5 — Informe final EPI (B4 → E4) — *documento de grado*
1. Recuperar/reconstruir el informe (formato EPI/IEEE) integrando: contexto y marco (de la propuesta), Fases 2–5 actualizadas, comparativa H3, impacto de la recodificación, limitaciones (n pequeño, 2 cohortes, desbalance de género) y trabajo futuro (integración plataforma, nuevas cohortes).
2. Revisión con directora y codirectora → ajustes → aval.
- **Criterio de cierre:** documento avalado por jurados y directora.

### H6 — Divulgación (B5+B6 → E1+E5) — *productos académicos*
1. Artículo (estilo revista BI, Cat. B/C): ángulo sugerido — *comparación de algoritmos de ML para trayectoria académica en programas STEM con corrección de calidad de datos como factor determinante del desempeño predictivo*.
2. Ponencia: derivar del artículo; postular a evento nacional/internacional; actualizar la presentación existente.
- **Criterio de cierre:** artículo sometido + certificado de aceptación/participación en evento.

## 7. Convenciones técnicas obligatorias (para cualquier agente que retome)

1. **Nunca modificar los `.xlsx` originales de `Datos/`** (respaldo en `Datos.zip`). Toda corrección se codifica en `src/recodificacion.py` y se regeneran los `*_recod.xlsx`.
2. **Reproducibilidad:** SEED=42 en todo; CV-5 estratificada out-of-fold para métricas reportadas; sin SMOTE (desbalance leve, justificado en Fase 4).
3. **Anti-leakage:** `PROMEDIO_CARRERA` solo en target; `prom_global` excluye la materia objetivo; `nota_mat1` fuera del modelo de Matemáticas I; nada del futuro del estudiante en las features.
4. **Estados originales del historial son la norma**; las imputaciones llevan `ORIGEN` trazable y color en el xlsx.
5. **Umbrales operativos:** 0.29 (rendimiento_bajo, prioriza Recall+ para alertas), 0.50 (graduado).
6. La app lee métricas de `src/*.csv` — tras re-entrenar, **no** editar métricas a mano en `app.py` (solo textos narrativos).
7. Flujo de ejecución completo: ver `README.md`.

## 8. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Muestra pequeña por programa (~90) debilita el modelo multiclase | Modelo general FCBI (n≈360) con `programa` como feature; reportar por-clase con IC |
| Clase "rezagado" ambigua | Definirla con la codirectora (experticia en trayectoria) antes de H3 |
| Datos con nombres (privacidad) | Anonimizar todo paquete que salga del repo (E3); el repo es privado |
| Corrupción de archivos xlsx (ocurrió 2 veces) | `Datos.zip` intacto + todo regenerable por script |
| Cifras desactualizadas entre documentos | Fuente única: CSVs de `src/`; este plan es el documento rector |
