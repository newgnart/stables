"""Script to update circulating supply data."""

import asyncio
import argparse
from stables.core.database import SessionLocal
from stables.core.services import LlamaService
from stables.config.logging import setup_logging
from stables.config.settings import UPDATE_INTERVAL_MINUTES

logger = setup_logging()


async def update_llama_data():
    """Update circulating supply data."""
    db = SessionLocal()
    try:
        service = LlamaService(db)
        await service.add_circulating_data()
        logger.info("Successfully updated llama data")
    except Exception as e:
        logger.error(f"Error updating llama data: {str(e)}")
    finally:
        await service.close()


async def run_periodically():
    """Run the update periodically."""
    while True:
        await update_llama_data()
        await asyncio.sleep(UPDATE_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update circulating supply data")
    parser.add_argument(
        "--once", action="store_true", help="Run the update once and exit"
    )
    args = parser.parse_args()

    if args.once:
        asyncio.run(update_llama_data())
    else:
        asyncio.run(run_periodically())
