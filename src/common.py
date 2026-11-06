import os
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['tenure', 'MonthlyCharges', 'TotalCharges', 'Contract', 'InternetService', 'PaymentMethod']
NUMERIC = FEATURES[:3]
CATEGORICAL = FEATURES[3:]
NAME = 'telco-churn'
def tracking():
    return os.getenv('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5000')
def data():
    df = pd.read_csv(ROOT / 'data/telco.csv')
    df['TotalCharges'] = pd.to_numeric(df.TotalCharges, errors='coerce')
    assert len(df) >= 1000 and df.customerID.is_unique
    assert set(df.Churn) == {'Yes', 'No'}
    return df[FEATURES], df.Churn.map({'Yes': 1, 'No': 0})
