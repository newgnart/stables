# PostgreSQL Setup Guide

This guide explains how to set up PostgreSQL for the stables data pipeline.

## Prerequisites

- Docker and Docker Compose (recommended) OR
- PostgreSQL installed locally

## Option 1: Docker Setup (Recommended)

### 1. Create Docker Compose File

Create a `docker-compose.yml` file in the project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: stables_postgres
    environment:
      POSTGRES_DB: stables
      POSTGRES_USER: stables_user
      POSTGRES_PASSWORD: your_password_here
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### 2. Start PostgreSQL

```bash
docker-compose up -d
```

### 3. Verify Connection

```bash
docker exec -it stables_postgres psql -U stables_user -d stables -c "SELECT version();"
```

## Option 2: Local Installation

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS
```bash
brew install postgresql
brew services start postgresql
```

### Create Database and User

```bash
sudo -u postgres psql

CREATE DATABASE stables;
CREATE USER stables_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE stables TO stables_user;
\q
```

## Configuration

### 1. Update Environment Variables

Update your `.env` file with PostgreSQL connection details:

```env
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=stables
POSTGRES_USER=stables_user
POSTGRES_PASSWORD=your_password_here
```

### 2. Install Python Dependencies

```bash
uv sync
```

This will install the updated dependencies including:
- `dbt-postgres`
- `dlt[postgres]`
- `psycopg2-binary`

## Database Schema Structure

The PostgreSQL database will use the following schema organization:

- `raw_curve` - Raw Curve Finance data
- `raw_ethena` - Raw Ethena data
- `crvusd_market` - Staged Curve data
- `usde` - Staged Ethena data
- `usde_marts` - Ethena marts/analytics tables

## Testing the Setup

### 1. Test DLT Pipeline

```bash
python scripts/curve_dlt_pipeline.py
```

### 2. Test DBT Transformations

```bash
cd dbt_subprojects/curve
uv run dbt run
```

### 3. Check Database Contents

```bash
docker exec -it stables_postgres psql -U stables_user -d stables

-- List all schemas
\dn

-- List tables in a schema
\dt crvusd_market.*

-- Check table contents
SELECT COUNT(*) FROM crvusd_market.logs;
```

## Common Issues

### Connection Issues
- Ensure PostgreSQL is running: `docker-compose ps` or `sudo systemctl status postgresql`
- Check firewall settings if connecting remotely
- Verify connection details in `.env` file

### Permission Issues
- Ensure the database user has proper permissions
- Check if the database and schemas exist

### Memory Issues
- Increase PostgreSQL memory settings in `postgresql.conf` for large datasets
- Consider using connection pooling for high-volume operations

## Monitoring

### Check Database Size
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Monitor Active Connections
```sql
SELECT count(*) FROM pg_stat_activity;
```

## Backup and Restore

### Backup
```bash
docker exec stables_postgres pg_dump -U stables_user stables > backup.sql
```

### Restore
```bash
docker exec -i stables_postgres psql -U stables_user stables < backup.sql
```