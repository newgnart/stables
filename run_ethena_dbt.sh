#!/bin/bash

cd "$(dirname "$0")/dbt_subprojects/ethena"

case "${1:-staged}" in
    "staged")
        echo "Running dbt with staged target..."
        uv run dbt run --target staged
        ;;
    "marts")
        echo "Running dbt with marts target..."
        uv run dbt run --target marts
        ;;
    "all")
        echo "Running dbt for both staged and marts..."
        uv run dbt run --target staged
        uv run dbt run --target marts
        ;;
    *)
        echo "Usage: $0 [staged|marts|all]"
        echo "  staged: Run staging models (default)"
        echo "  marts: Run marts models"
        echo "  all: Run both staging and marts"
        exit 1
        ;;
esac