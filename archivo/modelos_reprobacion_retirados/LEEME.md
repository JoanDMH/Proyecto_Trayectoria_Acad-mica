# Modelos de reprobación por asignatura — RETIRADOS

**Fecha de retiro:** 2026-09-03 · **Paso:** I-4 · **Registro:** RC-013, RC-022

Estos artefactos corresponden a los cinco modelos de reprobación por asignatura crítica
(Matemáticas II, Física I, Álgebra Lineal, Matemáticas I y Fundamentos de Programación).
Se apartaron del pipeline activo pero **no se eliminaron**, como evidencia del hallazgo.

## Por qué se retiraron

Fuga temporal de información. Las cinco asignaturas son de primer y segundo semestre,
pero el predictor dominante `prom_global` es el promedio del estudiante en el **resto de
la carrera**: entre el **70 % y el 83 %** de esa información proviene de semestres
**posteriores** a la asignatura que se predice. No es predicción, es retrodicción.

`veces_cursada` tiene el mismo defecto: no es observable antes de cursar la asignatura.

| | AUC reportado | AUC honesto |
|---|---|---|
| Rango de las 5 asignaturas | 0,865 – 0,939 | — |
| Matemáticas II (solo con información del semestre 1) | — | **0,707** |
| Física I (solo con información del semestre 1) | — | **0,740** |
| Solo variables de ingreso (SABER 11 + socioeconómicas) | — | 0,41 – 0,51 (azar) |

## Contenido

| Archivo | Descripción |
|---|---|
| `modelos_materias.pkl` | Los 5 Random Forest entrenados (copia de `src/`) |
| `01_modelos_materias.pkl` | Réplica que estaba en `Fase 4/` |
| `metricas_materias.csv` | Métricas infladas — **no reutilizar como resultado** |

## Qué sigue vigente

El **índice de criticidad** (`src/indice_materias.py` → `src/materias_criticas.csv`)
**no está afectado**: es un indicador descriptivo que ordena las 52 asignaturas cursadas
por al menos 20 estudiantes según tasa de reprobación (0,70) y repitencia media (0,30).
No predice nada, así que no puede tener fuga.

## Si se quisiera reconstruir

Limitarse a las asignaturas de **segundo semestre** y usar únicamente información
observada en el **primero** (`prom_sem1`, `nota_mat1`). Regresión logística resulta más
estable que Random Forest con n=54. AUC esperado: 0,70–0,74.

No es un entregable comprometido en la propuesta de grado.

**Análisis completo:** `AUDITORIA_2026-09.md` §3.
