#!/usr/bin/env python3
"""
Triton73 Paper Trading Simulator
Simulates trading on MEXC without placing real orders
Tracks virtual positions and calculates P&L based on real market prices
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
import csv
import time

# Import from Triton73
from Triton73 import (
    MEXC_API_BASE, SYMBOL, INTERVAL, SESSION_CLOSE_HOUR_UTC,
    BREAKOUT_CONFIRMATION_PCT, SL_PCT, TP_MULTIPLIER,
    BASE_LEVERAGE, MIN_LEVERAGE, MAX_LEVERAGE, MIN_LEVEL_AGE_HOURS,
    RISK_PER_TRADE_PCT, CURRENT_CAPITAL,
    LEVEL_DECAY_24H, LEVEL_DECAY_72H, VOLUME_CONFIRMATION_MULTIPLIER,
    EMA_SHORT, EMA_LONG, DRAWDOWN_PAUSE_THRESHOLD, DRAWDOWN_RESUME_THRESHOLD,
    USE_SECOND_CONFIRMATION, STATE_FILE, TRADE_JOURNAL,
    fetch_mexc_klines, klines_to_df, calculate_atr, calculate_ema,
    calculate_dynamic_leverage, calculate_level_with_decay,
    check_trend_filter, check_volume_confirmation, check_breakout_enhanced,
    calculate_position_size, load_strategy_state, save_strategy_state,
    check_drawdown_pause, log_trade, send_telegram, fetch_funding_rate
)

# Paper Trading Files
PAPER_POSITIONS_FILE = 'paper_positions.json'
PAPER_TRADE_LOG = 'paper_trade_log.csv'
PAPER_STATE_FILE = 'paper_state.json'

# Paper Trading Settings
USE_PAPER_TRADING = True
PAPER_INITIAL_CAPITAL = float(os.environ.get('PAPER_CAPITAL', '1000.0'))


def load_paper_state():
    """Load paper trading state"""
    if os.path.exists(PAPER_STATE_FILE):
        try:
            with open(PAPER_STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    state = {
        'capital': PAPER_INITIAL_CAPITAL,
        'max_equity': PAPER_INITIAL_CAPITAL,
        'open_positions': [],
        'closed_trades': [],
        'total_trades': 0,
        'winning_trades': 0,
        'losing_trades': 0,
        'total_pnl': 0.0,
        'last_update': datetime.now().isoformat()
    }
    save_paper_state(state)
    return state


def save_paper_state(state):
    """Save paper trading state"""
    try:
        state['last_update'] = datetime.now().isoformat()
        with open(PAPER_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving paper state: {e}")


def get_current_price():
    """Get current BTCUSDT price from MEXC"""
    try:
        url = f"{MEXC_API_BASE}/ticker/price"
        params = {'symbol': SYMBOL}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"Error fetching current price: {e}")
        return None


def check_open_positions(paper_state, current_price):
    """Check if any open positions should be closed (TP or SL hit)"""
    if not paper_state['open_positions']:
        return paper_state
    
    updated_positions = []
    closed_trades = []
    
    for position in paper_state['open_positions']:
        entry = position['entry']
        stop_loss = position['stop_loss']
        take_profit = position['take_profit']
        side = position['side']
        position_units = position['position_units']
        leverage = position['leverage']
        entry_time = position['entry_time']
        
        should_close = False
        exit_price = None
        result = None
        reason = None
        
        if side == 'LONG':
            if current_price <= stop_loss:
                exit_price = stop_loss
                result = 'LOSS'
                reason = 'Stop Loss'
                should_close = True
            elif current_price >= take_profit:
                exit_price = take_profit
                result = 'WIN'
                reason = 'Take Profit'
                should_close = True
        else:  # SHORT
            if current_price >= stop_loss:
                exit_price = stop_loss
                result = 'LOSS'
                reason = 'Stop Loss'
                should_close = True
            elif current_price <= take_profit:
                exit_price = take_profit
                result = 'WIN'
                reason = 'Take Profit'
                should_close = True
        
        if should_close:
            # TRITON73: SLIPPAGE MODELING
            # Apply slippage to exit price (0.25% average slippage)
            slippage_pct = 0.0025  # 0.25% average slippage on MEXC
            if side == 'LONG':
                exit_price_with_slippage = exit_price * (1 - slippage_pct)  # Slippage reduces exit price for longs
            else:  # SHORT
                exit_price_with_slippage = exit_price * (1 + slippage_pct)  # Slippage increases exit price for shorts
            
            # Use slippage-adjusted exit price for P&L calculation
            exit_price = exit_price_with_slippage
            
            # Calculate P&L
            if side == 'LONG':
                pnl_amount = position_units * (exit_price - entry) * leverage
            else:
                pnl_amount = position_units * (entry - exit_price) * leverage
            
            # Apply fees (0.1% each way)
            fees = (position_units * entry + position_units * exit_price) * 0.001
            net_pnl = pnl_amount - fees
            
            # Update capital
            paper_state['capital'] += net_pnl
            paper_state['total_pnl'] += net_pnl
            
            # Update stats
            paper_state['total_trades'] += 1
            if result == 'WIN':
                paper_state['winning_trades'] += 1
            else:
                paper_state['losing_trades'] += 1
            
            # Create trade record
            trade = {
                'entry_time': entry_time,
                'exit_time': datetime.now().isoformat(),
                'side': side,
                'entry': entry,
                'exit': exit_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_units': position_units,
                'leverage': leverage,
                'pnl': net_pnl,
                'pnl_pct': (net_pnl / paper_state['capital']) * 100 if paper_state['capital'] > 0 else 0,
                'result': result,
                'reason': reason,
                'capital_after': paper_state['capital']
            }
            
            closed_trades.append(trade)
            paper_state['closed_trades'].append(trade)
            
            # Log trade
            log_trade({
                'timestamp': trade['exit_time'],
                'side': side,
                'level': position.get('level', 0),
                'entry': entry,
                'sl': stop_loss,
                'tp': take_profit,
                'result': result,
                'pnl': net_pnl,
                'pnl_pct': trade['pnl_pct'],
                'capital_after': paper_state['capital'],
                'leverage': leverage
            })
            
            print(f"\n📊 POSITION CLOSED: {result}")
            print(f"   Side: {side}")
            print(f"   Entry: ${entry:,.2f} → Exit: ${exit_price:,.2f}")
            print(f"   Reason: {reason}")
            print(f"   P&L: ${net_pnl:,.2f} ({trade['pnl_pct']:.2f}%)")
            print(f"   Capital: ${paper_state['capital']:,.2f}")
            
            # Send Telegram alert
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
   Percentage: {trade['pnl_pct']:+.2f}%

💵 Capital:
   Before: ${paper_state['capital'] - net_pnl:,.2f}
   After: ${paper_state['capital']:,.2f}

📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🔒 Strategy: Triton73 (3.5x base, 0.3% risk)
"""
            if send_telegram(message):
                print(f"   ✓ Telegram alert sent")
            else:
                print(f"   ⚠ Telegram not configured or failed")
        else:
            # Position still open
            updated_positions.append(position)
    
    paper_state['open_positions'] = updated_positions
    
    # Update max equity
    if paper_state['capital'] > paper_state['max_equity']:
        paper_state['max_equity'] = paper_state['capital']
    
    save_paper_state(paper_state)
    return paper_state


def open_paper_position(signal, position, leverage, paper_state):
    """Open a paper trading position (simulated)"""
    current_price = get_current_price()
    if not current_price:
        print("⚠️  Could not get current price, skipping position")
        return paper_state
    
    # TRITON73: SLIPPAGE MODELING
    # Apply slippage to entry price (0.25% average slippage on MEXC)
    slippage_pct = 0.0025  # 0.25% average slippage
    if signal['side'] == 'LONG':
        entry_with_slippage = signal['entry'] * (1 + slippage_pct)  # Slippage increases entry price for longs
    else:  # SHORT
        entry_with_slippage = signal['entry'] * (1 - slippage_pct)  # Slippage decreases entry price for shorts
    
    # Use slippage-adjusted entry price
    adjusted_entry = entry_with_slippage
    
    # Create position record
    paper_position = {
        'entry_time': datetime.now().isoformat(),
        'side': signal['side'],
        'entry': adjusted_entry,  # Use slippage-adjusted entry
        'stop_loss': signal['stop_loss'],
        'take_profit': signal['take_profit'],
        'position_units': position['position_units'],
        'leverage': leverage,
        'margin_required': position['margin_required'],
        'level': signal['level'],
        'current_price': current_price
    }
    
    paper_state['open_positions'].append(paper_position)
    save_paper_state(paper_state)
    
    print(f"\n✅ PAPER POSITION OPENED:")
    print(f"   Side: {signal['side']}")
    print(f"   Entry: ${signal['entry']:,.2f}")
    print(f"   Stop Loss: ${signal['stop_loss']:,.2f}")
    print(f"   Take Profit: ${signal['take_profit']:,.2f}")
    print(f"   Position Size: {position['position_units']:.4f} BTC")
    print(f"   Leverage: {leverage}x")
    print(f"   Margin: ${position['margin_required']:,.2f}")
    
    return paper_state


def print_paper_stats(paper_state):
    """Print paper trading statistics"""
    print("\n" + "="*80)
    print("PAPER TRADING STATISTICS")
    print("="*80)
    print(f"Initial Capital: ${PAPER_INITIAL_CAPITAL:,.2f}")
    print(f"Current Capital: ${paper_state['capital']:,.2f}")
    print(f"Total P&L: ${paper_state['total_pnl']:,.2f} ({(paper_state['capital'] / PAPER_INITIAL_CAPITAL - 1) * 100:.2f}%)")
    print(f"Max Equity: ${paper_state['max_equity']:,.2f}")
    print(f"Drawdown: ${(paper_state['capital'] - paper_state['max_equity']):,.2f} ({(paper_state['capital'] - paper_state['max_equity']) / paper_state['max_equity'] * 100:.2f}%)")
    print(f"\nTotal Trades: {paper_state['total_trades']}")
    print(f"Winning Trades: {paper_state['winning_trades']}")
    print(f"Losing Trades: {paper_state['losing_trades']}")
    if paper_state['total_trades'] > 0:
        win_rate = (paper_state['winning_trades'] / paper_state['total_trades']) * 100
        print(f"Win Rate: {win_rate:.2f}%")
    print(f"Open Positions: {len(paper_state['open_positions'])}")
    print("="*80)


def main():
    """Main paper trading loop"""
    print("="*80)
    print("TRITON73 PAPER TRADING SIMULATOR")
    print("="*80)
    print(f"Mode: Paper Trading (Virtual Positions)")
    print(f"Initial Capital: ${PAPER_INITIAL_CAPITAL:,.2f}")
    print(f"Strategy: Triton73 (3.5x base leverage, 0.3% risk)")
    print("="*80)
    
    # Load paper trading state
    paper_state = load_paper_state()
    
    # Check for open positions
    current_price = get_current_price()
    if current_price:
        paper_state = check_open_positions(paper_state, current_price)
    
    # Load strategy state (for signal generation)
    strategy_state = load_strategy_state()
    strategy_state['current_capital'] = paper_state['capital']  # Use paper capital
    
    if check_drawdown_pause(strategy_state):
        print("\n⚠️  STRATEGY IS PAUSED DUE TO DRAWDOWN")
        print_paper_stats(paper_state)
        return
    
    print(f"\nChecking {SYMBOL} for signals...")
    
    # Fetch data
    klines = fetch_mexc_klines(SYMBOL, INTERVAL)
    if not klines:
        print(f"  ⚠ No data for {SYMBOL}")
        print_paper_stats(paper_state)
        return
    
    df = klines_to_df(klines)
    if len(df) < 100:
        print(f"  ⚠ Insufficient data ({len(df)} candles)")
        print_paper_stats(paper_state)
        return
    
    # Calculate level with decay
    level = calculate_level_with_decay(df, len(df) - 1)
    if level is None:
        print(f"  ⚠ No valid level found")
        print_paper_stats(paper_state)
        return
    
    print(f"  Level: ${level['price']:,.2f} (age: {level['age_hours']:.1f}h)")
    
    # Check trend filter
    trend_filter = check_trend_filter(df)
    print(f"  Trend: {trend_filter['trend']} (LONG: {'✅' if trend_filter['long_allowed'] else '❌'}, SHORT: {'✅' if trend_filter['short_allowed'] else '❌'})")
    
    # Calculate dynamic leverage
    current_price = float(df.iloc[-1]['close'])
    leverage = calculate_dynamic_leverage(df, current_price)
    print(f"  Dynamic Leverage: {leverage}x (ATR-based)")
    
    # Check for breakout signal
    signal = check_breakout_enhanced(df, level, trend_filter, USE_SECOND_CONFIRMATION)
    
    if signal:
        # Check if we already have an open position
        if len(paper_state['open_positions']) > 0:
            print(f"  ⚠ Signal detected but position already open")
            print_paper_stats(paper_state)
            return
        
        # Fetch funding rate for position size adjustment
        funding_rate = fetch_funding_rate(SYMBOL)
        if funding_rate != 0:
            print(f"  Funding Rate: {funding_rate*100:.3f}% per 8h")
        
        # Calculate position size
        position = calculate_position_size(
            paper_state['capital'],
            signal['entry'],
            signal['stop_loss'],
            signal['side'],
            leverage,
            current_price=signal['current_price'],
            funding_rate=funding_rate  # Pass funding rate for adjustment
        )
        
        if position:
            # Open paper position
            paper_state = open_paper_position(signal, position, leverage, paper_state)
            
            # Send Telegram notification
            message = f"""
📊 PAPER TRADE OPENED - {SYMBOL} (TRITON73)

Side: {signal['side']}
Entry: ${signal['entry']:,.2f}
Stop Loss: ${signal['stop_loss']:,.2f}
Take Profit: ${signal['take_profit']:,.2f}

Position: {position['position_units']:.4f} BTC
Leverage: {leverage}x (Base: {BASE_LEVERAGE}x, Range: {MIN_LEVERAGE}x-{MAX_LEVERAGE}x)
Capital: ${paper_state['capital']:,.2f}
Risk: {RISK_PER_TRADE_PCT*100:.2f}% per trade
"""
            send_telegram(message)
        else:
            print(f"  ⚠ Could not calculate position size")
    else:
        print(f"  No signal")
    
    # Print statistics
    print_paper_stats(paper_state)


if __name__ == "__main__":
    main()

