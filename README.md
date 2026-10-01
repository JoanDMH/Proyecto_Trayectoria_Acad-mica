# Modelo predictivo de trayectoria académica — FCBI, Universidad de los Llanos

Trabajo de grado en Ingeniería de Sistemas. Predice el **bajo rendimiento académico según el artículo 19 del Reglamento Estudiantil** en las cohortes de ingreso 2017-2 y 2018-1 de la Facultad de Ciencias Básicas e Ingeniería, siguiendo CRISP-DM.

**Autor:** Joan David Martínez Hernández · joan.martinez@unillanos.edu.co
**Dirección:** Diana M. Cardona-Román · Sara C. Guerrero
**Proyecto DGI/Unillanos** C07-02-2026-027 · **Estado del paquete:** 29 de septiembre de 2026

---

## ⚠️ ANTES DE ABRIR NADA: datos personales sin anonimizar

La carpeta `Datos/` contiene **datos personales identificables de estudiantes reales**, entregados por la Oficina de Sistemas de la universidad:

| Archivo | Campos sensibles |
|---|---|
| `caracterización.xlsx` | `FECHA_NAC`, `DIRECCION_ACTUAL`, `BARRIO`, `TELEFONO_ACU`, `IDENTIFICACION_VICTIMA`, tipo de identificación de los padres |
| `historial_estados_recod.xlsx` | `NOMBRE1`, `NOMBRE2`, `APELLIDO1`, `APELLIDO2` |
| `homologaciones.xlsx` | ídem |
| `detalle_materias_recod.xlsx` | códigos institucionales |

Este paquete se comparte **sin anonimizar**, por decisión expresa del autor y bajo el supuesto de que quien lo recibe está cubierto por el mismo marco de tratamiento de datos de la universidad.

**Si usted recibe esta carpeta:** no la redistribuya, no la suba a servicios en la nube de terceros, no la incluya en repositorios públicos, y elimínela cuando termine su intervención. El entregable E3 del proyecto contempla un **paquete anonimizado** que todavía no se ha construido (ver `WP-OE1.5` en el kanban); construirlo antes de cualquier difusión posterior es la vía correcta.

---

## Por dónde empezar

Lea en este orden. Son cuatro documentos y bastan para tener el cuadro completo.

| # | Documento | Qué le da |
|---|---|---|
| 1 | **`PROBLEMAS_DETECTADOS.txt`** | **Empiece aquí.** 21 problemas hallados, qué se corrigió y, sobre todo, el **bloque 5: lo que sigue abierto**. Si solo va a leer una cosa, que sea esto. |
| 2 | `KANBAN_AGENTES.md` | Estado real de cada paquete de trabajo. Revisado contra la realidad el 29-09. |
| 3 | `REGISTRO_CIENTIFICO.md` | Bitácora completa, RC-001 a RC-044. Cada decisión con su fecha, su medición y su justificación. Es la fuente de verdad. |
| 4 | `bitacora/CONSOLIDADO_RESULTADOS.xlsx` | Todas las tablas y comparativas en un solo archivo, con notas de lectura. |

Complementarios: `MARCO_NORMATIVO.md` (el reglamento aplicado al modelo, y el cambio de régimen 2003 → 2022), `AUDITORIA_2026-09.md` (auditoría metodológica extendida), `PLAN_DE_TRABAJO.md` (plan rector, sustituye a la propuesta en PDF).

---

## Estado del modelo en una tabla

| Concepto | Valor |
|---|---|
| Variable objetivo | Bajo rendimiento, art. 19 del Reglamento Estudiantil |
| Población | **n = 80** expuestos, de 90 con actividad académica |
| Positivos | 19 (23,8 %) — línea base de azar para AUC-PR = **0,2375** |
| Variables | **6** (conjunto S3: promedio de 1er semestre, indicador de ausencia, y SABER 11 total/mat/lec/nat) |
| Modelo | **Random Forest · AUC-PR 0,745 ± 0,025** (factor 3,1× sobre el azar) |
| Protocolo | CV-5 estratificada × 10 repeticiones, **anidada**, semilla 42 |
| Selección | Por aplicación directa de la regla pre-registrada, sin desviaciones |

**No tome esta cifra sin sus tres matices** (detalle en `PROBLEMAS_DETECTADOS.txt`, bloque 5):

1. **El 42 % de los eventos es simultáneo, no predicho** (P19): 8 de los 19 positivos activan el art. 19 en el primer semestre, donde `prom_sem1` es contemporánea al evento. Restringido a los casos genuinamente predictivos, el AUC-PR cae a 0,473 aunque el *lift* se mantiene en 3,10×. (En el conjunto de la FCBI la proporción es del 44 %: 26 de 59.)
2. **No hay validación externa** (P18). Todo procede de remuestreo sobre una sola muestra de 80 casos. Es un estudio exploratorio, no una validación.
3. **Las probabilidades no están calibradas** (P17). El ordenamiento de riesgo sí es estable (Spearman 0,894); el número concreto no es interpretable.

---

## Lo que bloquea el avance no es código

Cinco decisiones pendientes de la dirección. Ninguna se resuelve programando:

| # | Decisión | Por qué importa |
|---|---|---|
| **D-REGIMEN** | Las cohortes cursaron bajo el **Acuerdo 015 de 2003** pero se etiquetan con el **reglamento vigente desde 2022** | Es el punto más atacable en sustentación. Si se decide etiquetar con la norma de la época, el target cambia otra vez |
| **D-MULTI** | El target multiclase comprometido en la propuesta **no es viable** (clase ACTIVO n=5) | Modifica el entregable E2 |
| **D-ALCANCE** | ¿Un modelo para la FCBI o **tres por programa**? Los separados ganan (Δ = −0,031) | Modifica el entregable E2 |
| **D-COLIN** | `icfes_total` tiene **VIF 6,66** y es en un 85 % combinación de sus áreas | Invalida toda lectura de coeficientes, importancias o SHAP en el bloque SABER 11 |
| **D-APP** | Calibrar las probabilidades o retirar el porcentaje de la aplicación | Hoy la app publica un número que el modelo no puede sostener |

---

## Estructura del repositorio

```
proyecto_rendimiento_academico/
│
├── README.md                    ← este archivo
├── PROBLEMAS_DETECTADOS.txt     ← EMPIECE AQUÍ: 21 problemas, bloque 5 = lo abierto
├── KANBAN_AGENTES.md            ← estado real de cada paquete de trabajo
├── REGISTRO_CIENTIFICO.md       ← bitácora RC-001…RC-044 (fuente de verdad)
├── PLAN_DE_TRABAJO.md           ← plan rector (sustituye a la propuesta en PDF)
├── PLAN_OPERATIVO_AGENTES.md    ← protocolo de trabajo multiagente
├── PLAN_MEJORAS.md              ← mejoras priorizadas con su evidencia
├── AUDITORIA_2026-09.md         ← auditoría metodológica extendida
├── MARCO_NORMATIVO.md           ← reglamento aplicado al modelo (2003 vs 2022)
├── RESUMEN_ASESOR_2026-09.md    ← resumen ejecutivo para la dirección
├── BORRADOR_INFORME.md          ← borrador del informe final
├── ESPEC_I3.md, INSTRUCCIONES_I3BIS.md  ← especificaciones de los experimentos
├── reglamento_estudiantil_unillanos.md  ← transcripción del reglamento vigente
│
├── verificar_coherencia_documental.py  ← comprueba que ningún documento quede desfasado
├── app.py                       ← aplicación Streamlit (prototipo de despliegue)
├── requirements.txt
│
├── Datos/                       ⚠ DATOS PERSONALES — ver advertencia arriba
│   ├── *.xlsx                     originales de la Oficina de Sistemas (NUNCA se modifican)
│   ├── *_recod.xlsx               generados por src/recodificacion.py
│   └── diccionario_siif.md
│
├── src/                         ← código del pipeline y artefactos del modelo
│   ├── preprocessing.py           construcción del dataset y del target art. 19
│   ├── recodificacion.py          corrección de la codificación de los extractos
│   ├── entrenar_i3bis.py          comparación definitiva de los 5 algoritmos
│   ├── arnes_experimentos.py      protocolo común (CV anidada, t corregida)
│   ├── pca_seleccion.py           bloque A · PCA          (RC-042)
│   ├── modelos_bayesianos.py      bloque B · bayesianos   (RC-043)
│   ├── pocos_datos.py             bloque C · pocos datos  (RC-044)
│   ├── seleccion_variables.py     permutación, VIF, ablación anidada
│   ├── diagnostico_error.py       brecha, curva de aprendizaje, bootstrap .632+
│   ├── comparacion_estadistica.py t corregida de Nadeau-Bengio
│   ├── instrumentacion.py         bitácora automática de corridas
│   ├── longitudinal.py            diseño por cortes semestrales (refutado, RC-038)
│   ├── experimento_ancho_target.py  art. 19 vs art. 20 (RC-039)
│   ├── target_multiclase.py       target de 4 clases (inviable, RC-041)
│   ├── verificacion_fcbi.py       los tres programas de la Facultad
│   ├── dataset_fcbi.py            dataset maestro FCBI (262 estudiantes)
│   ├── indice_materias.py         índice de criticidad por asignatura
│   ├── *.pkl                      artefactos que consume app.py
│   └── _cache_experimentos/       resultados por repetición (evidencia cruda)
│
├── bitacora/
│   ├── CONSOLIDADO_RESULTADOS.xlsx  ← 11 hojas con todos los resultados
│   ├── _build_consolidado.py        lo regenera desde los CSV
│   ├── _hojas_asesor.py             hojas 9-11 (PCA, bayesianos, pocos datos)
│   └── 2026*/                       corridas instrumentadas de I-3 bis
│
├── Fase 2/ … Fase 5/            ← entregables por fase de CRISP-DM
├── figuras/                     ← figuras del informe (fig1–fig8)
├── paper_congreso/              ← ponencia CICI 2026 (Springer LNCS, 4 pp.)
│   ├── paper_congreso.tex/.pdf    versión final
│   ├── Presentacion_CICI2026_Martinez.pptx
│   └── figuras/
├── documentos_fuente/           ← reglamento y propuesta originales en PDF
├── archivo/                     ← material retirado con trazabilidad
└── _APARTADO_sacar_antes_de_enviar/   ⚠ SACAR antes de comprimir el envío
```

---

## Reproducir los resultados

Todo es reproducible con `SEED = 42`. Requiere Python 3.10+.

```bash
pip install -r requirements.txt

# 1 · preparación (regenera Datos/*_recod.xlsx y src/df_master_limpio.csv)
python src/recodificacion.py
python src/preprocessing.py

# 2 · comparación de los 5 algoritmos con el target del art. 19  (RC-033)
python src/entrenar_i3bis.py

# 3 · encargos de la dirección del 29-09
python src/pca_seleccion.py descriptivo
python src/pca_seleccion.py correr        # ~5 min por configuración
python src/pca_seleccion.py tabla
python src/modelos_bayesianos.py correr
python src/modelos_bayesianos.py posterior
python src/pocos_datos.py correr
python src/pocos_datos.py curva

# 4 · consolidar todo en el Excel
python bitacora/_build_consolidado.py

# 5 · aplicación
streamlit run app.py
```

**Nota sobre tiempos.** Los scripts del paso 3 guardan el resultado **después de cada repetición** en `src/_cache_experimentos/` y reanudan donde se quedaron: se pueden interrumpir sin perder trabajo. Borre esa carpeta para recalcular desde cero.

---

## Dos técnicas que se pidieron y no hacen lo que parece

Se documentan porque es probable que vuelvan a proponerse. Detalle en RC-042 y RC-044.

**PCA para validar la selección de variables.** Es no supervisado: busca varianza en X sin mirar nunca a *y*, así que por construcción no puede demostrar que unas variables sean las mejores para predecir. En estos datos la demostración es contundente: la variable más predictiva del estudio —el promedio del primer semestre, 40,4 % de la importancia— tiene su carga máxima en **CP3, que explica el 8,3 % de la varianza**. Medido con el mismo protocolo, el PCA **destruye la señal**: AUC-PR 0,372 frente a 0,742 (p < 0,0001). Sí sirve como diagnóstico de redundancia y como representación alternativa comparable.

**One-shot / few-shot learning.** Requiere un corpus de preentrenamiento del que transferir y una estructura por episodios con clases nuevas en prueba. Aquí el problema es tabular, binario y con ambas clases presentes desde el inicio. Se trasladó el *mecanismo* (métrica aprendida + prototipos de clase, que es ProtoNet sin la red) y el resultado es instructivo: **aprender la métrica con NCA empeora** (0,356 frente a 0,437), porque con 19 positivos NCA sobreajusta.

---

## Qué se apartó al preparar este envío

Se movieron **35 elementos** a la carpeta `_APARTADO_sacar_antes_de_enviar/`, **sin borrar nada**: corridas abortadas y vacías de la incidencia del 15-09, versiones preliminares del paper, materiales de la presentación de junio con cifras del target antiguo, comprimidos que duplicaban contenido ya extraído, código del pipeline obsoleto y dos archivos ajenos a este proyecto. El detalle está en `MANIFIESTO.md` dentro de esa carpeta. Para restaurar cualquiera, cópielo de vuelta respetando su ruta original.

> **Si usted es quien envía este proyecto:** saque `_APARTADO_sacar_antes_de_enviar/` de la carpeta antes de comprimir. Está aquí dentro solo porque es el único sitio accesible; no forma parte del paquete.

---

## Licencia y uso

Material académico de un trabajo de grado en curso. No publicar resultados ni datos sin autorización del autor y de la dirección del proyecto.
