"""Diagramas de la ponencia en formato draw.io (.drawio editables) — Joan D. Martínez, CICI 2026."""
from xml.sax.saxutils import escape
import pathlib
OUT = pathlib.Path('/tmp/claude-0/dio/out')
F = 'fontFamily=Carlito;'
INK, MUT = '#0F1E36', '#55657E'
BL, BLF = '#2A78D6', '#E3ECF8'
GR, GRF = '#1BAF7A', '#E2F4EC'
OR, ORF = '#EB6834', '#FBE3DC'
TE, TEF = '#0F766E', '#E0F2F1'
VI, VIF = '#4A3AA7', '#ECE9F7'
AM, AMF = '#C98A00', '#FDF1D8'
RD, RDF = '#C0392B', '#FBE9E7'
GY, GYF = '#7F7F7F', '#F2F2F2'


class D:
    def __init__(s):
        s.c, s.n = [], 1

    def v(s, label, x, y, w, h, style, parent='1', id=None):
        s.n += 1; id = id or f'v{s.n}'
        s.c.append(f'<mxCell id="{id}" value="{escape(label, {chr(34): "&quot;"})}" style="{style}" vertex="1" parent="{parent}">'
                   f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return id

    def e(s, a, b, style='', label='', parent='1', pos=None):
        s.n += 1; id = f'e{s.n}'
        gx = '' if pos is None else f'x="{pos}" '
        s.c.append(f'<mxCell id="{id}" value="{escape(label, {chr(34): "&quot;"})}" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;'
                   f'endArrow=blockThin;endFill=1;endSize=10;strokeWidth=2.5;strokeColor=#555555;{F}fontSize=21;fontColor={MUT};{style}" '
                   f'edge="1" parent="{parent}" source="{a}" target="{b}"><mxGeometry {gx}relative="1" as="geometry"/></mxCell>')
        return id

    def xml(s):
        return '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(s.c) + '</root></mxGraphModel>'


def caja(stroke, fill, fs=26, extra=''):
    return (f'rounded=1;arcSize=12;whiteSpace=wrap;html=1;{F}fontSize={fs};fontColor={INK};'
            f'strokeColor={stroke};fillColor={fill};strokeWidth=2.5;{extra}')


def grupo(stroke, fill='none', dashed=0, fs=24):
    return (f'rounded=1;arcSize=4;whiteSpace=wrap;html=1;{F}fontSize={fs};fontColor={stroke};verticalAlign=top;align=left;'
            f'spacingLeft=14;spacingTop=6;strokeColor={stroke};fillColor={fill};strokeWidth=2.5;dashed={dashed};container=1;collapsible=0;')


# ── 1 · Validación cruzada anidada ───────────────────────────────────────────
def anidada():
    d = D()
    datos = d.v('<b>80 estudiantes</b><br><font style="font-size:22px">19 perdieron la calidad de estudiante</font>',
                0, 245, 180, 210, caja(GY, GYF))
    rep = d.v('<b>Se repite 10 veces</b> · cada vez con un reparto distinto de los 80', 210, 0, 1160, 660, grupo(BL, '#F7FAFE', 0, 25))
    rp = d.v('<b>Repartir</b> en 5 grupos de 16<br><font style="font-size:21px">estratificado: 3-4 casos por grupo</font>',
             20, 275, 180, 150, caja(BL, '#FFFFFF', 24), parent=rep)
    cols = ['#2A78D6', '#1BAF7A', '#EDA100', '#EB6834', '#E87BA4']
    for k, c in enumerate(cols):
        d.v(chr(65 + k), 32 + k * 32, 440, 28, 28, f'rounded=1;html=1;{F}fontSize=17;fontStyle=1;fontColor=#FFFFFF;fillColor={c};strokeColor=none;', parent=rep)
    vu = d.v('<b>5 vueltas</b> · cada grupo es el examen una vez', 230, 70, 690, 560, grupo(TE, '#FFFFFF', 0, 25), parent=rep)
    tr = d.v('<b>64 entrenan</b><br><font style="font-size:22px">4 grupos</font>', 25, 85, 185, 120, caja(BL, BLF), parent=vu)
    te = d.v('<b>16 de examen</b><br><font style="font-size:22px">1 grupo, apartado</font>', 25, 405, 185, 120, caja(GR, GRF), parent=vu)
    inn = d.v('<b>Validación interna</b> · solo con los 64', 245, 50, 425, 190, grupo(OR, '#FFF8F5', 1, 23), parent=vu)
    d.v('4 particiones × 24 combinaciones<br>de hiperparámetros<br><b>gana la de mejor AUC-PR</b>', 15, 50, 395, 125,
        f'text;html=1;whiteSpace=wrap;align=center;verticalAlign=middle;{F}fontSize=24;fontColor={INK};', parent=inn)
    rf = d.v('<b>Reentrenar</b> la ganadora con los 64', 245, 290, 425, 75, caja(BL, BLF, 24), parent=vu)
    pr = d.v('<b>Predecir a los 16</b><br><font style="font-size:22px">nunca participaron en la elección</font>',
             245, 405, 425, 120, caja(GR, '#FFFFFF', 26, 'strokeWidth=3;'), parent=vu)
    d.e(tr, inn, parent=vu); d.e(inn, rf, parent=vu); d.e(rf, pr, parent=vu); d.e(te, pr, parent=vu)
    po = d.v('<b>80 predicciones</b><br><font style="font-size:22px">fuera de muestra</font><br><br>→ <b>1 AUC-PR</b>',
             940, 245, 200, 210, caja(VI, VIF), parent=rep)
    fin = d.v('<b>10 AUC-PR</b><br>por algoritmo<br><font style="font-size:22px">media ± DE<br>t de Nadeau-Bengio</font>',
              1400, 225, 200, 250, caja(VI, '#FFFFFF', 27, 'strokeWidth=3;'))
    d.e(datos, rp); d.e(rp, vu); d.e(vu, po); d.e(po, fin)
    return d.xml()


# ── 2 · Equivalencias del primer año ─────────────────────────────────────────
def equivalencias():
    d = D()
    pares = [('Fundamentos de Programación', 1, 'Algoritmia y programación', 1), ('Matemáticas I', 1, 'Cálculo diferencial', 1),
             ('Álgebra Lineal', 1, 'Álgebra lineal', 2), ('Programación', 2, 'Programación orientada a objetos', 2),
             ('Matemáticas II', 2, 'Cálculo integral', 2), ('Física I', 2, 'Física mecánica', 2),
             ('Electrónica Básica', 3, 'Sistemas digitales', 2)]
    crit = {'Matemáticas II', 'Física I', 'Álgebra Lineal', 'Matemáticas I', 'Fundamentos de Programación'}
    hd = f'text;html=1;align=center;verticalAlign=middle;{F}fontSize=27;fontColor={INK};'
    d.v('<b>Plan 2011</b> <font color="#55657E">· códigos 602xxx</font>', 0, 0, 560, 50, hd)
    d.v('<b>Plan 2018</b> <font color="#55657E">· códigos 603xxx</font>', 900, 0, 600, 50, hd)
    d.v('Resolución Académica<br>036 de 2017', 600, 0, 260, 60, f'text;html=1;align=center;verticalAlign=middle;{F}fontSize=21;fontColor={MUT};')
    for i, (a, sa, b, sb) in enumerate(pares):
        y = 75 + i * 76
        c = a in crit
        l = d.v(f'{"<b>" if c else ""}{a}{"</b>" if c else ""}', 0, y, 560, 60,
                caja(RD if c else GY, RDF if c else '#FFFFFF', 25, 'align=left;spacingLeft=18;'))
        d.v(f'sem {sa}', 470, y + 14, 74, 32, f'rounded=1;arcSize=50;html=1;{F}fontSize=19;fontColor={MUT};fillColor=#FFFFFF;strokeColor=#C9D3E0;')
        r = d.v(b, 900, y, 600, 60, caja(BL, BLF, 25, 'align=left;spacingLeft=18;'))
        d.v(f'sem {sb}', 1410, y + 14, 74, 32, f'rounded=1;arcSize=50;html=1;{F}fontSize=19;fontColor={MUT};fillColor=#FFFFFF;strokeColor=#C9D3E0;')
        d.e(l, r, 'edgeStyle=none;strokeColor=#8A96A8;strokeWidth=2.2;fontSize=26;fontColor=#8A96A8;labelBackgroundColor=#FFFFFF;', '≡')
    y = 75 + 7 * 76 + 10
    d.v('', 0, y + 8, 26, 26, f'rounded=1;html=1;fillColor={RDF};strokeColor={RD};strokeWidth=2.5;')
    d.v('asignatura crítica (top 5 del índice de criticidad)', 36, y, 620, 42,
        f'text;html=1;align=left;verticalAlign=middle;{F}fontSize=22;fontColor={MUT};')
    d.v('los intentos de un mismo curso se suman entre planes', 900, y, 600, 42,
        f'text;html=1;align=right;verticalAlign=middle;{F}fontSize=22;fontColor={MUT};')
    return d.xml()


# ── 3 · Arquitectura de TRAYECTA ─────────────────────────────────────────────
def trayecta():
    d = D()
    sub = lambda t: f'<br><font style="font-size:21px" color="#55657E">{t}</font>'
    siif = d.v('<b>Extracto SIIF</b>' + sub('notas + Saber 11<br>sin nombres'), 0, 75, 240, 170,
               f'shape=cylinder3;boundedLbl=1;size=16;whiteSpace=wrap;html=1;{F}fontSize=26;fontColor={INK};strokeColor={GY};fillColor={GYF};strokeWidth=2.5;')
    eq = d.v('<b>Equivalencias</b>' + sub('plan 2011 ↔ 2018<br>Res. 036 de 2017'), 320, 90, 260, 140, caja(AM, AMF))
    re = d.v('<b>Reglas del reglamento</b>' + sub('situación de cada semestre'), 670, 0, 330, 130, caja(GR, GRF))
    mo = d.v('<b>Modelos</b>' + sub('alerta de bajo rendimiento<br>probabilidad de graduación'), 670, 190, 330, 130, caja(BL, BLF))
    pa = d.v('<b>Pantallas</b>' + sub('cohorte · ficha · carga<br>simulador'), 1090, 90, 280, 140, caja(VI, VIF))
    us = d.v('equipo de<br>acompañamiento', 1450, 100, 110, 120,
             f'shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;{F}fontSize=21;fontColor={MUT};strokeColor={INK};strokeWidth=2.5;fillColor=#FFFFFF;')
    d.e(siif, eq); d.e(eq, re); d.e(eq, mo); d.e(re, pa); d.e(mo, pa); d.e(pa, us)
    return d.xml()


for nombre, f in [('validacion_anidada', anidada), ('equivalencias_primer_anio', equivalencias), ('arquitectura_trayecta', trayecta)]:
    x = f()
    (OUT / f'{nombre}.xml').write_text(x, encoding='utf-8')
    (OUT / f'{nombre}.drawio').write_text(f'<mxfile host="CICI2026"><diagram name="{nombre}">{x}</diagram></mxfile>', encoding='utf-8')
    print('ok', nombre, len(x))


# ── 4 · CRISP-DM con regresos (lámina 4, izquierda) ──────────────────────────
def crisp_flujo():
    d = D()
    fases = [(1, 'Negocio', 'Definir el problema', BL, BLF, 0, 30), (2, 'Datos', '6 fuentes del SIIF', GR, GRF, 470, 30),
             (3, 'Preparación', 'Limpiar e integrar', AM, AMF, 940, 30), (4, 'Modelado', '5 algoritmos', OR, ORF, 940, 430),
             (5, 'Evaluación', 'Métricas y pruebas', VI, VIF, 470, 430), (6, 'Despliegue', 'TRAYECTA', TE, TEF, 0, 430)]
    ids = {}
    for n, t, s, c, f, x, y in fases:
        ids[n] = d.v(f'<b style="font-size:34px">{t}</b><br><font color="#55657E">{s}</font>', x, y, 400, 140,
                     caja(c, f, 27, f'align=left;spacingLeft=118;strokeWidth=3;'))
        d.v(str(n), x + 24, y + 30, 80, 80, f'ellipse;html=1;{F}fontSize=40;fontStyle=1;fontColor=#FFFFFF;fillColor={c};strokeColor=none;')
    for a, b in [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]:
        d.e(ids[a], ids[b], 'strokeColor=#2B3A55;strokeWidth=3.5;')
    rr = f'edgeStyle=none;dashed=1;dashPattern=8 6;strokeColor={RD};strokeWidth=3;fontColor={RD};fontSize=24;labelBackgroundColor=#FFFFFF;'
    d.e(ids[4], ids[1], rr + 'exitX=0.25;exitY=0;entryX=0.75;entryY=1;', 'nueva variable objetivo (art. 19)', pos=0.55)
    d.e(ids[5], ids[3], rr + 'exitX=0.75;exitY=0;entryX=0.25;entryY=1;', 'codificación y estados', pos=0.6)
    leg = d.v('', 0, 625, 440, 100, f'rounded=1;arcSize=10;html=1;fillColor=#FFFFFF;strokeColor=#C9D3E0;strokeWidth=2;')
    for k, (txt, est) in enumerate([('Flujo principal', 'strokeColor=#2B3A55;'), ('Retroalimentación / dependencia', f'dashed=1;dashPattern=8 6;strokeColor={RD};')]):
        y = 650 + k * 45
        a = d.v('', 20, y, 1, 1, 'text;html=1;'); b = d.v('', 95, y, 1, 1, 'text;html=1;')
        d.e(a, b, 'edgeStyle=none;strokeWidth=3;' + est)
        d.v(txt, 110, y - 18, 320, 36, f'text;html=1;align=left;verticalAlign=middle;{F}fontSize=23;fontColor={INK};')
    return d.xml()


# ── 5 · CRISP-DM adaptado al proyecto (lámina 4, derecha; contenido del autor) ─
def crisp_ciclo():
    d = D(); O = 30
    flecha = f'endArrow=block;endFill=1;endSize=12;strokeWidth=3.5;strokeColor={INK};'
    d.v('', O, O, 900, 900, f'rounded=1;arcSize=12;html=1;fillColor=none;strokeColor={INK};strokeWidth=3.5;')
    for x, y, rot in [(440, -12, 0), (888, 440, 90), (440, 888, 180), (-12, 440, 270)]:
        d.v('', O + x, O + y, 24, 24, f'triangle;html=1;fillColor={INK};strokeColor=none;rotation={rot};')
    caj = lambda t, x, y, w: d.v(f'<b>{t}</b>', x, y, w, 66, f'rounded=0;whiteSpace=wrap;html=1;{F}fontSize=23;fontColor={INK};fillColor=#FFFFFF;strokeColor=#555555;strokeWidth=1.5;')
    txt = lambda t, x, y, w, h: d.v(t, x, y, w, h, f'text;html=1;whiteSpace=wrap;align=center;verticalAlign=top;{F}fontSize=22;fontColor={INK};')
    def etapa(n, x, y, w, h, c, f):
        x += O; y += O
        e = d.v('', x, y, w, h, caja(c, f, 22, 'strokeWidth=3;'))
        d.v(f'Etapa {n}', x + w / 2 - 55, y - 18, 110, 34, f'rounded=1;html=1;{F}fontSize=20;fontColor={INK};fillColor={f};strokeColor={c};strokeWidth=2;')
        return e, x, y
    e1, x, y = etapa(1, 50, 60, 520, 210, AM, AMF)
    cn = caj('Comprensión del Negocio', x + 25, y + 30, 200); cd = caj('Comprensión de los Datos', x + 295, y + 30, 200)
    d.e(cd, cn, flecha + 'edgeStyle=none;exitX=0;exitY=0.3;entryX=1;entryY=0.3;strokeWidth=3;')
    d.e(cn, cd, flecha + 'edgeStyle=none;exitX=1;exitY=0.7;entryX=0;entryY=0.7;strokeWidth=3;')
    txt('Delimitación de la variable objetivo y exploración visual del contexto sociodemográfico y académico.', x + 20, y + 110, 480, 80)
    e2, x, y = etapa(2, 630, 90, 230, 240, BL, BLF)
    caj('Preparación de los Datos', x + 25, y + 30, 180); txt('Depuración, integración y transformación de los registros', x + 10, y + 110, 210, 120)
    e3, x, y = etapa(3, 630, 400, 230, 220, RD, RDF)
    caj('Modelado', x + 25, y + 30, 180); txt('Entrenamiento y ajuste de los algoritmos candidatos', x + 10, y + 110, 210, 100)
    e4, x, y = etapa(4, 330, 640, 270, 215, GY, GYF)
    caj('Evaluación', x + 35, y + 30, 200); txt('Validación técnica e institucional; análisis de predictores', x + 10, y + 108, 250, 80)
    e5, x, y = etapa(5, 50, 400, 250, 220, GR, GRF)
    caj('Documentación y transferencia', x + 25, y + 30, 200); txt('Empaquetado del modelo y documentación técnica', x + 10, y + 110, 230, 100)
    d.v('<b>Datos</b>', O + 385, O + 345, 130, 190, f'shape=cylinder3;boundedLbl=1;size=22;verticalLabelPosition=bottom;verticalAlign=top;html=1;{F}fontSize=28;fontColor={INK};fillColor=#FFFFFF;strokeColor={INK};strokeWidth=3.5;')
    d.e(e1, e2, flecha + 'exitX=1;exitY=0.4;entryX=0;entryY=0.225;')
    d.e(e2, e3, flecha + 'exitX=0.85;exitY=1;entryX=0.85;entryY=0;')
    d.e(e3, e2, flecha + 'exitX=0.15;exitY=0;entryX=0.15;entryY=1;')
    d.e(e3, e4, flecha + 'exitX=0.5;exitY=1;entryX=1;entryY=0.6;')
    d.e(e4, e1, flecha + 'exitX=1;exitY=0.2;entryX=1;entryY=0.8;')
    d.e(e4, e5, flecha + 'exitX=0;exitY=0.6;entryX=0.5;entryY=1;')
    return d.xml()


for nombre, f in [('crisp_flujo', crisp_flujo), ('crisp_ciclo', crisp_ciclo)]:
    x = f()
    (OUT / f'{nombre}.xml').write_text(x, encoding='utf-8')
    (OUT / f'{nombre}.drawio').write_text(f'<mxfile host="CICI2026"><diagram name="{nombre}">{x}</diagram></mxfile>', encoding='utf-8')
    print('ok', nombre, len(x))
