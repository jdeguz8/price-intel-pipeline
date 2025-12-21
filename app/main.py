from fastapi import FastAPI
from .db import products_table
from .models import ProductCreate, ProductOut, new_product_item
from .db import (
    get_latest_snapshots,
    get_snapshots_last_days,
    get_product_meta,   # 👈 this one
)
from .insights import ProductInsightsOut

app = FastAPI(title="Price Intelligence Pipeline API")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/products", response_model=ProductOut)
def create_product(payload: ProductCreate):
    item = new_product_item(payload)
    products_table().put_item(Item=item)

    return ProductOut(
        product_id=item["product_id"],
        name=item["name"],
        url=item["url"],
        source=item["source"],
        created_at=item["created_at"],
    )

@app.get("/products", response_model=list[ProductOut])
def list_products(limit: int = 25):
    resp = products_table().scan(Limit=limit)
    items = resp.get("Items", [])

    out: list[ProductOut] = []
    for it in items:
        if it.get("sk") != "META":
            continue
        out.append(ProductOut(
            product_id=it["product_id"],
            name=it["name"],
            url=it["url"],
            source=it.get("source", "manual"),
            created_at=it["created_at"],
             last_price=float(it["last_price"]) if it.get("last_price") is not None else None,
            last_checked_at=it.get("last_checked_at"),
            lowest_price_all_time=float(it["lowest_price_all_time"]) if it.get("lowest_price_all_time") is not None else None,
        ))
    return out

@app.get("/products/{product_id}/insights", response_model=ProductInsightsOut)
def product_insights(product_id: str):
    # Read aggregates from META (fast-path)
    meta = get_product_meta(product_id)

    latest_price = None
    latest_ts = None
    lowest_seen_all_time = None

    if meta:
        if meta.get("last_price") is not None:
            latest_price = float(meta["last_price"])
        latest_ts = meta.get("last_checked_at")
        if meta.get("lowest_price_all_time") is not None:
            lowest_seen_all_time = float(meta["lowest_price_all_time"])

    # Fetch last 2 snapshots for delta (cheap)
    latest = get_latest_snapshots(product_id, limit=2)
    prev_item = latest[1] if len(latest) > 1 else None

    previous_price = float(prev_item["price"]) if prev_item else None
    previous_ts = prev_item["timestamp"] if prev_item else None

    change_amount = None
    change_percent = None
    if latest_price is not None and previous_price not in (None, 0):
        change_amount = round(latest_price - previous_price, 2)
        change_percent = round((change_amount / previous_price) * 100, 2)

    # 30-day windowed low (time-based analytics)
    last_30 = get_snapshots_last_days(product_id, days=30, limit=200)
    lowest_seen_30d = min((float(it["price"]) for it in last_30), default=None)

    return ProductInsightsOut(
        product_id=product_id,
        latest_price=latest_price,
        latest_timestamp=latest_ts,
        previous_price=previous_price,
        previous_timestamp=previous_ts,
        change_amount=change_amount,
        change_percent=change_percent,
        lowest_seen_all_time=lowest_seen_all_time,
        lowest_seen_30d=lowest_seen_30d,
        snapshots_count_used=len(latest),
    )
