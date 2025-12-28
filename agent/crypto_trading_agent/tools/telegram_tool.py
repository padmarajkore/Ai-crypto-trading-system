import requests

# Hardcoded for simplicity in this session
BOT_TOKEN = "8586315160:AAHhRtxnGH9hvTW4_h0wSAsjkFnPNVT8z5Q"
CHAT_ID = "5999610154"

def send_telegram_message(message: str):
    """
    Sends a message to the user via Telegram.
    Use this to reply to user questions asked via /ask, or to notify of important events.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return "✅ Telegram message sent successfully."
        else:
            return f"⚠️ Telegram Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Failed to send Telegram message: {e}"
