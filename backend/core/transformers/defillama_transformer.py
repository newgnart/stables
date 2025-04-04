"""Data transformer for DeFiLlama stablecoin data."""

from typing import Dict, List
import pandas as pd
from dataclasses import dataclass
from datetime import datetime

now = datetime.now()


@dataclass
class LlamaChainCirculatingData:
    """Represents chain-specific circulating data for a stablecoin."""

    stable_id: str
    chain: str
    circulating: float


@dataclass
class LlamaStableData:
    """Represents a stablecoin's complete data."""

    id: str
    name: str
    symbol: str
    gecko_id: str
    peg_type: str
    peg_mechanism: str
    total_circulating: float


class LlamaStableTransformer:
    """Transforms raw DeFiLlama data into structured formats."""

    @staticmethod
    def to_stable_df(raw_data: List[Dict]) -> pd.DataFrame:
        """Convert raw API response to list of StablecoinData objects."""
        records = []
        for item in raw_data:
            # Skip stablecoins without a gecko_id
            if not item.get("gecko_id"):
                continue

            stablecoin = LlamaStableData(
                id=item["id"],
                name=item["name"],
                symbol=item["symbol"],
                gecko_id=item["gecko_id"],
                peg_type=item["pegType"],
                peg_mechanism=item["pegMechanism"],
                total_circulating=item["circulating"][item["pegType"]],
            )
            records.append(stablecoin)
        return pd.DataFrame(records)

    @staticmethod
    def to_chain_circulating_df(raw_data: List[Dict]) -> pd.DataFrame:
        """Convert stablecoin data to chain distribution DataFrame."""
        records = []
        for item in raw_data:
            # Skip stablecoins without a gecko_id to maintain consistency
            if not item.get("gecko_id"):
                continue

            peg_type = item.get("pegType")
            chain_circulating = item.get("chainCirculating", {})
            for chain, chain_data in chain_circulating.items():
                chain_circulating = LlamaChainCirculatingData(
                    stable_id=item["id"],
                    chain=chain,
                    circulating=chain_data.get("current").get(peg_type),
                )
                records.append(chain_circulating)
        return pd.DataFrame(records)
