"""Visualization components for stablecoin data."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import logging

import plotly.graph_objects as go
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StableVisualizer:
    """Create visualizations for stablecoin data."""

    @staticmethod
    def plot_yields(
        pools_data: Dict[str, pd.DataFrame],
        title: str = "Pool Yields Over Time",
        days: int = 90,
    ) -> go.Figure:
        """
        Create a plot showing APY and TVL trends for multiple pools.

        Args:
            pools_data: Dictionary mapping pool names to their yield data DataFrames
            title: Title for the plot

        Returns:
            Plotly figure object with two subplots (APY and TVL)
        """
        # Create figure with secondary y-axis
        fig = go.Figure()

        # Calculate the date N days ago in UTC
        days_ago = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)

        # Plot each pool's data
        for pool_name, df in pools_data.items():
            # Convert timestamp to datetime if it's not already
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Filter data for last N days
            df = df[df["timestamp"] >= days_ago]

            # Add APY trace
            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=df["apy"],
                    name=f"{pool_name}",
                    line=dict(width=2),
                )
            )

        # Update layout with two y-axes
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis=dict(
                title="APY (%)", side="left", showgrid=True, gridcolor="lightgrey"
            ),
            hovermode="x unified",
            showlegend=True,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.05),
            template="plotly_white",
            xaxis=dict(range=[days_ago, pd.Timestamp.now(tz="UTC")]),
        )

        return fig
