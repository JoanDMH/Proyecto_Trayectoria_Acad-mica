"""
recodificacion.py
Fase 3 CRISP-DM - Preparacion de datos (reproducible)
Universidad de los Llanos - Genera los archivos *_recod.xlsx desde los ORIGINALES.

Los archivos originales son la norma y NUNCA se modifican. Este script encapsula
todas las reglas de limpieza validadas con la Oficina de Sistemas (jul-2026):

A) detalle_materias_recod.xlsx
   1. Se ELIMINAN los registros de actividad posteriores al periodo del estado
      GRADUADO (residuos administrativos, p.ej. TRAMITE DE GRADO repetido).
   2. OBSERVACION recodificada (se conserva OBSERVACION_ORIG y RECOD_REGLA):
      - vacia con nota                  -> N (curso normal)
      - TRAMITE DE GRADO (TG o vacia)   -> A si es el ultimo tramite del estudiante
                                            y su periodo <= periodo GRADUADO; si no -> P
      - vacia sin nota, periodo reciente (2026-1) -> E (en curso)
      - vacia sin nota, no reciente     -> R (no presenta)
      - N, C, H, O, V, I                -> sin cambio (C = CURSO INTERSEMESTRAL)

B) historial_estados_recod.xlsx
   1. Estados originales se conservan siempre (son la norma).
   2. Periodo con actividad academica y sin estado -> MATRICULADO (imputado).
   3. 2020-2 (no existe en los datos: pandemia) -> NO REALIZO PAGO, solo para
      estudiantes con actividad posterior a 2020-1.
   4. Periodo truncado sin actividad ni estado -> NO MATRICULADO (imputado).
   5. Regla anti-residuo: NO se imputa nada despues del primer estado terminal ORIGINAL.
   6. Estado final inferido (para no graduados sin acta formal de retiro) si cumple:
      3.1 actividad real >= MIN_ACT registros en periodos regulares
      3.2 sin actividad ni estados desde UMBRAL_RECIENTE (2024-1)
      3.3 BAJO RENDIMIENTO >= 1 -> RETIRADO BR
          si no, NO REALIZO PAGO >= 2 -> RETIRO POR NO RENOVACION DE MATRICULA
          si no -> no se infiere.
   7. Estudiantes sin actividad academica: sin cambios.

Convencion temporal: el periodo 'AAAA-0' es el intersemestral de inicio de anio
(enero), por lo que el orden cronologico AAAA-1 > AAAA-0 > (AAAA-1)-2 coincide
con el orden lexicografico de las cadenas.
"""
import pandas as pd, re, os

BASE = os.path.join(os.path.dirname(__file__), '..', 'Datos')
PROGRAMAS_INFERENCIA = ['INGENIERIA DE SISTEMAS', 'INGENIERIA ELECTRONICA', 'BIOLOGIA']
UMBRAL_RECIENTE = '2024-1'
PERIODO_PANDEMIA = '2020-2'
MIN_ACT = 1          # 3.1: minimo de registros reales
MIN_NRP = 2          # 3.3: minimo de NO REALIZO PAGO sin BR
RET = {"RETIRADO BR", "RETIRO DEFINITIVO DEL PROGRAMA CON BAJO RENDIMIENTO",
       "RETIRO DEFINITIVO VOLUNTARIO DEL PROGRAMA", "RETIRO POR NO RENOVACION DE MATRICULA"}
TERM = RET | {'GRADUADO'}
CAL = ['2017-2','2018-1','2018-2','2019-1','2019-2','2020-1','2020-2','2021-1','2021-2',
       '2022-1','2022-2','2023-1','2023-2','2024-1','2024-2','2025-1','2025-2','2026-1']
POS = {p: i for i, p in enumerate(CAL)}
REGP = re.compile(r'^(\d{4})-([12])$')

def pnum(p):
    m = REGP.match(str(p))
    return int(m.group(1)) * 2 + (int(m.group(2)) - 1) if m else None

def cargar():
    he = pd.read_excel(os.path.join(BASE, 'historial_estados_.xlsx'))
    dm = pd.read_excel(os.path.join(BASE, 'detalle_materias.xlsx'))
    he['cod'] = he['CODIGO_INST'].astype(str).str.strip()
    dm['cod'] = dm['CODIGO_INST'].astype(str).str.strip()
    he['ESTADO'] = he['ESTADO'].astype(str).str.strip().str.upper()
    return he, dm

def recodificar_detalle(he, dm):
    gradper = he[he['ESTADO'] == 'GRADUADO'].groupby('cod')['PERIODO_ESTADO'].min().map(str).to_dict()
    d = dm.copy()
    d['OBS'] = d['OBSERVACION'].astype(str).str.strip().str.upper()
    d['per'] = d['PERIODO_INSCRIPCION'].astype(str)
    d['pn'] = d['per'].map(pnum)
    d['MAT'] = d['MATERIA'].astype(str).str.strip().str.upper()
    # 1. borrar actividad posterior a la graduacion
    tope = d['cod'].map(lambda c: pnum(gradper[c]) if c in gradper else None)
    err = tope.notna() & d['pn'].notna() & (d['pn'] > tope)
    d = d[~err].copy()
    n_borrados = int(err.sum())
    # 2. recodificar
    vacia = d['OBSERVACION'].isna() | d['OBS'].isin(['NAN', ''])
    nueva, regla = [], []
    ult_tram = {}
    tram_mask = d['MAT'] == 'TRAMITE DE GRADO'
    for c, g in d[tram_mask].groupby('cod'):
        ult_tram[c] = g['pn'].max()
    for i, r in d.iterrows():
        if r['MAT'] == 'TRAMITE DE GRADO':
            gp = gradper.get(r['cod'])
            if gp is not None and r['pn'] == ult_tram[r['cod']] and r['pn'] <= pnum(gp):
                nueva.append('A'); regla.append('Tramite: ultimo + periodo<=GRADUADO -> A')
            else:
                nueva.append('P'); regla.append('Tramite: no aprobado/en curso -> P')
        elif vacia.loc[i]:
            if pd.notna(r['DEFINITIVA']):
                nueva.append('N'); regla.append('Vacia con nota -> N')
            elif r['per'] == '2026-1':
                nueva.append('E'); regla.append('Vacia sin nota, 2026-1 -> E')
            else:
                nueva.append('R'); regla.append('Vacia sin nota, no reciente -> R')
        else:
            nueva.append(r['OBS']); regla.append('sin cambio')
    out = d.drop(columns=['OBS', 'per', 'pn', 'MAT', 'cod']).rename(columns={'OBSERVACION': 'OBSERVACION_ORIG'})
    out['OBSERVACION'] = nueva
    out['RECOD_REGLA'] = regla
    cols = list(out.columns); cols.remove('OBSERVACION'); cols.remove('RECOD_REGLA')
    k = cols.index('OBSERVACION_ORIG') + 1
    out = out[cols[:k] + ['OBSERVACION', 'RECOD_REGLA'] + cols[k:]]
    return out, n_borrados

def _meta(he, dm, base):
    ho = pd.read_excel(os.path.join(base, 'homologaciones.xlsx'))
    car = pd.read_excel(os.path.join(base, 'caracterización.xlsx'))
    ho['cod'] = ho['CODIGO_INST'].astype(str).str.strip()
    car['cod'] = car['CODIGO_ESTUDIANTIL'].astype(str).str.strip()
    mc = ['COHORTE', 'NOMBRE1', 'NOMBRE2', 'APELLIDO1', 'APELLIDO2', 'PROGRAMA']
    src = [d[['cod'] + [c for c in mc if c in d.columns]] for d in (he, dm, ho)]
    src.append(car[['cod', 'PERIODO_INGRESO', 'PROGRAMA']].rename(columns={'PERIODO_INGRESO': 'COHORTE'}))
    allm = pd.concat(src, ignore_index=True); meta = {}
    for c, g in allm.groupby('cod'):
        rec = {}
        for col in mc:
            v = g[col].dropna() if col in g.columns else pd.Series([], dtype=object)
            v = v[v.astype(str).str.strip() != ''] if len(v) else v
            rec[col] = v.iloc[0] if len(v) else None
        meta[c] = rec
    return meta, mc

def recodificar_historial(he, dm):
    meta, metacols = _meta(he, dm, BASE)
    dm = dm.copy(); dm['per'] = dm['PERIODO_INSCRIPCION'].astype(str)
    act = dm[dm['per'].str.match(REGP)].groupby('cod')['per'].apply(set)
    he_reg = he[he['PERIODO_ESTADO'].astype(str).str.match(REGP)]
    existentes = set((r['cod'], str(r['PERIODO_ESTADO'])) for _, r in he_reg.iterrows())
    est_per = he_reg.groupby('cod')['PERIODO_ESTADO'].apply(lambda s: set(s.astype(str)))
    first_term = {c: min(POS[str(p)] for p in g[g['ESTADO'].isin(TERM)]['PERIODO_ESTADO'])
                  for c, g in he_reg.groupby('cod') if g['ESTADO'].isin(TERM).any()}
    U = pnum('2020-1'); UMB = pnum(UMBRAL_RECIENTE)
    cols = metacols[:2] if False else None
    columnas = ['COHORTE','CODIGO_INST','NOMBRE1','NOMBRE2','APELLIDO1','APELLIDO2','PROGRAMA','PERIODO_ESTADO','ESTADO','ORIGEN']
    filas = []
    for c in sorted(set(he['cod']) | set(act.index)):
        a = act.get(c, set())
        if not a: continue                                   # regla 7: sin actividad -> sin cambios
        e = est_per.get(c, set())
        idxs = [POS[p] for p in (a | e) if p in POS]
        lo, hi = min(idxs), max(idxs)
        tope = first_term.get(c, 10**9)                      # regla 5: anti-residuo
        q = any(pnum(p) > U for p in a)                      # regla 3
        m = meta.get(c, {})
        for i in range(lo, hi + 1):
            if i > tope: continue
            p = CAL[i]
            if (c, p) in existentes: continue
            nuevo = ('NO REALIZO PAGO' if (p == PERIODO_PANDEMIA and q)
                     else ('MATRICULADO' if p in a else 'NO MATRICULADO'))
            filas.append({**{k: m.get(k) for k in metacols}, 'CODIGO_INST': c,
                          'PERIODO_ESTADO': p, 'ESTADO': nuevo, 'ORIGEN': f'IMPUTADO: {nuevo}'})
    imp = pd.DataFrame(filas)
    # regla 6: estado final inferido
    finales = []
    for prog in PROGRAMAS_INFERENCIA:
        he_p = he[he['PROGRAMA'].str.strip().str.upper() == prog]
        dm_p = dm[dm['PROGRAMA'].str.strip().str.upper() == prog]
        for c in sorted(set(he_p['cod']) | set(dm_p['cod'])):
            est = he_p[he_p['cod'] == c]['ESTADO']
            s = set(est)
            if 'GRADUADO' in s or (s & RET): continue
            a_real = dm_p[(dm_p['cod'] == c) & dm_p['per'].str.match(REGP)]
            ults = [pnum(p) for p in a_real['per']] + [pnum(str(p)) for p in he_p[he_p['cod']==c]['PERIODO_ESTADO'] if pnum(str(p)) is not None]
            if len(a_real) < MIN_ACT: continue                          # 3.1
            if not ults or max(ults) >= UMB: continue                   # 3.2
            nBR = (est == 'BAJO RENDIMIENTO').sum(); nNRP = (est == 'NO REALIZO PAGO').sum()
            if nBR >= 1: ef = 'RETIRADO BR'                             # 3.3
            elif nNRP >= MIN_NRP: ef = 'RETIRO POR NO RENOVACION DE MATRICULA'
            else: continue
            last_idx = max([POS[p] for p in est_per.get(c, set())] + [POS[p] for p in act.get(c, set()) if p in POS])
            j = last_idx + 1
            if j < len(CAL) and CAL[j] == PERIODO_PANDEMIA: j += 1
            m = meta.get(c, {})
            finales.append({**{k: m.get(k) for k in metacols}, 'CODIGO_INST': c,
                            'PERIODO_ESTADO': CAL[min(j, len(CAL)-1)], 'ESTADO': ef,
                            'ORIGEN': 'IMPUTADO: ESTADO FINAL INFERIDO'})
    fin = pd.DataFrame(finales)
    orig = he.drop(columns=['cod']).copy(); orig['ORIGEN'] = 'ORIGINAL'
    full = pd.concat([orig[columnas], imp[columnas], fin[columnas]], ignore_index=True)
    og = {'ORIGINAL': 0, 'IMPUTADO: ESTADO FINAL INFERIDO': 2}
    full['_c'] = full['CODIGO_INST'].astype(str).str.strip()
    full['_o'] = full['PERIODO_ESTADO'].astype(str).map(lambda p: POS.get(p, 99))
    full['_g'] = full['ORIGEN'].map(lambda o: og.get(o, 1))
    full = full.sort_values(['_c', '_o', '_g']).drop(columns=['_c', '_o', '_g']).reset_index(drop=True)
    return full

if __name__ == '__main__':
    import sys
    he, dm = cargar()
    fase = sys.argv[1] if len(sys.argv) > 1 else 'todo'
    if fase in ('detalle', 'todo'):
        det, nb = recodificar_detalle(he, dm)
        det.to_excel(os.path.join(BASE, 'detalle_materias_recod.xlsx'), index=False)
        print(f'detalle_materias_recod.xlsx: {len(det)} filas ({nb} borrados post-graduacion)')
        print(det['OBSERVACION'].value_counts().to_string())
    if fase in ('historial', 'todo'):
        h = recodificar_historial(he, dm)
        outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, 'historial_estados_recod_gen.xlsx')
        h.to_excel(outp, index=False)
        print(f'historial generado: {len(h)} filas -> {outp}')
        print(h['ORIGEN'].value_counts().to_string())
