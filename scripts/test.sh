#!/bin/bash
set -e

# Start postgres test instance
docker-compose -f docker-compose.test.yml up -d

# Wait for postgres to start
sleep 3

# Export Env variables & run tests
export $(cat .env | xargs)
export POSTGRES_HOST=localhost
export POSTGRES_DB=test_db
python tests.py

# Stop postgres
docker-compose down