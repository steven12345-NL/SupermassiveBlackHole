# Telegram Setup Guide

## 🔑 How to Get Your Telegram Bot Token

### Step 1: Create a Bot with BotFather

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send the command**: `/newbot`
4. **Follow the prompts**:
   - Choose a name for your bot (e.g., "My Trading Bot")
   - Choose a username (must end in `bot`, e.g., "my_trading_bot")
5. **BotFather will give you a token** that looks like:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
6. **Copy and save this token** - this is your `TELEGRAM_BOT_TOKEN`

### Step 2: Get Your Chat ID

#### Method 1: Using @userinfobot (Easiest)
1. Search for `@userinfobot` on Telegram
2. Start a chat with it
3. It will reply with your Chat ID (a number like `123456789`)

#### Method 2: Using getUpdates API
1. Send a message to your bot (any message)
2. Visit this URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Look for `"chat":{"id":123456789}` in the response
4. The number is your `TELEGRAM_CHAT_ID`

#### Method 3: Using @RawDataBot
1. Search for `@RawDataBot` on Telegram
2. Start a chat with it
3. It will show your Chat ID in the response

### Step 3: Set Environment Variables

Once you have both:

```bash
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
export TELEGRAM_CHAT_ID='your_chat_id_here'
```

### Step 4: Test It

```bash
cd /Users/catharsis/test/final_trading_strategy
python3 test_telegram.py
```

---

## 🔍 If You Already Have a Bot

If you created a bot before but forgot the token:

1. **Open Telegram** and search for `@BotFather`
2. **Send**: `/mybots`
3. **Select your bot** from the list
4. **Click "API Token"** or send `/token`
5. **Copy the token** that appears

---

## 📝 Quick Reference

- **Bot Token**: Get from `@BotFather` → `/newbot` or `/mybots`
- **Chat ID**: Get from `@userinfobot` or `@RawDataBot`
- **Test**: Run `python3 test_telegram.py`

---

## ⚠️ Security Note

- **Never share your bot token** publicly
- **Never commit it to GitHub** (it's in `.gitignore`)
- **Keep it secret** - anyone with it can control your bot

---

## 🆘 Troubleshooting

### "Bot token is invalid"
- Make sure you copied the entire token
- Check for extra spaces
- Try creating a new bot

### "Chat not found"
- Make sure you sent at least one message to your bot first
- Verify the Chat ID is correct (should be a number)

### "Unauthorized"
- Your bot token might be wrong
- Try getting a new token from BotFather

---

*Need help? Check the Telegram Bot API documentation: https://core.telegram.org/bots/api*

