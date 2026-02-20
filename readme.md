# Transaction Webhook Processing Service

This project is a simple backend service built using FastAPI to receive transaction webhooks, process them asynchronously, and store the results.

It simulates how real payment processors (like Razorpay) send transaction events and how a backend system handles them in a reliable way.

---
## Hosted url: [wallnutfoks-assesment-production.up.railway.app](https://wallnutfoks-assesment-production.up.railway.app/)

---
## Postman collection included in the project: [PostmanCollection](/Transactoins%20collection.postman_collection.json)

## Tech Stack

- Python 3.9+
- FastAPI
- SQLAlchemy
- SQLite
- Uvicorn

---

## Project Structure

```
app/
    ├── models.py    # Database models
    ├── database.py  # Database configuration
├── main.py      # API routes and background processing
```

---

## How to Run the Service

### 1. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Server

From project root directory:

```bash
uvicorn app.main:app --reload
```

Server will start at: `http://127.0.0.1:8000`

---

## How to Test the APIs

### 1. Health Check

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{
  "status": "HEALTHY",
  "current_time": "2026-02-20T10:30:00Z"
}
```

### 2. Send Webhook Request

```bash
curl -X POST http://127.0.0.1:8000/v1/webhooks/transactions \
-H "Content-Type: application/json" \
-d '{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500,
  "currency": "INR"
}'
```

Expected response:

```json
{
  "message": "Accepted"
}
```

Status code will be `202 Accepted`. This request returns immediately and processing happens in the background.

### 3. Check Transaction Status

```bash
curl http://127.0.0.1:8000/v1/transactions/txn_abc123def456
```

- **Before 30 seconds:** Status will be `PROCESSING`
- **After 30 seconds:** Status will change to `PROCESSED`

### 4. Test Idempotency

Send the same webhook again with the same `transaction_id`.

Expected response:

```json
{
  "message": "Transaction already received"
}
```

Duplicate transactions will not be processed again.

---

## Technical Design Decisions

### 1. FastAPI

FastAPI is used because it is lightweight, fast, and easy to build REST APIs with validation using Pydantic. It also supports background tasks natively, which is useful for this assignment.

### 2. Background Processing

FastAPI `BackgroundTasks` is used to process transactions asynchronously. This ensures that the webhook endpoint responds within 500ms and does not wait for long processing. A `time.sleep(30)` is used to simulate external API delay.

In real production systems, a proper job queue like Celery or Kafka should be used.

### 3. Database

SQLite is used for simplicity and quick setup. It stores all transaction data persistently in a local file. For real systems, PostgreSQL or MySQL would be more suitable.

### 4. Idempotency Handling

`transaction_id` is used as the primary key in the database. This ensures that duplicate webhook requests with the same `transaction_id` are ignored. SQLAlchemy `IntegrityError` is used to catch duplicate inserts.

### 5. Error Handling

Basic error handling is added for:
- Duplicate transactions
- Missing transactions
- Database rollback

More advanced retry and monitoring can be added in production.

---
