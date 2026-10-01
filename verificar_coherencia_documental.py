# -*- coding: utf-8 -*-
"""
_auditar_documentos.py — contrasta CADA documento del proyecto contra la verdad
de referencia del REGISTRO_CIENTIFICO.

Motivo: en la preparacion del envio se reviso solo lo que se habia tocado, y el
documento rector (PLAN_DE_TRABAJO.md) quedo tres semanas desfasado. Esto es lo
contrario: barrido exhaustivo y mecanico, documento por documento.

Los documentos se clasifican en tres regimenes, porque una cifra "vieja" no es
un error en todos ellos:

  VIVO       debe estar al dia. Cualquier cifra obsoleta es un fallo.
  HISTORICO  narra el pasado (bitacora, especificaciones de experimentos ya
             ejecutados, material retirado). Las cifras viejas son legitimas.
  PUBLICADO  ya salio del proyecto (paper aceptado, ponencia). NO se toca.

Uso:  python verificar_coherencia_documental.py

Devuelve codigo 0 si no hay hallazgos. Util antes de cualquier entrega: si alguien
actualiza una cifra en un documento y se olvida de los demas, esto lo detecta.
"""
import os, re, json, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))

REGIMEN = {
    'VIVO': [
        'PLAN_DE_TRABAJO.md', 'README.md', 'KANBAN_AGENTES.md',
        'PROBLEMAS_DETECTADOS.txt', 'PLAN_OPERATIVO_AGENTES.md',
        'PLAN_MEJORAS.md', 'MARCO_NORMATIVO.md', 'BORRADOR_INFORME.md',
        'RESUMEN_ASESOR_2026-09.md',
        'Fase 2/04_hallazgos_eda.md', 'Fase 2/08_verificacion_fcbi.md',
        'app.py', '_VERDAD_DE_REFERENCIA.md',
    ],
    'HISTORICO': [
        'REGISTRO_CIENTIFICO.md', 'ESPEC_I3.md', 'INSTRUCCIONES_I3BIS.md',
        'Fase 2/01_recoleccion_datos.md', 'Fase 2/02_descripcion_datos.md',
        'Fase 2/03_diccionario_datos.md', 'Fase 3/03_reporte_transformaciones.md',
        'Fase 4/03_hiperparametros_seleccion.md', 'Datos/diccionario_siif.md',
        'reglamento_estudiantil_unillanos.md',
        'archivo/auditoria_proyecto.md', 'archivo/control_correcciones.md',
        'archivo/plan_crisp_dm_unillanos.md',
        'archivo/modelos_reprobacion_retirados/LEEME.md',
        # Informes de fase y auditoria: narran un momento del proceso y llevan
        # aviso de cabecera que remite al estado vigente. No se reescriben.
        'AUDITORIA_2026-09.md', 'Fase 4/02_informe_modelado.md',
        'Fase 4/04_metricas_evaluacion.md', 'Fase 5/01_informe_evaluacion.md',
        'Fase 5/03_impacto_recodificacion_antes_despues.md',
    ],
    'PUBLICADO': [
        'paper_congreso/paper_congreso.tex',
    ],
}

# (etiqueta, patron, por que es un problema, como se arregla)
REGLAS = [
    ('TARGET-OBSOLETO', r'PROMEDIO_CARRERA\s*<\s*3[.,]0',
     'El target "promedio de carrera < 3,0" se descarto por tautologico (RC-012/RC-017)',
     'Sustituir por el target del art. 19, o marcar explicitamente como historico'),
    ('TARGET-OBSOLETO', r'`?rendimiento_bajo`?',
     'Nombre del target antiguo',
     'Usar bajo_rendimiento_art19, o marcar como obsoleto'),
    ('METRICA-VIEJA', r'0[.,]816',
     'Recall+ 0,816 es del target antiguo',
     'El vigente es AUC-PR 0,745 sobre el art. 19'),
    ('METRICA-VIEJA', r'\bAUC\s*0[.,]752\b',
     'AUC 0,752 es del target antiguo',
     'El vigente es AUC-PR 0,745 / AUC-ROC 0,794'),
    ('MATERIAS-RETIRADAS', r'(?:AUC|F1-w|F1-weighted)[^|\n]{0,30}0[.,]9[23][0-9]|0[.,]865\s*[–-]\s*0[.,]939|F1-w\s*0[.,]785',
     'Metricas de los modelos de reprobacion por asignatura, retirados en RC-022',
     'Retirar; solo sobrevive el indice descriptivo de criticidad'),
    ('POBLACION', r'\b20\s*/\s*90\b|\b20 de 90\b',
     'El target del art. 19 tiene 19 positivos sobre 80 expuestos, no 20 sobre 90',
     'Corregir a 19/80 (la colision de periodos se arreglo en RC-020)'),
    ('POBLACION', r'\bN\s*=\s*89\b|\bn\s*=\s*89\b',
     'n=89 es anterior a la recodificacion',
     'La poblacion con actividad es 90; la expuesta al art. 19 es 80'),
    ('VARIABLES', r'1[89] (features|variables) (de entrada )?(actuales|vigentes)',
     'El conjunto vigente es S3, de 6 variables (RC-032)',
     'Corregir a 6 variables'),
    ('PROTOCOLO', r'CV-5 (estratificada )?out-of-fold(?!.{0,80}anidada)',
     'El protocolo vigente es CV-5 ANIDADA x 10 repeticiones (RC-021)',
     'Indicar que la busqueda de hiperparametros va dentro del pliegue'),
    ('PROTOCOLO', r'train_test_split|split 72/18|72\s*/\s*18',
     'La particion fija 72/18 esta obsoleta; se usa validacion cruzada anidada',
     'Retirar la referencia a la particion fija'),
    ('UMBRAL', r'umbral\s*0[.,]29(?!.{0,120}(tres niveles|0[.,]62|historic|antiguo|paper))',
     'El umbral unico 0,29 se sustituyo por el esquema de tres niveles (RC-034)',
     'Referir el esquema de 3 niveles: 0,62 / 0,12 / 0,06'),
    ('MULTICLASE', r'multiclase.{0,80}(por construir|pendiente|falta)|falta.{0,40}multiclase',
     'El target multiclase se declaro INVIABLE (RC-041)',
     'Marcar como cerrado con respuesta negativa'),
    ('PONENCIA', r'[Pp]onencia.{0,60}(no inicia|No inicia|🔴)',
     'La ponencia esta aceptada en CICI 2026 (ID 129)',
     'Marcar como cerrada'),
    ('RC-RANGO', r'RC-0*([0-3][0-9])\b(?!\s*(a|hasta|…|\.\.))(?=.{0,25}(última entrada|llega hasta))',
     'El registro llega hasta RC-044',
     'Actualizar el rango'),
    ('DESERCION', r'62[.,]1\s*%',
     'La cifra de desercion vigente en el paper es 63 %',
     'Unificar con la cifra reportada'),
]

# cifras y afirmaciones vigentes, para el informe de cobertura
VIGENTE = {
    'AUC-PR del modelo': '0,745',
    'Linea base de azar': '0,2375',
    'Poblacion expuesta': 'n = 80',
    'Positivos': '19',
    'Variables': '6',
    'Dataset FCBI': '262',
    'Ultima entrada del registro': 'RC-044',
}


def clasificar(rel):
    for reg, lista in REGIMEN.items():
        if rel in lista:
            return reg
    return 'SIN-CLASIFICAR'


def documentos():
    out = []
    for dp, dn, fn in os.walk(RAIZ):
        dn[:] = [d for d in dn if d not in
                 ('.git', '__pycache__', '_cache_experimentos', '_i3bis_cache')
                 and not d.startswith('_APARTADO')]
        for f in fn:
            if f.endswith(('.md', '.txt', '.tex')) or f == 'app.py':
                rel = os.path.relpath(os.path.join(dp, f), RAIZ).replace('\\', '/')
                if rel.startswith('Springer') or rel == 'requirements.txt':
                    continue
                out.append(rel)
    return sorted(out)


def main():
    hallazgos = []
    sin_clasificar = []
    for rel in documentos():
        reg = clasificar(rel)
        if reg == 'SIN-CLASIFICAR':
            sin_clasificar.append(rel)
            continue
        if reg != 'VIVO':
            continue
        texto = open(os.path.join(RAIZ, rel), encoding='utf8', errors='ignore').read()
        lineas = texto.splitlines()
        for etiqueta, patron, porque, arreglo in REGLAS:
            for i, l in enumerate(lineas, 1):
                if re.search(patron, l):
                    # exculpar lineas que ya se marcan como historicas
                    ctx = ' '.join(lineas[max(0, i - 3):i + 2]).lower()
                    if any(w in ctx for w in ('obsolet', 'descartad', 'retirad', 'antiguo',
                                              'históric', 'historic', 'sustituid', 'ya no',
                                              'refutad', 'apartad', 'derogad', 'corregid',
                                              'target sustituido', 'ya no es ciert',
                                              'no se reescrib', '⚠')):
                        continue
                    hallazgos.append({'documento': rel, 'linea': i, 'regla': etiqueta,
                                      'texto': l.strip()[:150], 'porque': porque,
                                      'arreglo': arreglo})

    print('=' * 78)
    print('AUDITORÍA DE DOCUMENTOS — contraste contra la verdad de referencia')
    print('=' * 78)
    docs = documentos()
    print(f'\nDocumentos analizados: {len(docs)}')
    for reg in ('VIVO', 'HISTORICO', 'PUBLICADO'):
        n = sum(1 for d in docs if clasificar(d) == reg)
        print(f'   {reg:12s} {n:3d}')
    if sin_clasificar:
        print(f'\n⚠ SIN CLASIFICAR ({len(sin_clasificar)}) — revisar a mano:')
        for d in sin_clasificar:
            print(f'     {d}')

    print(f'\n{"─" * 78}\nHALLAZGOS EN DOCUMENTOS VIVOS: {len(hallazgos)}\n{"─" * 78}')
    por_doc = {}
    for h in hallazgos:
        por_doc.setdefault(h['documento'], []).append(h)
    for doc in sorted(por_doc, key=lambda d: -len(por_doc[d])):
        hs = por_doc[doc]
        print(f'\n■ {doc}  ({len(hs)} hallazgo{"s" if len(hs) > 1 else ""})')
        vistas = set()
        for h in hs:
            clave = (h['regla'], h['texto'][:60])
            if clave in vistas:
                continue
            vistas.add(clave)
            print(f'   L{h["linea"]:<5d} [{h["regla"]}] {h["texto"][:110]}')
    if not hallazgos:
        print('\n   Ninguno.')

    json.dump(hallazgos, open(os.path.join(RAIZ, 'informe_coherencia_documental.json'), 'w',
                              encoding='utf8'), ensure_ascii=False, indent=1)
    print(f'\n[OK] detalle en informe_coherencia_documental.json')
    return len(hallazgos)


if __name__ == '__main__':
    sys.exit(0 if main() == 0 else 1)
