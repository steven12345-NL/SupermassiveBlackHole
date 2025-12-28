#!/usr/bin/env python3
"""
Triton73 Backtest
Backtests the complete Triton73 strategy with all enhancements:
- Funding rate adjustment
- Slippage modeling
- All 10 enhanced features
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Import all Triton73 functions
from Triton73 import (
    MEXC_API_BASE, SYMBOL, INTERVAL, SESSION_CLOSE_HOUR_UTC,
    BREAKOUT_CONFIRMATION_PCT, SL_PCT, TP_MULTIPLIER,
    BASE_LEVERAGE, MIN_LEVERAGE, MAX_LEVERAGE, MIN_LEVEL_AGE_HOURS,
    RISK_PER_TRADE_PCT,
    LEVEL_DECAY_24H, LEVEL_DECAY_72H, VOLUME_CONFIRMATION_MULTIPLIER,
    EMA_SHORT, EMA_LONG, DRAWDOWN_PAUSE_THRESHOLD, DRAWDOWN_RESUME_THRESHOLD,
    USE_SECOND_CONFIRMATION,
    fetch_mexc_klines, klines_to_df, calculate_atr, calculate_ema,
    calculate_dynamic_leverage, calculate_level_with_decay,
    check_trend_filter, check_volume_confirmation, check_breakout_enhanced,
    calculate_position_size, fetch_funding_rate
)

# Backtest Parameters
INITIAL_CAPITAL = 1000.0
SLIPPAGE_PCT = 0.0025  # 0.25% slippage
FEE_PCT = 0.001  # 0.1% per trade (0.1% entry + 0.1% exit = 0.2% total)


def fetch_historical_funding_rates(symbol, start_time, end_time):
    """Estimate funding rates for historical period (simplified)"""
    # In real backtest, you'd fetch historical funding rates
    # For now, we'll use a simplified model: average 0.01% per 8h
    # This is a conservative estimate
    return 0.0001  # 0.01% per 8h average


def backtest_triton73(start_date, end_date, initial_capital=INITIAL_CAPITAL):
    """Backtest Triton73 strategy"""
    print("="*80)
    print("TRITON73 BACKTEST")
    print("="*80)
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Strategy: Triton73 with all enhancements")
    print("="*80)
    print()
    
    # Fetch historical data
    print("📊 Fetching historical data...")
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
    
    # Fetch all klines (MEXC has limited history, so we'll use what's available)
    all_klines = []
    limit = 1000
    current_time = start_timestamp
    
    while current_time < end_timestamp:
        try:
            url = f"{MEXC_API_BASE}/klines"
            params = {
                'symbol': SYMBOL,
                'interval': INTERVAL,
                'limit': limit,
                'startTime': current_time
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            all_klines.extend(data)
            current_time = data[-1][0] + 1  # Next start time
            
            if len(data) < limit:
                break
        except Exception as e:
            print(f"⚠️  Error fetching data: {e}")
            break
    
    if not all_klines:
        print("❌ No data fetched")
        return None
    
    # Convert to DataFrame
    df = klines_to_df(all_klines)
    df = df[df['open_time'] >= pd.Timestamp(start_date)]
    df = df[df['open_time'] <= pd.Timestamp(end_date)]
    
    if len(df) < 100:
        print(f"⚠️  Insufficient data: {len(df)} candles")
        return None
    
    print(f"✅ Loaded {len(df)} candles")
    print()
    
    # Initialize backtest state
    capital = initial_capital
    max_equity = initial_capital
    current_position = None
    trades = []
    paused = False
    
    # Track metrics
    total_trades = 0
    winning_trades = 0
    losing_trades = 0
    total_pnl = 0.0
    
    print("🔄 Running backtest...")
    print()
    
    # Iterate through candles
    for i in range(100, len(df)):  # Start from 100 to have enough history
        current_candle = df.iloc[i]
        current_price = float(current_candle['close'])
        current_time = current_candle['open_time']
        
        # Check drawdown pause
        if capital > max_equity:
            max_equity = capital
        
        drawdown = (capital - max_equity) / max_equity if max_equity > 0 else 0
        if drawdown <= -DRAWDOWN_PAUSE_THRESHOLD:
            if not paused:
                print(f"⏸️  Strategy paused at {drawdown*100:.2f}% drawdown (candle {i})")
                paused = True
        elif paused and capital >= max_equity * DRAWDOWN_RESUME_THRESHOLD:
            print(f"▶️  Strategy resumed (candle {i})")
            paused = False
        
        if paused:
            # Skip trading if paused
            if current_position:
                # Still check for exits
                entry = current_position['entry']
                stop_loss = current_position['stop_loss']
                take_profit = current_position['take_profit']
                side = current_position['side']
                
                should_close = False
                exit_price = None
                result = None
                
                if side == 'LONG':
                    if current_price <= stop_loss:
                        exit_price = stop_loss
                        result = 'LOSS'
                        should_close = True
                    elif current_price >= take_profit:
                        exit_price = take_profit
                        result = 'WIN'
                        should_close = True
                else:  # SHORT
                    if current_price >= stop_loss:
                        exit_price = stop_loss
                        result = 'LOSS'
                        should_close = True
                    elif current_price <= take_profit:
                        exit_price = take_profit
                        result = 'WIN'
                        should_close = True
                
                if should_close:
                    # Apply slippage
                    if side == 'LONG':
                        exit_price *= (1 - SLIPPAGE_PCT)
                    else:
                        exit_price *= (1 + SLIPPAGE_PCT)
                    
                    # Calculate P&L
                    position_units = current_position['position_units']
                    leverage = current_position['leverage']
                    
                    if side == 'LONG':
                        pnl_amount = position_units * (exit_price - entry) * leverage
                    else:
                        pnl_amount = position_units * (entry - exit_price) * leverage
                    
                    # Apply fees
                    fees = (position_units * entry + position_units * exit_price) * FEE_PCT
                    net_pnl = pnl_amount - fees
                    
                    capital += net_pnl
                    total_pnl += net_pnl
                    total_trades += 1
                    
                    if result == 'WIN':
                        winning_trades += 1
                    else:
                        losing_trades += 1
                    
                    trades.append({
                        'entry_time': current_position['entry_time'],
                        'exit_time': current_time,
                        'side': side,
                        'entry': entry,
                        'exit': exit_price,
                        'result': result,
                        'pnl': net_pnl,
                        'capital_after': capital,
                        'leverage': leverage
                    })
                    
                    current_position = None
            continue
        
        # Check for position exit
        if current_position:
            entry = current_position['entry']
            stop_loss = current_position['stop_loss']
            take_profit = current_position['take_profit']
            side = current_position['side']
            
            should_close = False
            exit_price = None
            result = None
            
            if side == 'LONG':
                if current_price <= stop_loss:
                    exit_price = stop_loss
                    result = 'LOSS'
                    should_close = True
                elif current_price >= take_profit:
                    exit_price = take_profit
                    result = 'WIN'
                    should_close = True
            else:  # SHORT
                if current_price >= stop_loss:
                    exit_price = stop_loss
                    result = 'LOSS'
                    should_close = True
                elif current_price <= take_profit:
                    exit_price = take_profit
                    result = 'WIN'
                    should_close = True
            
            if should_close:
                # Apply slippage
                if side == 'LONG':
                    exit_price *= (1 - SLIPPAGE_PCT)
                else:
                    exit_price *= (1 + SLIPPAGE_PCT)
                
                # Calculate P&L
                position_units = current_position['position_units']
                leverage = current_position['leverage']
                
                if side == 'LONG':
                    pnl_amount = position_units * (exit_price - entry) * leverage
                else:
                    pnl_amount = position_units * (entry - exit_price) * leverage
                
                # Apply fees
                fees = (position_units * entry + position_units * exit_price) * FEE_PCT
                net_pnl = pnl_amount - fees
                
                capital += net_pnl
                total_pnl += net_pnl
                total_trades += 1
                
                if result == 'WIN':
                    winning_trades += 1
                else:
                    losing_trades += 1
                
                trades.append({
                    'entry_time': current_position['entry_time'],
                    'exit_time': current_time,
                    'side': side,
                    'entry': entry,
                    'exit': exit_price,
                    'result': result,
                    'pnl': net_pnl,
                    'capital_after': capital,
                    'leverage': leverage
                })
                
                current_position = None
                continue
        
        # Check for new signal (only on candle close, and need enough history)
        if i < len(df) - 1:  # Don't check on last candle
            # Calculate level with decay
            level = calculate_level_with_decay(df, i)
            if level is None:
                continue
            
            # Check level age
            if level['age_hours'] < MIN_LEVEL_AGE_HOURS:
                continue
            
            # Check trend filter
            trend_filter = check_trend_filter(df.iloc[:i+1])
            if not trend_filter['long_allowed'] and not trend_filter['short_allowed']:
                continue
            
            # Calculate dynamic leverage
            leverage = calculate_dynamic_leverage(df.iloc[:i+1], current_price)
            
            # Check for breakout
            signal = check_breakout_enhanced(df.iloc[:i+1], level, trend_filter, USE_SECOND_CONFIRMATION)
            
            if signal:
                # Estimate funding rate (simplified for backtest)
                funding_rate = fetch_historical_funding_rates(SYMBOL, start_date, end_date)
                
                # Calculate position size
                position = calculate_position_size(
                    capital,
                    signal['entry'],
                    signal['stop_loss'],
                    signal['side'],
                    leverage,
                    current_price=current_price,
                    funding_rate=funding_rate
                )
                
                if position:
                    # Apply slippage to entry
                    entry_with_slippage = signal['entry']
                    if signal['side'] == 'LONG':
                        entry_with_slippage *= (1 + SLIPPAGE_PCT)
                    else:
                        entry_with_slippage *= (1 - SLIPPAGE_PCT)
                    
                    # Open position
                    current_position = {
                        'entry_time': current_time,
                        'side': signal['side'],
                        'entry': entry_with_slippage,
                        'stop_loss': signal['stop_loss'],
                        'take_profit': signal['take_profit'],
                        'position_units': position['position_units'],
                        'leverage': leverage
                    }
    
    # Final results
    final_return = ((capital / initial_capital) - 1) * 100
    max_drawdown = ((capital - max_equity) / max_equity) * 100 if max_equity > 0 else 0
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate profit factor
    wins = [t for t in trades if t['result'] == 'WIN']
    losses = [t for t in trades if t['result'] == 'LOSS']
    total_wins = sum(t['pnl'] for t in wins) if wins else 0
    total_losses = abs(sum(t['pnl'] for t in losses)) if losses else 0
    profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
    
    # Calculate average R:R
    avg_rr = 0
    if wins and losses:
        avg_win = sum(t['pnl'] for t in wins) / len(wins)
        avg_loss = abs(sum(t['pnl'] for t in losses) / len(losses))
        avg_rr = avg_win / avg_loss if avg_loss > 0 else 0
    
    # Print results
    print("="*80)
    print("BACKTEST RESULTS")
    print("="*80)
    print(f"Period: {start_date} to {end_date}")
    print(f"Candles Analyzed: {len(df)}")
    print()
    print("💰 PERFORMANCE")
    print("-"*80)
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Capital: ${capital:,.2f}")
    print(f"Total P&L: ${total_pnl:+,.2f}")
    print(f"Return: {final_return:+.2f}%")
    print(f"Max Equity: ${max_equity:,.2f}")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print()
    print("📊 TRADE STATISTICS")
    print("-"*80)
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Average R:R: {avg_rr:.2f}:1")
    print()
    
    if trades:
        print("📈 RECENT TRADES (Last 10)")
        print("-"*80)
        for i, trade in enumerate(reversed(trades[-10:]), 1):
            result_emoji = "✅" if trade['result'] == 'WIN' else "❌"
            print(f"{i}. {result_emoji} {trade['side']} | Entry: ${trade['entry']:,.2f} | Exit: ${trade['exit']:,.2f} | P&L: ${trade['pnl']:+,.2f}")
    print()
    print("="*80)
    
    return {
        'initial_capital': initial_capital,
        'final_capital': capital,
        'total_pnl': total_pnl,
        'return_pct': final_return,
        'max_equity': max_equity,
        'max_drawdown': max_drawdown,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'avg_rr': avg_rr,
        'trades': trades
    }


if __name__ == "__main__":
    # Backtest for recent period (MEXC has limited history)
    # Try to get last 6 months of data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    print("Starting Triton73 backtest...")
    print(f"Note: MEXC has limited historical data. Using available period.")
    print()
    
    results = backtest_triton73(start_date, end_date, INITIAL_CAPITAL)
    
    if results:
        # Save results
        with open('triton73_backtest_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n✅ Results saved to triton73_backtest_results.json")

