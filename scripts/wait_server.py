import time,requests
for _ in range(60):
    try:
        if requests.get('http://127.0.0.1:5000/health',timeout=2).ok: break
    except requests.RequestException: pass
    time.sleep(1)
else: raise SystemExit('MLflow did not start')
