from stables.utils.postgres import PostgresConfig, get_loaded_block
from stables.utils.logging import setup_streaming_logging
import logging

logger = logging.getLogger(__name__)

setup_streaming_logging()


def test_get_loaded_block():
    db_config = PostgresConfig()
    table_schema = "ethena_raw"
    table_name = "usde_contract_logs"
    chainid = 1
    contract_address = "0x4c9edd5852cd905f086c759e8383e09bff1e68b3"
    column_name = "block_number"
    loaded_block = get_loaded_block(
        db_config, table_schema, table_name, chainid, contract_address, column_name
    )

    logger.info(f"Loaded block: {loaded_block}")


if __name__ == "__main__":
    test_get_loaded_block()
