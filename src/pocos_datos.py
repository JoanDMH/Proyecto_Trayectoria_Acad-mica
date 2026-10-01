# -*- coding: utf-8 -*-
"""
pocos_datos.py — Bloque C · Aprendizaje con pocos datos
Petición del asesor, 2026-09-29.

SOBRE "ONE-SHOT LEARNING": QUÉ SE PUEDE Y QUÉ NO
------------------------------------------------
El one-shot / few-shot learning en sentido estricto es un paradigma para
reconocer CLASES NUEVAS a partir de uno o pocos ejemplos, y descansa sobre dos
cosas que aquí no existen:

  1. un corpus grande de preentrenamiento del que transferir una representación
     (ImageNet, un corpus de texto), y
  2. una estructura por episodios en la que en prueba aparecen clases que no se
     vieron en entrenamiento.

Nuestro problema es tabular, binario, con las dos clases presentes desde el
principio y sin corpus del que transferir. Aplicar literalmente una red siamesa
o una ProtoNet sería ponerle nombre de moda a un clasificador corriente.

Lo que sí se traslada, y es lo que se ejecuta, es el MECANISMO que hace que esas
arquitecturas funcionen con pocos ejemplos: aprender una métrica y clasificar
por cercanía a un prototipo de clase. De hecho ProtoNet, despojada de la red, ES
la clasificación por media de clase en un espacio métrico aprendido. Por eso:

  C1  Prototipos (media de clase, distancia euclídea sobre variables tipificadas)
      — el equivalente tabular exacto de ProtoNet.
  C2  NCA + prototipos — NCA aprende la métrica, que es el papel de la red
      siamesa: acercar lo semejante y separar lo distinto.
  C3  NCA + k vecinos — la variante por vecindario en vez de por centroide.
  C4  k vecinos sin métrica aprendida, como control.

Y el resultado que de verdad interesa al asesor tras pedir cohortes nuevas:

  C5  CURVA DE TAMAÑO MUESTRAL. Cuánto mejora el modelo al crecer n, ajustada a
      una ley de potencias y extrapolada a los tamaños que traerían las cohortes
      nuevas. Es la estimación cuantitativa de qué compra la petición de datos.

Uso:
    python src/pocos_datos.py correr
    python src/pocos_datos.py curva
    python src/pocos_datos.py tabla
"""
import os, sys, json
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnes_experimentos import (S3, cargar, evaluar, comparar_contra,
                                prevalencia, SRC, SEED, N_REP, N_EXT)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier, NeighborhoodComponentsAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, StratifiedShuffleSplit
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.base import BaseEstimator, ClassifierMixin
from scipy.optimize import curve_fit

SALIDA = os.path.join(SRC, '_resultados_pocos.json')


class Prototipos(BaseEstimator, ClassifierMixin):
    """Clasificador por media de clase: el análogo tabular de ProtoNet.

    Se calcula el centroide de cada clase en el espacio (opcionalmente
    transformado por NCA) y se puntúa por distancia relativa a los dos
    centroides, convertida a probabilidad con una softmax de temperatura T.
    """

    def __init__(self, metrica='euclidea', T=1.0, n_components=None):
        self.metrica, self.T, self.n_components = metrica, T, n_components

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        self._sc = StandardScaler().fit(X)
        Z = self._sc.transform(X)
        self._nca = None
        if self.metrica == 'nca':
            k = self.n_components or min(X.shape[1], 4)
            self._nca = NeighborhoodComponentsAnalysis(
                n_components=k, random_state=SEED, max_iter=120).fit(Z, y)
            Z = self._nca.transform(Z)
        self._cent = np.vstack([Z[y == c].mean(axis=0) for c in self.classes_])
        return self

    def _proj(self, X):
        Z = self._sc.transform(X)
        return self._nca.transform(Z) if self._nca is not None else Z

    def predict_proba(self, X):
        Z = self._proj(X)
        d = np.linalg.norm(Z[:, None, :] - self._cent[None, :, :], axis=2)
        logits = -d / max(self.T, 1e-6)
        logits -= logits.max(axis=1, keepdims=True)
        e = np.exp(logits)
        return e / e.sum(axis=1, keepdims=True)

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]


class NCAkNN(BaseEstimator, ClassifierMixin):
    """NCA (métrica aprendida) seguido de k vecinos."""

    def __init__(self, n_components=3, n_neighbors=7):
        self.n_components, self.n_neighbors = n_components, n_neighbors

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        self._sc = StandardScaler().fit(X)
        Z = self._sc.transform(X)
        k = min(self.n_components, X.shape[1])
        self._nca = NeighborhoodComponentsAnalysis(
            n_components=k, random_state=SEED, max_iter=120).fit(Z, y)
        self._knn = KNeighborsClassifier(
            n_neighbors=min(self.n_neighbors, len(y) - 1),
            weights='distance').fit(self._nca.transform(Z), y)
        return self

    def predict_proba(self, X):
        return self._knn.predict_proba(self._nca.transform(self._sc.transform(X)))

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]


CONFIGS = {
    'C0': ('A0 · S3 (6 variables) · Random Forest',
           lambda: Pipeline([('sc', StandardScaler()),
                             ('clf', RandomForestClassifier(random_state=SEED, n_jobs=1))]),
           {'clf__n_estimators': [200], 'clf__max_depth': [3, 4, None],
            'clf__min_samples_leaf': [1, 2]}),
    'C1': ('C1 · Prototipos de clase (ProtoNet tabular)',
           Prototipos, {'T': [0.5, 1.0, 2.0, 4.0]}),
    'C2': ('C2 · NCA + prototipos (métrica aprendida)',
           lambda: Prototipos(metrica='nca'),
           {'T': [0.5, 1.0, 2.0], 'n_components': [2, 3, 4]}),
    'C3': ('C3 · NCA + k vecinos',
           NCAkNN, {'n_components': [2, 3, 4], 'n_neighbors': [5, 7, 11]}),
    'C4': ('C4 · k vecinos sin métrica aprendida',
           lambda: Pipeline([('sc', StandardScaler()), ('clf', KNeighborsClassifier())]),
           {'clf__n_neighbors': [3, 5, 7, 11, 15], 'clf__weights': ['uniform', 'distance']}),
}


def correr(claves):
    for k in claves:
        nombre, constructor, grid = CONFIGS[k]
        print(f'· {k} …', flush=True)
        evaluar(nombre, constructor, variables=S3, grid=grid)


# ================================================== C5 · curva de tamaño muestral
def ley_potencias(n, a, b, c):
    """AUC-PR(n) = c - a * n^(-b): saturación con techo c."""
    return c - a * np.power(n, -b)


def curva():
    X, y, _ = cargar(S3)
    prev = prevalencia()
    fracciones = [0.35, 0.45, 0.55, 0.70, 0.85, 1.00]
    # Hiperparámetros fijados en los valores más votados en I-3 bis, para que
    # la curva aísle el efecto del tamaño y no el del presupuesto de búsqueda.
    hp = dict(n_estimators=200, max_depth=4, min_samples_leaf=1, random_state=SEED, n_jobs=1)

    print('═' * 78)
    print('C5 · CURVA DE TAMAÑO MUESTRAL')
    print('═' * 78)
    print('Se submuestrea SOLO el pliegue de entrenamiento; el de prueba queda intacto.')
    print(f'Random Forest con hiperparámetros fijos · {N_REP} repeticiones\n')

    filas, curva_pts = [], {}
    for f in fracciones:
        aps, rocs, n_ent, n_pos = [], [], [], []
        for r in range(N_REP):
            cv = StratifiedKFold(N_EXT, shuffle=True, random_state=SEED + r)
            p = np.zeros(len(y))
            for tr, te in cv.split(X, y):
                if f < 1.0:
                    sss = StratifiedShuffleSplit(1, train_size=f, random_state=SEED + r)
                    idx, _ = next(sss.split(X[tr], y[tr]))
                    tr_f = tr[idx]
                else:
                    tr_f = tr
                sc = StandardScaler().fit(X[tr_f])
                m = RandomForestClassifier(**hp).fit(sc.transform(X[tr_f]), y[tr_f])
                p[te] = m.predict_proba(sc.transform(X[te]))[:, 1]
                n_ent.append(len(tr_f)); n_pos.append(int(y[tr_f].sum()))
            aps.append(average_precision_score(y, p))
            rocs.append(roc_auc_score(y, p))
        n_med = float(np.mean(n_ent)); pos_med = float(np.mean(n_pos))
        curva_pts[n_med] = float(np.mean(aps))
        filas.append({'Fracción de entrenamiento': f'{f:.0%}',
                      'n entrenamiento (medio)': round(n_med, 1),
                      'positivos (medio)': round(pos_med, 1),
                      'AUC-PR': round(float(np.mean(aps)), 4),
                      'DE': round(float(np.std(aps)), 4),
                      'AUC-ROC': round(float(np.mean(rocs)), 4)})
        print(f'  {f:5.0%}  n_ent={n_med:5.1f}  positivos={pos_med:4.1f}  '
              f'AUC-PR {np.mean(aps):.4f} ± {np.std(aps):.4f}')

    ns = np.array(sorted(curva_pts)); vals = np.array([curva_pts[n] for n in ns])
    extrap = {}
    try:
        popt, _ = curve_fit(ley_potencias, ns, vals, p0=[1.0, 0.5, 0.85],
                            bounds=([0, 0.01, 0.3], [50, 3.0, 1.0]), maxfev=20000)
        a, b, c = popt
        pred = ley_potencias(ns, *popt)
        r2 = 1 - ((vals - pred) ** 2).sum() / ((vals - vals.mean()) ** 2).sum()
        print(f'\n  Ajuste  AUC-PR(n) = {c:.3f} − {a:.3f}·n^(−{b:.3f})   R² = {r2:.3f}')
        print(f'  Techo asintótico estimado: {c:.3f}\n')
        print('  Extrapolación a los tamaños que traerían las cohortes nuevas:')
        print(f'{"n total":>10s} {"n entrenamiento":>17s} {"AUC-PR estimado":>17s} {"ganancia":>10s}')
        base_ap = ley_potencias(64, *popt)
        for n_tot in [80, 160, 240, 320, 400]:
            n_tr = n_tot * 0.8
            v = float(ley_potencias(n_tr, *popt))
            extrap[str(n_tot)] = round(v, 4)
            print(f'{n_tot:>10d} {n_tr:>17.0f} {v:>17.3f} {v - base_ap:>+10.3f}')
        ajuste = {'a': round(float(a), 4), 'b': round(float(b), 4),
                  'c_techo': round(float(c), 4), 'R2': round(float(r2), 4),
                  'extrapolacion': extrap}
        print('\n  ADVERTENCIA: extrapolar desde 64 casos de entrenamiento hasta 320 es')
        print('  una proyección de orden de magnitud, no una predicción. Supone que las')
        print('  cohortes nuevas se parecen a las actuales y que la prevalencia se mantiene.')
    except Exception as e:  # pragma: no cover
        print(f'\n  [!] el ajuste de la ley de potencias no convergió: {e}')
        ajuste = {'error': str(e)}

    return {'puntos': filas, 'ajuste': ajuste, 'prevalencia': round(prev, 4)}


def tabla_comparativa():
    prev = prevalencia()
    base = evaluar(CONFIGS['C0'][0], CONFIGS['C0'][1], variables=S3,
                   grid=CONFIGS['C0'][2], verbose=False)
    claves = [k for k in ['C1', 'C2', 'C3', 'C4']
              if os.path.exists(os.path.join(SRC, '_cache_experimentos',
                                             CONFIGS[k][0] + '.json'))]
    otros = [evaluar(CONFIGS[k][0], CONFIGS[k][1], variables=S3,
                     grid=CONFIGS[k][2], verbose=False) for k in claves]
    tabla = comparar_contra(base, otros)
    print('═' * 78)
    print('C · MÉTODOS DE POCOS DATOS FRENTE A LA REFERENCIA')
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
    elif modo == 'curva':
        out['curva'] = curva()
    elif modo == 'tabla':
        out['comparativa'] = tabla_comparativa()
    else:
        correr(list(CONFIGS))
        out['comparativa'] = tabla_comparativa()
        out['curva'] = curva()
    json.dump(out, open(SALIDA, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f'\n[OK] {SALIDA}')


if __name__ == '__main__':
    main()
