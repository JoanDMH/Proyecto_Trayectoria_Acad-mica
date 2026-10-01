# Impacto de la Recodificación de Datos: Antes vs. Después

> ## ⚠️ DOCUMENTO DE FASE — sus cifras corresponden al target SUSTITUIDO
>
> Este informe documenta lo que se hizo y se midió **en su momento**, con la variable
> objetivo `rendimiento_bajo` (`PROMEDIO_CARRERA < 3,0`) y, donde aparezcan, con los
> modelos de reprobación por asignatura. **Ambos fueron retirados después:**
>
> | Lo que dice este documento | Estado actual |
> |---|---|
> | Target `PROMEDIO_CARRERA < 3,0` | **Descartado por tautológico** (RC-012, RC-017). Sustituido por el derivado del **artículo 19** |
> | Recall+ 0,816 · AUC 0,752 | El modelo vigente es Random Forest con **AUC-PR 0,745 ± 0,025** sobre n=80 (RC-033, RC-045) |
> | Modelos de reprobación por asignatura (AUC 0,865–0,939) | **Retirados por fuga temporal** (RC-013, RC-022). Solo sobrevive el índice descriptivo de criticidad |
> | 18 variables · umbral único 0,29 · CV-5 simple | 6 variables (S3) · esquema de tres niveles · **CV-5 anidada** × 10 repeticiones |
>
> **No se reescribe**: narra la iteración de CRISP-DM y es parte del expediente del trabajo.
> Para el estado vigente: `PLAN_DE_TRABAJO.md`, `PROBLEMAS_DETECTADOS.txt` y `REGISTRO_CIENTIFICO.md`.

## CRISP-DM · Universidad de los Llanos · Ing. de Sistemas · Cohortes 2017-2 y 2018-1

> ## ⛔ AVISO — MODELOS POR ASIGNATURA RETIRADOS (I-4 · RC-013 / RC-022)
> Las métricas de los **modelos de reprobación por asignatura** que aparecen en este
> documento (AUC 0,865–0,939, F1-w 0,79–0,93) **quedan invalidadas por fuga temporal**:
> el predictor `prom_global` es el promedio del estudiante en el resto de la carrera y
> entre el 70 % y el 83 % de esa información proviene de semestres **posteriores** a la
> asignatura que se predice. El desempeño honesto es AUC 0,70–0,74.
>
> El **índice de criticidad** (ranking de asignaturas) **no está afectado**: es un
> indicador descriptivo, no un modelo. Sigue siendo válido.
>
> Este documento se conserva como registro histórico de la fase. Ver
> `AUDITORIA_2026-09.md` §3 antes de reutilizar cualquier cifra.

> **Propósito.** Este documento explica, detalla y justifica cómo las correcciones aplicadas a los datos fuente —validadas con la Oficina de Sistemas (jul-2026) y aprobadas por auditoría— aumentaron la calidad descriptiva y predictiva del estudio. Todas las transformaciones son reproducibles con `src/recodificacion.py`; ninguna cifra proviene de edición manual de resultados.

---

## 1. El origen del problema: un diccionario mal documentado

La cadena causal del bajo desempeño previo de los modelos no estaba en los algoritmos, sino en la **interpretación errónea del diccionario de datos**:

| Elemento | Interpretación anterior (errónea) | Interpretación corregida (Oficina de Sistemas) |
|---|---|---|
| `OBSERVACION = C` | "Cancelada" → **se excluía** del análisis | **Curso intersemestral** → nota real, puede reprobarse |
| `OBSERVACION` vacía con nota | "Sin registro" → **se excluía** | Curso normal (`N`) → nota real válida |
| `OBSERVACION = V` | "Vacía" | Validada (nota externa) |
| `OBSERVACION = TG` | Categoría única | Se desdobla en `A` (aprobado) / `P` (no aprobado) |
| `historial_estados_` | Se asumía completo | **Deficiente**: omite matrículas tempranas y estudiantes enteros |

Consecuencia directa: el pipeline anterior **descartaba registros académicos reales** y trabajaba con historias incompletas. Los modelos no eran malos; estaban **ciegos a una parte de la realidad**.

## 2. Recuperación de datos (Fase 2) — antes vs. después

### 2.1 Registros con nota válidos para el análisis (Ing. de Sistemas)

| Indicador | Antes | Después | Δ |
|---|---|---|---|
| Registros con nota válidos | 2 448 | **2 524** | **+76 (+3.1 %)** |
| — Vacías con nota recuperadas (→ `N`) | 0 | 61 | +61 |
| — Cursos intersemestrales (`C`) incluidos | 0 | 15 | +15 |
| Registros fantasma post-graduación | 17 | **0** | −17 eliminados |

Un 3.1 % puede parecer poco, pero esos 76 registros **no estaban distribuidos al azar**: se concentraban en los periodos y materias donde los estudiantes resolvían su situación académica (recuperaciones de 2019-1 e intersemestrales de enero). Eran, precisamente, los desenlaces que faltaban.

### 2.2 Población de modelado

| Indicador | Antes | Después |
|---|---|---|
| Muestra de modelado | N = 89 | **N = 90** |
| Exclusiones | 6 (5 sin actividad + 1 "sin historial") | **5** (solo sin actividad real) |
| Target `rendimiento_bajo` | 37 (41.6 %) | 38 (42.2 %) |

El estudiante recuperado (160004030) estaba excluido **por un defecto del archivo, no por una decisión metodológica**: cursó 6 materias en 2017-2 con promedio 2.9, pero el historial original lo omitía por completo. Se verificó que todas sus features clave son reales (no imputadas) y aporta un caso positivo verídico del perfil que el modelo debe detectar.

### 2.3 Materias críticas: estadísticas descriptivas más realistas

| Materia | Tasa reprobación (antes) | Tasa reprobación (después) | N (antes → después) |
|---|---|---|---|
| Matemáticas II | 44.0 % | **31.5 %** | 52 → 54 |
| Física I | 26.0 % | 27.8 % | 53 → 54 |
| Álgebra Lineal | 29.0 % | 29.2 % | 72 → 72 |
| Matemáticas I | 26.0 % | 26.0 % | 73 → 73 |
| Fund. de Programación | 21.0 % | 20.8 % | 72 → 72 |

**La caída de Matemáticas II (44 % → 31.5 %) no es una pérdida de criticidad: es la corrección de un sesgo.** Al excluir los intersemestrales y las notas sin observación, el pipeline anterior ignoraba justamente los intentos donde los estudiantes **lograban aprobar** la materia después de reprobarla. La "última nota" de varios estudiantes quedaba congelada en un intento fallido antiguo. La materia sigue siendo la #1 del índice (la repitencia sube a 1.61 veces: cuesta más intentos aprobarla), pero su tasa ya refleja el desenlace real. **El top 5 y su orden se mantienen intactos**, lo que confirma que el hallazgo institucional era robusto.

---

## 3. Modelos de reprobación por materia (el cambio dramático)

Ambas mediciones son **validación cruzada CV-5 out-of-fold, sin fugas de información** (mismas features anti-leakage, mismo algoritmo, misma semilla). Lo único que cambió son los datos de entrada.

| Materia | F1-w antes | F1-w después | AUC antes | AUC después | Δ AUC |
|---|---|---|---|---|---|
| **Matemáticas II** | 0.674 | **0.785** | 0.691 | **0.865** | **+0.174** |
| Física I | 0.778 | **0.848** | 0.863 | 0.884 | +0.021 |
| Álgebra Lineal | 0.898 | **0.912** | 0.943 | 0.939 | −0.004 |
| Matemáticas I | 0.867 | **0.928** | 0.832 | 0.928 | +0.096 |
| Fund. de Programación | 0.941 | 0.928 | 0.918 | 0.923 | +0.005 |
| **Promedio F1-w** | **0.832** | **0.880** | | | |

### Por qué la mejora es legítima (y no una fuga de información)

El caso de Matemáticas II es la demostración empírica central. Antes era "impredecible" (AUC 0.691, apenas mejor que el azar en términos prácticos) y se concluía que *"sus reprobaciones dependen de factores dentro del semestre"*. La recodificación demostró que la explicación real era otra: **etiquetas y features contaminadas por datos ocultos**.

1. **Etiquetas (`y`) corregidas.** El target es "reprobó en su último intento". Con los intersemestrales y las vacías-con-nota excluidos, a varios estudiantes se les asignaba `reprobado = 1` cuando en realidad habían aprobado en un intento posterior invisible para el pipeline. El modelo intentaba aprender un patrón parcialmente falso — ningún algoritmo puede predecir bien una etiqueta equivocada.
2. **Features (`X`) más completas.** `prom_global` (promedio en las demás materias, excluyendo la objetivo) y `veces_cursada` ahora se calculan sobre la historia académica completa. Un promedio calculado sobre historias truncadas es una señal ruidosa.
3. **Sin fugas.** Las salvaguardas anti-leakage se mantuvieron idénticas: `prom_global` sigue excluyendo la materia objetivo y `nota_mat1` sigue fuera del modelo de Matemáticas I. La evaluación sigue siendo out-of-fold (el modelo nunca ve al estudiante que predice). La mejora no proviene de "ver la respuesta", sino de **dejar de aprender respuestas equivocadas**.

En síntesis: *garbage in, garbage out* — y su recíproco. El AUC de Matemáticas II subió +0.174 sin tocar una sola línea del algoritmo.

---

## 4. Modelo principal (rendimiento bajo y graduación)

| Métrica | Antes (N=89) | Después (N=90) |
|---|---|---|
| RF `rendimiento_bajo` — Recall+ (umbral 0.29) | 0.811 | **0.816** |
| RF `rendimiento_bajo` — AUC | 0.775 | 0.752 |
| XGB `graduado` — AUC | 0.870 | 0.853 |
| Importancia de `prom_sem1` (RF) | 37.8 % | **40.4 %** |

Aquí la lectura honesta es distinta y conviene decirla explícitamente: **el modelo principal apenas cambió, y así debía ser.** Sus features (socioeconómicas, Saber 11, promedio del primer semestre) no dependen de `detalle_materias`, por lo que la recodificación solo le aportó un estudiante más y correcciones marginales. Las pequeñas variaciones de AUC (−0.02) están dentro del ruido esperable de una muestra de 90 con CV-5, no son una regresión. El indicador operativo del sistema de alertas —**Recall+ = 0.816**, detectar a 8 de cada 10 estudiantes en riesgo— se mantuvo, y `prom_sem1` se **consolidó** como el predictor dominante (40.4 %), reforzando la tesis de la alerta temprana al primer semestre.

Esta asimetría es en sí misma una validación: los modelos cuyos insumos fueron corregidos mejoraron dramáticamente; los modelos cuyos insumos no cambiaron se mantuvieron estables. Si la mejora hubiera sido producto de un error metodológico (una fuga), se habría inflado *todo*.

---

## 5. Calidad estructural ganada (más allá de las métricas)

- **Historial de estados saneado**: 603 imputaciones trazables (columna `ORIGEN`), regla anti-residuo (nada se imputa después de un estado terminal), 57 estados finales inferidos con criterios explícitos (3.1–3.3) y el periodo 2020-2 (pandemia) documentado en vez de silenciado.
- **Estados originales intactos**: la corrección solo *añade* información auditable; los 1 968 registros originales nunca se modificaron.
- **Reproducibilidad total**: originales → `src/recodificacion.py` → archivos recodificados → pipeline → métricas. Cualquier auditor puede regenerar cada cifra de este documento desde los archivos fuente.
- **Extensibilidad**: las mismas reglas están parametrizadas para Ing. Electrónica, Biología y cohortes futuras.

## 6. Conclusión

El aumento de calidad no provino de ajustar algoritmos sino de **corregir la semántica de los datos**: un código mal documentado (`C` = "cancelada" en vez de *intersemestral*) y un historial incompleto habían ocultado el 3 % de los registros más informativos —los desenlaces de recuperación— y a un estudiante completo. Al restituirlos: la estadística descriptiva se volvió realista (Matemáticas II: 31.5 % de reprobación real), los cinco modelos por materia alcanzaron rango útil para intervención (AUC 0.86–0.94, F1-w promedio 0.832 → 0.880), la conclusión errónea "Matemáticas II es impredecible" quedó refutada y el modelo principal confirmó su estabilidad. Es el recordatorio clásico de la minería de datos: **la fase de preparación no es un trámite previo al modelado; es donde se gana o se pierde el modelo.**
