# -*- coding: utf-8 -*-
"""
Hojas 9, 10 y 11 del consolidado — encargo del asesor del 2026-09-29.

Se importa desde _build_consolidado.py y recibe su libro y sus estilos, para que
el formato no se bifurque. Lee los JSON que dejan los tres scripts del bloque:
    src/_resultados_pca.json
    src/_resultados_bayes.json
    src/_resultados_pocos.json
"""
import json, os
import pandas as pd


def agregar(wb, SRC, ayudas):
    titulo, tabla, nota, sub = (ayudas['titulo'], ayudas['tabla'],
                                ayudas['nota'], ayudas['sub'])
    fill_ok, fill_bad, fill_warn = ayudas['ok'], ayudas['bad'], ayudas['warn']

    def cargar(nombre):
        p = os.path.join(SRC, nombre)
        return json.load(open(p, encoding='utf8')) if os.path.exists(p) else None

    pca = cargar('_resultados_pca.json')
    bay = cargar('_resultados_bayes.json')
    poc = cargar('_resultados_pocos.json')

    FMT_AP = {'AUC-PR': '0.0000', 'DE': '0.0000', 'AUC-ROC': '0.0000',
              'Δ vs referencia': '+0.0000;-0.0000', 't corregido': '0.000',
              'p': '0.0000'}

    # ═══════════════════════════════════ 9 · PCA ═══════════════════════════════
    if pca:
        ws = wb.create_sheet('9 · PCA y selección')
        titulo(ws, 'BLOQUE A — PCA COMO RESPALDO DE LA SELECCIÓN DE VARIABLES', 8)
        ws['A2'] = ('Encargo del asesor, 2026-09-29 · protocolo idéntico a I-3 bis '
                    '(CV-5 anidada, 10 repeticiones, n=80, 19 positivos)')
        r = 4

        ws.cell(r, 1, 'LO PRIMERO: QUÉ PUEDE Y QUÉ NO PUEDE DEMOSTRAR EL PCA').font = sub
        r += 1
        nota(ws, r, 'El PCA es NO SUPERVISADO: busca direcciones de máxima varianza en las '
                    'variables, sin mirar nunca el resultado que se quiere predecir. Por '
                    'construcción NO puede demostrar que un conjunto de variables sea el mejor '
                    'para predecir. Sirve para (a) medir redundancia y (b) generar una '
                    'representación alternativa que SÍ se puede comparar en capacidad '
                    'predictiva. Eso último es lo que se hace en la sección C.', 8, fill_warn)
        r += 2

        d = pca.get('descriptivo')
        if d:
            ws.cell(r, 1, 'A · Estructura de varianza de las 19 variables').font = sub
            r += 1
            r = tabla(ws, pd.DataFrame(d['varianza']), r,
                      anchos=[14, 12, 13, 14, 20],
                      fmt={'Autovalor': '0.000', '% varianza': '0.00',
                           '% acumulado': '0.00'}) + 1
            nota(ws, r, f'Hacen falta {d["n90"]} de 19 componentes para explicar el 90 % de la '
                        f'varianza ({d["n80"]} para el 80 %, {d["n95"]} para el 95 %). Las 19 '
                        f'variables NO son fuertemente redundantes: ocupan muchas dimensiones '
                        f'reales. Pero esa varianza es en su mayor parte NO informativa sobre el '
                        f'riesgo académico, como demuestra la sección C.', 8)
            r += 2

            ws.cell(r, 1, 'B · Cargas de los cinco primeros componentes').font = sub
            r += 1
            r = tabla(ws, pd.DataFrame(d['cargas']), r,
                      anchos=[30, 9, 10, 10, 10, 10, 10],
                      resalta=lambda x, c: x['En S3'] == 'sí') + 1
            nota(ws, r, f'⚠ HALLAZGO CENTRAL. La variable más predictiva de todo el estudio '
                        f'—el promedio del primer semestre— alcanza su carga máxima en el '
                        f'componente CP{d["cp_prom_sem1"]}, que explica solo el '
                        f'{d["var_cp_prom_sem1"]} % de la varianza. Quien hubiera seleccionado '
                        f'variables por varianza explicada la habría descartado. Es la '
                        f'demostración empírica de por qué el PCA no vale como criterio de '
                        f'selección en un problema supervisado.', 8, fill_bad)
            r += 2

            ws.cell(r, 1, 'B2 · Redundancia interna del conjunto S3').font = sub
            r += 1
            s3 = pd.DataFrame({'Componentes': [f'CP1..CP{i+1}' for i in range(len(d['s3_cum']))],
                               '% acumulado': d['s3_cum']})
            r = tabla(ws, s3, r, anchos=[16, 14], fmt={'% acumulado': '0.00'}) + 1
            nota(ws, r, f'S3 necesita {d["s3_n90"]} de sus 6 componentes para el 90 %: no hay '
                        f'redundancia estructural apreciable que comprimir. (Ojo: el análisis '
                        f'bayesiano de la hoja 10 sí encuentra una colinealidad que el PCA no '
                        f'delata, porque el PCA mira varianza y no efecto.)', 8)
            r += 2

        pr = pca.get('predictivo')
        if pr:
            ws.cell(r, 1, 'C · PRUEBA DECISIVA — ¿alguna representación supera a las 6 variables?').font = sub
            r += 1
            ws.cell(r, 1, f'Referencia: {pr["base"]["nombre"]} — AUC-PR '
                          f'{pr["base"]["ap"]:.4f} ± {pr["base"]["de"]:.4f} '
                          f'(azar = {pr["prevalencia"]:.4f})')
            r += 1
            r = tabla(ws, pd.DataFrame(pr['tabla']), r,
                      anchos=[46, 11, 10, 11, 17, 13, 10, 22], fmt=FMT_AP,
                      resalta=lambda x, c: 'empate' in str(x['Veredicto'])) + 1
            nota(ws, r, 'VEREDICTO: ninguna representación mejora a las 6 variables '
                        'seleccionadas. El PCA no solo no ayuda: DESTRUYE la señal '
                        '(−0,37 de AUC-PR, p<0,0001) porque la rotación diluye la única '
                        'variable muy predictiva dentro de componentes dominados por varianza '
                        'irrelevante. El PLS, que sí es supervisado, tampoco alcanza: elige '
                        'k=1 componente en las 50 iteraciones, confirmando que hay una sola '
                        'dirección útil, pero al ser lineal no captura su forma.', 8, fill_bad)
            r += 2
            nota(ws, r, 'RESPALDO A LA SELECCIÓN: usar las 19 variables crudas empata '
                        'estadísticamente con usar 6 (p=0,42), y toda compresión no supervisada '
                        'empeora. La selección S3 queda sustentada por tres vías '
                        'independientes: ablación anidada (RC-032), esta comparación de '
                        'representaciones, y la posterior bayesiana de la hoja 10.', 8, fill_ok)
            r += 2

            if pr.get('k_elegidos'):
                ws.cell(r, 1, 'D · Componentes elegidos dentro de los pliegues').font = sub
                r += 1
                fil = [{'Configuración': k, 'Frecuencia (sobre 50 pliegues)':
                        ' · '.join(f'k={a}: {b}' for a, b in v.items())}
                       for k, v in pr['k_elegidos'].items()]
                r = tabla(ws, pd.DataFrame(fil), r, anchos=[46, 52]) + 1

    # ══════════════════════════════ 10 · BAYESIANOS ════════════════════════════
    if bay:
        ws = wb.create_sheet('10 · Modelos bayesianos')
        titulo(ws, 'BLOQUE B — MODELOS BAYESIANOS', 8)
        ws['A2'] = ('Encargo del asesor, 2026-09-29 · mismo protocolo anidado · '
                    'la aportación no es acierto, es incertidumbre cuantificada')
        r = 4

        cmp_ = bay.get('comparativa')
        if cmp_:
            ws.cell(r, 1, 'A · Desempeño frente a la referencia').font = sub
            r += 1
            ws.cell(r, 1, f'Referencia: {cmp_["base"]["nombre"]} — AUC-PR '
                          f'{cmp_["base"]["ap"]:.4f} (azar = {cmp_["prevalencia"]:.4f})')
            r += 1
            r = tabla(ws, pd.DataFrame(cmp_['tabla']), r,
                      anchos=[50, 11, 10, 11, 17, 13, 10, 22], fmt=FMT_AP,
                      resalta=lambda x, c: 'empate' in str(x['Veredicto'])) + 1
            nota(ws, r, 'Ningún modelo bayesiano supera a Random Forest en AUC-PR, y era '
                        'esperable: son modelos de frontera lineal (salvo el proceso '
                        'gaussiano) frente a un problema con interacciones. El dato que sí '
                        'importa: la logística bayesiana (0,619) supera a su propio MAP '
                        'regularizado (0,605) con idénticas variables. Esa diferencia es lo '
                        'que aporta integrar sobre la posterior en vez de quedarse con la '
                        'moda — poco en acierto, mucho en honestidad.', 8)
            r += 2

        po = bay.get('posterior')
        if po:
            ws.cell(r, 1, 'B · Posterior de los coeficientes (PyMC, muestra completa n=80)').font = sub
            r += 1
            nota(ws, r, 'Coeficientes sobre variables tipificadas, por tanto comparables entre '
                        'sí. Un intervalo creíble del 94 % que NO contiene el cero indica un '
                        'efecto que los datos sostienen. Es una respuesta a la selección de '
                        'variables independiente del PCA y del bosque aleatorio.', 8)
            r += 1
            r = tabla(ws, pd.DataFrame(po['coeficientes']), r,
                      anchos=[30, 17, 18, 18, 11, 26],
                      fmt={'Media posterior': '+0.000;-0.000',
                           'IC 94 % inferior': '+0.000;-0.000',
                           'IC 94 % superior': '+0.000;-0.000', 'P(β<0)': '0.000'},
                      resalta=lambda x, c: x['Veredicto'] == 'efecto creíble') + 1
            nota(ws, r, '⚠ HALLAZGO NO BUSCADO. El coeficiente de SABER 11 · total sale '
                        'POSITIVO y creíble (+1,56): más puntaje, más riesgo. Es imposible '
                        'sustantivamente, y es el síntoma clásico de colinealidad por '
                        'supresión — el total es en un 85 % una combinación lineal de sus '
                        'tres áreas (VIF 6,7). El modelo está ajustando contrastes entre el '
                        'total y sus partes, no efectos interpretables. Ver sección C.',
             8, fill_bad)
            r += 2

            ws.cell(r, 1, 'C · Colinealidad dentro de S3 y consecuencia práctica').font = sub
            r += 1
            vif = pd.DataFrame([
                ['Promedio 1er semestre', 1.10, 0.0901, 'sin problema'],
                ['Sin primer semestre', 1.01, 0.0112, 'sin problema'],
                ['SABER 11 · total', 6.66, 0.8500, 'colinealidad problemática (>5)'],
                ['SABER 11 · matemáticas', 2.04, 0.5104, 'sin problema'],
                ['SABER 11 · lectura', 2.39, 0.5825, 'sin problema'],
                ['SABER 11 · naturales', 2.71, 0.6315, 'sin problema'],
            ], columns=['Variable', 'VIF', 'R² contra las demás', 'Lectura'])
            r = tabla(ws, vif, r, anchos=[30, 10, 20, 34],
                      fmt={'VIF': '0.00', 'R² contra las demás': '0.0000'},
                      resalta=lambda x, c: x['VIF'] > 5) + 1
            nota(ws, r, 'QUÉ HACER: a Random Forest la colinealidad no le afecta (quitar el '
                        'total deja AUC-PR 0,721 frente a 0,742, empate estadístico p=0,13), '
                        'así que el modelo en producción no está comprometido. Pero cualquier '
                        'lectura de coeficientes o de importancias individuales dentro del '
                        'bloque SABER 11 es inválida mientras el total conviva con sus partes. '
                        'Recomendación: conservar el total y retirar las tres áreas, o al '
                        'revés, antes de interpretar nada.', 8, fill_warn)
            r += 2

            inc = po['incertidumbre']
            ws.cell(r, 1, 'D · Incertidumbre por estudiante — la razón para cambiar la app').font = sub
            r += 1
            tb = pd.DataFrame([
                ['Anchura mediana del IC 94 %', inc['mediana']],
                ['Anchura mínima', inc['min']],
                ['Anchura máxima', inc['max']],
                ['Estudiantes con IC más ancho que 0,30', inc['n_ancho_mayor_030']],
                ['Porcentaje sobre los 80', inc['pct_ancho_mayor_030']],
            ], columns=['Medida', 'Valor'])
            r = tabla(ws, tb, r, anchos=[42, 14]) + 1
            nota(ws, r, f'En {inc["n_ancho_mayor_030"]} de 80 estudiantes '
                        f'({inc["pct_ancho_mayor_030"]:.0%}) el intervalo creíble del 94 % de su '
                        f'probabilidad es más ancho que 0,30. Para esos casos el modelo no está '
                        f'en condiciones de emitir un número. Esto confirma por una vía '
                        f'independiente el defecto de calibración detectado el 16-09 y sostiene '
                        f'la recomendación: la app debe mostrar nivel de alerta y puesto '
                        f'relativo, no un porcentaje.', 8, fill_bad)

    # ═════════════════════════ 11 · POCOS DATOS / TAMAÑO ═══════════════════════
    if poc:
        ws = wb.create_sheet('11 · Pocos datos y tamaño')
        titulo(ws, 'BLOQUE C — APRENDIZAJE CON POCOS DATOS Y CURVA DE TAMAÑO MUESTRAL', 8)
        ws['A2'] = ('Encargo del asesor, 2026-09-29 · incluye la estimación de qué aportarán '
                    'las cohortes nuevas solicitadas')
        r = 4

        ws.cell(r, 1, 'SOBRE "ONE-SHOT LEARNING": QUÉ SE TRASLADA Y QUÉ NO').font = sub
        r += 1
        nota(ws, r, 'El one-shot / few-shot learning en sentido estricto sirve para reconocer '
                    'CLASES NUEVAS con uno o pocos ejemplos, y descansa en dos cosas que aquí '
                    'no existen: un corpus grande de preentrenamiento del que transferir una '
                    'representación, y una estructura por episodios con clases no vistas en '
                    'entrenamiento. Nuestro problema es tabular, binario y con ambas clases '
                    'presentes desde el inicio. Aplicar una red siamesa literal sería ponerle '
                    'nombre de moda a un clasificador corriente. Lo que SÍ se traslada es el '
                    'mecanismo: aprender una métrica y clasificar por cercanía a un prototipo '
                    'de clase — ProtoNet, despojada de la red, es exactamente eso.', 8, fill_warn)
        r += 2

        cmp_ = poc.get('comparativa')
        if cmp_:
            ws.cell(r, 1, 'A · Métodos basados en métrica y prototipos').font = sub
            r += 1
            ws.cell(r, 1, f'Referencia: {cmp_["base"]["nombre"]} — AUC-PR '
                          f'{cmp_["base"]["ap"]:.4f} (azar = {cmp_["prevalencia"]:.4f})')
            r += 1
            r = tabla(ws, pd.DataFrame(cmp_['tabla']), r,
                      anchos=[46, 11, 10, 11, 17, 13, 10, 22], fmt=FMT_AP) + 1
            nota(ws, r, 'Ninguno alcanza a Random Forest. Y un detalle instructivo: aprender la '
                        'métrica con NCA EMPEORA los prototipos (0,356 frente a 0,437) y apenas '
                        'mejora los vecinos. Con 19 positivos, NCA sobreajusta la métrica; es '
                        'justo el régimen en el que los métodos de few-shot dependen de un '
                        'preentrenamiento externo que aquí no tenemos. El resultado no dice '
                        'que la familia sea mala: dice que sin corpus del que transferir, no '
                        'hay atajo.', 8)
            r += 2

        cv = poc.get('curva')
        if cv:
            ws.cell(r, 1, 'B · CURVA DE TAMAÑO MUESTRAL — qué compra pedir más datos').font = sub
            r += 1
            nota(ws, r, 'Se submuestrea SOLO el pliegue de entrenamiento; el de prueba queda '
                        'intacto, de modo que la curva mide el efecto del tamaño y no el de '
                        'cambiar la evaluación. Hiperparámetros fijos para aislar la variable.', 8)
            r += 1
            r = tabla(ws, pd.DataFrame(cv['puntos']), r,
                      anchos=[24, 24, 19, 11, 10, 11],
                      fmt={'AUC-PR': '0.0000', 'DE': '0.0000', 'AUC-ROC': '0.0000',
                           'n entrenamiento (medio)': '0.0', 'positivos (medio)': '0.0'}) + 1

            aj = cv.get('ajuste', {})
            if 'extrapolacion' in aj:
                ws.cell(r, 1, 'C · Extrapolación por ley de potencias').font = sub
                r += 1
                base_ap = aj['extrapolacion'].get('80', 0)
                ext = pd.DataFrame([
                    {'n total estimado': int(k),
                     'AUC-PR proyectado': v,
                     'Ganancia sobre hoy': round(v - base_ap, 4),
                     'Comentario': ('situación actual' if k == '80' else
                                    'duplicar la muestra' if k == '160' else
                                    'triplicar' if k == '240' else
                                    'cuadruplicar' if k == '320' else 'quintuplicar')}
                    for k, v in aj['extrapolacion'].items()])
                r = tabla(ws, ext, r, anchos=[20, 20, 20, 28],
                          fmt={'AUC-PR proyectado': '0.000',
                               'Ganancia sobre hoy': '+0.000;-0.000'},
                          resalta=lambda x, c: x['n total estimado'] == 160) + 1
                nota(ws, r, f'Ajuste AUC-PR(n) = {aj["c_techo"]:.3f} − {aj["a"]:.3f}·n^(−'
                            f'{aj["b"]:.3f}) con R² = {aj["R2"]:.3f}. Techo asintótico estimado: '
                            f'{aj["c_techo"]:.3f}.', 8)
                r += 1
                nota(ws, r, 'LECTURA PARA LA PETICIÓN DE DATOS: duplicar la muestra (una cohorte '
                            'más) compra en torno a +0,05 de AUC-PR; cuadruplicarla, unos +0,07. '
                            'La curva satura pronto porque el techo lo impone la INFORMACIÓN '
                            'DISPONIBLE, no el número de filas. Conclusión honesta: las cohortes '
                            'nuevas son muy valiosas —sobre todo porque permiten la validación '
                            'externa que hoy no existe— pero si además se pudiera incorporar '
                            'asistencia (art. 58), fechas de pago y créditos cancelados, el '
                            'techo mismo subiría. Más filas mejoran la estimación; más '
                            'variables mueven el límite.', 8, fill_ok)
                r += 2
                nota(ws, r, '⚠ CAUTELA: extrapolar desde 64 casos de entrenamiento hasta 320 es '
                            'una proyección de orden de magnitud, no una predicción. Supone que '
                            'las cohortes nuevas se parecen a las actuales y que la prevalencia '
                            'del evento se mantiene. Si el reglamento cambió de régimen entre '
                            'cohortes, ese supuesto se rompe.', 8, fill_warn)
