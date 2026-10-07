# Pre-registro · Experimento de variables excluidas y de monotonía (oct-2026)

Escrito el 2026-10-06 **antes de ejecutar** `src/exp_variables_monotonia.py`. Ninguna regla de
este documento se modifica después de ver resultados.

## Motivación
1. Los asesores reportan que `repitio_escolar` les dio buenos resultados. El conjunto S3 se validó
   frente al conjunto completo (RC-032), pero nunca se probó S3 + cada variable excluida, ni para el
   modelo de graduación.
2. En TRAYECTA, un perfil con promedio y Saber 11 altos recibe más riesgo que uno con promedio 1,8.
   Causa diagnosticada: los 7 estudiantes con Saber 11 total > 350 no se graduaron y la mayoría perdió
   la calidad de estudiante tras buenos primeros semestres; y ningún estudiante con promedio de primer
   semestre entre 2,0 y 3,0 la perdió. El modelo reproduce esos patrones de una muestra de 80.

## Protocolo común
Datos `src/df_master_limpio.csv`; alerta: n = 80 expuestos (19 casos); graduación: n = 90 (35 graduados).
Random Forest, 150 árboles. CV externa estratificada 5 × 10 con semillas 42 + r (idénticas a I-3 bis),
AUC-PR con predicciones fuera de muestra agrupadas por repetición; prueba t corregida de Nadeau-Bengio
sobre las 10 repeticiones pareadas.

## E1 · Variables excluidas
- **Etapa 1 (cribado):** S3 + cada una de las 13 variables excluidas, y S3 + las 13 juntas, con los
  hiperparámetros desplegados fijos. Solo sirve para decidir qué se confirma.
- **Etapa 2 (confirmación):** validación anidada completa (rejilla y semillas de I-3 bis) para toda
  variable con Δ AUC-PR ≥ +0,01 en el cribado, y **siempre** para `repitio_escolar`.
- **Regla de adopción:** una variable entra al modelo solo si en la etapa 2 mejora a S3 en
  Δ ≥ 0,03 con p corregido (Holm sobre las candidatas) < 0,05.

## E2 · Monotonía
Validación anidada completa con `monotonic_cst` de scikit-learn:
- M1: riesgo no creciente (graduación no decreciente) en el promedio y las cuatro puntuaciones Saber 11;
- M2: solo en el promedio del primer semestre.
- **Regla de adopción:** el modelo monótono sustituye al actual si **no pierde** más de 0,03 de AUC-PR
  frente a S3 sin restricción (misma regla de parsimonia/interpretabilidad del proyecto). La coherencia
  se verifica además con los perfiles del simulador.

## Alcance
Los modelos desplegados y las cifras de la ponencia del CICI no se modifican hasta concluir y aprobar.
