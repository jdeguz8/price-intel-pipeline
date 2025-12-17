from fastapi import FastAPI
from .db import products_table
from .models import ProductCreate, ProductOut, new_product_item

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
        ))
    return out
