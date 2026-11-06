# Arquitectura, trazabilidad y modelo servido

## Identidad comprobada en esta ejecución

| Elemento | Valor |
|---|---|
| Experimento | telco-churn-individual |
| Nombre registrado | telco-churn |
| Alias | production |
| Versión seleccionada y servida en HTTP Linux | 4 |
| Run exacto | 73dacc6ce01d45859fe4fbea8b1335db |
| Hiperparámetro C | 10.0 |
| ROC AUC validación | 0.830572 |

Esto acredita el servicio HTTP de este entorno, **no un despliegue Kubernetes ya
verificado**. En tu equipo, cada entrenamiento puede incrementar las versiones.
Tras `verify-k8s.ps1`, `record-deployment.py` genera `docs/DESPLIEGUE_REAL.md` y
`evidence/deployed-model.json` con la versión/run realmente servidos, UIDs e imágenes.
El comprobador de balanceo exige que cada Pod coincida con el último training.json.

```mermaid
flowchart TD
    D["CSV versionado + hash"] --> T["Entrenamiento: cinco runs"]
    T --> R["MLflow: Registry + alias production"]
    R --> A["FastAPI: modelo en memoria por Pod"]
    W["Web HTML: POST /predict"] --> S["Service NodePort"]
    S --> A
    A --> O["Identidad Pod, versión y run"]
```

## Separación de responsabilidades

MLflow almacena metadatos en SQLite y artifacts en PVC; los sirve por HTTP. La API
resuelve el alias una vez al arrancar y carga esa versión numérica inmutable. No
administra pickle/joblib manual ni copia rutas Windows dentro de los Pods.
El flavor sklearn puede serializar internamente: la gestión del artefacto sigue siendo MLflow.
El servicio inicia automáticamente con Uvicorn y usa Registry ya inicializado. Los
pasos de entrenamiento/población inicial del Registry son provisión del entorno,
no pasos manuales de cada contenedor de inferencia.

Tres réplicas FastAPI, probes y Service permiten disponibilidad horizontal. MLflow
tiene una réplica y PVC para esta práctica; una caída suya no elimina los modelos ya
cargados, pero impide nuevos arranques mientras esté indisponible. No se afirma alta
disponibilidad del plano MLflow. Para producción: DB externa, object storage,
autenticación y redundancia. El contenedor API no requiere Python instalado en el host.

## Balanceo, autorreparación y escala

NodePort 30080 expone la API; 30500 expone MLflow. POST con conexión nueva permite
que el Service seleccione otros backends. Se exigen >=3 y luego >=5 Pods distintos,
sin imponer reparto idéntico. No usar port-forward como prueba de balanceo.

`recovery.py` emite inferencias antes, durante y después de eliminar un Pod, registra
todas las solicitudes y verifica un UID nuevo Running/Ready y recuperación a tres.
Cero errores observados es el criterio; no se ocultarán fallos ni se reintenta una
solicitud fallida para hacerla parecer exitosa. Es observación finita, no prueba
matemática de uptime absoluto. preStop espera cinco segundos para favorecer el
retiro de endpoints antes de finalizar Uvicorn; el período de gracia es 30 segundos.
La prueba de escala cambia 3→5→3 y exige cinco identidades sirviendo inferencias.

## Reproducibilidad y actualización

Pipeline contiene imputación/escalado/one-hot y clasificador. Semilla 42; split
60/20/20 estratificado. Cinco configuraciones comparables seleccionadas por validación;
test no elige C. Datos con SHA256, lock transitivo y hash del script registrados.
Cambiar alias requiere rollout de Pods; no se promete cambio atómico de todas las
réplicas. K8s y Docker pendientes de ejecución local, como indica MATRIZ.md.
