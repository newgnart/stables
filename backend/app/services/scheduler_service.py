from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.services.aggregation_service import AggregationService
from app.services.supply_service import SupplyService
from app.database import SessionLocal
from app.blockchain.alchemy_client import AlchemyClient
import os
import asyncio


class SchedulerService:
    """Service for managing scheduled tasks."""

    def __init__(self, alchemy_client: AlchemyClient = None):
        self.scheduler = BackgroundScheduler()
        self.aggregation_service = None
        self.supply_service = None
        self.alchemy_client = alchemy_client or AlchemyClient(
            api_key=os.getenv("ALCHEMY_API_KEY")
        )

    def start(self) -> None:
        """Start the scheduler and schedule the hourly jobs."""
        # Create a new database session for the scheduler
        db = SessionLocal()
        self.aggregation_service = AggregationService(db, self.alchemy_client)
        self.supply_service = SupplyService(db)

        # Schedule hourly aggregation job
        self.scheduler.add_job(
            self._run_aggregation,
            CronTrigger(minute=0),  # Run at the start of every hour
            id="hourly_aggregation",
            name="Aggregate hourly transfer metrics",
        )

        # Schedule hourly supply data collection
        self.scheduler.add_job(
            self._run_supply_collection,
            CronTrigger(minute=0),  # Run at the start of every hour
            id="hourly_supply_collection",
            name="Collect hourly supply data",
        )

        # Start the scheduler
        self.scheduler.start()

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            # Close the supply service
            asyncio.run(self.supply_service.close())

    def _run_aggregation(self) -> None:
        """Run the hourly aggregation job."""
        try:
            self.aggregation_service.aggregate_hourly_metrics()
        except Exception as e:
            # Log the error (you might want to add proper logging here)
            print(f"Error running hourly aggregation: {str(e)}")

    def _run_supply_collection(self) -> None:
        """Run the hourly supply data collection job."""
        try:
            asyncio.run(self.supply_service.collect_supply_data())
        except Exception as e:
            # Log the error (you might want to add proper logging here)
            print(f"Error running supply collection: {str(e)}")
