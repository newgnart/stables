#!/bin/bash

# Script to sync PostgreSQL environment variables from .env to .dlt/secrets.toml
# Usage: ./scripts/sync_env_to_dlt.sh

set -e  # Exit on any error

ENV_FILE=".env"
SECRETS_FILE=".dlt/secrets.toml"
BACKUP_FILE=".dlt/secrets.toml.backup"

echo "🔄 Syncing environment variables from $ENV_FILE to $SECRETS_FILE"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE file not found!"
    exit 1
fi

# Create .dlt directory if it doesn't exist
mkdir -p .dlt

# Create backup of existing secrets.toml if it exists
if [ -f "$SECRETS_FILE" ]; then
    cp "$SECRETS_FILE" "$BACKUP_FILE"
    echo "📋 Backup created: $BACKUP_FILE"
fi

# Source the .env file to load variables
set -a  # Automatically export all variables
source "$ENV_FILE"
set +a  # Stop auto-exporting

# Check if required PostgreSQL variables are set
if [ -z "$POSTGRES_HOST" ] || [ -z "$POSTGRES_PORT" ] || [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ Error: Missing required PostgreSQL environment variables in $ENV_FILE"
    echo "Required variables: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD"
    exit 1
fi

# Generate the secrets.toml file
cat > "$SECRETS_FILE" << EOF
[destination.postgres.credentials]
host = "$POSTGRES_HOST"
port = $POSTGRES_PORT
database = "$POSTGRES_DB"
username = "$POSTGRES_USER"
password = "$POSTGRES_PASSWORD"
EOF

echo "✅ Successfully updated $SECRETS_FILE with PostgreSQL credentials"

# Display the generated configuration (without password)
echo "📋 Generated configuration:"
echo "   Host: $POSTGRES_HOST"
echo "   Port: $POSTGRES_PORT"
echo "   Database: $POSTGRES_DB"
echo "   Username: $POSTGRES_USER"
echo "   Password: [HIDDEN]"

# Set appropriate permissions
chmod 600 "$SECRETS_FILE"
echo "🔒 Set secure permissions (600) on $SECRETS_FILE"

echo "🎉 Environment sync complete!"