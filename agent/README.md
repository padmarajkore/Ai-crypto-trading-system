# Crypto Trading Agent (Freqtrade Integration)

This example demonstrates how to orchestrate a real-world crypto trading workflow with the Google Agent Development Kit (ADK) by integrating with the [Freqtrade](https://www.freqtrade.io/) open-source trading bot.

The agentic system coordinates market analysis, strategy design, and trade execution while delegating low-level trading actions to Freqtrade via its REST API.

## Architecture Overview

```
ai-crypto-trading-system/agent/
├── README.md
└── crypto_trading_agent/
    ├── __init__.py
    ├── agent.py              # Root coordinator agent
    ├── .env                  # Your credentials (not committed to git)
    ├── .env.example          # Environment template for Google + Freqtrade secrets
    ├── run_agent.sh          # Agent startup script
    ├── tools/
    │   ├── __init__.py
    │   └── freqtrade_client.py  # REST API wrappers exposed as ADK tools
    └── sub_agents/
        ├── __init__.py
        ├── market_intel/
        │   └── agent.py      # LLM market-sentiment synthesis
        ├── strategy_designer/
        │   └── agent.py      # LLM strategy proposal generation
        └── risk_controller/
            └── agent.py      # LLM risk checks & position sizing guidance
```

### Agent Responsibilities

1. **CryptoTradingManager (root agent)** – orchestrates workflow, calls sub-agents as tools, and triggers Freqtrade REST endpoints.
2. **MarketIntelAgent** – synthesizes technical and news insights from provided market data.
3. **StrategyDesignerAgent** – drafts trade setups (entry/exit, timeframe, confidence) based on intel.
4. **RiskControllerAgent** – evaluates strategy compliance with risk rules and suggests size/hedging.

### Tooling Layer

The manager uses Python function tools (wrappers around REST endpoints) to:
- Inspect bot health (`/ping`, `/status`)
- Retrieve open trades and performance metrics
- Submit manual entries/exits via `forceenter` / `forceexit`
- Pause, stop, or resume the bot (`/pause`, `/start`)

These wrappers rely on environment variables defined in `.env`.

## Prerequisites

1. **Python environment** – reuse the repository-level `.venv` and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. **Google API key** – needed for Gemini models used by ADK agents.
3. **Running Freqtrade instance** – follow the official [Docker Quickstart](https://www.freqtrade.io/en/stable/docker_quickstart/) to spin up Freqtrade with REST API enabled.

## Configuration

Copy the environment template and provide secrets:

```bash
cd crypto_trading_agent
cp .env.example .env
```

Update the file with your credentials:

```env
GOOGLE_API_KEY=your_google_key
FREQTRADE_API_URL=http://127.0.0.1:8080
FREQTRADE_USERNAME=Freqtrader
FREQTRADE_PASSWORD=SuperSecret1!
FREQTRADE_VERIFY_TLS=false
```

also in the file

into into ai-crypto-trading-system/agent/crypto_trading_agent/tools/telegram_tool.py

add

``` agentic_system communication
BOT_TOKEN = "add_your_bot_token"
CHAT_ID = "chat_id"
```

> **note**: refer telegram docs/project readme to create one BOT_TOKEN.

> **Security note:** keep the API bound to localhost or tunnel it via SSH/VPN. The REST API provides full control over your bot.

## Running the Agent

```bash
# Navigate to the agent directory
cd /path/to/ai-crypto-trading-system/agent/crypto_trading_agent

# Run the agent
./run_agent.sh
```

1. Select `crypto_trading_agent` in the ADK web UI.
2. Ask for market analysis, request new strategies, or instruct the agent to enter/exit positions.

## Freqtrade Integration Notes

- The helper module uses `requests` with HTTP Basic Auth to call `/api/v1/*` endpoints.
- Responses are normalized into dicts that ADK tools can return directly.
- `forceenter` and `forceexit` endpoints are exposed for manual overrides; ensure `force_entry_enable` is enabled in your Freqtrade config.
- Extend `freqtrade_client.py` with additional endpoints (e.g., `/performance`, `/balance`) as needed.

## Next Steps

- Add automated sentiment feeds (news/price APIs) as additional tools feeding the MarketIntelAgent.
- Schedule agent runs or connect it to alerts for continuous monitoring.
- Store generated strategies/trade rationales in persistent storage for auditing.
