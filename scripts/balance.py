import argparse,collections,json
from pathlib import Path
import requests
p=argparse.ArgumentParser();p.add_argument('--url',default='http://localhost:30080');p.add_argument('--requests',type=int,default=120);p.add_argument('--min-pods',type=int,default=3);a=p.parse_args()
payload={'tenure':12,'MonthlyCharges':75,'TotalCharges':900,'Contract':'Month-to-month','InternetService':'Fiber optic','PaymentMethod':'Electronic check'}
counts=collections.Counter();errors=[];models={}
expected=json.loads(Path('evidence/training.json').read_text())['selected']
for i in range(a.requests):
    try:
        # Fresh connections: Service selects backends at connection granularity.
        r=requests.post(a.url+'/predict',json=payload,headers={'Connection':'close'},timeout=10);r.raise_for_status();d=r.json()
        if not 0<=d['probability']<=1: raise ValueError('Invalid probability')
        if d['version']!=str(expected['version']) or d['run_id']!=expected['run_id']: raise ValueError('Runtime version/run differs from most recent training selection')
        counts[d['pod']]+=1;models[d['pod']]={'version':d['version'],'run_id':d['run_id'],'alias':d['alias']}
    except Exception as e: errors.append(str(e))
result={'url':a.url,'requests':a.requests,'counts':dict(counts),'models_by_pod':models,'expected_model':expected,'errors':errors,'success':len(counts)>=a.min_pods and not errors}
Path('evidence').mkdir(exist_ok=True);Path('evidence/balance.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
raise SystemExit(0 if result['success'] else 1)
