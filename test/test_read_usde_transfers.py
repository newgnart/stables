import pandas as pd
from stables.utils.postgres import get_sqlalchemy_engine
from stables.config import PostgresConfig


def read_usde_erc20_transfers(db_config: PostgresConfig) -> pd.DataFrame:
    """
    Read ethena_marts.usde_erc20_transfers table into a pandas DataFrame.
    
    Args:
        db_config: PostgresConfig instance with database connection parameters
        
    Returns:
        pd.DataFrame: DataFrame containing all rows from ethena_marts.usde_erc20_transfers
        
    Raises:
        Exception: If the table doesn't exist or there's a database connection error
    """
    engine = get_sqlalchemy_engine(db_config)
    query = "SELECT * FROM ethena_marts.usde_erc20_transfers"
    return pd.read_sql(query, engine)


def test_read_usde_erc20_transfers():
    """Test reading usde erc20 transfers data."""
    db_config = PostgresConfig()
    
    try:
        df = read_usde_erc20_transfers(db_config)
        print(f"Successfully read {len(df)} rows from ethena_marts.usde_erc20_transfers")
        print(f"Columns: {list(df.columns)}")
        if not df.empty:
            print(f"Sample data:\n{df.head()}")
        return df
    except Exception as e:
        print(f"Error reading table: {e}")
        return None


if __name__ == "__main__":
    test_read_usde_erc20_transfers()