import argparse,json
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.metrics import log_loss
import mlflow, mlflow.sklearn
from src.common import ROOT, FEATURES, NUMERIC, CATEGORICAL, NAME, tracking

# Bonferroni alpha over numeric features plus practical KS distance.
ALPHA=.05/len(NUMERIC)
KS_MIN=.1
TV_MIN=.15
LOSS_DELTA=.10

def check(reference,current,model):
    stats={}
    for c in NUMERIC:
        s=ks_2samp(reference[c].dropna(),current[c].dropna())
        stats[c]={'ks':float(s.statistic),'p':float(s.pvalue),'drift':bool(s.pvalue<ALPHA and s.statistic>KS_MIN)}
    for c in CATEGORICAL:
        a=reference[c].value_counts(normalize=True);b=current[c].value_counts(normalize=True)
        levels=a.index.union(b.index)
        tv=float(abs(a.reindex(levels,fill_value=0)-b.reindex(levels,fill_value=0)).sum()/2)
        stats[c]={'tv':tv,'drift':tv>TV_MIN}
    baseline=log_loss(reference.Churn,model.predict_proba(reference[FEATURES])[:,1],labels=[0,1])
    loss=log_loss(current.Churn,model.predict_proba(current[FEATURES])[:,1],labels=[0,1])
    return {'data_drift':any(s['drift'] for s in stats.values()),'concept_drift':bool(loss-baseline>LOSS_DELTA), 'reference_log_loss':float(baseline),'current_log_loss':float(loss),'loss_delta':float(loss-baseline),'features':stats,'thresholds':{'ks_alpha':ALPHA,'ks_min':KS_MIN,'tv_min':TV_MIN,'loss_delta':LOSS_DELTA}}

def scenario(current,name):
    d=current.copy()
    if name=='data': d['MonthlyCharges']=d.MonthlyCharges+100
    if name=='concept': d['Churn']=1-d.Churn
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument('scenario',choices=['normal','data','concept']);a=p.parse_args()
    mlflow.set_tracking_uri(tracking());model=mlflow.sklearn.load_model(f'models:/{NAME}@production')
    ref=pd.read_csv(ROOT/'evidence/reference.csv');cur=scenario(pd.read_csv(ROOT/'evidence/current.csv'),a.scenario)
    result=check(ref,cur,model)
    (ROOT/f'evidence/drift-{a.scenario}.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    raise SystemExit(2 if result['data_drift'] or result['concept_drift'] else 0)
if __name__=='__main__': main()
