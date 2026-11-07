# Revisión y adaptación de materiales

Se inspeccionaron los tres ZIP y se extrajo por OCR el contenido de las 55 diapositivas
(Clase 5: 18; Clase 6: 21; Clase 7: 16). El OCR contiene errores de reconocimiento;
no reemplaza los originales. La matriz de cumplimiento se contrasta con el enunciado oficial publicado para el módulo.

| Fuente | Uso en esta implementación | Ajuste necesario |
|---|---|---|
| Clase 5, diap. 5–7, 11, 13, 15–18 | Experimento/runs, firma, artifacts, versiones y alias | Carga real desde Registry, resolución a versión inmutable |
| `mlflow/entrenar2.py` | Barrido de cinco valores de C y logging | Churn en lugar de Iris, split train/validation/test, Registry |
| Clase 6, diap. 5–12, 14, 20–21 | Pruebas, compuerta de calidad, Docker y FastAPI | Dependencias fijadas y workflow CI; CD local explícito |
| `heladeria-ci-cd-ct` | Organización API/web/tests y CI | Se descarta modelo JSON manual y no se copia su `.git` |
| Clase 7, diap. 5–11 | Monitoreo técnico, datos y desempeño, etiquetas tardías | KS y chi cuadrado, log loss auxiliar y alarma temporal ROC AUC |
| `drift/clase_drift.ipynb` | Separar cambio de entradas de cambio en relación X→y | Escenarios normal, desplazamiento y etiquetas invertidas |

No se copiaron caches, identidades, historial Git, rutas personales ni modelos de los ejemplos.
No se adoptaron sus versiones de dependencias sin comprobarlas. La instalación inicial
resolvió SQLAlchemy 2.1.8 incompatible con MLflow 2.22.2; se corrigió a 2.0.40 y
Alembic 1.15.2. El lock recoge la instalación corregida.

Referencias primarias consultadas:
- https://mlflow.org/docs/latest/model-registry/
- https://www.mlflow.org/docs/latest/ml/model-registry/workflow/
- https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv
