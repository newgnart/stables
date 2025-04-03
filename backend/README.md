# Stablecoin Supply API

A FastAPI-based service for collecting and serving stablecoin circulating supply data from DeFiLlama.

## Features

- Collects stablecoin supply data from DeFiLlama
- Stores data in PostgreSQL database
- Provides REST API endpoints for accessing the data
- Supports filtering by stablecoin symbol and chain
- Tracks supply changes over 24h, 7d, and 30d periods

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
# Create a PostgreSQL database named 'stables'
# Update DATABASE_URL in .env file or use default:
# postgresql://postgres:postgres@localhost:5432/stables

# Run database migrations
alembic upgrade head
```

4. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /`: Root endpoint with API information
- `GET /supply`: Get circulating supply data
  - Query parameters:
    - `symbol`: Filter by stablecoin symbol
    - `chain`: Filter by chain
    - `limit`: Maximum number of records to return (default: 100)
- `POST /collect`: Trigger data collection from DeFiLlama

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: postgresql://postgres:postgres@localhost:5432/stables)

## Development

To run database migrations:
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
``` 