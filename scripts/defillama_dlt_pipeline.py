import os, json, time, logging
import dlt, duckdb
from utils import setup_logging
from stables.data.source import (
    defillama_stables_base,
    defillama_stables_chain_circulating,
    defillama_stablecoin_chain_tokens,
    defillama_yield_pools,
)

logger = logging.getLogger(__name__)
setup_logging(log_file="logs/defillama_dlt_pipeline.log")


def defillama_stables_pipeline():
    """
    Runs the DeFiLlama stablecoins pipeline and displays the loaded data.
    """
    duckdb_destination = "data/raw/raw_defillama.duckdb"
    pipeline = dlt.pipeline(
        pipeline_name="defillama_stables",
        destination=dlt.destinations.duckdb(duckdb_destination),
        dataset_name="yields",
    )

    # Run the pipeline
    # pipeline.run(
    #     defillama_stables_base(), table_name="base", write_disposition="replace"
    # )
    # pipeline.run(
    #     defillama_stables_chain_circulating(),
    #     table_name="chain_circulating",
    #     write_disposition="replace",
    # )

    # pipeline.run(
    #     defillama_stablecoin_chain_tokens(stablecoin_id=110),
    #     table_name="chain_tokens",
    #     write_disposition="replace",
    # )

    pipeline.run(
        defillama_yield_pools(),
        table_name="all_pools",
        write_disposition="replace",
    )


if __name__ == "__main__":
    defillama_stables_pipeline()
