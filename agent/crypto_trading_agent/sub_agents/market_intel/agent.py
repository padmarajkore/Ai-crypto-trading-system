"""Market Intelligence sub-agent."""

from google.adk.agents import LlmAgent
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

market_intel_agent = LlmAgent(
    name="MarketIntelAgent",
    model=GEMINI_MODEL,
    # model=model,
    description="Synthesizes crypto market context from provided data feeds.",
    instruction="""
    You are a crypto-market intelligence analyst.

    Goals:
    1. Analyze the provided raw OHLCV/candle data to identify trends and key levels.
    2. Summarize key market structure (trend, volatility, liquidity) for the provided pairs.
    3. Incorporate any news snippets or on-chain metrics supplied in the input.
    4. Highlight actionable insights and confidence levels (low / medium / high).

    Output format (Markdown):
    - Market Overview
    - Pair Highlights (bullet list per symbol)
    - Risks & Unknowns
    - Confidence: <low|medium|high>
    """,
    output_key="market_intel",
)
