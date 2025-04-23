# Stablecoin Supply API

A FastAPI-based service for collecting and serving stablecoin circulating supply data from DeFiLlama.

## Features

- Collects stablecoin supply data from DeFiLlama
- Stores data in PostgreSQL database with UTC timestamps
- Provides REST API endpoints for accessing the data
- Supports filtering by stablecoin symbol and chain
- Tracks supply changes over 24h, 7d, and 30d periods

## Setup

### 1. Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- `psql` command-line tool

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb stables
```

### 3. Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the backend directory:
```bash
# Default configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/stables
```

### 5. Database Migration

```bash
# Initialize database schema
alembic upgrade head
```

### 6. Start the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Database Schema

### Stablecoin Table
- `id`: Primary key (from DeFiLlama)
- `name`: Stablecoin name
- `symbol`: Token symbol (indexed)
- `gecko_id`: CoinGecko ID (indexed)
- `peg_type`: Type of peg (e.g., USD, EUR)
- `peg_mechanism`: Peg mechanism type
- `total_circulating`: Total supply across all chains
- `time_utc`: Timestamp with minute precision

### Chain Circulating Table
- Composite primary key: (`stable_id`, `chain`, `time_utc`)
- `stable_id`: Foreign key to stablecoin table
- `chain`: Blockchain name
- `circulating`: Circulating supply on this chain
- `time_utc`: Timestamp with minute precision

## API Endpoints

- `GET /`: Root endpoint with API information
- `GET /supply`: Get circulating supply data
  - Query parameters:
    - `symbol`: Filter by stablecoin symbol
    - `chain`: Filter by chain
    - `limit`: Maximum number of records (default: 100)
- `POST /collect`: Trigger data collection from DeFiLlama

## Development

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

### Code Style

The project follows PEP 8 guidelines. Before committing:
```bash
# Install development dependencies
pip install black isort

# Format code
black .
isort .
``` 