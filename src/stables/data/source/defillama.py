import dlt
from dlt.sources.rest_api import rest_api_source
from dlt.sources.helpers.rest_client import paginators

import logging

logger = logging.getLogger(__name__)

DEFILLAMA_STABLECOINS_API_URL = "https://stablecoins.llama.fi"
DEFILLAMA_YIELDS_API_URL = "https://yields.llama.fi"
YIELDS_POOLS_COLUMNS = {
    "reward_tokens": {"data_type": "json"},
    "underlying_tokens": {"data_type": "json"},
}
YIELDS_POOL_COLUMNS = {
    "apy_reward": {"data_type": "json"},
    "il7d": {"data_type": "json"},
    "apy_base7d": {"data_type": "json"},
    "apy_base": {"data_type": "json"},
}


def _create_defillama_source(endpoint: str):
    """
    Creates a dlt rest_api_source for a given set of Etherscan API parameters.
    It includes a rate-limited session for the client.
    """
    return rest_api_source(
        {
            "client": {
                "base_url": f"{DEFILLAMA_YIELDS_API_URL}/{endpoint}",
                "paginator": paginators.SinglePagePaginator(),
            },
            "resources": [
                {
                    "name": "",  # Etherscan result is not nested
                },
            ],
        }
    )


@dlt.resource(columns=YIELDS_POOLS_COLUMNS)
def defillama_yield_pools():
    """Get the latest data for all yield pools."""
    return _create_defillama_source("pools")


@dlt.resource(columns=YIELDS_POOL_COLUMNS)
def defillama_yield_pool(pool_id: str):
    """Get historical data for a yield pool."""
    return _create_defillama_source(f"chart/{pool_id}")
