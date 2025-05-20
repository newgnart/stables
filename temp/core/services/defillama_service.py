"""Service for collecting and processing DeFiLlama stablecoin data."""

from datetime import datetime
import pytz
import logging
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path

from data.defillama_api import DeFiLlamaAPI
from src.processing.transformations import DeFiLlamaTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeFiLlamaService:
    """Service for managing DeFiLlama stablecoin data collection and processing."""

    def __init__(self, data_dir: str = "data/raw/defi"):
        """
        Initialize the DeFiLlama service.

        Args:
            data_dir: Directory to store raw data files
        """
        self.api = DeFiLlamaAPI()
        self.transformer = DeFiLlamaTransformer()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def collect_circulating_data(self) -> None:
        """Collect and store circulating supply data from DeFiLlama."""
        try:
            # Fetch and transform data
            raw_data = await self.api.get_circulating()
            stable_df = self.transformer.circulating_to_stable_df(raw_data)
            chain_circulating_df = self.transformer.circulating_to_chain_circulating_df(
                raw_data
            )

            # Get current time in UTC with minute precision
            current_time = datetime.now(pytz.UTC).replace(second=0, microsecond=0)
            timestamp = current_time.strftime("%Y%m%d_%H%M")

            # Save stablecoin data
            stable_file = self.data_dir / f"stablecoins_{timestamp}.csv"
            stable_df.to_csv(stable_file, index=False)
            logger.info(f"Saved stablecoin data to {stable_file}")

            # Save chain circulating data
            chain_file = self.data_dir / f"chain_circulating_{timestamp}.csv"
            chain_circulating_df.to_csv(chain_file, index=False)
            logger.info(f"Saved chain circulating data to {chain_file}")

        except Exception as e:
            logger.error(f"Error collecting circulating data: {str(e)}")
            raise

    async def collect_historical_data(
        self, stablecoin_id: str
    ) -> Optional[pd.DataFrame]:
        """
        Collect historical data for a specific stablecoin.

        Args:
            stablecoin_id: The DeFiLlama ID of the stablecoin

        Returns:
            DataFrame containing historical data if successful, None otherwise
        """
        try:
            raw_data = await self.api.get_historical(stablecoin_id)
            if not raw_data:
                logger.warning(
                    f"No historical data found for stablecoin {stablecoin_id}"
                )
                return None

            historical_df = self.transformer.historical_to_historical_df(raw_data)

            # Save historical data
            timestamp = datetime.now(pytz.UTC).strftime("%Y%m%d_%H%M")
            historical_file = (
                self.data_dir / f"historical_{stablecoin_id}_{timestamp}.csv"
            )
            historical_df.to_csv(historical_file, index=False)
            logger.info(f"Saved historical data to {historical_file}")

            return historical_df

        except Exception as e:
            logger.error(
                f"Error collecting historical data for {stablecoin_id}: {str(e)}"
            )
            return None

    async def close(self) -> None:
        """Close any open connections."""
        pass  # No connections to close in this implementation
