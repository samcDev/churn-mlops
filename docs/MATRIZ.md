# Matriz provisional de cumplimiento

Base: los 13 requisitos del mensaje del usuario, no una rúbrica oficial disponible.
Estados: V = ejecutado aquí; I/P = implementado, pendiente en Windows; P = pendiente.
No se asignan porcentajes ni puntaje extra sin el enunciado oficial.

| ID | Requisito | Implementación y criterio verificable | Evidencia / estado |
|---|---|---|---|
| 1 | Analizar enunciado y matriz | Matriz trazable; falta archivo oficial | Esta matriz; P de contraste oficial |
| 2 | Revisar clases y ejemplos | Revisión de 55 diapositivas y tres ZIP | MATERIALES.md, clases-ocr.txt; V |
| 3 | Repositorio profesional | src/tests/scripts/k8s/docs/evidence/CI, Git real | Repositorio y bundle; V |
| 4 | Entrenamiento reproducible, cinco experimentos | Cinco configuraciones/runs en un experimento; semilla, split, hash y lock | training.json, training.log; V, confirmar terminología oficial |
| 5 | Varias versiones y alias | Cinco versiones MLflow; v4 con alias production en ejecución incluida | training.json y snapshot Registry; V |
| 6 | FastAPI carga registrado | Resuelve alias y carga versión de Registry; POST predict | pytest.log, http-smoke.json; V |
| 7 | Dockerfile y dependencias | Dos Dockerfiles; lock transitivo; usuario API sin root | I/P: sin daemon Docker aquí |
| 8 | Kubernetes >=3 réplicas y Service | API 3 réplicas, probes, recursos, Service NodePort | stack.yaml; parseo V, despliegue I/P |
| 9 | Balanceo, recuperación y escala | POST a NodePort; >=3/5 Pods; delete y UID nuevo Ready; 3→5→3 | balance.py, verify-k8s.ps1; I/P |
| 10 | Data/concept drift normal/alterado | KS + TV + pérdida logarítmica; umbrales y códigos explícitos | drift-*.json, drift-exit-codes.txt; V |
| 11 | Web real sobre K8s (+15 por confirmar) | Formulario fetch same-origin /predict, expone versión/Pod/run | HTML y HTTP 200 V; navegador sobre K8s I/P |
| 12 | Pruebas, documentación e informe | Nueve pruebas, HTTP real, informe y guía PowerShell | pytest.xml, http-smoke.json, docs; V; evidencias K8s pendientes |
| 13 | Historial individual y defensa | Commits reales, atribución de asistencia, guion | Git, DEFENSA.md; V; publicación remota P |

## Criterios de aceptación locales pendientes

- `deploy.ps1` finaliza con tres Pods Ready y modelo descargado por HTTP desde Registry.
- `verify-k8s.ps1` finaliza sin excepción y los JSON contienen >=3 y >=5 identidades.
- `recovery.json` prueba UID distinto, Ready y tres réplicas recuperadas.
- Captura auténtica de la web y Network demuestra POST a localhost:30080/predict.
- URL GitHub real, workflow CI verde y ZIP actualizado con evidencias personales.
- Contrastar cada punto y formato de entrega contra el enunciado oficial faltante.
