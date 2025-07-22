import logging
from dotenv import load_dotenv
from stables.utils.logging import setup_logging
from stables.data import (
    load_stables_metadata,
    load_token_price,
    load_protocol_revenue,
    load_stable_circulating,
    load_all_yield_pools,
    load_yield_pool,
)
from stables.config import local_pg_config

logger = logging.getLogger(__name__)
setup_logging()
load_dotenv()


if __name__ == "__main__":

    pg_config = local_pg_config

    # llama
    ## 1. stables metadata ✅
    load_stables_metadata(pg_config)

    ## 2. circulating ✅
    ## load historical first time
    load_stable_circulating(id=146, pg_config=pg_config, get_response="chainBalances")
    ### next times just get currentChainBalances
    # load_stable_circulating(id=146, pg_config=pg_config)

    # # # 3. token price ✅
    network = "ethereum"
    contract_address = "0x57e114B691Db790C35207b2e685D4A43181e6061"
    # ### First time load with default params {"span": 1000, "period": "1d"}
    load_token_price(network, contract_address, pg_config)  # 477
    # ### Next time with smaller span, 10 would overlap but fine
    # load_token_price(
    #     network, contract_address, pg_config, params={"span": 10, "period": "1d"}
    # )

    # # # 4. protocol revenue ✅
    # # both first time and ongoing use same params, merge with primary_key will take care
    load_protocol_revenue(protocol="ethena", pg_config=pg_config)

    # ## 5. all yield_pools ✅
    load_all_yield_pools(pg_config=pg_config)

    # 6. yield
    # susde_staking_pool_defillama_id = "66985a81-9c51-46ca-9977-42b4fe7bc6df"
    load_yield_pool(
        pool_id="66985a81-9c51-46ca-9977-42b4fe7bc6df",
        pool_name="susde",
        pg_config=pg_config,
    )
