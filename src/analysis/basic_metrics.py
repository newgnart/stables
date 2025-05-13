"""Basic metrics analysis for stablecoin data."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StablecoinMetrics:
    """Calculate basic metrics for stablecoin data."""

    @staticmethod
    def calculate_market_share(stable_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate market share for each stablecoin.

        Args:
            stable_df: DataFrame containing stablecoin data

        Returns:
            DataFrame with market share calculations
        """
        total_supply = stable_df["total_circulating"].sum()
        market_share = stable_df.copy()
        market_share["market_share"] = (
            market_share["total_circulating"] / total_supply * 100
        )
        return market_share.sort_values("market_share", ascending=False)

    @staticmethod
    def calculate_chain_distribution(chain_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate distribution of stablecoins across chains.

        Args:
            chain_df: DataFrame containing chain circulating data

        Returns:
            DataFrame with chain distribution metrics
        """
        chain_dist = (
            chain_df.groupby("chain")
            .agg({"circulating": "sum", "id": "nunique"})
            .reset_index()
        )

        chain_dist.columns = ["chain", "total_circulating", "unique_stablecoins"]
        chain_dist["chain_share"] = (
            chain_dist["total_circulating"]
            / chain_dist["total_circulating"].sum()
            * 100
        )
        return chain_dist.sort_values("total_circulating", ascending=False)

    @staticmethod
    def calculate_growth_metrics(chain_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate growth metrics for each stablecoin-chain pair.

        Args:
            chain_df: DataFrame containing chain circulating data

        Returns:
            DataFrame with growth metrics
        """
        growth_metrics = chain_df.copy()

        # Calculate daily growth
        growth_metrics["daily_growth"] = (
            (growth_metrics["circulating"] - growth_metrics["circulatingPrevDay"])
            / growth_metrics["circulatingPrevDay"]
            * 100
        )

        # Calculate weekly growth
        growth_metrics["weekly_growth"] = (
            (growth_metrics["circulating"] - growth_metrics["circulatingPrevWeek"])
            / growth_metrics["circulatingPrevWeek"]
            * 100
        )

        # Calculate monthly growth
        growth_metrics["monthly_growth"] = (
            (growth_metrics["circulating"] - growth_metrics["circulatingPrevMonth"])
            / growth_metrics["circulatingPrevMonth"]
            * 100
        )

        return growth_metrics

    @staticmethod
    def analyze_stablecoin_health(
        stable_df: pd.DataFrame, chain_df: pd.DataFrame
    ) -> Dict:
        """
        Analyze overall health metrics for stablecoins.

        Args:
            stable_df: DataFrame containing stablecoin data
            chain_df: DataFrame containing chain circulating data

        Returns:
            Dictionary containing health metrics
        """
        # Calculate market concentration
        market_share = StablecoinMetrics.calculate_market_share(stable_df)
        top_3_share = market_share["market_share"].head(3).sum()

        # Calculate chain diversity
        chain_dist = StablecoinMetrics.calculate_chain_distribution(chain_df)
        avg_chains_per_stablecoin = chain_df.groupby("id")["chain"].nunique().mean()

        # Calculate growth metrics
        growth_metrics = StablecoinMetrics.calculate_growth_metrics(chain_df)
        avg_daily_growth = growth_metrics["daily_growth"].mean()

        return {
            "total_stablecoins": len(stable_df),
            "total_circulating_supply": stable_df["total_circulating"].sum(),
            "top_3_market_share": top_3_share,
            "avg_chains_per_stablecoin": avg_chains_per_stablecoin,
            "avg_daily_growth": avg_daily_growth,
            "unique_chains": len(chain_dist),
        }
