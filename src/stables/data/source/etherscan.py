import os
import requests
from datetime import datetime
import dlt
from dlt.sources.helpers.rest_client import paginators
from dlt.sources.rest_api import rest_api_source
from stables.config import (
    ETHERSCAN_API_BASE_URL,
    ETHERSCAN_API_KEY,
    ETHERSCAN_LOG_COLUMNS,
    ETHERSCAN_TRANSACTION_COLUMNS,
)
import json
import time
import logging

# Set up logging
logger = logging.getLogger(__name__)


class RateLimitedSession(requests.Session):
    """Simple rate-limited session for Etherscan API"""

    def __init__(self, calls_per_second=5):
        super().__init__()
        self.calls_per_second = calls_per_second
        self.last_request_time = 0
        self.min_interval = 1.0 / calls_per_second
        self.request_count = 0

    def request(self, method, url, **kwargs):
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()
        self.request_count += 1

        # Log API call
        logger.info(f"API Call #{self.request_count}: {method} {url}")

        response = super().request(method, url, **kwargs)

        # Log response status
        logger.info(
            f"Response #{self.request_count}: {response.status_code} - {response.reason}"
        )

        return response


def _create_etherscan_source(params: dict):
    """
    Creates a dlt rest_api_source for a given set of Etherscan API parameters.
    It includes a rate-limited session for the client.
    """
    session = RateLimitedSession(calls_per_second=5)
    return rest_api_source(
        {
            "client": {
                "base_url": ETHERSCAN_API_BASE_URL,
                "paginator": paginators.PageNumberPaginator(
                    base_page=1, total_path=None, page_param="page"
                ),
                "session": session,
            },
            "resources": [
                {
                    "name": "",  # Etherscan result is not nested
                    "endpoint": {"params": params},
                },
            ],
        }
    )


@dlt.resource(columns=ETHERSCAN_TRANSACTION_COLUMNS)
def etherscan_transactions(
    chainid,
    address,
    module="account",
    action="txlist",
    startblock=0,
    endblock="latest",
    offset=1000,
    sort="asc",
):
    """dlt resource to get transactions for a given address."""
    params = {
        "chainid": chainid,
        "module": module,
        "action": action,
        "address": address,
        "startblock": startblock,
        "endblock": endblock,
        "offset": offset,
        "sort": sort,
        "apikey": ETHERSCAN_API_KEY,
    }
    logger.info(f"Fetching transactions for address {address} from block {startblock}")
    return _create_etherscan_source(params)


@dlt.resource(columns=ETHERSCAN_LOG_COLUMNS)
def etherscan_logs(
    chainid,
    address,
    module="logs",
    action="getLogs",
    fromBlock=0,
    toBlock="latest",
    offset=1000,
):
    """dlt resource to get event logs for a given address."""
    params = {
        "chainid": chainid,
        "module": module,
        "action": action,
        "address": address,
        "fromBlock": fromBlock,
        "toBlock": toBlock,
        "offset": offset,
        "apikey": ETHERSCAN_API_KEY,
    }
    logger.info(
        f"Fetching logs for address {address} from block {fromBlock} to {toBlock}"
    )
    return _create_etherscan_source(params)


# --- Refactored V2 API Calls ---

_v2_session = RateLimitedSession(calls_per_second=5)


def _etherscan_v2_call(params: dict):
    """
    Helper to make a call to the Etherscan 'v2' API.
    It uses a shared, rate-limited session and handles common error checking.
    """
    base_url = "https://api.etherscan.io/v2/api"
    params["apikey"] = ETHERSCAN_API_KEY

    response = _v2_session.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    # Check for API errors
    if data.get("status") == "0":
        message = data.get("message", "Etherscan API error")
        logger.error(f"API error: {message}")
        if "rate limit" in message.lower():
            raise Exception(f"Etherscan rate limit exceeded: {message}")
        raise Exception(f"Etherscan API error: {message}")

    return data["result"]


def get_latest_block(chainid, timestamp: int = None, closest="before"):
    """Gets the latest block number, or the block number closest to a timestamp."""
    if timestamp is None:
        timestamp = int(datetime.now().timestamp())

    logger.info(f"Getting latest block for chain {chainid}")

    params = {
        "chainid": chainid,
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": closest,
    }
    result = _etherscan_v2_call(params)

    latest_block = int(result)
    logger.info(f"Latest block: {latest_block}")
    return latest_block


def get_contract_abi(chainid, address, save=True, save_dir: str = "data/abi"):
    """Gets the ABI for a given contract address."""
    logger.info(f"Getting ABI for contract {address} on chain {chainid}")

    params = {
        "chainid": chainid,
        "module": "contract",
        "action": "getabi",
        "address": address,
    }
    result = _etherscan_v2_call(params)

    # Parse the ABI string to get proper JSON
    abi_json = json.loads(result)

    if save:
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, f"{address}.json"), "w") as f:
            json.dump(abi_json, f, indent=2)
        logger.info(f"ABI saved to {os.path.join(save_dir, f'{address}.json')}")

    return abi_json


def get_contract_creation_txn(chainid, contract_addresses):
    """
    Gets contract creation block numbers for one or more contract addresses.

    Args:
        chainid: The chain ID.
        contract_addresses: A single contract address string or a list of contract address strings.

    Returns:
        A tuple containing:
        - A dictionary mapping contract addresses (lowercase) to their creation block numbers.
        - The raw API response.
    """
    # Handle single address case
    if isinstance(contract_addresses, str):
        contract_addresses = [contract_addresses]

    logger.info(
        f"Getting creation block numbers for {len(contract_addresses)} contracts on chain {chainid}"
    )

    params = {
        "chainid": chainid,
        "module": "contract",
        "action": "getcontractcreation",
        "contractaddresses": ",".join(contract_addresses),
    }
    result = _etherscan_v2_call(params)
    if len(result) == 1:
        return result[0]
    return result
