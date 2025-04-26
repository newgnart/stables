import pandas as pd


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
