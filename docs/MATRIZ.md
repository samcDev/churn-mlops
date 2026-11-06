# Matriz de cumplimiento del enunciado oficial

Fuente: ENUNCIADO_OFICIAL.md, texto recibido en el chat. V = verificado en Linux;
I/P = implementado, pendiente de ejecución Windows/Docker/Kubernetes; P = pendiente.
No se asigna una nota ni se dan por obtenidos los 15 puntos extra.

| Cláusula | Requisito | Solución / evidencia | Estado |
|---|---|---|---|
| 2 | Modalidad individual y reparto | RESPONSABILIDADES.md; historial real, asistencia declarada | V; completar identificación académica antes de entregar |
| 2 | Git obligatorio | .git y repository.bundle con commits reales | V local; URL GitHub P |
| 2 | Defensa individual de todo el proyecto | DEFENSA.md con demostración y preguntas | Preparada; defensa P |
| 3.1 | Problema con varias entradas, dataset público recomendado >=1000 | IBM Telco: 7.043 filas, seis predictores | V |
| 3.2 | Entrenamiento reproducible y split documentado | Semilla 42, split 60/20/20, Pipeline, hash y lock | V |
| 3.2 | >=5 ejecuciones comparables con distintos hiperparámetros | Cinco runs de C=0.01/0.1/1/10/100 sobre mismo split | V; cinco runs cumplen el texto oficial |
| 3.3 | Experimentación y versionado en MLflow | Tracking HTTP, métricas, parámetros, firma y artifacts | V |
| 3.3.2 | Nombre estable y varias versiones | Registry telco-churn, cinco versiones | V |
| 3.3.2 | Referencia explícita de producción | production → versión numérica; API resuelve alias y carga esa versión | V local; consumo en clúster I/P |
| 3.3.2 | Arquitectura identifica versión y run | ARQUITECTURA.md y training.json; DESPLIEGUE_REAL.md se genera tras K8s | V local; correspondencia K8s I/P |
| 3.4 | UI MLflow operativa y demostración en vivo | Servidor preparado, snapshot, guion de filtro/orden/comparación/Registry | HTTP del servidor V; interacción y defensa local P |
| 4 | Dockerfile propio | Dockerfile API y Dockerfile.mlflow | I/P construcción real |
| 4 | Dependencias fijadas, incluido MLflow | requirements-lock.txt y Python base fijado | V instalación Linux; Docker/Windows I/P |
| 4 | Contenedor levanta inferencia sin intervención | CMD Uvicorn, carga de Registry al inicio, sin archivos modelo manuales | I/P ejecución de contenedor |
| 5.2 | >=3 réplicas Running simultáneamente | Deployment replicas=3; chequeos Running y Ready | I/P |
| 5.2 | Tráfico entre Pods distintos por Service | POST NodePort con conexiones nuevas, identidad y versión/run por Pod | I/P; exige >=3 identidades, cero errores |
| 5.2 | Autorreparación sin dejar de responder | recovery.py: POST antes/durante/después de delete, nuevo UID Ready | I/P; criterio cero solicitudes fallidas observadas |
| 5.2 | Escalado y efecto | 3→5→3; cinco Ready y POST atendidos por cinco Pods | I/P |
| 6.1 | Cada entrada contra baseline de entrenamiento | reference.csv contiene 4.225 filas train; seis variables comparadas | V |
| 6.1 | Prueba por tipo de variable y justificación | KS numéricas; chi-cuadrado categóricas más distancia TV | V; MONITOREO.md |
| 6.1 | Umbrales y procedencia | Bonferroni 0.05/6; KS>0.1; TV>0.15, tolerancias didácticas previas | V; límites documentados |
| 6.1 | Verde normal y rojo perturbado | drift normal=0; data=2; pruebas categóricas y numéricas | V; logs y JSON |
| 6.2 | Cambiar relación entrada/objetivo | Inversión de etiquetas desde lote 5 manteniendo entradas | V, simulación explícita |
| 6.2 | Métrica principal por lotes y gráfica temporal | ROC AUC en diez lotes disjuntos, CSV/JSON/PNG | V; tiempo simulado |
| 6.2 | Caída sostenida y criterio de reentrenamiento | ROC AUC cae >=0.10 durante 3 lotes etiquetados consecutivos | V; alarma lote 7 en escenario alterado |
| 6.2 | Retraso de etiquetas | Sin etiquetas: no calcular desempeño; cola de conciliación; vigilar entradas/API | V diseño y prueba lógica; MONITOREO.md |
| 7 | UI consume API real en Kubernetes | HTML fetch /predict same-origin, muestra versión/run/Pod | HTTP Linux V; navegador/Network K8s I/P |
| Entrega | Enlace repo y ZIP con documentación/evidencias | ZIP y bundle presentes | ZIP V; URL GitHub y evidencia K8s P |

El proyecto base no se declara completo hasta ejecutar los puntos Docker/Kubernetes.
La web ya está implementada, pero los extras dependen de cerrar primero el proyecto base.
