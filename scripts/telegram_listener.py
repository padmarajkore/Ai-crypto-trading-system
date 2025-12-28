import asyncio
import sqlite3
import os
import requests
from telethon import TelegramClient, events

# --- Configuration ---
# Get these from https://my.telegram.org (API development tools)
API_ID = 'your_api_id_here'
API_HASH = 'your_api_hash_here'

# List of Channel Usernames to listen to
CHANNELS_TO_LISTEN = ['testnewsh', 'cryptocurrency_media', 'crypto_news', 'WatcherGuru']

# Database Path
DB_PATH = "/Users/padamarajkore/Documents/ADK-crash-course/ai-crypto-trading-system/freqtrade/tradesv3.dryrun.sqlite"

# Agent API URL
AGENT_API_URL = "http://localhost:8000/trigger"

# Global dict to store resolved channel info
CHANNEL_MAP = {}  # {channel_id: channel_username}

# My User ID for /ask command auth
# Get this from @userinfobot in Telegram
MY_USER_ID = 0000000000

# --- Database Helper ---
def log_news_to_db(source, content):
    """Logs the incoming news to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                content TEXT,
                sentiment_score REAL,
                impact_level TEXT,
                action_taken TEXT
            )
        ''')
        
        cursor.execute('''
            INSERT INTO news_sentiment (source, content, sentiment_score, impact_level, action_taken)
            VALUES (?, ?, ?, ?, ?)
        ''', (source, content, 0.0, "PENDING", "none"))
        
        conn.commit()
        conn.close()
        print(f"✅ Logged news from {source}: {content[:50]}...")
    except Exception as e:
        print(f"❌ Error logging to DB: {e}")

def trigger_news_agent(source, content):
    """Sends a trigger to the AI Agent API (non-blocking)."""
    import threading
    
    def _trigger():
        try:
            message = f"New high-priority news received from {source}: '{content}'. Please analyze this using the TelegramNewsAgent and decide if we need to close any trades."
            response = requests.post(AGENT_API_URL, json={"message": message}, timeout=600)
            print(f"🔔 AI Agent triggered successfully. Response: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Could not trigger AI Agent: {e}")
    
    thread = threading.Thread(target=_trigger, daemon=True)
    thread.start()
    print("🚀 AI Agent trigger sent (processing in background)")

# --- Telegram Client ---
client = TelegramClient('anon', API_ID, API_HASH)

async def resolve_channels():
    """Resolves all channel usernames to their entity IDs."""
    global CHANNEL_MAP
    from telethon.tl.functions.channels import JoinChannelRequest
    
    print("\n🔗 Resolving channel entities...")
    for channel in CHANNELS_TO_LISTEN:
        try:
            entity = await client.get_entity(channel)
            # Store both positive and negative IDs (Telegram uses negative for channels)
            CHANNEL_MAP[entity.id] = channel
            CHANNEL_MAP[-entity.id] = channel
            CHANNEL_MAP[-100*abs(entity.id) + entity.id] = channel  # Full channel ID format
            
            print(f"📌 Resolved: {channel} (ID: {entity.id})")
            
            # Try to join if not already a member
            if hasattr(entity, 'left') and entity.left:
                await client(JoinChannelRequest(channel))
                print(f"   ✅ Joined channel")
        except Exception as e:
            print(f"⚠️ Could not resolve {channel}: {e}")
    
    print(f"\n📡 Monitoring {len(CHANNELS_TO_LISTEN)} channels")

# Handler for ALL new messages (we filter manually)
@client.on(events.NewMessage())
async def catch_all_handler(event):
    """Catches ALL new messages and filters for our channels."""
    try:
        chat = await event.get_chat()
        chat_id = event.chat_id
        
        # Get username or title
        source = getattr(chat, 'username', None) or getattr(chat, 'title', None) or str(chat_id)
        
        # Check if this is from one of our monitored channels (by ID or username)
        is_monitored = (
            chat_id in CHANNEL_MAP or 
            abs(chat_id) in [abs(k) for k in CHANNEL_MAP.keys()] or
            (source and source.lower() in [c.lower() for c in CHANNELS_TO_LISTEN])
        )
        
        if is_monitored:
            content = event.text
            if content and len(content.strip()) > 0:
                # Deduplication: Check if message is essentially same as recent ones
                import hashlib
                msg_hash = hashlib.md5(content.strip().encode()).hexdigest()
                current_time = asyncio.get_event_loop().time()
                
                # Clean up old hashes (simple linear scan or just let it grow for now/restart clears it)
                # For simplicity, we use a global dict with timestamp
                global MESSAGE_CACHE
                if 'MESSAGE_CACHE' not in globals():
                    MESSAGE_CACHE = {}
                
                # Check for duplicates within 10 minutes (600 seconds)
                if msg_hash in MESSAGE_CACHE:
                    if current_time - MESSAGE_CACHE[msg_hash] < 600:
                        print(f"♻️ Skipping duplicate message from {source}")
                        return
                
                MESSAGE_CACHE[msg_hash] = current_time
                
                print(f"📩 New Message from {source} (ID: {chat_id})")
                log_news_to_db(source, content)
                trigger_news_agent(source, content)
    except Exception as e:
        print(f"⚠️ Error processing message: {e}")


def call_agent_sync(message):
    """Synchronously calls the agent API and returns the result."""
    try:
        # We wrap the user query to give context
        full_prompt = f"User Question via Telegram: {message}. You MUST use the `send_telegram_message` tool to reply."
        response = requests.post(AGENT_API_URL, json={"message": full_prompt}, timeout=900)
        
        # NOTE: standard ADK agent endpoint usually returns status, not the text response directly
        # To get the actual answer, we would need to read the agent logs or have the agent callback.
        # For now, we confirm receipt.
        if response.status_code == 200:
             return "✅ Request sent to Agent. (Check logs for full reasoning)"
        else:
            return f"⚠️ Agent returned status: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Handler for /ask commands (Chat with AI Agent)
@client.on(events.NewMessage(pattern='/ask'))
async def ask_handler(event):
    """Handles /ask commands to chat with the AI Agent."""
    sender_id = event.sender_id
    
    # Optional: Security check (uncomment to restrict to only you)
    if sender_id != MY_USER_ID:
         print(f"⚠️ Unauthorized /ask from {sender_id}")
         # await event.reply("⚠️ You are not authorized.")
         # return

    query = event.text.replace('/ask', '').strip()
    if not query:
        await event.reply("❓ Please provide a question. Example: `/ask status`")
        return

    print(f"💬 Received /ask from {sender_id}: {query}")
    await event.reply("🤖 Analyzing... please wait a moment.")

    # Call Agent API in a separate thread to avoid blocking
    loop = asyncio.get_event_loop()
    try:
        response_text = await loop.run_in_executor(None, call_agent_sync, query)
        await event.reply(response_text)
            
    except Exception as e:
        await event.reply(f"❌ Error communicating with AI Agent: {e}")
        print(f"❌ Agent Error: {e}")

async def main():
    print("🎧 Telegram News Listener Started...")
    print(f"   (Enable /ask command for User ID: {MY_USER_ID})")
    print(f"Target channels: {', '.join(CHANNELS_TO_LISTEN)}")
    print(f"Logging to: {DB_PATH}")
    print(f"Triggering Agent at: {AGENT_API_URL}")
    
    await client.start()
    await resolve_channels()
    
    print("\n✅ Listener is now active (catch-all mode)...")
    print("📋 Waiting for messages from monitored channels...\n")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    if not os.path.exists("anon.session"):
        print("⚠️  First run: You will be asked to enter your phone number to log in.")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Listener Stopped.")
