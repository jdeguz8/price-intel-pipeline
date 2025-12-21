from pydantic import BaseModel
from typing import Optional


class ProductInsightsOut(BaseModel):
    product_id: str

    latest_price: Optional[float] = None
    latest_timestamp: Optional[str] = None

    previous_price: Optional[float] = None
    previous_timestamp: Optional[str] = None

    change_amount: Optional[float] = None
    change_percent: Optional[float] = None

    lowest_seen_all_time: Optional[float] = None
    lowest_seen_30d: Optional[float] = None

    snapshots_count_used: int = 0
