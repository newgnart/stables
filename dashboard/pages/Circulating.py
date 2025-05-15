import os
import sys
import plotly.express as px
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Circulating", page_icon="💰", layout="wide")


def load_data():
    """Load and merge circulating data from multiple sources."""
    # Load chain-specific circulating data
    chain_circulating_path = "data/processed/stables_chain.csv"
    chain_df = pd.read_csv(chain_circulating_path)

    # Load stablecoin metadata
    stables_path = "data/processed/stables.csv"
    stables_df = pd.read_csv(stables_path)

    # Merge the dataframes
    df = pd.merge(
        chain_df,
        stables_df[["id", "name", "symbol", "peg_type", "peg_mechanism"]],
        on="id",
        how="left",
    )

    return df


def main():
    st.title("Circulating Dashboard")

    df = load_data()
    st.dataframe(df)


if __name__ == "__main__":
    main()
