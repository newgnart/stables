"""FastAPI application."""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.models import Circulating
from config.settings import API_PREFIX, API_VERSION, API_TITLE, API_DESCRIPTION
from config.logging import setup_logging

logger = setup_logging()

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
)


@app.get(f"{API_PREFIX}/supply")
async def get_supply_data(
    symbol: str = None,
    chain: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get circulating supply data."""
    query = db.query(Circulating)

    if symbol:
        query = query.filter(Circulating.symbol == symbol)
    if chain:
        query = query.filter(Circulating.chain == chain)

    results = query.order_by(Circulating.timestamp.desc()).limit(limit).all()
    return results
