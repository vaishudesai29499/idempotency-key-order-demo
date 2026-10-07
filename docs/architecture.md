# Architecture Flow

```text
Client -> POST /orders + Idempotency-Key -> FastAPI
                                           |
                              Check idempotency key
                                /                \
                           Not found            Found
                              |                   |
                         Create order       Return original
                              |                   |
                              +------> SQLite DB
                                      orders + idempotency_records
```
