import dlt
from dlt.sources.rest_api import rest_api_source
from dlt.sources.helpers.rest_client import paginators
from dlt.common.typing import TDataItems
from typing import Iterable, Literal
import json
import logging

import time

logger = logging.getLogger(__name__)

DEFILLAMA_STABLECOINS_API_URL = "https://stablecoins.llama.fi"
DEFILLAMA_YIELDS_API_URL = "https://yields.llama.fi"
YIELD_POOLS_COLUMNS = {
    "reward_tokens": {"data_type": "text", "nullable": True},
    "underlying_tokens": {"data_type": "text", "nullable": True},
}
YIELD_POOL_COLUMNS = {
    # "apy_reward": {"data_type": "json"},
    # "il7d": {"data_type": "json"},
    # "apy_base7d": {"data_type": "json"},
    "apy_base": {"data_type": "json"},
}


STABLECOIN_CHAIN_TOKENS_COLUMNS = {
    "circulating": {"data_type": "float"},
    "bridged_to": {"data_type": "float"},
}

STABLE_CIRCULATING_COLUMNS = {
    "id": {"data_type": "bigint"},
    "name": {"data_type": "text"},
    "symbol": {"data_type": "text"},
    "date": {"data_type": "bigint"},
    "chain": {"data_type": "text"},
    "circulating": {"data_type": "bigint"},
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


@dlt.resource(columns=YIELD_POOLS_COLUMNS)  # type: ignore[arg-type]
def yield_pools() -> Iterable[TDataItems]:
    """Get the latest data for all yield pools."""
    resource = _create_defillama_source(
        DEFILLAMA_YIELDS_API_URL, "pools", data_selector="data"
    )

    # Process each pool to ensure reward_tokens and underlying_tokens are always present
    for pool in resource:
        # Extract the original fields
        reward_tokens = pool.get("rewardTokens", []) or []
        underlying_tokens = pool.get("underlyingTokens", []) or []

        # Remove the original camelCase fields to prevent DLT from creating separate tables
        if "rewardTokens" in pool:
            del pool["rewardTokens"]
        if "underlyingTokens" in pool:
            del pool["underlyingTokens"]

        pool["reward_tokens"] = json.dumps(reward_tokens)
        pool["underlying_tokens"] = json.dumps(underlying_tokens)

        yield pool


@dlt.resource(columns=YIELD_POOL_COLUMNS)  # type: ignore[arg-type]
def yield_pool(pool_id: str) -> dlt.sources.DltResource:
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


@dlt.resource(columns=STABLE_CIRCULATING_COLUMNS)  # type: ignore[arg-type]
def stable_circulating(coin_id: int) -> Iterable[TDataItems]:
    """Get chain circulating data for a specific stablecoin by ID."""
    resource = _create_defillama_source(
        DEFILLAMA_STABLECOINS_API_URL,
        f"stablecoin/{coin_id}",
        data_selector="$",  # Get full response to access both metadata and chainBalances
    )

    for response in resource:
        base_info = {
            "id": coin_id,
            "name": response.get("name"),
            "symbol": response.get("symbol"),
        }

        for chain_name, chain_data in response.get("chainBalances", {}).items():
            for entry in chain_data.get("tokens", []):
                circulating_data = entry.get("circulating", {})
                if circulating_data:
                    circulating_value = list(circulating_data.values())[0]
                    yield {
                        **base_info,
                        "date": entry.get("date"),
                        "circulating": (
                            int(circulating_value)
                            if circulating_value is not None
                            else None
                        ),
                        "chain": chain_name,
                    }


@dlt.resource()
def protocol_revenue(
    protocol: str,
    data_type: Literal["historical", "current", "breakdown"] = "historical",
) -> Iterable[TDataItems]:
    """
    Get protocol revenue data with unified structure.

    Args:
        protocol: Protocol name (e.g., "ethena")
        data_type: "historical", "current", "both", or "breakdown"
    """
    if data_type == "historical":
        # Get historical data from totalDataChart
        historical_resource = _create_defillama_source(
            "https://api.llama.fi",
            f"summary/fees/{protocol}",
            data_selector="totalDataChart",
        )

        # Yield historical data
        for item in historical_resource:
            if isinstance(item, list) and len(item) == 2:
                yield {
                    "timestamp": item[0],
                    "revenue": item[1],
                    "protocol": protocol,
                }

    if data_type == "current":
        # Get current data
        current_resource = _create_defillama_source(
            "https://api.llama.fi", f"summary/fees/{protocol}", data_selector="$"
        )

        current_timestamp = int(time.time())

        for item in current_resource:
            current_revenue = item.get("total24h", 0)
            yield {
                "timestamp": current_timestamp,
                "revenue": current_revenue,
                "protocol": protocol,
            }

    if data_type == "breakdown":
        # Get breakdown data from totalDataChartBreakdown
        breakdown_resource = _create_defillama_source(
            "https://api.llama.fi",
            f"summary/fees/{protocol}",
            data_selector="totalDataChartBreakdown",
        )

        for item in breakdown_resource:
            if isinstance(item, list) and len(item) == 2:
                timestamp = item[0]
                breakdown_data = item[1]  # {"Ethereum": {"Ethena USDe": value}}

                # Extract revenue data from nested structure
                if isinstance(breakdown_data, dict):
                    # Flatten the nested chain -> protocol -> revenue structure
                    for chain, chain_data in breakdown_data.items():
                        if isinstance(chain_data, dict):
                            for sub_protocol, revenue_value in chain_data.items():
                                yield {
                                    "timestamp": timestamp,
                                    "revenue": revenue_value,
                                    "protocol": protocol,
                                    "chain": chain,
                                    "sub_protocol": sub_protocol,
                                }
