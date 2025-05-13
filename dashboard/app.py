"""Main Streamlit dashboard for stablecoin analytics."""

import streamlit as st
import pandas as pd
from pathlib import Path
import asyncio
import logging
from datetime import datetime, timedelta

from temp.core.services.defillama_service import DeFiLlamaService
from src.analysis.basic_metrics import StablecoinMetrics
from src.visualization.components import StablecoinVisualizations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if "last_update" not in st.session_state:
    st.session_state.last_update = None


def load_latest_data():
    """Load the most recent data files."""
    data_dir = Path("data/raw/defi")
    if not data_dir.exists():
        return None, None

    # Find latest stablecoin data
    stable_files = list(data_dir.glob("stablecoins_*.csv"))
    if not stable_files:
        return None, None

    latest_stable = max(stable_files, key=lambda x: x.stat().st_mtime)
    stable_df = pd.read_csv(latest_stable)

    # Find latest chain data
    chain_files = list(data_dir.glob("chain_circulating_*.csv"))
    if not chain_files:
        return stable_df, None

    latest_chain = max(chain_files, key=lambda x: x.stat().st_mtime)
    chain_df = pd.read_csv(latest_chain)

    return stable_df, chain_df


def main():
    """Main dashboard application."""
    st.set_page_config(
        page_title="Stablecoin Analytics Dashboard", page_icon="📊", layout="wide"
    )

    st.title("Stablecoin Analytics Dashboard")

    # Add refresh button
    if st.button("Refresh Data"):
        with st.spinner("Fetching latest data..."):
            service = DeFiLlamaService()
            asyncio.run(service.collect_circulating_data())
            st.session_state.last_update = datetime.now()

    # Load data
    stable_df, chain_df = load_latest_data()

    if stable_df is None or chain_df is None:
        st.warning(
            "No data available. Please click 'Refresh Data' to fetch the latest data."
        )
        return

    # Display last update time
    if st.session_state.last_update:
        st.info(
            f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    # Create two columns for metrics
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Market Overview")
        # Calculate and display basic metrics
        metrics = StablecoinMetrics.analyze_stablecoin_health(stable_df, chain_df)

        st.metric("Total Stablecoins", metrics["total_stablecoins"])
        st.metric(
            "Total Circulating Supply", f"${metrics['total_circulating_supply']:,.2f}"
        )
        st.metric("Top 3 Market Share", f"{metrics['top_3_market_share']:.1f}%")

    with col2:
        st.subheader("Chain Distribution")
        st.metric("Unique Chains", metrics["unique_chains"])
        st.metric(
            "Avg Chains per Stablecoin", f"{metrics['avg_chains_per_stablecoin']:.1f}"
        )
        st.metric("Avg Daily Growth", f"{metrics['avg_daily_growth']:.1f}%")

    # Create visualizations
    st.subheader("Market Share Distribution")
    fig_market = StablecoinVisualizations.create_market_share_pie(stable_df)
    st.plotly_chart(fig_market, use_container_width=True)

    st.subheader("Chain Distribution")
    fig_chain = StablecoinVisualizations.create_chain_distribution_bar(chain_df)
    st.plotly_chart(fig_chain, use_container_width=True)

    # Growth metrics
    st.subheader("Growth Analysis")
    growth_metrics = StablecoinMetrics.calculate_growth_metrics(chain_df)
    fig_growth = StablecoinVisualizations.create_growth_heatmap(growth_metrics)
    st.plotly_chart(fig_growth, use_container_width=True)

    # Raw data tables
    st.subheader("Raw Data")
    tab1, tab2 = st.tabs(["Stablecoins", "Chain Distribution"])

    with tab1:
        st.dataframe(stable_df)

    with tab2:
        st.dataframe(chain_df)


if __name__ == "__main__":
    main()
