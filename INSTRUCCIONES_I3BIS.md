# I-3 bis — Instrucciones de ejecución
**Script:** `src/entrenar_i3bis.py` · **Preparado:** 2026-09-15 · **Registrar en:** RC-033

El sandbox de esta sesión corta las ejecuciones a ~175 s y Random Forest necesita
más de 110 s por repetición, así que la corrida completa debe hacerse en tu máquina.
El script ya está probado: tres de los cinco modelos corrieron sin problemas.

---

## Qué cambia respecto a I-3

| Corrección | Detalle | Registro |
|---|---|---|
| **Variables** | S3 (6 académicas) en lugar de 19. Iguala al set completo (Δ=−0,0005; p=0,983) sin selección guiada por los datos | RC-032 |
| **Presupuesto equilibrado** | Todas las rejillas entre 16 y 24 combinaciones. Antes: 8 para XGBoost frente a 48 para RF (desventaja de 6:1) | RC-025 |
| **XGBoost** | `min_child_weight=1` fijo y `reg_lambda` en rango bajo. Regularizar agresivamente hunde el AUC-PR con 19 positivos | RC-031 |
| **Población de `graduado`** | n=90, no 80. Los 10 sin actividad son negativos legítimos — ninguno se graduó | — |
| **Instrumentación** | Métricas por repetición, hiperparámetros de cada pliegue, versiones y hash de los datos | RC-027 |

Repeticiones: **10** (antes 15), para acotar el costo con las rejillas ampliadas.

---

## Ejecución

```bash
cd C:\Users\Admin\Desktop\proyecto_rendimiento_academico

# Un modelo por vez (se acumulan en caché). Nombre parcial, sin distinguir mayúsculas.
python src/entrenar_i3bis.py art19 "Logística"
python src/entrenar_i3bis.py art19 "Árbol"
python src/entrenar_i3bis.py art19 "Random Forest"
python src/entrenar_i3bis.py art19 "SVM"
python src/entrenar_i3bis.py art19 "XGBoost"

# O los cinco de una vez, si tu máquina aguanta:
python src/entrenar_i3bis.py art19

# Después, el target de graduación (n=90):
python src/entrenar_i3bis.py graduado

# Finalmente, tablas y contrastes:
python src/entrenar_i3bis.py consolidar
```

**Tiempo estimado en tu máquina:** Random Forest es el más costoso; los demás
rondan los 30–45 s cada uno con 10 repeticiones.

---

## Estado actual del caché

Ya corrieron y están guardados en `src/_i3bis_cache/art19.pkl`:

| Modelo | AUC-PR | sd |
|---|:---:|:---:|
| SVM (RBF) | 0,7136 | ±0,0368 |
| Árbol de Decisión | 0,6144 | ±0,0549 |
| Regresión Logística (L2) | 0,5495 | ±0,0877 |

Faltan **Random Forest** y **XGBoost**. El caché es incremental: al ejecutarlos se
suman a los anteriores sin repetir lo hecho.

> Si prefieres empezar de cero: `rmdir /s /q src\_i3bis_cache`

### Ejecución en paralelo

**Ya es seguro.** Cada modelo escribe su propio archivo de caché
(`art19__Random_Forest.pkl`, `art19__XGBoost.pkl`, …), así que puedes lanzar
varias ventanas a la vez sin que se pisen.

> ⚠️ En la versión anterior del script todos escribían en el mismo `art19.pkl`
> con el patrón leer-actualizar-escribir: si dos corrían en paralelo, el último
> en terminar sobrescribía al otro. Corregido el 2026-09-15.

Al terminar, `consolidar` avisa explícitamente si falta algún modelo.

Línea base de AUC-PR (clasificador aleatorio) = prevalencia = **0,2375**.

---

## Salidas que genera

| Archivo | Contenido |
|---|---|
| `src/i3bis_tabla_art19.csv` | AUC-PR media, sd e IC 95 % por algoritmo |
| `src/i3bis_tabla_graduado.csv` | Idem para graduación |
| `src/i3bis_comparaciones_*.csv` | Todos los contrastes pareados con Nadeau-Bengio |
| `src/i3bis_curva_umbrales.csv` | Curva de umbral del modelo ganador |
| `bitacora/<fecha>_I3bis_*/` | Contexto, métricas por repetición, hiperparámetros por pliegue, estabilidad |

---

## Cómo leer el resultado

1. **AUC-PR contra 0,2375**, no contra 0,5. Un 0,55 es más del doble del azar.
2. **Regla de decisión pre-registrada:** si la diferencia entre los mejores es
   < 0,03 de AUC-PR, es **empate técnico**. El script lo declara solo.
3. **Si vuelve a haber empate, no fuerces un ganador.** Con n=80 ese es el
   resultado honesto, y ya está documentado que el target pesa mucho más que el
   algoritmo. Si eliges uno igualmente, **declara la desviación** como se hizo en
   RC-023.
4. **Revisa `estabilidad_hiperparametros.csv`** en la bitácora: si la configuración
   ganadora cambia en casi todos los pliegues, la búsqueda está dominada por el
   ruido — dato reportable, no un defecto que ocultar.

---

## Verificación de reproducibilidad (opcional, recomendado)

Ejecuta dos veces y compara. Con `SEED=42` y las mismas versiones debe dar idéntico:

```python
from src.instrumentacion import comparar_corridas
iguales, informe = comparar_corridas('bitacora/<corrida_1>', 'bitacora/<corrida_2>')
print(iguales); print(informe)
```

Eso te permite afirmar en el informe que los resultados son reproducibles —
afirmación que solo se sostiene si se ejecuta dos veces.

⚠️ `requirements.txt` fija scikit-learn 1.8.0 y xgboost 3.2.0. No cambies esas
versiones entre corridas.
