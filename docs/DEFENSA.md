# Guion de defensa y demostraciones en vivo

1. Abrir README y explicar objetivo: reproducibilidad, disponibilidad y degradación;
   la exactitud del clasificador es secundaria a la ingeniería del ciclo de vida.
2. Datos: IBM Telco, 7.043 registros, seis entradas, limpieza de TotalCharges, hash,
   partición estratificada 60/20/20. Explicar por qué la imputación se ajusta solo con train.
3. Abrir http://localhost:30500 y el experimento `telco-churn-individual`.
   Cada run representa un valor diferente de C sobre exactamente el mismo split.
4. En la lista de runs, filtrar `metrics.val_roc_auc > 0.82` y ordenar val_roc_auc
   descendente. Seleccionar varios runs (casillas) y abrir Compare. Comparar C,
   ROC AUC y F1. El mayor ROC AUC de validación decide; el test no selecciona C.
5. Abrir Models / telco-churn: versiones, alias production, run asociado. Comparar
   con http://localhost:30080/model y docs/DESPLIEGUE_REAL.md. Mostrar linaje exacto.
6. Explicar Dockerfile propio, lock, arranque automático y Registry HTTP. Mostrar
   que la imagen no necesita librerías Python instaladas en Windows para inferir.
7. Mostrar tres Pods Running/Ready; ejecutar balance.py. Explicar nuevas conexiones
   al Service y conteo real por Pod, sin port-forward ni reparto uniforme obligatorio.
8. Ejecutar recovery.py: observar delete y POST durante la sustitución; mostrar
   UIDs distintos, cero fallos muestreados y nuevo Pod Ready. No ocultar errores.
9. Escalar a cinco, esperar rollout y mostrar cinco identidades respondiendo;
   volver a tres. verify-k8s.ps1 automatiza las cuatro demostraciones exigidas.
10. Ejecutar run-drift.ps1. Explicar baseline train, KS para números y chi-cuadrado
    para categorías, corrección múltiple y tamaño práctico del efecto.
11. Mostrar temporal-normal.png y temporal-concept.png: métrica principal ROC AUC,
    diez lotes disjuntos, inversión desde lote 5 y alarma en lote 7. Explicar caída
    de 0,10 durante tres lotes y por qué una anomalía aislada no dispara reentrenamiento.
12. Etiquetas retrasadas: no se conoce el AUC todavía; vigilar datos e infraestructura,
    conciliar ground truth cuando madure y evaluar cohortes sin inventar etiquetas.
13. Solo con el proyecto base completo: abrir http://localhost:30080, predecir y
    mostrar Network → POST /predict al Service Kubernetes. La respuesta muestra Pod/run/versión.
14. Explicar límites: benchmark educativo, alarmas didácticas, SQLite local,
    sin autenticación, ausencia de CT automático y CI remoto pendiente de ejecutar.

Preguntas que debes poder responder: ¿run vs versión vs alias? ¿por qué resolver
alias al inicio? ¿qué ocurre si cae MLflow? ¿qué garantiza readiness? ¿por qué
Service no prueba balanceo? ¿puede haber concept drift sin data drift? ¿qué hace
la alarma cuando faltan etiquetas? ¿qué cambia al entrenar otra vez?

Trabajo individual asistido por IA: revisar y comprender todos los archivos.
El historial y las evidencias registran lo que realmente se construyó y ejecutó.
