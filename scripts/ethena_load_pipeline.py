import logging
import dlt
from dotenv import load_dotenv
from stables.utils.logging import setup_logging
from stables.data.source.defillama import stable_circulating, yield_pools, yield_pool

logger = logging.getLogger(__name__)
setup_logging()
load_dotenv()


def load_circulating(coin_id):
    """
    Loads the circulating data for a specific stablecoin by ID into the DLT pipeline.
    """
    pipeline = dlt.pipeline(
        pipeline_name="ethena_defillama",
        destination="postgres",
        dataset_name="ethena_raw",
    )

    pipeline.run(
        stable_circulating(coin_id),
        table_name=f"circulating",
        write_disposition="merge",
        primary_key=["id", "date", "chain"],
    )


def load_yield_pool(pool_id: str):
    """
    Loads the yield pool data for a specific pool ID into the DLT pipeline.
    """
    pipeline = dlt.pipeline(
        pipeline_name="ethena_defillama",
        destination="postgres",
        dataset_name="ethena_raw",
    )

    pipeline.run(
        yield_pool(pool_id),
        table_name=f"susde_pool",
        # write_disposition="merge",
        # primary_key=["id", "date", "chain"],
    )


def load_all_yield_pools():
    """
    Runs the DeFiLlama yield pools pipeline and displays the loaded data.
    """
    pipeline = dlt.pipeline(
        pipeline_name="ethena_defillama",
        destination="postgres",
        dataset_name="yields",
    )

    pipeline.run(
        yield_pools(),
        table_name="all_yield_pools",
        write_disposition="replace",
    )


if __name__ == "__main__":
    # circulating(146)
    # circulating(221)
    # all_yield_pools()
    susde_staking_pool_defillama_id = "66985a81-9c51-46ca-9977-42b4fe7bc6df"
    load_yield_pool(susde_staking_pool_defillama_id)
