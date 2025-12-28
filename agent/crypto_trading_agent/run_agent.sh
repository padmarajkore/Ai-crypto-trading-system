#!/bin/bash

# Check if .env exists and source it
if [ -f .env ]; then
    echo "Sourcing .env..."
    set -a
    source .env
    set +a
fi

# Prompt for GOOGLE_API_KEY if not set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "GOOGLE_API_KEY is not set."
    read -p "Enter your Google API Key: " input_key
    export GOOGLE_API_KEY="$input_key"
fi

# Set Freqtrade variables if not set
export FREQTRADE_API_URL="${FREQTRADE_API_URL:-http://127.0.0.1:8081}"
export FREQTRADE_USERNAME="${FREQTRADE_USERNAME:-Freqtrader}"
export FREQTRADE_PASSWORD="${FREQTRADE_PASSWORD:-SuperSecret1!}"

echo "Environment configured."
echo "GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:5}..."
echo "FREQTRADE_API_URL: $FREQTRADE_API_URL"

# Run the agent
echo "Starting Agent..."
/Users/padamarajkore/Documents/ADK-crash-course/.venv/bin/adk run .
