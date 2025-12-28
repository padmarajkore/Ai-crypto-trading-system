#!/bin/bash

# AI Crypto Trading System - Stop All Services

echo "🛑 Stopping AI Crypto Trading System..."
echo ""

# Kill Freqtrade (port 8081)
if lsof -i:8081 > /dev/null 2>&1; then
    echo "   Stopping Freqtrade..."
    lsof -ti:8081 | xargs kill -9 2>/dev/null
    echo "   ✅ Freqtrade stopped"
else
    echo "   ℹ️  Freqtrade not running"
fi

# Kill any running agent processes
pkill -f "run_agent.sh" 2>/dev/null || true
pkill -f "crypto_trading_agent" 2>/dev/null || true

# Kill Autonomous Services
echo "   Stopping Autonomous Services..."
pkill -f "agent_server.py" 2>/dev/null || true
pkill -f "telegram_listener.py" 2>/dev/null || true
pkill -f "daily_refiner.py" 2>/dev/null || true
echo "   ✅ Autonomous Services stopped"

echo ""
echo "✅ All services stopped"
