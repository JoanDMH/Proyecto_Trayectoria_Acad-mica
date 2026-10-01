"""
comparacion_estadistica.py
Utilidades para comparar algoritmos de forma estadísticamente honesta con n pequeño.

Preparado para el paso I-3 (RC-016, RC-021). Resuelve dos errores frecuentes:

1. Comparar AUC medios sin medir incertidumbre → "ganadores" que son ruido.
2. Aplicar un t-test o Wilcoxon ordinario sobre repeticiones de validación cruzada
   → los p-valores salen inflados, porque las repeticiones reutilizan los mismos
   datos y NO son independientes.

La corrección de Nadeau-Bengio (2003) ajusta la varianza por ese solapamiento.
Es el estándar para comparar modelos con CV repetida.

Uso típico:

    from comparacion_estadistica import evaluar_repetido, comparar, tabla_comparativa

    res = {nombre: evaluar_repetido(est, X, y) for nombre, est in modelos.items()}
    print(tabla_comparativa(res))
    print(comparar(res['Random Forest'], res['XGBoost'], 'RF', 'XGB'))
"""
import numpy as np
from scipy import stats
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score

SEED = 42

# Umbral de relevancia PRÁCTICA pre-registrado (RC-016): por debajo de esta
# diferencia de AUC se declara empate técnico y se elige el modelo más simple,
# aunque la prueba estadística resulte significativa.
DELTA_RELEVANTE = 0.03


def evaluar_repetido(estimador_factory, X, y, n_rep=15, n_splits=5, seed=SEED,
                     metrica=roc_auc_score):
    """
    Evalúa un estimador con validación cruzada estratificada repetida.

    `estimador_factory` debe ser un CALLABLE que devuelva un estimador NUEVO en
    cada llamada (p. ej. `lambda: RandomForestClassifier(...)`). Si se pasa un
    GridSearchCV, la búsqueda de hiperparámetros ocurre dentro de cada pliegue
    de entrenamiento (validación anidada), que es lo correcto — ver RC-021.

    Retorna array con la métrica de cada repetición (longitud n_rep).
    """
    vals = []
    for r in range(n_rep):
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed + r)
        p = cross_val_predict(estimador_factory(), X, y, cv=cv,
                              method='predict_proba', n_jobs=-1)[:, 1]
        vals.append(metrica(y, p))
    return np.array(vals)


def t_corregido_nadeau_bengio(a, b, n_splits=5):
    """
    t-test pareado con corrección de Nadeau-Bengio para validación cruzada repetida.

    a, b : arrays con la métrica por repetición de dos modelos (mismos pliegues).
    n_splits : nº de pliegues usados (define la proporción test/train).

    La varianza se infla por el factor (1/k + n_test/n_train), donde para k-fold
    n_test/n_train = 1/(k-1). Sin esa corrección el p-valor es anticonservador.

    Retorna (t, p_valor, diferencia_media).
    """
    d = np.asarray(a, float) - np.asarray(b, float)
    n = len(d)
    if n < 2:
        return np.nan, np.nan, float(np.mean(d)) if n else np.nan
    dif = d.mean()
    var = d.var(ddof=1)
    if var == 0:
        return np.inf if dif else 0.0, 0.0 if dif else 1.0, dif
    correccion = 1.0 / n + 1.0 / (n_splits - 1)
    t = dif / np.sqrt(correccion * var)
    p = 2 * (1 - stats.t.cdf(abs(t), df=n - 1))
    return float(t), float(p), float(dif)


def comparar(a, b, nombre_a='A', nombre_b='B', n_splits=5, alpha=0.05,
             delta=DELTA_RELEVANTE):
    """
    Compara dos modelos y emite un veredicto que combina significancia
    estadística con relevancia práctica.

    Retorna dict con las cifras y el veredicto en texto.
    """
    t, p, dif = t_corregido_nadeau_bengio(a, b, n_splits)
    signif = p < alpha
    relevante = abs(dif) > delta
    if signif and relevante:
        ganador = nombre_a if dif > 0 else nombre_b
        veredicto = f'{ganador} es mejor (diferencia significativa y relevante)'
    elif signif and not relevante:
        veredicto = (f'EMPATE TÉCNICO: la diferencia es significativa (p={p:.3f}) '
                     f'pero de magnitud irrelevante (|Δ|={abs(dif):.3f} < {delta}). '
                     f'Elegir el modelo más simple.')
    else:
        veredicto = (f'EMPATE: sin evidencia de diferencia (p={p:.3f}). '
                     f'Elegir el modelo más simple.')
    return {'modelo_a': nombre_a, 'modelo_b': nombre_b,
            'media_a': float(np.mean(a)), 'media_b': float(np.mean(b)),
            'diferencia': dif, 't': t, 'p_valor': p,
            'significativo': bool(signif), 'relevante': bool(relevante),
            'veredicto': veredicto}


def tabla_comparativa(resultados, n_splits=5):
    """
    `resultados`: dict {nombre: array de métricas por repetición}.
    Devuelve un string con media, desviación e intervalo de confianza al 95 %.
    """
    filas = []
    for nom, v in sorted(resultados.items(), key=lambda x: -np.mean(x[1])):
        v = np.asarray(v, float)
        lo, hi = np.percentile(v, [2.5, 97.5])
        filas.append(f'{nom:20s} {v.mean():.3f}  ±{v.std():.3f}   [{lo:.3f}–{hi:.3f}]')
    cab = f"{'algoritmo':20s} {'AUC':>5s}   {'sd':>5s}   {'IC 95 %':>13s}"
    return cab + '\n' + '-' * len(cab) + '\n' + '\n'.join(filas)


def matriz_comparaciones(resultados, n_splits=5):
    """Compara todos los pares y devuelve lista de dicts ordenada por |diferencia|."""
    nombres = list(resultados)
    out = []
    for i in range(len(nombres)):
        for j in range(i + 1, len(nombres)):
            a, b = nombres[i], nombres[j]
            out.append(comparar(resultados[a], resultados[b], a, b, n_splits))
    return sorted(out, key=lambda d: -abs(d['diferencia']))


if __name__ == '__main__':
    # Demostración de la corrección con datos sintéticos
    rng = np.random.RandomState(SEED)
    base = rng.normal(0.80, 0.03, 30)
    otro = base + rng.normal(0.008, 0.02, 30)   # ventaja diminuta
    t0, p0 = stats.ttest_rel(otro, base)[:2]
    t1, p1, d1 = t_corregido_nadeau_bengio(otro, base)
    print(f't-test ordinario     : p={p0:.4f}   <- anticonservador')
    print(f't Nadeau-Bengio      : p={p1:.4f}   <- correcto')
    print(f'diferencia media     : {d1:+.4f}')
