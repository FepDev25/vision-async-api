#!/bin/bash

set -e

echo "Waiting for database to be ready..."
uv run python -c "
import time
import psycopg2
from app.core.config import settings

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )
        conn.close()
        print('Database is ready!')
        break
    except psycopg2.OperationalError:
        retry_count += 1
        print(f'Database not ready yet. Retry {retry_count}/{max_retries}...')
        time.sleep(2)
else:
    print('Could not connect to database after maximum retries.')
    exit(1)
"

echo "Running database migrations..."
uv run alembic -c app/alembic.ini upgrade head

echo "Starting API server..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
