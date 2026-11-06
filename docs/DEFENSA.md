# Guion de defensa individual

1. Problema: priorizar retención; la probabilidad no demuestra causalidad ni garantiza abandono.
2. Datos: 7.043 clientes, seis predictores, target Churn, fuente IBM y hash de integridad.
3. Evitar fuga: split estratificado 60/20/20; imputación y escalado entrenados solo con train.
4. Diferenciar experimento, run, artefacto, versión y alias. Mostrar cinco corridas y ganador.
5. Explicar selección por validación y evaluación de test; leer métricas reales del JSON.
6. Mostrar API cargando Registry y reportando versión/run/Pod. Cambiar alias no cambia un proceso vivo.
7. Mostrar tres Pods y conteo real por NodePort. Service por sí solo no acredita balanceo.
8. Eliminar Pod y comparar UID; escalar a cinco y comprobar recepción por cinco identidades.
9. Drift: P(X) frente a P(y|X), etiquetas retrasadas, umbrales y códigos 0/2.
10. Mostrar formulario y solicitud POST real. Explicar límites: local, sin autenticación,
    simulaciones controladas, CI remoto pendiente y rúbrica oficial pendiente.

El historial registra el desarrollo real asistido por IA. Revisar cada archivo y poder
explicar las decisiones es indispensable para una defensa individual. No atribuir como
propias pruebas que todavía figuren pendientes.
