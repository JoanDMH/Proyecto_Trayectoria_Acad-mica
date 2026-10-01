"""
equivalencias.py — Capa de equivalencias entre planes de estudio (Ing. de Sistemas)

Fuentes normativas (transcritas en src/planes_estudio/):
  · Acuerdo Académico 008 de 2011  → plan IS-2011 (códigos 602xxx), 167 créditos, 52 cursos
  · Acuerdo Académico 001 de 2017  → plan IS-2018 (códigos 603xxx), 165 créditos, 53 cursos
  · Resolución Académica 036 de 2017 → equivalencias y homologaciones entre ambos
        Art. 1  estudiante que CONTINÚA en el plan 2011: curso 2011 «a ver» ← curso 2018 «que puede tomar»
        Art. 2  estudiante que CAMBIA al plan 2018: curso 2018 «a ver» ← curso 2011 «vista»
        Parágrafo: cursos institucionales homologados directamente (emparejados aquí por nombre)
        Art. 2 parágrafo 2: cursos 2018 sin equivalente (obligatorios para quien cambia)

Propósito
---------
Dar a cada registro de `detalle_materias` una identidad de curso ESTABLE entre planes
(`CODIGO_CANONICO`), para que las piezas del pipeline que razonan «por curso» sigan
funcionando cuando se carguen cohortes del plan 2011, del plan 2018 o mezcladas:

  · art. 19, vía de la cuarta reprobación (cuenta intentos del MISMO curso)
  · panel longitudinal (`max_veces_cursado`, arts. 21-22)
  · índice descriptivo de criticidad por asignatura

El plan canónico es el VIGENTE (IS-2018): un curso 2011 se traduce al curso 2018 que lo
reconoce. Prioridad de la relación: Art. 2 (reconocimiento formal al cambiar de plan)
> Art. 1 > cursos institucionales. Los cursos 2011 sin equivalente conservan su propio
código como canónico y quedan marcados `EQUIV_FUENTE='sin_equivalente'`.

Garantía de no ruptura
----------------------
Nada en el pipeline cambia por importar este módulo. Las funciones que lo usan reciben
`clave_curso='MATERIA'` por defecto (comportamiento histórico). Con los datos actuales
ningún estudiante mezcla códigos de los dos planes, por lo que `clave_curso=
'CODIGO_CANONICO'` produce exactamente el mismo target del art. 19 (verificado en
tests/test_equivalencias.py).

Programas sin documento de equivalencias (Electrónica 612/613, Biología 642): sus
códigos pasan sin traducción (`EQUIV_FUENTE='sin_catalogo'`).
"""
import os
import unicodedata
import pandas as pd

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'planes_estudio')
CATALOGO_CSV = os.path.join(_DIR, 'catalogo_cursos.csv')
EQUIV_CSV = os.path.join(_DIR, 'equivalencias_IS_2011_2018.csv')
SIN_EQUIV_CSV = os.path.join(_DIR, 'sin_equivalente_IS_2018.csv')

# Prefijo del código de curso -> plan (pensum). Coincide con la columna PENSUM del SIIF.
PREFIJO_PLAN = {
    '602': 'IS-2011', '603': 'IS-2018',      # Ingeniería de Sistemas
    '612': 'IE-612', '613': 'IE-613',        # Ingeniería Electrónica (sin documento aún)
    '642': 'BIO-642',                        # Biología (plan único en los datos)
    '411': 'LM-411', '412': 'LM-412',        # Lic. Matemáticas (fuera de alcance)
}
PLAN_CANONICO = 'IS-2018'
PRIORIDAD = ('cambia_a_2018', 'continua_en_2011', 'institucional_inferida')
_ETIQUETA = {'cambia_a_2018': 'Art. 2', 'continua_en_2011': 'Art. 1',
             'institucional_inferida': 'institucional'}


def _norm(txt):
    """Mayúsculas sin tildes ni espacios dobles (para comparar nombres)."""
    t = unicodedata.normalize('NFKD', str(txt)).encode('ascii', 'ignore').decode()
    return ' '.join(t.upper().replace(',', ' ').split())


def _cod(x):
    try:
        return str(int(float(x)))
    except (TypeError, ValueError):
        return str(x).strip()


def cargar_catalogo():
    c = pd.read_csv(CATALOGO_CSV, dtype={'codigo': str, 'requisitos': str})
    c['codigo'] = c['codigo'].map(_cod)
    return c


def cargar_equivalencias():
    e = pd.read_csv(EQUIV_CSV, dtype={'codigo_plan_2011': str, 'codigo_plan_2018': str})
    e['codigo_plan_2011'] = e['codigo_plan_2011'].map(_cod)
    e['codigo_plan_2018'] = e['codigo_plan_2018'].map(_cod)
    return e


def plan_de_codigo(codigo):
    return PREFIJO_PLAN.get(_cod(codigo)[:3])


def mapa_canonico():
    """
    dict {codigo_2011: (codigo_2018, fuente)}. Los códigos 2018 se mapean a sí
    mismos en `normalizar_materias`. Lanza ValueError si un curso 2011 recibiera dos
    destinos distintos dentro de la MISMA relación (la tabla sería ambigua).
    """
    e = cargar_equivalencias()
    out = {}
    for sentido in PRIORIDAD:
        sub = e[e['sentido'] == sentido]
        dup = sub.groupby('codigo_plan_2011')['codigo_plan_2018'].nunique()
        if (dup > 1).any():
            raise ValueError(f'Equivalencia ambigua en {sentido}: {list(dup[dup > 1].index)}')
        for _, r in sub.iterrows():
            out.setdefault(r['codigo_plan_2011'], (r['codigo_plan_2018'], _ETIQUETA[sentido]))
    return out


def normalizar_materias(df, col_codigo='CODIGO_MATERIA'):
    """
    Devuelve una COPIA de `df` con columnas añadidas (las originales no se tocan):
        PLAN               plan del registro según el prefijo del código
        CODIGO_CANONICO    código del curso en el plan vigente (IS-2018) o el propio
        MATERIA_CANONICA   nombre oficial del curso canónico
        SEMESTRE_CANONICO  semestre del curso canónico en su plan
        EQUIV_FUENTE       propio | Art. 2 | Art. 1 | institucional | sin_equivalente | sin_catalogo
        CURSO_INTENTOS     clave para CONTAR INTENTOS de un mismo curso: el código canónico
                           si la relación es 1:1, y el código original si el curso 2011 es
                           parte de una fusión n:1 (p. ej. 602303 + 602603 -> 603403), para
                           no sumar como «repetición» dos cursos distintos del plan 2011
    """
    cat = cargar_catalogo().set_index('codigo')
    mapa = mapa_canonico()
    d = df.copy()
    cods = d[col_codigo].map(_cod)
    d['PLAN'] = cods.map(plan_de_codigo)

    def _canon(c):
        if c in mapa:
            return mapa[c]
        if c in cat.index:
            return (c, 'propio' if cat.at[c, 'plan'] == PLAN_CANONICO else 'sin_equivalente')
        return (c, 'sin_catalogo')

    res = cods.map(_canon)
    d['CODIGO_CANONICO'] = res.map(lambda t: t[0])
    d['EQUIV_FUENTE'] = res.map(lambda t: t[1])
    nombre = cat['nombre'].to_dict()
    sem = cat['semestre'].to_dict()
    d['MATERIA_CANONICA'] = [
        _norm(nombre[c]) if c in nombre else _norm(m)
        for c, m in zip(d['CODIGO_CANONICO'], d.get('MATERIA', d['CODIGO_CANONICO']))
    ]
    d['SEMESTRE_CANONICO'] = d['CODIGO_CANONICO'].map(sem)
    destinos = pd.Series({k: v[0] for k, v in mapa.items()})
    fusionados = set(destinos[destinos.duplicated(keep=False)].index)   # cursos 2011 en fusiones n:1
    d['CURSO_INTENTOS'] = [c if c in fusionados else k
                           for c, k in zip(cods, d['CODIGO_CANONICO'])]
    return d


def clave_de_curso(df, clave_curso='MATERIA'):
    """Serie con la clave de agrupación por curso. 'MATERIA' = comportamiento histórico."""
    if clave_curso == 'MATERIA':
        return df['MATERIA']
    if clave_curso == 'CODIGO_CANONICO':
        if 'CODIGO_CANONICO' not in df.columns:
            df = normalizar_materias(df)
        return df['CODIGO_CANONICO']
    raise ValueError("clave_curso debe ser 'MATERIA' o 'CODIGO_CANONICO'")


def validar(df, col_codigo='CODIGO_MATERIA', programa='INGENIERIA DE SISTEMAS'):
    """
    Informe de cobertura de una extracción frente al catálogo. Útil al cargar una
    cohorte nueva: detecta cursos que no existen en ningún plan conocido, discrepancias
    de nombre o de créditos, y estudiantes que mezclan planes.
    """
    d = df[df['PROGRAMA'].astype(str).str.strip().str.upper() == programa].copy() \
        if 'PROGRAMA' in df.columns else df.copy()
    cat = cargar_catalogo().set_index('codigo')
    d['_c'] = d[col_codigo].map(_cod)
    usados = d.drop_duplicates('_c')
    fuera = sorted(set(usados['_c']) - set(cat.index))
    nombres, creditos = [], []
    for _, r in usados[usados['_c'].isin(cat.index)].iterrows():
        oficial = cat.loc[r['_c']]
        if 'MATERIA' in r and _norm(r['MATERIA']) != _norm(oficial['nombre']):
            nombres.append((r['_c'], r['MATERIA'], oficial['nombre']))
        if 'CREDITOS' in r and pd.notna(r['CREDITOS']) and int(r['CREDITOS']) != int(oficial['creditos']):
            creditos.append((r['_c'], int(r['CREDITOS']), int(oficial['creditos'])))
    mezcla = 0
    if 'CODIGO_INST' in d.columns:
        planes = d.assign(_p=d['_c'].map(plan_de_codigo)).groupby('CODIGO_INST')['_p'].nunique()
        mezcla = int((planes > 1).sum())
    return {'registros': len(d), 'cursos_distintos': int(usados.shape[0]),
            'codigos_fuera_de_catalogo': fuera,
            'discrepancias_de_nombre': nombres,
            'discrepancias_de_creditos': creditos,
            'estudiantes_con_planes_mezclados': mezcla}


def verificar_consistencia():
    """Comprobaciones internas de la tabla normativa. Devuelve lista de avisos."""
    cat = cargar_catalogo()
    e = cargar_equivalencias()
    avisos = []
    cods = set(cat['codigo'])
    for col in ('codigo_plan_2011', 'codigo_plan_2018'):
        falt = sorted(set(e[col]) - cods)
        if falt:
            avisos.append(f'{col} sin catálogo: {falt}')
    a1 = e[e.sentido == 'continua_en_2011'].set_index('codigo_plan_2011')['codigo_plan_2018']
    a2 = e[e.sentido == 'cambia_a_2018'].groupby('codigo_plan_2011')['codigo_plan_2018'].first()
    for c in sorted(set(a1.index) & set(a2.index)):
        if a1[c] != a2[c]:
            avisos.append(f'Art.1 y Art.2 discrepan para {c}: {a1[c]} vs {a2[c]}')
    solo1 = sorted(set(a1.index) - set(a2.index))
    if solo1:
        avisos.append(f'Equivalencias SOLO en Art. 1 (asimétricas): {solo1}')
    return avisos


if __name__ == '__main__':
    import json
    print('Consistencia de la tabla normativa:')
    for a in verificar_consistencia() or ['  sin avisos']:
        print('  ·', a)
    data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'Datos', 'detalle_materias_recod.xlsx')
    if os.path.exists(data):
        rep = validar(pd.read_excel(data))
        print('\nCobertura de la extracción vigente (Ing. de Sistemas):')
        print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
