import json
import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Stablecoin, Chain
from app.stablecoins_loader import load_stablecoins

# Test database URL
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/stables_test"


@pytest.fixture
def test_db():
    """Create a test database and tables."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def test_json_path(tmp_path):
    """Create a temporary JSON file with test data."""
    test_data = {
        "stablecoins": [
            {
                "symbol": "TEST",
                "name": "Test Coin",
                "decimals": 18,
                "type": "test",
                "addresses": {
                    "test_chain": "0x1234567890123456789012345678901234567890"
                },
            }
        ],
        "chains": [
            {
                "name": "test_chain",
                "chain_id": 999,
                "rpc_url": "https://test.example.com",
            }
        ],
    }
    json_path = tmp_path / "test_stablecoins.json"
    with open(json_path, "w") as f:
        json.dump(test_data, f)
    return json_path


def test_load_stablecoins(test_db, test_json_path):
    """Test loading stablecoins and chains into database."""
    # Load the test data
    load_stablecoins(test_db, test_json_path)

    # Check if chain was loaded
    chain = test_db.query(Chain).filter_by(name="test_chain").first()
    assert chain is not None
    assert chain.chain_id == 999
    assert chain.rpc_url == "https://test.example.com"

    # Check if stablecoin was loaded
    coin = test_db.query(Stablecoin).filter_by(symbol="TEST").first()
    assert coin is not None
    assert coin.name == "Test Coin"
    assert coin.decimals == 18
    assert coin.type == "test"
    assert coin.addresses == {
        "test_chain": "0x1234567890123456789012345678901234567890"
    }
