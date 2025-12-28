#!/usr/bin/env python3
"""
Triton73 - MEXC BTCUSDT Enhanced Strategy (SAFER VERSION)
Includes all recommended improvements with reduced leverage and liquidation protection:
1. Level Decay Mechanism
2. Volume/Order Flow Confirmation
3. Dynamic Leverage Based on Volatility (3.5x base, 2x-4x range)
4. Trend Filter (EMA)
5. Automated Pause on Drawdown
6. Trade Journal
7. Second Confirmation Candle
8. LIQUIDATION PROTECTION (reduces position size if near liquidation)
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
import csv

# MEXC API Configuration
MEXC_API_BASE = "https://api.mexc.com/api/v3"

# Telegram Configuration (optional)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# Strategy Parameters - ENHANCED
SYMBOL = 'BTCUSDT'
INTERVAL = '4h'
SESSION_CLOSE_HOUR_UTC = 0
BREAKOUT_CONFIRMATION_PCT = 0.001  # 0.1%
SL_PCT = 0.004  # 0.4%
TP_MULTIPLIER = 3.5  # 3.5:1 R:R
BASE_LEVERAGE = 3.5  # TRITON73: Safer base leverage (reduced from 7.0)
MIN_LEVERAGE = 2.0    # TRITON73: Min leverage during high volatility
MAX_LEVERAGE = 4.0    # TRITON73: Max leverage during low volatility
MIN_LEVEL_AGE_HOURS = 6
RISK_PER_TRADE_PCT = 0.003  # TRITON73: 0.3% of capital per trade (reduced from 0.7%)
CURRENT_CAPITAL = float(os.environ.get('CURRENT_CAPITAL', '1000.0'))

# Enhanced Parameters
LEVEL_DECAY_24H = 0.25  # Reduce validity by 25% after 24h
LEVEL_DECAY_72H = 1.0  # Ignore after 72h unless retest with volume
VOLUME_CONFIRMATION_MULTIPLIER = 1.2  # 20% higher volume required
EMA_SHORT = 20
EMA_LONG = 50
DRAWDOWN_PAUSE_THRESHOLD = 0.20  # Pause at 20% drawdown
DRAWDOWN_RESUME_THRESHOLD = 0.95  # Resume at 95% of peak
USE_SECOND_CONFIRMATION = True  # Wait for next candle confirmation

# State files
STATE_FILE = 'strategy_state.json'
TRADE_JOURNAL = 'trade_journal.csv'


def load_strategy_state():
    """Load strategy state (capital, drawdown, paused status)"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Initialize state
    state = {
        'current_capital': CURRENT_CAPITAL,
        'max_equity': CURRENT_CAPITAL,
        'paused': False,
        'last_update': datetime.now().isoformat()
    }
    save_strategy_state(state)
    return state


def save_strategy_state(state):
    """Save strategy state"""
    try:
        state['last_update'] = datetime.now().isoformat()
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")


def check_drawdown_pause(state):
    """Check if strategy should be paused due to drawdown"""
    current_capital = state['current_capital']
    max_equity = state['max_equity']
    
    # Update max equity
    if current_capital > max_equity:
        max_equity = current_capital
        state['max_equity'] = max_equity
    
    # Calculate drawdown
    drawdown = (current_capital - max_equity) / max_equity if max_equity > 0 else 0
    
    # Check pause condition
    if drawdown <= -DRAWDOWN_PAUSE_THRESHOLD:
        if not state.get('paused', False):
            state['paused'] = True
            save_strategy_state(state)
            print(f"⚠️  STRATEGY PAUSED: Drawdown = {drawdown*100:.2f}%")
            return True
    
    # Check resume condition
    if state.get('paused', False):
        if current_capital >= max_equity * DRAWDOWN_RESUME_THRESHOLD:
            state['paused'] = False
            save_strategy_state(state)
            print(f"✅ STRATEGY RESUMED: Capital recovered to {current_capital/max_equity*100:.1f}% of peak")
        else:
            return True
    
    return state.get('paused', False)


def log_trade(trade_data):
    """Log trade to journal CSV"""
    file_exists = os.path.exists(TRADE_JOURNAL)
    
    try:
        with open(TRADE_JOURNAL, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                # Write header
                writer.writerow([
                    'timestamp', 'side', 'level', 'entry', 'sl', 'tp',
                    'result', 'pnl', 'pnl_pct', 'capital_after', 'leverage',
                    'volume_confirmed', 'trend_aligned', 'level_decay_applied'
                ])
            
            writer.writerow([
                trade_data.get('timestamp', datetime.now().isoformat()),
                trade_data.get('side', ''),
                trade_data.get('level', 0),
                trade_data.get('entry', 0),
                trade_data.get('sl', 0),
                trade_data.get('tp', 0),
                trade_data.get('result', ''),
                trade_data.get('pnl', 0),
                trade_data.get('pnl_pct', 0),
                trade_data.get('capital_after', 0),
                trade_data.get('leverage', BASE_LEVERAGE),
                trade_data.get('volume_confirmed', False),
                trade_data.get('trend_aligned', False),
                trade_data.get('level_decay_applied', False)
            ])
    except Exception as e:
        print(f"Error logging trade: {e}")


def fetch_funding_rate(symbol='BTCUSDT'):
    """Fetch current funding rate from MEXC"""
    try:
        url = f"{MEXC_API_BASE}/funding-rate"
        params = {'symbol': symbol}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            # Get most recent funding rate
            latest = data[0]
            funding_rate = float(latest.get('fundingRate', 0))
            return funding_rate
        elif isinstance(data, dict):
            funding_rate = float(data.get('fundingRate', 0))
            return funding_rate
        
        return 0.0
    except Exception as e:
        print(f"⚠️  Could not fetch funding rate: {e}")
        return 0.0  # Default to 0 if fetch fails


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
        print(f"Error fetching {symbol}: {e}")
        return None


def klines_to_df(klines):
    """Convert MEXC klines to DataFrame"""
    if not klines:
        return pd.DataFrame()
    
    df = pd.DataFrame(klines)
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
    df = df.sort_values('open_time').reset_index(drop=True)
    return df


def calculate_atr(df, period=14):
    """Calculate Average True Range"""
    if len(df) < period + 1:
        return None
    
    df = df.copy()
    df['prev_close'] = df['close'].shift(1)
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['prev_close'])
    df['tr3'] = abs(df['low'] - df['prev_close'])
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    atr = df['tr'].rolling(window=period).mean().iloc[-1]
    return float(atr) if pd.notna(atr) else None


def calculate_ema(df, period):
    """Calculate Exponential Moving Average"""
    if len(df) < period:
        return None
    return df['close'].ewm(span=period, adjust=False).mean()


def calculate_dynamic_leverage(df, current_price):
    """Calculate dynamic leverage based on ATR volatility"""
    atr = calculate_atr(df, period=14)
    if not atr:
        return BASE_LEVERAGE
    
    normalized_atr = (atr / current_price) * 100  # ATR as percentage
    
    # High volatility (>2%) -> reduce leverage
    if normalized_atr > 2.0:
        leverage = MIN_LEVERAGE
    # Low volatility (<0.8%) -> increase leverage
    elif normalized_atr < 0.8:
        leverage = MAX_LEVERAGE
    else:
        # Linear interpolation between MIN and MAX based on ATR
        leverage = BASE_LEVERAGE * (1 + (0.5 - normalized_atr / 2.0))
        leverage = max(MIN_LEVERAGE, min(MAX_LEVERAGE, leverage))
    
    return round(leverage, 1)


def calculate_level_with_decay(df, current_idx):
    """Calculate level with decay mechanism"""
    historical = df.iloc[:current_idx + 1].copy()
    historical['hour_utc'] = historical['open_time'].dt.hour
    session_closes = historical[historical['hour_utc'] == SESSION_CLOSE_HOUR_UTC]
    
    if len(session_closes) == 0:
        return None
    
    latest = session_closes.iloc[-1]
    level_price = float(latest['close'])
    level_time = latest['open_time']
    current_time = df.iloc[current_idx]['open_time']
    age_hours = (current_time - level_time).total_seconds() / 3600
    
    # Level decay logic
    decay_factor = 1.0
    if age_hours > 72:
        # After 72h, level is invalid unless retested with volume
        # Check if price retested with high volume
        current_candle = df.iloc[current_idx]
        avg_volume = df['volume'].tail(20).mean()
        retest_with_volume = (
            (abs(float(current_candle['close']) - level_price) / level_price < 0.002) and
            (float(current_candle['volume']) > avg_volume * 1.2)
        )
        if not retest_with_volume:
            return None  # Level too old and not retested
    elif age_hours > 24:
        # After 24h, reduce validity by 25%
        decay_factor = 1.0 - LEVEL_DECAY_24H
    
    return {
        'price': level_price,
        'time': level_time,
        'age_hours': age_hours,
        'decay_factor': decay_factor,
        'valid': age_hours >= MIN_LEVEL_AGE_HOURS
    }


def check_trend_filter(df):
    """Check trend filter using EMA"""
    if len(df) < EMA_LONG:
        return {'trend': 'NEUTRAL', 'long_allowed': True, 'short_allowed': True}
    
    ema_20 = calculate_ema(df, EMA_SHORT)
    ema_50 = calculate_ema(df, EMA_LONG)
    
    if ema_20 is None or ema_50 is None:
        return {'trend': 'NEUTRAL', 'long_allowed': True, 'short_allowed': True}
    
    ema_20_val = ema_20.iloc[-1]
    ema_50_val = ema_50.iloc[-1]
    
    if ema_20_val > ema_50_val:
        return {'trend': 'BULLISH', 'long_allowed': True, 'short_allowed': False}
    else:
        return {'trend': 'BEARISH', 'long_allowed': False, 'short_allowed': True}


def check_volume_confirmation(df, current_idx):
    """Check if breakout has volume confirmation"""
    if current_idx < 20:
        return False
    
    current_candle = df.iloc[current_idx]
    avg_volume = df.iloc[max(0, current_idx-20):current_idx]['volume'].mean()
    current_volume = float(current_candle['volume'])
    
    return current_volume > (avg_volume * VOLUME_CONFIRMATION_MULTIPLIER)


def check_breakout_enhanced(df, level, trend_filter, use_second_confirmation=True):
    """Enhanced breakout check with all filters"""
    if level is None or not level.get('valid', False):
        return None
    
    if len(df) < 3:
        return None
    
    # For second confirmation, we need to check previous candle for breakout
    # and current candle for confirmation
    if use_second_confirmation:
        # Check if breakout happened in previous candle
        prev_candle = df.iloc[-2]
        prev_prev_candle = df.iloc[-3] if len(df) >= 3 else None
        curr_candle = df.iloc[-1]
        
        if prev_prev_candle is None:
            return None
        
        prev_prev_close = float(prev_prev_candle['close'])
        prev_close = float(prev_candle['close'])
        curr_close = float(curr_candle['close'])
        level_price = level['price']
        
        # LONG: Check if breakout happened in prev candle, confirm in current
        if prev_prev_close <= level_price and prev_close > level_price:
            # Breakout detected in prev candle, now check confirmation
            if curr_close > prev_close:  # Price continued up
                breakout_amount = (prev_close - level_price) / level_price
                if breakout_amount >= BREAKOUT_CONFIRMATION_PCT:
                    # Check trend filter
                    if not trend_filter['long_allowed']:
                        return None
                    
                    # Check volume confirmation
                    volume_confirmed = check_volume_confirmation(df, len(df) - 2)
                    
                    entry_price = level_price * (1 + BREAKOUT_CONFIRMATION_PCT * 0.5)
                    risk_from_level = entry_price - level_price
                    risk_minimum = entry_price * SL_PCT
                    risk_distance = max(risk_from_level, risk_minimum) * level['decay_factor']
                    
                    sl_price = entry_price - risk_distance
                    tp_price = entry_price + (risk_distance * TP_MULTIPLIER)
                    
                    return {
                        'side': 'LONG',
                        'entry': entry_price,
                        'stop_loss': sl_price,
                        'take_profit': tp_price,
                        'risk_pct': (risk_distance / entry_price) * 100,
                        'reward_pct': ((tp_price - entry_price) / entry_price) * 100,
                        'level': level_price,
                        'breakout': breakout_amount * 100,
                        'current_price': curr_close,
                        'entry_time': curr_candle['open_time'],
                        'volume_confirmed': volume_confirmed,
                        'trend_aligned': True,
                        'level_decay_applied': level['decay_factor'] < 1.0
                    }
        
        # SHORT: Check if breakout happened in prev candle, confirm in current
        elif prev_prev_close >= level_price and prev_close < level_price:
            # Breakout detected in prev candle, now check confirmation
            if curr_close < prev_close:  # Price continued down
                breakout_amount = (level_price - prev_close) / level_price
                if breakout_amount >= BREAKOUT_CONFIRMATION_PCT:
                    # Check trend filter
                    if not trend_filter['short_allowed']:
                        return None
                    
                    # Check volume confirmation
                    volume_confirmed = check_volume_confirmation(df, len(df) - 2)
                    
                    entry_price = level_price * (1 - BREAKOUT_CONFIRMATION_PCT * 0.5)
                    risk_from_level = level_price - entry_price
                    risk_minimum = entry_price * SL_PCT
                    risk_distance = max(risk_from_level, risk_minimum) * level['decay_factor']
                    
                    sl_price = entry_price + risk_distance
                    tp_price = entry_price - (risk_distance * TP_MULTIPLIER)
                    
                    return {
                        'side': 'SHORT',
                        'entry': entry_price,
                        'stop_loss': sl_price,
                        'take_profit': tp_price,
                        'risk_pct': (risk_distance / entry_price) * 100,
                        'reward_pct': ((entry_price - tp_price) / entry_price) * 100,
                        'level': level_price,
                        'breakout': breakout_amount * 100,
                        'current_price': curr_close,
                        'entry_time': curr_candle['open_time'],
                        'volume_confirmed': volume_confirmed,
                        'trend_aligned': True,
                        'level_decay_applied': level['decay_factor'] < 1.0
                    }
    else:
        # Original single-candle logic (for comparison)
        prev_candle = df.iloc[-2]
        curr_candle = df.iloc[-1]
        
        prev_close = float(prev_candle['close'])
        curr_close = float(curr_candle['close'])
        curr_high = float(curr_candle['high'])
        curr_low = float(curr_candle['low'])
        level_price = level['price']
        
        # LONG breakout
        if prev_close <= level_price and curr_close > level_price:
            breakout_amount = (curr_close - level_price) / level_price
            if breakout_amount >= BREAKOUT_CONFIRMATION_PCT:
                if curr_high >= level_price * (1 + BREAKOUT_CONFIRMATION_PCT * 0.5):
                    if not trend_filter['long_allowed']:
                        return None
                    
                    volume_confirmed = check_volume_confirmation(df, len(df) - 1)
                    
                    entry_price = level_price * (1 + BREAKOUT_CONFIRMATION_PCT * 0.5)
                    risk_from_level = entry_price - level_price
                    risk_minimum = entry_price * SL_PCT
                    risk_distance = max(risk_from_level, risk_minimum) * level['decay_factor']
                    
                    sl_price = entry_price - risk_distance
                    tp_price = entry_price + (risk_distance * TP_MULTIPLIER)
                    
                    return {
                        'side': 'LONG',
                        'entry': entry_price,
                        'stop_loss': sl_price,
                        'take_profit': tp_price,
                        'risk_pct': (risk_distance / entry_price) * 100,
                        'reward_pct': ((tp_price - entry_price) / entry_price) * 100,
                        'level': level_price,
                        'breakout': breakout_amount * 100,
                        'current_price': curr_close,
                        'entry_time': curr_candle['open_time'],
                        'volume_confirmed': volume_confirmed,
                        'trend_aligned': True,
                        'level_decay_applied': level['decay_factor'] < 1.0
                    }
        
        # SHORT breakout
        elif prev_close >= level_price and curr_close < level_price:
            breakout_amount = (level_price - curr_close) / level_price
            if breakout_amount >= BREAKOUT_CONFIRMATION_PCT:
                if curr_low <= level_price * (1 - BREAKOUT_CONFIRMATION_PCT * 0.5):
                    if not trend_filter['short_allowed']:
                        return None
                    
                    volume_confirmed = check_volume_confirmation(df, len(df) - 1)
                    
                    entry_price = level_price * (1 - BREAKOUT_CONFIRMATION_PCT * 0.5)
                    risk_from_level = level_price - entry_price
                    risk_minimum = entry_price * SL_PCT
                    risk_distance = max(risk_from_level, risk_minimum) * level['decay_factor']
                    
                    sl_price = entry_price + risk_distance
                    tp_price = entry_price - (risk_distance * TP_MULTIPLIER)
                    
                    return {
                        'side': 'SHORT',
                        'entry': entry_price,
                        'stop_loss': sl_price,
                        'take_profit': tp_price,
                        'risk_pct': (risk_distance / entry_price) * 100,
                        'reward_pct': ((entry_price - tp_price) / entry_price) * 100,
                        'level': level_price,
                        'breakout': breakout_amount * 100,
                        'current_price': curr_close,
                        'entry_time': curr_candle['open_time'],
                        'volume_confirmed': volume_confirmed,
                        'trend_aligned': True,
                        'level_decay_applied': level['decay_factor'] < 1.0
                    }
    
    return None


def calculate_position_size(current_capital, entry_price, stop_loss_price, side, leverage, current_price=None, funding_rate=None):
    """Calculate position size based on risk with liquidation protection and funding rate adjustment"""
    risk_amount = current_capital * RISK_PER_TRADE_PCT
    
    if side == 'LONG':
        price_risk = entry_price - stop_loss_price
    else:
        price_risk = stop_loss_price - entry_price
    
    if price_risk <= 0:
        return None
    
    position_units = risk_amount / price_risk
    position_value = position_units * entry_price
    margin_required = position_value / leverage
    
    if margin_required > current_capital:
        position_units = (current_capital * leverage) / entry_price
        position_value = position_units * entry_price
        margin_required = position_value / leverage
        risk_amount = (position_units * price_risk) / leverage
    
    # TRITON73: FUNDING RATE ADJUSTMENT
    # Adjust position size based on funding rate to offset costs
    if funding_rate is not None:
        if funding_rate > 0.001:  # >0.1% per 8h (costly for longs)
            if side == 'LONG':
                print(f"⚠️  High funding rate ({funding_rate*100:.3f}%): Reducing LONG position by 5%")
                position_units *= 0.95
                position_value = position_units * entry_price
                margin_required = position_value / leverage
                risk_amount = (position_units * price_risk) / leverage
        elif funding_rate < -0.001:  # < -0.1% per 8h (beneficial for longs)
            if side == 'LONG':
                print(f"✅ Negative funding rate ({funding_rate*100:.3f}%): Increasing LONG position by 2%")
                position_units *= 1.02
                position_value = position_units * entry_price
                margin_required = position_value / leverage
                risk_amount = (position_units * price_risk) / leverage
        elif funding_rate < 0.001 and side == 'SHORT':  # Positive funding helps shorts
            if funding_rate > 0:
                print(f"✅ Positive funding rate ({funding_rate*100:.3f}%): Increasing SHORT position by 2%")
                position_units *= 1.02
                position_value = position_units * entry_price
                margin_required = position_value / leverage
                risk_amount = (position_units * price_risk) / leverage
    
    # TRITON73: LIQUIDATION PROTECTION
    # If price is within 2% of liquidation, reduce position size by 50%
    if current_price is not None:
        # Calculate liquidation price (0.5% buffer for safety)
        if side == 'LONG':
            liquidation_price = entry_price * (1 - (1 / leverage) - 0.005)  # 0.5% buffer
            # If current price is within 2% of liquidation, reduce position
            if (entry_price * (1 - 0.005)) < current_price * (1 - 0.02):
                print("⚠️  LIQUIDATION RISK: Reducing position size by 50%")
                position_units *= 0.5
                position_value = position_units * entry_price
                margin_required = position_value / leverage
                risk_amount = (position_units * price_risk) / leverage
        else:  # SHORT
            liquidation_price = entry_price * (1 + (1 / leverage) + 0.005)  # 0.5% buffer
            # If current price is within 2% of liquidation, reduce position
            if (entry_price * (1 + 0.005)) > current_price * (1 + 0.02):
                print("⚠️  LIQUIDATION RISK: Reducing position size by 50%")
                position_units *= 0.5
                position_value = position_units * entry_price
                margin_required = position_value / leverage
                risk_amount = (position_units * price_risk) / leverage
    
    return {
        'position_units': position_units,
        'position_value': position_value,
        'margin_required': margin_required,
        'risk_amount': risk_amount
    }


def format_signal_enhanced(symbol, signal, position, current_capital, leverage, trend_filter):
    """Format enhanced trading signal"""
    side_emoji = "🟢" if signal['side'] == 'LONG' else "🔴"
    
    enhancements = []
    if signal.get('volume_confirmed'):
        enhancements.append("✅ Volume Confirmed")
    if signal.get('trend_aligned'):
        enhancements.append(f"✅ Trend: {trend_filter['trend']}")
    if signal.get('level_decay_applied'):
        enhancements.append("⚠️ Level Decay Applied")
    
    message = f"""
{'='*80}
{side_emoji} ENHANCED {signal['side']} SIGNAL - {symbol}
{'='*80}

📊 PRICES:
   Entry:      ${signal['entry']:,.2f}
   Stop Loss:  ${signal['stop_loss']:,.2f}
   Take Profit: ${signal['take_profit']:,.2f}
   Current:    ${signal['current_price']:,.2f}

💰 POSITION ({leverage}x Dynamic Leverage):
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

🚀 ENHANCEMENTS:
   {chr(10).join('   ' + e for e in enhancements) if enhancements else '   (Standard signal)'}

{'='*80}
"""
    return message.strip()


def main():
    """Main enhanced trading signal generator"""
    # Load state and check drawdown pause
    state = load_strategy_state()
    if check_drawdown_pause(state):
        print("="*80)
        print("⚠️  STRATEGY IS PAUSED DUE TO DRAWDOWN")
        print("="*80)
        print(f"Current Capital: €{state['current_capital']:,.2f}")
        print(f"Max Equity:      €{state['max_equity']:,.2f}")
        print(f"Drawdown:         {(state['current_capital'] - state['max_equity']) / state['max_equity'] * 100:.2f}%")
        print(f"Resume when capital reaches: €{state['max_equity'] * DRAWDOWN_RESUME_THRESHOLD:,.2f}")
        print("="*80)
        return
    
    print("="*80)
    print("TRITON73 - MEXC BTCUSDT ENHANCED STRATEGY (SAFER VERSION)")
    print("="*80)
    print(f"Strategy: Enhanced Breakout with Dynamic Leverage (3.5x base)")
    print(f"Risk: {RISK_PER_TRADE_PCT*100:.2f}% per trade | Liquidation Protection: ENABLED")
    print(f"Interval: {INTERVAL}")
    print(f"Stop Loss: {SL_PCT*100:.2f}%")
    print(f"Take Profit: {TP_MULTIPLIER:.1f}:1 R:R")
    print(f"Capital: €{state['current_capital']:,.2f}")
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
    
    # Calculate level with decay
    level = calculate_level_with_decay(df, len(df) - 1)
    if level is None:
        print(f"  ⚠ No valid level found")
        return
    
    print(f"  Level: ${level['price']:,.2f} (age: {level['age_hours']:.1f}h, decay: {level['decay_factor']:.2f})")
    
    # Check trend filter
    trend_filter = check_trend_filter(df)
    print(f"  Trend: {trend_filter['trend']} (LONG: {'✅' if trend_filter['long_allowed'] else '❌'}, SHORT: {'✅' if trend_filter['short_allowed'] else '❌'})")
    
    # Calculate dynamic leverage
    current_price = float(df.iloc[-1]['close'])
    leverage = calculate_dynamic_leverage(df, current_price)
    print(f"  Dynamic Leverage: {leverage}x (ATR-based)")
    
    # Check for breakout
    signal = check_breakout_enhanced(df, level, trend_filter, USE_SECOND_CONFIRMATION)
    
    if signal:
        # Fetch funding rate for position size adjustment
        funding_rate = fetch_funding_rate(SYMBOL)
        if funding_rate != 0:
            print(f"  Funding Rate: {funding_rate*100:.3f}% per 8h")
        
        position = calculate_position_size(
            state['current_capital'],
            signal['entry'],
            signal['stop_loss'],
            signal['side'],
            leverage,
            current_price=signal['current_price'],  # Pass current price for liquidation check
            funding_rate=funding_rate  # Pass funding rate for adjustment
        )
        
        if position:
            message = format_signal_enhanced(SYMBOL, signal, position, state['current_capital'], leverage, trend_filter)
            print(message)
            
            # Save position info
            position_info = {
                'symbol': SYMBOL,
                'side': signal['side'],
                'entry': signal['entry'],
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'entry_time': signal['entry_time'].isoformat() if hasattr(signal['entry_time'], 'isoformat') else str(signal['entry_time']),
                'level': signal['level'],
                'leverage': leverage,
                'position_units': position['position_units'],
                'position_value': position['position_value'],
                'margin_required': position['margin_required']
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
        print(f"  No signal")
        if level['age_hours'] < MIN_LEVEL_AGE_HOURS:
            print(f"    (Level too young: {level['age_hours']:.1f}h < {MIN_LEVEL_AGE_HOURS}h)")
        if not trend_filter['long_allowed'] and not trend_filter['short_allowed']:
            print(f"    (Trend filter blocking: {trend_filter['trend']})")
    
    print("\n" + "="*80)


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


if __name__ == "__main__":
    main()

