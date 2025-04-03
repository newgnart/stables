"""Script to update circulating supply data."""

import asyncio
import argparse
from data.database import SessionLocal
from data.services.supply_service import SupplyService
from config.logging import setup_logging
from config.settings import UPDATE_INTERVAL_MINUTES

logger = setup_logging()


async def update_supply_data():
    """Update circulating supply data."""
    db = SessionLocal()
    try:
        service = SupplyService(db)
        await service.collect_supply_data()
        logger.info("Successfully updated supply data")
    except Exception as e:
        logger.error(f"Error updating supply data: {str(e)}")
    finally:
        await service.close()


async def run_periodically():
    """Run the update periodically."""
    while True:
        await update_supply_data()
        await asyncio.sleep(UPDATE_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update circulating supply data")
    parser.add_argument(
        "--once", action="store_true", help="Run the update once and exit"
    )
    args = parser.parse_args()

    if args.once:
        asyncio.run(update_supply_data())
    else:
        asyncio.run(run_periodically())
