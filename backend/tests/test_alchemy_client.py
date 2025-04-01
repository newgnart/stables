import pytest
from unittest.mock import patch, MagicMock
from web3 import Web3
from app.blockchain.alchemy_client import AlchemyClient
from app.models import Chain


@pytest.fixture
def alchemy_client():
    return AlchemyClient(api_key="test_api_key")


@pytest.fixture
def mock_chain():
    return Chain(
        name="Ethereum",
        chain_id=1,
        rpc_url="https://eth-mainnet.g.alchemy.com/v2/test_api_key",
    )


def test_init(alchemy_client):
    assert alchemy_client.api_key == "test_api_key"
    assert alchemy_client.base_url == "https://eth-mainnet.g.alchemy.com/v2"
    assert alchemy_client.rate_limit_delay == 0.1


@patch("requests.post")
def test_make_request(mock_post, alchemy_client):
    # Mock successful response
    mock_response = MagicMock()
    mock_response.json.return_value = {"jsonrpc": "2.0", "id": 1, "result": "0x123"}
    mock_post.return_value = mock_response

    result = alchemy_client._make_request("eth_blockNumber", [])
    assert result == "0x123"

    # Mock error response
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"message": "API Error"},
    }
    with pytest.raises(Exception) as exc_info:
        alchemy_client._make_request("eth_blockNumber", [])
    assert "Alchemy API error" in str(exc_info.value)


@patch("requests.post")
def test_get_token_transfers(mock_post, alchemy_client, mock_chain):
    # Mock responses for both block number and getLogs
    mock_responses = [
        # First call for block number
        MagicMock(
            json=MagicMock(
                return_value={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": "0x1000",  # Block number as hex string
                }
            )
        ),
        # Second call for getLogs
        MagicMock(
            json=MagicMock(
                return_value={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": [],  # Empty list of events
                }
            )
        ),
    ]
    mock_post.side_effect = mock_responses

    # Test with chain
    events = alchemy_client.get_token_transfers(
        contract_address="0x1234567890123456789012345678901234567890", chain=mock_chain
    )
    assert events == []  # Empty list since we're mocking empty events

    # Reset mock for second test
    mock_post.reset_mock()
    mock_post.side_effect = mock_responses

    # Test with custom block range
    events = alchemy_client.get_token_transfers(
        contract_address="0x1234567890123456789012345678901234567890",
        from_block=1000,
        to_block=2000,
    )
    assert events == []


@patch("app.blockchain.alchemy_client.Web3")
def test_get_token_balance(mock_web3_class, alchemy_client, mock_chain):
    # Create mock Web3 instance
    mock_web3_instance = MagicMock()
    mock_web3_class.return_value = mock_web3_instance

    # Keep the real to_checksum_address function
    mock_web3_class.to_checksum_address = Web3.to_checksum_address

    # Mock HTTPProvider
    mock_web3_class.HTTPProvider = MagicMock()

    # Mock eth.contract
    mock_contract = MagicMock()
    mock_contract.functions.balanceOf.return_value.call.return_value = 1000000
    mock_web3_instance.eth.contract.return_value = mock_contract

    # Test with chain
    balance = alchemy_client.get_token_balance(
        contract_address="0x1234567890123456789012345678901234567890",
        wallet_address="0x2345678901234567890123456789012345678901",
        chain=mock_chain,
    )
    assert balance == 1000000

    # Test without chain
    balance = alchemy_client.get_token_balance(
        contract_address="0x1234567890123456789012345678901234567890",
        wallet_address="0x2345678901234567890123456789012345678901",
    )
    assert balance == 1000000
