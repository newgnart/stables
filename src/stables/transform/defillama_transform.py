"""Data transformation utilities for stablecoin data."""

from typing import Dict, List, Any, Optional
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class ChainCirculatingData:
    """Represents chain-specific circulating data for a stablecoin."""

    id: str
    chain: str
    circulating: float
    circulatingPrevDay: float
    circulatingPrevWeek: float
    circulatingPrevMonth: float


@dataclass
class StableData:
    """Represents a stablecoin's complete data."""

    id: str
    name: str
    symbol: str
    gecko_id: str
    peg_type: str
    peg_mechanism: str
    total_circulating: float


class DeFiLlamaTransformer:
    """Transforms raw DeFiLlama data into structured formats."""

    @staticmethod
    def stables_to_df(raw_data: List[Dict]) -> pd.DataFrame:
        """Convert raw API response to list of StableData objects."""
        records = []
        for item in raw_data:
            # Skip stablecoins without a gecko_id
            if not item.get("gecko_id"):
                continue

            stablecoin = StableData(
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
    def stables_to_chain_circulating_df(raw_data: List[Dict]) -> pd.DataFrame:
        """Convert stablecoin data to chain distribution DataFrame."""
        records = []
        for item in raw_data:
            # Skip stablecoins without a gecko_id to maintain consistency
            if not item.get("gecko_id"):
                continue

            peg_type = item.get("pegType")
            chain_circulating = item.get("chainCirculating", {})
            for chain, chain_data in chain_circulating.items():
                # Handle possible None values with try/except blocks
                try:
                    circulatingPrevDay = chain_data.get("circulatingPrevDay").get(
                        peg_type
                    )
                except Exception:
                    circulatingPrevDay = chain_data.get("circulatingPrevDay")

                try:
                    circulatingPrevWeek = chain_data.get("circulatingPrevWeek").get(
                        peg_type
                    )
                except Exception:
                    circulatingPrevWeek = chain_data.get("circulatingPrevWeek")

                try:
                    circulatingPrevMonth = chain_data.get("circulatingPrevMonth").get(
                        peg_type
                    )
                except Exception:
                    circulatingPrevMonth = chain_data.get("circulatingPrevMonth")

                # Create object with prepared values
                chain_data_obj = ChainCirculatingData(
                    id=item["id"],
                    chain=chain,
                    circulating=chain_data.get("current").get(peg_type),
                    circulatingPrevDay=circulatingPrevDay,
                    circulatingPrevWeek=circulatingPrevWeek,
                    circulatingPrevMonth=circulatingPrevMonth,
                )
                records.append(chain_data_obj)
        return pd.DataFrame(records)

    @staticmethod
    def stable_to_df(raw_data: Dict, to_date: Optional[bool] = True) -> pd.DataFrame:
        """Convert historical data of a single stablecoin to historical DataFrame."""
        df = pd.DataFrame()
        chainBalances = raw_data["chainBalances"]
        for chain, _data in chainBalances.items():
            data_list = _data["tokens"]
            _df = DeFiLlamaTransformer._flatten_to_df(data_list)
            _df["chain"] = chain
            _df["peg_type"] = raw_data.get("pegType")
            df = pd.concat([df, _df])
        df.replace(0.0, np.nan, inplace=True)
        df = df.dropna(axis=1, how="all")
        df = df.dropna(axis=0, how="all")
        df.columns = df.columns.str.replace(f"_{raw_data.get('pegType')}", "")
        if to_date:
            df["date"] = pd.to_datetime(df["date"].astype(int), unit="s")
        return df

    @staticmethod
    def yield_pools_to_df(raw_data: List[Dict]) -> pd.DataFrame:
        """Convert yield pools data to DataFrame."""
        df = pd.DataFrame(raw_data)
        return df

    @staticmethod
    def yield_pool_to_df(raw_data: Dict) -> pd.DataFrame:
        """Convert yield pool data to DataFrame."""
        df = pd.DataFrame(raw_data)
        return df

    @staticmethod
    def _flatten_nested_dict(
        data_list: List[Dict], separator: str = "_"
    ) -> List[Dict[str, Any]]:
        """
        Flatten nested dictionaries in a list, converting nested structures to flat key-value pairs.

        Args:
            data_list: List of dictionaries that may contain nested dictionaries
            separator: String to use when concatenating keys (default: "_")

        Returns:
            List of flattened dictionaries with concatenated keys
        """
        result = []

        def _flatten_dict(d: Dict, parent_key: str = "") -> Dict[str, Any]:
            flat_dict = {}
            for key, value in d.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key

                if isinstance(value, dict):
                    flat_dict.update(_flatten_dict(value, new_key))
                else:
                    flat_dict[new_key] = value
            return flat_dict

        for item in data_list:
            flattened = _flatten_dict(item)
            result.append(flattened)

        return result

    @staticmethod
    def _flatten_to_df(data_list: List[Dict], separator: str = "_") -> pd.DataFrame:
        """
        Convert a list of potentially nested dictionaries to a flat DataFrame.

        Args:
            data_list: List of dictionaries that may contain nested dictionaries
            separator: String to use when concatenating keys (default: "_")

        Returns:
            Pandas DataFrame with flattened structure
        """
        flattened_list = DeFiLlamaTransformer._flatten_nested_dict(data_list, separator)
        return pd.DataFrame(flattened_list)
