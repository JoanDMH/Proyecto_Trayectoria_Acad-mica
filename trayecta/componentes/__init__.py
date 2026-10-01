"""Componente D3 bidireccional de TRAYECTA (sin compilación: HTML + JS servidos tal cual)."""
import json
import os

import numpy as np
import streamlit.components.v1 as components

_viz = components.declare_component('trayecta_viz', path=os.path.join(os.path.dirname(__file__), 'viz'))


def _limpio(o):
    if isinstance(o, dict):
        return {k: _limpio(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_limpio(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if (o != o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def viz(tipo, datos, titulo=None, ayuda=None, alto=None, key=None):
    """Dibuja la visualización `tipo` (hero, enjambre, situacion, trayectoria, perfil, barras,
    curva, gauge). Devuelve el último evento del usuario (p. ej. clic en un estudiante)."""
    return _viz(tipo=tipo, datos=json.dumps(_limpio(datos), ensure_ascii=False), titulo=titulo,
                ayuda=ayuda, key=key, default=None, height=alto)
