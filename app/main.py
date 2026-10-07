import hashlib, json
from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import IdempotencyRecord, Order
from .schemas import OrderCreate, OrderResponse
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Idempotency Key Order Demo", description="Prevents duplicate orders on retries.", version="1.0.0")

def request_hash(payload: OrderCreate) -> str:
    encoded = json.dumps(payload.model_dump(), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()

@app.get("/")
def health_check(): return {"service":"Idempotency Key Order Demo","status":"running","docs":"/docs"}

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), db: Session = Depends(get_db)):
    if not idempotency_key: raise HTTPException(400, "Idempotency-Key header is required.")
    if len(idempotency_key) > 255: raise HTTPException(400, "Idempotency-Key is too long.")
    current_hash = request_hash(payload)
    existing = db.query(IdempotencyRecord).filter(IdempotencyRecord.idempotency_key == idempotency_key).first()
    if existing:
        if existing.request_hash != current_hash:
            raise HTTPException(409, "This Idempotency-Key was already used with a different request body.")
        original_order = db.get(Order, existing.order_id)
        if original_order is None: raise HTTPException(500, "Original order was not found.")
        return original_order
    order = Order(customer_name=payload.customer_name, product=payload.product, quantity=payload.quantity, amount=payload.amount, status="confirmed")
    db.add(order); db.flush()
    db.add(IdempotencyRecord(idempotency_key=idempotency_key, request_hash=current_hash, order_id=order.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(IdempotencyRecord).filter(IdempotencyRecord.idempotency_key == idempotency_key).first()
        if not existing: raise HTTPException(409, "Concurrent idempotency conflict. Please retry.")
        if existing.request_hash != current_hash: raise HTTPException(409, "Idempotency-Key was reused with a different request body.")
        return db.get(Order, existing.order_id)
    db.refresh(order)
    return order

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, "Order not found.")
    return order
