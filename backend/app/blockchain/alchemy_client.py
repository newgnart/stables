from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import requests
from web3 import Web3
from app.models import Chain


class AlchemyClient:
    """Client for interacting with Alchemy API."""

    def __init__(self, api_key: str):
        """Initialize the Alchemy client.

        Args:
            api_key: Alchemy API key
        """
        self.api_key = api_key
        self.base_url = "https://eth-mainnet.g.alchemy.com/v2"
        self.rate_limit_delay = 0.1  # 100ms between requests
        self._w3 = None

    @property
    def w3(self) -> Web3:
        """Get or create Web3 instance."""
        if self._w3 is None:
            self._w3 = Web3(Web3.HTTPProvider(self.base_url))
        return self._w3

    def _make_request(self, method: str, params: List) -> Dict:
        """Make a request to the Alchemy API with rate limiting.

        Args:
            method: RPC method name
            params: List of parameters for the RPC call

        Returns:
            Dict containing the API response

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/{self.api_key}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}

        time.sleep(self.rate_limit_delay)  # Rate limiting
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        if "error" in result:
            raise Exception(f"Alchemy API error: {result['error']}")

        return result["result"]

    def get_token_transfers(
        self,
        contract_address: str,
        from_block: Optional[int] = None,
        to_block: Optional[int] = None,
        chain: Optional[Chain] = None,
    ) -> List[Dict]:
        """Get token transfer events for a contract.

        Args:
            contract_address: The token contract address (must be a valid Ethereum address)
            from_block: Starting block number (optional)
            to_block: Ending block number (optional)
            chain: Chain model instance (optional)

        Returns:
            List of transfer events with details
        """
        if chain:
            # Use chain-specific RPC URL if provided
            self.base_url = chain.rpc_url
            self._w3 = None  # Reset Web3 instance to use new URL

        # Validate and normalize contract address
        contract_address = Web3.to_checksum_address(contract_address.lower())

        # If no block range specified, get last 1000 blocks
        if not from_block or not to_block:
            latest_block = int(self._make_request("eth_blockNumber", []), 16)
            if not from_block:
                from_block = latest_block - 1000
            if not to_block:
                to_block = latest_block

        # Get transfer events
        events = self._make_request(
            "eth_getLogs",
            [
                {
                    "address": contract_address,
                    "fromBlock": hex(from_block),
                    "toBlock": hex(to_block),
                    "topics": [
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"  # Transfer event signature
                    ],
                }
            ],
        )

        return events if isinstance(events, list) else []

    def get_token_balance(
        self, contract_address: str, wallet_address: str, chain: Optional[Chain] = None
    ) -> int:
        """Get token balance for a wallet.

        Args:
            contract_address: The token contract address (must be a valid Ethereum address)
            wallet_address: The wallet address to check (must be a valid Ethereum address)
            chain: Chain model instance (optional)

        Returns:
            Token balance in smallest unit (wei)
        """
        if chain:
            self.base_url = chain.rpc_url
            self._w3 = None  # Reset Web3 instance to use new URL

        # Validate and normalize addresses
        contract_address = Web3.to_checksum_address(contract_address.lower())
        wallet_address = Web3.to_checksum_address(wallet_address.lower())

        # Create contract instance
        contract = self.w3.eth.contract(
            address=contract_address,
            abi=[
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function",
                }
            ],
        )

        return contract.functions.balanceOf(wallet_address).call()
