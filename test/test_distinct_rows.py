"""
Logging distinct rows from a table to if it matches the expected number of logs/transactions.
"""

from stables.utils.postgres import get_postgres_connection
from stables.config import PostgresConfig
from stables.utils.logging import setup_streaming_logging
import logging

setup_streaming_logging()
logger = logging.getLogger(__name__)


def logs_raw(table_schema: str, table_name: str):
    """Get distinct row count and block range using direct SQL queries."""

    db_config = PostgresConfig()

    with get_postgres_connection(db_config) as conn:
        cursor = conn.cursor()

        # First, get all columns to see what we're working with
        cursor.execute(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s 
            ORDER BY ordinal_position
        """,
            (table_schema, table_name),
        )

        all_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"All columns in {table_schema}.{table_name}: {all_columns}")

        # Filter out DLT metadata columns
        columns = [c for c in all_columns if not c.startswith("_dlt") and "__" not in c]

        if not columns:
            logger.warning(f"No non-DLT columns found in {table_schema}.{table_name}")
            return

        columns_str = ", ".join(columns)
        logger.info(f"Using columns: {columns_str}")

        # Get distinct count
        distinct_query = f"SELECT COUNT(*) FROM (SELECT DISTINCT {columns_str} FROM {table_schema}.{table_name}) as distinct_rows"
        cursor.execute(distinct_query)
        distinct_count = cursor.fetchone()[0]

        # Get block range
        cursor.execute(
            f"SELECT MIN(block_number), MAX(block_number) FROM {table_schema}.{table_name}"
        )
        min_block, max_block = cursor.fetchone()

        cursor.close()

    logger.info(
        f"{distinct_count} distinct rows in table {table_schema}.{table_name}, from block {min_block} to {max_block}"
    )


if __name__ == "__main__":
    logs_raw(table_schema="ethena_raw", table_name="usde_contract_logs")
