# Idempotency Key Demo — Prevent Duplicate Orders

A small real-world FastAPI example showing how an **Idempotency-Key** prevents duplicate orders when the same request is retried.

## Problem

A customer clicks **Place Order**. The server creates the order, but the response is lost. The customer retries. Without protection, the backend may create two orders.

## Solution

The client sends a unique key for each logical operation:

```http
POST /orders
Idempotency-Key: checkout-abc-123
```

The server stores the key, request fingerprint and created order. A retry with the same key returns the original order instead of creating another one.

```text
Request 1 -> checkout-abc-123 -> Create Order #1 -> Store key
Request 2 -> checkout-abc-123 -> Already exists -> Return Order #1
```

## What this project demonstrates

- FastAPI order API
- SQLite persistence
- Idempotency record table
- Database UNIQUE constraint on the idempotency key
- Same key + same body returns the original order
- Same key + different body returns `409 Conflict`
- Different key creates a new order
- Retry simulation using `demo_client.py`
- Swagger docs

## Run it

```bash
python -m venv .venv
```

Windows:
```bash
.venv\\Scripts\\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Start:
```bash
uvicorn app.main:app --reload
```

Open Swagger: `http://127.0.0.1:8000/docs`

In another terminal:
```bash
python demo_client.py
```

## Expected behavior

| Scenario | Key | Body | Result |
|---|---|---|---|
| First request | checkout-123 | A | Creates order |
| Retry | checkout-123 | A | Returns original order |
| Changed body | checkout-123 | B | 409 Conflict |
| New operation | checkout-456 | B | Creates new order |

## Why the database constraint matters

The application checks for an existing key, but two requests can arrive concurrently. The database also enforces `UNIQUE(idempotency_key)` so the race cannot silently create two records.

## Production notes

SQLite is used only to keep this demo easy to run. A production implementation may use PostgreSQL, MySQL, Redis or another shared store. Also consider key expiration, payload hashing, atomic transactions, concurrent requests, cleanup and authentication/ownership of keys.

## Real-world use cases

- Payments
- E-commerce orders
- Money transfers
- Bookings
- Ticket reservations
- Subscription creation

> Idempotency does not prevent a request from being sent twice. It makes repeated execution of the same logical operation safe.

**Study/demo project only.**
