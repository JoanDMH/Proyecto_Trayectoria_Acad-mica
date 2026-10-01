"""
experimento_ancho_target.py — RC-039 · ¿Falta de datos o mal planteamiento?

Experimento controlado para diagnosticar por qué el diseño longitudinal no predice
(RC-038). Mantiene TODO constante —diseño por cortes, variables, algoritmo y
protocolo— y varía únicamente el UMBRAL que define el evento.

Se compara con AUC-ROC, no con AUC-PR: al cambiar el umbral cambia la prevalencia,
y el AUC-PR no es comparable entre prevalencias distintas. El AUC-ROC sí lo es.

Resultado: el AUC-ROC sube de forma monótona al ampliar el target
(0,496 -> 0,603 -> 0,647 en el corte 1), lo que demuestra que el problema es la
DEFINICIÓN del evento, no la cantidad de datos.

Requiere: src/longitudinal_panel.csv y src/df_master_fcbi.csv
Uso:  python src/experimento_ancho_target.py
"""
import warnings,sys; warnings.filterwarnings('ignore'); sys.path.insert(0,'src')
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import average_precision_score, roc_auc_score
SEED=42; NREP=5
per=pd.read_csv('src/longitudinal_panel.csv')
base=pd.read_csv('src/df_master_fcbi.csv'); base['CODIGO_INST']=base.CODIGO_INST.astype(str)
ING=['icfes_total','icfes_mat','icfes_lec','icfes_nat','estrato','log_ingresos','sisben_nivel',
     'repitio_escolar','sexo','tipo_plantel','zona_rural','nivel_edu_max_padres','cohorte_encoded']
ACU=['prom_ponderado_acum','pct_creditos_reprob_acum','pct_creditos_reprob_ultimo',
     'n_art20_acum','max_veces_cursado','creditos_acum','n_asignaturas_acum']
def rf(): return RandomForestClassifier(n_estimators=120,max_depth=4,random_state=SEED,n_jobs=-1)
def ev(X,y):
    ap,au=[],[]
    for r in range(NREP):
        cv=StratifiedKFold(5,shuffle=True,random_state=SEED+r); p=np.zeros(len(y))
        for tr,te in cv.split(X,y): p[te]=rf().fit(X[tr],y[tr]).predict_proba(X[te])[:,1]
        ap.append(average_precision_score(y,p)); au.append(roc_auc_score(y,p))
    return np.mean(ap),np.std(ap),np.mean(au)
def corte(k,umbral,col):
    per['ev']= (per[col]>=umbral)&(per.regular==True)
    hasta=per[per.k<=k]; ya=set(hasta[hasta.ev].CODIGO_INST.astype(str))
    fut=set(per[(per.k>k)&(per.ev)].CODIGO_INST.astype(str))
    s=per[per.k==k].copy(); s['cod']=s.CODIGO_INST.astype(str)
    s=s[~s.cod.isin(ya)]; s['y']=s.cod.isin(fut).astype(int)
    d=s[['cod','y']+ACU].merge(base,left_on='cod',right_on='CODIGO_INST',how='inner')
    return d.dropna(subset=ING+ACU+['y'])
print('=== ¿Es el target o es la falta de datos? ===')
print('Mismo diseño longitudinal, distinto ANCHO del target.\n')
print(f"{'Target':38s} {'corte':>5s} {'n':>5s} {'ev':>4s} {'base':>7s} {'AUC-PR':>8s} {'lift':>6s} {'ROC':>6s}")
for nom,umb in [('art.19 estricto (100% creditos)',1.0),
                ('>=75% de creditos reprobados',0.75),
                ('>50% (art.20, mas amplio)',0.51)]:
    for k in (1,2):
        d=corte(k,umb,'pct_creditos_reprob_ultimo'); y=d.y.values.astype(int)
        if y.sum()<10: print(f'{nom:38s} {k:>5d} {len(y):>5d} {y.sum():>4d}   (pocos eventos)'); continue
        a,s,u=ev(d[ING+ACU].values,y)
        print(f'{nom:38s} {k:>5d} {len(y):>5d} {y.sum():>4d} {y.mean():>7.3f} {a:>8.4f} {a/y.mean():>5.2f}x {u:>6.3f}')
