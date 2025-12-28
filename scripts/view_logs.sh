#!/bin/bash

# AI Crypto Trading System - Log Viewer
# Tails all relevant logs in one window

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📊 Starting Log Viewer..."
echo "   - Freqtrade Log"
echo "   - Agent Conversation History"
echo "   - Telegram Listener Log"
echo "---------------------------------------------------"

# Ensure log files exist to avoid tail errors
touch "$PROJECT_DIR/freqtrade/freqtrade.log"
touch "$PROJECT_DIR/agent/crypto_trading_agent/conversation_history.log"
touch "$PROJECT_DIR/scripts/telegram_listener.log"

# Tail them all
tail -f \
    "$PROJECT_DIR/freqtrade/freqtrade.log" \
    "$PROJECT_DIR/agent/crypto_trading_agent/conversation_history.log" \
    "$PROJECT_DIR/scripts/telegram_listener.log"
