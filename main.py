from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import time

from app.database import engine, SessionLocal
from app.models import Base, Transaction


app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# Dependency (forr DB Session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Request Schema
class TransactionWebhook(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str


# Health Check
@app.get("/")
def health_check():
    return {
        "status": "HEALTHY",
        "current_time": datetime.utcnow().isoformat() + "Z"
    }


# Background Processing
def process_transaction(transaction_id: str):
    db = SessionLocal()

    transaction = db.query(Transaction).filter_by(
        transaction_id=transaction_id
    ).first()

    if not transaction:
        db.close()
        return

    # Simulate external API delay
    time.sleep(30)

    transaction.status = "PROCESSED"
    transaction.processed_at = datetime.utcnow()

    db.commit()
    db.close()


# Webhook Endpoint
@app.post("/v1/webhooks/transactions", status_code=202)
def receive_webhook(
    payload: TransactionWebhook,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    transaction = Transaction(
        transaction_id=payload.transaction_id,
        source_account=payload.source_account,
        destination_account=payload.destination_account,
        amount=payload.amount,
        currency=payload.currency,
        status="PROCESSING",
        created_at=datetime.utcnow(),
        processed_at=None
    )

    try:
        db.add(transaction)
        db.commit()
    except IntegrityError:
        db.rollback()
        # Idempotent check
        return {"message": "Transaction already received"}

    background_tasks.add_task(
        process_transaction,
        payload.transaction_id
    )

    return {"message": "Accepted"}


# Query Transaction
@app.get("/v1/transactions/{transaction_id}")
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter_by(
        transaction_id=transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return [{
        "transaction_id": transaction.transaction_id,
        "source_account": transaction.source_account,
        "destination_account": transaction.destination_account,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "status": transaction.status,
        "created_at": transaction.created_at.isoformat() + "Z",
        "processed_at": transaction.processed_at.isoformat() + "Z"
        if transaction.processed_at else None,
    }]