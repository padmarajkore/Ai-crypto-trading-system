"""Strategy Designer sub-agent."""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

GEMINI_MODEL = "gemini-3-flash-preview"

# Configure LiteLLM to use NVIDIA's API
model = LiteLlm(
   #  model="nvidia_nim/openai/gpt-oss-20b",  # Using a valid NVIDIA model
   #  model="nvidia_nim/moonshotai/kimi-k2-instruct-0905",  # Using a valid NVIDIA model
    # model="nvidia_nim/qwen/qwen3-coder-480b-a35b-instruct",  # Using a valid NVIDIA model
    # model="nvidia/llama-3.1-nemotron-ultra-253b-v1",  # Using a valid NVIDIA model
    model="openrouter/google/gemini-3-flash-preview",  # Using a valid NVIDIA model
    # model="nvidia_nim/deepseek-ai/deepseek-v3.2",  # Using a valid NVIDIA model
    # model="nvidia_nim/openai/gpt-oss-120b",  # Using a valid NVIDIA model
    stream=True,
    allowed_openai_params=["tools"]
)

strategy_designer_agent = LlmAgent(
    name="StrategyDesignerAgent",
    model=GEMINI_MODEL,
    # model=model,
    description="Transforms market intel into concrete trading strategies.",
    instruction="""
    You are a quantitative crypto strategist.

    Inputs: structured market intelligence plus optional portfolio constraints.

    Tasks:
    1. Propose up to 3 trade ideas (entry, exit, timeframe) aligned with received intel.
    2. Annotate each idea with rationale, confidence (0-1), and key indicators to monitor.
    3. Flag required Freqtrade settings (pair, stake amount, order type) when applicable.

    Output as JSON with schema:
    {
      "ideas": [
        {
          "pair": "BTC/USDT",
          "side": "long",
          "timeframe": "4h",
          "entry": "Spot pullback to 200 EMA",
          "exit_plan": "Scale out @ 3% / stop -1.5%",
          "confidence": 0.7,
          "rationale": "",
          "freqtrade_overrides": {
            "force_entry": false,
            "order_type": "limit",
            "stake_amount": 100
          }
        }
      ],
      "notes": "Portfolio level remarks"
    }
    Ensure numeric fields are numbers, not strings.
    """,
    output_key="strategy_proposals",
)
