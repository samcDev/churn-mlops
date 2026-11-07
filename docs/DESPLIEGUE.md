# Anexo de arquitectura: despliegue real

Modelo `telco-churn`, alias `production`, versión **4**, run `049f06a318534d88ab7514bb635396dd`.

Service NodePort: http://localhost:30080; Registry: http://localhost:30500.

| Pod | UID | Imagen | Ready |
|---|---|---|---|
| churn-api-6d6b9cb9c6-czswd | 8c56e49e-d113-4295-ba3f-c551222e0a9f | docker-pullable://churn-api@sha256:98905291cda2b81326da3ebbaa1a504bd8c227a06629bc404ef43db3099e8660 | True |
| churn-api-6d6b9cb9c6-gf85t | 83d2da80-7376-4f2c-b2ea-2d1deaad261b | docker-pullable://churn-api@sha256:98905291cda2b81326da3ebbaa1a504bd8c227a06629bc404ef43db3099e8660 | True |
| churn-api-6d6b9cb9c6-vpxnx | 8d5a9f56-f4b9-4036-bed5-42d6f0e087b5 | docker-pullable://churn-api@sha256:98905291cda2b81326da3ebbaa1a504bd8c227a06629bc404ef43db3099e8660 | True |
