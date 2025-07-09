import os
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
}
