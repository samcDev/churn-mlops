$ErrorActionPreference = 'Stop'
function Check { if ($LASTEXITCODE -ne 0) { throw 'Previous command failed' } }
$ctx = kubectl config current-context
if ($ctx -ne 'docker-desktop') { throw 'Run kubectl config use-context docker-desktop first' }
docker build -f Dockerfile.mlflow -t churn-mlflow:1.0.0 .; Check
docker build -t churn-api:1.0.0 .; Check
kubectl apply -f k8s/stack.yaml; Check
kubectl -n churn rollout status deployment/mlflow --timeout=300s; Check
$env:MLFLOW_TRACKING_URI = 'http://localhost:30500'
python -c "import os,time,requests; u=os.environ['MLFLOW_TRACKING_URI']+'/health'; r=requests.get(u,timeout=20); r.raise_for_status()"; Check
python -m src.train; Check
kubectl -n churn rollout restart deployment/churn-api; Check
kubectl -n churn rollout status deployment/churn-api --timeout=300s; Check
Write-Host 'Open http://localhost:30080 and http://localhost:30500'
