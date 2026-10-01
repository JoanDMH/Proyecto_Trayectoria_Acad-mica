"""Genera bitacora/CONSOLIDADO_RESULTADOS.xlsx a partir de los CSV de src/."""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, 'src')
OUT = os.path.join(RAIZ, 'bitacora', 'CONSOLIDADO_RESULTADOS.xlsx')
F = 'Arial'
AZUL, GRIS, AMAR = '1B6CA8', 'F0F4F8', 'FFF2CC'

tit = Font(name=F, size=14, bold=True, color='FFFFFF')
sub = Font(name=F, size=11, bold=True, color=AZUL)
hdr = Font(name=F, size=10, bold=True, color='FFFFFF')
nor = Font(name=F, size=10)
neg = Font(name=F, size=10, bold=True)
fill_tit = PatternFill('solid', fgColor=AZUL)
fill_hdr = PatternFill('solid', fgColor='34495E')
fill_alt = PatternFill('solid', fgColor=GRIS)
fill_ok = PatternFill('solid', fgColor='D5F5E3')
fill_bad = PatternFill('solid', fgColor='FDEDEC')
fill_warn = PatternFill('solid', fgColor=AMAR)
bd = Border(*[Side(style='thin', color='BDC3C7')] * 4)
wrap = Alignment(wrap_text=True, vertical='top')
ctr = Alignment(horizontal='center', vertical='center')

wb = Workbook(); wb.remove(wb.active)


def titulo(ws, txt, ncol, fila=1):
    ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=ncol)
    c = ws.cell(fila, 1, txt); c.font = tit; c.fill = fill_tit; c.alignment = ctr
    ws.row_dimensions[fila].height = 24


def nota(ws, fila, txt, ncol, fill=None):
    ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=ncol)
    c = ws.cell(fila, 1, txt); c.font = Font(name=F, size=9, italic=True); c.alignment = wrap
    if fill: c.fill = fill
    ws.row_dimensions[fila].height = 32


def tabla(ws, df, fila, anchos=None, fmt=None, resalta=None):
    for j, col in enumerate(df.columns, 1):
        c = ws.cell(fila, j, str(col)); c.font = hdr; c.fill = fill_hdr
        c.border = bd; c.alignment = ctr
    for i, (_, rw) in enumerate(df.iterrows(), 1):
        for j, col in enumerate(df.columns, 1):
            v = rw[col]
            if isinstance(v, np.floating): v = float(v)
            if isinstance(v, np.integer): v = int(v)
            if pd.isna(v) if not isinstance(v, str) else False: v = None
            c = ws.cell(fila + i, j, v); c.font = nor; c.border = bd
            if i % 2 == 0: c.fill = fill_alt
            if fmt and col in fmt: c.number_format = fmt[col]
            if resalta and resalta(rw, col):
                c.font = neg; c.fill = fill_ok
    if anchos:
        for j, w in enumerate(anchos, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
    return fila + len(df) + 1


# ═══ 1 · RESUMEN ═══
ws = wb.create_sheet('1 · Resumen')
titulo(ws, 'CONSOLIDADO DE RESULTADOS — Modelo predictivo de trayectoria académica FCBI', 6)
ws['A2'] = 'Universidad de los Llanos · Ing. de Sistemas · Cohortes 2017-2 y 2018-1 · Corte: 2026-09-29'
ws['A2'].font = Font(name=F, size=10, italic=True)
r = 4
ws.cell(r, 1, 'ESTADO ACTUAL DEL MODELO').font = sub; r += 1
res = pd.DataFrame([
    ['Variable objetivo', 'Bajo rendimiento — Art. 19 del Reglamento Estudiantil', 'RC-017'],
    ['Definición', 'Reprobar 100% de créditos de un periodo regular Y promedio acumulado < 3,0; O reprobar un curso por 4ª vez', 'MARCO_NORMATIVO §3'],
    ['Población', 'n = 80 expuestos (de 90). Los 10 sin actividad no pueden activar el artículo', 'RC-020'],
    ['Positivos', '19 (23,8 %) — línea base AUC-PR = 0,2375', 'RC-020'],
    ['Variables', '6 (conjunto S3, solo académicas)', 'RC-032'],
    ['Modelo ganador', 'Random Forest — AUC-PR 0,745 ± 0,025', 'RC-033'],
    ['Protocolo', 'CV-5 × 10 repeticiones ANIDADA; rejillas equilibradas 16-24 combinaciones', 'RC-021, RC-025'],
    ['Criterio de umbral', 'Máxima detección. La capacidad de atención la decide la universidad', 'Decisión del estudiante'],
], columns=['Concepto', 'Valor', 'Fuente'])
r = tabla(ws, res, r, anchos=[26, 80, 22]) + 1
ws.cell(r, 1, 'CÓMO LEER ESTE ARCHIVO').font = sub; r += 1
guia = pd.DataFrame([
    ['2 · Selección variables', 'Por qué se pasó de 19 a 6 variables. Incluye el sesgo de selección medido (+0,150)', ''],
    ['3 · Comparación modelos', 'Los 5 algoritmos, antes y después de corregir el protocolo', ''],
    ['4 · Umbral operativo', 'Cuántos estudiantes detecta el modelo según el umbral elegido', ''],
    ['5 · Diagnóstico error', '¿Sobreajuste? ¿Faltan datos? Curva de aprendizaje y bootstrap', ''],
    ['6 · Errores corregidos', 'Las tres fugas de información y su magnitud', ''],
    ['9 · PCA y selección', 'Encargo del asesor: ¿respalda el PCA la selección de variables?', '2026-09-29'],
    ['10 · Modelos bayesianos', 'Encargo del asesor: Naive Bayes, logística bayesiana y proceso gaussiano', '2026-09-29'],
    ['11 · Pocos datos y tamaño', 'Encargo del asesor: few-shot y cuánto aportarán las cohortes nuevas', '2026-09-29'],
    ['7 · Cronología', 'Todas las decisiones con su registro RC', ''],
], columns=['Hoja', 'Qué responde', ''])
r = tabla(ws, guia, r, anchos=[26, 80, 22]) + 1
nota(ws, r, '⚠ AUC-PR se compara contra la línea base 0,2375 (prevalencia), NO contra 0,5. Un AUC-PR de 0,745 equivale a 3,1 veces el azar.', 6, fill_warn)

# ═══ 2 · SELECCIÓN DE VARIABLES ═══
ws = wb.create_sheet('2 · Selección variables')
titulo(ws, 'SELECCIÓN DE VARIABLES — ¿hacen falta 19 o bastan 6?', 7)
r = 3
ws.cell(r, 1, 'A · Ablación de subconjuntos definidos a priori').font = sub; r += 1
ab = pd.DataFrame([
    ['Set completo', 19, 'a priori', 0.7201, 0.0468, 'referencia'],
    ['S3 · solo académicas', 6, 'a priori', 0.7196, 0.0462, 'EMPATE (p=0,983)'],
    ['S5 · sin redundancias', 17, 'a priori', 0.7260, 0.0210, 'EMPATE (p=0,532)'],
    ['S7 · solo prom_sem1', 1, 'a priori', 0.6110, 0.0190, 'Peor'],
    ['S1 · sin primer semestre', 17, 'a priori', 0.4420, 0.0410, 'Peor'],
    ['S4 · solo socioeconómicas', 11, 'a priori', 0.3440, 0.0340, 'Muy inferior'],
], columns=['Subconjunto', 'N vars', 'Tipo', 'AUC-PR', 'sd', 'Veredicto vs. completo'])
r = tabla(ws, ab, r, anchos=[28, 9, 12, 11, 9, 26],
          fmt={'AUC-PR': '0.0000', 'sd': '0.0000'},
          resalta=lambda x, c: str(x['Subconjunto']).startswith('S3')) + 1
nota(ws, r, 'CONCLUSIÓN: 6 variables rinden igual que 19 (Δ = −0,0005; p = 0,983). Las socioeconómicas por sí solas apenas superan el azar (0,344 frente a 0,2375).', 7); r += 2

ws.cell(r, 1, 'B · El sesgo de selección — por qué NO se adoptó el "top-5"').font = sub; r += 1
sb = pd.DataFrame([
    ['Set completo (19)', 'a priori', 0.7201, '—'],
    ['S3 · académicas (6)', 'a priori', 0.7196, 'Empata con el completo'],
    ['top-5 CONTAMINADO', 'elegido viendo TODOS los datos', 0.8204, '⚠ INFLADO — no usar'],
    ['top-5 ANIDADO', 'elegido dentro de cada pliegue', 0.6705, 'Honesto: peor que S3'],
], columns=['Conjunto', 'Tipo de selección', 'AUC-PR', 'Lectura'])
r = tabla(ws, sb, r, anchos=[28, 34, 11, 34], fmt={'AUC-PR': '0.0000'})
ws.cell(r, 1, 'SESGO MEDIDO =').font = neg
c = ws.cell(r, 3, '=0.8204-0.6705'); c.font = neg; c.number_format = '0.0000'; c.fill = fill_bad
ws.cell(r, 4, '5 veces el umbral de relevancia (0,03)').font = neg; r += 2
nota(ws, r, 'Elegir las mejores variables mirando toda la muestra y evaluar sobre esa misma muestra infló el resultado en 0,150 de AUC-PR — más que la diferencia entre el mejor y el peor algoritmo. Habría llevado a adoptar un conjunto PEOR creyéndolo mejor.', 7, fill_bad); r += 2

ws.cell(r, 1, 'C · Importancia por permutación (caída de AUC-PR al barajar la variable)').font = sub; r += 1
imp = pd.read_csv(os.path.join(SRC, 'permutacion_importancia.csv'))
imp = imp.rename(columns={imp.columns[0]: 'Variable'})
imp = imp[['Variable', 'caida_AUC_PR_media', 'veces_positiva', 'MDI_referencia']].head(12)
imp.columns = ['Variable', 'Caída AUC-PR', 'Fiabilidad (% pliegues +)', 'Importancia MDI (engañosa)']
r = tabla(ws, imp, r, anchos=[24, 14, 22, 26],
          fmt={'Caída AUC-PR': '0.0000', 'Fiabilidad (% pliegues +)': '0%', 'Importancia MDI (engañosa)': '0.0000'}) + 1
nota(ws, r, '⚠ La importancia MDI NO mide poder predictivo. Prueba: al inyectar 2 columnas de ruido aleatorio puro capturaron el 14,3 % de la importancia MDI, una de ellas por encima de 13 variables reales. nivel_edu_madre tiene 7,6 % de MDI pero RESTA capacidad predictiva (−0,007).', 7, fill_warn); r += 2

ws.cell(r, 1, 'D · Redundancia estructural (VIF)').font = sub; r += 1
vif = pd.read_csv(os.path.join(SRC, 'redundancia_vif.csv')).head(6)
diag = ['Suma determinista de componentes incluidas', 'max(nivel_edu_padre, nivel_edu_madre)',
        'Colinealidad moderada', 'Aceptable', 'Aceptable', 'Aceptable']
vif['Diagnóstico'] = diag[:len(vif)]
vif.columns = ['Variable', 'R² vs. resto', 'VIF', 'Diagnóstico']
r = tabla(ws, vif, r, anchos=[24, 14, 10, 46], fmt={'R² vs. resto': '0.0000', 'VIF': '0.00'}) + 1

ws.cell(r, 1, 'E · Estabilidad de la selección (frecuencia en el top-5 entre 40 pliegues)').font = sub; r += 1
est = pd.read_csv(os.path.join(SRC, 'estabilidad_seleccion.csv'))
est.columns = ['Variable', 'Frecuencia']
r = tabla(ws, est, r, anchos=[24, 14], fmt={'Frecuencia': '0%'}) + 1
nota(ws, r, 'Solo prom_sem1 se elige el 100 % de las veces. Desde la 3ª posición la selección es casi azar: con 19 positivos, el ranking de importancia más allá del top-2/3 es RUIDO.', 7)

# ═══ 3 · COMPARACIÓN DE MODELOS ═══
ws = wb.create_sheet('3 · Comparación modelos')
titulo(ws, 'COMPARACIÓN DE ALGORITMOS — resultado definitivo (I-3 bis)', 6)
r = 3
ws.cell(r, 1, 'A · Resultado vigente · 6 variables (S3) · CV-5 × 10 anidada · rejillas equilibradas').font = sub; r += 1
t = pd.read_csv(os.path.join(SRC, 'i3bis_tabla_art19.csv'))
t.columns = ['Algoritmo', 'AUC-PR', 'sd', 'IC 95 % inf', 'IC 95 % sup']
t['Veces sobre el azar'] = np.nan
r0 = r + 1
r = tabla(ws, t, r, anchos=[26, 11, 9, 12, 12, 18],
          fmt={'AUC-PR': '0.0000', 'sd': '0.0000', 'IC 95 % inf': '0.0000',
               'IC 95 % sup': '0.0000', 'Veces sobre el azar': '0.00"x"'},
          resalta=lambda x, c: x['Algoritmo'] == 'Random Forest')
for i in range(len(t)):
    c = ws.cell(r0 + i, 6, f'=B{r0 + i}/0.2375')
    c.number_format = '0.00"x"'; c.font = nor; c.border = bd
r += 1
nota(ws, r, 'Random Forest gana POR LA REGLA PRE-REGISTRADA (empate técnico → orden de parsimonia), sin necesidad de desviación. Tiene además la menor dispersión del conjunto.', 6, fill_ok); r += 2

ws.cell(r, 1, 'B · Contrastes pareados (t corregido de Nadeau-Bengio)').font = sub; r += 1
cmp = pd.read_csv(os.path.join(SRC, 'i3bis_comparaciones_art19.csv'))
cmp = cmp[['modelo_a', 'modelo_b', 'diferencia', 'p_valor', 'veredicto']]
cmp.columns = ['Modelo A', 'Modelo B', 'Δ AUC-PR', 'p-valor', 'Veredicto']
r = tabla(ws, cmp, r, anchos=[26, 26, 11, 10, 62],
          fmt={'Δ AUC-PR': '+0.0000;-0.0000', 'p-valor': '0.0000'}) + 1

ws.cell(r, 1, 'C · Antes y después de corregir el protocolo').font = sub; r += 1
ant = pd.DataFrame([
    ['Random Forest', 0.569, 0.745, np.nan, 'Gana en ambos; sube al corregir'],
    ['SVM (RBF)', 0.573, 0.714, np.nan, 'Era 1º, ahora 2º'],
    ['XGBoost', 0.528, 0.630, np.nan, '⭐ Mayor recuperación: era último'],
    ['Árbol de Decisión', 0.463, 0.614, np.nan, 'Sube'],
    ['Regresión Logística', 0.548, 0.550, np.nan, 'Cae al último con 6 vars'],
], columns=['Algoritmo', 'I-3 (19 vars, desiguales)', 'I-3 bis (6 vars, equilibradas)', 'Cambio', 'Lectura'])
r1 = r + 1
r = tabla(ws, ant, r, anchos=[24, 26, 28, 11, 40],
          fmt={'I-3 (19 vars, desiguales)': '0.000', 'I-3 bis (6 vars, equilibradas)': '0.000',
               'Cambio': '+0.000;-0.000'})
for i in range(len(ant)):
    c = ws.cell(r1 + i, 4, f'=C{r1 + i}-B{r1 + i}')
    c.number_format = '+0.000;-0.000'; c.font = neg; c.border = bd
r += 1
nota(ws, r, 'XGBoost recuperó +0,102 SOLO por equilibrar la rejilla de búsqueda (antes tenía 8 combinaciones frente a 48 de Random Forest). Esa recuperación es MAYOR que la distancia entre el 1º y el 2º: un presupuesto de ajuste desigual no penaliza a un algoritmo, REORDENA la tabla completa.', 6, fill_warn); r += 2

ws.cell(r, 1, 'D · Presupuesto de búsqueda por algoritmo').font = sub; r += 1
pre = pd.DataFrame([
    ['Regresión Logística', 5, 16], ['Árbol de Decisión', 24, 24],
    ['Random Forest', 48, 24], ['SVM (RBF)', 12, 20], ['XGBoost', 8, 24],
], columns=['Algoritmo', 'Combinaciones en I-3', 'Combinaciones en I-3 bis'])
r = tabla(ws, pre, r, anchos=[26, 22, 24])

# ═══ 4 · UMBRAL ═══
ws = wb.create_sheet('4 · Umbral operativo')
titulo(ws, 'UMBRAL OPERATIVO — criterio: MÁXIMA DETECCIÓN de estudiantes en riesgo', 8)
r = 3
nota(ws, r, 'Decisión del estudiante: el objetivo es detectar el mayor número posible de casos en riesgo. La capacidad de atención es decisión de la universidad (art. 23), no un criterio del modelo.', 8, fill_ok); r += 2
cur = pd.read_csv(os.path.join(SRC, 'i3bis_curva_umbrales.csv'))
cur = cur[['umbral', 'Recall+', 'Prec+', 'n_alertas', 'pct_cohorte', 'lift_vs_azar', 'F1+', 'MCC']]
cur.columns = ['Umbral', 'Recall+ (detecta)', 'Precisión+', 'Alertas (de 80)', '% cohorte',
               'Veces sobre azar', 'F1+', 'MCC']
r = tabla(ws, cur, r, anchos=[10, 17, 12, 15, 11, 16, 9, 9],
          fmt={'Recall+ (detecta)': '0.000', 'Precisión+': '0.000', '% cohorte': '0%',
               'Veces sobre azar': '0.00"x"', 'F1+': '0.000', 'MCC': '0.000'},
          resalta=lambda x, c: float(x['Umbral']) in (0.06, 0.12)) + 1
nota(ws, r, 'LECTURA · Umbral 0,06 → detecta el 100 % (19 de 19) alertando sobre 66 estudiantes. Umbral 0,12 → detecta el 84 % con 52 alertas y mejor discriminación (1,30x sobre el azar). Por debajo de 0,06 el modelo se acerca a "alertar a todos" y pierde valor (1,01x).', 8, fill_warn); r += 2
ws.cell(r, 1, 'LIMITACIÓN INTRÍNSECA').font = sub; r += 1
nota(ws, r, 'Con 19 positivos entre 80, un modelo con AUC-PR 0,745 NO puede dar alta precisión y alta exhaustividad a la vez. Detectar el 100 % exige alertar sobre el 83 % de la cohorte. Es aritmética de la prevalencia, no un defecto corregible.', 8)

# ═══ 5 · DIAGNÓSTICO ═══
ws = wb.create_sheet('5 · Diagnóstico error')
titulo(ws, 'DIAGNÓSTICO — ¿sobreajuste o falta de datos?', 6)
r = 3
ws.cell(r, 1, 'A · Curva de aprendizaje (Random Forest)').font = sub; r += 1
ca = pd.read_csv(os.path.join(SRC, 'curva_aprendizaje.csv'))
ca.columns = ['Fracción', 'n entrenamiento', 'AUC-PR train', 'AUC-PR validación', 'sd validación']
r = tabla(ws, ca, r, anchos=[11, 17, 14, 18, 14],
          fmt={'Fracción': '0%', 'AUC-PR train': '0.000', 'AUC-PR validación': '0.000',
               'sd validación': '0.000'}) + 1
nota(ws, r, 'La validación sube de forma MONOTÓNICA Y SIN MESETA (0,557 → 0,768). El modelo está limitado por FALTA DE DATOS, no por el algoritmo. Es el argumento empírico para extender el estudio a la FCBI completa (n≈275).', 6, fill_ok); r += 2

ws.cell(r, 1, 'B · Brecha train–validación (sobreajuste)').font = sub; r += 1
br = pd.read_csv(os.path.join(SRC, 'brecha_train_val.csv'))
br.columns = ['Modelo', 'AUC-PR train', 'AUC-PR validación', 'Brecha', 'sd validación']
r = tabla(ws, br, r, anchos=[26, 14, 18, 11, 14],
          fmt={'AUC-PR train': '0.000', 'AUC-PR validación': '0.000', 'Brecha': '0.000',
               'sd validación': '0.000'}) + 1
nota(ws, r, 'Todos los modelos memorizan el entrenamiento (RF llega a 1,000). Con 64 casos y 15 positivos por pliegue, cualquier modelo con capacidad suficiente lo hará. Hay señal real (la validación supera ampliamente el 0,238 del azar) pero la varianza es alta.', 6); r += 2

ws.cell(r, 1, 'C · Bootstrap .632+ (estimador independiente de la validación cruzada)').font = sub; r += 1
bo = pd.read_csv(os.path.join(SRC, 'bootstrap_632.csv'))
bo.columns = ['Modelo', 'AUC-PR aparente', 'AUC-PR OOB', 'Peso w', 'AUC-PR .632+', 'n bootstrap']
r = tabla(ws, bo, r, anchos=[26, 17, 14, 10, 14, 12],
          fmt={'AUC-PR aparente': '0.000', 'AUC-PR OOB': '0.000', 'Peso w': '0.000',
               'AUC-PR .632+': '0.000'}) + 1
nota(ws, r, '⚠ La adaptación del .632+ a AUC-PR NO es canónica (el estimador se derivó para tasas de error). Se declara como tal. Es comparable con la ablación (hiperparámetros fijos), no con la CV anidada.', 6, fill_warn); r += 2

ws.cell(r, 1, 'D · Curva de validación de la regularización de XGBoost').font = sub; r += 1
cx = pd.read_csv(os.path.join(SRC, 'curva_validacion_xgb.csv'))
cx.columns = ['min_child_weight', 'reg_lambda', 'AUC-PR', 'sd']
r = tabla(ws, cx, r, anchos=[20, 14, 11, 9], fmt={'AUC-PR': '0.000', 'sd': '0.000'}) + 1
nota(ws, r, 'RESULTADO CONTRAINTUITIVO: regularizar AGRESIVAMENTE es contraproducente. min_child_weight=3 hunde el AUC-PR de 0,710 a 0,397 — con 15 positivos, exigir 3 instancias por hoja bloquea los cortes sobre la clase minoritaria.', 6, fill_warn)

# ═══ 6 · ERRORES ═══
ws = wb.create_sheet('6 · Errores corregidos')
titulo(ws, 'FUGAS DE INFORMACIÓN Y ERRORES CORREGIDOS — la contribución metodológica', 4)
r = 3
nota(ws, r, 'El estudio detectó la MISMA clase de error (usar información no disponible al momento de predecir) en TRES niveles independientes, y midió cada uno con datos propios. La fuga no es un accidente puntual sino un riesgo sistemático con muestras pequeñas.', 4, fill_warn); r += 2
fug = pd.DataFrame([
    ['1 · Temporal (variables)', 'prom_global era el promedio del RESTO de la carrera: entre el 70 % y el 83 % venía de semestres POSTERIORES a la asignatura predicha', 'AUC 0,865-0,939 → 0,70-0,74', 'RC-013'],
    ['2 · Hiperparámetros', 'La búsqueda en malla se hacía sobre toda la muestra y luego se medía por CV: los pliegues de prueba ya habían intervenido en elegir la configuración', '+0,046 en XGBoost / +0,008 en RF', 'RC-021'],
    ['3 · Selección de variables', 'El "top-5 por importancia" se elegía viendo toda la muestra y se evaluaba sobre esa misma muestra', '+0,150 de AUC-PR', 'RC-030, RC-032'],
], columns=['Nivel', 'Qué se filtraba', 'Efecto medido', 'Registro'])
r = tabla(ws, fug, r, anchos=[24, 70, 28, 16]) + 1
nota(ws, r, 'La fuga nº 3 se cometió DESPUÉS de haber documentado las otras dos. Ilustra mejor que cualquier argumento lo difícil que es evitarla incluso estando advertido.', 4, fill_bad); r += 2
ws.cell(r, 1, 'Otros errores detectados y corregidos').font = sub; r += 1
err = pd.DataFrame([
    ['Target tautológico', 'PROMEDIO_CARRERA incluía el 1er semestre, que era su propio predictor. Sin prom_sem1 el modelo caía a AUC 0,483 (azar)', 'RC-012'],
    ['Colisión de periodos', 'AAAA-0 (intersemestral) se mezclaba con AAAA-2: 133 registros afectados', 'RC-020'],
    ['Presupuesto desigual', 'Rejillas de 8 a 48 combinaciones según el algoritmo, sin regularización en XGBoost', 'RC-025'],
    ['Umbral por métrica errónea', 'Se elegía por F1-macro (favorece umbrales altos) en vez de por recall', 'RC-034'],
    ['Curva con 1 repetición', 'La curva de umbral usaba una sola repetición: techo falso de recall 0,684', 'RC-034'],
    ['Importancia MDI', 'Ruido aleatorio puro capturó el 14,3 % de la importancia MDI', 'RC-019'],
    ['Diccionario mal interpretado', 'C leída como "cancelada": se excluían 76 registros reales', 'RC-002'],
    ['Imputación post-terminal', 'Trámites fantasma tras la graduación generaban estados imputados inválidos', 'RC-002'],
], columns=['Error', 'Descripción y magnitud', 'Registro'])
r = tabla(ws, err, r, anchos=[26, 92, 16])

# ═══ 7 · CRONOLOGÍA ═══
ws = wb.create_sheet('7 · Cronología')
titulo(ws, 'CRONOLOGÍA DE DECISIONES — registro científico RC-012 a RC-034', 4)
r = 3
cro = pd.DataFrame([
    ['RC-012', '2026-09-02', 'Target tautológico detectado', 'Sustituir rendimiento_bajo'],
    ['RC-013', '2026-09-02', 'Fuga temporal en modelos por asignatura', 'Retirarlos del proyecto'],
    ['RC-014', '2026-09-02', 'Incorporación del Reglamento Estudiantil', 'Usar la definición institucional'],
    ['RC-015', '2026-09-02', 'Cambio de régimen 2003 → 2022', 'Re-derivar la etiqueta; supuesto declarado'],
    ['RC-016', '2026-09-02', 'El ganador cambia con el target', 'Umbral de relevancia ΔAUC ≥ 0,03'],
    ['RC-017', '2026-09-02', 'APROBADO: target del art. 19', 'n=80, 19 positivos'],
    ['RC-018', '2026-09-03', 'Imputación de prom_sem1 corregida', 'Indicador sin_primer_semestre'],
    ['RC-019', '2026-09-03', 'Verificación de I-2; MDI engañosa', 'Usar permutación, no MDI'],
    ['RC-020', '2026-09-03', 'Target implementado; colisión de periodos', '19 positivos, 0 dudosos'],
    ['RC-021', '2026-09-03', 'Sesgo por CV no anidada', 'Validación anidada obligatoria'],
    ['RC-022', '2026-09-03', 'Modelos por asignatura retirados', 'Índice de criticidad conservado'],
    ['RC-023', '2026-09-03', 'I-3: empate técnico a 3 bandas', 'RF con desviación declarada'],
    ['RC-024', '2026-09-15', 'No hubo selección empírica de variables', 'Implementar WP-OE1.2'],
    ['RC-025', '2026-09-15', 'Presupuesto de rejilla desigual', 'Equilibrar a 16-24 combinaciones'],
    ['RC-026', '2026-09-15', 'El error se estimaba solo por CV', 'Añadir .632+ y curvas'],
    ['RC-027', '2026-09-15', 'Instrumentación de bitácora', 'Métricas por repetición'],
    ['RC-028', '2026-09-15', 'Resultados de selección de variables', '[CORREGIDO por RC-030]'],
    ['RC-029', '2026-09-15', 'Diagnóstico de error', 'Limitado por datos, no por sesgo'],
    ['RC-030', '2026-09-15', 'Sesgo de selección detectado', 'Retirar el subconjunto S6'],
    ['RC-031', '2026-09-15', 'Regularización contraproducente', 'min_child_weight = 1'],
    ['RC-032', '2026-09-15', 'Sesgo medido: +0,150 de AUC-PR', 'Conjunto definitivo = S3'],
    ['RC-033', '2026-09-15', 'I-3 bis: Random Forest gana 0,745', 'Sin desviación del protocolo'],
    ['RC-034', '2026-09-15', 'Umbral corregido', 'Criterio de máxima detección'],
], columns=['RC', 'Fecha', 'Hallazgo', 'Decisión adoptada'])
r = tabla(ws, cro, r, anchos=[10, 12, 54, 44]) + 1
nota(ws, r, 'Detalle completo de cada entrada en REGISTRO_CIENTIFICO.md. Análisis extendido en AUDITORIA_2026-09.md.', 4)

# ═══ 8 · FCBI — VERIFICACIÓN DE LOS TRES PROGRAMAS ═══
if os.path.exists(os.path.join(SRC, 'fcbi_target_art19.csv')):
    ws = wb.create_sheet('8 · FCBI 3 programas')
    titulo(ws, 'VERIFICACIÓN FCBI — ¿aplica a Electrónica y Biología? ¿son mezclables?', 7)
    r = 3
    ws.cell(r, 1, 'A · Cobertura y llaves por programa').font = sub; r += 1
    cob = pd.read_csv(os.path.join(SRC, 'fcbi_cobertura.csv'))
    r = tabla(ws, cob, r, anchos=[14, 17, 14, 12, 18, 19, 26]) + 1
    nota(ws, r, 'Pérdida homogénea del 4,7 % en los tres programas, por la misma causa: admitidos sin actividad académica calificada. No hay un problema de calidad específico de Electrónica o Biología.', 7); r += 2

    ws.cell(r, 1, 'B · Target del art. 19 aplicado a los tres programas').font = sub; r += 1
    tg = pd.read_csv(os.path.join(SRC, 'fcbi_target_art19.csv'))
    r = tabla(ws, tg, r, anchos=[14, 22, 18, 13, 18, 20],
              fmt={'Prevalencia': '0.0%'},
              resalta=lambda x, c: x['Programa'] == 'Electrónica') + 1
    nota(ws, r, 'El target aplica a los tres. FCBI: 59 positivos de 234 expuestos (25,2 %). Electrónica tiene la mayor prevalencia (31,5 %). El 44 % de los eventos ocurre en el primer semestre, con proporciones casi idénticas entre programas: es un patrón ESTRUCTURAL, no una peculiaridad de Sistemas.', 7, fill_warn); r += 2

    ws.cell(r, 1, 'C · EDA comparativo — ¿son mezclables?').font = sub; r += 1
    eda = pd.read_csv(os.path.join(SRC, 'fcbi_eda_comparativo.csv'))
    r = tabla(ws, eda, r, anchos=[14, 8, 11, 15, 20, 18, 12, 17],
              fmt={'Mujeres': '0.0%', 'Tasa graduación': '0.0%',
                   'Prom. carrera medio': '0.000', 'Prom. carrera sd': '0.000'},
              resalta=lambda x, c: x['Programa'] == 'Biología') + 1
    nota(ws, r, '⚠ BIOLOGÍA ES UNA POBLACIÓN DISTINTA: 64,7 % de mujeres (vs 15,8 % y 7,4 %), Saber 11 unos 10 puntos por debajo, promedio de carrera 2,702 (vs 3,083 y 3,036). Sistemas y Electrónica sí son comparables entre sí.', 7, fill_bad); r += 1
    nota(ws, r, '⚠ La tasa de graduación de Biología (7,1 %) está SESGADA POR CENSURA: 15 estudiantes (18 %) siguen matriculados y su desenlace no se conoce. Sistemas y Electrónica tienen cero. La desventaja real existe, pero esa cifra no debe reportarse sin la advertencia.', 7, fill_bad); r += 2

    ws.cell(r, 1, 'D · Viabilidad de cortes longitudinales con la muestra FCBI completa').font = sub; r += 1
    via = pd.read_csv(os.path.join(SRC, 'fcbi_viabilidad_cortes.csv'))
    r = tabla(ws, via, r, anchos=[18, 13, 18, 28],
              resalta=lambda x, c: str(x['Modelable (n>=60 y ev>=15)']) == 'Sí') + 1
    nota(ws, r, 'DESBLOQUEO: con Sistemas solo, NINGÚN corte era modelable (11, 9, 9, 5, 3 eventos). Con la FCBI completa, los cortes 1, 2 y 3 superan el filtro de RC-008 (33, 19 y 16 eventos). La ampliación de la muestra era el prerrequisito del diseño longitudinal, no una alternativa a él.', 7, fill_ok)


# ═══ 9, 10, 11 · ENCARGO DEL ASESOR (2026-09-29) ═══
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hojas_asesor import agregar as _agregar_hojas_asesor
_agregar_hojas_asesor(wb, SRC, {'titulo': titulo, 'tabla': tabla, 'nota': nota,
                                'sub': sub, 'ok': fill_ok, 'bad': fill_bad,
                                'warn': fill_warn})

for s in wb.worksheets:
    s.sheet_view.showGridLines = False
    s.freeze_panes = 'A3'
wb.save(OUT)
print('OK:', OUT)
