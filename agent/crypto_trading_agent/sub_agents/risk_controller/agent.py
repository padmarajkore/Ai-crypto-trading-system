"""Risk Controller sub-agent."""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

model = LiteLlm(
   #  model="nvidia_nim/openai/gpt-oss-20b",  # Using a valid NVIDIA model
    # model="nvidia_nim/moonshotai/kimi-k2-instruct-0905",  # Using a valid NVIDIA model
    # model="nvidia_nim/qwen/qwen3-coder-480b-a35b-instruct",  # Using a valid NVIDIA model
    # model="nvidia/llama-3.1-nemotron-ultra-253b-v1",  # Using a valid NVIDIA model
    model="openrouter/google/gemini-3-flash-preview",  # Using a valid NVIDIA model
    # model="nvidia_nim/deepseek-ai/deepseek-v3.2",  # Using a valid NVIDIA model
    # model="nvidia_nim/openai/gpt-oss-120b",  # Using a valid NVIDIA model
    stream=True,
    allowed_openai_params=["tools"]
)

GEMINI_MODEL = "gemini-3-flash-preview"

risk_controller_agent = LlmAgent(
    name="RiskControllerAgent",
    model=GEMINI_MODEL,
    # model=model,
    description="Validates proposed trades against portfolio risk guardrails.",
    instruction="""
    You are a chief risk officer ensuring prudent crypto trading.

    Responsibilities:
    - Evaluate each proposed trade idea for risk/reward, liquidity, and correlation.
    - Suggest position sizing guidelines and whether to approve / revise / reject.
    - Monitor compliance with constraints provided (max exposure, leverage limits, drawdown tolerance).

    Output as JSON with schema:
    {
      "verdict": "approve|revise|reject",
      "portfolio_notes": "",
      "ideas": [
        {
          "pair": "",
          "side": "",
          "max_position_pct": 0.05,
          "stop_loss": "",
          "take_profit": "",
          "adjustments": "",
          "warnings": []
        }
      ]
    }
    Keep warnings as an array of strings. Ensure numeric fields are actual numbers.
    """,
    output_key="risk_summary",
)
