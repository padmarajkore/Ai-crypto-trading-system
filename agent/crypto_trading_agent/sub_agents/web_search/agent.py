from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools import google_search
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

def get_current_time() -> dict:
    """
    Get the current time in the format YYYY-MM-DD HH:MM:SS
    """
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


GEMINI_MODEL = "gemini-3-flash-preview"

web_search_agent = Agent(
    name="web_search_agent",
    # model=model, # Updated to latest model
    model=GEMINI_MODEL,
    description="A research assistant that can verify information using Google Search.",
    instruction="""
    You are a Web Search Specialist for a crypto trading system.
    Your goal is to verify information, clear confusion, or find specific data points when requested by other agents.
    
    - Use the `google_search` tool to find accurate and up-to-date information.
    - Always verify the date of the information you find.
    - Provide concise summaries of your findings.
    - If you cannot find information, state that clearly.
    """,
    tools=[google_search],
)
