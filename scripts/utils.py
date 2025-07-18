import os
import logging
import logging.handlers
from stables.data.source import get_contract_creation_txn


def setup_logging(log_file: str):
    """Sets up root logger to log to file and console."""
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


# def get_loaded_block(
#     duckdb_destination: str,
#     table_catalog: str,
#     table_schema: str,
#     table_name: str,
#     chainid: int,
#     address: str,
#     column_name: str = "block_number",
# ):
#     """
#     Get the last loaded block number for a specific address from the database.

#     This function determines the starting point for incremental data loading by finding
#     the highest block number already processed for a given contract address. If no data
#     exists for the address or the database doesn't exist, it falls back to the contract
#     creation block number to ensure complete data coverage.

#     Args:
#         duckdb_destination (str): Path to the DuckDB database file.
#         table_catalog (str): Database catalog name containing the target table.
#         table_schema (str): Schema name containing the target table.
#         table_name (str): Name of the table to query for loaded block numbers.
#         chainid (int): Blockchain chain ID (e.g., 1 for Ethereum mainnet).
#         address (str): Contract address to filter records by.
#         column_name (str, optional): Name of the column containing block numbers.
#             Defaults to "block_number".

#     Returns:
#         int: The highest block number already loaded for the given address,
#              or the contract creation block number if no data exists.

#     Note:
#         - If the database file doesn't exist, returns the contract creation block number
#         - If the table exists but contains no data for the address, returns the contract creation block number
#         - Used primarily for incremental data loading to avoid reprocessing existing data
#     """
#     if os.path.exists(duckdb_destination):
#         conn = duckdb.connect(duckdb_destination)
#         df = conn.execute(
#             f"SELECT MAX(CAST({column_name} AS INTEGER)) FROM {table_catalog}.{table_schema}.{table_name} WHERE address = '{address}'"
#         ).fetchone()
#         conn.close()
#         return (
#             df[0]
#             - 1  # Return the last loaded block minus one to start from the next block
#             if df[0] is not None
#             else int(get_contract_creation_txn(chainid, address)["blockNumber"])
#         )
#     else:
#         return int(get_contract_creation_txn(chainid, address)["blockNumber"])
