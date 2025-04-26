from stables.core.sources import LlamaStableAPI
from stables.core.transformers import LlamaStableTransformer
from stables.config.logging import setup_logging
import asyncio
from datetime import datetime
import os

logger = setup_logging()
today = datetime.now().strftime("%Y-%m-%d")


async def get_stable_df():
    api = LlamaStableAPI()
    raw_data = await api.get_circulating()
    transformer = LlamaStableTransformer()
    df = transformer.circulating_to_stable_df(raw_data)
    return df


async def main():
    stable_df = await get_stable_df()
    api = LlamaStableAPI()
    if not os.path.exists(f"data/historical/{today}"):
        os.makedirs(f"data/historical/{today}")
    for stable_id in stable_df["id"]:
        raw_data = await api.get_historical(stable_id)
        df = LlamaStableTransformer.historical_to_historical_df(raw_data)
        logger.info(
            f"got historical data for stable_id: {stable_id}, df.lengh: {df.shape[0]}"
        )
        df.to_csv(f"data/historical/{today}/{stable_id}.csv")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
