from stables.data.defillama_api import DeFiLlamaAPI
from stables.transform.defillama_transform import DeFiLlamaTransformer
import json


def get_yield_pools():
    defillama_api = DeFiLlamaAPI()
    yield_pools = defillama_api.fetch_yield_pools()
    with open("data/raw/yield_pools.json", "w") as f:
        json.dump(yield_pools, f)

    yield_pools_df = DeFiLlamaTransformer.yield_pools_to_df(yield_pools)
    yield_pools_df.to_csv("data/processed/yield_pools.csv", index=False)


def get_yield_pool(pool: str):
    defillama_api = DeFiLlamaAPI()
    yield_pool = defillama_api.fetch_yield_pool(pool)
    with open(f"data/raw/yield_pool_{pool}.json", "w") as f:
        json.dump(yield_pool, f)
    yield_pool_df = DeFiLlamaTransformer.yield_pool_to_df(yield_pool)
    yield_pool_df.to_csv(f"data/processed/yield_pool_{pool}.csv", index=False)


if __name__ == "__main__":
    # get_yield_pools()
    get_yield_pool("5fd328af-4203-471b-bd16-1705c726d926")
