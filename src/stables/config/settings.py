"""Application settings and configuration."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database settings
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "stables")

# API settings
API_PREFIX = "/api"
API_VERSION = "v1"
API_TITLE = "Stablecoin Data API"
API_DESCRIPTION = "API for accessing stablecoin data"

# Data update settings
UPDATE_INTERVAL_MINUTES = int(
    os.getenv("UPDATE_INTERVAL_MINUTES", "60")
)  # Default to 1 hour
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))

# DeFiLlama settings
DEFILLAMA_STABLECOINS_API_URL = "https://stablecoins.llama.fi"
DEFILLAMA_TIMEOUT = int(os.getenv("DEFILLAMA_TIMEOUT", "30"))  # seconds

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", "app.log")
