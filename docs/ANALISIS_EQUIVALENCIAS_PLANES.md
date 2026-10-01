# Equivalencias entre los planes de estudio 2011 y 2018 (Ing. de Sistemas)

**Fecha:** 30 de septiembre de 2026 · **Implementación:** `src/equivalencias.py` y `src/planes_estudio/` · **Pruebas:** `tests/test_equivalencias.py` (20 pruebas que pasan)

**Fuentes normativas:**

- Acuerdo Académico 008 de 2011: plan **IS-2011**, códigos `602xxx`, 167 créditos, 52 cursos.
- Acuerdo Académico 001 de 2017: plan **IS-2018**, códigos `603xxx`, 165 créditos, 53 cursos. Rige para quienes ingresan desde 2018-I.
- Resolución Académica 036 de 2017: equivalencias y homologaciones entre ambos planes.

---

## 1. Resumen

1. **Las cifras actuales no cambian.** En la extracción vigente **ningún estudiante mezcla códigos de los dos planes**. El target del art. 19 sale idéntico con la clave histórica y con la canónica, tanto en Sistemas como en la FCBI. El dataset maestro tampoco cambia. Las pruebas lo verifican.
2. **Las cohortes nuevas sí necesitan la capa de equivalencias.** Sin ella, quien reprueba Matemáticas II (2011) y luego Cálculo integral (2018) aparece con dos cursos distintos, y la cuarta reprobación del art. 19 o la repitencia del art. 21 quedan sin detectar. Con la clave canónica se detectan. Hay un caso sintético en las pruebas que lo demuestra.
3. **Los datos muestran dos hechos que la documentación del proyecto no recogía:**
   - La cohorte **2018-1 cursó el plan 2011**: 39 de 44 estudiantes tienen `PENSUM 602`, y el primer registro `603` aparece en 2019-0, aunque el Acuerdo 001 de 2017 rige desde 2018-I. Es un desfase habitual mientras se implanta un plan nuevo, y la capa de equivalencias lo absorbe.
   - Los 16 estudiantes con `PENSUM 603` son **ingresos por homologación**: 16 de 20 tienen `HOMOLOGACION = SI` en `homologaciones.xlsx`. Son exactamente los 16 marcados con `sin_primer_semestre`. Ver `REVISION_FASES_2_3.md`, hallazgo R1.
4. **El modelo de alerta se puede aplicar a cohortes del plan 2018, pero hay que revisar sus umbrales.** El promedio del primer semestre se recompone porque Álgebra Lineal pasa a 2.º semestre. Ver §5.

## 2. Qué dicen los datos

| Programa | Cohorte | PENSUM 602 (2011) | PENSUM 603 (2018) |
|---|---|:---:|:---:|
| Ing. de Sistemas | 2017-2 | 35 | 11 |
| Ing. de Sistemas | 2018-1 | 39 | 5 |

Cobertura de la extracción (`python src/equivalencias.py`):

- 2 711 registros y 107 códigos de curso distintos.
- **0 códigos fuera de catálogo.**
- **0 discrepancias de créditos.**
- 4 diferencias de nombre, todas cosméticas. Por ejemplo, el extracto dice «LENGUAJE DE PROGRAMACIÓN» y el acuerdo dice «Lenguajes de programación».
- **0 estudiantes con planes mezclados.**

En **Ingeniería Electrónica** pasa lo mismo: hay dos planes (612 y 613) y 36 de los 37 estudiantes del 613 están marcados como `sin_primer_semestre`. **No se dispone de su resolución de equivalencias**, así que sus códigos pasan sin traducción (`EQUIV_FUENTE = 'sin_catalogo'`). Hay que solicitarla antes de ampliar el producto a ese programa.

## 3. En qué partes del pipeline importa el plan

| Componente | ¿Depende del curso? | Efecto sin equivalencias | Solución |
|---|---|---|---|
| Modelo de alerta (S3: `prom_sem1` y SABER 11) | No: usa el promedio del periodo y el ingreso | Ninguno mecánico; sí hay **desplazamiento de distribución** (§5) | Revisar los umbrales con la primera cohorte real del plan 2018 |
| Art. 19, cuarta reprobación | **Sí**: cuenta intentos del *mismo* curso | Repeticiones que cruzan planes no detectadas | `construir_target_art19(..., clave_curso='CODIGO_CANONICO')` |
| Art. 21 (segunda reprobación) y `max_veces_cursado` | **Sí** | Igual que el anterior | `panel_estudiante_periodo(..., clave_curso=...)`, `trayecta/motor.py` |
| Índice de criticidad | **Sí**: agrupa por asignatura | El mismo curso aparece partido en dos filas | `calcular_indice(canonico=True)` |
| Promedio ponderado acumulado y % de créditos reprobados | No: usan créditos y notas del registro | Ninguno | — |

## 4. Diseño de la capa de equivalencias

**Catálogo** (`catalogo_cursos.csv`): los dos planes transcritos de los acuerdos, con código, semestre, créditos, tipo, área, carácter institucional y requisitos. Las sumas reproducen los totales oficiales: 167 y 165 créditos, y 53 cursos en el plan 2018.

**Relaciones** (`equivalencias_IS_2011_2018.csv`, 72 filas: 32 del Art. 1, 35 del Art. 2 y 5 institucionales), con su sentido normativo:

- **Art. 1** (`continua_en_2011`): curso 2011 «a ver» ← curso 2018 «que puede tomar».
- **Art. 2** (`cambia_a_2018`): curso 2018 «a ver» ← curso 2011 «vista».
- **Parágrafo de cursos institucionales** (`institucional_inferida`): la resolución los homologa «directamente» sin listarlos. Aquí se emparejan por nombre y quedan marcados como inferidos.
- **Art. 2, parágrafo 2** (`sin_equivalente_IS_2018.csv`): 14 cursos 2018 que no tienen equivalente.

**Regla canónica.** La identidad de un curso es la de su equivalente en el **plan vigente (2018)**. La prioridad es Art. 2 > Art. 1 > institucional, porque el Art. 2 es el reconocimiento formal al cambiar de plan. Un curso 2011 sin equivalente conserva su propio código y queda marcado como `sin_equivalente`. Son ocho: Matemática Discreta, Teoría General de Sistemas, Probabilidad y Estadística, Control Análogo, Algoritmia Avanzada y los tres Cursos de Profundización.

**Asimetrías que declara la propia norma** (aparecen solo en el Art. 1): 602102 → 603102, 602301 → 603301, 602706 → 603606 y 602003 → 603004. Por ejemplo, Introducción e Estructuras de Datos del plan 2018 son exigibles a quien cambia de plan aunque el Art. 1 las acepte para quien continúa en el 2011. La capa las usa para la identidad del curso y las reporta en `verificar_consistencia()`.

**Fusiones n:1.**

- Ecuaciones Diferenciales y en Diferencia más Modelamiento de Sistemas (2011) corresponden a Ecuaciones Diferenciales y Modelado Matemático (2018).
- Las dos Electivas Complementarias (2011) corresponden a una sola (2018).

Para **contar intentos** se usa `CURSO_INTENTOS`, que en las fusiones conserva el código original. Así, cursar los dos cursos fusionados no se confunde con «repetir» uno. Hay una prueba específica para esto.

**Inconsistencias menores entre documentos** (registradas en la columna `observacion`):

- La Res. 036 ubica Matemáticas Especiales (603503) en el semestre «IV»; el Acuerdo 001 la ubica en el 5.
- La Res. 036 ubica 603403 en el semestre 3; el Acuerdo 001 la ubica en el 4.
- En ambos casos prevalece el acuerdo.

**Garantía de no ruptura.** Todas las funciones conservan el comportamiento histórico por defecto (`clave_curso='MATERIA'`, `canonico=False`). La normalización **añade** columnas (`PLAN`, `CODIGO_CANONICO`, `MATERIA_CANONICA`, `SEMESTRE_CANONICO`, `EQUIV_FUENTE`, `CURSO_INTENTOS`) y nunca modifica las originales. `materias_criticas.csv` se regenera idéntico y la versión canónica se escribe en un archivo aparte (`materias_criticas_canonicas.csv`).

## 5. Qué pasa con el modelo en una cohorte del plan 2018

El primer semestre cambia de composición:

- **Plan 2011:** 6 cursos y 18 créditos, Álgebra Lineal incluida.
- **Plan 2018:** 5 cursos y 16 créditos. Álgebra Lineal pasa a 2.º semestre.

Álgebra Lineal es la 3.ª asignatura más crítica del estudio. Para medir el efecto sin datos del plan nuevo se recalculó `prom_sem1` usando solo los cursos que siguen siendo de primer semestre en el plan 2018 (`src/analisis_cambio_plan.py`, RF con la configuración modal, CV-5 × 10):

| Escenario | n | AUC-PR | Línea base | Lift |
|---|:---:|:---:|:---:|:---:|
| A · Referencia (S3) | 80 | 0,751 | 0,238 | 3,16× |
| B · Sin el ingreso por homologación (PENSUM 603) | 74 | 0,756 | 0,230 | 3,29× |
| C1 · Composición 2018, **sin reentrenar** | 80 | 0,749 | 0,238 | 3,15× |
| C2 · Composición 2018, reentrenado | 80 | 0,740 | 0,238 | 3,11× |

**Lectura:**

- La correlación entre la variable original y la recompuesta es 0,983, y el modelo **conserva su capacidad de ordenamiento**.
- El promedio recompuesto es, en media, **+0,125 puntos más alto**, con un cambio mayor de 0,1 en 43 de 80 estudiantes. Por eso un umbral fijo dispararía **menos** alertas en el plan nuevo.
- **Protocolo recomendado:** aplicar el modelo sin reentrenar a la primera cohorte real del plan 2018 y revisar los umbrales con ella (es la validación externa P18). Esa cohorte debe además estar regida por el reglamento de 2022 (D-REGIMEN).

## 6. Cómo cargar una cohorte nueva

1. Exportar del SIIF los dos archivos con el formato de `trayecta/README.md`, **sin nombres**.
2. Ejecutar `python -c "import sys; sys.path.insert(0,'src'); import equivalencias as e, pandas as pd; print(e.validar(pd.read_excel('archivo.xlsx')))"` o usar la pantalla «Cargar cohorte» de TRAYECTA.
3. Si aparecen códigos fuera de catálogo, hay un plan nuevo o un programa sin catálogo. Se transcribe su acuerdo en `catalogo_cursos.csv`, su resolución en un CSV de equivalencias y se añade el prefijo en `PREFIJO_PLAN`.
4. Ejecutar `python -m pytest tests/ -q` antes de publicar cualquier cifra.

## 7. Índice de criticidad con identidad canónica

El top 5 **se conserva** al traducirlo al plan vigente. Es un resultado útil para el Programa, porque la intervención sigue apuntando a los mismos cursos con su nombre nuevo:

| # | Plan 2011 (índice) | Plan 2018, canónico (índice) |
|---|---|---|
| 1 | Matemáticas II (0,983) | Cálculo integral (0,983) |
| 2 | Física I (0,918) | Física mecánica (0,922) |
| 3 | Álgebra Lineal (0,835) | Álgebra lineal (0,814) |
| 4 | Matemáticas I (0,623) | Cálculo diferencial (0,623) |
| 5 | Fundamentos de Programación (0,534) | Algoritmia y programación (0,518) |

## 8. Pendientes

- **Solicitar la resolución de equivalencias de Ingeniería Electrónica** (planes 612 y 613).
- Validar con el Comité de Programa el emparejamiento de los cursos institucionales, que aquí es inferido.
