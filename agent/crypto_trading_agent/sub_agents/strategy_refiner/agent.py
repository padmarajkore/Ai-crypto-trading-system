from google.adk.agents import Agent
from ...tools.strategy_manager import (
    read_strategy_code, 
    update_strategy_code, 
    create_and_switch_strategy, 
    list_strategies
)
from ...tools.news_db_tool import get_recent_news
# Assuming a tool to get trade stats exists or we use freqtrade_client
from ...tools.freqtrade_client import freqtrade_get_profit
from google.adk.models.lite_llm import LiteLlm

model = LiteLlm(
    # model="nvidia_nim/qwen/qwen3-coder-480b-a35b-instruct",  # Using a valid NVIDIA model
    # model="nvidia_nim/deepseek-ai/deepseek-v3.2",  # Using a valid NVIDIA model
    # model="nvidia_nim/openai/gpt-oss-120b",  # Using a valid NVIDIA model
    # model="nvidia/llama-3.1-nemotron-ultra-253b-v1",  # Using a valid NVIDIA model
    model="openrouter/google/gemini-3-flash-preview",  # Using a valid NVIDIA model

    stream=True,
    allowed_openai_params=["tools"]
)

GEMINI_MODEL = "gemini-3-flash-preview"

strategy_refiner_agent = Agent(
    name="strategy_refiner_agent",
    # model=model, # Reasoning model for coding
    model=GEMINI_MODEL,
    description="Reviews performance and news to refine the trading strategy code.",
    instruction="""
    You are the Lead Strategy Architect. Your GOAL is to generate 3-5% daily profit.
    
    **Inputs:**
    1. **Recent Performance**: Call `freqtrade_get_profit()`. If checks verify NO trades in the last 24h, this is UNACCEPTABLE.
    2. **Market Context**: Call `get_recent_news()`.
    3. **Existing Strategies**: Call `list_strategies()` to see what you have.
    
    **Decision Logic:**
    - **Scenario A: Current Strategy is Profitable**:
      - Call `read_strategy_code()` to inspect it.
      - Refine it slightly using `update_strategy_code()` (e.g. adjust stoploss, optimize entry).
      
    - **Scenario B: Zero Trades / Stagnant (CRITICAL)**:
      - The current strategy is too conservative. You MUST CHANGE TACTICS.
      - **Option 1**: Create a NEW, more aggressive strategy file (e.g. `AggressiveScalp.py`, `MomentumChaser.py`).
        - Use `create_and_switch_strategy(filename, code)`.
        - Ensure the new strategy uses significantly looser entry conditions (e.g. RSI crosses, simple EMA crossovers).
      - **Option 2**: If you already have multiple strategies, verify if another one suits the current market better and switch to it.
    
    **Knowledge Base:**
    - **Aggressive Strategies**: Lower RSI thresholds (e.g. buy at 40), shorter timeframes (5m, 1m).
    - **Safety**: Always keep a stoploss (e.g. -0.05).
    - **Class Name**: Must match the filename (e.g. file `Scalp.py` -> class `Scalp`).
    
    **Process:**
    1. Analyze performance.
    2. Analyze news.
    3. DECIDE: Refine current strategy OR Create/Switch to a new one.
    4. EXECUTE: Use `update_strategy_code` OR `create_and_switch_strategy`.
       - Do NOT just return text. You must use the tools to apply changes.
    """,
    tools=[read_strategy_code, update_strategy_code, create_and_switch_strategy, list_strategies, get_recent_news, freqtrade_get_profit],
)
