import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_chain_chart(data: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart of total circulation by blockchain.

    Args:
        data: DataFrame with circulation data aggregated by chain

    Returns:
        Plotly figure object
    """
    fig = px.bar(
        data,
        x="chain",
        y="circulating",
        title="Total Stablecoin Circulation by Blockchain",
        labels={"chain": "Blockchain", "circulating": "Total Circulation (USD)"},
        color="circulating",
        color_continuous_scale="Viridis",
    )

    fig.update_layout(
        xaxis_title="Blockchain",
        yaxis_title="Total Circulation (USD)",
        yaxis_type="log",  # Log scale for better visualization
        height=600,
    )

    return fig


def create_name_chart(data: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart of total circulation by stablecoin.

    Args:
        data: DataFrame with circulation data aggregated by name

    Returns:
        Plotly figure object
    """
    fig = px.bar(
        data,
        x="name",
        y="circulating",
        title="Total Stablecoin Circulation by Coin",
        labels={"name": "Stablecoin", "circulating": "Total Circulation (USD)"},
        color="circulating",
        color_continuous_scale="Plasma",
    )

    fig.update_layout(
        xaxis_title="Stablecoin",
        yaxis_title="Total Circulation (USD)",
        yaxis_type="log",  # Log scale for better visualization
        height=600,
    )

    return fig
