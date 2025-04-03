"""Data transformer for DeFiLlama stablecoin data."""

from typing import Dict, List
import pandas as pd
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChainCirculatingData:
    """Represents chain-specific circulating data for a stablecoin."""

    datetime: datetime
    id: str  # stablecoin id
    chain: str
    circulating: float


@dataclass
class StablecoinData:
    """Represents a stablecoin's complete data.
    "id": "1",
    "name": "Tether",
    "symbol": "USDT",
    "gecko_id": "tether",
    "pegType": "peggedUSD",
    "priceSource": "defillama",
    "pegMechanism": "fiat-backed",
    "circulating": { "peggedUSD": 144714050088.3748 },
    """

    id: str
    name: str
    symbol: str
    gecko_id: str
    peg_type: str
    peg_mechanism: str
    circulating: Dict[str, float]
    # chain_circulating: Dict[str, ChainCirculatingData]


class DeFiLlamaTransformer:
    """Transforms raw DeFiLlama data into structured formats."""

    @staticmethod
    def to_stablecoin_df(raw_data: List[Dict]) -> pd.DataFrame:
        """Convert raw API response to list of StablecoinData objects."""
        records = []
        for item in raw_data:
            stablecoin = StablecoinData(
                id=item["id"],
                name=item["name"],
                symbol=item["symbol"],
                gecko_id=item["gecko_id"],
                peg_type=item["pegType"],
                peg_mechanism=item["pegMechanism"],
                circulating=item["circulating"][item["pegType"]],
            )
            records.append(stablecoin)
        return pd.DataFrame(records)

    @staticmethod
    def to_chain_circulating_df(raw_data: List[Dict]) -> pd.DataFrame:
        """Convert stablecoin data to chain distribution DataFrame."""
        records = []
        for item in raw_data:
            id = item.get("id")
            peg_type = item.get("pegType")
            chain_circulating = item.get("chainCirculating", {})
            for chain, chain_data in chain_circulating.items():
                records.append(
                    {
                        "datetime": datetime.now(),
                        "id": id,
                        "chain": chain,
                        "circulating": chain_data.get("current").get(peg_type),
                    }
                )
        return pd.DataFrame(records)
