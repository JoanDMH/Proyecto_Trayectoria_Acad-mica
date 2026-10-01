# ESPECIFICACIÓN DEL PASO I-3
### Re-entrenamiento y comparación de algoritmos con el target normativo
**Estado:** listo para ejecutar · **Depende de:** I-1 (RC-017), I-2 (RC-018), I-2b (RC-020)
**Ejecuta:** Joan · **Preparado por:** auditoría · **Registrar en:** RC-022

---

## 1. Punto de partida (ya resuelto, no rehacer)

| Elemento | Estado |
|---|---|
| Dataset | `src/df_master_limpio.csv` (90 × 37), regenerado y verificado |
| Target vigente | `bajo_rendimiento_art19` — **19 positivos de 80** (23,8 %), sin casos ambiguos |
| Población de análisis | `tiene_actividad_academica == 1` → **n = 80** |
| Features | **19** (las 18 anteriores + `sin_primer_semestre`) |
| Utilidad estadística | `src/comparacion_estadistica.py` (probada) |

```python
import pandas as pd
d = pd.read_csv('src/df_master_limpio.csv')
e = d[d.tiene_actividad_academica == 1]          # n=80
y = e['bajo_rendimiento_art19'].astype(int)      # 19 positivos
```

> ⚠️ **No usar `rendimiento_bajo`.** Está marcado como obsoleto (RC-012). Sigue en el
> archivo solo para comparaciones antes/después.

---

## 2. Protocolo pre-registrado

Fijar esto **antes** de ver resultados. Cambiarlo después invalida la comparación.

### 2.1 Algoritmos (los cinco de la propuesta)

| Algoritmo | Notas |
|---|---|
| Regresión logística (L2) | **Línea base declarada.** Dentro de `Pipeline` con `StandardScaler` |
| Árbol de decisión | — |
| Random Forest | — |
| SVM (RBF) | Dentro de `Pipeline` con `StandardScaler`; `probability=True` |
| XGBoost | — |

El escalado **debe ir dentro del pipeline**, nunca aplicado antes de la validación
cruzada: escalar con la media de todo el conjunto filtra información de los pliegues
de prueba.

### 2.2 Validación

- `SEED = 42` en todo.
- **CV-5 estratificada repetida**, 15 repeticiones. Reportar media ± desviación e IC 95 %.
- Predicciones **out-of-fold** exclusivamente (`cross_val_predict`). Prohibido reportar métricas in-sample.
- **Búsqueda de hiperparámetros ANIDADA** — ver §3, es el punto crítico de este paso.
- Sin SMOTE (RC-004). Evaluar `class_weight='balanced'` como variante, no como base.

### 2.3 Sin conjunto de prueba retenido

El split 72/18 de `train_test_split.json` **queda sin efecto**: fue calculado sobre
90 estudiantes y el target antiguo. Con n = 80 y 19 positivos, un holdout del 20 %
tendría ~4 positivos: cualquier métrica sobre él sería ruido puro.

**Decisión:** reportar únicamente validación cruzada repetida, y justificarlo en el
informe. Es metodológicamente más sólido que un holdout minúsculo.

### 2.4 Métricas

Reportar todas; **AUC-PR es la métrica principal** con 24 % de positivos, porque el
AUC-ROC es optimista con clases desbalanceadas.

`AUC-PR (average_precision)` · `AUC-ROC` · `Recall+` · `Precisión+` · `F1+` ·
`F1-macro` · `MCC` · `Exactitud`

### 2.5 Criterio de selección del ganador

1. Comparar por AUC-PR con `comparacion_estadistica.comparar()`.
2. **Umbral de relevancia práctica: ΔAUC ≥ 0,03** (RC-016).
3. Si la diferencia es menor a 0,03 → **empate técnico**, se elige el modelo **más simple e interpretable** (orden de preferencia: logística → árbol → RF → XGBoost → SVM).
4. Prohibido declarar ganador por diferencias de la tercera cifra decimal.

### 2.6 Umbral de decisión

Ajustar sobre probabilidades out-of-fold, **no** heredar el 0,29 anterior (correspondía
a otro target). Reportar la tabla de umbral y justificar el elegido por el costo del
falso negativo en alertas tempranas.

---

## 3. ⚠️ Corrección obligatoria: validación anidada

`src/entrenar_principal.py` contiene actualmente este patrón:

```python
gs = GridSearchCV(base, grid, cv=cv, ...)
gs.fit(X, y)                                   # ← usa TODOS los datos
p = cross_val_predict(gs.best_estimator_, X, y, cv=cv, ...)
```

Los hiperparámetros se eligen viendo el conjunto completo, incluidos los pliegues que
después se usan como prueba. **El AUC resultante está sesgado al alza.**

Sesgo medido sobre el target nuevo (CV-5, 3 repeticiones):

| Algoritmo | Método actual | Anidado (correcto) | Sesgo |
|---|---|---|---|
| Árbol de decisión | 0,757 | 0,745 | +0,011 |
| Random Forest | 0,800 | 0,792 | +0,008 |
| **XGBoost** | **0,826** | **0,780** | **+0,046** |

**El sesgo no es uniforme: XGBoost se beneficia cinco veces más que Random Forest.**
Con el método actual XGBoost ganaría (0,826 vs 0,800); con validación anidada el orden
se invierte (0,792 vs 0,780). El protocolo decide el ganador, no los datos.

**Corrección:** pasar el objeto `GridSearchCV` como estimador, para que la búsqueda
ocurra dentro de cada pliegue de entrenamiento.

```python
inner = StratifiedKFold(4, shuffle=True, random_state=SEED+100)
gs = GridSearchCV(base, grid, cv=inner, scoring='average_precision', n_jobs=-1)
p = cross_val_predict(gs, X, y, cv=cv_externo, method='predict_proba')[:, 1]
```

`evaluar_repetido()` de `comparacion_estadistica.py` acepta directamente un
`GridSearchCV` como factory, así que basta con pasarlo.

---

## 4. Cambios concretos en `src/entrenar_principal.py`

1. `FEATURES` → añadir `'sin_primer_semestre'` (queda en 19).
2. `data(target)` → filtrar `tiene_actividad_academica == 1` antes de `dropna()`.
3. Añadir los dos algoritmos faltantes: regresión logística L2 y SVM-RBF, ambos en `Pipeline` con `StandardScaler`.
4. Reemplazar el patrón `gs.fit(X,y)` + `cross_val_predict(best)` por validación anidada (§3).
5. `UMBRAL` → recalcular; no heredar 0,29.
6. `scoring` de la búsqueda → `'average_precision'` en lugar de `'f1_weighted'`, coherente con la métrica principal.
7. Guardar las métricas por repetición (no solo la media) para poder aplicar la prueba pareada.

**Objetivo `graduado`:** se mantiene sin cambios de definición (no está afectado por
RC-012), pero debe re-evaluarse con el mismo protocolo corregido para que ambas
comparativas sean homogéneas.

---

## 5. Criterios de aceptación

- [ ] `comparativa_bajo_rendimiento_art19.csv` y `comparativa_graduado.csv` con las 8 métricas para los 5 algoritmos.
- [ ] Tabla con media ± sd e IC 95 % por algoritmo (`tabla_comparativa`).
- [ ] Matriz de comparaciones pareadas con p-valor corregido (`matriz_comparaciones`).
- [ ] Veredicto explícito del ganador **o** declaración de empate técnico según §2.5.
- [ ] Curva de umbral y justificación del umbral elegido.
- [ ] Entrada RC-022 con motivación, método, resultados y decisión.
- [ ] Todas las cifras regenerables ejecutando el script; ninguna escrita a mano.

---

## 6. Qué esperar (referencia, no objetivo)

Con hiperparámetros fijos y sin anidar, CV-5 × 15 repeticiones sobre el target nuevo:

| Algoritmo | AUC-ROC |
|---|---|
| XGBoost | 0,829 ± 0,033 |
| Random Forest | 0,825 ± 0,021 |
| LogReg (L2) | 0,775 ± 0,034 |
| Árbol de decisión | 0,761 ± 0,039 |

Prueba pareada corregida entre los dos primeros: **p = 0,836 → empate**. Con validación
anidada es probable que Random Forest quede por delante de XGBoost.

**No ajustes el protocolo para obtener un ganador.** Si el resultado honesto es un
empate entre tres algoritmos, ese es el resultado — y es reportable: significa que con
n = 80 la elección del algoritmo importa menos que la definición del target, que es
precisamente el hallazgo central de esta auditoría.

---

## 7. Después de I-3

`I-4` (retirar los modelos de reprobación) es independiente y puede ejecutarse en
paralelo. `I-5` (verificación de Electrónica y Biología) depende de que I-3 cierre.
