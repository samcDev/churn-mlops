import hashlib, json, subprocess
import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, accuracy_score
from src.common import ROOT, NUMERIC, CATEGORICAL, NAME, data, tracking

def main():
    mlflow.set_tracking_uri(tracking())
    mlflow.set_experiment('telco-churn-individual')
    X,y=data()
    Xdev,Xtest,ydev,ytest=train_test_split(X,y,test_size=.2,stratify=y,random_state=42)
    Xtr,Xval,ytr,yval=train_test_split(Xdev,ydev,test_size=.25,stratify=ydev,random_state=42)
    digest=hashlib.sha256((ROOT/'data/telco.csv').read_bytes()).hexdigest()
    try: commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    except subprocess.CalledProcessError: commit='uncommitted'
    rows=[]
    client=MlflowClient()
    for c in [.01,.1,1.,10.,100.]:
        pre=ColumnTransformer([
            ('numeric',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),NUMERIC),
            ('category',OneHotEncoder(handle_unknown='ignore'),CATEGORICAL)])
        model=Pipeline([('preprocess',pre),('classifier',LogisticRegression(C=c,max_iter=2000,random_state=42))])
        with mlflow.start_run(run_name=f'logistic-C-{c}') as run:
            model.fit(Xtr,ytr)
            proba=model.predict_proba(Xval)[:,1]
            score=roc_auc_score(yval,proba)
            mlflow.log_params({'C':c,'seed':42,'train_rows':len(Xtr),'validation_rows':len(Xval),'test_rows':len(Xtest),'threshold':.5})
            mlflow.set_tags({'dataset_sha256':digest,'git_commit':commit,'selection':'validation_roc_auc','authoring':'individual-assisted'})
            mlflow.log_metrics({'val_roc_auc':score,'val_pr_auc':average_precision_score(yval,proba),'val_f1':f1_score(yval,proba>=.5)})
            mlflow.log_artifact(str(ROOT/'requirements.txt'))
            info=mlflow.sklearn.log_model(model,'model',signature=infer_signature(Xtr,model.predict(Xtr)),input_example=Xtr.head(2))
            version=mlflow.register_model(info.model_uri,NAME)
            rows.append({'run_id':run.info.run_id,'version':version.version,'C':c,'val_roc_auc':score})
    best=max(rows,key=lambda r:r['val_roc_auc'])
    model=mlflow.sklearn.load_model(f"models:/{NAME}/{best['version']}")
    prob=model.predict_proba(Xtest)[:,1]
    metrics={'test_roc_auc':roc_auc_score(ytest,prob),'test_f1':f1_score(ytest,prob>=.5),'test_accuracy':accuracy_score(ytest,prob>=.5)}
    if metrics['test_roc_auc'] < .75:
        raise RuntimeError('Quality gate failed: test AUC < .75; production alias unchanged')
    client.set_registered_model_alias(NAME,'production',best['version'])
    client.set_model_version_tag(NAME,best['version'],'selection_reason','maximum validation ROC AUC; test AUC >= .75')
    with mlflow.start_run(run_id=best['run_id']): mlflow.log_metrics(metrics)
    evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
    result={'runs':rows,'selected':best,'test':metrics,'dataset_sha256':digest,'split_seed':42,'split_sizes':[len(Xtr),len(Xval),len(Xtest)]}
    (evidence/'training.json').write_text(json.dumps(result,indent=2))
    Xval.assign(Churn=yval).to_csv(evidence/'reference.csv',index=False)
    Xtest.assign(Churn=ytest).to_csv(evidence/'current.csv',index=False)
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
