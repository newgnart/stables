# Stablecoin Research Data Pipeline

This project provides a data engineering pipeline to extract, load, and transform data. It uses `dlt` for data ingestion and `dbt` for data transformation.

## Architecture

The pipeline follows an ELT (Extract, Load, Transform) architecture:

1.  **Extract & Load**: A Python script using the `dlt` library fetches log data from Etherscan, and some other sources. This raw data is then loaded into a local DuckDB database.
2.  **Transform**: `dbt` is used to transform raw data into a analytics-ready tables.
3.  Example usage:
    - `scripts/curve_dlt_pipeline.py` for Curve Finance's crvUSD market data, raw data is loaded into `data/raw/raw_curve.duckdb`.
    - `dbt_subprojects/curve/models/staging/logs.sql` for parsing the raw logs into decoded logs (with decoded topics).

## Tech Stack

*   **Python**: The core language for the data ingestion scripts.
*   **dlt (Data Load Tool)**: For creating robust and scalable data ingestion pipelines.
*   **dbt (Data Build Tool)**: For transforming data in the warehouse using SQL.
*   **DuckDB**: As the local data warehouse.
*   **Etherscan API**: As the source for blockchain data.
*   **uv**: For Python package management.

## Project Structure

```
.
├── data/                 # Raw and processed data
├── dbt_subprojects/      # dbt project for data transformation (example: dbt_subprojects/curve)
├── notebooks/            # Jupyter notebooks for analysis
├── scripts/              # Python scripts for data ingestion (dlt pipelines)
├── src/                  # Python source code
├── pyproject.toml        # Project dependencies
└── README.md
```

## Setup and Usage


```bash
git clone git@github.com:newgnart/stables.git
cd stables

uv sync
cp .env.example .env  # then add Etherscan API key to the `.env` file
```

### 4. Run the example dlt pipeline

To start the data ingestion process, run the `dlt` pipeline script:

```bash
python scripts/curve_dlt_pipeline.py
```
This will fetch the event logs and load them into `data/raw/raw_curve.duckdb`.

### 5. Run dbt transformations

Once the raw data is loaded, you can run the `dbt` models to transform.

Navigate to the dbt project directory and run the models:
```bash
cd dbt_subprojects/curve
uv run dbt run
```
This will run the dbt models and save the transformed data in the `staged` schema `data/staged/staged_curve.duckdb`.



