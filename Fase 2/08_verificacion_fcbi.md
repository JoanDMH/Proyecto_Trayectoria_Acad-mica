# Verificación de comprensión de datos — FCBI completa
## CRISP-DM Fase 2 · WP-OE1.1 / paso I-5 · Ing. de Sistemas, Ing. Electrónica y Biología
**Fecha:** 2026-09-15 · **Script:** `src/verificacion_fcbi.py` · **Registro:** RC-036

**Pregunta rectora:** ¿lo aprendido sobre los datos de Ingeniería de Sistemas —calidad, huecos, semántica, definición del target— aplica igual a los otros dos programas? ¿Son mezclables en un modelo único?

---

## Resumen de la decisión

| Verificación | Resultado |
|---|---|
| Cobertura y llaves | ✅ **Consistente.** Se pierden 4–5 estudiantes por programa, por la misma causa |
| Nulos de las variables | ✅ **Consistente.** Mismo patrón en los tres programas |
| Target del art. 19 | ✅ **Aplicable a los tres.** Prevalencia 21 %–32 % |
| Diseño longitudinal | ✅ **Se vuelve viable.** Tres cortes pasan el filtro de RC-008 |
| ¿Mezclables? | ⚠️ **Con reservas.** Sistemas y Electrónica sí; **Biología es una población distinta** |

---

## A · Cobertura y llaves por programa

| Programa | Caracterización | En historial | Con notas | Con prom. carrera | Pérdida |
|---|:---:|:---:|:---:|:---:|:---:|
| Sistemas | 95 | 95 | 90 | 90 | 5 |
| Electrónica | 95 | 94 | 91 | 91 | 4 |
| Biología | 85 | 83 | 81 | 81 | 4 |
| **FCBI** | **275** | **272** | **262** | **262** | **13** |

La pérdida es pequeña (4,7 %) y **homogénea entre programas**: son estudiantes admitidos que nunca registraron actividad académica calificada. No hay un problema de calidad específico de Electrónica o Biología.

**Hallazgo operativo:** la caracterización usa `CODIGO_ESTUDIANTIL` como llave, mientras que el resto de fuentes usa `CODIGO_INST`. Es una trampa para quien retome el proyecto; queda documentado.

---

## B · Nulos de las variables del modelo

| Variable | Sistemas | Electrónica | Biología |
|---|:---:|:---:|:---:|
| `NIVEL_ED_PADRE` | 22,1 % | 20,0 % | 17,6 % |
| `NIVEL_ED_MADRE` | 4,2 % | 7,4 % | 2,4 % |
| Saber 11 (`PMATN`…`PNATN`) | 1 % | 7 % | 6 % |
| Sexo, estrato, plantel, zona, ingresos, SISBEN | 0 % | 0 % | 0 % |

**Conclusión: el patrón de nulos es el mismo.** La educación del padre es la variable más incompleta en los tres programas (17–22 %), lo que confirma que es una característica del formulario SIIF y no de un programa concreto. Las estrategias de imputación validadas en Sistemas son trasladables sin cambios.

---

## C · El target del art. 19 aplica a los tres programas

| Programa | Expuestos | Positivos | Prevalencia | Evento en sem. 1 | Evento en sem. ≥ 2 |
|---|:---:|:---:|:---:|:---:|:---:|
| Sistemas | 80 | 19 | 23,8 % | 8 | 11 |
| **Electrónica** | 73 | **23** | **31,5 %** | 11 | 12 |
| Biología | 81 | 17 | 21,0 % | 7 | 10 |
| **FCBI** | **234** | **59** | **25,2 %** | **26** | **33** |

Dos observaciones:

1. **Electrónica tiene la mayor prevalencia** (31,5 %), un 32 % más alta que Biología. El fenómeno del art. 19 no se distribuye igual entre programas.
2. **El patrón de simultaneidad se repite:** el 44 % de los eventos ocurre en el primer semestre (26 de 59), con proporciones muy parecidas en los tres programas (42 %, 48 %, 41 %). No es una peculiaridad de Sistemas, es estructural.

---

## D · EDA comparativo — ¿son mezclables?

| Indicador | Sistemas | Electrónica | **Biología** |
|---|:---:|:---:|:---:|
| n | 95 | 95 | 85 |
| **Mujeres** | 15,8 % | 7,4 % | **64,7 %** |
| Estrato medio | 1,94 | 2,08 | 2,02 |
| Saber 11 matemáticas | 65,6 | 65,3 | **54,8** |
| Saber 11 lectura | 62,7 | 62,0 | **55,9** |
| **Promedio de carrera** | 3,083 | 3,036 | **2,702** |
| **Tasa de graduación** | 36,8 % | 26,3 % | **7,1 %** |
| Estados finales `MATRICULADO` (censura) | 0 | 0 | **15** |

### Sistemas y Electrónica son comparables

Difieren en tasa de graduación (36,8 % vs 26,3 %) pero coinciden en composición de género, estrato, Saber 11 y promedio de carrera. **Mezclarlos es defendible.**

### Biología es una población distinta

Tres diferencias estructurales, no de grado:

- **Composición de género invertida:** 64,7 % de mujeres frente al 15,8 % y 7,4 % de las ingenierías. Cualquier análisis por género sobre la FCBI agregada mezclaría dos realidades opuestas.
- **Perfil de ingreso más bajo:** unos 10 puntos menos en todas las áreas del Saber 11 (54,8 vs 65,6 en matemáticas). El punto de partida académico no es el mismo.
- **Desenlace mucho peor:** promedio de carrera 2,702 y tasa de graduación del 7,1 %.

### ⚠️ Advertencia sobre la tasa de graduación de Biología

**El 7,1 % está sesgado a la baja por censura.** Biología tiene **15 estudiantes cuyo último estado es `MATRICULADO`** (18 % de la muestra): siguen cursando y su desenlace aún no se conoce. Sistemas y Electrónica tienen cero.

La diferencia real existe —Biología acumula 24 `RETIRADO BR` frente a 23 y 16, con menos estudiantes— pero **la magnitud del 7,1 % no debe reportarse sin esta advertencia**. Sería un error del mismo tipo que los corregidos en la auditoría: presentar como resultado lo que en parte es un artefacto de la ventana de observación.

---

## E · El diseño longitudinal se vuelve viable

Aplicando la regla de viabilidad pre-registrada en RC-008 (*un corte es modelable si n ≥ 60 y la clase minoritaria ≥ 15*) sobre la muestra FCBI completa:

| Corte (semestre) | En riesgo | Eventos futuros | ¿Modelable? |
|:---:|:---:|:---:|:---:|
| 1 | 208 | **33** | **✅ Sí** |
| 2 | 173 | **19** | **✅ Sí** |
| 3 | 147 | **16** | **✅ Sí** |
| 4 | 107 | 8 | No |
| 5–8 | ≤ 93 | ≤ 4 | No |

**Comparación con Sistemas solo** (donde ningún corte era modelable: 11, 9, 9, 5, 3…):

La extensión a la FCBI **triplica los eventos por corte y habilita tres sub-modelos longitudinales**. Queda confirmado que la ampliación de la muestra era el prerrequisito del diseño por cortes, no una alternativa a él.

Los cortes 4 en adelante siguen sin ser viables: el modelo longitudinal cubrirá los **tres primeros semestres**, que es además donde se concentra el riesgo.

---

## Decisión y recomendación

**1. Lo aprendido en Sistemas es trasladable.** Cobertura, nulos, semántica del diccionario, reglas de recodificación y definición del target funcionan igual en los tres programas. No hace falta rehacer la Fase 2 para Electrónica y Biología.

**2. Modelo conjunto con indicador de programa, verificado empíricamente.** La recomendación es incluir `programa` como variable y **contrastar el modelo conjunto contra modelos separados** bajo el mismo protocolo anidado. No se decide por opinión: se mide. Si el conjunto no supera a los separados por ΔAUC-PR ≥ 0,03, se mantienen separados.

**3. Biología requiere tratamiento explícito de la censura.** Los 15 estudiantes activos no tienen desenlace conocido. Opciones a pre-registrar antes de modelar: (a) excluirlos del target de graduación conservándolos en el del art. 19, que sí es observable; (b) tratarlos como censura a la derecha con análisis de supervivencia. La opción (a) es suficiente para el alcance actual.

**4. Se habilita el diseño longitudinal** para los cortes 1 a 3 (WP-OE1.4).

---

**Salidas:** `src/fcbi_cobertura.csv`, `src/fcbi_nulos.csv`, `src/fcbi_target_art19.csv`, `src/fcbi_eda_comparativo.csv`, `src/fcbi_viabilidad_cortes.csv`, `src/fcbi_target_detalle.csv`
