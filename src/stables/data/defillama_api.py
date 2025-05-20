"""DeFiLlama API client for stablecoin data."""

import requests
from typing import Dict, List, Union
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFILLAMA_STABLECOINS_API_URL = "https://stablecoins.llama.fi"
DEFILLAMA_YIELDS_API_URL = "https://yields.llama.fi"
DEFILLAMA_TIMEOUT = 30  # seconds


class DeFiLlamaAPI:
    """Client for interacting with the DeFiLlama Stablecoins API."""

    def __init__(self):
        """
        Initialize the DeFiLlama API client.

        Args:

        """
        self.base_stables_url = DEFILLAMA_STABLECOINS_API_URL
        self.base_yields_url = DEFILLAMA_YIELDS_API_URL

    def fetch_stables(self) -> List[Dict]:
        """Get chain-specific data for all stablecoin."""

        try:
            with requests.get(f"{self.base_stables_url}/stablecoins") as response:
                if response.status_code == 200:
                    response = response.json()
                    data = response["peggedAssets"]
                    return data
                else:
                    logger.error(f"Error fetching chain data {response}")
                    return []
        except Exception as e:
            logger.error(f"Exception fetching chain data: {str(e)}")
            return []

    def fetch_stable(self, id: str) -> List[Dict]:
        """Get historical stablecoin data."""
        try:
            with requests.get(f"{self.base_stables_url}/stablecoin/{id}") as response:
                if response.status_code == 200:
                    response = response.json()
                    return response
                else:
                    logger.error(
                        f"Error fetching historical stablecoin data {response.status}"
                    )
                    return []
        except Exception as e:
            logger.error(f"Exception fetching historical stablecoin data: {str(e)}")
            return []

    def fetch_yield_pools(self) -> List[Dict]:
        """Get lastest data for all pools"""
        try:
            with requests.get(f"{self.base_yields_url}/pools") as response:
                if response.status_code == 200:
                    response = response.json()
                    return response["data"]
                else:
                    logger.error(f"Error fetching yield pools {response}")
                    return []
        except Exception as e:
            logger.error(f"Exception fetching yield pools: {str(e)}")
            return []

    def fetch_yield_pool(self, pool: str) -> List[Dict]:
        """Get historical yield pool data."""
        try:
            with requests.get(f"{self.base_yields_url}/chart/{pool}") as response:
                if response.status_code == 200:
                    response = response.json()
                    return response["data"]
                else:
                    logger.error(f"Error fetching yield pool data {response}")
                    return []
        except Exception as e:
            logger.error(f"Exception fetching yield pool data: {str(e)}")
            return []
