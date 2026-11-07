# Dataset y contrato

Fuente primaria: IBM, repositorio `telco-customer-churn-on-icp4d`, archivo
`data/Telco-Customer-Churn.csv`, rama master. URL de descarga:
https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv

Se incluye el CSV exacto para reproducibilidad sin descargar datos cambiantes.
SHA256: `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91`.
Este conjunto se usa como benchmark educativo; no representa clientes reales de
una organización específica ni permite estimar su tasa de abandono. Consultar los términos y atribución
del repositorio de origen antes de redistribución comercial.

| Campo | Tipo | Tratamiento |
|---|---|---|
| tenure | Entero, meses | Imputación mediana y escalado |
| MonthlyCharges | Numérico | Imputación mediana y escalado |
| TotalCharges | Numérico, blancos convertidos a NaN | Imputación mediana y escalado |
| Contract | Categórico | One-hot con desconocidos ignorados en pipeline |
| InternetService | Categórico | One-hot |
| PaymentMethod | Categórico | One-hot |
| Churn | Yes/No | Objetivo 1/0; nunca predictor |

El endpoint impone categorías conocidas, valores finitos, rangos y prohíbe campos
extra. El pipeline es tolerante a categorías desconocidas para procesos offline.
El dataset tiene 7.043 filas; particiones estratificadas y semilla 42:
train 4.225, validación 1.409, test 1.409. Los seis campos de entrada excluyen
identificador y objetivo. El límite de nulos permitido por columna es 1%; solo
TotalCharges admite nulos originales. CSV versionado en Git en lugar de DVC, ya
que pesa menos de 1 MB y puede mantenerse junto al código con hash de integridad.
