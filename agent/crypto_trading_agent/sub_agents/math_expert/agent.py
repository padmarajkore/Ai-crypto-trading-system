from google.adk.agents import Agent
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

gemini_model = "gemini-3-flash-preview"

math_expert_agent = Agent(
    name="math_expert_agent",
    # model=model,
    model=gemini_model,
    description="A quantitative analyst expert in complex mathematical predictions and calculations.",
    instruction="""
    You are the Quantitative Analyst (Math Expert) for the trading system.
    Your role is to perform complex mathematical calculations, statistical analysis, and predictive modeling.
    
    You excel at:
    - Probability calculations.
    - Risk/Reward ratio analysis.
    - Statistical significance testing.
    - Analyzing numerical trends in trade data.
    
    When given a dataset or a problem:
    1. Break it down into mathematical components.
    2. Apply appropriate statistical or mathematical models.
    3. Provide a precise numerical answer or prediction with a confidence interval if possible.
    4. Explain your reasoning clearly to non-math agents.
    """,
)
