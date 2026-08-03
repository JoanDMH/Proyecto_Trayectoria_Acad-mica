# KANBAN DE AGENTES — Estado de los paquetes de trabajo
### Única fuente de verdad sobre quién trabaja en qué. Ver protocolo en `PLAN_OPERATIVO_AGENTES.md` §0.1

**Cómo reclamar un WP:** edita tu fila poniendo tu identificador de agente, la fecha y estado `EN CURSO`, e inclúyelo en tu **primer commit** del WP. Un WP con agente asignado no se toca. Si un WP lleva **>7 días sin commits**, cualquier agente puede liberarlo (estado `LIBRE` + nota en Historial).

**Estados válidos:** `LIBRE` · `EN CURSO` · `EN REVISIÓN` (espera verificación cruzada de otro agente) · `BLOQUEADO(motivo)` · `HECHO(commit)`

| WP | Descripción corta | Depende de | Estado | Agente | Fecha reclamo | Último commit |
|---|---|---|---|---|---|---|
| WP-OE1.1 | Verificación de datos Electrónica/Biología | — | LIBRE | — | — | — |
| WP-OE1.2 | Verificación de variables + ablation (RF + LogReg) | — | LIBRE | — | — | — |
| WP-OE1.3 | Target multiclase de trayectoria (regla rezagado pre-registrada) | OE1.1 | LIBRE | — | — | — |
| WP-OE1.4 | Snapshots longitudinales (sub-modelo por corte) | OE1.3 | LIBRE | — | — | — |
| WP-OE1.5 | Dataset maestro FCBI + paquete anonimizado (E3) | OE1.2–OE1.4 | LIBRE | — | — | — |
| WP-OE2.1 | Auditoría de modelos preliminares | — | LIBRE | — | — | — |
| WP-OE2.2 | Framework de comparación (LogReg, DT, RF, SVM, XGB) | — | LIBRE | — | — | — |
| WP-OE2.3 | Modelo principal de trayectoria (por corte) | OE1.5 + OE2.2 | LIBRE | — | — | — |
| WP-OE3.1 | Protocolo de evaluación (pre-registrado) | — | LIBRE | — | — | — |
| WP-OE3.2 | Comparativa final + ganador único (rango entre cortes) | OE2.3 + OE3.1 | LIBRE | — | — | — |
| WP-OE3.3 | Interpretación institucional (SHAP, curva por corte) | OE3.2 | LIBRE | — | — | — |
| WP-OE3.4 | Paquete de inferencia dual + manual + app (E2) | OE3.2 | LIBRE | — | — | — |
| E4.1 | Guía de estilo aplicada / preparación del informe | plantilla del estudiante | BLOQUEADO(esperando plantilla LaTeX) | — | — | — |
| E4.2 | Redacción por secciones (consume REGISTRO_CIENTIFICO) | E4.1 + WPs fuente | LIBRE | — | — | — |
| E4.3 | Cierre: verificación cifra-por-cifra + compilación limpia | E4.2 | LIBRE | — | — | — |

## Historial de cambios de estado

| Fecha | WP | Cambio | Agente | Nota |
|---|---|---|---|---|
| 2026-08-03 | — | Tablero creado; todos los WP en LIBRE salvo E4.1 (espera plantilla) | coordinador | — |
