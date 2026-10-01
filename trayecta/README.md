# TRAYECTA: alerta y trayectoria académica (Ing. de Sistemas)

Es el producto mínimo viable del proyecto *Modelo predictivo de trayectoria académica FCBI* (DGI/Unillanos C07-02-2026-027). Toma como referencia de producto a **SPADIES** (MEN) y se diferencia de él en tres cosas: trabaja a nivel de programa, usa el Reglamento Estudiantil de la Universidad y declara la evidencia de cada número que muestra.

## Ejecutar

Desde la raíz del repositorio:

```bash
pip install -r trayecta/requirements.txt
streamlit run trayecta/app.py
```

Las gráficas están hechas con **D3** (componente propio en `trayecta/componentes/viz`, con `d3.min.js` incluido, así que funciona sin internet). Al hacer clic en un estudiante del panorama se abre su ficha. Las explicaciones están en los íconos **?**.

La app abre con dos **cohortes sintéticas** (`trayecta/datos_demo/`), así que se puede mostrar en público sin exponer datos reales. Para regenerarlas, ejecute `python trayecta/generar_demo.py`.

## Qué hace

| Pantalla | Qué muestra | Tipo |
|---|---|---|
| Panorama de cohorte | Niveles de alerta, situación normativa por semestre y lista de priorización descargable | predictivo + normativo |
| Ficha del estudiante | Trayectoria semestre a semestre: promedios, créditos, situaciones del Reglamento Estudiantil explicadas, alerta y graduación | predictivo + normativo |
| Asignaturas críticas | Índice de criticidad por **curso canónico**, comparable entre los planes 2011 y 2018 | descriptivo |
| Cargar cohorte | Recibe extractos del plan 2011, del 2018 o mezclados, los valida, los traduce y devuelve los resultados | — |
| Simulador de ingreso | Alerta y graduación para un perfil hipotético | predictivo |
| Botón flotante «i» (esquina inferior derecha) | Uso responsable, qué calcula cada modelo, comparación con el azar y limitaciones, en lenguaje no técnico | transparencia |

**Lenguaje de la interfaz.** La interfaz está dirigida a personal administrativo sin formación en ciencia de datos. Nunca muestra solo el número de un artículo del reglamento: cada situación aparece con su nombre en lenguaje claro, qué ocurrió y qué implica (`motor.SITUACIONES`), y el artículo solo como fundamento secundario. Los códigos de registro científico (RC-xxx), las métricas técnicas y los nombres internos de variables quedan en este README y en la documentación del repositorio, para el equipo de mantenimiento.

## Modelos que carga (`modelos/`)

| Paquete | Pregunta | Algoritmo | Desempeño (CV-5×10 anidada) | Estado |
|---|---|---|---|---|
| `alerta_art19.joblib` | ¿Perderá la calidad de estudiante (art. 19)? Se responde al cierre del 1.er semestre | Random Forest, 6 variables (S3) | AUC-PR **0,745 ± 0,025**, frente a 0,2375 por azar (RC-033) | desplegado |
| `graduacion.joblib` | ¿Se graduará? | Random Forest (empata con SVM y lo elige la parsimonia) | AUC-PR **0,705 ± 0,021**, frente a 0,389 por azar; AUC-ROC 0,81 | desplegado |
| `trayectoria_art20.joblib` | Semestre a semestre: ¿reprobará más del 50 % de los créditos más adelante? | Logística / RF | lift ≈ 1 (sin señal) | **no desplegado**; se muestra como resultado negativo |

Cada paquete tiene su tarjeta en `modelos/tarjetas/*.json`, con los datos de entrenamiento, las métricas, los umbrales, los límites y las versiones. El entrenamiento es reproducible con `python src/entrenar_mvp.py` (ver la cabecera del script).

## Formato de entrada

- **materias**: `CODIGO_INST, COHORTE, PERIODO_INSCRIPCION, CODIGO_MATERIA, MATERIA, CREDITOS, DEFINITIVA, OBSERVACION`
- **ingreso**: `CODIGO_INST, COHORTE, PMATN, PCRIN, PNATN, PINGN, PCIUN` (SABER 11)

Se aceptan CSV con separador `,` o `;`, decimales con coma, y también Excel. **No incluya nombres ni documentos de identidad**: un código anónimo por estudiante es suficiente.

## Planes de estudio

`src/equivalencias.py` traduce cada curso a su identidad en el plan vigente (Acuerdo Académico 001 de 2017) según la **Resolución Académica 036 de 2017**. Gracias a eso, una repetición que cruza planes, por ejemplo Matemáticas II (2011) seguida de Cálculo integral (2018), se cuenta como el mismo curso para el art. 19 (cuarta reprobación) y el art. 21. El análisis completo está en `docs/ANALISIS_EQUIVALENCIAS_PLANES.md`.

## Pruebas

```bash
python -m pytest tests/ -q
```

## Límites que la app declara

- No hay validación externa: todo procede de remuestreo sobre una muestra de 80 o 90 estudiantes.
- El 42 % de los casos del art. 19 ocurre en el primer semestre: el modelo los detecta, no los anticipa.
- El puntaje ordena a los estudiantes por riesgo, pero no es una probabilidad individual precisa. Debe usarse el **nivel**, no el decimal.
- En las cohortes del plan 2018, el promedio del 1.er semestre sube en media +0,125, porque Álgebra Lineal pasa a 2.º semestre. El ordenamiento se conserva, pero los umbrales deben revisarse con la primera cohorte real del plan nuevo.
