import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models import Chain, Stablecoin, AggregatedMetrics
from app.database import get_db, SessionLocal, engine, Base


@pytest.fixture(scope="session")
def db():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_chain(db: Session):
    """Get or create a test chain."""
    chain = db.query(Chain).filter_by(name="ethereum").first()
    if not chain:
        chain = Chain(
            name="ethereum",
            chain_id=1,
        )
        db.add(chain)
        db.commit()
        db.refresh(chain)
    return chain


@pytest.fixture
def test_stablecoin(db: Session, test_chain: Chain):
    """Get or create a test stablecoin."""
    stablecoin = db.query(Stablecoin).filter_by(symbol="USDC").first()
    if not stablecoin:
        stablecoin = Stablecoin(
            symbol="USDC",
            name="USD Coin",
            decimals=6,
            contract_address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            chain_id=test_chain.id,
        )
        db.add(stablecoin)
        db.commit()
        db.refresh(stablecoin)
    return stablecoin


@pytest.fixture
def test_metrics(db: Session, test_stablecoin: Stablecoin):
    """Create test metrics."""
    # First, delete any existing metrics for this stablecoin
    db.query(AggregatedMetrics).filter_by(stablecoin_id=test_stablecoin.id).delete()
    db.commit()

    metrics = []
    for i in range(3):
        metric = AggregatedMetrics(
            stablecoin_id=test_stablecoin.id,
            timestamp=datetime.utcnow() - timedelta(hours=i),
            total_transfer_volume=1000.0 * (i + 1),
            transfer_count=100 * (i + 1),
        )
        db.add(metric)
        metrics.append(metric)
    db.commit()
    return metrics


def test_get_metrics_no_filters(client: TestClient, test_metrics):
    """Test getting metrics without filters."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(test_metrics)
    assert all(metric["symbol"] == "USDC" for metric in data)


def test_get_metrics_with_stablecoin_filter(client: TestClient, test_metrics):
    """Test getting metrics with stablecoin filter."""
    response = client.get("/api/metrics?stablecoin=USDC")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(test_metrics)
    assert all(metric["symbol"] == "USDC" for metric in data)


def test_get_metrics_with_chain_filter(client: TestClient, test_metrics):
    """Test getting metrics with chain filter."""
    response = client.get("/api/metrics?chain=ethereum")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(test_metrics)
    assert all(metric["chain_name"] == "ethereum" for metric in data)


def test_get_metrics_with_time_range(client: TestClient, test_metrics):
    """Test getting metrics with time range filter."""
    now = datetime.utcnow()
    start_time = now - timedelta(hours=2)
    end_time = now + timedelta(hours=1)

    response = client.get(
        f"/api/metrics?start_time={start_time.isoformat()}&end_time={end_time.isoformat()}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Only metrics within the last 2 hours


def test_get_metrics_empty_result(client: TestClient, db: Session):
    """Test getting metrics when no data exists."""
    # Clean up any existing data
    db.query(AggregatedMetrics).delete()
    db.commit()

    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_get_metrics_invalid_stablecoin(client: TestClient):
    """Test getting metrics with invalid stablecoin."""
    response = client.get("/api/metrics?stablecoin=INVALID")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_get_metrics_invalid_chain(client: TestClient):
    """Test getting metrics with invalid chain."""
    response = client.get("/api/metrics?chain=INVALID")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
