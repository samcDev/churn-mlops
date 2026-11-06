import json
from pathlib import Path
import requests
base='http://127.0.0.1:8000'
payload={'tenure':12,'MonthlyCharges':75,'TotalCharges':900,'Contract':'Month-to-month','InternetService':'Fiber optic','PaymentMethod':'Electronic check'}
r=requests.post(base+'/predict',json=payload,timeout=15);r.raise_for_status();d=r.json()
assert 0<=d['probability']<=1 and d['version'] and d['pod']
bad=requests.post(base+'/predict',json={**payload,'tenure':-1},timeout=15)
assert bad.status_code==422
home=requests.get(base+'/',timeout=15);assert home.ok and "fetch('/predict'" in home.text
result={'environment':'local Linux HTTP; not Kubernetes','prediction_status':r.status_code,'prediction':d,'invalid_status':bad.status_code,'frontend_status':home.status_code,'browser_execution':'pending Windows Kubernetes'}
Path('evidence/http-smoke.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
