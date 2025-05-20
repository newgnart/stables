"""Service for collecting and storing circulating supply data."""

from datetime import datetime
import pytz
from sqlalchemy.orm import Session
from stables.core.models import LlamaStable, LlamaChainCirculating
from stables.core.sources.llama_api import LlamaStableAPI
from stables.core.transformers.defillama_transformer import LlamaStableTransformer
from stables.config.logging import setup_logging

logger = setup_logging()


class LlamaService:
    """Service for managing circulating supply data."""

    def __init__(self, db: Session):
        self.db = db
        self.api = LlamaStableAPI()
        self.transformer = LlamaStableTransformer()

    async def add_circulating_data(self) -> None:
        """Collect supply data from DeFiLlama and store it in the database."""
        try:
            # Fetch and transform data
            raw_data = await self.api.get_circulating()
            stable_df = self.transformer.to_stable_df(raw_data)
            chain_circulating_df = self.transformer.to_chain_circulating_df(raw_data)

            # Get current time in UTC with minute precision
            current_time = datetime.now(pytz.UTC).replace(second=0, microsecond=0)

            # First, update stablecoin table
            for _, row in stable_df.iterrows():
                # add data to stable table
                llama_stable = LlamaStable(
                    id=row["id"],
                    time_utc=current_time,
                    name=row["name"],
                    symbol=row["symbol"],
                    gecko_id=row["gecko_id"],
                    peg_type=row["peg_type"],
                    peg_mechanism=row["peg_mechanism"],
                    total_circulating=row["total_circulating"],
                )
                self.db.add(llama_stable)
                logger.debug(f"Adding stablecoin data: {llama_stable}")

            # Commit stablecoin changes first
            self.db.commit()
            logger.info("Successfully added llama stable data")

            # Then, update chain_circulating table
            for _, row in chain_circulating_df.iterrows():
                llama_chain_circulating = LlamaChainCirculating(
                    stable_id=row["stable_id"],
                    chain=row["chain"],
                    circulating=row["circulating"],
                    time_utc=current_time,
                )
                self.db.add(llama_chain_circulating)
                logger.debug(
                    f"Adding chain circulating data: {llama_chain_circulating}"
                )

            # Commit chain_circulating changes
            self.db.commit()
            logger.info("Successfully added llama chain circulating data")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding circulating data: {str(e)}")
            raise

    async def close(self) -> None:
        """Close the database session."""
        self.db.close()
