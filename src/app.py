from contextlib import asynccontextmanager
import os, socket
import mlflow, mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from src.common import ROOT, NAME, tracking

class Customer(BaseModel):
    model_config=ConfigDict(extra='forbid', allow_inf_nan=False)
    tenure: int=Field(ge=0,le=100)
    MonthlyCharges: float=Field(ge=0,le=1000)
    TotalCharges: float=Field(ge=0,le=100000)
    Contract: Literal['Month-to-month','One year','Two year']
    InternetService: Literal['DSL','Fiber optic','No']
    PaymentMethod: Literal['Electronic check','Mailed check','Bank transfer (automatic)','Credit card (automatic)']

@asynccontextmanager
async def lifespan(app):
    mlflow.set_tracking_uri(tracking())
    alias=os.getenv('MODEL_ALIAS','production')
    version=MlflowClient().get_model_version_by_alias(NAME,alias)
    # Resolve alias once, then load immutable version to avoid a metadata/load race.
    app.state.model=mlflow.sklearn.load_model(f'models:/{NAME}/{version.version}')
    app.state.version=version.version
    app.state.run_id=version.run_id
    app.state.alias=alias
    yield

app=FastAPI(title='Churn MLOps UAGRM',lifespan=lifespan)
@app.get('/')
def web(): return FileResponse(ROOT/'frontend/index.html')
@app.get('/health')
def health(): return {'status':'alive','pod':socket.gethostname()}
@app.get('/ready')
def ready(): return {'ready':app.state.model is not None,'version':app.state.version}
@app.get('/model')
def metadata(): return {'name':NAME,'alias':app.state.alias,'version':app.state.version,'run_id':app.state.run_id,'pod':socket.gethostname()}
@app.post('/predict')
def predict(customer:Customer):
    probability=float(app.state.model.predict_proba(pd.DataFrame([customer.model_dump()]))[0,1])
    return {'churn':int(probability>=.5),'probability':probability,'threshold':.5,**metadata()}
