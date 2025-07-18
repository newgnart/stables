import os, json, time, logging
import dlt
from utils import setup_logging
from stables.data.source import (
    defillama_stables_base,
    defillama_stables_chain_circulating,
    defillama_stablecoin_chain_tokens,
    defillama_yield_pools,
)

logger = logging.getLogger(__name__)
setup_logging(log_file="logs/defillama_dlt_pipeline.log")
from dotenv import load_dotenv

load_dotenv()


def defillama_stables_pipeline():
    """
    Runs the DeFiLlama stablecoins pipeline and displays the loaded data.
    """
    # DLT will now use the credentials from .dlt/secrets.toml
    pipeline = dlt.pipeline(
        pipeline_name="defillama_stables",
        destination="postgres",
        dataset_name="yields",
    )

    pipeline.run(
        defillama_yield_pools(),
        table_name="all_pools",
        write_disposition="replace",
    )


if __name__ == "__main__":
    defillama_stables_pipeline()
    # check_variables()
