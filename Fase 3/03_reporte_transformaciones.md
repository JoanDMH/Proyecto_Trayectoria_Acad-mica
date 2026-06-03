# Reporte de Transformaciones Aplicadas
## CRISP-DM Fase 3 · Universidad de los Llanos · Cohortes 2017-2 y 2018-1 · Ingeniería de Sistemas

---

## 1. Resumen del pipeline de preparación

| Paso | Descripción | Archivo |
|---|---|---|
| Carga y filtrado | Selección de cohorte 2017-2, Ing. de Sistemas | `preprocessing.py` |
| Definición de población base | Cruce de caracterización ∩ historial → 46 estudiantes | `preprocessing.py` |
| Selección de features | 17 variables de entrada | `preprocessing.py` |
| Transformaciones | Encoding, imputación, normalización, derivación | `preprocessing.py` |
| Construcción de targets | 2 variables objetivo binarias | `preprocessing.py` |
| División train/test | 80 % / 20 % estratificada | `train_test_split.json` |
| Dataset final | Guardado en CSV | `df_master_limpio.csv` |

---

## 2. Transformaciones por variable

### Variables binarias (encoding directo)

| Variable original | Variable generada | Transformación | Justificación |
|---|---|---|---|
| `SEXO` (M/F) | `sexo` | M→1, F→0 | Codificación numérica para el modelo |
| `ANOS_REPITIO` (S/N) | `repitio_escolar` | S→1, N→0 | Codificación numérica |
| `TIPO_PLANTEL` (G/P) | `tipo_plantel` | P→1, G→0 | Privado=1, Público=0 |
| `ZONA_LUGAR_RESIDENCIA` (U/R) | `zona_rural` | R→1, U→0 | Rural=1, Urbano=0 |

### Variables ordinales (mapeo con escala corregida)

| Variable original | Variable generada | Transformación | Nulos | Impuatción |
|---|---|---|---|---|
| `NIVEL_ED_PADRE` (códigos DANE 1–14, sin 6) | `nivel_edu_padre` | Mapeo ordinal 0–12 | 8 (17.4 %) | fillna(0) = Analfabeta/Desconocido |
| `NIVEL_ED_MADRE` (códigos DANE 1–14, sin 6) | `nivel_edu_madre` | Mapeo ordinal 0–12 | 1 (2.2 %) | fillna(0) |
| `NIVEL_ED_PADRE/MADRE` | `nivel_edu_max_padres` | max(padre, madre) | 0 | — (derivada) |
| `ESTRATO_ACTUAL` (1–6) | `estrato` | Sin cambio (ya ordinal) | 0 | — |
| `URBANA_SISBEN` / `RURAL_SISBEN` + `SISBEN` | `sisben_nivel` | Regla: sin SISBEN→0, con SISBEN→nivel (1–4 urbano, 1–6 rural) | 0 | — |

> **Nota mapeo NIVEL_ED:** El código 6 no existe en el sistema institucional (salto directo de 5 a 7). La escala ordinal se reindexó de 0 a 12 de forma continua para preservar el orden sin saltos.

### Variables numéricas continuas

| Variable original | Variable generada | Transformación | Nulos | Imputación |
|---|---|---|---|---|
| `INGRESOS` (COP, rango 3M–62.7M) | `log_ingresos` | log1p(x) | 0 | — |
| `PMATN` (Saber 11 Matemáticas, 0–500) | `icfes_mat` | Sin cambio | 1 | Mediana del grupo (65.0) |
| `PINGN` (Inglés) | `icfes_ing` | Sin cambio | 1 | Mediana (63.0) |
| `PCRIN` (Lectura Crítica) | `icfes_lec` | Sin cambio | 1 | Mediana (63.0) |
| `PCIUN` (Soc. y Ciudadanas) | `icfes_soc` | Sin cambio | 1 | Mediana (63.0) |
| `PNATN` (Ciencias Naturales) | `icfes_nat` | Sin cambio | 1 | Mediana (64.0) |
| Suma de 5 componentes | `icfes_total` | Suma aritmética | 0 | — (derivada) |
| `PROMEDIO_SEMESTRE` período 2017-2 | `prom_sem1` | Sin cambio | 0 | Mediana (3.7) si falta |

> **Justificación log1p en ingresos:** La distribución original está fuertemente sesgada a la derecha (media 14.4M, máximo 62.7M, moda ~8.3M). La transformación logarítmica reduce la asimetría y evita que valores extremos dominen el modelo.

> **¿Por qué no se aplicó StandardScaler?** Los modelos seleccionados (Árbol de Decisión, Random Forest, XGBoost) son invariantes a la escala de las features. No se requiere normalización.

### Variables categóricas nominales (sin encoding OHE)

| Variable original | Variable generada | Transformación | Nulos | Imputación |
|---|---|---|---|---|
| `VIVE_CON` (1–5) | `vive_con` | Numérico entero | 1 | fillna(1) = Con ambos padres |
| `SITUACION_PADRES` (1–3) | `situacion_padres` | Numérico entero | 2 | fillna(1) = Separados |

> **Justificación sin One-Hot Encoding:** Con solo 46 registros, OHE inflaría la dimensionalidad innecesariamente. Los árboles de decisión (y sus variantes) pueden manejar variables categóricas codificadas como enteros sin pérdida de información relevante.

---

## 3. Construcción de variables target

| Target | Definición | Positivos | Negativos | Desbalance |
|---|---|---|---|---|
| `rendimiento_bajo` | `PROMEDIO_CARRERA` < 3.0 | 18 (39 %) | 28 (61 %) | Moderado |
| `graduado` | Último estado = `GRADUADO` | 14 (30 %) | 32 (70 %) | Significativo |

**Manejo del desbalance:** Se aplica SMOTE (Synthetic Minority Oversampling Technique) únicamente sobre el conjunto de entrenamiento cuando la proporción minoritaria es < 55 %. Nunca se aplica sobre el test set para evitar data leakage.

---

## 4. Filtrado de registros en detalle_materias

Para el análisis de materias críticas y el submodelo de predicción por materia:

| Acción | Registros excluidos | Razón |
|---|---|---|
| `OBSERVACION` = O (Homologada) | 54 | Nota no refleja aprendizaje en el programa |
| `OBSERVACION` = I (Intercambio) | — | Nota de otra institución |
| `OBSERVACION` = C (Cancelada) | 11 | Sin nota definitiva |
| `OBSERVACION` = E (En curso) | — | Sin nota definitiva |
| `DEFINITIVA` nula | 33 | Sin información |
| **Total excluidos** | **~98** | |
| **Registros válidos** | **1 044 de 1 183** | |

Adicionalmente, por cada estudiante-materia se toma **únicamente la última nota registrada** (orden por `PERIODO_INSCRIPCION` descendente) para evitar contar múltiples intentos como observaciones independientes.

---

## 5. División train/test

| Parámetro | Valor |
|---|---|
| Método | `train_test_split` estratificado |
| Semilla aleatoria | 42 |
| Proporción test | 20 % |
| Variable de estratificación | `rendimiento_bajo` |
| **N train** | **75 estudiantes** |
| **N test** | **19 estudiantes** |
| Distribución target train | 40 % rendimiento bajo |
| Distribución target test | 37 % rendimiento bajo |

La estratificación garantiza que ambas particiones tengan proporciones similares de la clase positiva.

La validación cruzada (StratifiedKFold, k=5) se aplica **solo sobre el train set** para selección de hiperparámetros y estimación de rendimiento.

> **Índices exactos guardados en:** `src/train_test_split.json`

---

## 6. Dataset final — Verificación de criterios

| Criterio | Estado |
|---|---|
| Sin nulos en features | ✅ 0 nulos |
| Sin duplicados | ✅ 0 duplicados |
| Tipos de datos correctos | ✅ Todos numéricos (int/float) |
| Sin data leakage | ✅ `PROMEDIO_CARRERA` solo en target, no en features |
| Número de features | ✅ 18 (≥ 15 requeridas, incluye `cohorte_encoded`) |
| Población base correcta | ✅ 94 estudiantes (2017-2 + 2018-1) |
| Targets definidos | ✅ `rendimiento_bajo` y `graduado` |
