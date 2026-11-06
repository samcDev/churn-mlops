"""Data drift against training inputs; labeled performance uses held-out validation."""
import argparse,json
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency
from sklearn.metrics import log_loss
import mlflow, mlflow.sklearn
from src.common import ROOT, FEATURES, NUMERIC, CATEGORICAL, NAME, tracking

# Family-wise alpha .05 across six feature comparisons (Bonferroni).
ALPHA=.05/len(FEATURES)
KS_MIN=.1
TV_MIN=.15
LOSS_DELTA=.10

def check(reference,current,model,performance_reference=None):
    stats={}
    for c in NUMERIC:
        s=ks_2samp(reference[c].dropna(),current[c].dropna())
        stats[c]={'test':'KS','ks':float(s.statistic),'p':float(s.pvalue),'drift':bool(s.pvalue<ALPHA and s.statistic>KS_MIN)}
    for c in CATEGORICAL:
        a=reference[c].value_counts();b=current[c].value_counts()
        levels=a.index.union(b.index)
        table=[a.reindex(levels,fill_value=0).to_numpy(),b.reindex(levels,fill_value=0).to_numpy()]
        if len(levels)>1:
            chi,pvalue,_,expected=chi2_contingency(table,correction=False)
            valid=bool((expected>=5).all())
            if not valid: raise ValueError(f'{c}: sparse expected counts; aggregate categories or use permutation test')
        else: chi,pvalue,valid=0.,1.,True
        tv=float(abs(a.reindex(levels,fill_value=0)/a.sum()-b.reindex(levels,fill_value=0)/b.sum()).sum()/2)
        stats[c]={'test':'chi-square homogeneity','chi2':float(chi),'p':float(pvalue),'expected_counts_valid':valid,'tv':tv,'drift':bool(pvalue<ALPHA and tv>TV_MIN)}
    perf=reference if performance_reference is None else performance_reference
    baseline=log_loss(perf.Churn,model.predict_proba(perf[FEATURES])[:,1],labels=[0,1])
    loss=log_loss(current.Churn,model.predict_proba(current[FEATURES])[:,1],labels=[0,1])
    return {'data_drift':any(s['drift'] for s in stats.values()),'concept_drift':bool(loss-baseline>LOSS_DELTA),'concept_signal_scope':'single-batch auxiliary log-loss signal; temporal ROC AUC rule is authoritative for retraining','reference_rows':len(reference),'performance_reference_rows':len(perf),'reference_log_loss':float(baseline),'current_log_loss':float(loss),'loss_delta':float(loss-baseline),'features':stats,'thresholds':{'feature_alpha':ALPHA,'ks_min':KS_MIN,'tv_min':TV_MIN,'auxiliary_loss_delta':LOSS_DELTA}}

def scenario(current,name):
    d=current.copy()
    if name=='data': d['MonthlyCharges']=d.MonthlyCharges+100
    if name=='concept': d['Churn']=1-d.Churn
    return d

def main():
    p=argparse.ArgumentParser();p.add_argument('scenario',choices=['normal','data','concept']);a=p.parse_args()
    mlflow.set_tracking_uri(tracking());model=mlflow.sklearn.load_model(f'models:/{NAME}@production')
    ref=pd.read_csv(ROOT/'evidence/reference.csv');perf=pd.read_csv(ROOT/'evidence/performance-reference.csv')
    cur=scenario(pd.read_csv(ROOT/'evidence/current.csv'),a.scenario)
    result=check(ref,cur,model,perf)
    (ROOT/f'evidence/drift-{a.scenario}.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    raise SystemExit(2 if result['data_drift'] or result['concept_drift'] else 0)
if __name__=='__main__': main()
