import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


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


def create_chain_coins_chart(data: pd.DataFrame, chain: str) -> go.Figure:
    """
    Create a bar chart of stablecoin circulation for a specific blockchain.

    Args:
        data: DataFrame with circulation data filtered by chain
        chain: Name of the blockchain

    Returns:
        Plotly figure object
    """
    fig = px.bar(
        data,
        x="name",
        y="circulating",
        title=f"Stablecoin Circulation on {chain}",
        labels={"name": "Stablecoin", "circulating": "Circulation (USD)"},
        color="circulating",
        color_continuous_scale="Turbo",
    )

    fig.update_layout(
        xaxis_title="Stablecoin",
        yaxis_title="Circulation (USD)",
        yaxis_type="log",  # Log scale for better visualization
        height=600,
    )

    return fig


def create_movers_scatter_plot(
    data: pd.DataFrame, entity_type: str, log_scale: bool = True
) -> go.Figure:
    """
    Create a scatter plot of movers showing circulation vs percentage change.

    Args:
        data: DataFrame with mover data (must include circulating, pct_change, and category columns)
        entity_type: Type of entity ('chain' or 'coin')
        log_scale: Whether to use logarithmic scale for circulation

    Returns:
        Plotly figure object
    """
    # Determine the x-axis column
    x_col = "chain" if entity_type == "chain" else "name"

    # Create the scatter plot
    fig = px.scatter(
        data,
        x="circulating",
        y="pct_change",
        color="category",
        size=data["circulating"].abs(),
        size_max=60,
        hover_name=x_col,
        hover_data={
            "circulating": ":,.2f",
            "abs_change": ":,.2f",
            "pct_change": ":+.2f%",
        },
        labels={
            "circulating": "Circulation (USD)",
            "pct_change": "Percentage Change (%)",
            "category": "Category",
        },
        title=f"Circulation Movers by {entity_type.capitalize()}",
        color_discrete_map={
            "Rising Stars": "#00CC96",  # Green
            "Major Growers": "#636EFA",  # Blue
            "Declining Leaders": "#EF553B",  # Red
            "Fading Coins": "#FFA15A",  # Orange
            "Stable": "#CCCCCC",  # Gray
        },
    )

    # Add quadrant lines
    circ_threshold = np.percentile(data["circulating"], 75)
    fig.add_shape(
        type="line",
        x0=circ_threshold,
        x1=circ_threshold,
        y0=data["pct_change"].min(),
        y1=data["pct_change"].max(),
        line=dict(color="rgba(0,0,0,0.3)", width=1, dash="dash"),
    )
    fig.add_shape(
        type="line",
        x0=data["circulating"].min(),
        x1=data["circulating"].max(),
        y0=0,
        y1=0,
        line=dict(color="rgba(0,0,0,0.3)", width=1, dash="dash"),
    )

    # Update layout
    fig.update_layout(
        height=600,
        xaxis_title="Circulation (USD)",
        yaxis_title="Percentage Change (%)",
        xaxis_type="log" if log_scale else "linear",
        legend_title="Category",
    )

    # Add annotations for quadrants
    fig.add_annotation(
        x=(
            np.log10(data["circulating"].min() * 2)
            if log_scale
            else data["circulating"].min() * 2
        ),
        y=data["pct_change"].max() * 0.9,
        text="Rising Stars",
        showarrow=False,
        font=dict(size=12, color="#00CC96"),
    )
    fig.add_annotation(
        x=(
            np.log10(data["circulating"].max() * 0.8)
            if log_scale
            else data["circulating"].max() * 0.8
        ),
        y=data["pct_change"].max() * 0.9,
        text="Major Growers",
        showarrow=False,
        font=dict(size=12, color="#636EFA"),
    )
    fig.add_annotation(
        x=(
            np.log10(data["circulating"].max() * 0.8)
            if log_scale
            else data["circulating"].max() * 0.8
        ),
        y=data["pct_change"].min() * 0.9,
        text="Declining Leaders",
        showarrow=False,
        font=dict(size=12, color="#EF553B"),
    )
    fig.add_annotation(
        x=(
            np.log10(data["circulating"].min() * 2)
            if log_scale
            else data["circulating"].min() * 2
        ),
        y=data["pct_change"].min() * 0.9,
        text="Fading Coins",
        showarrow=False,
        font=dict(size=12, color="#FFA15A"),
    )

    return fig


def create_movers_bar_chart(
    data: pd.DataFrame, entity_type: str, top_n: int = 10
) -> go.Figure:
    """
    Create a horizontal bar chart showing top gainers and losers.

    Args:
        data: DataFrame with mover data (must include pct_change)
        entity_type: Type of entity ('chain' or 'coin')
        top_n: Number of top gainers and losers to show

    Returns:
        Plotly figure object
    """
    # Determine x-axis column
    x_col = "chain" if entity_type == "chain" else "name"

    # Sort and select top gainers and losers
    gainers = data.sort_values("pct_change", ascending=False).head(top_n)
    losers = data.sort_values("pct_change", ascending=True).head(top_n)

    # Create a single DataFrame for the chart
    plot_data = pd.concat([gainers, losers])

    # Add color information
    plot_data["color"] = np.where(plot_data["pct_change"] >= 0, "#00CC96", "#EF553B")

    # Create the bar chart
    fig = px.bar(
        plot_data,
        y=x_col,
        x="pct_change",
        orientation="h",
        color="pct_change",
        color_continuous_scale=["#EF553B", "#FFFFFF", "#00CC96"],
        range_color=[
            -max(abs(plot_data["pct_change"])),
            max(abs(plot_data["pct_change"])),
        ],
        labels={x_col: entity_type.capitalize(), "pct_change": "Percentage Change (%)"},
        title=f"Top {top_n} Gainers and Losers by {entity_type.capitalize()}",
        hover_data={
            "circulating": ":,.2f",
            "abs_change": ":,.2f",
            "pct_change": ":+.2f%",
        },
    )

    # Update layout
    fig.update_layout(
        height=600,
        xaxis_title="Percentage Change (%)",
        yaxis_title=entity_type.capitalize(),
    )

    # Add a vertical line at 0
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=-0.5,
        y1=len(plot_data) - 0.5,
        line=dict(color="black", width=1),
    )

    return fig
