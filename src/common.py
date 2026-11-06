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
    if len(df) < 1000 or not df.customerID.is_unique:
        raise ValueError('Dataset must have >=1000 unique customers')
    if set(df.Churn) != {'Yes', 'No'}:
        raise ValueError('Invalid binary target')
    if df[FEATURES].isna().mean().max() > .01:
        raise ValueError('Missing value fraction exceeds 1%')
    if df[['tenure','MonthlyCharges']].isna().any().any():
        raise ValueError('Unexpected missing tenure or MonthlyCharges')
    return df[FEATURES], df.Churn.map({'Yes': 1, 'No': 0})
