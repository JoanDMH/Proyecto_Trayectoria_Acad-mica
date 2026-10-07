exec(open('figuras.py').read().split('# ── 1 · Duración')[0])
# f05 · sobreestimación del resultado
s = pd.DataFrame({'fuente': ['Variables elegidas con toda la muestra',
                             'Hiperparámetros elegidos con datos de evaluación · XGBoost',
                             'Hiperparámetros elegidos con datos de evaluación · Árbol',
                             'Hiperparámetros elegidos con datos de evaluación · Random Forest'],
                  'sesgo': [0.150, 0.046, 0.011, 0.008]})
s['fuente'] = pd.Categorical(s.fuente, categories=s.fuente[::-1])
s['lab'] = ['+' + coma(v, 3) for v in s.sesgo]
p = (ggplot(s, aes('fuente', 'sesgo')) + geom_col(fill='#c0392b', width=.6) +
     geom_hline(yintercept=.03, linetype='dashed', color='#333333', size=.9) +
     annotate('text', x=4.42, y=.033, label='umbral de relevancia 0,03', ha='left', size=BASE - 2, family=FONT) +
     geom_text(aes(label='lab'), ha='left', nudge_y=.003, size=BASE, family=FONT, fontweight='bold') + coord_flip() +
     scale_y_continuous(limits=(0, .18), labels=lab_coma(2)) +
     labs(x='', y='Sobreestimación del AUC-PR (con el error − sin el error)') + TEMA)
guardar(p, 'f05_sesgos_v5.png', 11.4, 3.7)

# f12 · matrices normalizadas por fila
k = pd.read_csv(D + 'oof_art19_calibracion.csv')
y, pr0 = k.y.values, k['sin calibrar'].values
cm = []
for nivel, u in [('Confirmado · umbral 0,63', .63), ('Seguimiento · umbral 0,13', .13)]:
    yp = (pr0 >= u).astype(int)
    for real in (1, 0):
        tot = int((y == real).sum())
        for pred in (1, 0):
            n = int(((y == real) & (yp == pred)).sum())
            cm.append({'nivel': nivel, 'Real': f'Con bajo rendimiento\n({tot} estudiantes)' if real else f'Sin bajo rendimiento\n({tot} estudiantes)',
                       'Predicho': 'Alerta' if pred else 'Sin alerta', 'n': n, 'pct': 100 * n / tot,
                       'ok': 'acierto' if real == pred else 'error'})
cm = pd.DataFrame(cm)
cm['Real'] = pd.Categorical(cm.Real, categories=sorted(cm.Real.unique(), key=lambda r: r.startswith('Con')))
cm['Predicho'] = pd.Categorical(cm.Predicho, categories=['Alerta', 'Sin alerta'])
cm['lab_p'] = [coma(v, 1) + ' %' for v in cm.pct]
cm['lab_n'] = ['(' + str(v) + ')' for v in cm.n]
print(cm[['nivel', 'Real', 'Predicho', 'n', 'lab_p']])
p = (ggplot(cm, aes('Predicho', 'Real', fill='ok')) + geom_tile(color='white', size=2) +
     geom_text(aes(label='lab_p'), nudge_y=.1, size=BASE + 9, family=FONT, fontweight='bold', color='#222222') +
     geom_text(aes(label='lab_n'), nudge_y=-.2, size=BASE + 1, family=FONT, color='#444444') +
     scale_fill_manual(values={'acierto': '#cfe0f5', 'error': '#f6d3cf'}, guide=None) + facet_wrap('~nivel') +
     labs(x='Predicción del modelo   ·   porcentaje sobre cada fila (número de estudiantes)', y='Realidad') +
     TEMA + theme(panel_grid=element_blank()))
guardar(p, 'f12_confusion_v5.png', 11.4, 4.7)
