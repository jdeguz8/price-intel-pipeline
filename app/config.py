from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    aws_region: str = Field(default="ca-central-1", alias="AWS_REGION")
    products_table: str = Field(default="PriceIntel_Products", alias="PRODUCTS_TABLE")
    snapshots_table: str = Field(default="PriceIntel_PriceSnapshots", alias="SNAPSHOTS_TABLE")

    price_check_queue_url: str = Field(alias="PRICE_CHECK_QUEUE_URL")

settings = Settings()
