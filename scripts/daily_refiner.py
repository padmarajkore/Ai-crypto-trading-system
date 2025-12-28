import requests
import time
import datetime
import sys

AGENT_API_URL = "http://localhost:8000/trigger"

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

def trigger_strategy_refiner():
    """Triggers the Strategy Refiner Agent."""
    print(f"⏰ Triggering Hourly Strategy Refinement at {datetime.datetime.now()}")
    try:
        message = "It is time for the hourly strategy review. Please use the StrategyRefinerAgent to analyze performance and recent news, read the current strategy with read_strategy_code, and then SAVE the refined strategy using update_strategy_code."
        response = requests.post(AGENT_API_URL, json={"message": message}, timeout=1800)  # 30 min timeout
        print(f"✅ Agent Response: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"⚠️ Request timed out (agent might still be processing)")
    except Exception as e:
        print(f"❌ Error triggering agent: {e}")

if __name__ == "__main__":
    print(f"🗓️ Hourly Strategy Refiner Started at {datetime.datetime.now()}")
    print(f"⏳ Will trigger every 1 hour...")
    print("")
    
    while True:
        # Wait for 1 hour
        time.sleep(7200)  # Run every 2 hours
        trigger_strategy_refiner()
        print("")  # Add spacing between triggers
