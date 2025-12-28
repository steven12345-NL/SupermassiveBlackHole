#!/usr/bin/env python3
"""
MEXC BTCUSDT Perpetual Futures Trading Signals
Optimized for manual trading with original best settings
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

# MEXC API Configuration
MEXC_API_BASE = "https://api.mexc.com/api/v3"

# Telegram Configuration (optional)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# Strategy Parameters - ORIGINAL BEST SETTINGS
SYMBOL = 'BTCUSDT'  # ONLY BTCUSDT
INTERVAL = '4h'
SESSION_CLOSE_HOUR_UTC = 0
BREAKOUT_CONFIRMATION_PCT = 0.001  # 0.1%
SL_PCT = 0.004  # 0.4% (ORIGINAL BEST - DO NOT CHANGE)
TP_MULTIPLIER = 3.5  # 3.5:1 R:R
LEVERAGE = 3.0
MIN_LEVEL_AGE_HOURS = 6
RISK_PER_TRADE_PCT = 0.003  # 0.3% of capital per trade
USE_ATR_STOPS = False  # NO ATR (ORIGINAL BEST)
CURRENT_CAPITAL = float(os.environ.get('CURRENT_CAPITAL', '1000.0'))


def fetch_mexc_klines(symbol, interval, limit=500):
    """Fetch klines from MEXC"""
    try:
        interval_map = {
            '1h': '1h',
            '4h': '4h',
            '1d': '1d'
        }
        mexc_interval = interval_map.get(interval, '4h')
        
        url = f"{MEXC_API_BASE}/klines"
        params = {
            'symbol': symbol,
            'interval': mexc_interval,
            'limit': limit
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # MEXC returns: [openTime, open, high, low, close, volume, closeTime, ...]
        if data and len(data) > 0:
            formatted = []
            for k in data:
                formatted.append({
                    'open_time': k[0],
                    'open': k[1],
                    'high': k[2],
                    'low': k[3],
                    'close': k[4],
                    'volume': k[5],
                    'close_time': k[6]
                })
            return formatted
        
        return data
    except Exception as e:
        print(f"Error fetching {symbol} from MEXC: {e}")
        return None


def klines_to_df(klines):
    """Convert MEXC klines to DataFrame"""
    if not klines:
        return pd.DataFrame()
    
    df = pd.DataFrame(klines)
    
    # Convert types
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
    df = df.sort_values('open_time').reset_index(drop=True)
    
    return df


def calculate_level(df):
    """Calculate current level (session close price)"""
    df['hour_utc'] = df['open_time'].dt.hour
    session_closes = df[df['hour_utc'] == SESSION_CLOSE_HOUR_UTC]
    
    if len(session_closes) == 0:
        return None
    
    latest_session = session_closes.iloc[-1]
    level_price = float(latest_session['close'])
    level_time = latest_session['open_time']
    
    return {
        'price': level_price,
        'time': level_time,
        'age_hours': (pd.Timestamp.now(tz='UTC') - level_time).total_seconds() / 3600
    }


def check_breakout(df, level):
    """Check if price has broken through level"""
    if level is None or level['age_hours'] < MIN_LEVEL_AGE_HOURS:
        return None
    
    if len(df) < 2:
        return None
    
    prev_candle = df.iloc[-2]
    curr_candle = df.iloc[-1]
    
    prev_close = float(prev_candle['close'])
    curr_close = float(curr_candle['close'])
    curr_high = float(curr_candle['high'])
    curr_low = float(curr_candle['low'])
    level_price = level['price']
    
    signal = None
    
    # LONG breakout
    if prev_close <= level_price and curr_close > level_price:
        breakout_amount = (curr_close - level_price) / level_price
        if breakout_amount >= BREAKOUT_CONFIRMATION_PCT:
            if curr_high >= level_price * (1 + BREAKOUT_CONFIRMATION_PCT * 0.5):
                entry_price = level_price * (1 + BREAKOUT_CONFIRMATION_PCT * 0.5)
                # Original logic: max(Entry - Level, Entry × 0.4%)
                risk_from_level = entry_price - level_price
                risk_minimum = entry_price * SL_PCT
                risk_distance = max(risk_from_level, risk_minimum)
                
                sl_price = entry_price - risk_distance
                tp_price = entry_price + (risk_distance * TP_MULTIPLIER)
                
                signal = {
                    'side': 'LONG',
                    'entry': entry_price,
                    'stop_loss': sl_price,
                    'take_profit': tp_price,
                    'risk_pct': (risk_distance / entry_price) * 100,
                    'reward_pct': ((tp_price - entry_price) / entry_price) * 100,
                    'level': level_price,
                    'breakout': breakout_amount * 100,
                    'current_price': curr_close,
                    'entry_time': curr['open_time']
                }
    
    # SHORT breakout
    elif prev_close >= level_price and curr_close < level_price:
        breakout_amount = (level_price - curr_close) / level_price
        if breakout_amount >= BREAKOUT_CONFIRMATION_PCT:
            if curr_low <= level_price * (1 - BREAKOUT_CONFIRMATION_PCT * 0.5):
                entry_price = level_price * (1 - BREAKOUT_CONFIRMATION_PCT * 0.5)
                # Original logic: max(Level - Entry, Entry × 0.4%)
                risk_from_level = level_price - entry_price
                risk_minimum = entry_price * SL_PCT
                risk_distance = max(risk_from_level, risk_minimum)
                
                sl_price = entry_price + risk_distance
                tp_price = entry_price - (risk_distance * TP_MULTIPLIER)
                
                signal = {
                    'side': 'SHORT',
                    'entry': entry_price,
                    'stop_loss': sl_price,
                    'take_profit': tp_price,
                    'risk_pct': (risk_distance / entry_price) * 100,
                    'reward_pct': ((entry_price - tp_price) / entry_price) * 100,
                    'level': level_price,
                    'breakout': breakout_amount * 100,
                    'current_price': curr_close,
                    'entry_time': curr['open_time']
                }
    
    return signal


def calculate_position_size(current_capital, entry_price, stop_loss_price, side):
    """Calculate position size based on risk"""
    risk_amount = current_capital * RISK_PER_TRADE_PCT
    
    if side == 'LONG':
        price_risk = entry_price - stop_loss_price
    else:
        price_risk = stop_loss_price - entry_price
    
    if price_risk <= 0:
        return None
    
    position_units = risk_amount / price_risk
    position_value = position_units * entry_price
    margin_required = position_value / LEVERAGE
    
    if margin_required > current_capital:
        position_units = (current_capital * LEVERAGE) / entry_price
        position_value = position_units * entry_price
        margin_required = position_value / LEVERAGE
        risk_amount = (position_units * price_risk) / LEVERAGE
    
    return {
        'position_units': position_units,
        'position_value': position_value,
        'margin_required': margin_required,
        'risk_amount': risk_amount
    }


def format_signal(symbol, signal, position, current_capital):
    """Format trading signal for display"""
    side_emoji = "🟢" if signal['side'] == 'LONG' else "🔴"
    
    message = f"""
{'='*80}
{side_emoji} {signal['side']} SIGNAL - {symbol}
{'='*80}

📊 PRICES:
   Entry:      ${signal['entry']:,.2f}
   Stop Loss:  ${signal['stop_loss']:,.2f}
   Take Profit: ${signal['take_profit']:,.2f}
   Current:    ${signal['current_price']:,.2f}

💰 POSITION (3x Leverage):
   Quantity:   {position['position_units']:,.4f} BTC
   Value:      €{position['position_value']:,.2f}
   Margin:     €{position['margin_required']:,.2f}

⚖️ RISK/REWARD:
   Risk:       {signal['risk_pct']:.2f}% (€{position['risk_amount']:,.2f})
   Reward:     {signal['reward_pct']:.2f}%
   R:R Ratio:  {TP_MULTIPLIER:.1f}:1

📈 SIGNAL DETAILS:
   Level:      ${signal['level']:,.2f}
   Breakout:   {signal['breakout']:.3f}%
   Capital:    €{current_capital:,.2f}

{'='*80}

✅ MANUAL TRADING INSTRUCTIONS:
1. Go to MEXC → Futures → BTCUSDT Perpetual
2. Set Leverage: 3x
3. Enter {signal['side']} position at: ${signal['entry']:,.2f}
4. Set Stop Loss at: ${signal['stop_loss']:,.2f}
5. Set Take Profit at: ${signal['take_profit']:,.2f}
6. Position Size: {position['position_units']:,.4f} BTC

⚠️ IMPORTANT:
- Use LIMIT orders for entry (not market)
- Set SL/TP immediately after entry
- Risk per trade: €{position['risk_amount']:,.2f} (0.3% of capital)
"""
    return message.strip()


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


def main():
    """Main trading signal generator"""
    print("="*80)
    print("MEXC BTCUSDT PERPETUAL FUTURES - TRADING SIGNALS")
    print("="*80)
    print(f"Strategy: Breakout with {LEVERAGE}x leverage")
    print(f"Interval: {INTERVAL}")
    print(f"Stop Loss: {SL_PCT*100:.2f}% (ORIGINAL BEST)")
    print(f"Take Profit: {TP_MULTIPLIER:.1f}:1 R:R")
    print(f"ATR-Based Stops: {'ON' if USE_ATR_STOPS else 'OFF'}")
    print(f"Capital: €{CURRENT_CAPITAL:,.2f}")
    print("="*80)
    
    print(f"\nChecking {SYMBOL}...")
    
    # Fetch data
    klines = fetch_mexc_klines(SYMBOL, INTERVAL)
    if not klines:
        print(f"  ⚠ No data for {SYMBOL}")
        return
    
    df = klines_to_df(klines)
    if len(df) < 100:
        print(f"  ⚠ Insufficient data ({len(df)} candles)")
        return
    
    # Calculate level
    level = calculate_level(df)
    if level is None:
        print(f"  ⚠ No level found")
        return
    
    print(f"  Level: ${level['price']:,.2f} (age: {level['age_hours']:.1f}h)")
    
    # Check for breakout
    signal = check_breakout(df, level)
    
    if signal:
        current_price = float(df.iloc[-1]['close'])
        position = calculate_position_size(CURRENT_CAPITAL, signal['entry'], signal['stop_loss'], signal['side'])
        
        if position:
            message = format_signal(SYMBOL, signal, position, CURRENT_CAPITAL)
            print(message)
            
            # Save position info for position monitor
            position_info = {
                'symbol': SYMBOL,
                'side': signal['side'],
                'entry': signal['entry'],
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'entry_time': signal['entry_time'].isoformat() if hasattr(signal['entry_time'], 'isoformat') else str(signal['entry_time']),
                'level': signal['level'],
                'position_units': position['units'],
                'position_value': position['value'],
                'margin_required': position['margin']
            }
            try:
                with open('current_position.json', 'w') as f:
                    json.dump(position_info, f, indent=2, default=str)
                print(f"\n  ✓ Position saved for monitoring")
            except Exception as e:
                print(f"\n  ⚠ Could not save position: {e}")
            
            # Send to Telegram
            if send_telegram(message):
                print(f"\n  ✓ Sent to Telegram")
            else:
                print(f"\n  ⚠ Telegram not configured or failed")
        else:
            print(f"  ⚠ Could not calculate position size")
    else:
        print(f"  No signal (level age: {level['age_hours']:.1f}h, min: {MIN_LEVEL_AGE_HOURS}h)")
        print(f"  Current price: ${df.iloc[-1]['close']:,.2f}")
        print(f"  Level: ${level['price']:,.2f}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()



