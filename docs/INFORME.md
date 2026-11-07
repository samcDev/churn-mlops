# Predicción de abandono de clientes con un flujo MLOps reproducible y observable

Maestría en Ciencia de Datos — UAGRM  
Módulo: MLOps y Puesta en Producción  
Modalidad: individual  
Verificación: 6 de noviembre de 2026, Bolivia  
Estado: entrenamiento, Registry, API, contenedores, Kubernetes y drift comprobados
en Windows 11 con Docker Desktop. Publicación GitHub y empaquetado final por completar.

## 1. Resumen y objetivo

Se implementó un repositorio funcional que lleva un clasificador de abandono desde
el entrenamiento hasta un servicio trazable. El énfasis, conforme al enunciado, es
la reproducibilidad, el empaquetado, la disponibilidad y la detección de degradación,
no alcanzar una exactitud máxima. Se usaron 7.043 registros del benchmark público
IBM Telco y seis predictores. Cinco configuraciones comparables se registraron en
MLflow, con cinco versiones y un alias de producción explícito. FastAPI carga el
modelo por esa referencia, sin archivos de modelo administrados manualmente.

La implementación contiene Dockerfiles propios, manifiestos Kubernetes con tres
réplicas, verificadores de balanceo/autorreparación/escala y una interfaz HTML que
consume la API. Se comprobó el servicio desplegado en Kubernetes mediante inferencias HTTP,
distribución entre Pods, recuperación y escalamiento. Trece pruebas automatizadas
pasaron en Windows. Se ejecutaron escenarios de drift con estados normales y
alertas deliberadas. El informe conserva los límites de cada comprobación.

## 2. Datos y metodología

Fuente: IBM, `telco-customer-churn-on-icp4d`, CSV versionado incluido en el repositorio.
SHA256: `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91`.
Es un benchmark educativo; no permite extrapolar su desempeño a una empresa específica.

Predictores: tenure, MonthlyCharges, TotalCharges, Contract, InternetService y
PaymentMethod. El objetivo Churn se convierte Yes→1, No→0. Se excluye customerID.
Los blancos de TotalCharges se convierten a NaN; el pipeline imputa mediana y
estandariza los números, y aplica one-hot a las categorías. Se ajusta solo con train.
El esquema de la API limita rangos, categorías y valores finitos, y prohíbe campos extra.

La división estratificada usa semilla 42: train=4.225, validación=1.409 y test=1.409.
Las cinco corridas comparten datos, split, algoritmo y preprocesamiento; varían C.
La selección usa ROC AUC de validación, y el test se reserva para evaluar al ganador.
El artefacto seleccionado no se reentrena sobre validación antes de servirlo, de modo
que el modelo evaluado y promovido es el mismo. La compuerta inicial exige AUC test
>=0,75. No se implementa un duelo automático contra un campeón histórico para
promociones sucesivas ni optimización del umbral por costo de negocio.

## 3. Experimentación, registro y trazabilidad

| Versión | C | ROC AUC validación |
|---|---|---|
| 1 | 0.01 | 0.824950 |
| 2 | 0.1 | 0.828838 |
| 3 | 1.0 | 0.830393 |
| 4 | 10.0 | 0.830572 |
| 5 | 100.0 | 0.830559 |

Los cinco runs pertenecen al experimento `telco-churn-individual`. Esto cumple el
requisito oficial de **cinco ejecuciones**, sin necesitar cinco objetos Experiment.
Cada run registra parámetros, métricas, firma, ejemplo, modelo, hash de datos,
commit y hash del script de entrenamiento. MLflow administra la serialización y los artifacts.

Modelo estable: `telco-churn`; alias: `production`; versión: **4**; run:
`049f06a318534d88ab7514bb635396dd`. Esta identidad corresponde al Registry de Kubernetes y a las
respuestas del servicio desplegado. El anexo [DESPLIEGUE.md](DESPLIEGUE.md) y el archivo
`evidence/deployed-model.json` relacionan el modelo con los UIDs y la imagen de los Pods.

| Métrica de test | Resultado |
|---|---|
| ROC AUC | 0.835731 |
| F1, umbral 0,5 | 0.589928 |
| Exactitud | 79.772889% |

El AUC supera la compuerta didáctica; F1≈0,59 impide describir el modelo como perfecto.
La UI de MLflow se comprobó en `http://localhost:30500`: listado de cinco runs,
orden descendente por `val_roc_auc`, comparación de hiperparámetros y versión 4
con alias `production`. Las capturas E02, E03 y E04 documentan ese recorrido.
La demostración oral prevista en el enunciado se evalúa por separado.

## 4. Arquitectura y contenerización

El pipeline registrado es consumido por FastAPI, que resuelve production al iniciar
y carga la versión numérica resultante. La respuesta expone clase, probabilidad,
umbral, versión, run e identidad de Pod. No se gestiona un pickle/joblib suelto.
Cambiar alias requiere renovar los procesos; no se promete cambio atómico entre réplicas.

El contenedor API tiene Dockerfile propio, Python base fijado y lock de dependencias
que incluye MLflow 2.22.2. El CMD inicia Uvicorn; no precisa instalar librerías en el
host. MLflow es un servicio separado con metadatos SQLite y artifacts en PVC,
descargados por HTTP. La provisión inicial entrena/publica el modelo antes de esperar
la API lista. No hay pasos manuales adicionales dentro de cada contenedor de inferencia.
Se construyeron las imágenes `churn-api:1.0.0` y `churn-mlflow:1.0.0` en Docker
Desktop. La imagen de inferencia se ejecutó efectivamente en los Pods. Las
dependencias fijan SQLAlchemy 2.0.40 y Alembic 1.15.2 junto a MLflow 2.22.2.

## 5. Kubernetes y disponibilidad

Deployment API: tres réplicas; Service NodePort 30080, sin afinidad de sesión;
MLflow NodePort 30500; probes startup/readiness/liveness; recursos CPU/memoria.
Se añadió preStop de cinco segundos y grace period de treinta para favorecer drenaje.

Las cuatro demostraciones exigidas se ejecutaron en el clúster local:

1. **Réplicas:** tres Pods `churn-api` simultáneamente `Running` y `Ready 1/1`.
2. **Balanceo:** 120 inferencias al Service, distribuidas 39, 41 y 40 entre tres
   Pods, con cero errores. Todas las respuestas identificaron versión 4, alias
   `production` y el mismo run seleccionado.
3. **Autorreparación:** eliminación del Pod `churn-api-6d6b9cb9c6-clfqv`, UID
   `fe425103-e9c3-4c79-b55b-7e2821af3ecf`. Kubernetes creó
   `churn-api-6d6b9cb9c6-gf85t`, UID `83d2da80-7376-4f2c-b2ea-2d1deaad261b`.
   Se registraron 152 solicitudes, 136 durante eliminación y reemplazo, y cero
   solicitudes fallidas; el estado final fue tres Pods listos. Es una observación
   finita, no una garantía de ausencia absoluta de interrupciones.
4. **Escalamiento:** cambio de tres a cinco réplicas. Se observaron cinco Pods
   listos y 250 inferencias distribuidas en conteos 53, 53, 47, 42 y 55, sin errores.
   Se volvió después a tres réplicas y se esperó a que terminaran las dos sobrantes.

Evidencias: `balance-three.json`, `balance-five.json`, `recovery.json`,
`deployed-model.json` y capturas E07 a E10 en la carpeta `evidence`.

No se usa port-forward para acreditar balanceo, pues puede fijar un backend. No se
exige reparto uniforme. La única réplica MLflow no ofrece alta disponibilidad de
su plano de control: los procesos cargados pueden inferir sin ella, pero nuevos
arranques la requieren. Producción demandaría DB y almacenamiento redundantes,
autenticación y controles operativos adicionales.

## 6. Data drift

Cada una de las seis variables se compara con el **train original de 4.225 filas**.
Numéricas: KS, p<0,05/6 y distancia>0,10. Categóricas: chi-cuadrado de homogeneidad,
p<0,05/6 y variación total>0,15. Se valida que las frecuencias esperadas sean >=5.
KS no impone normalidad; chi-cuadrado compara proporciones sin ordenar categorías.
Bonferroni controla la familia de seis pruebas. Las distancias mínimas reducen
alertas por cambios diminutos en muestras grandes.

0,05 es una convención estadística; las magnitudes 0,10/0,15 son tolerancias didácticas
fijadas previamente, no números derivados de una calibración industrial. Se explican
sus límites y su calibración futura con históricos estables en [MONITOREO.md](MONITOREO.md).
El lote normal pasó y el desplazamiento deliberado de MonthlyCharges +100 activó
la alerta. Hay además una prueba automatizada de perturbación categórica.

## 7. Concept drift y evolución temporal

La referencia de desempeño es validación independiente, AUC=0.830572,
para evitar una referencia optimista calculada sobre train. Test se divide en diez
lotes disjuntos estratificados. El control normal conserva etiquetas; la simulación
concept invierte las etiquetas desde el lote 5, manteniendo las entradas de esos lotes.
El eje temporal es el orden simulado de llegada de lotes, sin inventar fechas reales.

**Regla de alarma/reentrenamiento:** caída absoluta de ROC AUC >=0,10 respecto de
validación durante **tres lotes etiquetados consecutivos**. Una recuperación rompe
la racha. Una etiqueta pendiente pausa la evaluación; no se fabrica una métrica.
La caída elegida es material para el ejercicio y tres ventanas reducen reacción a
ruido aislado. No se afirma significancia estadística ni calibración de negocio.

El escenario normal no disparó alarma. El alterado la disparó en el lote **7**,
tras los lotes 5, 6 y 7 degradados. Resultados por lote, umbrales y alarma están en
CSV y JSON. Las figuras son:

![Control temporal sin alteración](../evidence/temporal-normal.png)

![Concept drift con etiquetas invertidas](../evidence/temporal-concept.png)

Log loss se conserva como señal auxiliar de lote: normal=0,426171, perturbación de
cargos=0,433883 e inversión completa=2,075489; referencia=0,437579. Ese detector de
un lote no sustituye la regla principal sostenida de ROC AUC. La caída de desempeño
es señal compatible con drift, no prueba causal suficiente en una operación real.
La simulación cambia explícitamente P(y|X); no es un hallazgo en clientes reales.

## 8. Retraso de etiquetas y respuesta operativa

En producción, registrar prediction_id, fecha, versión/run y probabilidad, para
conciliar ground truth cuando madure la ventana de churn. Mientras no llegue,
marcar la métrica pendiente y vigilar distribución de entradas, calidad, errores,
latencia y categorías nuevas. Estos proxies no demuestran concept drift. Si el
riesgo lo exige, revisión humana o menor automatización mientras se confirma la causa.

Cuando haya etiquetas suficientes, evaluar cohortes por fecha de predicción, sin
sesgo de observar solo resultados tempranos. Una ventana desconocida no se trata
como saludable. Se prueba la lógica de espera con valores None, pero no se afirma
que esté implementada una cola productiva de conciliación. La alarma solicita
investigación y entrenamiento con datos nuevos válidos; no se reentrena con etiquetas
manipuladas solo para pasar la demostración.

## 9. Verificación, web y entrega

Se ejecutaron **13 pruebas aprobadas**: dataset, versiones/alias, inferencia desde
Registry, entradas inválidas, baseline train, drift numérico/categórico y alarmas
transitorias/sostenidas con etiquetas pendientes. Los procesos drift devolvieron
normal=0 y alterados=2; temporal normal=0 y concept=2. Los estados rojos son fallos
intencionales de la compuerta y éxito de las pruebas del detector.

La interfaz se comprobó en `http://localhost:30080`. Una consulta capturada obtuvo
17,4 % de probabilidad y clasificación de no abandono, con versión 4, alias
`production`, nombre de Pod y run del Registry del clúster. Network mostró
`POST http://localhost:30080/predict` con `200 OK`. La web usa fetch sobre el mismo
origen. El puntaje extra corresponde a la valoración del docente; el informe no
presupone los 15 puntos.

Los registros de pytest con `MLFLOW_TRACKING_URI=http://localhost:30500` verifican
integración con el Registry del clúster. El caso de API de pytest usa TestClient;
las pruebas NodePort y Network son las que acreditan el servicio efectivamente
desplegado. Las advertencias de deprecación no se contabilizan como pruebas fallidas.

## 10. Responsabilidades del trabajo individual

| Componente | Responsable | Evidencia técnica |
|---|---|---|
| Datos y entrenamiento | Estudiante responsable del trabajo individual | Pipeline, cinco runs y training.json |
| Tracking y versionado | Misma responsable | Registry, alias y run asociado |
| API y contenedores | Misma responsable | FastAPI, Dockerfiles e imágenes |
| Despliegue y disponibilidad | Misma responsable | Pods, Service, balanceo, recuperación y escala |
| Drift y pruebas | Misma responsable | Pruebas, JSON, CSV y gráficas temporales |
| Documentación y entrega | Misma responsable | Informe, matriz, capturas y repositorio |

El historial Git conserva los commits reales. El estado de publicación se confirma
mediante `git remote -v` y un push exitoso; aún falta ese paso al corte del informe.
La defensa individual y la demostración oral no se presentan como realizadas ni
como sustituidas automáticamente por documentación.

## 11. Entrega y límites

La entrega se compone del enlace al repositorio Git y un ZIP con código,
documentación y evidencias. El informe con capturas puede incorporarse en Word/PDF;
los archivos JSON, XML, CSV y PNG se conservan como respaldo verificable. El informe
no afirma una ejecución remota de GitHub Actions: el workflow está configurado, pero
su resultado debe comprobarse en la plataforma después de publicar.

El laboratorio usa un clúster local de un nodo. Tres Pods en ese nodo no protegen
contra la caída completa del equipo. MLflow utiliza SQLite y un PVC con una sola
réplica. No se implementan autenticación, un sistema productivo de etiquetas tardías,
CT automático, A/B testing ni promoción continua frente a un campeón histórico.
Estas limitaciones no se confunden con funciones ya demostradas.

## Referencias

- UAGRM. Enunciado oficial del proyecto final del módulo MLOps y Puesta en Producción.
- UAGRM. Diapositivas clases 5, 6 y 7 y proyectos de ejemplo; revisión en [MATERIALES.md](MATERIALES.md).
- IBM. Telco Customer Churn: https://github.com/IBM/telco-customer-churn-on-icp4d
- MLflow. Model Registry: https://mlflow.org/docs/latest/model-registry/
- MLflow. Workflows: https://www.mlflow.org/docs/latest/ml/model-registry/workflow/
