# Price Intelligence Pipeline

A serverless, event-driven backend that tracks product prices over time,
detects drops and new lows, and sends alerts.

## Tech Stack
- Python 3.12
- FastAPI
- AWS DynamoDB
- AWS Lambda (next milestone)
- EventBridge / SQS (next milestone)

## Current Features (Milestone 1)
- Add products to track
- List tracked products
- DynamoDB single-table design

## Analytics (Milestone 2)

Price snapshots are written as immutable time-series events.  
On write, the system maintains aggregates on the Product META record:

- `last_price`
- `last_checked_at`
- `lowest_price_all_time`

This enables O(1) reads for headline metrics while preserving full history
for time-window analytics (e.g., 30-day low).

The API exposes:
- `/products` — configuration + headline aggregates
- `/products/{id}/insights` — derived analytics (change %, windowed lows)

**Flow:** Scheduler → SQS → Lambda → DynamoDB (Snapshots + META aggregates)

## Alerts (SNS)

The worker publishes SNS email alerts when:
- a new all-time low is detected (atomic DynamoDB conditional update)
- a price drop exceeds a configurable threshold

This keeps reads cheap (aggregates stored on Product META) and ensures alerts are reliable and idempotent.


## Run Locally
```bash
uvicorn app.main:app --reload

