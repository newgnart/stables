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
DEFILLAMA_TIMEOUT = 30  # seconds


class DeFiLlamaAPI:
    """Client for interacting with the DeFiLlama Stablecoins API."""

    def __init__(self):
        """
        Initialize the DeFiLlama API client.

        Args:

        """
        self.base_url = DEFILLAMA_STABLECOINS_API_URL

    def fetch_stables(self) -> List[Dict]:
        """Get chain-specific data for all stablecoin."""

        try:
            with requests.get(f"{self.base_url}/stablecoins") as response:
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
            with requests.get(f"{self.base_url}/stablecoin/{id}") as response:
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
