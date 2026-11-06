"""Observe real POST availability while deleting one Pod. Run only on local Docker Desktop."""
import argparse,datetime,json,subprocess,threading,time
from pathlib import Path
import requests

PAYLOAD={'tenure':12,'MonthlyCharges':75,'TotalCharges':900,'Contract':'Month-to-month','InternetService':'Fiber optic','PaymentMethod':'Electronic check'}

def kubectl(*args):
    r=subprocess.run(['kubectl',*args],capture_output=True,text=True,timeout=60,check=True)
    return r.stdout

def ready_pods():
    items=json.loads(kubectl('-n','churn','get','pods','-l','app=churn-api','-o','json'))['items']
    return [p for p in items if p['status'].get('phase')=='Running' and not p['metadata'].get('deletionTimestamp') and p['status'].get('containerStatuses') and all(s.get('ready') for s in p['status']['containerStatuses'])]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://localhost:30080');ap.add_argument('--timeout',type=int,default=180);a=ap.parse_args()
    if kubectl('config','current-context').strip()!='docker-desktop': raise SystemExit('Expected docker-desktop context')
    before=ready_pods()
    if len(before)!=3: raise SystemExit('Expected exactly three Running and Ready Pods before deletion')
    old=before[0];old_uids={p['metadata']['uid'] for p in before}
    samples=[];stop=threading.Event();phase={'value':'before_delete'}
    def monitor():
        while not stop.is_set():
            item={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase['value']}
            start=time.monotonic()
            try:
                r=requests.post(a.url+'/predict',json=PAYLOAD,headers={'Connection':'close'},timeout=3)
                r.raise_for_status();d=r.json()
                if not 0<=d['probability']<=1: raise ValueError('Invalid probability')
                item.update({'ok':True,'status':r.status_code,'pod':d['pod'],'version':d['version']})
            except Exception as e: item.update({'ok':False,'error':str(e)})
            item['latency_seconds']=time.monotonic()-start;samples.append(item)
            stop.wait(.15)
    thread=threading.Thread(target=monitor,daemon=True);thread.start()
    replacement=[];failure=None;after=[]
    try:
        deadline=time.monotonic()+15
        while len(samples)<5 and time.monotonic()<deadline: time.sleep(.1)
        if len(samples)<5 or not all(s['ok'] for s in samples): raise RuntimeError('Pre-deletion API check failed')
        phase['value']='delete_and_replacement'
        kubectl('-n','churn','delete','pod',old['metadata']['name'],'--wait=false')
        deadline=time.monotonic()+a.timeout
        while time.monotonic()<deadline:
            after=ready_pods();replacement=[p for p in after if p['metadata']['uid'] not in old_uids]
            if len(after)==3 and replacement and all(p['metadata']['uid']!=old['metadata']['uid'] for p in after): break
            time.sleep(.5)
        else: raise RuntimeError('Replacement did not become Ready before deadline')
        phase['value']='after_ready';time.sleep(2)
    except Exception as e: failure=str(e)
    finally: stop.set();thread.join(timeout=5)
    during=[s for s in samples if s['phase']=='delete_and_replacement']
    post=[s for s in samples if s['phase']=='after_ready']
    success=failure is None and len(during)>=1 and len(post)>=1 and all(s['ok'] for s in samples)
    result={'success':success,'criterion':'zero failed sampled POST requests before/during/after delete plus new UID Running and Ready; finite observation, not proof of absolute uptime','old_pod':{'name':old['metadata']['name'],'uid':old['metadata']['uid']},'new_pods':[{'name':p['metadata']['name'],'uid':p['metadata']['uid'],'phase':p['status']['phase']} for p in replacement],'ready_after':len(after),'sample_count':len(samples),'during_delete_count':len(during),'failed_requests':sum(not s['ok'] for s in samples),'failure':failure,'samples':samples}
    Path('evidence/recovery.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2))
    raise SystemExit(0 if success else 1)
if __name__=='__main__': main()
