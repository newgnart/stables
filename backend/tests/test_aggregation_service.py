import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, call
from app.services.aggregation_service import AggregationService
from app.models import Stablecoin, Chain, AggregatedMetrics


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def mock_alchemy_client():
    return Mock()


@pytest.fixture
def mock_chain():
    return Chain(
        id=1,
        name="ethereum",
    )


@pytest.fixture
def mock_stablecoin(mock_chain):
    return Stablecoin(
        id=1,
        name="USDC",
        symbol="USDC",
        contract_address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        decimals=6,
        chain=mock_chain,
    )


@pytest.fixture
def mock_events():
    return [
        {
            "data": "0x0000000000000000000000000000000000000000000000000000000000000001",  # 1
        },
        {
            "data": "0x0000000000000000000000000000000000000000000000000000000000000002",  # 2
        },
    ]


def test_aggregate_hourly_metrics(
    mock_db, mock_alchemy_client, mock_stablecoin, mock_events
):
    """Test hourly metrics aggregation."""
    # Setup
    mock_db.query.return_value.all.return_value = [mock_stablecoin]
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_alchemy_client.get_token_transfers.return_value = mock_events

    # Create service and run aggregation
    service = AggregationService(mock_db, mock_alchemy_client)
    service.aggregate_hourly_metrics()

    # Verify database queries
    assert mock_db.query.call_args_list == [
        call(Stablecoin),
        call(AggregatedMetrics),
    ]

    # Verify Alchemy client calls
    mock_alchemy_client.get_token_transfers.assert_called_once()
    call_args = mock_alchemy_client.get_token_transfers.call_args[1]
    assert call_args["chain"] == "ethereum"
    assert call_args["contract_address"] == mock_stablecoin.contract_address
    assert isinstance(call_args["from_block"], datetime)
    assert isinstance(call_args["to_block"], datetime)

    # Verify database commit
    mock_db.commit.assert_called_once()


def test_update_existing_metrics(
    mock_db, mock_alchemy_client, mock_stablecoin, mock_events
):
    """Test updating existing metrics."""
    # Setup
    mock_db.query.return_value.all.return_value = [mock_stablecoin]
    existing_metrics = AggregatedMetrics(
        stablecoin_id=mock_stablecoin.id,
        timestamp=datetime.utcnow() - timedelta(hours=1),
        total_transfer_volume=Decimal("0"),
        transfer_count=0,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = existing_metrics
    mock_alchemy_client.get_token_transfers.return_value = mock_events

    # Create service and run aggregation
    service = AggregationService(mock_db, mock_alchemy_client)
    service.aggregate_hourly_metrics()

    # Verify metrics were updated
    assert existing_metrics.total_transfer_volume == Decimal(
        "0.000003"
    )  # (1 + 2) / 10^6
    assert existing_metrics.transfer_count == 2

    # Verify no new metrics were added
    mock_db.add.assert_not_called()
