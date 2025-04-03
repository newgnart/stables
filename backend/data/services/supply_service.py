"""Service for collecting and storing circulating supply data."""

from datetime import datetime
from sqlalchemy.orm import Session
from data.models import Circulating
from data.sources.defillama import DeFiLlamaClient
from config.logging import setup_logging

logger = setup_logging()


class SupplyService:
    """Service for managing circulating supply data."""

    def __init__(self, db: Session):
        self.db = db
        self.defillama_client = DeFiLlamaClient()

    async def collect_supply_data(self) -> None:
        """Collect supply data from DeFiLlama and store it in the database."""
        try:
            # Get stablecoin data from DeFiLlama
            stablecoins = await self.defillama_client.get_stablecoin_chain_data()

            for stablecoin in stablecoins:
                # Get chain data for each stablecoin
                chain_data = await self.defillama_client.get_stablecoin_chain_data(
                    stablecoin["gecko_id"]
                )

                for chain in chain_data:
                    # Create or update record
                    record = Circulating(
                        timestamp=datetime.utcnow(),
                        symbol=stablecoin["symbol"],
                        name=stablecoin["name"],
                        gecko_id=stablecoin["gecko_id"],
                        peg_type=stablecoin["pegType"],
                        peg_mechanism=stablecoin["pegMechanism"],
                        chain=chain["chain"],
                        supply=chain["current"],
                        price=stablecoin.get("price", 0.0),
                    )

                    self.db.merge(record)

            self.db.commit()
            logger.info("Successfully collected and stored supply data")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error collecting supply data: {str(e)}")
            raise

    async def close(self) -> None:
        """Close the database session."""
        self.db.close()
