from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime, timezone
import uuid


class ProductCreate(BaseModel):
    name: str
    url: HttpUrl
    source: Optional[str] = "manual"


class ProductOut(BaseModel):
    product_id: str
    name: str
    url: str
    source: str
    created_at: str
    last_price: float | None = None
    last_checked_at: str | None = None
    lowest_price_all_time: float | None = None


def new_product_item(data: ProductCreate) -> dict:
    product_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    return {
        "pk": f"PRODUCT#{product_id}",
        "sk": "META",
        "product_id": product_id,
        "name": data.name,
        "url": str(data.url),
        "source": data.source or "manual",
        "created_at": created_at,
        "active": True,
    }
