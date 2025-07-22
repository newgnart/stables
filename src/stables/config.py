import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()


ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
COINGECKO_PRICES_COLUMNS = {
    "timestamp": {"data_type": "timestamp", "timezone": False, "precision": 3},
    "price": {"data_type": "decimal"},
}

COINGECKO_OHLC_COLUMNS = {
    "timestamp": {"data_type": "timestamp", "timezone": False, "precision": 3},
    "open": {"data_type": "decimal"},
    "high": {"data_type": "decimal"},
    "low": {"data_type": "decimal"},
    "close": {"data_type": "decimal"},
}


class API_URL:
    Etherscan = "https://api.etherscan.io/v2/api"
    Coingecko = "https://api.coingecko.com/api/v3"
    DeFiLlamaStablecoins = "https://stablecoins.llama.fi"
    DeFiLlamaYields = "https://yields.llama.fi"


class BlockExplorerColumns:
    Log = {
        "topics": {"data_type": "json"},
        "block_number": {"data_type": "bigint"},
        "time_stamp": {"data_type": "bigint"},
        "gas_price": {"data_type": "bigint"},
        "gas_used": {"data_type": "bigint"},
        "log_index": {"data_type": "bigint"},
        "transaction_index": {"data_type": "bigint"},
    }
    Transaction = {
        "block_number": {"data_type": "bigint"},
        "time_stamp": {"data_type": "timestamp"},
    }


class PostgresConfig:
    """PostgreSQL configuration manager that reads from environment variables."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        database: str = None,
        username: str = None,
        password: str = None,
    ):
        """Initializes the PostgresConfig with environment variables or provided parameters."""
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    def get_connection_params(self) -> Dict[str, Any]:
        """Return connection parameters for psycopg2."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "username": self.username,
            "password": self.password,
        }


local_pg_config = PostgresConfig(
    host=os.getenv("LOCAL_POSTGRES_HOST"),
    port=int(os.getenv("LOCAL_POSTGRES_PORT")),
    database=os.getenv("LOCAL_POSTGRES_DB"),
    username=os.getenv("LOCAL_POSTGRES_USER"),
    password=os.getenv("LOCAL_POSTGRES_PASSWORD"),
)

remote_pg_config = PostgresConfig(
    host=os.getenv("REMOTE_POSTGRES_HOST"),
    port=int(os.getenv("REMOTE_POSTGRES_PORT")),
    database=os.getenv("REMOTE_POSTGRES_DB"),
    username=os.getenv("REMOTE_POSTGRES_USER"),
    password=os.getenv("REMOTE_POSTGRES_PASSWORD"),
)
