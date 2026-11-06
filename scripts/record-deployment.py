"""Generate the actual deployment appendix after successful local-cluster checks."""
import datetime,json,subprocess
from pathlib import Path
import requests
model=requests.get('http://localhost:30080/model',timeout=15);model.raise_for_status();d=model.json()
expected=json.loads(Path('evidence/training.json').read_text())['selected']
assert d['version']==str(expected['version']) and d['run_id']==expected['run_id']
pods=json.loads(subprocess.check_output(['kubectl','-n','churn','get','pods','-l','app=churn-api','-o','json'],text=True))
Path('evidence/deployed-model.json').write_text(json.dumps({'model':d,'pods':pods,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
rows=[]
for pod in pods['items']:
    for c in pod['status'].get('containerStatuses',[]):
        rows.append(f"| {pod['metadata']['name']} | {pod['metadata']['uid']} | {c.get('imageID','')} | {c['ready']} |")
text=f"# Anexo de arquitectura: despliegue real\n\nModelo `{d['name']}`, alias `{d['alias']}`, versión **{d['version']}**, run `{d['run_id']}`.\n\nService NodePort: http://localhost:30080; Registry: http://localhost:30500.\n\n| Pod | UID | Imagen | Ready |\n|---|---|---|---|\n"+'\n'.join(rows)+'\n'
Path('docs/DESPLIEGUE_REAL.md').write_text(text)
print(text)
