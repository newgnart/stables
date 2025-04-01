import pytest
from decimal import Decimal
from app.metrics_processor import MetricsProcessor


def test_empty_events():
    """Test processing of empty events list."""
    result = MetricsProcessor.process_transfer_events([], 6)
    assert result["total_transfer_volume"] == Decimal("0")
    assert result["transfer_count"] == 0


def test_single_event():
    """Test processing of a single transfer event."""
    events = [
        {
            "data": "0x0000000000000000000000000000000000000000000000000000000000000001",  # 1 in hex
        }
    ]
    result = MetricsProcessor.process_transfer_events(events, 6)
    assert result["total_transfer_volume"] == Decimal("0.000001")  # 1 / 10^6
    assert result["transfer_count"] == 1


def test_multiple_events():
    """Test processing of multiple transfer events."""
    events = [
        {
            "data": "0x0000000000000000000000000000000000000000000000000000000000000001",  # 1
        },
        {
            "data": "0x0000000000000000000000000000000000000000000000000000000000000002",  # 2
        },
        {
            "data": "0x0000000000000000000000000000000000000000000000000000000000000003",  # 3
        },
    ]
    result = MetricsProcessor.process_transfer_events(events, 6)
    assert result["total_transfer_volume"] == Decimal("0.000006")  # (1 + 2 + 3) / 10^6
    assert result["transfer_count"] == 3


def test_large_numbers():
    """Test processing of large numbers."""
    events = [
        {
            "data": "0x000000000000000000000000000000000000000000000000000000174876e800",  # 100000000000
        }
    ]
    result = MetricsProcessor.process_transfer_events(events, 6)
    assert result["total_transfer_volume"] == Decimal("100000")  # 100000000000 / 10^6
    assert result["transfer_count"] == 1


def test_missing_data():
    """Test handling of events with missing data."""
    events = [
        {
            "data": "0x0",  # Missing data defaults to 0
        }
    ]
    result = MetricsProcessor.process_transfer_events(events, 6)
    assert result["total_transfer_volume"] == Decimal("0")
    assert result["transfer_count"] == 1
