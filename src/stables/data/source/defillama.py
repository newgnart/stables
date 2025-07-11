import dlt
from dlt.sources.rest_api import rest_api_source
from dlt.sources.helpers.rest_client import paginators
from dlt.common.typing import TDataItems
from typing import Iterable

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

STABLECOIN_CHAIN_BALANCES_COLUMNS = {
    "circulating": {"data_type": "json"},
    "bridgedTo": {"data_type": "json"},
    "bridges": {"data_type": "json"},
}

STABLECOIN_CHAIN_TOKENS_COLUMNS = {
    "circulating": {"data_type": "float"},
    "bridged_to": {"data_type": "float"},
}


def _get_circulating_value(data: dict | None, peg_type: str) -> float | None:
    """Safely extracts circulating value from a dictionary for a given peg type."""
    if isinstance(data, dict):
        return data.get(peg_type)
    return None


def _create_defillama_source(
    base_url: str, endpoint: str, data_selector: str
) -> dlt.sources.DltResource:
    """
    Creates a dlt rest_api_source for a given set of API parameters.
    """
    source = rest_api_source(
        {
            "client": {
                "base_url": base_url,
                "paginator": paginators.SinglePagePaginator(),
            },
            "resources": [
                {
                    "name": endpoint,
                    "endpoint": {
                        "path": f"/{endpoint}",
                        "data_selector": data_selector,
                    },
                }
            ],
        }
    )
    return source.resources[endpoint]


@dlt.resource(columns=YIELDS_POOLS_COLUMNS)  # type: ignore[arg-type]
def defillama_yield_pools() -> dlt.sources.DltResource:
    """Get the latest data for all yield pools."""
    resource = _create_defillama_source(
        DEFILLAMA_YIELDS_API_URL, "pools", data_selector="data"
    )
    return resource


@dlt.resource(columns=YIELDS_POOL_COLUMNS)  # type: ignore[arg-type]
def defillama_yield_pool(pool_id: str) -> dlt.sources.DltResource:
    """Get historical data for a yield pool."""
    resource = _create_defillama_source(
        DEFILLAMA_YIELDS_API_URL, f"chart/{pool_id}", data_selector="data"
    )
    return resource


@dlt.resource()
def defillama_stables_base() -> Iterable[TDataItems]:
    """
    Fetches stablecoin data from DefiLlama and yields data for the 'stables' table.
    """
    raw_data_resource = _create_defillama_source(
        DEFILLAMA_STABLECOINS_API_URL, "stablecoins", data_selector="peggedAssets"
    )

    for item in raw_data_resource:

        peg_type = item.get("pegType")
        if not peg_type:
            continue

        circulating_keys = [
            "circulating",
            "circulatingPrevDay",
            "circulatingPrevWeek",
            "circulatingPrevMonth",
        ]

        circulating_data = {
            c: _get_circulating_value(item.get(c), peg_type) for c in circulating_keys
        }

        stable = {
            "id": int(item["id"]),
            "name": item["name"],
            "symbol": item["symbol"],
            "gecko_id": item["gecko_id"] or None,
            "peg_type": peg_type,
            "peg_mechanism": item.get("pegMechanism"),
            **circulating_data,
        }
        yield stable


@dlt.resource()
def defillama_stables_chain_circulating() -> Iterable[TDataItems]:
    """
    Fetches stablecoin data from DefiLlama and yields data for the 'chain_circulating' table.
    """
    raw_data_resource = _create_defillama_source(
        DEFILLAMA_STABLECOINS_API_URL, "stablecoins", data_selector="peggedAssets"
    )

    for item in raw_data_resource:
        if not item.get("gecko_id"):
            continue

        peg_type = item.get("pegType")
        if not peg_type:
            continue

        chain_circulating = item.get("chainCirculating", {})
        if not chain_circulating:
            continue

        for chain, chain_data in chain_circulating.items():
            if not chain_data:
                continue

            circulating_keys_map = {
                "current": "circulating",
                "circulatingPrevDay": "circulating_prev_day",
                "circulatingPrevWeek": "circulating_prev_week",
                "circulatingPrevMonth": "circulating_prev_month",
            }

            circulating_data = {
                target_key: _get_circulating_value(chain_data.get(source_key), peg_type)
                for source_key, target_key in circulating_keys_map.items()
            }

            chain_data_obj = {
                "id": int(item["id"]),
                "chain": chain,
                **circulating_data,
            }
            yield chain_data_obj


@dlt.resource(columns=STABLECOIN_CHAIN_BALANCES_COLUMNS)  # type: ignore[arg-type]
def defillama_stablecoin_chain_balances(stablecoin_id: str) -> dlt.sources.DltResource:
    """Get chain balances data for a specific stablecoin by ID."""
    resource = _create_defillama_source(
        DEFILLAMA_STABLECOINS_API_URL,
        f"stablecoin/{stablecoin_id}",
        data_selector="chainBalances",
    )
    return resource.with_name("stablecoin_chain_balances")


@dlt.resource()
def defillama_stablecoin_chain_tokens(stablecoin_id: str) -> Iterable[TDataItems]:
    """
    Fetches stablecoin chain token data from DefiLlama and yields normalized data.
    """
    raw_data_resource = _create_defillama_source(
        DEFILLAMA_STABLECOINS_API_URL,
        f"stablecoin/{stablecoin_id}",
        data_selector="chainBalances",
    )
    # peg_type = _create_defillama_source(
    #     DEFILLAMA_STABLECOINS_API_URL,
    #     f"stablecoin/{stablecoin_id}",
    #     data_selector="pegType",
    # )
    peg_type = "peggedUSD"

    chain_balances = next(iter(raw_data_resource), None)
    if not chain_balances:
        return

    for chain_name, chain_data in chain_balances.items():
        if not chain_data or not isinstance(chain_data, dict):
            continue

        tokens = chain_data.get("tokens", [])
        if not tokens:
            continue

        for token_data in tokens:
            if not isinstance(token_data, dict):
                continue

            date = token_data.get("date")
            if not date:
                continue

            circulating_data = token_data.get("circulating", {})
            bridged_to_data = token_data.get("bridgedTo", {})

            # Extract peggedUSD values
            circulating_value = _get_circulating_value(circulating_data, peg_type)
            bridged_value = _get_circulating_value(bridged_to_data, peg_type)

            # Extract bridge information
            # bridges = bridged_to_data.get("bridges", {})

            chain_token = {
                "stablecoin_id": int(stablecoin_id),
                "chain": chain_name,
                "date": date,
                "circulating": circulating_value,
                "bridged_to": bridged_value,
                # "bridges": bridges,
            }
            yield chain_token
