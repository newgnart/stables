"""DeFi Llama API client for fetching stablecoin data."""

from typing import Dict, List, Optional, Any, Union
import aiohttp
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class DeFiLlamaClient:
    """API client for fetching stablecoin data from DeFi Llama."""

    def __init__(self) -> None:
        """Initialize the API client."""
        self.base_url = "https://stablecoins.llama.fi"
        self.session = None
        self.logger = logging.getLogger(__name__)

    async def _ensure_session(self) -> None:
        """Ensure we have an active aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def _fetch_response(self, endpoint: str) -> Dict:
        """Fetch raw stablecoins data from DeFi Llama API."""
        await self._ensure_session()
        url = f"{self.base_url}/{endpoint}"
        try:
            async with self.session.get(url) as response:
                response_json = await response.json()
                return response_json
        except Exception as e:
            self.logger.error(f"Error fetching stablecoins data: {e}")
            return None

    async def get_stablecoins(self) -> List[Dict]:
        """Fetch stablecoin data from DeFi Llama.

        Returns:
            List of dictionaries containing stablecoin data
        """
        response_json = await self._fetch_response(
            endpoint="stablecoins?includePrices=true"
        )
        if not response_json:
            return []

        data = response_json["peggedAssets"]
        stablecoins = []

        for stablecoin in data:
            if isinstance(stablecoin, dict):
                # Get circulating supply values
                circulating_value = self._process_stablecoin_circulating(
                    stablecoin.get("circulating", 0)
                )
                circulating_prev_day = self._process_stablecoin_circulating(
                    stablecoin.get("circulatingPrevDay", 0)
                )
                circulating_prev_week = self._process_stablecoin_circulating(
                    stablecoin.get("circulatingPrevWeek", 0)
                )
                circulating_prev_month = self._process_stablecoin_circulating(
                    stablecoin.get("circulatingPrevMonth", 0)
                )

                # Get chain information
                chain_circulating = stablecoin.get("chainCirculating", {})
                chain_data = self._process_stablecoin_chain_data(chain_circulating)
                chains = [item["chain"] for item in chain_data]

                stablecoins.append(
                    {
                        "id": stablecoin.get("id"),
                        "name": stablecoin.get("name"),
                        "symbol": stablecoin.get("symbol"),
                        "gecko_id": stablecoin.get("gecko_id"),
                        "pegType": stablecoin.get("pegType"),
                        "pegMechanism": stablecoin.get("pegMechanism"),
                        "priceSource": stablecoin.get("priceSource"),
                        "circulating": circulating_value,
                        "circulatingPrevDay": circulating_prev_day,
                        "circulatingPrevWeek": circulating_prev_week,
                        "circulatingPrevMonth": circulating_prev_month,
                        "chains": chains,
                        "chainData": chain_data,
                        "price": stablecoin.get("price", 1.0),
                    }
                )

        return stablecoins

    async def get_stablecoin_chain_data(self) -> List[Dict]:
        """Fetch chain-specific stablecoin data from DeFi Llama.

        Returns:
            List of dictionaries containing chain-specific data
        """
        response_json = await self._fetch_response(
            endpoint="stablecoins?includePrices=true"
        )
        if not response_json:
            return []

        data = response_json["peggedAssets"]
        chain_records = []

        for stablecoin in data:
            if not isinstance(stablecoin, dict):
                continue

            chain_circulating = stablecoin.get("chainCirculating", {})
            for chain, chain_data in chain_circulating.items():
                chain_records.append(
                    {
                        "id": stablecoin.get("id"),
                        "name": stablecoin.get("name"),
                        "symbol": stablecoin.get("symbol"),
                        "chain": chain,
                        "current": self._process_stablecoin_circulating(
                            chain_data.get("current", {})
                        ),
                        "prevDay": self._process_stablecoin_circulating(
                            chain_data.get("circulatingPrevDay", {})
                        ),
                        "prevWeek": self._process_stablecoin_circulating(
                            chain_data.get("circulatingPrevWeek", {})
                        ),
                        "prevMonth": self._process_stablecoin_circulating(
                            chain_data.get("circulatingPrevMonth", {})
                        ),
                    }
                )

        return chain_records

    def _process_stablecoin_circulating(
        self, circulating_data: Union[Dict, int, float]
    ) -> float:
        """Helper method to calculate total circulating supply from API response."""
        if isinstance(circulating_data, (int, float)):
            return float(circulating_data)
        elif isinstance(circulating_data, dict):
            return sum(
                float(value)
                for value in circulating_data.values()
                if isinstance(value, (int, float))
            )
        return 0.0

    def _process_stablecoin_chain_data(self, chain_circulating: Dict) -> List[Dict]:
        """Process chain-specific circulating supply data."""
        chain_data = []
        for chain, data in chain_circulating.items():
            chain_data.append(
                {
                    "chain": chain,
                    "current": self._process_stablecoin_circulating(
                        data.get("current", {})
                    ),
                    "prevDay": self._process_stablecoin_circulating(
                        data.get("circulatingPrevDay", {})
                    ),
                    "prevWeek": self._process_stablecoin_circulating(
                        data.get("circulatingPrevWeek", {})
                    ),
                    "prevMonth": self._process_stablecoin_circulating(
                        data.get("circulatingPrevMonth", {})
                    ),
                }
            )
        return chain_data

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
