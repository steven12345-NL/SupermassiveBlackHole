#!/usr/bin/env python3
"""
MEXC BTCUSDT Position Monitor
Monitors open positions and alerts if market conditions suggest TP may not be reached
Runs continuously and checks position status at each 4h candle close
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import sys
from collections import deque

# MEXC API Configuration
MEXC_API_BASE = "https://api.mexc.com/api/v3"

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# Strategy Parameters (must match mexc_btcusdt_signals.py)
SYMBOL = 'BTCUSDT'
INTERVAL = '4h'
SESSION_CLOSE_HOUR_UTC = 0
BREAKOUT_CONFIRMATION_PCT = 0.001  # 0.1%
SL_PCT = 0.004  # 0.4%
TP_MULTIPLIER = 3.5
LEVERAGE = 3.0
MIN_LEVEL_AGE_HOURS = 6

# Position tracking file (stores current position info)
POSITION_FILE = 'current_position.json'


def fetch_mexc_klines(symbol, interval, limit=500):
    """Fetch klines from MEXC"""
    try:
        url = f"{MEXC_API_BASE}/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
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


def load_position():
    """Load current position from file"""
    import json
    if not os.path.exists(POSITION_FILE):
        return None
    
    try:
        with open(POSITION_FILE, 'r') as f:
            return json.load(f)
    except:
        return None


def save_position(position):
    """Save position to file"""
    import json
    try:
        with open(POSITION_FILE, 'w') as f:
            json.dump(position, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving position: {e}")


def clear_position():
    """Clear position file"""
    if os.path.exists(POSITION_FILE):
        try:
            os.remove(POSITION_FILE)
        except:
            pass


def calculate_atr(df, period=14):
    """Calculate Average True Range"""
    if len(df) < period + 1:
        return None
    
    df = df.copy()
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    
    df['prev_close'] = df['close'].shift(1)
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['prev_close'])
    df['tr3'] = abs(df['low'] - df['prev_close'])
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    atr = df['tr'].rolling(window=period).mean().iloc[-1]
    return float(atr) if pd.notna(atr) else None


def analyze_position_health(df, position):
    """Analyze if position is at risk of not reaching TP"""
    if not position:
        return None
    
    current_price = float(df.iloc[-1]['close'])
    entry = float(position['entry'])
    stop_loss = float(position['stop_loss'])
    take_profit = float(position['take_profit'])
    side = position['side']
    entry_time = pd.to_datetime(position['entry_time'])
    
    # Calculate current P&L
    if side == 'LONG':
        pnl_pct = ((current_price - entry) / entry) * 100 * LEVERAGE
        distance_to_tp = (take_profit - current_price) / current_price * 100
        distance_to_sl = (current_price - stop_loss) / current_price * 100
        progress_to_tp = ((current_price - entry) / (take_profit - entry)) * 100 if take_profit > entry else 0
    else:  # SHORT
        pnl_pct = ((entry - current_price) / entry) * 100 * LEVERAGE
        distance_to_tp = (current_price - take_profit) / current_price * 100
        distance_to_sl = (stop_loss - current_price) / current_price * 100
        progress_to_tp = ((entry - current_price) / (entry - take_profit)) * 100 if take_profit < entry else 0
    
    # Position age
    position_age_hours = (pd.Timestamp.now(tz='UTC') - entry_time).total_seconds() / 3600
    
    # Recent price action (last 5 candles)
    recent = df.tail(5)
    recent_highs = [float(h) for h in recent['high']]
    recent_lows = [float(l) for l in recent['low']]
    
    # Check if price is moving away from TP
    if side == 'LONG':
        max_recent_high = max(recent_highs)
        price_moving_away = current_price < max_recent_high * 0.995  # 0.5% below recent high
        momentum_negative = current_price < recent['close'].iloc[-2] if len(recent) > 1 else False
    else:  # SHORT
        min_recent_low = min(recent_lows)
        price_moving_away = current_price > min_recent_low * 1.005  # 0.5% above recent low
        momentum_negative = current_price > recent['close'].iloc[-2] if len(recent) > 1 else False
    
    # Volatility analysis
    atr = calculate_atr(df, period=14)
    atr_pct = (atr / current_price * 100) if atr else None
    
    # Check if volatility is decreasing (bad for reaching TP)
    if len(df) >= 28:
        recent_atr = calculate_atr(df.tail(14), period=7)
        older_atr = calculate_atr(df.iloc[:-14], period=7) if len(df) > 14 else None
        volatility_decreasing = (recent_atr and older_atr and recent_atr < older_atr * 0.8) if older_atr else False
    else:
        volatility_decreasing = False
    
    # Risk assessment
    warnings = []
    risk_level = "LOW"
    
    # Check if price hit SL
    if side == 'LONG' and current_price <= stop_loss:
        warnings.append("🚨 STOP LOSS HIT - Position should be closed!")
        risk_level = "CRITICAL"
    elif side == 'SHORT' and current_price >= stop_loss:
        warnings.append("🚨 STOP LOSS HIT - Position should be closed!")
        risk_level = "CRITICAL"
    
    # Check if price hit TP
    elif side == 'LONG' and current_price >= take_profit:
        warnings.append("🎯 TAKE PROFIT REACHED - Close position!")
        risk_level = "SUCCESS"
    elif side == 'SHORT' and current_price <= take_profit:
        warnings.append("🎯 TAKE PROFIT REACHED - Close position!")
        risk_level = "SUCCESS"
    
    # Check if price is moving away from TP
    elif price_moving_away and momentum_negative:
        warnings.append("⚠️  Price moving away from TP with negative momentum")
        risk_level = "MEDIUM"
    
    # Check if volatility is decreasing
    elif volatility_decreasing and progress_to_tp < 50:
        warnings.append("⚠️  Volatility decreasing - may struggle to reach TP")
        risk_level = "MEDIUM"
    
    # Check if position is stuck (no progress for extended period)
    elif position_age_hours > 48 and abs(progress_to_tp) < 20:
        warnings.append("⚠️  Position stuck - minimal progress after 48+ hours")
        risk_level = "MEDIUM"
    
    # Check if price is near SL
    elif distance_to_sl < 0.2:  # Within 0.2% of SL
        warnings.append("⚠️  Price very close to stop loss")
        risk_level = "HIGH"
    
    # Check if progress is slow relative to time
    elif position_age_hours > 24 and progress_to_tp < 30:
        warnings.append("⚠️  Slow progress - only {:.1f}% to TP after 24+ hours".format(progress_to_tp))
        risk_level = "MEDIUM"
    
    return {
        'current_price': current_price,
        'entry': entry,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'side': side,
        'pnl_pct': pnl_pct,
        'distance_to_tp': distance_to_tp,
        'distance_to_sl': distance_to_sl,
        'progress_to_tp': progress_to_tp,
        'position_age_hours': position_age_hours,
        'price_moving_away': price_moving_away,
        'momentum_negative': momentum_negative,
        'volatility_decreasing': volatility_decreasing,
        'atr_pct': atr_pct,
        'warnings': warnings,
        'risk_level': risk_level
    }


def format_position_status(analysis, position):
    """Format position status message"""
    if not analysis:
        return None
    
    msg = []
    msg.append("=" * 80)
    msg.append("📊 POSITION MONITOR - BTCUSDT")
    msg.append("=" * 80)
    msg.append("")
    
    msg.append(f"Position: {analysis['side']}")
    msg.append(f"Entry:    ${analysis['entry']:,.2f}")
    msg.append(f"Current:  ${analysis['current_price']:,.2f}")
    msg.append(f"Stop Loss: ${analysis['stop_loss']:,.2f} ({analysis['distance_to_sl']:.2f}% away)")
    msg.append(f"Take Profit: ${analysis['take_profit']:,.2f} ({analysis['distance_to_tp']:.2f}% away)")
    msg.append("")
    
    msg.append(f"Current P&L: {analysis['pnl_pct']:+.2f}%")
    msg.append(f"Progress to TP: {analysis['progress_to_tp']:.1f}%")
    msg.append(f"Position Age: {analysis['position_age_hours']:.1f} hours")
    msg.append("")
    
    if analysis['atr_pct']:
        msg.append(f"Current Volatility (ATR): {analysis['atr_pct']:.3f}%")
    
    if analysis['warnings']:
        msg.append("")
        msg.append("⚠️  WARNINGS:")
        for warning in analysis['warnings']:
            msg.append(f"  {warning}")
    
    msg.append("")
    msg.append(f"Risk Level: {analysis['risk_level']}")
    msg.append("=" * 80)
    
    return "\n".join(msg)


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


def check_position():
    """Check current position status"""
    position = load_position()
    
    if not position:
        return None
    
    # Fetch current data
    klines = fetch_mexc_klines(SYMBOL, INTERVAL)
    if not klines:
        return None
    
    df = klines_to_df(klines)
    if len(df) < 50:
        return None
    
    # Analyze position
    analysis = analyze_position_health(df, position)
    
    if not analysis:
        return None
    
    # Check if position should be closed (hit SL or TP)
    if analysis['risk_level'] in ['CRITICAL', 'SUCCESS']:
        # Position hit SL or TP - clear it
        clear_position()
        return analysis
    
    return analysis


def get_next_check_time():
    """Calculate next 4h candle close time"""
    from datetime import timezone
    import pytz
    
    utc = pytz.UTC
    now = datetime.now(utc)
    
    current_hour = now.hour
    current_minute = now.minute
    
    # 4h candle closes at: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC
    candle_close_hours = [0, 4, 8, 12, 16, 20]
    
    for hour in candle_close_hours:
        if hour > current_hour or (hour == current_hour and current_minute < 5):
            next_time = now.replace(hour=hour, minute=5, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(hours=4)
            return next_time
    
    # If no check today, use first check tomorrow
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=0, minute=5, second=0, microsecond=0)


def main():
    """Main monitoring loop"""
    print("=" * 80)
    print("MEXC BTCUSDT POSITION MONITOR")
    print("=" * 80)
    print("Monitors open positions and alerts if TP may not be reached")
    print("Checks at each 4h candle close (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)")
    print("=" * 80)
    print()
    
    last_analysis = None
    
    while True:
        try:
            position = load_position()
            
            if not position:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No open position")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking position...")
                analysis = check_position()
                
                if analysis:
                    status_msg = format_position_status(analysis, position)
                    print(status_msg)
                    
                    # Send alert if risk level changed or warnings appeared
                    if last_analysis:
                        if (analysis['risk_level'] != last_analysis.get('risk_level') or
                            len(analysis['warnings']) > len(last_analysis.get('warnings', []))):
                            # Risk level changed or new warnings - send alert
                            send_telegram(status_msg)
                    elif analysis['warnings']:
                        # First check with warnings - send alert
                        send_telegram(status_msg)
                    
                    last_analysis = analysis
                else:
                    print("  ⚠️  Could not analyze position")
            
            # Wait until next 4h candle close
            next_check = get_next_check_time()
            wait_seconds = (next_check - datetime.now(pd.Timestamp.now(tz='UTC').tz)).total_seconds()
            
            if wait_seconds > 0:
                print(f"\nNext check: {next_check.strftime('%Y-%m-%d %H:%M:%S UTC')} (in {wait_seconds/3600:.1f} hours)")
                print("-" * 80)
                time.sleep(wait_seconds)
            else:
                time.sleep(300)  # Wait 5 minutes if calculation failed
                
        except KeyboardInterrupt:
            print("\n\nStopping position monitor...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(300)  # Wait 5 minutes on error


if __name__ == "__main__":
    main()

