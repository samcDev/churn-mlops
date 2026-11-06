# Predicción de abandono de clientes mediante un flujo MLOps reproducible

**Maestría en Ciencia de Datos e Inteligencia Artificial — UAGRM**  
**Módulo:** MLOps y Puesta en Producción  
**Modalidad:** Individual, con asistencia de IA declarada en la implementación  
**Fecha de verificación:** 5 de noviembre de 2026 (Bolivia)  
**Estado:** Entrenamiento, Registry, API y drift verificados; Docker/Kubernetes y
la interfaz sobre el clúster pendientes de verificación local. Identificación del
estudiante por completar antes de entrega: el titular de este chat no garantiza
la identidad de quien cursa el módulo.

## Resumen

Se construyó un repositorio ejecutable para predecir churn con 7.043 registros del
benchmark IBM Telco. El flujo versiona datos y código, evalúa cinco configuraciones
de regresión logística, registra sus pipelines en MLflow y promueve una versión
mediante alias. FastAPI consume el Registry real. Se implementaron contenedores,
un despliegue Kubernetes de tres réplicas y pruebas automatizadas de distribución
de solicitudes, recuperación y escalamiento. En el entorno disponible se ejecutaron
nueve pruebas de integración, solicitudes HTTP reales y tres escenarios de drift.
No se presentan resultados Kubernetes ni capturas que no hayan sido ejecutados.

## Objetivo y alcance

El objetivo es llevar un modelo desde el entrenamiento hasta una API reproducible
y observable, con trazabilidad entre datos, hiperparámetros, run y versión. Los datos
son un benchmark educativo, sin relación con una empresa del usuario. La clasificación
podría apoyar priorización de retención; no determina el efecto causal de una campaña.
La matriz es provisional porque no se adjuntó el documento oficial del proyecto final.

## Metodología

Se eligieron seis predictores: tenure, MonthlyCharges, TotalCharges, Contract,
InternetService y PaymentMethod. Se excluyen customerID y Churn de las entradas.
TotalCharges se convierte a numérico y sus blancos se imputan con mediana aprendida
solo de entrenamiento. Variables numéricas se estandarizan y categóricas se codifican
mediante one-hot. Todos los pasos forman parte del Pipeline registrado.

La partición es estratificada con semilla 42: 4.225 casos para entrenamiento,
1.409 para validación y 1.409 para prueba. Se mantiene el mismo split para las cinco
configuraciones de C. La selección utiliza exclusivamente ROC AUC de validación;
el test del ganador evalúa una compuerta mínima de AUC >= 0,75. No se reentrena sobre
validación después de escoger el ganador, por lo que el artefacto evaluado es exactamente
el promovido. Esta es una selección inicial: no se implementa un duelo automatizado
contra un campeón histórico para sucesivos datasets.

## Experimentos y resultados observados

| Versión | C | ROC AUC validación |
|---|---|---|
| 1 | 0.01 | 0.824950 |
| 2 | 0.1 | 0.828838 |
| 3 | 1.0 | 0.830393 |
| 4 | 10.0 | 0.830572 |
| 5 | 100.0 | 0.830559 |

La versión seleccionada fue **4**, C = **10**, run
`03b7addcc4ce4e40954a0b404dccedad`. Su alias es `production`.
En MLflow, las configuraciones son cinco *runs* dentro de un *experimento*, siguiendo
la taxonomía de la clase 5. Si la rúbrica exige cinco objetos Experiment separados,
se deberá ajustar esa organización; no se presume que sean equivalentes.

| Métrica de test | Resultado |
|---|---|
| ROC AUC | 0.835731 |
| F1 con umbral 0,5 | 0.589928 |
| Exactitud | 79.772889% |

El AUC supera la compuerta de 0,75. F1 ≈ 0,59 muestra que el desempeño está lejos de
ser perfecto; no se afirma aptitud comercial a partir de este benchmark. El umbral
0,5 no ha sido optimizado por costos de retención, falsos positivos o pérdida de clientes.

## Arquitectura de puesta en servicio

MLflow almacena metadatos en SQLite y artefactos mediante su servidor HTTP. Para el
laboratorio Kubernetes se utiliza un PVC y una sola réplica de MLflow. Las tres
réplicas FastAPI descargan el modelo desde ese servicio y guardan el objeto en memoria.
Al inicio resuelven el alias y cargan la versión numérica resultante, evitando que la
metadata reportada difiera de la versión realmente cargada si cambia el alias.

El endpoint valida el contrato y devuelve probabilidad, clase, umbral, versión, run e
identidad de proceso/Pod. La web usa fetch con ruta relativa al mismo servidor.
El Service expone NodePort 30080 y MLflow el 30500. El servicio de inferencia incluye
probes de inicio, disponibilidad y vida, además de límites de CPU/memoria.
El alias no se refresca automáticamente dentro de procesos vivos: se requiere rollout.

## Monitoreo y drift

Se usan ventanas independientes: validación como referencia y test como lote actual.
Para variables numéricas se exige p KS < 0,05/3 y distancia KS > 0,1. Para categorías
se utiliza distancia de variación total > 0,15. La compuerta de desempeño se activa
cuando la pérdida logarítmica actual excede la referencia en más de 0,10.
Estos umbrales son explícitos y didácticos; no están calibrados para una operación real.

| Escenario ejecutado | Data drift | Señal de concept drift | Log loss actual | Código |
|---|---|---|---|---|
| Normal, etiquetas reales | No | No | 0,426171 | 0 |
| MonthlyCharges +100, etiquetas conservadas | Sí | No | 0,433883 | 2 |
| Etiquetas invertidas, mismas entradas | No | Sí | 2,075489 | 2 |

La referencia tiene log loss 0,437579. El escenario de etiquetas invertidas es una
simulación controlada de cambio en P(y|X), no un hallazgo en clientes reales. La caída
de desempeño es una señal operativa compatible con concept drift; en producción
no demuestra por sí sola su causa. Se requieren etiquetas reales, análisis y control
de calidad. El desplazamiento de cargos es una perturbación deliberada para demostrar
el detector; no prueba que toda modificación de esa variable preserve P(y|X).
No se reentrena automáticamente con etiquetas manipuladas ni se promociona un modelo
ante una mera alerta. La acción propuesta es investigar y validar datos nuevos.

## Verificación y evidencias

Nueve pruebas pytest pasaron, incluidas carga del Registry, inferencia y rechazos de
entradas inválidas. Se ejecutó además Uvicorn por HTTP: POST /predict devolvió 200,
entrada inválida devolvió 422 y la página HTML devolvió 200. Se confirmó que el
formulario contiene fetch a /predict; su ejecución visual en navegador sobre Kubernetes
queda pendiente. `pip check` no detectó dependencias incompatibles. Se parsearon seis
recursos YAML y se comprobó el campo replicas=3, sin atribuirlo a validación de clúster.

Los scripts locales comprueban balanceo mediante inferencias POST, nuevas conexiones
y conteo por Pod, recuperación mediante UID y estado Ready, y escalamiento 3→5→3.
No basta mostrar un Service. No se exige un reparto idéntico entre Pods y no se usa
port-forward para demostrarlo. Estos scripts no fueron ejecutados en Windows en esta
sesión: sus resultados están pendientes y deben añadirse a la entrega.

## Reproducibilidad, límites y trabajo pendiente

El dataset está versionado con SHA256, los parámetros y semilla se registran, se
incluye un lock completo y un historial Git real. El entorno probado fue Linux con
Python 3.12.14; los Dockerfiles especifican Python 3.12.10, por lo que la construcción
y equivalencia entre entornos todavía requieren prueba en Docker Desktop. El lock
incluye marcadores de plataforma para Gunicorn, que no se instala en Windows.
Las advertencias de deprecación de MLflow/Pydantic observadas no impidieron las pruebas.

La API carece de autenticación; los NodePorts se destinan al laboratorio local. SQLite
y un PVC único no proporcionan alta disponibilidad de MLflow. No se implementan
monitorización continua de negocio, A/B testing, canary ni renovación automática del
modelo: son ampliaciones descritas en las clases, sin asumir obligatoriedad no verificada.
CI está configurado pero no se ha ejecutado en GitHub; el despliegue local se automatiza
mediante PowerShell. No se publicaron imágenes ni un repositorio remoto sin acceso a
la cuenta del estudiante.

Para cerrar la entrega: aportar el enunciado oficial, ejecutar la guía en Windows,
agregar evidencias auténticas, confirmar formato de informe y URL GitHub, identificar
al estudiante y actualizar matriz e informe con resultados del clúster.

## Referencias

IBM. Telco Customer Churn. Repositorio público y archivo de datos citado en DATOS.md.
https://github.com/IBM/telco-customer-churn-on-icp4d

MLflow. Model Registry y Model Registry Workflows. Documentación oficial consultada.
https://mlflow.org/docs/latest/model-registry/
https://www.mlflow.org/docs/latest/ml/model-registry/workflow/

UAGRM. Material del módulo: Clase 5 (MLflow), Clase 6 (automatización CD4ML) y
Clase 7 (monitoreo y drift). Archivos proporcionados por el usuario. Ejemplos:
mlflow.zip, heladeria-ci-cd-ct.zip y drift.zip. Adaptaciones documentadas en MATERIALES.md.
