import os
import sys
import plotly.express as px
import pandas as pd
import streamlit as st
from stables.visualization.components import plot_stable_chain_data

st.set_page_config(page_title="Yield", page_icon="💰", layout="wide")


def load_data():
    """Load and merge circulating data from multiple sources."""
    # Load chain-specific circulating data
    df_path = "data/processed/yield_pools.csv"
    df = pd.read_csv(df_path)

    _df = filter_data(df, filter_dict={"symbol": "SCRVUSD", "ilRisk": "no"})

    return _df


def filter_data(df: pd.DataFrame, filter_dict: dict) -> pd.DataFrame:
    _df = df[
        (df["symbol"].str.contains(filter_dict["symbol"], na=False))
        # & (df["ilRisk"] == filter_dict["ilRisk"])
        # & (df["chain"] != "Ethereum")
    ]
    return _df


def main():
    st.title("CRVUSD Yield Dashboard")
    st.markdown("Non Ethereum, No IL Risk, single exposure")
    df = load_data()
    st.dataframe(df)


if __name__ == "__main__":
    main()
