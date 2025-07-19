import logging
import dlt


from stables.utils.logging import setup_file_logging, setup_streaming_logging
from stables.config import PostgresConfig
from stables.data.load.logs import logs_loading

logger = logging.getLogger(__name__)
setup_file_logging(log_file="logs/ethena_dlt_pipeline.log")
setup_streaming_logging()


def backfill_logs(
    table_schema: str = "ethena_raw", table_name: str = "usde_contract_logs"
):
    """Backfill logs for a usde on ethereum contract address using DLT pipeline."""

    db_config = PostgresConfig()
    table_schema = table_schema
    pipeline = dlt.pipeline(
        pipeline_name="ethena",
        destination=dlt.destinations.postgres(**db_config.get_dlt_connection_params()),
        dataset_name=table_schema,
    )

    table_name = table_name
    chainid = 1
    contract_address = "0x4c9edd5852cd905f086c759e8383e09bff1e68b3"

    logs_loading(
        pipeline=pipeline,
        db_config=db_config,
        table_schema=table_schema,
        table_name=table_name,
        chainid=chainid,
        contract_address=contract_address,
        start_block=None,
        end_block=19_510_000,
        block_chunk_size=1_000,
    )


if __name__ == "__main__":
    backfill_logs()
