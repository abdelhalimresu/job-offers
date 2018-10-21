#!/bin/bash
set -e

# Start postgres service
docker-compose up -d postgres;

# Trap Ctrl+C
function ctrl_c() {
    # Stop postgres service
    docker-compose down
  }

trap ctrl_c INT

# Run python dev server
export $(cat .env | xargs)
export POSTGRES_HOST=localhost
python app.py