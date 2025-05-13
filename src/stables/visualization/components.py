"""Visualization components for stablecoin data."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StablecoinVisualizations:
    """Create visualizations for stablecoin data."""

    @staticmethod
    def create_market_share_pie(stable_df: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """
        Create a pie chart of market share distribution.

        Args:
            stable_df: DataFrame containing stablecoin data
            top_n: Number of top stablecoins to show

        Returns:
            Plotly figure object
        """
        # Calculate market share
        total_supply = stable_df["total_circulating"].sum()
        market_share = stable_df.copy()
        market_share["market_share"] = (
            market_share["total_circulating"] / total_supply * 100
        )

        # Get top N stablecoins
        top_stablecoins = market_share.nlargest(top_n, "market_share")
        others = market_share.nsmallest(len(market_share) - top_n, "market_share")

        # Create data for pie chart
        labels = list(top_stablecoins["symbol"]) + ["Others"]
        values = list(top_stablecoins["market_share"]) + [others["market_share"].sum()]

        # Create pie chart
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    textinfo="label+percent",
                    insidetextorientation="radial",
                )
            ]
        )

        fig.update_layout(title="Stablecoin Market Share Distribution", showlegend=True)

        return fig

    @staticmethod
    def create_chain_distribution_bar(
        chain_df: pd.DataFrame, top_n: int = 10
    ) -> go.Figure:
        """
        Create a bar chart of chain distribution.

        Args:
            chain_df: DataFrame containing chain circulating data
            top_n: Number of top chains to show

        Returns:
            Plotly figure object
        """
        # Calculate chain distribution
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

        # Get top N chains
        top_chains = chain_dist.nlargest(top_n, "total_circulating")

        # Create bar chart
        fig = go.Figure(
            data=[
                go.Bar(
                    x=top_chains["chain"],
                    y=top_chains["total_circulating"],
                    text=top_chains["unique_stablecoins"],
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            title="Stablecoin Distribution Across Chains",
            xaxis_title="Chain",
            yaxis_title="Total Circulating Supply",
            showlegend=False,
        )

        return fig

    @staticmethod
    def create_growth_heatmap(growth_df: pd.DataFrame) -> go.Figure:
        """
        Create a heatmap of growth metrics.

        Args:
            growth_df: DataFrame containing growth metrics

        Returns:
            Plotly figure object
        """
        # Pivot data for heatmap
        pivot_data = growth_df.pivot_table(
            values="daily_growth", index="id", columns="chain", aggfunc="mean"
        )

        # Create heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=pivot_data.values,
                x=pivot_data.columns,
                y=pivot_data.index,
                colorscale="RdYlGn",
                zmid=0,
            )
        )

        fig.update_layout(
            title="Daily Growth Rate by Stablecoin and Chain",
            xaxis_title="Chain",
            yaxis_title="Stablecoin",
            showlegend=True,
        )

        return fig

    @staticmethod
    def create_historical_trend(
        historical_df: pd.DataFrame, stablecoin_id: str
    ) -> go.Figure:
        """
        Create a line chart of historical trends.

        Args:
            historical_df: DataFrame containing historical data
            stablecoin_id: ID of the stablecoin to plot

        Returns:
            Plotly figure object
        """
        # Filter data for specific stablecoin
        coin_data = historical_df[historical_df["id"] == stablecoin_id]

        # Create line chart
        fig = go.Figure()

        for chain in coin_data["chain"].unique():
            chain_data = coin_data[coin_data["chain"] == chain]
            fig.add_trace(
                go.Scatter(
                    x=chain_data["date"],
                    y=chain_data["circulating"],
                    name=chain,
                    mode="lines",
                )
            )

        fig.update_layout(
            title=f"Historical Circulating Supply - {stablecoin_id}",
            xaxis_title="Date",
            yaxis_title="Circulating Supply",
            showlegend=True,
        )

        return fig
