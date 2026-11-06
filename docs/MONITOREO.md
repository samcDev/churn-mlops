# Monitoreo, umbrales y retraso de etiquetas

## Referencias separadas

- **Data drift:** `reference.csv`, las 4.225 filas de entrenamiento, compara las seis entradas.
- **Desempeño:** `performance-reference.csv`, validación independiente de 1.409 filas.
  Evita usar el rendimiento dentro de entrenamiento como referencia optimista.
- **Lote actual:** `current.csv`, test de 1.409 filas. La demostración temporal lo divide
  en diez lotes disjuntos estratificados. Cada fila aparece en un solo lote.

## Elección de pruebas y umbrales

| Tipo | Prueba y condición de alerta | Justificación |
|---|---|---|
| Numéricas | KS con p < 0.05/6 y distancia > 0.10 | Compara CDF sin asumir normalidad; distancia descarta cambios estadísticamente significativos pero muy pequeños |
| Categóricas | Chi-cuadrado de homogeneidad con p < 0.05/6 y TV > 0.15 | Compara proporciones sin asignar orden artificial a categorías; TV expresa el tamaño del cambio |

0,05 es una convención de significancia, no una garantía de error cero. Bonferroni
divide entre las seis pruebas para controlar la familia de comparaciones. KS>0,10
exige una separación mínima de diez puntos porcentuales entre CDF. TV>0,15 exige
al menos quince puntos porcentuales de masa de probabilidad redistribuida.
Esas magnitudes son **tolerancias de ingeniería didácticas fijadas previamente**;
no provienen de una calibración industrial ni de un análisis económico. En producción
se calibrarían con ventanas históricas estables, estacionalidad, volumen y costo de alertas.
Chi-cuadrado exige frecuencias esperadas >=5: se verifica y, si no se cumple, el código
rechaza el lote para revisión/agrupación de categorías o una prueba por permutaciones.
Los umbrales no se ajustaron para convertir estos resultados específicos en verde.

## Alarma sostenida de concept drift

La métrica principal es ROC AUC, la misma empleada al seleccionar el modelo.
Baseline de validación: **0.830572**. Umbral: **0.730572**.
La alarma de revisión/reentrenamiento exige caída absoluta >=0,10 en **tres lotes
etiquetados consecutivos**. Una recuperación por encima del umbral reinicia la racha.
La reducción de diez puntos de AUC es material para la práctica, y la persistencia
de tres ventanas evita reaccionar a un lote aislado. Son decisiones explícitas y
ajustables: no una demostración de significancia estadística de la caída del AUC.

El escenario normal no altera etiquetas. El escenario concept invierte etiquetas
de los lotes 5–10: cambia P(y|X), no las entradas de cada lote. En esta ejecución,
la alarma ocurrió en el lote **7**. El eje X es orden de lotes
en tiempo simulado; no se inventan fechas ni registros históricos de clientes.

`src.drift` conserva log loss como señal auxiliar de un lote (aumento >0,10).
**No es la regla sostenida de reentrenamiento**: esa regla está en `src.temporal`.
Las simulaciones son pruebas controladas, no evidencia de deriva observada en negocios reales.
No se entrena automáticamente con etiquetas deliberadamente manipuladas.

## ¿Qué hacer mientras no llegan las etiquetas?

1. Guardar cada inferencia con prediction_id, fecha, versión/run, probabilidad y una
   referencia segura al registro de entrada; no confundir probabilidad con etiqueta.
2. Vigilar drift de entradas, faltantes, categorías nuevas, errores y latencia. Estas
   señales son proxies y no prueban que P(y|X) haya cambiado.
3. Conciliar etiquetas reales cuando madure la ventana de abandono, por prediction_id.
   Evaluar ventanas por cohorte/fecha de predicción para evitar sesgo por etiquetas tempranas.
4. Mientras no haya etiquetas, marcar métrica como pendiente, sin calcular AUC con
   etiquetas inventadas ni dar el modelo por sano. Si el riesgo exige acción, revisión
   humana, reglas de respaldo o reducción de automatización.
5. Con etiquetas suficientes y ambas clases, evaluar la racha. En el controlador
   implementado, un valor `None` pausa la racha sin fabricar observaciones. La regla
   se interpreta como tres lotes evaluados consecutivos; una ventana aún sin etiquetas
   debe evaluarse cuando madure. En producción también habría caducidad por edad de evidencia.

La lógica de etiquetas pendientes está probada. La cola persistente y conciliación de
etiquetas se describen como diseño operativo; no se afirma que exista una plataforma
de telemetría de producción implementada.

## Estados reproducibles

```powershell
python -m src.drift normal       # 0: verde
python -m src.drift data         # 2: rojo esperado por data drift
python -m src.drift concept      # 2: rojo de señal auxiliar
python -m src.temporal normal    # 0: verde, sin alarma sostenida
python -m src.temporal concept   # 2: rojo, tres lotes con caída de AUC
```

Los códigos 2 se convierten en fallo real del proceso/compuerta. El wrapper PowerShell
y CI verifican esos códigos esperados para que la prueba del detector pase sin ocultar
un fallo inesperado. Evidencias: JSON, CSV, log, códigos y gráficas PNG en `evidence/`.
