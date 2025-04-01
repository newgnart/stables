from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.services.aggregation_service import AggregationService
from app.database import SessionLocal
from app.blockchain.alchemy_client import AlchemyClient
import os


class SchedulerService:
    """Service for managing scheduled tasks."""

    def __init__(self, alchemy_client: AlchemyClient = None):
        self.scheduler = BackgroundScheduler()
        self.aggregation_service = None
        self.alchemy_client = alchemy_client or AlchemyClient(
            api_key=os.getenv("ALCHEMY_API_KEY")
        )

    def start(self) -> None:
        """Start the scheduler and schedule the hourly aggregation job."""
        # Create a new database session for the scheduler
        db = SessionLocal()
        self.aggregation_service = AggregationService(db, self.alchemy_client)

        # Schedule hourly aggregation job
        self.scheduler.add_job(
            self._run_aggregation,
            CronTrigger(minute=0),  # Run at the start of every hour
            id="hourly_aggregation",
            name="Aggregate hourly transfer metrics",
        )

        # Start the scheduler
        self.scheduler.start()

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()

    def _run_aggregation(self) -> None:
        """Run the hourly aggregation job."""
        try:
            self.aggregation_service.aggregate_hourly_metrics()
        except Exception as e:
            # Log the error (you might want to add proper logging here)
            print(f"Error running hourly aggregation: {str(e)}")
