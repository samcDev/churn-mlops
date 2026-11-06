import os
import pytest
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
    perf=pd.read_csv(ROOT/'evidence/performance-reference.csv')
    normal=check(ref,cur,m,perf);assert not normal['data_drift'] and not normal['concept_drift']
    assert check(ref,scenario(cur,'data'),m,perf)['data_drift']
    concept=check(ref,scenario(cur,'concept'),m,perf)
    assert concept['concept_drift'] and not concept['data_drift']

@pytest.mark.parametrize('field,value',[('tenure',101),('MonthlyCharges',-1),('Contract','unknown'),('unexpected',1)])
def test_invalid_input_contract(field,value):
    with TestClient(app) as c:
        payload={'tenure':12,'MonthlyCharges':75,'TotalCharges':900,'Contract':'Month-to-month','InternetService':'Fiber optic','PaymentMethod':'Electronic check'}
        payload[field]=value
        assert c.post('/predict',json=payload).status_code==422

def test_categorical_drift():
    mlflow.set_tracking_uri(tracking());m=mlflow.sklearn.load_model(f'models:/{NAME}@production')
    ref=pd.read_csv(ROOT/'evidence/reference.csv');cur=pd.read_csv(ROOT/'evidence/current.csv')
    cur['Contract']='Two year'
    assert check(ref,cur,m)['features']['Contract']['drift']

from src.temporal import alarm_steps,evaluate

def test_training_drift_baseline():
    assert len(pd.read_csv(ROOT/'evidence/reference.csv'))==4225
    assert len(pd.read_csv(ROOT/'evidence/performance-reference.csv'))==1409

def test_transient_drop_does_not_trigger_retraining():
    assert not any(x['alarm'] for x in alarm_steps([.6,.6,.82,.6,.6],.83))

def test_sustained_drop_and_delayed_labels():
    states=alarm_steps([.6,None,.6,.6],.83)
    assert states[1]['status']=='waiting_for_labels'
    assert not any(x['alarm'] for x in states[:3])
    assert states[3]['alarm']

def test_temporal_real_registry():
    mlflow.set_tracking_uri(tracking());m=mlflow.sklearn.load_model(f'models:/{NAME}@production')
    perf=pd.read_csv(ROOT/'evidence/performance-reference.csv');cur=pd.read_csv(ROOT/'evidence/current.csv')
    normal=evaluate(m,perf,cur,'normal');shifted=evaluate(m,perf,cur,'concept')
    assert not normal['alarm']
    assert shifted['alarm'] and shifted['first_alarm_batch']==7
    assert sum(b['rows'] for b in shifted['batches'])==len(cur)
