# Responsabilidades y autoría del trabajo individual

Modalidad: una sola estudiante responsable de comprender, ejecutar, comprobar y
defender el proyecto completo. Completar su identificación académica en el informe
antes de presentarlo. No se presume que el titular de la cuenta sea quien cursa el módulo.

| Componente | Responsable individual | Evidencia de desarrollo |
|---|---|---|
| Datos, limpieza y entrenamiento | Estudiante responsable única, con asistencia de IA | src/common.py, src/train.py; commits y runs |
| MLflow Tracking y Registry | Misma responsable | Alias, versiones, snapshot y logs |
| FastAPI y web | Misma responsable | src/app.py, frontend; pruebas de contrato y HTTP |
| Docker y Kubernetes | Misma responsable | Dockerfiles, k8s, scripts; ejecución local pendiente |
| Drift y pruebas | Misma responsable | src/drift.py, src/temporal.py, tests y evidencias |
| Documentación y defensa | Misma responsable | docs, README, historial Git |

El código y documentación se prepararon con asistencia de ChatGPT. Los commits
creados en este entorno usan una identidad técnica neutral. El historial no simula
contribuciones personales ni fechas pasadas. Las evidencias Linux pertenecen a este
entorno; las de Windows/Kubernetes deben agregarse después de ejecutarlas realmente.
