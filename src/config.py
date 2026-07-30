"""Configuration du scraper, lue depuis les variables d'environnement (.env)."""
from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    base_url: str
    max_items: int
    request_delay_seconds: float
    user_agent: str
    output_jsonl_path: str
    raw_dir: str


def load_config() -> Config:
    return Config(
        base_url=os.getenv("TARGET_URL", "https://ecommerce-playground.lambdatest.io/"),
        max_items=int(os.getenv("MAX_ITEMS", "60")),
        request_delay_seconds=float(os.getenv("REQUEST_DELAY_SECONDS", "1")),
        user_agent=os.getenv("USER_AGENT", "IPSII-scraping-lab/1.0"),
        output_jsonl_path=os.getenv("OUTPUT_JSONL_PATH", "data/staging/products.jsonl"),
        raw_dir=os.getenv("RAW_DIR", "data/raw"),
    )
