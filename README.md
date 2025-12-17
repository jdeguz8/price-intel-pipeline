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

## Run Locally
```bash
uvicorn app.main:app --reload
