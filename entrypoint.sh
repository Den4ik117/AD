#!/bin/bash
set -euo pipefail

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"

until nc -z "$DB_HOST" "$DB_PORT"; do
    echo "Waiting for database $DB_HOST:$DB_PORT..."
    sleep 0.1
done

echo "Database is up. Applying migrations..."
alembic upgrade head

echo "Starting application: $*"
exec "$@"
