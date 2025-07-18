import os, json, time, logging
import dlt
import psycopg2
from utils import setup_logging, get_loaded_block
from stables.data.source import etherscan_logs, get_latest_block

logger = logging.getLogger(__name__)
setup_logging(log_file="logs/ethena_dlt_pipeline.log")


def load_logs(
    contract_address,
    table_name,
    chainid,
    pipeline,
    table_catalog,
    table_schema,
    block_chunk_size=100000,
    start_block=None,
    end_block=None,
):
    if start_block is None:
        start_block = get_loaded_block(
            None,  # No longer need file path for PostgreSQL
            table_catalog,
            table_schema,
            table_name,
            chainid,
            contract_address,
            column_name="block_number",
        )
    if end_block is None:
        end_block = get_latest_block(chainid=chainid)

    for from_block in range(start_block, end_block, block_chunk_size):
        to_block = str(min(from_block + block_chunk_size - 1, end_block))
        logger.info(f"Loading logs from block {from_block} to {to_block}")

        max_retries = 2
        retries = max_retries
        while retries > 0:
            try:
                conn = psycopg2.connect(
                    host=os.getenv("POSTGRES_HOST", "localhost"),
                    port=int(os.getenv("POSTGRES_PORT", "5432")),
                    database=os.getenv("POSTGRES_DB"),
                    user=os.getenv("POSTGRES_USER"),
                    password=os.getenv("POSTGRES_PASSWORD"),
                )
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_schema}.{table_name}")
                n_before = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                pipeline.run(
                    etherscan_logs(
                        chainid=chainid,
                        address=contract_address,
                        fromBlock=from_block,
                        toBlock=to_block,
                    ),
                    table_name=table_name,
                    write_disposition="append",
                )
                conn = psycopg2.connect(
                    host=os.getenv("POSTGRES_HOST", "localhost"),
                    port=int(os.getenv("POSTGRES_PORT", "5432")),
                    database=os.getenv("POSTGRES_DB"),
                    user=os.getenv("POSTGRES_USER"),
                    password=os.getenv("POSTGRES_PASSWORD"),
                )
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_schema}.{table_name}")
                n_after = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                if n_after - n_before == 1000:
                    logger.warning(
                        f"Loaded 1000 logs from {from_block} to {to_block}, smaller batch size may be needed."
                    )
                else:
                    logger.info(
                        f"Loaded {n_after - n_before} logs from {from_block} to {to_block}"
                    )
                break  # Succeeded
            except Exception as e:
                retries -= 1
                logger.error(
                    f"Error loading logs: {e}. Retrying... ({retries} retries left)"
                )
                if retries > 0:
                    time.sleep(3)
                else:
                    logger.error(
                        f"Failed to load logs for block range {from_block}-{to_block} after {max_retries} retries."
                    )
        time.sleep(0.2)


def backfill_logs():
    table_catalog = "raw_ethena"
    table_schema = "usde"
    table_name = "logs"
    chainid = 1
    pipeline = dlt.pipeline(
        pipeline_name="ethena",
        destination=dlt.destinations.postgres(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB"),
            username=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        ),
        dataset_name=table_schema,
    )
    contract_address = "0x4c9EDD5852cd905f086C759E8383e09bff1E68B3".lower()
    load_logs(
        contract_address,
        table_name,
        chainid,
        pipeline,
        table_catalog,
        table_schema,
        block_chunk_size=1000,
        end_block=21_000_000,
    )


if __name__ == "__main__":
    backfill_logs()
