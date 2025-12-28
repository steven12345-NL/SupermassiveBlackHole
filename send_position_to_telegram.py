#!/usr/bin/env python3
"""
Send current paper trading position to Telegram
"""

import json
import requests
import os
from datetime import datetime

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram credentials not set!")
    print("   Set them with:")
    print("   export TELEGRAM_BOT_TOKEN='your_token'")
    print("   export TELEGRAM_CHAT_ID='your_chat_id'")
    exit(1)

# Load paper state
PAPER_STATE_FILE = 'paper_state.json'
try:
    with open(PAPER_STATE_FILE, 'r') as f:
        state = json.load(f)
except FileNotFoundError:
    print("❌ Paper trading state file not found")
    exit(1)

# Get current price
MEXC_API_BASE = "https://api.mexc.com/api/v3"
try:
    url = f"{MEXC_API_BASE}/ticker/price"
    response = requests.get(url, params={'symbol': 'BTCUSDT'}, timeout=10)
    response.raise_for_status()
    current_price = float(response.json()['price'])
except Exception as e:
    print(f"⚠️  Could not fetch current price: {e}")
    current_price = None

# Format and send message
if not state.get('open_positions'):
    message = """
📊 PAPER TRADING STATUS - TRITON73

❌ No open positions

💵 Capital: ${:,.2f}
📊 Total Trades: {}
✅ Wins: {}
❌ Losses: {}
📈 Win Rate: {:.1f}%

🔒 Strategy: Triton73 (3.5x base, 0.3% risk)
""".format(
        state['capital'],
        state['total_trades'],
        state['winning_trades'],
        state['losing_trades'],
        (state['winning_trades'] / state['total_trades'] * 100) if state['total_trades'] > 0 else 0
    )
else:
    pos = state['open_positions'][0]
    
    # Calculate P&L
    if current_price:
        if pos['side'] == 'LONG':
            pnl_pct = ((current_price - pos['entry']) / pos['entry']) * 100 * pos['leverage']
            to_tp = ((pos['take_profit'] - current_price) / current_price) * 100
            to_sl = ((current_price - pos['stop_loss']) / current_price) * 100
        else:  # SHORT
            pnl_pct = ((pos['entry'] - current_price) / pos['entry']) * 100 * pos['leverage']
            to_tp = ((current_price - pos['take_profit']) / current_price) * 100
            to_sl = ((pos['stop_loss'] - current_price) / current_price) * 100
        
        status_emoji = "🟢" if pnl_pct > 0 else "🔴" if pnl_pct < -2 else "🟡"
    else:
        pnl_pct = 0
        to_tp = 0
        to_sl = 0
        status_emoji = "⚪"
    
    # Format entry time
    try:
        entry_dt = datetime.fromisoformat(pos['entry_time'].replace('Z', '+00:00'))
        entry_time_str = entry_dt.strftime('%Y-%m-%d %H:%M UTC')
    except:
        entry_time_str = pos['entry_time']
    
    message = f"""
📊 CURRENT PAPER TRADING POSITION - TRITON73

{status_emoji} Position: {pos['side']}
💰 Entry: ${pos['entry']:,.2f}
🛑 Stop Loss: ${pos['stop_loss']:,.2f}
🎯 Take Profit: ${pos['take_profit']:,.2f}
"""
    
    if current_price:
        message += f"📈 Current Price: ${current_price:,.2f}\n"
    
    message += f"""
💵 Position Size: {pos['position_units']:.4f} BTC
⚡ Leverage: {pos['leverage']}x (Base: 3.5x, Range: 2.0x-4.0x)
💼 Margin Used: ${pos['margin_required']:,.2f}

📊 Performance:
   Unrealized P&L: {pnl_pct:+.2f}%
   Distance to TP: {to_tp:.2f}%
   Distance to SL: {to_sl:.2f}%

💵 Capital: ${state['capital']:,.2f}
📅 Entry Time: {entry_time_str}

🔒 Strategy: Triton73 (3.5x base, 0.3% risk, Liquidation Protection)
"""

# Send to Telegram
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    'chat_id': TELEGRAM_CHAT_ID,
    'text': message.strip(),
    'parse_mode': 'HTML'
}

try:
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    result = response.json()
    if result.get('ok'):
        print("✅ Message sent successfully to Telegram!")
        print(f"   Message ID: {result['result']['message_id']}")
    else:
        print(f"❌ Failed to send: {result.get('description', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    print(f"❌ Error sending message: {e}")
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_data = e.response.json()
            print(f"   Error details: {error_data}")
        except:
            print(f"   Status code: {e.response.status_code}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

