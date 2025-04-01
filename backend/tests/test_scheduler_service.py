import pytest
from unittest.mock import Mock, patch
from app.services.scheduler_service import SchedulerService


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def mock_alchemy_client():
    return Mock()


def test_scheduler_initialization(mock_alchemy_client):
    """Test scheduler service initialization."""
    service = SchedulerService(alchemy_client=mock_alchemy_client)
    assert service.scheduler is not None
    assert service.aggregation_service is None


def test_scheduler_start(mock_db, mock_alchemy_client):
    """Test starting the scheduler."""
    with patch(
        "app.services.scheduler_service.SessionLocal"
    ) as mock_session_local, patch(
        "app.services.scheduler_service.AggregationService"
    ) as mock_aggregation_service:
        # Setup mocks
        mock_session_local.return_value = mock_db
        mock_aggregation_service.return_value = Mock()

        # Create and start service
        service = SchedulerService(alchemy_client=mock_alchemy_client)
        service.start()

        # Verify scheduler is running
        assert service.scheduler.running

        # Verify job was added
        jobs = service.scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].id == "hourly_aggregation"
        assert jobs[0].name == "Aggregate hourly transfer metrics"


def test_scheduler_stop(mock_alchemy_client):
    """Test stopping the scheduler."""
    service = SchedulerService(alchemy_client=mock_alchemy_client)
    service.start()
    assert service.scheduler.running

    service.stop()
    assert not service.scheduler.running


def test_run_aggregation_success(mock_alchemy_client):
    """Test successful aggregation run."""
    with patch(
        "app.services.scheduler_service.AggregationService"
    ) as mock_aggregation_service:
        # Setup mock
        mock_aggregation_service.return_value = Mock()

        # Create service and run aggregation
        service = SchedulerService(alchemy_client=mock_alchemy_client)
        service.aggregation_service = mock_aggregation_service.return_value
        service._run_aggregation()

        # Verify aggregation was called
        mock_aggregation_service.return_value.aggregate_hourly_metrics.assert_called_once()


def test_run_aggregation_error(mock_alchemy_client):
    """Test error handling during aggregation run."""
    with patch(
        "app.services.scheduler_service.AggregationService"
    ) as mock_aggregation_service:
        # Setup mock to raise an exception
        mock_aggregation_service.return_value = Mock()
        mock_aggregation_service.return_value.aggregate_hourly_metrics.side_effect = (
            Exception("Test error")
        )

        # Create service and run aggregation
        service = SchedulerService(alchemy_client=mock_alchemy_client)
        service.aggregation_service = mock_aggregation_service.return_value
        service._run_aggregation()

        # Verify aggregation was called
        mock_aggregation_service.return_value.aggregate_hourly_metrics.assert_called_once()
