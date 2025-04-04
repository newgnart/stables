"""Service for collecting and storing circulating supply data."""

from datetime import datetime
import pytz
from sqlalchemy.orm import Session
from core.models import LlamaStable, LlamaChainCirculating
from core.sources.llama_api import LlamaStableAPI
from core.transformers.defillama_transformer import LlamaStableTransformer
from config.logging import setup_logging

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

    async def get_stablecoin_info(
        self, stablecoin_id: str, time_utc: datetime = None
    ) -> None:
        """Get information about a specific stablecoin.

        Args:
            stablecoin_id: The ID of the stablecoin
            time_utc: Optional specific time to query. If None, gets latest record.
        """
        try:
            # Base query for the stablecoin
            query = self.db.query(LlamaStable).filter(LlamaStable.id == stablecoin_id)

            if time_utc:
                # Get record at specific time
                stable = query.filter(LlamaStable.time_utc == time_utc).first()
            else:
                # Get latest record
                stable = query.order_by(LlamaStable.time_utc.desc()).first()

            if not stable:
                logger.warning(f"No data found for stablecoin {stablecoin_id}")
                return None

            # Get chain distribution for this stablecoin at the same time
            chains = (
                self.db.query(LlamaChainCirculating)
                .filter(
                    LlamaChainCirculating.stable_id == stablecoin_id,
                    LlamaChainCirculating.time_utc == stable.time_utc,
                )
                .all()
            )

            # Print stablecoin info using __str__
            logger.info(f"Stablecoin Info: {stable}")

            # Print detailed info using individual fields
            logger.info("Chain Distribution:")
            for chain in chains:
                logger.info(f"  {chain}")  # Uses chain.__str__

            return stable, chains

        except Exception as e:
            logger.error(f"Error getting stablecoin info: {str(e)}")
            raise

    async def get_supply_history(self, stablecoin_id: str, limit: int = 10) -> None:
        """Get historical supply data for a stablecoin.

        Args:
            stablecoin_id: The ID of the stablecoin
            limit: Maximum number of records to return
        """
        try:
            # Get historical records
            records = (
                self.db.query(LlamaStable)
                .filter(LlamaStable.id == stablecoin_id)
                .order_by(LlamaStable.time_utc.desc())
                .limit(limit)
                .all()
            )

            if not records:
                logger.warning(f"No history found for stablecoin {stablecoin_id}")
                return None

            logger.info(f"Supply history for {records[0].symbol}:")
            for record in records:
                logger.info(f"  {record.time_utc}: {record.total_circulating:,.2f}")

            return records

        except Exception as e:
            logger.error(f"Error getting supply history: {str(e)}")
            raise
