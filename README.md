# AI Crypto Trading System

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Personal%20Use-green.svg)](LICENSE)
[![Freqtrade](https://img.shields.io/badge/freqtrade-latest-orange.svg)](https://www.freqtrade.io/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4.svg)](https://ai.google.dev/adk)

An intelligent cryptocurrency trading system combining Google ADK AI agents with Freqtrade for automated trading with AI-powered market analysis, strategy design, and risk management.

## ✨ Features

- 🤖 **AI-Powered Trading**: Google ADK agents for market analysis, strategy design, and risk management
- ⚡ **Automated Execution**: Freqtrade bot for reliable trade execution
- 📊 **FreqUI Dashboard**: Built-in web interface for real-time monitoring and control
- 💬 **Telegram Integration**: Instant trade notifications and bot control via Telegram
- 💾 **Persistent Storage**: SQLite database for secure trade history
- 🔄 **Backtesting**: Test strategies against historical data
- 🎯 **Strategy Optimization**: Machine learning-powered hyperparameter tuning

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed
- **pip** package manager
- **Google API Key** ([Get one here](https://aistudio.google.com/app/apikey))
- **Telegram Bot Token & Chat ID** (optional, for notifications)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ai-crypto-trading-system
```

### 2. Setup Freqtrade

```bash
cd freqtrade
pip install -r requirements.txt
```

### 3. Configure AI Agent

```bash
cd ../agent/crypto_trading_agent

# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

Required environment variables:
- `GOOGLE_API_KEY`: Your Google AI API key
- `FREQTRADE_API_URL`: Freqtrade API endpoint (default: `http://127.0.0.1:8081`)
- `FREQTRADE_USERNAME`: API username (set in `adk_config.json`)
- `FREQTRADE_PASSWORD`: API password (set in `adk_config.json`)

### 4. Configure Telegram (Optional)

#### Get Telegram Bot Token

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather and send `/newbot`
3. **Follow the prompts**:
   - Choose a name for your bot (e.g., "My Trading Bot")
   - Choose a username (must end in 'bot', e.g., "my_trading_bot")
4. **Copy the token** - BotFather will send you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

#### Get Your Chat ID

1. **Start a chat** with your newly created bot
2. **Send any message** to the bot (e.g., "Hello")
3. **Open this URL** in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. **Find your chat_id** in the response - look for `"chat":{"id":123456789}`
5. **Copy the number** after `"id":` (e.g., `123456789`)

#### Add to Configuration

Edit `freqtrade/adk_config.json`:

```json
{
  "telegram": {
    "enabled": true,
    "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "123456789"
  }
}
```

> **Need detailed instructions?** See the [Telegram Setup Guide](docs/TELEGRAM_SETUP.md) for step-by-step instructions with troubleshooting.


### 5. Run the System

**Terminal 1 - Start Freqtrade:**
```bash
cd freqtrade
freqtrade trade --dry-run -c adk_config.json --strategy SampleStrategy
```

**Terminal 2 - Start AI Agent:**
```bash
cd agent/crypto_trading_agent
./run_agent.sh
```

**Access FreqUI:** Open [http://127.0.0.1:8081/ui](http://127.0.0.1:8081/ui) in your browser

### 6. Start Autonomous Mode (Optional)

For continuous operation:
```bash
caffeinate -i ./scripts/start_autonomous.sh
```

## 📁 Project Structure

```
ai-crypto-trading-system/
├── agent/                          # AI Trading Agent
│   ├── README.md
│   └── crypto_trading_agent/
│       ├── agent.py                # Root coordinator agent
│       ├── .env.example            # Environment template
│       ├── run_agent.sh            # Agent startup script
│       ├── tools/                  # Freqtrade API wrappers
│       └── sub_agents/             # Specialized AI agents
│           ├── market_intel/       # Market analysis
│           ├── strategy_designer/  # Strategy generation
│           └── risk_controller/    # Risk management
├── freqtrade/                      # Freqtrade Trading Bot
│   ├── README.md
│   ├── adk_config.json             # Bot configuration
│   ├── user_data/                  # Market data & logs
│   └── tradesv3.dryrun.sqlite      # Trade database
├── scripts/                        # Utility Scripts
│   ├── start_all.sh                # Start all services
│   ├── start_autonomous.sh         # Autonomous mode
│   ├── stop_all.sh                 # Stop all services
│   ├── telegram_listener.py        # Telegram bot
│   └── daily_refiner.py            # Daily strategy refinement
├── docs/                           # Documentation
├── GETTING_STARTED.md              # Detailed setup guide
├── FREQTRADE_FEATURES.md           # Feature documentation
└── README.md                       # This file
```

## 🔧 Configuration

### Freqtrade Configuration
- **Location**: `freqtrade/adk_config.json`
- **Key Settings**:
  - Trading pairs
  - Exchange settings
  - API credentials
  - Risk parameters
  - Telegram settings

### AI Agent Configuration
- **Location**: `agent/crypto_trading_agent/.env`
- **Key Settings**:
  - Google API key
  - Freqtrade API connection
  - Authentication credentials

## 📊 Components

### 1. AI Agent System
The multi-agent system orchestrates trading decisions:

- **CryptoTradingManager**: Root coordinator agent
- **MarketIntelAgent**: Analyzes market sentiment and technical indicators
- **StrategyDesignerAgent**: Generates trading strategies
- **RiskControllerAgent**: Manages risk and position sizing

### 2. Freqtrade Bot
Handles actual trade execution:

- Connects to cryptocurrency exchanges
- Executes buy/sell orders
- Manages open positions
- Provides REST API and web UI
- Sends Telegram notifications

### 3. Utility Scripts
Automation and monitoring tools:

- `start_all.sh`: Launch all components
- `telegram_listener.py`: Telegram bot for remote control
- `daily_refiner.py`: Daily strategy optimization

## 🛡️ Safety & Security

> [!WARNING]
> **This system is configured for DRY-RUN mode by default** (no real money at risk)

**Before enabling live trading:**
1. ✅ Thoroughly test strategies in dry-run mode
2. ✅ Understand the risks of automated trading
3. ✅ Start with small amounts
4. ✅ Monitor the system regularly
5. ✅ Keep API keys secure (never commit `.env` files)

**Security Best Practices:**
- Never share your `.env` file or API keys
- Use strong passwords for Freqtrade API
- Keep the API bound to localhost or use VPN/SSH tunnels
- Regularly review trade history and logs
- Enable 2FA on exchange accounts

## 📚 Additional Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)**: Comprehensive setup guide
- **[FREQTRADE_FEATURES.md](FREQTRADE_FEATURES.md)**: Detailed feature documentation
- **[docs/TELEGRAM_SETUP.md](docs/TELEGRAM_SETUP.md)**: Step-by-step Telegram bot setup
- **[agent/README.md](agent/README.md)**: AI agent architecture
- **[freqtrade/README.md](freqtrade/README.md)**: Freqtrade documentation

## 🐛 Troubleshooting

### Common Issues

**Freqtrade won't start:**
- Check that port 8081 is available
- Verify `adk_config.json` is valid JSON
- Ensure all dependencies are installed

**AI Agent connection errors:**
- Verify Freqtrade is running
- Check `.env` file has correct credentials
- Ensure `FREQTRADE_API_URL` matches Freqtrade's API port

**No trades executing:**
- Confirm you're in dry-run mode (check `adk_config.json`)
- Verify strategy conditions are being met
- Check logs in `freqtrade/user_data/logs/`

### Logs Location
- **Freqtrade**: `freqtrade/freqtrade.log`
- **AI Agent**: `agent/crypto_trading_agent/agent_server.log`
- **Scripts**: `scripts/*.log`

## 🤝 Contributing

This is a personal trading system. Feel free to fork and modify for your own use.

## ⚖️ License

For personal use only. See [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This software is for educational purposes only.**

- Do not risk money you cannot afford to lose
- USE THE SOFTWARE AT YOUR OWN RISK
- The authors assume NO RESPONSIBILITY for your trading results
- Always start with dry-run mode
- Understand the code before using it with real money
- Cryptocurrency trading carries significant risk

## 📞 Support

For issues and questions:
- Check the [documentation](docs/)
- Review [Freqtrade documentation](https://www.freqtrade.io)
- Check existing issues before creating new ones

---

**Built with:** [Freqtrade](https://www.freqtrade.io/) • [Google ADK](https://ai.google.dev/adk) • Python