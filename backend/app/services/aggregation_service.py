from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import Stablecoin, Chain, AggregatedMetrics
from app.blockchain.alchemy_client import AlchemyClient
from app.metrics_processor import MetricsProcessor
import os


class AggregationService:
    """Service for aggregating transfer metrics."""

    def __init__(self, db: Session, alchemy_client: AlchemyClient = None):
        self.db = db
        self.alchemy_client = alchemy_client or AlchemyClient(
            api_key=os.getenv("ALCHEMY_API_KEY")
        )

    def aggregate_hourly_metrics(self) -> None:
        """Aggregate transfer metrics for the last hour for all stablecoins."""
        # Get all stablecoins
        stablecoins = self.db.query(Stablecoin).all()

        # Calculate time range (last hour)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)

        for stablecoin in stablecoins:
            # Get transfer events for the last hour
            events = self.alchemy_client.get_token_transfers(
                chain=stablecoin.chain.name,
                contract_address=stablecoin.contract_address,
                from_block=start_time,
                to_block=end_time,
            )

            # Process events to get metrics
            metrics = MetricsProcessor.process_transfer_events(
                events=events,
                decimals=stablecoin.decimals,
            )

            # Create or update aggregated metrics
            aggregated_metrics = AggregatedMetrics(
                stablecoin_id=stablecoin.id,
                timestamp=start_time,
                total_transfer_volume=metrics["total_transfer_volume"],
                transfer_count=metrics["transfer_count"],
            )

            # Check if metrics already exist for this hour
            existing_metrics = (
                self.db.query(AggregatedMetrics)
                .filter(
                    AggregatedMetrics.stablecoin_id == stablecoin.id,
                    AggregatedMetrics.timestamp == start_time,
                )
                .first()
            )

            if existing_metrics:
                # Update existing metrics
                existing_metrics.total_transfer_volume = metrics[
                    "total_transfer_volume"
                ]
                existing_metrics.transfer_count = metrics["transfer_count"]
            else:
                # Add new metrics
                self.db.add(aggregated_metrics)

        self.db.commit()
