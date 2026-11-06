# Bitácora de ejecución y decisiones

Sesión: 5 de noviembre de 2026, Bolivia. Todos los comandos se ejecutaron desde
la raíz salvo preparación y OCR. Los logs originales pueden contener rutas Linux
que corresponden al entorno real de esta sesión; no se reemplazaron por rutas ficticias.

| Acción | Resultado observado | Archivo / decisión |
|---|---|---|
| Inventario inicial | Tres PDF y tres ZIP; enunciado recibido después en el chat | ENUNCIADO_OFICIAL.md y matriz oficial |
| pdftotext y OCR de páginas | PDFs basados en imágenes; 55 páginas leídas por OCR | clases-ocr.txt |
| Inspección ZIP sin copiar historia ajena | MLflow C sweep, CI/CD heladería, KS drift | MATERIALES.md |
| Descarga CSV público IBM | 7.043 filas, 21 columnas originales | data/telco.csv y DATOS.md |
| Instalación aislada | MLflow 2.22.2 y sklearn 1.6.1 instalados | requirements-lock.txt |
| Primer inicio MLflow | ImportError FallbackAsyncAdaptedQueuePool con SQLAlchemy 2.1.8 | Corregido a SQLAlchemy 2.0.40 y Alembic 1.15.2 |
| Inicio de servicios en procesos separados | Loopback aislado entre ejecuciones de este entorno | Verificación servidor/cliente en un mismo comando |
| python -m src.train con servidor HTTP | Cinco runs/versions; alias production v4 | training.json y mlflow-official.log |
| pytest -v --junitxml=evidence/pytest.xml | 13 pruebas pasaron en la verificación actual | pytest.log y pytest.xml |
| python -m src.drift normal/data/concept | Códigos 0/2/2; alertas esperadas | drift-exit-codes.txt y JSON |
| uvicorn + python scripts/smoke_http.py | 200 inferencia, 422 inválido, 200 HTML | http-smoke.json, api-http.log |
| python -m pip check | No broken requirements found | pip-check.txt |
| python -m compileall -q src scripts tests | Completado sin error | Verificación sintáctica Python |
| Parseo YAML con PyYAML | Seis recursos, replicas API=3 | No equivale a aplicar Kubernetes |
| Docker/kubectl | Binarios/daemon no disponibles | Ejecutar deploy.ps1 y verify-k8s.ps1 en Windows |
| Publicación GitHub | No ejecutada; sin cuenta/repositorio destino conectado | Comandos en README |

Pendientes: Windows/lock, construcción Docker, despliegue, balanceo POST, recuperación,
escalamiento, navegador y Network, CI remoto, capturas auténticas y defensa en vivo.
Git usa identidad técnica neutral `MLOps Project <project@localhost>` en los commits
creados aquí; el estudiante puede configurar su identidad para sus siguientes cambios.
No se modificaron fechas para simular un proceso histórico.

## Ajustes al recibir el enunciado oficial

- Confirmado: cinco runs son las cinco ejecuciones exigidas.
- Data drift ahora usa train, separado de la referencia de desempeño held-out.
- Añadida prueba chi-cuadrado categórica, Bonferroni para seis comparaciones y justificación de tolerancias.
- Añadidos diez lotes disjuntos, gráfica temporal ROC AUC y alarma por caída >=0,10 durante tres lotes.
- Ejecutados controles temporales: normal=0; alterado=2, primera alarma lote 7.
- Añadido monitoreo de POST durante eliminación de Pod; ejecución del clúster aún pendiente.
- Añadidos tabla individual, identidad run/versión en arquitectura y guía UI de MLflow.
- Se repitió entrenamiento en un Registry limpio (official.db), cinco versiones, alias v4.
- Los logs mlflow-verified.log y mlflow-recheck.log pertenecen a la primera iteración;
  mlflow-official.log y evidencias de entrenamiento/drift/pytest actuales son la referencia vigente.
