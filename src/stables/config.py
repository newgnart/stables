import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_BASE_URL = "https://api.etherscan.io/v2/api"
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

ETHERSCAN_TRANSACTION_COLUMNS = {
    "block_number": {"data_type": "bigint"},
    "time_stamp": {"data_type": "timestamp"},
}

COINGECKO_API_BASE_URL = "https://api.coingecko.com/api/v3"
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

ETHERSCAN_LOG_COLUMNS = {
    "topics": {"data_type": "json"},
    "block_number": {"data_type": "bigint"},
    "time_stamp": {"data_type": "bigint"},
    "gas_price": {"data_type": "bigint"},
    "gas_used": {"data_type": "bigint"},
    "log_index": {"data_type": "bigint"},
    "transaction_index": {"data_type": "bigint"},
}


class PostgresConfig:
    """PostgreSQL configuration manager that reads from environment variables."""

    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.database = os.getenv("POSTGRES_DB")
        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")

    def get_connection_params(self) -> Dict[str, Any]:
        """Return connection parameters as a dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
        }

    def get_dlt_connection_params(self) -> Dict[str, Any]:
        """Return connection parameters formatted for DLT destination."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "username": self.user,  # DLT uses 'username' instead of 'user'
            "password": self.password,
        }
