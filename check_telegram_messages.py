#!/usr/bin/env python3
"""
Check recent Telegram messages from the bot
"""

import requests
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram credentials not set in this shell session")
    print("   Set them with:")
    print("   export TELEGRAM_BOT_TOKEN='your_token'")
    print("   export TELEGRAM_CHAT_ID='your_chat_id'")
    exit(1)

print("="*80)
print("CHECKING TELEGRAM MESSAGES")
print("="*80)
print()

# Get recent updates
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
try:
    response = requests.get(url, params={'limit': 20}, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if not data.get('ok'):
        print(f"❌ Error: {data.get('description', 'Unknown error')}")
        exit(1)
    
    updates = data.get('result', [])
    
    if not updates:
        print("📭 No messages found")
        print("   This could mean:")
        print("   - No messages have been sent yet")
        print("   - Messages are older than 24 hours (Telegram API limit)")
        print("   - Check your Telegram app directly")
        exit(0)
    
    print(f"Found {len(updates)} recent updates\n")
    
    # Filter messages from the bot to this chat
    bot_messages = []
    for update in updates:
        if 'message' in update:
            msg = update['message']
            if str(msg.get('chat', {}).get('id')) == str(TELEGRAM_CHAT_ID):
                bot_messages.append(msg)
    
    if not bot_messages:
        print("📭 No messages found in this chat")
        print("   Check your Telegram app - messages should appear there")
        exit(0)
    
    # Show most recent messages
    print(f"Most recent messages ({len(bot_messages)} found):\n")
    print("="*80)
    
    for i, msg in enumerate(reversed(bot_messages[-5:]), 1):  # Last 5
        timestamp = msg.get('date', 0)
        msg_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        text = msg.get('text', '')
        
        print(f"\nMessage #{i}:")
        print(f"  Time: {msg_time}")
        print(f"  Text: {text[:300]}")
        if len(text) > 300:
            print(f"  ... (truncated)")
        print("-"*80)
    
    print("\n✅ Check your Telegram app for the full messages!")
    print("="*80)
    
except requests.exceptions.RequestException as e:
    print(f"❌ Error connecting to Telegram API: {e}")
    print("   Check your internet connection and credentials")
except Exception as e:
    print(f"❌ Error: {e}")

