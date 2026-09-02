# BORRADOR PARA EL INFORME FINAL — Bitácora consolidada de hallazgos
### Insumo de redacción (E4). No es el informe: es el inventario completo de cifras, grupos, decisiones y lecciones, con su fuente.
**Corte de la información:** 2026-08-03 · Complementa `REGISTRO_CIENTIFICO.md` (experimentos RC-001…RC-008). Toda cifra es regenerable con los scripts de `src/`.

---

## 1. Contexto y fuentes de datos

Datos suministrados por la Oficina de Sistemas de la Universidad de los Llanos (extracción may-2026), en el marco del proyecto longitudinal de trayectoria estudiantil FCBI (codirectora S. Guerrero). Cohortes de ingreso **2017-2 y 2018-1**; ventana de observación hasta **2026-1** (~8–9 años de trayectoria).

| Archivo | Dimensiones | Contenido | Llave |
|---|---|---|---|
| `caracterización.xlsx` | 337 × 147 | Formulario SIIF al ingreso: sociodemográficas, familiares, Saber 11 | `CODIGO_ESTUDIANTIL` |
| `detalle_materias.xlsx` | 8 503 × 14 | Materia × intento: nota definitiva, periodo, observación | `CODIGO_INST` |
| `historial_estados_.xlsx` | 1 968 × 9 | Estado académico-administrativo por semestre | `CODIGO_INST` |
| `PROMEDIOS_DE_CARRERA.xlsx` | 323 × 10 | Promedio acumulado final | `CODIGO_INST` |
| `promedios_semestre.xlsx` | 1 903 × 9 | Promedio por semestre cursado | `CODIGO_INST` |
| `homologaciones.xlsx` | 343 × 10 | Pénsum y marca de homologación | `CODIGO_INST` |

Calendario real de los datos: 17 periodos regulares (2017-2 → 2026-1). **2020-2 no existe en ningún archivo** (suspensión por pandemia). Los periodos `AAAA-0` son cortes administrativos de inicio de año donde se asientan homologaciones (`O`) y cursos intersemestrales (`C`); no contienen cursos "normales".

## 2. Población por programa

| Programa | n caracterización | Graduados | Retiro formal | Sin acta (no grad.) | Activos 2024-1+ | Sin actividad académica |
|---|---|---|---|---|---|---|
| Ing. de Sistemas | 95 | 35 (36.8 %) | 30 | 30 | 1 | 15* |
| Ing. Electrónica | 95 | 25 (26.3 %) | 32 | 38 | 4 | 22* |
| Biología | 85 | 6 (7.1 %) | 33 | 46 | 15 | 4 |
| *(Lic. en Matemáticas — fuera del alcance)* | 62 | 14 | 14 | 34 | 5 | 2 |
| **Total FCBI (alcance)** | **275** | **66 (24.0 %)** | 95 | 114 | 20 | 41 |

\* "Sin actividad" = sin cursos en periodos regulares; incluye a quienes solo tienen bloque de homologación en periodos `-0` (Sistemas: 10 de los 15).

**Hallazgo de heterogeneidad (clave para el modelo general vs. por programa):** la tasa de graduación de Biología (7.1 %) es radicalmente inferior, con 15 estudiantes aún activos a 2026 — su trayectoria típica es más larga y su deserción/permanencia se comporta distinto. Esto debe pesarse en WP-OE1.1 antes de mezclar programas.

## 3. Semántica de los datos: lo que hubo que corregir (diccionario real)

La columna `OBSERVACION` de `detalle_materias` estaba mal interpretada. Diccionario validado con la Oficina de Sistemas (jul-2026):

| Código | Significado real | Interpretación errónea previa | Registros (global) |
|---|---|---|---|
| `N` | Curso normal | ✓ | 6 961 |
| `O` | Homologada (nota externa, siempre ≥3.0) | ✓ | 628 |
| `H` | Habilitada | ✓ | 324 |
| `TG` | Trámite de grado (sin nota) → se recodifica `A`/`P` | categoría única | 207 |
| (vacía) | **209 con nota = cursos reales** → `N`; sin nota → `R`/`E` | "sin registro" (se excluían) | 301 |
| `C` | **Curso intersemestral** (nota real, 17/79 reprobados) | **"Cancelada" (se excluían)** | 79 |
| `V` | Validada | "Vacía" | 2 |
| `I` | Intercambio | ✓ | 1 |

Otras propiedades verificadas: las homologadas (`O`) **nunca** tienen nota <3.0 (no se homologa lo reprobado); el historial de estados **no conserva** matrículas tempranas de muchos estudiantes e **omite estudiantes completos** (caso 160004030: 6 materias cursadas en 2017-2, cero filas de estado); tras un `RETIRADO BR` el sistema deja residuos administrativos (`NO REALIZO PAGO` un periodo después, 5 casos verificados) — los graduados en cambio cierran limpio (35/35 con `GRADUADO` como último estado, sin residuos).

## 4. Recodificación reproducible (la contribución metodológica central)

Todos los originales permanecen intactos (respaldo `Datos.zip`); las correcciones viven en `src/recodificacion.py` que genera:

**`detalle_materias_recod.xlsx`** (8 486 filas): elimina 17 trámites de grado fantasma posteriores a la graduación; recodifica `OBSERVACION` (vacías-con-nota→`N` 209; trámites→`A` 75/`P` 183 con regla "último trámite y periodo ≤ graduación"; vacías sin nota→`E` 24). Notas válidas para análisis: {N, C, H}.

**`historial_estados_recod.xlsx`** (2 566 filas): 1 968 originales intactas (columna `ORIGEN`) + 541 imputaciones trazables + 57 estados finales inferidos:

| Imputación | N | Regla |
|---|---|---|
| MATRICULADO | 256 | Periodo con cursos reales pero sin estado |
| NO MATRICULADO | 184 | Hueco truncado (sin actividad ni estado) dentro de la ventana |
| NO REALIZO PAGO (2020-2) | 101 | Pandemia; solo si hay actividad posterior a 2020-1 |
| Estado final inferido | 57 | Ver §5; **regla anti-residuo:** nada se imputa después de un estado terminal original |

## 5. Grupos de trayectoria identificados (detalle Ing. de Sistemas, n=95)

Clasificación por **regla de recencia** (en formación solo si hay actividad/matrícula en 2024-1+):

- **Graduados: 35 (36.8 %).** Tiempo a la graduación: media 6.4 años, mediana 6.0, rango 5.0–8.0 (plan nominal: 5). Cierre administrativo limpio en el 100 %.
- **Desertores: 59 (62.1 %).** Solo 30 con acta formal (17 RETIRADO BR, 8 voluntario, 4 no renovación, 1 definitivo BR); 29 sin acta. Duración antes de abandonar: mediana 1 periodo activo, media 2.2; **64 % deserta con ≤2 periodos** (concentración en el primer año); 5 nunca tuvieron actividad.
- **En formación: 1 (1.1 %)** (160004146, activo hasta 2026-1).

Subgrupos con valor analítico:

| Subgrupo | N | Evidencia |
|---|---|---|
| Sin acta con patrón `BAJO RENDIMIENTO→NO REALIZO PAGO` | 12 | Idéntico a los RETIRADO BR confirmados → estado final inferido RETIRADO BR |
| Sin acta con solo `NO REALIZO PAGO` (×2–3) | 3 | → inferido RETIRO POR NO RENOVACIÓN |
| Solo homologación (bloque 2019-0, pénsum 603) | 9 | Homologaron plan y desaparecieron; **0 traspasos internos** verificados por cruce de nombres en los 4 programas |
| Semestres truncados con reingreso | 12 | Hueco real de 1–3 periodos y retorno (10 con acta posterior, 2 graduados) |
| Invisibles en historial | 1 (160004030) | Recuperado vía imputación; entró a la muestra de modelado |

Predictor administrativo notable: **`BAJO RENDIMIENTO` es terminal en la práctica — 0 de 36 estudiantes que lo recibieron se graduaron.** Estados finales inferidos en total FCBI: 57 (Sistemas 15, Electrónica 15, Biología 27; mapeo BR≥1→RETIRADO BR 44, NRP≥2→NO RENOVACIÓN 13).

## 6. Variables consideradas (muestra de modelado Sistemas, n=90)

**Población de modelado:** caracterización ∩ historial(recod) ∩ promedio de carrera no nulo = **90** (se excluyen 5 sin ninguna actividad). Targets prototipo: `rendimiento_bajo` = promedio final <3.0 (38/90, 42.2 %); `graduado` (35/90, 38.9 %). Split 72/18 estratificado; SEED=42.

**18 features** (todas de ingreso + primer semestre; sin información futura):

| Grupo | Variables |
|---|---|
| Sociodemográficas/familiares | `sexo`, `estrato`, `log_ingresos`, `sisben_nivel`, `tipo_plantel`, `zona_rural`, `vive_con`, `situacion_padres`, `repitio_escolar`, `nivel_edu_padre`, `nivel_edu_madre`, `nivel_edu_max_padres` |
| Académicas de entrada | `icfes_total`, `icfes_mat`, `icfes_lec`, `icfes_nat` |
| Cohorte | `cohorte_encoded` |
| Primer semestre | `prom_sem1` |

Transformaciones documentadas: log1p en ingresos (asimetría fuerte: media 14.4M, máx 62.7M COP); mapeo ordinal de educación parental (códigos DANE sin el 6); imputaciones con mediana/moda (nulos relevantes: NIVEL_ED_PADRE 22.1 %). Sin escalado para árboles (los pipelines de LogReg/SVM lo incorporarán internamente). Excluidas hoy y **pendientes de re-evaluación** (WP-OE1.2): `icfes_ing`, `icfes_soc`, edad al ingreso, % créditos aprobados en sem 1. La verificación formal del set (ablation con RF + regresión logística) está pre-registrada.

## 7. Errores cometidos durante el estudio (y sus correcciones)

Se documentan porque son parte del método (CRISP-DM iterativo) y de la discusión del informe:

1. **Fugas de información en los modelos por materia** (RC-001): `prom_global` incluía la nota objetivo y `nota_mat1` era el target del modelo de Matemáticas I → métricas infladas (Matemáticas I F1 in-sample = 1.000). Corregido: features anti-leakage + CV out-of-fold obligatoria.
2. **Métricas in-sample reportadas al inicio** para los modelos por materia → sustituidas en su totalidad por CV-5 out-of-fold.
3. **Diccionario mal interpretado** (RC-002): `C` leída como "cancelada" y vacías-con-nota descartadas → se excluían 76 registros reales solo en Sistemas; tasa de reprobación de Matemáticas II sobreestimada (44 % aparente vs. 31.5 % real).
4. **Cifra obsoleta arrastrada** ("N=12" en materias críticas) detectada en revisión cruzada: el pipeline reproducible por script eliminó la clase de errores "número editado a mano".
5. **Imputación con residuos post-terminales** (fila 1216): un trámite fantasma post-graduación generó un `MATRICULADO` imputado después del `GRADUADO`; se detectaron y borraron 17 registros fuente y se instauró la regla anti-residuo (43 imputaciones post-retiro también eliminadas).
6. **Riesgo del periodo "-0" y del 2020-2**: al inicio se trató 2020-2 como hueco individual (producía ~40 falsos "semestres truncados"); corregido al descubrir que el periodo no existe institucionalmente (pandemia).
7. **Incidencias operativas**: corrupción de archivos xlsx en disco (2 veces) y una alteración accidental del original `detalle_materias.xlsx` (1 nota borrada) — recuperado todo desde `Datos.zip`; motivó la regla "todo regenerable por script".

## 8. Decisiones estratégicas tomadas (con justificación corta)

| # | Decisión | Justificación |
|---|---|---|
| D1 | Clasificación del estado final por **recencia** (activo solo si 2024-1+) | Un `NO REALIZO PAGO` de hace 5 años no es "en formación" |
| D2 | **Originales intactos + recodificación por script** | Reproducibilidad y defensa ante auditoría |
| D3 | Estados originales = norma; imputaciones trazables (`ORIGEN`) | No se sobreescribe evidencia administrativa |
| D4 | Estados finales **inferidos** solo con criterios 3.1–3.3 | Evita imputar sin evidencia (excluidos: activos, sin actividad, señal insuficiente) |
| D5 | Índice de materias críticas **centrado en reprobación** (0.70/0.30) | Mide dificultad de aprobar; el promedio penalizaba materias fáciles con notas bajas |
| D6 | **Sin SMOTE** en binarios (42/39 % minoritaria) | Desbalance leve; ruido sintético con n=90 (RC-004) |
| D7 | Umbral 0.29 en riesgo de bajo rendimiento | Prioriza Recall+ (0.816): el falso negativo es el error caro en alertas (RC-005) |
| D8 | n=89→**90** al recuperar a 160004030 | Su exclusión era un defecto del archivo, no metodológica; features reales |
| D9 | Alcance: Sistemas + Electrónica + Biología (**sin** Lic. Matemáticas) | Decisión del estudiante |
| D10 | Target de trayectoria multiclase con **sub-modelos por corte** semestral | Evita el sesgo de supervivencia (RC-008) |
| D11 | Regla de viabilidad pre-registrada para la clase "rezagado" | <25 casos → colapso a 3 clases (RC-008) |
| D12 | E2 = paquete de inferencia dual (trayectoria + bajo rendimiento) | Visión de producto SPADIES |

## 9. Resultados de la muestra de Ing. de Sistemas (estudios preliminares)

### 9.1 Materias críticas (índice, datos recodificados)

| # | Materia | Tasa reprobación | Repitencia media | Índice | N |
|---|---|---|---|---|---|
| 1 | Matemáticas II | 31.5 % | 1.61 | 0.983 | 54 |
| 2 | Física I | 27.8 % | 1.65 | 0.918 | 54 |
| 3 | Álgebra Lineal | 29.2 % | 1.40 | 0.835 | 72 |
| 4 | Matemáticas I | 26.0 % | 1.10 | 0.623 | 73 |
| 5 | Fund. de Programación | 20.8 % | 1.15 | 0.534 | 72 |

Las 5 son de los primeros semestres y de énfasis matemático — coherente con la literatura STEM citada en la propuesta.

### 9.2 Modelos prototipo — comparativa de algoritmos (CV-5 OOF, n=90)

**Target `rendimiento_bajo` (umbral 0.29):**

| Modelo | Recall+ | Prec+ | F1-mac | AUC | MCC | Acc |
|---|---|---|---|---|---|---|
| Árbol de Decisión | 0.632 | 0.667 | 0.702 | 0.702 | 0.404 | 0.711 |
| **Random Forest** ✓ | **0.816** | 0.484 | 0.548 | 0.752 | 0.197 | 0.556 |
| XGBoost | 0.737 | 0.596 | 0.677 | 0.776 | 0.367 | 0.678 |

**Target `graduado` (umbral 0.50):**

| Modelo | Recall+ | Prec+ | F1-mac | AUC | MCC | Acc |
|---|---|---|---|---|---|---|
| Árbol de Decisión | 0.686 | 0.686 | 0.743 | 0.728 | 0.486 | 0.756 |
| Random Forest | 0.657 | 0.821 | **0.792** | 0.844 | **0.596** | 0.811 |
| **XGBoost** ✓ | 0.600 | 0.808 | 0.764 | **0.853** | 0.548 | 0.789 |

**Modelos de reprobación por materia (RF, CV-5, sin fugas):**

| Materia | F1-w | AUC | N | % reprobación |
|---|---|---|---|---|
| Matemáticas I | 0.928 | 0.928 | 73 | 26.0 |
| Fund. de Programación | 0.928 | 0.923 | 72 | 20.8 |
| Álgebra Lineal | 0.912 | 0.939 | 72 | 29.2 |
| Física I | 0.848 | 0.884 | 54 | 27.8 |
| Matemáticas II | 0.785 | 0.865 | 54 | 31.5 |

### 9.3 Importancia de variables (comportamiento del modelo)

| Rank | RF → rendimiento_bajo | Imp. | XGB → graduado | Imp. |
|---|---|---|---|---|
| 1 | `prom_sem1` | **0.404** | `prom_sem1` | 0.197 |
| 2 | `icfes_total` | 0.121 | `cohorte_encoded` | 0.171 |
| 3 | `icfes_lec` | 0.071 | `icfes_total` | 0.138 |
| 4 | `log_ingresos` | 0.070 | `log_ingresos` | 0.098 |
| 5 | `icfes_nat` | 0.066 | `icfes_nat` | 0.088 |

**El promedio del primer semestre domina ambos targets** — la señal de alerta más temprana y accionable. Matiz metodológico anotado: la importancia Gini favorece variables continuas; verificar con permutation importance/SHAP en OE3.3.

### 9.4 Pruebas estadísticas (n=90) — resultados negativos que se publican

Ninguna asociación significativa: género vs. promedio (Mann-Whitney p=0.246; medianas 3.20 M / 3.70 F), educación del padre/madre vs. promedio (Spearman p=0.627 / 0.862), repitencia escolar vs. rendimiento bajo (χ² p=0.215). Poder limitado (15 mujeres; 15 repitentes).

### 9.5 Impacto de la calidad de datos (antes → después de la recodificación)

| Indicador | Antes | Después |
|---|---|---|
| Registros con nota válidos (Sistemas) | 2 448 | 2 524 (+76) |
| n modelado | 89 | 90 |
| Tasa reprobación Matemáticas II | 44 % | 31.5 % |
| F1-w promedio (modelos por materia) | 0.832 | 0.880 |
| AUC Matemáticas II | 0.691 | **0.865** (+0.174) |
| Modelo principal (features independientes) | — | estable (validación de que no hubo fuga) |

La conclusión previa "Matemáticas II es impredecible" quedó **refutada**: era un artefacto de datos ocultos. Tabla completa: `Fase 5/03_impacto_recodificacion_antes_despues.md`.

## 10. Comportamiento cualitativo de los modelos prototipo (lecciones para el modelo principal)

1. **El trade-off Recall/Precisión es la decisión de producto:** RF a umbral 0.29 detecta 8 de cada 10 en riesgo pero con ~1 falsa alarma por acierto — aceptable para alertas con revisión humana, inaceptable para decisiones automáticas. El informe debe presentarlo como decisión de negocio, no como defecto.
2. **Ningún algoritmo domina en todo:** XGB gana en AUC de graduación, RF en F1-mac/MCC, DT es sorprendentemente competitivo con n pequeño. Con n≈90 las diferencias entre familias son modestas → refuerza la necesidad del test de comparación formal (WP-OE3.2) antes de declarar un ganador.
3. **La señal académica temprana aplasta a la socioeconómica** en estas cohortes (40.4 % vs. ≤12 % por variable): las socioeconómicas aportan en conjunto pero ninguna individualmente es decisiva (consistente con las pruebas no significativas §9.4).
4. **La calidad del dato importó más que el algoritmo:** +0.174 de AUC en Matemáticas II sin tocar una línea de modelado. Lección central del estudio.
5. Los modelos por materia funcionan con features mínimas (promedio global sin la materia + veces cursada + nota Matemáticas I) — la reprobación es fuertemente autocorrelacionada con el desempeño general previo.

## 11. Limitaciones vigentes (para el capítulo de limitaciones)

- Muestra pequeña: 90 (Sistemas) / ~275 (FCBI); solo 2 cohortes de una misma ventana histórica (incluye disrupción por pandemia).
- Desbalance de género (84 % masculino en Sistemas) limita el análisis por género.
- 57 estados finales inferidos (20.7 % de los no graduados FCBI) y 541 estados imputados: trazables, pero son inferencias, no registros.
- Biología tiene 15 estudiantes aún activos: su etiqueta final está censurada (truncamiento de observación) — considerar al definir el target multiclase.
- Sin variables de desempeño psicosocial ni asistencia; el formulario SIIF tiene ~30 columnas inutilizables (>95 % nulos).
- Validez externa restringida a la FCBI Unillanos.

## 12. Pendientes que alimentarán este borrador

Extensión de EDA y modelos a Electrónica/Biología (WP-OE1.1), verificación formal de variables (WP-OE1.2), target multiclase y su distribución (WP-OE1.3), sub-modelos por corte y curva desempeño-vs-semestre (WP-OE1.4/OE3.3), comparativa con LogReg y SVM (WP-OE2.2), calibración de probabilidades (WP-OE3.1) y selección del ganador único (WP-OE3.2). Cada uno añadirá su sección aquí vía `REGISTRO_CIENTIFICO.md`.
