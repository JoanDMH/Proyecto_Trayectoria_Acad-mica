# -*- coding: utf-8 -*-
"""
modelos_bayesianos.py — Bloque B · Modelos bayesianos
Petición del asesor, 2026-09-29.

POR QUÉ AQUÍ SÍ TIENEN SENTIDO
------------------------------
Con n=80 y 19 positivos el problema no es la capacidad del modelo, es la
incertidumbre. Un enfoque bayesiano no promete más acierto: promete decir
CUÁNTO no sabe. Eso ataca de raíz el defecto encontrado el 16-09: la app
mostraba probabilidades mal calibradas en la banda media (decía 24 % donde la
tasa observada era 7 %) sin ninguna señal de que ese número fuese poco fiable.

Modelos evaluados, todos con el protocolo anidado de I-3 bis:

  B1  Naive Bayes gaussiano — la línea base bayesiana clásica.
  B2  Regresión logística bayesiana (PyMC, priores débilmente informativas
      Normal(0, 2,5) sobre coeficientes estandarizados). Da distribución
      posterior de cada coeficiente, no un punto.
  B3  Proceso gaussiano — bayesiano no paramétrico; su marco natural es
      precisamente el de muestras pequeñas.
  B4  Logística con regularización L2, que es el MAP de B2 con prior gaussiana.
      Se incluye para aislar cuánto aporta la integración sobre la posterior
      frente a quedarse con la moda.

Y lo que de verdad pide el asesor sin decirlo: B5 entrega el intervalo creíble
del 94 % de cada coeficiente sobre la muestra completa. Es una respuesta
bayesiana a la pregunta de selección de variables, independiente del PCA.

Uso:
    python src/modelos_bayesianos.py correr B1 B3 B4
    python src/modelos_bayesianos.py posterior
    python src/modelos_bayesianos.py tabla
"""
import os, sys, json
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnes_experimentos import (S3, V19, ETIQUETAS, cargar, evaluar,
                                comparar_contra, prevalencia, SRC, SEED)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.base import BaseEstimator, ClassifierMixin

SALIDA = os.path.join(SRC, '_resultados_bayes.json')


# -------------------------------- B2 · logística bayesiana (Laplace, rápida)
class LogisticaLaplace(BaseEstimator, ClassifierMixin):
    """Regresión logística bayesiana con aproximación de Laplace.

    Por qué Laplace y no MCMC dentro de la validación cruzada: cada ajuste con
    ADVI cuesta ~100 s (casi todo compilación de PyTensor), lo que pone las 500
    reajustes del protocolo anidado en ~14 horas. La aproximación de Laplace
    —gaussiana centrada en la moda con covarianza igual a la inversa del
    hessiano— es el método clásico para este caso (Bishop, §4.5) y con 6
    variables y n≈64 es muy fiel, porque la posterior de una logística con
    prior gaussiana es log-cóncava y casi gaussiana.

    La predicción NO usa la moda: integra sobre la posterior mediante la
    aproximación probit de MacKay, de modo que un caso alejado de los datos de
    entrenamiento recibe una probabilidad atraída hacia 0,5. Eso es exactamente
    lo que faltaba en la app: prudencia donde no hay evidencia.

    La inferencia completa por MCMC/ADVI sí se ejecuta, una sola vez, sobre la
    muestra entera en posterior().
    """

    def __init__(self, sigma=2.5):
        self.sigma = sigma

    def fit(self, X, y):
        from scipy.optimize import minimize
        self.classes_ = np.unique(y)
        self._sc = StandardScaler().fit(X)
        Z = np.column_stack([np.ones(len(X)), self._sc.transform(X)])
        t = y.astype(float)
        # prior: Normal(0, 2.5) en el intercepto y Normal(0, sigma) en las pendientes
        prec = np.concatenate([[1 / 2.5 ** 2], np.full(Z.shape[1] - 1, 1 / self.sigma ** 2)])

        def neg_log_post(w):
            a = Z @ w
            nll = np.sum(np.logaddexp(0, a) - t * a)
            return nll + 0.5 * np.sum(prec * w ** 2)

        def grad(w):
            p = 1 / (1 + np.exp(-(Z @ w)))
            return Z.T @ (p - t) + prec * w

        r = minimize(neg_log_post, np.zeros(Z.shape[1]), jac=grad, method='L-BFGS-B')
        self.w_ = r.x
        p = 1 / (1 + np.exp(-(Z @ self.w_)))
        H = (Z * (p * (1 - p))[:, None]).T @ Z + np.diag(prec)
        self.cov_ = np.linalg.pinv(H)
        return self

    def _mu_var(self, X):
        Z = np.column_stack([np.ones(len(X)), self._sc.transform(X)])
        mu = Z @ self.w_
        var = np.einsum('ij,jk,ik->i', Z, self.cov_, Z)
        return mu, np.maximum(var, 0.0)

    def predict_proba(self, X):
        mu, var = self._mu_var(X)
        # aproximacion probit: integra la logistica sobre la gaussiana posterior
        p = 1 / (1 + np.exp(-mu / np.sqrt(1 + np.pi * var / 8)))
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]

    def incertidumbre(self, X):
        """Anchura aproximada del intervalo creíble del 94 % de cada caso."""
        mu, var = self._mu_var(X)
        s = np.sqrt(var)
        lo = 1 / (1 + np.exp(-(mu - 1.881 * s)))
        hi = 1 / (1 + np.exp(-(mu + 1.881 * s)))
        return hi - lo


# ------------------------------------------- B6 · logística bayesiana (PyMC)
class LogisticaBayesiana(BaseEstimator, ClassifierMixin):
    """Regresión logística con inferencia variacional (ADVI).

    Prior Normal(0, sigma) sobre coeficientes estandarizados: débilmente
    informativa, mantiene los coeficientes en un rango plausible sin imponer
    un signo. Con 19 positivos, el prior es lo que evita la separación
    perfecta que haría divergir la estimación por máxima verosimilitud.
    """

    def __init__(self, sigma=2.5, n_iter=12000, draws=600, seed=SEED):
        self.sigma, self.n_iter, self.draws, self.seed = sigma, n_iter, draws, seed

    def fit(self, X, y):
        import pymc as pm
        self.classes_ = np.unique(y)
        self._sc = StandardScaler().fit(X)
        Z = self._sc.transform(X)
        with pm.Model() as m:
            a = pm.Normal('a', 0.0, 2.5)
            b = pm.Normal('b', 0.0, self.sigma, shape=Z.shape[1])
            pm.Bernoulli('y', logit_p=a + pm.math.dot(Z, b), observed=y)
            aprox = pm.fit(self.n_iter, method='advi',
                           random_seed=self.seed, progressbar=False)
            idata = aprox.sample(self.draws, random_seed=self.seed)
        self.a_ = idata.posterior['a'].values.reshape(-1)
        self.b_ = idata.posterior['b'].values.reshape(-1, Z.shape[1])
        return self

    def predict_proba(self, X):
        Z = self._sc.transform(X)
        logit = self.a_[:, None] + self.b_ @ Z.T        # (draws, n)
        p = 1.0 / (1.0 + np.exp(-logit))
        # media de la posterior predictiva: integra sobre la incertidumbre
        pm_ = p.mean(axis=0)
        return np.column_stack([1 - pm_, pm_])

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]

    def incertidumbre(self, X):
        """Anchura del intervalo creíble del 94 % de la probabilidad por caso."""
        Z = self._sc.transform(X)
        p = 1.0 / (1.0 + np.exp(-(self.a_[:, None] + self.b_ @ Z.T)))
        return np.percentile(p, 97, axis=0) - np.percentile(p, 3, axis=0)


def _gp():
    k = ConstantKernel(1.0, (1e-2, 1e2)) * RBF(1.0, (1e-1, 1e2)) \
        + WhiteKernel(1e-2, (1e-5, 1e0))
    return GaussianProcessClassifier(kernel=k, random_state=SEED,
                                     n_restarts_optimizer=0, max_iter_predict=60)


CONFIGS = {
    'B0': ('A0 · S3 (6 variables) · Random Forest',
           lambda: Pipeline([('sc', StandardScaler()),
                             ('clf', RandomForestClassifier(random_state=SEED, n_jobs=1))]),
           S3, {'clf__n_estimators': [200], 'clf__max_depth': [3, 4, None],
                'clf__min_samples_leaf': [1, 2]}),
    'B1': ('B1 · Naive Bayes gaussiano',
           lambda: Pipeline([('sc', StandardScaler()), ('clf', GaussianNB())]),
           S3, {'clf__var_smoothing': [1e-9, 1e-7, 1e-5, 1e-3]}),
    'B2': ('B2 · Logística bayesiana (Laplace)',
           LogisticaLaplace, S3, {'sigma': [0.5, 1.0, 2.5, 5.0]}),
    'B2b': ('B2b · Logística bayesiana (Laplace) · 19 variables',
            LogisticaLaplace, V19, {'sigma': [0.5, 1.0, 2.5, 5.0]}),
    'B3': ('B3 · Proceso gaussiano',
           _gp, S3, None),
    'B4': ('B4 · Logística L2 (MAP de B2)',
           lambda: Pipeline([('sc', StandardScaler()),
                             ('clf', LogisticRegression(max_iter=4000))]),
           S3, {'clf__C': [0.02, 0.1, 0.4, 1.0, 4.0]}),
    'B7': ('B7 · S3 sin SABER-total (VIF 6,7) · Random Forest',
           lambda: Pipeline([('sc', StandardScaler()),
                             ('clf', RandomForestClassifier(random_state=SEED, n_jobs=1))]),
           ['prom_sem1', 'sin_primer_semestre', 'icfes_mat', 'icfes_lec', 'icfes_nat'],
           {'clf__n_estimators': [200], 'clf__max_depth': [3, 4, None],
            'clf__min_samples_leaf': [1, 2]}),
    'B8': ('B8 · S3 sin SABER-total · Logística bayesiana',
           LogisticaLaplace,
           ['prom_sem1', 'sin_primer_semestre', 'icfes_mat', 'icfes_lec', 'icfes_nat'],
           {'sigma': [0.5, 1.0, 2.5, 5.0]}),
    'B5': ('B5 · Naive Bayes gaussiano · 19 variables',
           lambda: Pipeline([('sc', StandardScaler()), ('clf', GaussianNB())]),
           V19, {'clf__var_smoothing': [1e-9, 1e-7, 1e-5, 1e-3]}),
}


def correr(claves):
    for k in claves:
        nombre, constructor, variables, grid = CONFIGS[k]
        print(f'· {k} …', flush=True)
        evaluar(nombre, constructor, variables=variables, grid=grid)


# ============================================ B6 · posterior sobre la muestra
def posterior():
    """Distribución posterior de los coeficientes con toda la muestra.

    Es descriptivo, no una estimación de desempeño: sirve para leer qué
    variables tienen efecto creíblemente distinto de cero.
    """
    X, y, nombres = cargar(S3)
    mod = LogisticaBayesiana(sigma=2.5, n_iter=30000, draws=3000).fit(X, y)
    print('═' * 78)
    print('B6 · POSTERIOR DE LOS COEFICIENTES (muestra completa, n=80)')
    print('═' * 78)
    print('Coeficientes sobre variables estandarizadas: comparables entre sí.')
    print('El intervalo creíble del 94 % que NO contiene el cero indica un efecto')
    print('que los datos sostienen; el que lo contiene, uno que no se distingue.\n')
    print(f'{"Variable":32s} {"media":>8s} {"IC 94 % inferior":>17s} {"superior":>10s}'
          f' {"P(β<0)":>8s}  veredicto')
    filas = []
    for j, v in enumerate(nombres):
        b = mod.b_[:, j]
        lo, hi = np.percentile(b, [3, 97])
        pneg = float((b < 0).mean())
        cred = (lo > 0) or (hi < 0)
        ver = 'efecto creíble' if cred else 'no distinguible de cero'
        print(f'{ETIQUETAS.get(v, v):32s} {b.mean():>+8.3f} {lo:>+17.3f} {hi:>+10.3f}'
              f' {pneg:>8.3f}  {ver}')
        filas.append({'Variable': ETIQUETAS.get(v, v),
                      'Media posterior': round(float(b.mean()), 4),
                      'IC 94 % inferior': round(float(lo), 4),
                      'IC 94 % superior': round(float(hi), 4),
                      'P(β<0)': round(pneg, 4),
                      'Veredicto': ver})

    anchura = mod.incertidumbre(X)
    p = mod.predict_proba(X)[:, 1]
    print(f'\nIncertidumbre por estudiante (anchura del IC 94 % de su probabilidad):')
    print(f'   mediana {np.median(anchura):.3f} · mínimo {anchura.min():.3f} '
          f'· máximo {anchura.max():.3f}')
    print(f'   Casos con IC más ancho que 0,30: {int((anchura > 0.30).sum())} de {len(y)}'
          f'  ({(anchura > 0.30).mean():.0%})')
    print('\n   Lectura: en esos casos el modelo no está en condiciones de emitir un')
    print('   número; la app debería mostrar "sin evidencia suficiente" en vez de un %.')

    return {'coeficientes': filas,
            'incertidumbre': {
                'mediana': round(float(np.median(anchura)), 4),
                'min': round(float(anchura.min()), 4),
                'max': round(float(anchura.max()), 4),
                'n_ancho_mayor_030': int((anchura > 0.30).sum()),
                'pct_ancho_mayor_030': round(float((anchura > 0.30).mean()), 4)},
            'proba': p.tolist(), 'anchura': anchura.tolist()}


def tabla_comparativa():
    prev = prevalencia()
    base = evaluar(CONFIGS['B0'][0], CONFIGS['B0'][1], variables=CONFIGS['B0'][2],
                   grid=CONFIGS['B0'][3], verbose=False)
    claves = [k for k in ['B1','B2','B2b','B3','B4','B5','B7','B8']
              if os.path.exists(os.path.join(SRC, '_cache_experimentos',
                                             CONFIGS[k][0] + '.json'))]
    otros = [evaluar(CONFIGS[k][0], CONFIGS[k][1], variables=CONFIGS[k][2],
                     grid=CONFIGS[k][3], verbose=False) for k in claves]
    tabla = comparar_contra(base, otros)
    print('═' * 78)
    print('B · MODELOS BAYESIANOS FRENTE A LA REFERENCIA')
    print('═' * 78)
    print(f'Referencia = {base["nombre"]} · AUC-PR {np.mean(base["ap"]):.4f}'
          f'   (azar = {prev:.4f})\n')
    print(tabla.to_string(index=False))
    return {'base': {'nombre': base['nombre'],
                     'ap': round(float(np.mean(base['ap'])), 4),
                     'de': round(float(np.std(base['ap'])), 4),
                     'roc': round(float(np.mean(base['roc'])), 4)},
            'tabla': tabla.to_dict('records'), 'prevalencia': round(prev, 4)}


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else 'todo'
    out = json.load(open(SALIDA, encoding='utf8')) if os.path.exists(SALIDA) else {}
    if modo == 'correr':
        correr(sys.argv[2:] or list(CONFIGS))
        return
    elif modo == 'posterior':
        out['posterior'] = posterior()
    elif modo == 'tabla':
        out['comparativa'] = tabla_comparativa()
    else:
        correr(list(CONFIGS))
        out['comparativa'] = tabla_comparativa()
        out['posterior'] = posterior()
    json.dump(out, open(SALIDA, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f'\n[OK] {SALIDA}')


if __name__ == '__main__':
    main()
