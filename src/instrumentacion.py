"""
instrumentacion.py — Bitácora de ejecución para experimentos reproducibles

Resuelve la carencia detectada al revisar I-3: el script persistía solo métricas
agregadas, de modo que no era posible reconstruir las pruebas pareadas, los
intervalos de confianza ni auditar qué hiperparámetros eligió la búsqueda interna
en cada pliegue.

Qué registra:
  1. Contexto de ejecución: versiones de librerías, hash del CSV de entrada,
     semilla, timestamp. Sin esto, "reproducible" es una afirmación sin respaldo.
  2. Métricas POR REPETICIÓN de cada modelo (no solo la media).
  3. Hiperparámetros seleccionados en CADA pliegue externo. Su variabilidad es un
     hallazgo en sí: con 19 positivos la búsqueda interna es ruidosa, y mostrar
     cuánto oscila la configuración óptima documenta la incertidumbre real.

Uso desde un script de experimentación:

    from instrumentacion import Bitacora
    bit = Bitacora('I-3_rerun', archivos_entrada=['src/df_master_limpio.csv'])
    ...
    bit.registrar_fold(modelo='Random Forest', rep=r, fold=k,
                       params=gs.best_params_, score=gs.best_score_)
    bit.registrar_repeticion(modelo='Random Forest', rep=r,
                             metricas={'AUC_PR': ap, 'AUC_ROC': auc})
    ...
    bit.cerrar()
"""
import os, sys, json, hashlib, platform, warnings
from datetime import datetime
import pandas as pd

SRC = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(SRC)
DIR_BITACORA = os.path.join(RAIZ, 'bitacora')


def _hash_archivo(path, n=12):
    """SHA-256 truncado del contenido. Permite afirmar que dos corridas usaron
    exactamente los mismos datos de entrada."""
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:n]
    except FileNotFoundError:
        return 'NO_ENCONTRADO'


def _versiones():
    v = {'python': sys.version.split()[0], 'plataforma': platform.platform()}
    for mod in ('numpy', 'pandas', 'sklearn', 'xgboost', 'scipy'):
        try:
            v[mod] = __import__(mod).__version__
        except Exception:
            v[mod] = 'no disponible'
    return v


class Bitacora:
    """Registra el detalle de una corrida experimental y lo persiste en disco."""

    def __init__(self, nombre, archivos_entrada=None, notas=None, seed=42):
        self.nombre = nombre
        self.inicio = datetime.now()
        self.seed = seed
        self.notas = notas or ''
        self.dir = os.path.join(DIR_BITACORA, f"{self.inicio:%Y%m%d_%H%M%S}_{nombre}")
        os.makedirs(self.dir, exist_ok=True)
        self.folds = []
        self.repeticiones = []
        self.eventos = []
        self.contexto = {
            'experimento': nombre,
            'inicio': self.inicio.isoformat(timespec='seconds'),
            'seed': seed,
            'versiones': _versiones(),
            'archivos_entrada': {
                p: {'hash_sha256_12': _hash_archivo(os.path.join(RAIZ, p)),
                    'bytes': os.path.getsize(os.path.join(RAIZ, p))
                    if os.path.exists(os.path.join(RAIZ, p)) else None}
                for p in (archivos_entrada or [])
            },
            'notas': self.notas,
        }
        print(f'[bitácora] {self.dir}')

    # ── registro ────────────────────────────────────────────────────────────
    def registrar_fold(self, modelo, rep, fold, params, score=None, n_train=None,
                       n_test=None, pos_train=None, pos_test=None):
        """Hiperparámetros elegidos por la búsqueda interna en un pliegue externo."""
        self.folds.append({
            'modelo': modelo, 'repeticion': rep, 'pliegue': fold,
            'params': json.dumps(params, default=str, ensure_ascii=False),
            'score_interno': score,
            'n_train': n_train, 'n_test': n_test,
            'positivos_train': pos_train, 'positivos_test': pos_test,
        })

    def registrar_repeticion(self, modelo, rep, metricas):
        """Métricas out-of-fold de una repetición completa."""
        fila = {'modelo': modelo, 'repeticion': rep}
        fila.update(metricas)
        self.repeticiones.append(fila)

    def evento(self, texto):
        marca = (datetime.now() - self.inicio).total_seconds()
        self.eventos.append({'t_segundos': round(marca, 1), 'evento': texto})
        print(f'[{marca:7.1f}s] {texto}')

    # ── cierre ──────────────────────────────────────────────────────────────
    def cerrar(self, resumen=None):
        fin = datetime.now()
        self.contexto['fin'] = fin.isoformat(timespec='seconds')
        self.contexto['duracion_segundos'] = round((fin - self.inicio).total_seconds(), 1)
        if resumen:
            self.contexto['resumen'] = resumen

        if self.repeticiones:
            df_rep = pd.DataFrame(self.repeticiones)
            df_rep.to_csv(os.path.join(self.dir, 'metricas_por_repeticion.csv'), index=False)
            self.contexto['n_repeticiones_registradas'] = len(df_rep)

        if self.folds:
            df_f = pd.DataFrame(self.folds)
            df_f.to_csv(os.path.join(self.dir, 'hiperparametros_por_pliegue.csv'), index=False)
            self.contexto['n_pliegues_registrados'] = len(df_f)
            # Estabilidad: ¿con qué frecuencia se repite la configuración ganadora?
            est = (df_f.groupby('modelo')['params']
                       .agg(configuraciones_distintas='nunique',
                            config_mas_frecuente=lambda s: s.value_counts().idxmax(),
                            frecuencia_de_la_moda=lambda s: round(s.value_counts().iloc[0] / len(s), 3))
                       .reset_index())
            est.to_csv(os.path.join(self.dir, 'estabilidad_hiperparametros.csv'), index=False)

        if self.eventos:
            pd.DataFrame(self.eventos).to_csv(
                os.path.join(self.dir, 'eventos.csv'), index=False)

        with open(os.path.join(self.dir, 'contexto.json'), 'w', encoding='utf-8') as f:
            json.dump(self.contexto, f, indent=2, ensure_ascii=False)

        print(f"[bitácora] cerrada · {self.contexto['duracion_segundos']} s · {self.dir}")
        return self.dir


def comparar_corridas(dir_a, dir_b, tol=1e-12):
    """
    Verificación de reproducibilidad: compara las métricas por repetición de dos
    corridas. Con semilla fija y las mismas versiones deben ser idénticas.
    Devuelve (identicas: bool, informe: DataFrame).
    """
    a = pd.read_csv(os.path.join(dir_a, 'metricas_por_repeticion.csv'))
    b = pd.read_csv(os.path.join(dir_b, 'metricas_por_repeticion.csv'))
    clave = ['modelo', 'repeticion']
    m = a.merge(b, on=clave, suffixes=('_a', '_b'))
    num = [c[:-2] for c in m.columns if c.endswith('_a')]
    filas = []
    for c in num:
        d = (m[f'{c}_a'] - m[f'{c}_b']).abs()
        filas.append({'metrica': c, 'max_diferencia_abs': float(d.max()),
                      'identica': bool(d.max() <= tol)})
    inf = pd.DataFrame(filas)
    return bool(inf['identica'].all()), inf


if __name__ == '__main__':
    b = Bitacora('demo', archivos_entrada=['src/df_master_limpio.csv'],
                 notas='Prueba de humo de la instrumentación')
    b.evento('inicio de demostración')
    b.registrar_fold('Modelo X', 0, 0, {'max_depth': 3}, score=0.5,
                     n_train=64, n_test=16, pos_train=15, pos_test=4)
    b.registrar_repeticion('Modelo X', 0, {'AUC_PR': 0.55, 'AUC_ROC': 0.78})
    b.cerrar(resumen={'estado': 'demo'})
