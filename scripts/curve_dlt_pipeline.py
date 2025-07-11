import os, json, time, logging
import dlt, duckdb
from utils import setup_logging, get_loaded_block
from stables.data.source import etherscan_logs, get_latest_block

logger = logging.getLogger(__name__)
setup_logging(log_file="logs/curve_dlt_pipeline.log")


def backfill_logs():
    duckdb_destination = "data/raw/raw_curve.duckdb"
    table_catalog = "raw_curve"
    table_schema = "crvusd_market"
    table_name = "logs"
    chainid = 1
    block_chunk_size = 100000
    pipeline = dlt.pipeline(
        pipeline_name="curve",
        destination=dlt.destinations.duckdb(duckdb_destination),
        dataset_name=table_schema,
    )
    with open("data/address/curve_addresses.json", "r") as f:
        addresses = json.load(f)
    controller_addresses = [
        addresses["crvusd_market"][x]["controller"] for x in addresses["crvusd_market"]
    ]

    end_block = get_latest_block(chainid=chainid)
    for controller_address in controller_addresses[4:]:
        start_block = get_loaded_block(
            duckdb_destination,
            table_catalog,
            table_schema,
            table_name,
            chainid,
            controller_address,
            column_name="block_number",
        )
        for from_block in range(start_block, end_block, block_chunk_size):
            to_block = str(min(from_block + block_chunk_size - 1, end_block))
            logger.info(f"Loading logs from block {from_block} to {to_block}")

            max_retries = 2
            retries = max_retries
            while retries > 0:
                try:
                    load_info = pipeline.run(
                        etherscan_logs(
                            chainid=chainid,
                            address=controller_address,
                            fromBlock=from_block,
                            toBlock=to_block,
                        ),
                        table_name=table_name,
                        write_disposition="append",
                    )
                    logger.info(load_info)
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
        time.sleep(10)


if __name__ == "__main__":
    backfill_logs()
