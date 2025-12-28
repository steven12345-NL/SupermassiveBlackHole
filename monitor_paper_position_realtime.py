#!/usr/bin/env python3
"""
Real-time Paper Position Monitor
Checks position status every minute and sends Telegram alerts when TP/SL is hit
Runs continuously until position is closed
"""

import json
import requests
import os
import time
from datetime import datetime
import sys

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# MEXC API
MEXC_API_BASE = "https://api.mexc.com/api/v3"
PAPER_STATE_FILE = 'paper_state.json'

# Check interval (seconds)
CHECK_INTERVAL = 60  # Check every minute


def get_current_price(symbol='BTCUSDT'):
    """Get current price from MEXC"""
    try:
        url = f"{MEXC_API_BASE}/ticker/price"
        response = requests.get(url, params={'symbol': symbol}, timeout=10)
        response.raise_for_status()
        return float(response.json()['price'])
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def send_telegram(message):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending Telegram: {e}")
        return False


def check_position_status():
    """Check if position should be closed and send alert"""
    try:
        with open(PAPER_STATE_FILE, 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        print("No paper trading state file found")
        return False
    
    if not state.get('open_positions'):
        return False  # No position to monitor
    
    position = state['open_positions'][0]
    current_price = get_current_price()
    
    if not current_price:
        return False
    
    entry = position['entry']
    stop_loss = position['stop_loss']
    take_profit = position['take_profit']
    side = position['side']
    leverage = position['leverage']
    
    should_close = False
    exit_price = None
    result = None
    reason = None
    
    if side == 'LONG':
        if current_price <= stop_loss:
            exit_price = stop_loss
            result = 'LOSS'
            reason = 'Stop Loss Hit'
            should_close = True
        elif current_price >= take_profit:
            exit_price = take_profit
            result = 'WIN'
            reason = 'Take Profit Hit'
            should_close = True
    else:  # SHORT
        if current_price >= stop_loss:
            exit_price = stop_loss
            result = 'LOSS'
            reason = 'Stop Loss Hit'
            should_close = True
        elif current_price <= take_profit:
            exit_price = take_profit
            result = 'WIN'
            reason = 'Take Profit Hit'
            should_close = True
    
    if should_close:
        # Calculate P&L
        if side == 'LONG':
            pnl_amount = position['position_units'] * (exit_price - entry) * leverage
        else:
            pnl_amount = position['position_units'] * (entry - exit_price) * leverage
        
        fees = (position['position_units'] * entry + position['position_units'] * exit_price) * 0.001
        net_pnl = pnl_amount - fees
        pnl_pct = (net_pnl / state['capital']) * 100
        
        # Send alert
        message = f"""
🚨 POSITION CLOSED - TRITON73 PAPER TRADING

{result} - {reason}

📊 Position Details:
   Side: {side}
   Entry: ${entry:,.2f}
   Exit: ${exit_price:,.2f}
   Leverage: {leverage}x

💰 P&L:
   Amount: ${net_pnl:+,.2f}
   Percentage: {pnl_pct:+.2f}%

💵 Capital:
   Before: ${state['capital']:,.2f}
   After: ${state['capital'] + net_pnl:,.2f}

📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🔒 Strategy: Triton73 (3.5x base, 0.3% risk)
"""
        
        send_telegram(message)
        print(f"\n🚨 ALERT SENT: {result} - {reason}")
        print(f"   Exit Price: ${exit_price:,.2f}")
        print(f"   P&L: ${net_pnl:+,.2f} ({pnl_pct:+.2f}%)")
        return True
    
    # Show current status
    if side == 'LONG':
        pnl_pct = ((current_price - entry) / entry) * 100 * leverage
        to_tp = ((take_profit - current_price) / current_price) * 100
        to_sl = ((current_price - stop_loss) / current_price) * 100
    else:
        pnl_pct = ((entry - current_price) / entry) * 100 * leverage
        to_tp = ((current_price - take_profit) / current_price) * 100
        to_sl = ((stop_loss - current_price) / current_price) * 100
    
    status = f"Position: {side} | P&L: {pnl_pct:+.2f}% | To TP: {to_tp:.2f}% | To SL: {to_sl:.2f}%"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {status}")
    
    return False  # Position still open


def main():
    """Main monitoring loop"""
    print("="*80)
    print("REAL-TIME PAPER POSITION MONITOR")
    print("="*80)
    print("Monitoring position every 60 seconds...")
    print("Will send Telegram alert immediately when TP/SL is hit")
    print("Press Ctrl+C to stop")
    print("="*80)
    print()
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  WARNING: Telegram credentials not set")
        print("   Alerts will not be sent")
        print()
    
    try:
        while True:
            position_closed = check_position_status()
            
            if position_closed:
                print("\n✅ Position closed. Monitor stopping.")
                print("   Paper trading script will update state at next 4h check.")
                break
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

