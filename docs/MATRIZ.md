# Matriz de cumplimiento del enunciado oficial

Fuente: enunciado del proyecto final del módulo MLOps y Puesta en Producción UAGRM.
V = verificado en Windows o en el clúster local. D = diseño documentado.
P = pendiente. No se asigna puntaje ni se presume sustitución de la defensa oral.

| Cláusula | Requisito | Implementación y evidencia | Estado |
|---|---|---|---|
| 2 | Trabajo individual y reparto | Tabla de responsabilidades en INFORME.md | Documentado |
| 2 | Historial Git | Commits locales conservados; publicación remota por completar | V local y P publicación |
| 2 | Defensa individual | No realizada; instancia de evaluación según el docente | P |
| 3.1 | Dataset y varias entradas | IBM Telco; 7.043 registros y seis predictores | V |
| 3.2 | Reproducibilidad | Semilla 42; split 60/20/20; Pipeline y hash | V |
| 3.2 | Cinco ejecuciones comparables | C=0.01, 0.1, 1, 10 y 100 sobre el mismo split | V |
| 3.3 | Ciclo de experimentación MLflow | Parámetros, métricas, firma y modelo registrados | V |
| 3.3.2 | Nombre estable y varias versiones | telco-churn; versiones 1 a 5 | V |
| 3.3.2 | Referencia explícita de producción | Alias production a versión 4; API resuelve alias al iniciar | V |
| 3.3.2 | Linaje del servicio | Run 049f06a318534d88ab7514bb635396dd; ARQUITECTURA.md y DESPLIEGUE.md | V |
| 3.4 | UI y comparación | Capturas de cinco runs, comparación de C y ROC AUC, Registry y run origen | V recorrido; presentación oral P |
| 4 | Dockerfile propio y dependencias fijadas | Dockerfile, Dockerfile.mlflow y requirements-lock.txt | V construcción |
| 4 | Inferencia en contenedor | Imagen churn-api:1.0.0 ejecutada en los Pods; carga Registry automática | V |
| 5.2 | Tres réplicas simultáneas | Tres Pods Running y Ready 1/1 | V |
| 5.2 | Balanceo por Service | 120 POST; conteos 39, 41 y 40; cero errores | V |
| 5.2 | Recuperación con servicio disponible | Nuevo UID; tres Ready; 152 solicitudes, 136 durante sustitución; cero fallos observados | V ventana muestreada |
| 5.2 | Escalamiento | 3 a 5 a 3; 250 POST atendidos por cinco Pods sin errores | V |
| 6.1 | Cada entrada contra train | Seis variables y baseline de 4.225 filas | V |
| 6.1 | Prueba por tipo y justificación | KS; chi cuadrado con TV; umbrales explicados en MONITOREO.md | V |
| 6.1 | Verde y rojo deliberado | Normal=0; perturbación de datos=2 | V |
| 6.2 | Cambio de relación entrada objetivo | Inversión de etiquetas desde lote 5 | V simulación |
| 6.2 | Lotes y gráfica temporal | Diez lotes disjuntos; ROC AUC en CSV, JSON y PNG | V |
| 6.2 | Criterio sostenido | Caída AUC de 0.10 por tres lotes; primera alarma lote 7 | V |
| 6.2 | Retraso de etiquetas | Lógica de espera probada; conciliación productiva descrita, no implementada | V lógica y D operación |
| 7 | Web consume API de Kubernetes | localhost:30080, POST /predict, 200 OK, identidad Pod versión y run | V funcionamiento; puntaje a criterio docente |
| Entrega | Enlace Git y ZIP con documentación y evidencia | Código, documentos y evidencia local disponibles; preparar versión final y publicar | P cierre |

Las pruebas técnicas de Docker, Kubernetes, API y drift están ejecutadas. Permanecen
pendientes la publicación, el empaquetado final y la instancia oral prevista en el
enunciado. El funcionamiento de la web acredita el consumo requerido para el extra;
no concede automáticamente una calificación.
