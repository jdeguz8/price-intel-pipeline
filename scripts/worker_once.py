import json
import random
import boto3
from datetime import datetime, timezone
from decimal import Decimal

from app.config import settings
from app.db import snapshots_table

def fake_price_fetch(url: str) -> Decimal:
    # DynamoDB needs Decimal, not float
    return Decimal(str(round(random.uniform(10.00, 80.00), 2)))


def main():
    sqs = boto3.client("sqs", region_name=settings.aws_region)

    resp = sqs.receive_message(
        QueueUrl=settings.price_check_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=2,
    )

    messages = resp.get("Messages", [])
    if not messages:
        print("No messages in queue.")
        return

    msg = messages[0]
    body = json.loads(msg["Body"])

    product_id = body["product_id"]
    url = body["url"]

    price = fake_price_fetch(url)
    timestamp = datetime.now(timezone.utc).isoformat()

    item = {
        "pk": f"PRODUCT#{product_id}",
        "sk": f"TS#{timestamp}",
        "product_id": product_id,
        "timestamp": timestamp,
        "price": price,
        "currency": "CAD",
        "source": body.get("source", "manual"),
        "url": url,
    }

    snapshots_table().put_item(Item=item)

    sqs.delete_message(
        QueueUrl=settings.price_check_queue_url,
        ReceiptHandle=msg["ReceiptHandle"],
    )

    print(f"Snapshot written: {product_id} @ ${price}")

if __name__ == "__main__":
    main()
