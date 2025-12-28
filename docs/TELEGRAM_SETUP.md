# Telegram Setup Guide

This guide will help you set up Telegram notifications for your AI Crypto Trading System.

## Why Use Telegram?

Telegram integration allows you to:
- 📱 Receive instant trade notifications on your phone
- 🎮 Control the bot remotely with commands
- 📊 Check status, profit, and performance on the go
- ⚠️ Get alerts for important events
- 📰 Monitor crypto news channels (advanced feature)

## Two Levels of Integration

### Level 1: Basic Bot Notifications (Freqtrade)
- **What you need**: Bot Token + Chat ID
- **Features**: Trade notifications, bot control commands
- **Used by**: `freqtrade/adk_config.json`

### Level 2: Advanced News Monitoring (Optional)
- **What you need**: API ID + API Hash + Bot Token + Chat ID
- **Features**: Monitor Telegram news channels, trigger AI analysis
- **Used by**: `scripts/telegram_listener.py`

> **Most users only need Level 1.** Level 2 is for advanced users who want to monitor crypto news channels.

---

## Level 1: Basic Setup (Required)

This section covers the basic bot setup for Freqtrade notifications.

### Step 1: Create a Telegram Bot

1. **Open Telegram** on your phone or desktop
2. **Search for `@BotFather`** in the search bar
3. **Start a conversation** by clicking "Start" or sending `/start`
4. **Create a new bot** by sending the command:
   ```
   /newbot
   ```

5. **Choose a name** for your bot when prompted:
   ```
   Example: My Crypto Trading Bot
   ```
   This is the display name users will see.

6. **Choose a username** for your bot:
   ```
   Example: my_crypto_trading_bot
   ```
   > **Important:** Username must end with `bot` (e.g., `my_trading_bot`, `crypto_alerts_bot`)

7. **Save your token** - BotFather will respond with a message like:
   ```
   Done! Congratulations on your new bot. You will find it at t.me/my_crypto_trading_bot.
   
   Use this token to access the HTTP API:
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
   
   Keep your token secure and store it safely, it can be used by anyone to control your bot.
   ```

   **Copy and save this token!** You'll need it for configuration.

### Step 2: Get Your Chat ID

#### Method 1: Using the Bot API (Recommended)

1. **Start a chat** with your newly created bot
   - Search for your bot's username in Telegram
   - Click "Start" or send any message (e.g., "Hello")

2. **Open this URL** in your web browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
   
   Example:
   ```
   https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz/getUpdates
   ```

3. **Find your chat_id** in the JSON response:
   ```json
   {
     "ok": true,
     "result": [
       {
         "update_id": 123456789,
         "message": {
           "message_id": 1,
           "from": {
             "id": 987654321,
             ...
           },
           "chat": {
             "id": 987654321,  ← This is your chat_id
             "first_name": "Your Name",
             "type": "private"
           },
           ...
         }
       }
     ]
   }
   ```

4. **Copy the chat ID** - it's the number after `"chat":{"id":` (e.g., `987654321`)

#### Method 2: Using @userinfobot

1. **Search for `@userinfobot`** in Telegram
2. **Start a chat** and send `/start`
3. The bot will reply with your user information including your **ID**
4. **Copy your ID** - this is your chat_id

### Step 3: Configure Freqtrade

1. **Open the configuration file**:
   ```bash
   nano freqtrade/adk_config.json
   ```

2. **Find the telegram section** and update it:
   ```json
   "telegram": {
       "enabled": true,
       "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
       "chat_id": "987654321",
       "notification_settings": {
           "status": "on",
           "warning": "on",
           "startup": "on",
           "entry": "on",
           "entry_fill": "on",
           "entry_cancel": "on",
           "exit": "on",
           "exit_fill": "on",
           "exit_cancel": "on",
           "protection_trigger": "on",
           "protection_trigger_global": "on"
       }
   }
   ```

3. **Save the file** (Ctrl+O, Enter, Ctrl+X in nano)

### Step 4: Test the Connection

1. **Start Freqtrade**:
   ```bash
   cd freqtrade
   freqtrade trade --dry-run -c adk_config.json --strategy SampleStrategy
   ```

2. **Check Telegram** - you should receive a startup message from your bot!

3. **Try a command** - send `/status` to your bot to check if it responds

## Level 2: Advanced Setup (Optional)

This section covers the setup for `scripts/telegram_listener.py`, which allows the AI Agent to listen to news channels.

### Step 1: Get Telegram API ID and API Hash

1. **Log in** to your Telegram account at [https://my.telegram.org](https://my.telegram.org).
2. Click on **"API development tools"**.
3. Fill in the **Create new application** form:
   - **App title**: Anything (e.g., `My Trading News Listener`)
   - **Short name**: Anything (e.g., `news_listener`)
   - **URL**: (Leave blank or enter any URL)
   - **Platform**: Desktop
   - **Description**: (Leave blank)
4. Click **"Create application"**.
5. Your **App api_id** and **App api_hash** will be displayed.
6. **Copy these values** - you'll need them for the listener script.

### Step 2: Configure the Listener Script

1. **Open the listener script**:
   ```bash
   nano scripts/telegram_listener.py
   ```

2. **Update the configuration**:
   ```python
   # --- Configuration ---
   API_ID = '1234567'            # Your App api_id
   API_HASH = 'abcdef123456...'  # Your App api_hash
   MY_USER_ID = 987654321        # Your Chat ID (from Level 1/Step 2)
   ```

3. **Save and exit** (Ctrl+O, Enter, Ctrl+X).

### Step 3: Run the Listener

For the first run, you will need to authenticate with your phone number:

```bash
python scripts/telegram_listener.py
```

Follow the prompts in the terminal to enter your phone number and the login code sent to your Telegram app. A file named `anon.session` will be created to keep you logged in.

---

## Available Telegram Commands

Once configured, you can control your bot with these commands:

| Command | Description |
|---------|-------------|
| `/start` | Start the trader |
| `/stop` | Stop the trader |
| `/status` | Show open trades |
| `/profit` | Show profit summary |
| `/balance` | Show account balance |
| `/daily` | Show daily profit/loss |
| `/performance` | Show performance by pair |
| `/help` | Show all commands |
| `/version` | Show bot version |

## Troubleshooting

### Bot doesn't respond to commands

**Problem:** You send commands but the bot doesn't reply.

**Solutions:**
1. Verify the bot token is correct in `adk_config.json`
2. Make sure `"enabled": true` in the telegram section
3. Restart Freqtrade after changing configuration
4. Check that you're messaging the correct bot

### Can't find chat_id in getUpdates

**Problem:** The getUpdates URL returns empty results.

**Solutions:**
1. Make sure you've sent at least one message to your bot first
2. Try the @userinfobot method instead
3. Check that you're using the correct bot token in the URL

### Getting "Unauthorized" error

**Problem:** Freqtrade logs show "Telegram Unauthorized" errors.

**Solutions:**
1. Verify your bot token is correct (no extra spaces)
2. Make sure you copied the entire token from BotFather
3. Try creating a new bot and using its token

### Receiving messages but can't send commands

**Problem:** You get notifications but commands don't work.

**Solutions:**
1. Verify your chat_id is correct
2. Make sure the chat_id is a string in the config: `"chat_id": "123456789"`
3. Try using @userinfobot to confirm your chat_id

### Bot token exposed or compromised

**Problem:** You accidentally shared your bot token publicly.

**Solutions:**
1. Go to @BotFather
2. Send `/mybots`
3. Select your bot
4. Choose "API Token"
5. Click "Revoke current token"
6. Get the new token and update your config

## Security Best Practices

> [!WARNING]
> **Keep your bot token secret!** Anyone with your token can control your bot.

✅ **Do:**
- Store the token in `adk_config.json` (which is gitignored)
- Use environment variables for extra security
- Revoke and regenerate if exposed

❌ **Don't:**
- Commit the token to GitHub
- Share it in public channels
- Post screenshots showing the token

## Advanced Configuration

### Using Environment Variables

For extra security, you can use environment variables:

1. **Set environment variables**:
   ```bash
   export TELEGRAM_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   export TELEGRAM_CHAT_ID="987654321"
   ```

2. **Reference in config** (requires custom setup):
   ```json
   "telegram": {
       "enabled": true,
       "token": "${TELEGRAM_TOKEN}",
       "chat_id": "${TELEGRAM_CHAT_ID}"
   }
   ```

### Multiple Chat IDs

To send notifications to multiple users:

```json
"telegram": {
    "enabled": true,
    "token": "your-token",
    "chat_id": "123456789,987654321,555555555"
}
```

Separate multiple chat IDs with commas.

## Next Steps

After setting up Telegram:
1. ✅ Test all commands to ensure they work
2. ✅ Customize notification settings in `adk_config.json`
3. ✅ Set up the autonomous mode for 24/7 operation
4. ✅ Monitor your trades via Telegram notifications


