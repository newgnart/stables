# Ethena DBT Transformations

## Overview

This DBT project transforms raw Ethena (USDe) blockchain data into analytics-ready tables for stablecoin research. The pipeline processes Ethereum event logs from the USDe contract to extract and analyze token transfer activity.

## Data Flow

```
Raw Data (PostgreSQL: ethena_usde schema)
    ↓
Staging Models (PostgreSQL: usde schema)
    ↓
Marts Models (PostgreSQL: usde_marts schema)
```

## Data Sources

- **ethena_usde.logs_raw**: Raw event logs from USDe contracts across all chains, loaded via DLT pipeline
  - Contains JSON topics array, contract addresses, transaction data, and block information
  - Source: Etherscan API event logs

## Models

### Staging Layer (`models/staging/`)

- **logs.sql**: Extracts and parses individual topics from raw JSON event logs
  - Converts hex values to proper data types (block numbers, timestamps, gas values)
  - Extracts up to 4 topics from the JSON topics array
  - Materializes as table in `usde` schema

### Marts Layer (`models/marts/`)

- **erc20_transfers.sql**: Processes ERC-20 transfer events into human-readable format
  - Filters for Transfer events (topic0 = `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`)
  - Extracts from/to addresses from topics
  - Converts transfer amounts from hex to decimal (wei to ether)
  - Materializes as table in `usde_marts` schema

## Key Transformations

1. **JSON Topic Parsing**: Extracts event signature and indexed parameters from Ethereum log topics
2. **Hex to Decimal Conversion**: Converts blockchain hex values to proper numeric types
3. **ERC-20 Transfer Detection**: Identifies and parses token transfer events
4. **Address Extraction**: Extracts sender and recipient addresses from indexed log topics
5. **Amount Normalization**: Converts wei amounts to ether (divided by 1e18)

## Usage

Run transformations from the ethena directory:

```bash
cd dbt_subprojects/ethena
uv run dbt run
```

This will process raw logs and create staged tables for analysis of USDe token transfers and contract activity.