# Modelo Predictivo de Trayectoria Académica — FCBI Unillanos

Trabajo de grado (Ing. de Sistemas, Universidad de los Llanos). Predicción de la trayectoria académica (rendimiento bajo, graduación, reprobación por materia) de las cohortes 2017-2 y 2018-1 de la FCBI mediante aprendizaje automático, siguiendo CRISP-DM.

**Documento rector:** [`PLAN_DE_TRABAJO.md`](PLAN_DE_TRABAJO.md) — sustituye a la propuesta en PDF; contiene objetivos, estado actual, brechas y plan incremental. **Léelo primero si retomas el proyecto.** La ejecución detallada por objetivos (multiagente) está en [`PLAN_OPERATIVO_AGENTES.md`](PLAN_OPERATIVO_AGENTES.md) y la bitácora de hallazgos en [`REGISTRO_CIENTIFICO.md`](REGISTRO_CIENTIFICO.md).

## Estructura del repositorio

```
├── PLAN_DE_TRABAJO.md        ← Plan rector (objetivos, estado, pendientes)
├── README.md                 ← Este archivo
├── app.py                    ← App Streamlit (prototipo de despliegue)
├── requirements.txt
├── Datos/                    ← Fuente de verdad
│   ├── *.xlsx                  Originales de la Oficina de Sistemas (NUNCA se modifican)
│   ├── detalle_materias_recod.xlsx      Generado por src/recodificacion.py
│   ├── historial_estados_recod.xlsx     Generado por src/recodificacion.py
│   ├── diccionario_siif.md              Diccionario del formulario SIIF
│   └── desglosado formulario diccionario siif.docx
├── Datos.zip                 ← Respaldo prístino de los originales (may-2026)
├── Fase 2/                   ← CRISP-DM Comprensión de datos (EDA, diccionario, hallazgos)
├── Fase 3/                   ← Preparación de datos (transformaciones, df_master, split)
├── Fase 4/                   ← Modelado (informes, comparativas, hiperparámetros)
├── Fase 5/                   ← Evaluación (informes, figuras, impacto recodificación)
├── src/                      ← Código del pipeline + artefactos de modelo (los que consume app.py)
├── figuras/                  ← Figuras para el informe final (fig1–fig8)
├── paper_congreso/           ← Resumen extenso para congreso (Springer LNCS, 4 pp.)
│   ├── paper_congreso.tex      Fuente LaTeX (versión final)
│   ├── paper_congreso.pdf      Compilado
│   └── figuras/                Solo las figuras que cita el .tex
└── archivo/                  ← Documentos históricos (plan interno inicial, auditorías)
```

## Pipeline reproducible (orden de ejecución)

```bash
pip install -r requirements.txt

# 1. Originales → archivos recodificados (reglas validadas con la Oficina de Sistemas)
python src/recodificacion.py            # genera Datos/*_recod.xlsx

# 2. Índice de materias críticas
python src/indice_materias.py           # genera src/materias_criticas.csv

# 3. Dataset maestro (n=90) + features
python -c "import sys; sys.path.insert(0,'src'); from preprocessing import pipeline_completo; pipeline_completo()"

# 4. Modelos por materia crítica (CV-5, sin fugas)
python src/entrenar_materias.py         # genera src/metricas_materias.csv + modelos_materias.pkl

# 5. Modelo principal (rendimiento_bajo + graduado)
python src/entrenar_principal.py rb
python src/entrenar_principal.py gr
python src/entrenar_principal.py ensamblar   # genera comparativas + mejor_modelo.pkl

# 6. App
streamlit run app.py
```

## Decisiones metodológicas clave (resumen)

| Tema | Decisión |
|---|---|
| Archivos fuente | Originales intocables; toda corrección vive en `src/recodificacion.py` → `*_recod.xlsx` |
| `OBSERVACION` | Diccionario corregido jul-2026: `C`=curso intersemestral (incluido en reprobación), `A`/`P`=trámite de grado, `R`/`E`=vacías. Notas válidas: {N, C, H} |
| Historial de estados | Imputación trazable (columna `ORIGEN`): MATRICULADO/NO MATRICULADO/2020-2→NO REALIZO PAGO; regla anti-residuo; 57 estados finales inferidos (criterios 3.1–3.3) |
| Población | Descriptiva n=95 (Sistemas); modelado n=90 |
| Targets actuales | `rendimiento_bajo` (promedio<3.0) y `graduado`, binarios + 5 modelos de reprobación por materia |
| Evaluación | CV-5 estratificada out-of-fold, SEED=42, sin SMOTE; umbral 0.29 (rendimiento_bajo, pro-Recall+) y 0.50 (graduado) |
| Anti-leakage | `prom_global` excluye la materia objetivo; `nota_mat1` fuera del modelo de Matemáticas I; `PROMEDIO_CARRERA` solo como target |

## Métricas vigentes (jul-2026, n=90)

- **Rendimiento bajo** — Random Forest, umbral 0.29: Recall+ **0.816**, AUC 0.752. Predictor dominante: `prom_sem1` (40.4 %).
- **Graduación** — XGBoost: AUC **0.853**.
- **Reprobación por materia** (5 materias críticas): F1-w 0.785–0.928, AUC 0.865–0.939.
- Detalle del antes/después de la recodificación: `Fase 5/03_impacto_recodificacion_antes_despues.md`.
