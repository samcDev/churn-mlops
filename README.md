# Customer Churn — Proyecto individual MLOps UAGRM

Implementación funcional con datos públicos IBM Telco (7.043 clientes), seis predictores,
cinco corridas reproducibles, cinco versiones registradas, alias `production`, FastAPI,
Docker, Kubernetes y controles de drift. Leer `docs/INFORME.md` y `docs/MATRIZ.md`.

**Alcance de la verificación:** resultados locales reales en `evidence/`. Docker,
Kubernetes y navegador contra Kubernetes requieren ejecución en Windows. No se
atribuyen puntos de la rúbrica oficial porque el enunciado no estaba entre los seis adjuntos.
Cinco configuraciones se agrupan en un experimento MLflow, con cinco runs: la terminología
del requisito debe contrastarse con el enunciado (clase 5, diapositiva 5).

## 1. Preparación en PowerShell (Python 3.12)

Desde la carpeta extraída, con VS Code:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
python -m pip check
```

Si la política bloquea la activación, se puede usar directamente
`.\.venv\Scripts\python.exe` en los comandos de Python.
El lock contiene el entorno probado; Gunicorn se excluye en Windows mediante un marcador.
No reutilizar los `requirements.txt` de los ejemplos sin revisar su compatibilidad.

## 2. Validación sin Docker (opcional, previa al despliegue)

Terminal A, desde la raíz del proyecto:

```powershell
mlflow server --backend-store-uri sqlite:///mlflow.db --serve-artifacts --artifacts-destination ./mlartifacts --host 127.0.0.1 --port 5000
```

Terminal B, mismo entorno y directorio:

```powershell
$env:MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
python -m src.train
pytest -v --junitxml=evidence/pytest-local.xml
.\scripts\run-drift.ps1
uvicorn src.app:app --host 127.0.0.1 --port 8000
```

Abrir http://localhost:8000 y http://localhost:5000. Los resultados de la API
provienen del Registry real. La aplicación no tiene modelo de respaldo manual.
Cada nuevo entrenamiento agrega cinco versiones; por ello la versión seleccionada
puede tener un número distinto de la ejecución incluida.

## 3. Despliegue en Docker Desktop Kubernetes

Activar Kubernetes en Docker Desktop y reservar aproximadamente 6 GB de RAM.
El motor de Docker y el clúster deben compartir las imágenes locales; los manifiestos
usan `imagePullPolicy: Never`. Ante `ErrImageNeverPull`, comprobar el almacén de
imágenes de Docker Desktop y su integración Kubernetes antes de continuar.

```powershell
kubectl config use-context docker-desktop
kubectl cluster-info
.\scripts\deploy.ps1
$env:MLFLOW_TRACKING_URI = 'http://localhost:30500'
pytest -v --junitxml=evidence/pytest-k8s-registry.xml
.\scripts\run-drift.ps1
.\scripts\verify-k8s.ps1
```

El despliegue crea MLflow con PVC y SQLite, entrena contra su NodePort HTTP y luego
reinicia los Pods de inferencia para cargar el alias aprobado. Los Pods que arrancan
antes de existir el alias pueden fallar inicialmente; el reinicio posterior al entrenamiento
es parte del procedimiento. SQLite con una réplica es apropiado para la práctica local;
un servicio de producción requeriría base de datos externa, autenticación y almacenamiento remoto.

- Web: http://localhost:30080
- OpenAPI: http://localhost:30080/docs
- MLflow: http://localhost:30500

**No usar `kubectl port-forward` para demostrar balanceo:** puede dirigir todo a un
solo Pod. El comprobador abre conexiones nuevas al NodePort, cuenta nombres de Pods,
exige tres y luego cinco identidades distintas y falla ante cualquier error HTTP.
No exige reparto uniforme: el Service distribuye conexiones y la muestra es finita.

## 4. Evidencias auténticas pendientes

El script de Kubernetes guarda transcripción, UIDs antes/después de eliminar un Pod,
conteos por Pod y estado de cinco réplicas. No demuestra ausencia absoluta de interrupciones
mientras se elimina un Pod; demuestra recuperación y disponibilidad posterior.
Capturar personalmente: MLflow comparando cinco runs; Registry con versiones y alias;
Pods Ready; salida de balanceo; eliminación y nuevo UID; cinco réplicas;
web mostrando resultado y pestaña Network con POST `/predict` al puerto 30080.
La prueba pytest contra el Registry Kubernetes todavía ejecuta la API mediante TestClient;
la comprobación NodePort y la prueba web son verificaciones separadas.

```powershell
kubectl -n churn get pods -o wide
kubectl -n churn get endpointslices
kubectl -n churn logs deployment/churn-api --tail=80
```

El control `data` devuelve código 2 por una alerta esperada; `concept` también.
El escenario normal debe devolver 0. Una alerta detectada correctamente es éxito del
detector y fallo intencional de la compuerta de datos/modelo.

## 5. Git y entrega

El paquete incluye el repositorio `.git` y un `repository.bundle` con el historial real
creado durante esta implementación. No contiene historia de días ficticios ni identidad
personal inventada. Alternativa para reconstruirlo:

```powershell
git clone .\repository.bundle churn-entrega
```

Para publicar, crear un repositorio vacío en tu cuenta de GitHub y ejecutar dentro del proyecto:

```powershell
git remote add origin https://github.com/TU_USUARIO/churn-mlops.git
git push -u origin main
```

Sustituir la URL por tu repositorio real. CI está preparado pero sus ejecuciones en GitHub
no se afirman verificadas. El runner hospedado no accede a tu Kubernetes local.
Después de ejecutar las pruebas locales, revisar y versionar sus evidencias:

```powershell
git add evidence docs
git commit -m "test: add real Docker Desktop Kubernetes evidence"
git push
```

Guardar capturas reales en `evidence/capturas/`. Para un ZIP actualizado, ejecutar
`python scripts/package.py`; incluye `.git` y excluye entornos, cachés y bases temporales.
La limpieza `kubectl delete namespace churn` elimina también el PVC y sus modelos:
usarla solamente cuando ya no se necesite el estado del laboratorio.

## Estado MLflow de la ejecución incluida

`evidence/mlflow-snapshot.zip` conserva la base del Registry y los artefactos reales.
Es evidencia reproducible de esta sesión; no se usa como sustituto del Registry.
Para inspeccionarlo sin reentrenar, desde la raíz y sin otro servidor en el puerto:

```powershell
Expand-Archive evidence/mlflow-snapshot.zip -DestinationPath . -Force
mlflow server --backend-store-uri sqlite:///verify.db --serve-artifacts --artifacts-destination ./mlartifacts --host 127.0.0.1 --port 5000
```

En otra terminal: `$env:MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'` y luego
`pytest -v`. Los CSV de referencia/actual están incluidos en el ZIP de entrega,
pero no en el bundle Git: el entrenamiento los regenera. Para comprobar despliegue
se recomienda entrenar nuevamente contra el Registry del clúster usando deploy.ps1.
