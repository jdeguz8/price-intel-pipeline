import boto3
from .config import settings
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone, timedelta
from decimal import Decimal


def dynamodb_resource():
    return boto3.resource("dynamodb", region_name=settings.aws_region)


def products_table():
    return dynamodb_resource().Table(settings.products_table)

def snapshots_table():
    return dynamodb_resource().Table(settings.snapshots_table)


def _to_float(n) -> float | None:
    if n is None:
        return None
    if isinstance(n, Decimal):
        return float(n)
    return float(n)


def get_latest_snapshots(product_id: str, limit: int = 50) -> list[dict]:
    """
    Get most recent snapshots for a product (newest first).
    """
    pk = f"PRODUCT#{product_id}"
    resp = snapshots_table().query(
        KeyConditionExpression=Key("pk").eq(pk) & Key("sk").begins_with("TS#"),
        ScanIndexForward=False,  # newest first
        Limit=limit,
    )
    return resp.get("Items", [])


def get_snapshots_last_days(product_id: str, days: int = 30, limit: int = 200) -> list[dict]:
    """
    Get snapshots in the last N days using sort-key range.
    """
    pk = f"PRODUCT#{product_id}"
    start = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    end = datetime.now(timezone.utc).isoformat()

    resp = snapshots_table().query(
        KeyConditionExpression=Key("pk").eq(pk) & Key("sk").between(f"TS#{start}", f"TS#{end}"),
        ScanIndexForward=True,  # oldest->newest (doesn't matter much here)
        Limit=limit,
    )
    return resp.get("Items", [])

def get_product_meta(product_id: str) -> dict | None:
    resp = products_table().get_item(
        Key={"pk": f"PRODUCT#{product_id}", "sk": "META"}
    )
    return resp.get("Item")
