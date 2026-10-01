# Revisión de las Fases 2 y 3 de CRISP-DM (comprensión y preparación de los datos)

**Fecha:** 30 de septiembre de 2026 · **Alcance:** `Fase 2/`, `Fase 3/`, `src/preprocessing.py`, `src/recodificacion.py`, `src/longitudinal.py`, los artefactos que consumen el modelo y `app.py`.

**Método:** se recalcularon los resultados a partir de los extractos recodificados y se contrastaron con los documentos de fase y con la norma (acuerdos de plan, Res. 036 de 2017 y Reglamento Estudiantil).

## Veredicto

**Los cálculos son correctos y reproducibles.** Los fallos están en la **documentación**, en **dos definiciones** y en **un artefacto de dudosa procedencia**. Ninguno invalida la cifra canónica del modelo (AUC-PR 0,745), pero cuatro hallazgos deben corregirse o declararse antes de la sustentación.

| # | Hallazgo | Severidad | Estado |
|---|---|:---:|---|
| R1 | `sin_primer_semestre` no es un dato faltante: identifica a la **población que ingresó por homologación** (PENSUM 603) | Alta | Medido; modelo robusto (0,756 sin ellos) |
| R2 | La cohorte **2018-1 cursó el plan 2011**, aunque el plan 2018 rige desde 2018-I | Media (normativa) | Confirmado en los datos (PENSUM 602); cubierto por la capa de equivalencias |
| R6 | `src/curva_umbrales_art19.csv` **no es una salida de cálculo** | Alta (integridad) | Retirado a `archivo/` |
| R7 | `app.py`: el predictor falla y mezcla dos modelos | Alta (producto) | Corregido el fallo; lo sustituye TRAYECTA |
| R5 | Panel longitudinal: los intersemestrales se cuentan como cortes y el art. 20 se aplica incompleto | Media | Corregido; cambia una conclusión (RC-039) |
| R3 | Informe de Fase 3 desactualizado (SMOTE, partición 72/18, target obsoleto) | Media | Fe de erratas |
| R4 | Nivel educativo faltante imputado como «Analfabeta» | Media | Conclusión del paper verificada como robusta |
| R8 | Repeticiones contadas por **nombre** de asignatura | Baja hoy, alta a futuro | Resuelto con la capa de equivalencias |
| R9 | Atípicos en SABER 11 e imputación fuera de la validación cruzada | Baja | Declarar |
| R10 | Electrónica tiene dos planes sin documento de equivalencias | Baja (alcance) | Solicitar resolución |

## Verificado y correcto

- **`prom_sem1`** coincide con el promedio ponderado recalculado desde `detalle_materias`: diferencia media de 0,024. En el primer semestre solo 2 de 74 estudiantes difieren en más de 0,05, y es efecto del truncamiento a un decimal del promedio oficial.
- **Las pruebas del paper se reproducen exactamente:**
  - Género: Mann-Whitney sobre el promedio de carrera, p = 0,246.
  - Educación del padre: Spearman, p = 0,627; de la madre, p = 0,862.
  - Repitencia escolar: χ², p = 0,215.
- **El target del art. 19** se mantiene idéntico con la clave canónica de curso, tanto en Sistemas como en la FCBI.
- **Cobertura del catálogo de planes:** 107 de 107 códigos, sin discrepancias de créditos.
- **Pruebas automáticas:** `python -m pytest tests/ -q` pasa las 24.

## R1 · `sin_primer_semestre` identifica otra población, no un dato faltante

| | `sin_primer_semestre = 0` | `= 1` |
|---|:---:|:---:|
| PENSUM 602 (plan 2011) | 74 | **0** |
| PENSUM 603 (plan 2018) | **0** | 16 |

- En `homologaciones.xlsx`, 16 de los 20 estudiantes con PENSUM 603 tienen `HOMOLOGACION = SI`.
- El primer registro de estos estudiantes es de 2019-0 o posterior, con notas externas (`OBSERVACION = O`).
- En Electrónica el patrón se repite: 36 de los 37 estudiantes del plan 613 tienen el indicador.

Por tanto **no les «falta» el primer semestre: no lo cursaron porque entraron por homologación**. La Fase 2 dejó fuera `homologaciones.xlsx` porque consideraba que la observación `O` bastaba. En realidad, ese archivo y la columna `PENSUM` de `PROMEDIOS_DE_CARRERA.xlsx` son la fuente directa de esta información.

**Efecto medido** (`src/analisis_cambio_plan.py`): al excluir a los 6 expuestos del PENSUM 603, el AUC-PR pasa de 0,751 a **0,756**. El modelo no depende de esta población.

**Recomendación:**

- Conservar el nombre `sin_primer_semestre` y alimentarla desde `PENSUM` y `HOMOLOGACION`. **Hecho:** `preprocessing.py` añade las columnas informativas `pensum` y `homologacion` y avisa si el indicador no coincide con el plan; en Sistemas coincide en los 90 casos y ninguna cifra cambia.
- Reportar el embudo por tipo de ingreso.
- En el informe, describir a esa población como distinta, no como un dato faltante.

## R2 · La cohorte 2018-1 cursó el plan 2011

El Acuerdo 001 de 2017 rige «para los estudiantes que ingresan a partir del I periodo académico de 2018». Sin embargo:

- 39 de los 44 estudiantes de la cohorte 2018-1 tienen PENSUM 602.
- Todos sus cursos de 2018 tienen código 602.
- El primer registro 603 del extracto es de 2019-0, y corresponde a homologaciones.

Los datos lo confirman: el plan nuevo empezó a operar más tarde, algo frecuente en instituciones públicas mientras se consolida el cambio. La capa de equivalencias se construyó precisamente para absorber esta situación. Importa por dos razones:

- **Para D-REGIMEN:** las dos cohortes son homogéneas en plan, lo que simplifica la defensa.
- **Para la validación externa:** la primera cohorte real del plan 2018 será la primera con la composición nueva del primer semestre (ver `docs/ANALISIS_EQUIVALENCIAS_PLANES.md` §5).

## R6 · `curva_umbrales_art19.csv` no procede de un cálculo

Sus valores de *recall* bajan exactamente **0,018 por cada paso de umbral** en toda la tabla, y el primero (0,95) no se puede obtener con 19 positivos: los valores posibles son k/19, y 18/19 = 0,947. Una curva calculada sobre 19 casos da saltos de 1/19 ≈ 0,053, como los de `i3bis_curva_umbrales.csv`.

- El script `entrenar_principal.py` sí escribe un archivo con ese nombre, pero el contenido actual no corresponde a esa salida.
- Ni la app ni el paper lo consumen. RC-023 lo cita como generado.
- **Acción:** se movió a `archivo/curva_umbrales_art19_NO_CALCULADA.csv` y se dejó una nota.
- **Curvas válidas:** `src/i3bis_curva_umbrales.csv` (RC-034) y `src/mvp_curva_umbral_art19.csv` (paquete MVP).

## R7 · `app.py` (prototipo anterior)

1. **El Predictor Interactivo falla** con `KeyError`, porque `feature_values` no incluye `sin_primer_semestre` y `FEATURES` sí. Se corrigió añadiendo la variable (= 0).
2. **Mezcla de modelos:**
   - `src/mejor_modelo.pkl` es el Random Forest de **19 variables** de I-3 (`max_depth = 3`).
   - Los niveles 0,62 / 0,12 / 0,06 que muestra la app se midieron con el **RF-S3** de I-3 bis.
   - Los umbrales no corresponden al modelo que se carga.
3. El texto de ayuda todavía dice «promedio < 3,0», que es el target descartado.

`trayecta/` sustituye a esta app. Carga `modelos/alerta_art19.joblib` (RF-S3) con umbrales calculados sobre sus propias predicciones fuera de muestra.

## R5 · Panel longitudinal: definición de corte y del art. 20

`longitudinal.py` tenía tres problemas:

- Numeraba los cortes con **todos** los periodos, incluidos los intersemestrales (-0). Un estudiante con un intersemestral llegaba al «corte 2» después de un solo semestre regular.
- Aplicaba el art. 20 como «≥ 51 %», sin el **redondeo de su parágrafo**.
- No exigía que el estudiante **apruebe al menos un curso** (para la variable acumulada).

Se corrigió en `src/entrenar_mvp.py::panel_regular` y en `trayecta/motor.py`.

**Consecuencia:** la mejora de +0,20 de AUC-ROC de RC-039 no sobrevive a la corrección dentro de la población comparable. Diagnóstico con RF fijo, CV-5 × 5:

| Configuración | Corte 1 AUC-ROC | Corte 2 AUC-ROC |
|---|:---:|:---:|
| A · Panel anterior, ≥ 51 %, FCBI (los 3 programas) | 0,647 | 0,673 |
| B · Panel anterior, ≥ 51 %, Sistemas + Electrónica | 0,567 | 0,618 |
| C · Panel corregido, art. 20 con redondeo, Sistemas + Electrónica | 0,565 | 0,524 |

Con el protocolo anidado completo (C, 10 repeticiones, `src/mvp_trayectoria_art20.csv`) el *lift* frente al azar es **≈ 1,0 en los tres cortes**. La señal de RC-039 venía de mezclar Biología, una población distinta según RC-037, y de la definición de corte.

**Decisión:** el riesgo semestre a semestre **no se despliega como predictor**. TRAYECTA muestra el seguimiento semestral con los indicadores normativos de los arts. 19-21, que son reglas exactas, y reserva la predicción para el cierre del primer semestre, donde sí hay señal. Este resultado negativo debe declararse en el informe.

## R3 · Documentos de fase desactualizados

En `Fase 3/03_reporte_transformaciones.md`:

- §3 describe SMOTE, pero el protocolo vigente no lo usa (sin SMOTE, `ESPEC_I3`).
- §5 describe una partición 72/18 que ya no aplica: se usa validación cruzada anidada y la partición está en `archivo/`.
- Los targets descritos son `rendimiento_bajo` y `graduado`; el vigente es `bajo_rendimiento_art19`.
- La mediana de `prom_sem1` es 3,4, no 3,6.
- Son 19 variables, no 18.
- La tabla de nulos marca 0 en `prom_sem1`, pero son 16, cubiertos por el indicador.
- «Homologadas siempre ≥ 3,0» no se verificó.

En `Fase 2/03_diccionario_datos.md`:

- El título dice «Cohorte 2017-2», pero son dos cohortes.
- En `02_descripcion_datos.md`, la escala de los puntajes SABER 11 por área es 0-100, no 0-500.

Se añadió una fe de erratas al inicio de ambos documentos para conservar el registro histórico, y se sincronizó `Fase 3/02_preprocessing.py` con `src/preprocessing.py`.

## R4 · Imputación del nivel educativo de los padres

`NIVEL_ED_PADRE` y `NIVEL_ED_MADRE` faltantes se codifican como 0 («Analfabeta»). Afecta a 19 padres (21 %) y 4 madres. La Fase 2 decía «imputar con la moda».

Esta codificación mezcla el dato faltante con el nivel más bajo. **El modelo S3 no usa estas variables**, y la conclusión del paper se mantiene al excluir los faltantes:

- Padre: Spearman p = 0,82 (n = 71).
- Madre: Spearman p = 0,98 (n = 86).

Para próximos usos conviene un indicador de faltante y excluir los faltantes en las pruebas bivariadas.

## R8 · Repeticiones contadas por nombre de asignatura

La cuarta reprobación del art. 19 y `max_veces_cursado` agrupaban por el texto de `MATERIA`:

- «ÁLGEBRA LINEAL» del plan 2011 y del plan 2018 se unían por coincidencia de nombre.
- «MATEMÁTICAS II» y «CÁLCULO INTEGRAL» no se unían, aunque son el mismo curso según la Res. 036.

Con los datos actuales no hay efecto, porque nadie mezcla planes. Con cohortes nuevas sí lo habría. Se resolvió con la clave canónica opcional (`src/equivalencias.py`), que es retrocompatible.

## R9 · Detalles menores

- `PCRIN` y `PNATN` tienen máximos de 100: hay que revisar si son atípicos de captura.
- Las medianas de SABER 11 se imputan sobre la muestra completa antes de la validación cruzada. Afecta a un solo caso y el efecto es despreciable, pero conviene declararlo.

## R10 · Electrónica

Hay dos planes (612 y 613) y no se dispone de su resolución de equivalencias. La capa los deja pasar sin traducir. Hay que solicitar la norma antes de ampliar TRAYECTA a Electrónica.

---

**Archivos nuevos o modificados en esta revisión:**

- `src/equivalencias.py`, `src/planes_estudio/*`, `tests/`
- `src/analisis_cambio_plan.py`, `src/entrenar_mvp.py`
- `modelos/`, `trayecta/`
- `docs/ANALISIS_EQUIVALENCIAS_PLANES.md`
- Fe de erratas en `Fase 2/03_diccionario_datos.md` y `Fase 3/03_reporte_transformaciones.md`
- Corrección puntual de `app.py`
- `archivo/curva_umbrales_art19_NO_CALCULADA.csv`
