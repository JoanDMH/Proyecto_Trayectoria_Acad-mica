"""Diagramas con Graphviz (dot) para la ponencia."""
import subprocess

O = '/tmp/claude-0/d3/fig/'
FONT = 'Carlito'


def render(nombre, dot):
    subprocess.run(['dot', '-Tpng', '-Gdpi=220', '-o', O + nombre], input=dot.encode('utf-8'), check=True)
    print('ok', nombre)


# 1 · CRISP-DM con las iteraciones reales
render('d1_crispdm.png', f'''
digraph G {{
  rankdir=LR; bgcolor="white"; nodesep=0.9; ranksep=0.9; pad=0.2; newrank=true;
  node [shape=box, style="rounded,filled", fontname="{FONT}", fontsize=24, penwidth=2.2, width=2.9, height=1.25, margin="0.18,0.1"];
  edge [fontname="{FONT}", fontsize=19, penwidth=2.2, color="#555555"];
  n [label=<<b>1 · Negocio</b><br/><font point-size="19">definir el problema</font>>, fillcolor="#e3ecf8", color="#2a78d6"];
  d [label=<<b>2 · Datos</b><br/><font point-size="19">6 fuentes del SIIF</font>>, fillcolor="#e2f4ec", color="#1baf7a"];
  p [label=<<b>3 · Preparación</b><br/><font point-size="19">limpiar e integrar</font>>, fillcolor="#fdf1d8", color="#eda100"];
  m [label=<<b>4 · Modelado</b><br/><font point-size="19">5 algoritmos</font>>, fillcolor="#fbe3dc", color="#eb6834"];
  e [label=<<b>5 · Evaluación</b><br/><font point-size="19">métricas y pruebas</font>>, fillcolor="#ece9f7", color="#4a3aa7"];
  s [label=<<b>6 · Despliegue</b><br/><font point-size="19">TRAYECTA</font>>, fillcolor="#e0f2f1", color="#0f766e"];
  {{rank=same; n; s;}} {{rank=same; d; e;}} {{rank=same; p; m;}}
  n -> d -> p; p -> m;
  s -> e -> m [style=invis];
  m -> e [constraint=false]; e -> s [constraint=false];
  e -> p [label=" codificación y estados ", color="#c0392b", fontcolor="#c0392b", style=dashed, constraint=false];
  m -> n [label=" nueva variable objetivo (art. 19) ", color="#c0392b", fontcolor="#c0392b", style=dashed, constraint=false];
}}''')

# 2 · Validación cruzada anidada
render('d2_anidada.png', f'''
digraph G {{
  rankdir=TB; ordering=out; bgcolor="white"; nodesep=0.45; ranksep=0.5; pad=0.2; newrank=true;
  node [shape=box, style="rounded,filled", fontname="{FONT}", fontsize=22, penwidth=2, margin="0.2,0.1"];
  edge [fontname="{FONT}", fontsize=18, penwidth=2, color="#555555"];
  datos [label=<<b>80 estudiantes</b> · 19 casos del art. 19>, fillcolor="#f2f2f2", color="#7f7f7f"];
  subgraph cluster_ext {{
    label=<<b>10 repeticiones × 5 particiones externas estratificadas</b>>; fontname="{FONT}"; fontsize=21; style="rounded"; color="#2a78d6"; penwidth=2.2;
    ent [label=<<b>Entrenamiento</b><br/><font point-size="18">64 estudiantes</font>>, fillcolor="#e3ecf8", color="#2a78d6"];
    grid [label=<<b>Rejilla interna</b><br/><font point-size="18">4 particiones · 16-24 combinaciones<br/>criterio: AUC-PR</font>>, fillcolor="#fbe3dc", color="#eb6834", style="rounded,filled,dashed"];
    mejor [label=<<b>Mejor configuración</b><br/><font point-size="18">reentrenada con los 64</font>>, fillcolor="#e3ecf8", color="#2a78d6"];
    prueba [label=<<b>Evaluación</b><br/><font point-size="18">16 nunca vistos</font>>, fillcolor="#e2f4ec", color="#1baf7a"];
    {{rank=same; ent; grid; mejor; prueba;}}
  }}
  res [label=<<b>50 mediciones por algoritmo</b> · media ± desviación · t de Nadeau-Bengio>, fillcolor="#ece9f7", color="#4a3aa7"];
  datos -> ent; ent -> grid -> mejor -> prueba; prueba -> res;
  datos -> res [style=invis];
}}''')

# 3 · Arquitectura de TRAYECTA
render('d3_trayecta.png', f'''
digraph G {{
  rankdir=LR; bgcolor="white"; nodesep=0.35; ranksep=0.55; pad=0.2;
  node [shape=box, style="rounded,filled", fontname="{FONT}", fontsize=19, penwidth=2, margin="0.2,0.12"];
  edge [penwidth=2, color="#555555"];
  a [label=<<b>Extracto SIIF</b><br/><font point-size="15">notas + Saber 11<br/>sin nombres</font>>, fillcolor="#f2f2f2", color="#7f7f7f"];
  b [label=<<b>Equivalencias</b><br/><font point-size="15">plan 2011 ↔ 2018<br/>Res. 036 de 2017</font>>, fillcolor="#fdf1d8", color="#eda100"];
  c [label=<<b>Reglas</b><br/><font point-size="15">arts. 19, 20 y 21<br/>semestre a semestre</font>>, fillcolor="#e2f4ec", color="#1baf7a"];
  d [label=<<b>Modelos</b><br/><font point-size="15">alerta art. 19<br/>graduación</font>>, fillcolor="#e3ecf8", color="#2a78d6"];
  e [label=<<b>Pantallas</b><br/><font point-size="15">cohorte · ficha · carga<br/>simulador · evidencia</font>>, fillcolor="#ece9f7", color="#4a3aa7"];
  a -> b -> c -> e; b -> d -> e;
}}''')

# 4 · Equivalencias del primer año
pares = [('Fundamentos de Programación', '1', 'Algoritmia y programación', '1'), ('Matemáticas I', '1', 'Cálculo diferencial', '1'),
         ('Álgebra Lineal', '1', 'Álgebra lineal', '2'), ('Programación', '2', 'Programación orientada a objetos', '2'),
         ('Matemáticas II', '2', 'Cálculo integral', '2'), ('Física I', '2', 'Física mecánica', '2'),
         ('Electrónica Básica', '3', 'Sistemas digitales', '2')]
crit = {'Matemáticas II', 'Física I', 'Álgebra Lineal', 'Matemáticas I', 'Fundamentos de Programación'}
lin = []
for i, (a, sa, b, sb) in enumerate(pares[::-1]):
    col = '#c0392b' if a in crit else '#7f7f7f'
    lin.append(f'v{i} [label=<{a} <font color="#7f7f7f">· sem {sa}</font>>, color="{col}", fillcolor="{"#fbe9e7" if a in crit else "#f2f2f2"}"];')
    lin.append(f'n{i} [label=<{b} <font color="#7f7f7f">· sem {sb}</font>>, color="#2a78d6", fillcolor="#e3ecf8"];')
    lin.append(f'v{i} -> n{i};')
render('d4_equivalencias.png', f'''
digraph G {{
  rankdir=LR; bgcolor="white"; nodesep=0.12; ranksep=1.6; pad=0.15;
  node [shape=box, style="rounded,filled", fontname="{FONT}", fontsize=18, penwidth=1.8, width=3.8, margin="0.15,0.06"];
  edge [penwidth=1.8, color="#555555", arrowsize=.8];
  t1 [label=<<b>Plan 2011 (602xxx)</b>>, shape=plaintext, style="", fontsize=20];
  t2 [label=<<b>Plan 2018 (603xxx)</b>>, shape=plaintext, style="", fontsize=20];
  t1 -> t2 [style=invis];
  {' '.join(lin)}
}}''')
