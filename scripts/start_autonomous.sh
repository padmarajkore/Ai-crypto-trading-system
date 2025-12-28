#!/bin/bash

# AI Crypto Trading System - Autonomous Mode Startup
# Starts Freqtrade, Agent API Server, Telegram Listener, and Daily Scheduler

echo "🚀 Starting AI Crypto Trading System (Autonomous Mode)..."
echo "========================================================"

# Get project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source .env file for API keys
if [ -f "$PROJECT_DIR/agent/crypto_trading_agent/.env" ]; then
    echo "🔑 Sourcing .env file..."
    set -a # Automatically export all variables
    source "$PROJECT_DIR/agent/crypto_trading_agent/.env"
    set +a
else
    echo "⚠️  Warning: .env file not found in agent/crypto_trading_agent/"
fi

# 1. Start Freqtrade (The Body)
echo "1️⃣  Starting Freqtrade Bot..."
if lsof -i:8081 > /dev/null 2>&1; then
    echo "   ⚠️  Freqtrade already running on port 8081"
else
    cd "$PROJECT_DIR/freqtrade"
    # Run in background, log to file
    nohup freqtrade trade --dry-run -c adk_config.json --strategy SampleStrategy > freqtrade.log 2>&1 &
    echo "   ✅ Freqtrade started (PID: $!)"
fi
sleep 2

# 2. Start Agent API Server (The Brain)
echo "2️⃣  Starting AI Agent API Server..."
if lsof -i:8000 > /dev/null 2>&1; then
    echo "   ⚠️  Agent Server already running on port 8000"
else
    cd "$PROJECT_DIR"
    # Run in background as module to fix imports
    nohup "$PROJECT_DIR/venv/bin/python3" -m agent.crypto_trading_agent.agent_server > agent/crypto_trading_agent/agent_server.log 2>&1 &
    echo "   ✅ Agent Server started (PID: $!)"
fi
sleep 2

# 3. Start Telegram Listener (The Ears)
echo "3️⃣  Starting Telegram Listener..."
# Check if running
if pgrep -f "telegram_listener.py" > /dev/null; then
    echo "   ⚠️  Telegram Listener already running"
else
    cd "$PROJECT_DIR/scripts"
    nohup "$PROJECT_DIR/venv/bin/python3" -u telegram_listener.py > telegram_listener.log 2>&1 &
    echo "   ✅ Telegram Listener started (PID: $!)"
fi
sleep 1

# 4. Start Daily Scheduler (The Clock)
echo "4️⃣  Starting Daily Scheduler..."
if pgrep -f "daily_refiner.py" > /dev/null; then
    echo "   ⚠️  Daily Scheduler already running"
else
    cd "$PROJECT_DIR/scripts"
    nohup "$PROJECT_DIR/venv/bin/python3" daily_refiner.py > daily_refiner.log 2>&1 &
    echo "   ✅ Daily Scheduler started (PID: $!)"
fi

echo ""
echo "✨ All Autonomous Services Started!"
echo "==================================="
echo "📊 FreqUI:       http://127.0.0.1:8081/ui"
echo "🧠 Agent API:    http://127.0.0.1:8000/docs"
echo "📝 Logs are being written to respective directories."
echo ""
echo "To stop everything, run: ./scripts/stop_all.sh"
