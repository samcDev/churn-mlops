import argparse,collections,json,time
from pathlib import Path
import requests
p=argparse.ArgumentParser();p.add_argument('--url',default='http://localhost:30080');p.add_argument('--requests',type=int,default=120);p.add_argument('--min-pods',type=int,default=3);a=p.parse_args()
payload={'tenure':12,'MonthlyCharges':75,'TotalCharges':900,'Contract':'Month-to-month','InternetService':'Fiber optic','PaymentMethod':'Electronic check'}
counts=collections.Counter();errors=[]
for i in range(a.requests):
    try:
        # A fresh TCP connection per request allows Service to select another backend.
        r=requests.post(a.url+'/predict',json=payload,headers={'Connection':'close'},timeout=10);r.raise_for_status();counts[r.json()['pod']]+=1
    except Exception as e: errors.append(str(e))
result={'url':a.url,'requests':a.requests,'counts':dict(counts),'errors':errors,'success':len(counts)>=a.min_pods and not errors}
Path('evidence').mkdir(exist_ok=True);Path('evidence/balance.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
raise SystemExit(0 if result['success'] else 1)
