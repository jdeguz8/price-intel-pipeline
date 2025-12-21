import json
import boto3
from datetime import datetime, timezone

from app.config import settings
from app.db import products_table

def main():
    sqs = boto3.client("sqs", region_name=settings.aws_region)

    resp = products_table().scan(Limit=50)
    products = [
        it for it in resp.get("Items", [])
        if it.get("sk") == "META" and it.get("active") is True
    ]

    if not products:
        print("No active products found.")
        return

    now = datetime.now(timezone.utc).isoformat()

    for p in products:
        event = {
            "event_type": "price_check_requested",
            "requested_at": now,
            "product_id": p["product_id"],
            "url": p["url"],
            "source": p.get("source", "manual"),
        }

        sqs.send_message(
            QueueUrl=settings.price_check_queue_url,
            MessageBody=json.dumps(event),
        )

    print(f"Enqueued {len(products)} price-check job(s).")

if __name__ == "__main__":
    main()
