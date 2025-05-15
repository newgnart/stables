from stables.data.defillama_api import DeFiLlamaAPI
from stables.transform.defillama_transform import DeFiLlamaTransformer
import json


def main():
    defillama_api = DeFiLlamaAPI()

    yield_pools = defillama_api.fetch_yield_pools()
    with open("data/raw/yield_pools.json", "w") as f:
        json.dump(yield_pools, f)

    yield_pools_df = DeFiLlamaTransformer.yield_pools_to_df(yield_pools)
    yield_pools_df.to_csv("data/processed/yield_pools.csv", index=False)


if __name__ == "__main__":
    main()
