#!/usr/bin/env python3
"""Script to test DeFiLlama API client functionality."""

import asyncio
import json
from data.sources.defillama import DeFiLlamaStablecoinsClient
from data.transformers.defillama_transformer import DeFiLlamaTransformer
from config.logging import setup_logging

logger = setup_logging()


async def main():
    """Main function to test DeFiLlama client."""
    # Initialize client and transformer
    client = DeFiLlamaStablecoinsClient()
    transformer = DeFiLlamaTransformer()

    # Fetch raw data
    logger.info("Fetching data from DeFiLlama...")

    circulating = await client.get_circulating()

    # Save raw data
    with open("circulating.json", "w") as f:
        json.dump(circulating, f)

    # Transform data
    logger.info("Transforming data...")
    stablecoin_df = transformer.to_stablecoin_df(circulating)

    print(stablecoin_df)

    chain_circulating_df = transformer.to_chain_circulating_df(circulating)
    print(chain_circulating_df)


if __name__ == "__main__":
    asyncio.run(main())
