"""Service for handling stablecoin supply data from DeFiLlama."""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Stablecoin, Chain, AggregatedMetrics
from app.data_sources.defillama_client import DeFiLlamaClient
import logging

logger = logging.getLogger(__name__)


class SupplyService:
    """Service for managing stablecoin supply data."""

    def __init__(self, db: Session):
        self.db = db
        self.defillama_client = DeFiLlamaClient()

    async def collect_supply_data(self) -> None:
        """Collect supply data for all stablecoins and chains."""
        try:
            # Get all stablecoins and their chain data
            chain_data = await self.defillama_client.get_stablecoin_chain_data()

            for record in chain_data:
                # Get or create stablecoin
                stablecoin = (
                    self.db.query(Stablecoin)
                    .filter(Stablecoin.symbol == record["symbol"])
                    .first()
                )

                if not stablecoin:
                    logger.warning(
                        f"Stablecoin {record['symbol']} not found in database"
                    )
                    continue

                # Get or create chain
                chain = (
                    self.db.query(Chain).filter(Chain.name == record["chain"]).first()
                )

                if not chain:
                    logger.warning(f"Chain {record['chain']} not found in database")
                    continue

                # Create or update metrics
                metrics = AggregatedMetrics(
                    stablecoin_id=stablecoin.id,
                    chain_id=chain.id,
                    timestamp=datetime.utcnow(),
                    circulating_supply=record["current"],
                    supply_change_24h=record["current"] - record["prevDay"],
                    supply_change_7d=record["current"] - record["prevWeek"],
                    supply_change_30d=record["current"] - record["prevMonth"],
                )

                # Check if metrics exist for this hour
                existing_metrics = (
                    self.db.query(AggregatedMetrics)
                    .filter(
                        AggregatedMetrics.stablecoin_id == stablecoin.id,
                        AggregatedMetrics.chain_id == chain.id,
                        AggregatedMetrics.timestamp == metrics.timestamp,
                    )
                    .first()
                )

                if existing_metrics:
                    # Update existing metrics
                    existing_metrics.circulating_supply = metrics.circulating_supply
                    existing_metrics.supply_change_24h = metrics.supply_change_24h
                    existing_metrics.supply_change_7d = metrics.supply_change_7d
                    existing_metrics.supply_change_30d = metrics.supply_change_30d
                else:
                    # Add new metrics
                    self.db.add(metrics)

            self.db.commit()
            logger.info("Successfully collected and stored supply data")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error collecting supply data: {str(e)}")
            raise

    async def close(self) -> None:
        """Close the DeFiLlama client session."""
        await self.defillama_client.close()
