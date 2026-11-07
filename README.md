# Customer Churn con MLflow Docker y Kubernetes

Proyecto individual del módulo MLOps y Puesta en Producción de la UAGRM.
Predice abandono de clientes sobre el dataset público IBM Telco, con 7.043 registros
y seis entradas. Incluye entrenamiento reproducible, cinco runs comparables, Model
Registry, FastAPI, contenedores propios, tres réplicas y pruebas de drift.

## Resultados verificados

Ejecución del 6 de noviembre de 2026 en Windows 11, Python 3.12.10 y Docker Desktop
con contexto Kubernetes `docker-desktop`.

| Comprobación | Resultado |
|---|---|
| Experimentación | Cinco valores de C; cinco versiones registradas |
| Modelo servido | telco-churn, versión 4, alias production |
| Run del modelo desplegado | 049f06a318534d88ab7514bb635396dd |
| ROC AUC test | 0.835731 |
| Pruebas automatizadas | 13 aprobadas |
| Balanceo con tres Pods | 120 POST; conteos 39, 41 y 40; cero errores |
| Recuperación | 152 solicitudes, 136 durante sustitución; cero fallos observados |
| Escalamiento | Tres a cinco a tres; 250 POST a cinco Pods sin errores |
| Drift | Normal pasa; alteraciones alertan; alarma temporal en lote 7 |
| Web | POST /predict al Service, puerto 30080; HTTP 200 |

La publicación GitHub y el ZIP final se completan después de revisar los documentos
y adjuntar las evidencias. La defensa oral es una instancia separada del enunciado.
El workflow CI está configurado; no se afirma una ejecución remota antes de comprobarla.

## Documentación

- [Informe técnico](docs/INFORME.md): metodología, resultados y responsabilidades.
- [Arquitectura](docs/ARQUITECTURA.md): componentes, decisiones y linaje.
- [Despliegue observado](docs/DESPLIEGUE.md): Pods, UIDs e imagen de la ejecución.
- [Datos](docs/DATOS.md): origen, variables y particiones.
- [Monitoreo](docs/MONITOREO.md): pruebas, umbrales y etiquetas tardías.
- [Matriz de cumplimiento](docs/MATRIZ.md): relación con cada requisito.
- [Materiales de referencia](docs/MATERIALES.md): adaptación de ejemplos de clase.

## Preparación en PowerShell

Requisitos: Python 3.12, Git, Docker Desktop funcionando, Kubernetes habilitado y
`kubectl` disponible. Ejecutar desde la carpeta que contiene el Dockerfile.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
python -m pip check
kubectl config use-context docker-desktop
kubectl get nodes
```

Si PowerShell bloquea la activación, usar una política solo para la sesión:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

El lock fija dependencias, incluido MLflow 2.22.2. Gunicorn se excluye en Windows
mediante un marcador de plataforma. No instalar las librerías del proyecto sobre
el Python global.

## Despliegue completo desde un entorno nuevo

```powershell
.\scripts\deploy.ps1
```

El script construye `churn-mlflow:1.0.0` y `churn-api:1.0.0`, aplica `k8s/stack.yaml`,
espera MLflow, entrena contra el Registry del clúster y reinicia la API para cargar
el alias aprobado. Los primeros Pods pueden fallar antes de que exista el alias;
el reinicio posterior al entrenamiento forma parte de la provisión.

Para realizar las etapas por separado:

```powershell
docker build -f Dockerfile.mlflow -t churn-mlflow:1.0.0 .
docker build -t churn-api:1.0.0 .
kubectl apply -f k8s/stack.yaml
kubectl -n churn rollout status deployment/mlflow --timeout=300s
$env:MLFLOW_TRACKING_URI = 'http://localhost:30500'
Invoke-RestMethod -Uri 'http://localhost:30500/health'
python -m src.train
kubectl -n churn rollout restart deployment/churn-api
kubectl -n churn rollout status deployment/churn-api --timeout=300s
kubectl -n churn get pods -l app=churn-api -o wide
```

En un despliegue ya inicializado no es necesario reentrenar para obtener capturas.
Repetir `src.train` crea cinco versiones adicionales y puede cambiar el número del
alias y el run. Actualizar la documentación si cambia la versión seleccionada.
Las imágenes deben estar disponibles para el Kubernetes de Docker Desktop porque
los manifiestos usan `imagePullPolicy: Never`.

| Servicio | URL local |
|---|---|
| Web | http://localhost:30080 |
| Documentación API | http://localhost:30080/docs |
| Identidad del modelo | http://localhost:30080/model |
| MLflow | http://localhost:30500 |

## Verificación y conservación de evidencias

Mantener el entorno virtual activo y apuntar al Registry del clúster:

```powershell
$env:MLFLOW_TRACKING_URI = 'http://localhost:30500'
python -m pytest -v --junitxml=evidence/pytest-windows.xml
.\scripts\run-drift.ps1
```

El wrapper de drift verifica los códigos esperados. Normal=0; data=2; concept=2;
temporal normal=0 y temporal concept=2. Los códigos 2 son alertas deliberadas de las
compuertas, no fallos de instalación. Se generan JSON, CSV y figuras en `evidence`.

La prueba pytest de API usa TestClient con el modelo del Registry. Para demostrar
la API desplegada y el balanceo, se usan las siguientes pruebas sobre el NodePort:

```powershell
python scripts/balance.py --min-pods 3
Copy-Item evidence/balance.json evidence/balance-three.json
python scripts/recovery.py
kubectl -n churn scale deployment/churn-api --replicas=5
kubectl -n churn rollout status deployment/churn-api --timeout=300s
kubectl -n churn get pods -l app=churn-api -o wide
python scripts/balance.py --requests 250 --min-pods 5
Copy-Item evidence/balance.json evidence/balance-five.json
kubectl -n churn scale deployment/churn-api --replicas=3
kubectl -n churn rollout status deployment/churn-api --timeout=300s
kubectl -n churn get pods -l app=churn-api -o wide
python scripts/record-deployment.py
Move-Item .\docs\DESPLIEGUE_REAL.md .\docs\DESPLIEGUE.md -Force
```

`recovery.py` requiere exactamente tres Pods Running y Ready antes de eliminar uno;
conserva todas las solicitudes y falla si observa errores. Tras reducir réplicas,
esperar a que desaparezcan los Pods en Terminating antes de capturar el estado final.
`verify-k8s.ps1` automatiza el recorrido; después puede aplicarse el mismo renombrado
del anexo generado para mantener el nombre `DESPLIEGUE.md` usado en esta entrega.

No usar `kubectl port-forward` como prueba de balanceo porque puede fijar un Pod.
El comprobador usa nuevas conexiones al Service, exige identidades diferentes y
comprueba versión/run en cada respuesta. No exige un reparto idéntico. Cero fallos
observados es una medición finita, no una promesa de uptime absoluto.

En la web, completar el formulario y pulsar Consultar API. En F12 > Network,
seleccionar `predict` y verificar POST al puerto 30080 con estado 200. Conservar
capturas en `evidence/capturas` y adjuntar las gráficas PNG originales al informe.

## Estructura de la entrega

- `src`, `tests`, `scripts`, `k8s` y `frontend`: implementación y verificadores.
- Dockerfiles y archivos de dependencias: construcción reproducible.
- `data/telco.csv`: dataset público versionado con hash de integridad.
- `docs`: documentación técnica del proyecto.
- `evidence`: pruebas, resultados y capturas del entorno de ejecución.
- `.github/workflows/ci.yml`: integración continua preparada para GitHub Actions.

Los CSV de referencia de `evidence` se regeneran al entrenar. La regla actual de
`.gitignore` excluye esos CSV de Git; pueden conservarse en el ZIP de entrega. Los
JSON, XML, figuras y capturas sí deben versionarse. No publicar `.venv`, cachés,
archivos temporales de Word ni bases locales; el Registry se inicializa con MLflow.

Después de publicar, entregar la URL del repositorio y un ZIP de código,
documentación y evidencias. `python scripts/package.py` genera el ZIP en la carpeta
padre. Revisar su contenido antes de enviar; incluye el historial `.git` y excluye
entorno virtual, cachés y bases temporales. El informe final Word/PDF y las capturas
deben estar dentro del proyecto antes de empaquetar si se pretende incluirlos.

## Límites operativos

El laboratorio utiliza un nodo local: varias réplicas no protegen ante pérdida del
equipo completo. MLflow usa SQLite y PVC con una réplica; los Pods ya iniciados
conservan el modelo en memoria, pero nuevos arranques dependen del Registry.
Los NodePorts se destinan al laboratorio sin autenticación. Los escenarios de drift
son simulaciones controladas; los umbrales son didácticos y requieren calibración
para uso comercial. La cola productiva de etiquetas tardías y CT automático no se
presentan como implementados. El runner CI hospedado no accede al clúster local.

Para diagnóstico:

```powershell
kubectl -n churn get pods -o wide
kubectl -n churn get endpointslices
kubectl -n churn logs deployment/churn-api --tail=80
```
