#!/bin/bash
# Quick Telegram Setup Script

echo "=========================================="
echo "Telegram Setup for Paper Trading"
echo "=========================================="
echo ""
echo "To get your Telegram credentials:"
echo ""
echo "1. Open Telegram and search for @BotFather"
echo "2. Send: /newbot"
echo "3. Follow the prompts to create a bot"
echo "4. Copy the token BotFather gives you"
echo ""
echo "5. Get your Chat ID:"
echo "   - Search for @userinfobot on Telegram"
echo "   - Start a chat - it will show your Chat ID"
echo ""
echo "=========================================="
echo ""
read -p "Enter your TELEGRAM_BOT_TOKEN: " BOT_TOKEN
read -p "Enter your TELEGRAM_CHAT_ID: " CHAT_ID

echo ""
echo "Setting environment variables..."
export TELEGRAM_BOT_TOKEN="$BOT_TOKEN"
export TELEGRAM_CHAT_ID="$CHAT_ID"

echo ""
echo "✅ Telegram credentials set!"
echo ""
echo "To make this permanent, add these lines to your ~/.zshrc:"
echo "export TELEGRAM_BOT_TOKEN='$BOT_TOKEN'"
echo "export TELEGRAM_CHAT_ID='$CHAT_ID'"
echo ""
echo "Or run this script before starting paper trading each time."
echo ""
echo "Testing Telegram connection..."
python3 test_telegram.py

