from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AggregatedMetrics, Stablecoin, Chain
from pydantic import BaseModel


router = APIRouter()


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""

    timestamp: datetime
    total_transfer_volume: float
    transfer_count: int
    stablecoin_symbol: str
    chain_name: str


@router.get("/metrics", response_model=List[MetricsResponse])
async def get_metrics(
    stablecoin: Optional[str] = Query(None, description="Stablecoin symbol"),
    chain: Optional[str] = Query(None, description="Chain name"),
    start_time: Optional[datetime] = Query(None, description="Start timestamp"),
    end_time: Optional[datetime] = Query(None, description="End timestamp"),
    db: Session = Depends(get_db),
):
    """Get aggregated metrics with optional filters."""
    # Start building the query
    query = (
        db.query(AggregatedMetrics)
        .join(Stablecoin, AggregatedMetrics.stablecoin_id == Stablecoin.id)
        .join(Chain, Stablecoin.chain_id == Chain.id)
    )

    # Apply filters
    if stablecoin:
        query = query.filter(Stablecoin.symbol == stablecoin)
    if chain:
        query = query.filter(Chain.name == chain)
    if start_time:
        query = query.filter(AggregatedMetrics.timestamp >= start_time)
    if end_time:
        query = query.filter(AggregatedMetrics.timestamp <= end_time)

    # Order by timestamp descending
    query = query.order_by(AggregatedMetrics.timestamp.desc())

    # Execute query and format results
    results = query.all()
    return [
        MetricsResponse(
            timestamp=metric.timestamp,
            total_transfer_volume=metric.total_transfer_volume,
            transfer_count=metric.transfer_count,
            stablecoin_symbol=metric.stablecoin.symbol,
            chain_name=metric.stablecoin.chain.name,
        )
        for metric in results
    ]
