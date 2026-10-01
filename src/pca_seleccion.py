# -*- coding: utf-8 -*-
"""
pca_seleccion.py — Bloque A · PCA como respaldo de la selección de variables
Petición del asesor, 2026-09-29.

QUÉ PUEDE Y QUÉ NO PUEDE RESPONDER EL PCA
-----------------------------------------
El PCA es NO SUPERVISADO: busca las direcciones de máxima varianza en X sin mirar
nunca la variable objetivo. Por construcción, por tanto, NO puede demostrar que un
conjunto de variables sea "el mejor" para predecir: una variable de varianza
minúscula puede ser el mejor predictor, y una de varianza enorme puede ser ruido.
Presentar un gráfico de sedimentación como prueba de que la selección es correcta
sería un error metodológico.

Lo que sí aporta, y es lo que se ejecuta aquí:

  A1  Redundancia estructural: cuántas dimensiones efectivas tienen las 19 variables.
  A2  Cargas: qué variables dominan cada componente.
  A3  PRUEBA DECISIVA: usar los componentes como representación alternativa y medirla
      contra S3 bajo el protocolo anidado idéntico. Si el PCA sobre las 19 variables
      no supera a las 6 seleccionadas, eso SÍ respalda la selección, porque compara
      capacidad predictiva con capacidad predictiva.
  A4  Contraste con PLS, el análogo de PCA que sí mira a y.

Todo el preprocesado va DENTRO del Pipeline: se ajusta solo con el pliegue de
entrenamiento. Ajustarlo antes de la CV es la fuga que costó +0,150 en RC-032.

Uso:
    python src/pca_seleccion.py descriptivo
    python src/pca_seleccion.py correr A0 A1        (una o varias configuraciones)
    python src/pca_seleccion.py tabla               (comparativa; usa la caché)
"""
import os, sys, json
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arnes_experimentos import (V19, S3, ETIQUETAS, cargar, evaluar,
                                comparar_contra, prevalencia, SRC)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.base import BaseEstimator, ClassifierMixin

SEED = 42
SALIDA = os.path.join(SRC, '_resultados_pca.json')


class PLSClasificador(BaseEstimator, ClassifierMixin):
    """PLS-DA: análogo supervisado del PCA. Proyecta buscando covarianza con y."""

    def __init__(self, n_components=2):
        self.n_components = n_components

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        self._sc = StandardScaler().fit(X)
        k = min(self.n_components, X.shape[1])
        self._pls = PLSRegression(n_components=k).fit(self._sc.transform(X),
                                                      y.astype(float))
        z = self._pls.transform(self._sc.transform(X))
        self._lr = LogisticRegression(max_iter=2000, C=1.0).fit(z, y)
        return self

    def predict_proba(self, X):
        return self._lr.predict_proba(self._pls.transform(self._sc.transform(X)))

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]


def _rf():
    return RandomForestClassifier(random_state=SEED, n_jobs=1)


# Rejillas recortadas a 6-8 combinaciones: con 2 núcleos, cada configuración
# cuesta ~5 min de reloj. El presupuesto se reparte por igual entre todas para
# que ninguna gane por tener más presupuesto de búsqueda (lección de RC-033).
GRID_RF = {'clf__n_estimators': [200], 'clf__max_depth': [3, 4, None],
           'clf__min_samples_leaf': [1, 2]}

CONFIGS = {
    'A0': ('A0 · S3 (6 variables) · Random Forest',
           lambda: Pipeline([('sc', StandardScaler()), ('clf', _rf())]),
           S3, GRID_RF),
    'A1': ('A1 · 19 variables crudas · Random Forest',
           lambda: Pipeline([('sc', StandardScaler()), ('clf', _rf())]),
           V19, GRID_RF),
    'A2': ('A2 · PCA(k) sobre 19 vars · Random Forest',
           lambda: Pipeline([('sc', StandardScaler()),
                             ('pca', PCA(random_state=SEED)), ('clf', _rf())]),
           V19, {'pca__n_components': [2, 4, 6, 8],
                 'clf__n_estimators': [200], 'clf__max_depth': [4, None]}),
    'A3': ('A3 · PCA(k) sobre 19 vars · Logística',
           lambda: Pipeline([('sc', StandardScaler()),
                             ('pca', PCA(random_state=SEED)),
                             ('clf', LogisticRegression(max_iter=4000))]),
           V19, {'pca__n_components': [2, 3, 4, 5, 6, 8, 10],
                 'clf__C': [0.05, 0.25, 1.0, 4.0]}),
    'A4': ('A4 · PCA(k) sobre S3 · Random Forest',
           lambda: Pipeline([('sc', StandardScaler()),
                             ('pca', PCA(random_state=SEED)), ('clf', _rf())]),
           S3, {'pca__n_components': [2, 3, 4, 5],
                'clf__n_estimators': [200], 'clf__max_depth': [4, None]}),
    'A5': ('A5 · PLS-DA(k) sobre 19 vars (supervisado)',
           PLSClasificador, V19, {'n_components': [1, 2, 3, 4, 5, 6, 8]}),
    'A6': ('A6 · PLS-DA(k) sobre S3 (supervisado)',
           PLSClasificador, S3, {'n_components': [1, 2, 3, 4, 5]}),
}


def correr(claves):
    for k in claves:
        nombre, constructor, variables, grid = CONFIGS[k]
        print(f'· {k} …', flush=True)
        evaluar(nombre, constructor, variables=variables, grid=grid)


# =========================================================== A1 · A2 descriptivo
def descriptivo():
    X, y, nombres = cargar(V19)
    Z = StandardScaler().fit_transform(X)
    p = PCA().fit(Z)
    ev, evr = p.explained_variance_, p.explained_variance_ratio_
    cum = np.cumsum(evr)

    print('═' * 78)
    print('A1 · ESTRUCTURA DE VARIANZA DE LAS 19 VARIABLES (descriptivo)')
    print('═' * 78)
    filas_var = []
    for i in range(len(evr)):
        if i < 12:
            print(f'CP{i+1:<3d} autovalor {ev[i]:6.3f}   {evr[i]*100:5.2f}%   '
                  f'acum {cum[i]*100:6.2f}%   {"Kaiser" if ev[i] > 1 else ""}')
        filas_var.append({'Componente': f'CP{i+1}',
                          'Autovalor': round(float(ev[i]), 4),
                          '% varianza': round(float(evr[i] * 100), 2),
                          '% acumulado': round(float(cum[i] * 100), 2),
                          'Kaiser (autovalor>1)': 'sí' if ev[i] > 1 else 'no'})
    n_kaiser = int((ev > 1).sum())
    n80, n90, n95 = [int(np.searchsorted(cum, q) + 1) for q in (.80, .90, .95)]
    print(f'\n  Kaiser (autovalor > 1): {n_kaiser} componentes')
    print(f'  Para el 80 / 90 / 95 % de la varianza: {n80} / {n90} / {n95} componentes')

    print('\n' + '═' * 78)
    print('A2 · CARGAS DE LOS PRIMEROS COMPONENTES')
    print('═' * 78)
    carga = pd.DataFrame(p.components_[:5].T, index=nombres,
                         columns=[f'CP{i+1}' for i in range(5)])
    for i in range(5):
        c = carga[f'CP{i+1}'].sort_values(key=abs, ascending=False)
        print(f'\nCP{i+1} ({evr[i]*100:.1f} %) — dominantes:')
        for v, val in c.head(5).items():
            marca = '  ← en S3' if v in S3 else ''
            print(f'     {ETIQUETAS.get(v, v):32s} {val:+.3f}{marca}')
    filas_carga = []
    for v in nombres:
        fila = {'Variable': ETIQUETAS.get(v, v), 'En S3': 'sí' if v in S3 else 'no'}
        for i in range(5):
            fila[f'CP{i+1}'] = round(float(carga.loc[v, f'CP{i+1}']), 3)
        filas_carga.append(fila)

    # ¿en qué componente aparece por primera vez la variable más predictiva?
    primer_cp = int(np.argmax([abs(p.components_[i][nombres.index('prom_sem1')])
                               for i in range(len(evr))]))
    print(f'\n  La variable más predictiva (promedio de 1er semestre) tiene su carga '
          f'máxima\n  en CP{primer_cp+1}, que explica solo el {evr[primer_cp]*100:.1f} % '
          f'de la varianza.')

    Xs, _, _ = cargar(S3)
    cums = np.cumsum(PCA().fit(StandardScaler().fit_transform(Xs)).explained_variance_ratio_)
    print('\n' + '═' * 78)
    print('A2b · REDUNDANCIA INTERNA DEL CONJUNTO S3 (6 variables)')
    print('═' * 78)
    for i, c in enumerate(cums):
        print(f'   CP1..CP{i+1}: {c*100:5.1f} % acumulado')
    n90s = int(np.searchsorted(cums, 0.90) + 1)
    print(f'\n  S3 necesita {n90s} de 6 componentes para el 90 %: no hay redundancia'
          '\n  interna apreciable que comprimir.')

    return {'varianza': filas_var, 'cargas': filas_carga, 'n_kaiser': n_kaiser,
            'n80': n80, 'n90': n90, 'n95': n95,
            'cp_prom_sem1': primer_cp + 1,
            'var_cp_prom_sem1': round(float(evr[primer_cp] * 100), 2),
            's3_cum': [round(float(c) * 100, 2) for c in cums], 's3_n90': n90s}


def tabla_comparativa():
    prev = prevalencia()
    base = evaluar(*[CONFIGS['A0'][0], CONFIGS['A0'][1]],
                   variables=CONFIGS['A0'][2], grid=CONFIGS['A0'][3], verbose=False)
    otros = [evaluar(CONFIGS[k][0], CONFIGS[k][1], variables=CONFIGS[k][2],
                     grid=CONFIGS[k][3], verbose=False)
             for k in ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']]
    tabla = comparar_contra(base, otros)
    print('═' * 78)
    print('A3/A4 · ¿MEJORA ALGUNA REPRESENTACIÓN A LAS 6 VARIABLES SELECCIONADAS?')
    print('═' * 78)
    print(f'Referencia = {base["nombre"]}  ·  AUC-PR {np.mean(base["ap"]):.4f} '
          f'± {np.std(base["ap"]):.4f}   (azar = {prev:.4f})\n')
    print(tabla.to_string(index=False))

    ks = {}
    for r in otros:
        vals = [h.get('pca__n_components') or h.get('n_components')
                for h in r['hiperparametros'] if h]
        vals = [v for v in vals if v]
        if vals:
            ks[r['nombre']] = {str(k): int(v) for k, v in pd.Series(vals).value_counts().items()}
    if ks:
        print('\nComponentes elegidos dentro de los pliegues (frecuencia sobre 50):')
        for nom, d in ks.items():
            print(f'   {nom[:44]:44s} {d}')

    return {'base': {'nombre': base['nombre'],
                     'ap': round(float(np.mean(base['ap'])), 4),
                     'de': round(float(np.std(base['ap'])), 4),
                     'roc': round(float(np.mean(base['roc'])), 4)},
            'tabla': tabla.to_dict('records'), 'k_elegidos': ks,
            'prevalencia': round(prev, 4)}


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else 'todo'
    out = json.load(open(SALIDA, encoding='utf8')) if os.path.exists(SALIDA) else {}
    if modo == 'descriptivo':
        out['descriptivo'] = descriptivo()
    elif modo == 'correr':
        correr(sys.argv[2:] or list(CONFIGS))
        return
    elif modo == 'tabla':
        out['predictivo'] = tabla_comparativa()
    else:
        out['descriptivo'] = descriptivo()
        correr(list(CONFIGS))
        out['predictivo'] = tabla_comparativa()
    json.dump(out, open(SALIDA, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f'\n[OK] {SALIDA}')


if __name__ == '__main__':
    main()
