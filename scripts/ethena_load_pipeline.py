import logging
from dotenv import load_dotenv
import dlt
from stables.utils.logging import setup_logging
from stables.data import (
    load_stables_metadata,
    load_token_price,
    load_protocol_revenue,
    load_stable_circulating,
    load_all_yield_pools,
    load_yield_pool,
)
from stables.data.load.etherscan import logs
from stables.config import local_pg_config

logger = logging.getLogger(__name__)
setup_logging()
load_dotenv()


def load_logs(table_schema: str, table_name: str, contract_address: str, chainid: int):
    """Backfill logs for a usde on ethereum contract address using DLT pipeline."""

    pg_config = local_pg_config
    destination = dlt.destinations.postgres(
        f"postgresql://{pg_config.user}:{pg_config.password}@{pg_config.host}:{pg_config.port}/{pg_config.database}"
    )

    pipeline = dlt.pipeline(
        pipeline_name="ethena_etherscan",
        destination=destination,
        dataset_name=table_schema,
    )
    logs(
        pipeline=pipeline,
        pg_config=pg_config,
        table_schema=table_schema,
        table_name=table_name,
        chainid=chainid,
        contract_address=contract_address,
        start_block=None,
        # end_block=22_000_000,
        block_chunk_size=50_000,
    )


def llama():

    pg_config = local_pg_config

    # llama
    ## 1. stables metadata ✅
    load_stables_metadata(pg_config)

    ## 2. circulating ✅
    ## load historical first time
    # load_stable_circulating(id=146, pg_config=pg_config, get_response="chainBalances")
    # load_stable_circulating(id=221, pg_config=pg_config, get_response="chainBalances")

    ### next times just get currentChainBalances
    load_stable_circulating(id=146, pg_config=pg_config)
    load_stable_circulating(id=221, pg_config=pg_config)

    # # # 3. token price ✅
    network = "ethereum"
    contract_address = "0x57e114B691Db790C35207b2e685D4A43181e6061"
    # # ### First time load with default params {"span": 1000, "period": "1d"}
    # # load_token_price(network, contract_address, pg_config)  # 477
    # # ### Next time with smaller span, 10 would overlap but fine
    load_token_price(
        network, contract_address, pg_config, params={"span": 10, "period": "1d"}
    )

    # # # # 4. protocol revenue ✅
    # # # both first time and ongoing use same params, merge with primary_key will take care
    load_protocol_revenue(protocol="ethena", pg_config=pg_config)

    # # ## 5. all yield_pools ✅
    load_all_yield_pools(pg_config=pg_config)

    # # 6. yield
    # # susde_staking_pool_defillama_id = "66985a81-9c51-46ca-9977-42b4fe7bc6df"
    load_yield_pool(
        pool_id="66985a81-9c51-46ca-9977-42b4fe7bc6df",
        pool_name="susde",
        pg_config=pg_config,
    )


if __name__ == "__main__":
    # llama()
    load_logs(
        table_schema="ethena_raw",
        table_name="mint_redeem_v2_contract_logs",
        chainid=1,
        # contract_address="0x2CC440b721d2CaFd6D64908D6d8C4aCC57F8Afc3".lower(),
        contract_address="0xe3490297a08d6fC8Da46Edb7B6142E4F461b62D3".lower(),
    )
