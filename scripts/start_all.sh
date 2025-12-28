#!/bin/bash

# AI Crypto Trading System - Master Startup Script
# Starts all three components of the trading system

echo "🚀 AI Crypto Trading System - Starting All Components"
echo "======================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 Project Directory: $PROJECT_DIR"
echo ""

# Check if components exist
if [ ! -d "$PROJECT_DIR/freqtrade" ]; then
    echo "❌ Error: Freqtrade directory not found"
    exit 1
fi

if [ ! -d "$PROJECT_DIR/agent/crypto_trading_agent" ]; then
    echo "❌ Error: Agent directory not found"
    exit 1
fi

if [ ! -d "$PROJECT_DIR/dashboard" ]; then
    echo "❌ Error: Dashboard directory not found"
    exit 1
fi

echo "✅ All components found"
echo ""

# Function to check if a port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
    return $?
}

# Check ports
echo "🔍 Checking ports..."

if check_port 8081; then
    echo "⚠️  Port 8081 (Freqtrade) is already in use"
    read -p "Kill existing process? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:8081 | xargs kill -9 2>/dev/null
        echo "✅ Port 8081 freed"
    fi
fi

echo ""
echo "🎬 Starting services..."
echo ""

# Start Freqtrade in background
echo "1️⃣  Starting Freqtrade Bot..."
cd "$PROJECT_DIR/freqtrade"
osascript -e 'tell app "Terminal" to do script "cd '"$PROJECT_DIR"'/freqtrade && freqtrade trade --dry-run -c adk_config.json --strategy SampleStrategy"' 2>/dev/null || \
    (freqtrade trade --dry-run -c adk_config.json --strategy SampleStrategy > /dev/null 2>&1 &)
echo "   ✅ Freqtrade started on port 8081"
sleep 3

# Start AI Agent in foreground (or background)
echo "2️⃣  Starting AI Agent..."
read -p "Start AI Agent in new terminal? (y/n): " -n 1 -r
echo ""

cd "$PROJECT_DIR/agent/crypto_trading_agent"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    osascript -e 'tell app "Terminal" to do script "cd '"$PROJECT_DIR"'/agent/crypto_trading_agent && ./run_agent.sh"' 2>/dev/null || \
        echo "⚠️  Could not open new terminal. Run manually: cd $PROJECT_DIR/agent/crypto_trading_agent && ./run_agent.sh"
    echo "   ✅ AI Agent terminal opened"
else
    ./run_agent.sh
fi

echo ""
echo "✨ All services started!"
echo ""
echo "📊 Access Points:"
echo "   • FreqUI (Dashboard): http://127.0.0.1:8081/ui"
echo "   • Freqtrade API:      http://127.0.0.1:8081"
echo ""
echo "📝 To stop all services:"
echo "   Run: $PROJECT_DIR/scripts/stop_all.sh"
echo ""
