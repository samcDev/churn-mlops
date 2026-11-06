import os
import mlflow, mlflow.sklearn
import pandas as pd
from fastapi.testclient import TestClient
from mlflow import MlflowClient
from src.common import NAME, ROOT, data, tracking
from src.drift import check,scenario
from src.app import app

def test_public_dataset():
    X,y=data();assert len(X)==7043;assert X.shape[1]>=4;assert not y.isna().any()

def test_registry_versions():
    mlflow.set_tracking_uri(tracking());c=MlflowClient()
    assert len(c.search_model_versions(f"name='{NAME}'"))>=5
    assert c.get_model_version_by_alias(NAME,'production').version

def test_api_real_registry():
    with TestClient(app) as c:
        assert c.get('/health').status_code==200
        assert c.get('/ready').json()['ready']
        payload={'tenure':12,'MonthlyCharges':75,'TotalCharges':900,'Contract':'Month-to-month','InternetService':'Fiber optic','PaymentMethod':'Electronic check'}
        r=c.post('/predict',json=payload);assert r.status_code==200
        d=r.json();assert 0<=d['probability']<=1 and d['pod'] and d['version']
        payload['tenure']=-1;assert c.post('/predict',json=payload).status_code==422
        assert 'fetch' in c.get('/').text

def test_drift_scenarios():
    mlflow.set_tracking_uri(tracking());m=mlflow.sklearn.load_model(f'models:/{NAME}@production')
    ref=pd.read_csv(ROOT/'evidence/reference.csv');cur=pd.read_csv(ROOT/'evidence/current.csv')
    normal=check(ref,cur,m);assert not normal['data_drift'] and not normal['concept_drift']
    assert check(ref,scenario(cur,'data'),m)['data_drift']
    concept=check(ref,scenario(cur,'concept'),m)
    assert concept['concept_drift'] and not concept['data_drift']
