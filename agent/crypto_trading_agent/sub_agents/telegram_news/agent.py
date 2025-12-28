from google.adk.agents import Agent
from ...tools.news_db_tool import log_news, get_recent_news
# Placeholder for Freqtrade client to close trades
from ...tools.freqtrade_client import freqtrade_stop_bot, freqtrade_get_open_trades 
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

telegram_news_agent = Agent(
    name="telegram_news_agent",
    # model=model,
    model=GEMINI_MODEL,
    description="Analyzes crypto news from Telegram and decides on trade actions.",
    instruction="""
    You are the News Sentiment Analyst. Your source is a trusted Telegram group.
    
    Your responsibilities:
    1. **Analyze News**: Read incoming news snippets. Determine if the sentiment is POSITIVE, NEGATIVE, or NEUTRAL.
    2. **Assess Impact**: Decide if the news is HIGH IMPACT (requires immediate action) or LOW IMPACT (informational).
    3. **Take Action**:
       - If HIGH IMPACT NEGATIVE (e.g., "Binance hacked", "SEC ban"): Recommend closing all LONG positions immediately.
       - If HIGH IMPACT POSITIVE (e.g., "ETF Approved"): Recommend closing SHORT positions or entering LONGS.
    4. **Log It**: Use the `log_news` tool to save your analysis to the database.
    
    Output your decision clearly: "CLOSE_ALL_TRADES", "HOLD", or "NO_ACTION".
    """,
    tools=[log_news, get_recent_news, freqtrade_get_open_trades],
)
