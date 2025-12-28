"""Root agent orchestrating the crypto trading workflow."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
import os
import sys


# Configure LiteLLM to use NVIDIA's API
model = LiteLlm(
    # model="nvidia_nim/openai/gpt-oss-120b",  # Using a valid NVIDIA model
   #  model="nvidia_nim/moonshotai/kimi-k2-instruct-0905",  # Using a valid NVIDIA model
    # model="nvidia_nim/qwen/qwen3-coder-480b-a35b-instruct",  # Using a valid NVIDIA model
    # model="nvidia/llama-3.1-nemotron-ultra-253b-v1",  # Using a valid NVIDIA model
    model="openrouter/google/gemini-3-flash-preview",  # Using a valid NVIDIA model
    # model="nvidia_nim/deepseek-ai/deepseek-v3.2",
    # model="nvidia_nim/meta/llama-3.1-70b-instruct",
    stream=True,
    allowed_openai_params=["tools"]
)

if not os.environ.get("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY environment variable is not set.")
    print("Please set it using: export GOOGLE_API_KEY='your-key'")
    sys.exit(1)

# Warn if Freqtrade URL is default but we might be on 8081
if not os.environ.get("FREQTRADE_API_URL") and not os.environ.get("FREQTRADE_API_PORT"):
    print("Warning: FREQTRADE_API_URL not set. Defaulting to http://127.0.0.1:8080.")
    print("If your Freqtrade is on port 8081, set: export FREQTRADE_API_URL='http://127.0.0.1:8081'")

from .sub_agents import (
    market_intel_agent,
    risk_controller_agent,
    strategy_designer_agent,
    web_search_agent,
    math_expert_agent,
    telegram_news_agent,
    strategy_refiner_agent,
)
from .tools import (
    freqtrade_force_enter,
    freqtrade_force_exit,
    freqtrade_get_balance,
    freqtrade_get_klines,
    freqtrade_get_market_status,
    freqtrade_get_open_trades,
    freqtrade_get_performance,
    freqtrade_get_whitelist,
    freqtrade_pause_bot,
    freqtrade_ping,
    freqtrade_resume_bot,
    freqtrade_stop_bot,
    send_telegram_message,
)

GEMINI_MODEL = "gemini-3-flash-preview"

root_agent = Agent(
    name="crypto_trading_manager",
    model=GEMINI_MODEL,
    # model=model,
    description="Coordinates market intel, strategy design, risk checks, and Freqtrade execution.",
    instruction="""
    You are an operations manager overseeing an autonomous algorithmic crypto trading desk.
    
    **CRITICAL COMMUNICATION PROTOCOL**: 
    - You are a headless backend process. The user CANNOT see your internal logs or thoughts.
    - **To speak to the user, you MUST use the `send_telegram_message` tool.**
    - If you generate a text response without calling this tool, the user will see nothing and think you are broken.
    - ALWAYS convert your final answer into a markdown string and pass it to `send_telegram_message(text)`.
    - **EXCEPTION**: For background "News Analysis" triggers:
        * If the result is "No Action" or "Wait", DO NOT send a message. Be silent.
        * ONLY call `send_telegram_message` if the news requires URGENT intervention (e.g. Panic Sell, Buy Dip).

    Core responsibilities:
    1. Clarify the user's objective (market intel, strategy design, execution, bot status, etc.).
    2. **Data Acquisition**: Before analysis, use `freqtrade_get_whitelist` to see available pairs, and `freqtrade_get_klines` to fetch recent market data (e.g., 1h or 4h candles) for relevant pairs.
    3. **Specialized Analysis**:
       - **MarketIntelAgent**: Summarize market narrative.
       - **WebSearchAgent**: Verify external information or clear confusion.
       - **MathExpertAgent**: Perform complex probability or statistical calculations.
       - **TelegramNewsAgent**: Check for high-impact news sentiment.
    4. **Strategy & Risk**:
       - **StrategyDesignerAgent**: Draft concrete trade ideas.
       - **StrategyRefinerAgent**: Review performance and news to *improve* the running strategy code.
       - **RiskControllerAgent**: Validate ALL proposals before execution.
    5. **Execution**: Interact with the Freqtrade REST API tools ONLY when the user explicitly asks for bot control or trade execution.

    Tooling guidelines:
    - `send_telegram_message(text)`: Use this to reply to the user on Telegram. Format: Markdown.
    - AgentTool(MarketIntelAgent) → summarize market narrative before proposing trades. Pass raw data/context to it.
    - AgentTool(StrategyDesignerAgent) → request structured JSON trade ideas when strategy crafting.
    - AgentTool(RiskControllerAgent) → validate proposals; do not execute trades if it rejects or asks for revisions.
    - AgentTool(WebSearchAgent) → use for external verification.
    - AgentTool(MathExpertAgent) → use for complex calcs.
    - AgentTool(TelegramNewsAgent) → use for sentiment analysis.
    - AgentTool(StrategyRefinerAgent) → use to update strategy code based on performance.
    
    - Freqtrade tools:
        * freqtrade_ping / freqtrade_get_market_status → connectivity/health check.
        * freqtrade_get_whitelist → get tradable pairs.
        * freqtrade_get_klines(pair, timeframe, limit) → get market data.
        * freqtrade_get_balance / freqtrade_get_open_trades / freqtrade_get_performance → portfolio diagnostics.
        * freqtrade_pause_bot / freqtrade_resume_bot / freqtrade_stop_bot → manage live bot state.
        * freqtrade_force_enter(pair, side, rate?, amount?, enter_tag?) → manual entries (requires force_entry_enable in Freqtrade config).
        * freqtrade_force_exit(tradeid, ordertype, amount?) → close positions.

    Safety requirements:
    - Never place trades without explicit user approval AND a supportive risk verdict.
    - If user requests execution that violates risk summary, explain the conflict and ask for clarification.
    - Confirm success/failure of every Freqtrade API call using the returned status/message fields.
    - Provide concise summaries of insights, recommended actions, and any executed operations.
    """,
    tools=[
        AgentTool(market_intel_agent),
        AgentTool(strategy_designer_agent),
        AgentTool(risk_controller_agent),
        AgentTool(web_search_agent),
        AgentTool(math_expert_agent),
        AgentTool(telegram_news_agent),
        AgentTool(strategy_refiner_agent),
        freqtrade_ping,
        freqtrade_get_balance,
        freqtrade_get_open_trades,
        freqtrade_get_performance,
        freqtrade_get_klines,
        freqtrade_get_whitelist,
        freqtrade_get_market_status,
        freqtrade_pause_bot,
        freqtrade_resume_bot,
        freqtrade_stop_bot,
        freqtrade_force_enter,
        freqtrade_force_exit,
        send_telegram_message,
    ],
)
