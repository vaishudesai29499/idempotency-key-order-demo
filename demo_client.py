import requests
BASE_URL = "http://127.0.0.1:8000/orders"
payload = {"customer_name":"Vaishnavi","product":"Wireless Headphones","quantity":1,"amount":2499}
key = "checkout-demo-001"
headers = {"Idempotency-Key": key}

def show(label, r):
    print(f"\n{label}\nHTTP {r.status_code}\n{r.json()}")

print("=== Idempotency Key Demo ===")
first = requests.post(BASE_URL, json=payload, headers=headers); show("1. First request", first)
second = requests.post(BASE_URL, json=payload, headers=headers); show("2. Retry with SAME key", second)
if first.ok and second.ok: print(f"\nSame order returned? {first.json()['id'] == second.json()['id']}")
changed = {**payload, "quantity": 2}
third = requests.post(BASE_URL, json=changed, headers=headers); show("3. Same key + DIFFERENT body", third)
fourth = requests.post(BASE_URL, json=changed, headers={"Idempotency-Key":"checkout-demo-002"}); show("4. New key", fourth)
