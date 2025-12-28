#!/usr/bin/env python3
"""
Quick script to check paper trading status
Run this anytime to see current positions and P&L
"""

import json
import requests
from datetime import datetime

PAPER_STATE_FILE = 'paper_state.json'
MEXC_API_BASE = "https://api.mexc.com/api/v3"

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

def main():
    """Display paper trading status"""
    try:
        with open(PAPER_STATE_FILE, 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        print("❌ Paper trading state file not found. Run paper trading first.")
        return
    except Exception as e:
        print(f"❌ Error reading state: {e}")
        return
    
    current_price = get_current_price()
    
    print("="*80)
    print("PAPER TRADING STATUS")
    print("="*80)
    print(f"Capital: ${state['capital']:,.2f}")
    print(f"Initial Capital: ${state.get('initial_capital', 1000):,.2f}")
    print(f"Total P&L: ${state['total_pnl']:,.2f} ({(state['capital'] / state.get('initial_capital', 1000) - 1) * 100:.2f}%)")
    print(f"Max Equity: ${state['max_equity']:,.2f}")
    drawdown = (state['capital'] - state['max_equity']) / state['max_equity'] * 100
    print(f"Drawdown: {drawdown:.2f}%")
    print()
    print(f"Total Trades: {state['total_trades']}")
    print(f"Winning Trades: {state['winning_trades']}")
    print(f"Losing Trades: {state['losing_trades']}")
    if state['total_trades'] > 0:
        win_rate = (state['winning_trades'] / state['total_trades']) * 100
        print(f"Win Rate: {win_rate:.1f}%")
    print()
    print(f"Open Positions: {len(state['open_positions'])}")
    print("="*80)
    
    if state['open_positions']:
        print()
        for i, pos in enumerate(state['open_positions'], 1):
            print(f"POSITION #{i}:")
            print(f"  Side: {pos['side']}")
            print(f"  Entry: ${pos['entry']:,.2f}")
            print(f"  Stop Loss: ${pos['stop_loss']:,.2f}")
            print(f"  Take Profit: ${pos['take_profit']:,.2f}")
            print(f"  Position Size: {pos['position_units']:.4f} BTC")
            print(f"  Leverage: {pos['leverage']}x")
            print(f"  Entry Time: {pos['entry_time']}")
            
            if current_price:
                if pos['side'] == 'LONG':
                    pnl_pct = ((current_price - pos['entry']) / pos['entry']) * 100 * pos['leverage']
                    to_tp = ((pos['take_profit'] - current_price) / current_price) * 100
                    to_sl = ((current_price - pos['stop_loss']) / current_price) * 100
                else:  # SHORT
                    pnl_pct = ((pos['entry'] - current_price) / pos['entry']) * 100 * pos['leverage']
                    to_tp = ((current_price - pos['take_profit']) / current_price) * 100
                    to_sl = ((pos['stop_loss'] - current_price) / current_price) * 100
                
                print(f"  Current Price: ${current_price:,.2f}")
                print(f"  Unrealized P&L: {pnl_pct:+.2f}%")
                print(f"  Distance to TP: {to_tp:.2f}%")
                print(f"  Distance to SL: {to_sl:.2f}%")
                
                # Status indicator
                if pnl_pct > 0:
                    print(f"  Status: 🟢 In Profit")
                elif pnl_pct < -5:
                    print(f"  Status: 🔴 At Risk")
                else:
                    print(f"  Status: 🟡 Neutral")
            else:
                print(f"  Current Price: Unable to fetch")
            print()
    
    print("="*80)
    print(f"Last Update: {state.get('last_update', 'Unknown')}")
    print("="*80)

if __name__ == "__main__":
    main()

