import pandas as pd
import numpy as np


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load and preprocess the CSV data.

    Args:
        file_path: Path to the CSV file

    Returns:
        Preprocessed DataFrame
    """
    df = pd.read_csv(file_path)
    return df


def aggregate_by_chain(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate circulation data by blockchain.

    Args:
        df: DataFrame containing circulation data

    Returns:
        DataFrame with total circulation by chain
    """
    # Group by chain and sum the circulating amounts
    chain_data = df.groupby("chain")["circulating"].sum().reset_index()
    chain_data = chain_data.sort_values("circulating", ascending=False)
    return chain_data


def aggregate_by_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate circulation data by coin name.

    Args:
        df: DataFrame containing circulation data

    Returns:
        DataFrame with total circulation by coin name
    """
    # Group by name and sum the circulating amounts
    name_data = df.groupby("name")["circulating"].sum().reset_index()
    name_data = name_data.sort_values("circulating", ascending=False)
    return name_data


def filter_by_chain(df: pd.DataFrame, chain: str) -> pd.DataFrame:
    """
    Filter circulation data for a specific blockchain.

    Args:
        df: DataFrame containing circulation data
        chain: Name of the blockchain to filter by

    Returns:
        DataFrame with circulation data for the specified chain
    """
    # Filter data for the specified chain
    chain_data = df[df["chain"] == chain].copy()
    chain_data = chain_data.sort_values("circulating", ascending=False)
    return chain_data


def calculate_movers_by_chain(
    df: pd.DataFrame, time_period: str = "prevDay"
) -> pd.DataFrame:
    """
    Calculate circulation changes by blockchain.

    Args:
        df: DataFrame containing circulation data
        time_period: Time period to compare against ('prevDay', 'prevWeek', 'prevMonth')

    Returns:
        DataFrame with circulation changes by chain
    """
    # Determine which column to use for comparison
    compare_col = f"circulating{time_period}"

    # Group by chain and sum current and previous circulation
    chain_data = (
        df.groupby("chain")
        .agg(
            {
                "circulating": "sum",
                compare_col: "sum",
            }
        )
        .reset_index()
    )

    # Calculate changes
    chain_data["abs_change"] = chain_data["circulating"] - chain_data[compare_col]
    chain_data["pct_change"] = np.where(
        chain_data[compare_col] > 0,
        (chain_data["circulating"] - chain_data[compare_col])
        / chain_data[compare_col]
        * 100,
        0,  # Handle division by zero
    )

    # Sort by absolute change
    chain_data = chain_data.sort_values("abs_change", ascending=False)

    return chain_data


def calculate_movers_by_coin(
    df: pd.DataFrame, time_period: str = "prevDay"
) -> pd.DataFrame:
    """
    Calculate circulation changes by coin.

    Args:
        df: DataFrame containing circulation data
        time_period: Time period to compare against ('prevDay', 'prevWeek', 'prevMonth')

    Returns:
        DataFrame with circulation changes by coin
    """
    # Determine which column to use for comparison
    compare_col = f"circulating{time_period}"

    # Group by name and sum current and previous circulation
    coin_data = (
        df.groupby("name")
        .agg(
            {
                "circulating": "sum",
                compare_col: "sum",
            }
        )
        .reset_index()
    )

    # Calculate changes
    coin_data["abs_change"] = coin_data["circulating"] - coin_data[compare_col]
    coin_data["pct_change"] = np.where(
        coin_data[compare_col] > 0,
        (coin_data["circulating"] - coin_data[compare_col])
        / coin_data[compare_col]
        * 100,
        0,  # Handle division by zero
    )

    # Sort by absolute change
    coin_data = coin_data.sort_values("abs_change", ascending=False)

    return coin_data


def calculate_detailed_movers(
    df: pd.DataFrame, time_period: str = "prevDay"
) -> pd.DataFrame:
    """
    Calculate detailed circulation changes by coin-chain combination.

    Args:
        df: DataFrame containing circulation data
        time_period: Time period to compare against ('prevDay', 'prevWeek', 'prevMonth')

    Returns:
        DataFrame with circulation changes for each coin-chain combination
    """
    # Determine which column to use for comparison
    compare_col = f"circulating{time_period}"

    # Make a copy of the DataFrame with the relevant columns
    movers_df = df[["chain", "name", "circulating", compare_col]].copy()

    # Calculate changes
    movers_df["abs_change"] = movers_df["circulating"] - movers_df[compare_col]
    movers_df["pct_change"] = np.where(
        movers_df[compare_col] > 0,
        (movers_df["circulating"] - movers_df[compare_col])
        / movers_df[compare_col]
        * 100,
        0,  # Handle division by zero
    )

    # Sort by percentage change
    movers_df = movers_df.sort_values("pct_change", ascending=False)

    return movers_df


def categorize_movers(
    df: pd.DataFrame,
    circ_threshold_percentile: float = 75,
    change_threshold: float = 1.0,
) -> pd.DataFrame:
    """
    Categorize movers based on circulation size and percentage change.

    Args:
        df: DataFrame with circulation and change data
        circ_threshold_percentile: Percentile to define "large circulation" (default: 75th percentile)
        change_threshold: Percentage change threshold to define "significant change" (default: 1.0%)

    Returns:
        DataFrame with category for each mover
    """
    # Make a copy of the DataFrame
    result_df = df.copy()

    # Determine circulation threshold
    circ_threshold = np.percentile(result_df["circulating"], circ_threshold_percentile)

    # Categorize based on quadrants
    conditions = [
        # Rising Stars: Small circulation + positive change
        (result_df["circulating"] < circ_threshold)
        & (result_df["pct_change"] > change_threshold),
        # Major Growers: Large circulation + positive change
        (result_df["circulating"] >= circ_threshold)
        & (result_df["pct_change"] > change_threshold),
        # Declining Leaders: Large circulation + negative change
        (result_df["circulating"] >= circ_threshold)
        & (result_df["pct_change"] < -change_threshold),
        # Fading Coins: Small circulation + negative change
        (result_df["circulating"] < circ_threshold)
        & (result_df["pct_change"] < -change_threshold),
    ]

    categories = ["Rising Stars", "Major Growers", "Declining Leaders", "Fading Coins"]

    # Default category for those with change within threshold
    result_df["category"] = "Stable"

    # Apply categorization
    result_df["category"] = np.select(conditions, categories, default="Stable")

    return result_df
