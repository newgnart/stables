from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.services.scheduler_service import SchedulerService
from app.blockchain.alchemy_client import AlchemyClient
import os

app = FastAPI(
    title="Stablecoin Metrics API",
    description="API for accessing stablecoin transfer metrics",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Initialize scheduler service
scheduler_service = SchedulerService(
    alchemy_client=AlchemyClient(api_key=os.getenv("ALCHEMY_API_KEY"))
)


@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the application starts."""
    scheduler_service.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler when the application shuts down."""
    scheduler_service.stop()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Stablecoin Metrics API",
        "version": "1.0.0",
    }
