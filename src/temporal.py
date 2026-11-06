"""Controlled temporal demonstration; batch index is simulated time, not real dates."""
import argparse,json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
import mlflow,mlflow.sklearn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mlflow import MlflowClient
from src.common import ROOT,FEATURES,NAME,tracking

AUC_DROP=.10
CONSECUTIVE=3

def alarm_steps(scores,baseline,drop=AUC_DROP,consecutive=CONSECUTIVE):
    """None means delayed/unavailable labels: pause streak; never manufacture labels."""
    streak=0
    result=[]
    for score in scores:
        if score is None:
            result.append({'breach':None,'streak':streak,'alarm':False,'status':'waiting_for_labels'})
            continue
        breach=bool(baseline-score>=drop)
        streak=streak+1 if breach else 0
        result.append({'breach':breach,'streak':streak,'alarm':streak>=consecutive,'status':'evaluated'})
    return result

def evaluate(model,performance_reference,current,mode):
    baseline=float(roc_auc_score(performance_reference.Churn,model.predict_proba(performance_reference[FEATURES])[:,1]))
    batches=[]
    folds=StratifiedKFold(n_splits=10,shuffle=True,random_state=42)
    for i,(_,idx) in enumerate(folds.split(current[FEATURES],current.Churn),1):
        batch=current.iloc[idx].copy()
        altered=mode=='concept' and i>=5
        if altered: batch['Churn']=1-batch.Churn
        score=float(roc_auc_score(batch.Churn,model.predict_proba(batch[FEATURES])[:,1]))
        batches.append({'batch':i,'rows':len(batch),'labels_available':True,'inverted_labels':altered,'roc_auc':score})
    states=alarm_steps([b['roc_auc'] for b in batches],baseline)
    for b,state in zip(batches,states): b.update(state)
    return {'mode':mode,'baseline_roc_auc':baseline,'metric':'roc_auc','drop_threshold':AUC_DROP,'consecutive_labeled_batches':CONSECUTIVE,'simulated_time':True,'disjoint_batches':True,'alarm':any(b['alarm'] for b in batches),'first_alarm_batch':next((b['batch'] for b in batches if b['alarm']),None),'batches':batches}

def plot(result,destination):
    fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained')
    x=[b['batch'] for b in result['batches']];y=[b['roc_auc'] for b in result['batches']]
    ax.plot(x,y,'o-',color='#167d9a',label='ROC AUC por lote')
    ax.axhline(result['baseline_roc_auc'],color='#626e79',linestyle='--',label='Referencia: validación')
    ax.axhline(result['baseline_roc_auc']-AUC_DROP,color='#bd3c3c',linestyle=':',label='Umbral: referencia - 0,10')
    if result['mode']=='concept': ax.axvspan(4.5,10.5,color='#f4c56b',alpha=.2,label='Etiquetas invertidas')
    if result['first_alarm_batch']: ax.axvline(result['first_alarm_batch'],color='#bd3c3c',label='Alarma: 3 lotes consecutivos')
    ax.set(xlabel='Lote sucesivo (tiempo simulado)',ylabel='ROC AUC',ylim=(0,1),xticks=x,title='Concept drift: '+result['mode'])
    ax.grid(alpha=.15);ax.legend(loc='lower left',fontsize=8)
    fig.savefig(destination,dpi=180);plt.close(fig)

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['normal','concept']);args=p.parse_args()
    mlflow.set_tracking_uri(tracking());v=MlflowClient().get_model_version_by_alias(NAME,'production')
    model=mlflow.sklearn.load_model(f'models:/{NAME}/{v.version}')
    ref=pd.read_csv(ROOT/'evidence/performance-reference.csv');cur=pd.read_csv(ROOT/'evidence/current.csv')
    result=evaluate(model,ref,cur,args.mode);result.update({'version':v.version,'run_id':v.run_id})
    dest=ROOT/f'evidence/temporal-{args.mode}'
    dest.with_suffix('.json').write_text(json.dumps(result,indent=2))
    pd.DataFrame(result['batches']).to_csv(dest.with_suffix('.csv'),index=False)
    plot(result,dest.with_suffix('.png'))
    print(json.dumps(result,indent=2));raise SystemExit(2 if result['alarm'] else 0)
if __name__=='__main__': main()
