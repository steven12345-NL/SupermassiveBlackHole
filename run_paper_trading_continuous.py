#!/usr/bin/env python3
"""
Continuous Runner for Triton73 Paper Trading
Runs paper trading simulation at each 4h candle close
"""

import subprocess
import time
import sys
from datetime import datetime, timedelta
import pytz

# Script to run
PAPER_TRADING_SCRIPT = "Triton73_paper_trading.py"
INTERVAL_HOURS = 4
CANDLE_CLOSE_HOURS = [0, 4, 8, 12, 16, 20]  # 4h candle closes


def get_next_check_time():
    """Calculate next 4h candle close time"""
    utc = pytz.UTC
    now = datetime.now(utc)
    
    current_hour = now.hour
    current_minute = now.minute
    
    # Find next candle close
    for hour in CANDLE_CLOSE_HOURS:
        if hour > current_hour or (hour == current_hour and current_minute < 5):
            next_time = now.replace(hour=hour, minute=5, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(hours=INTERVAL_HOURS)
            return next_time
    
    # If no check today, use first check tomorrow
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=0, minute=5, second=0, microsecond=0)


def run_paper_trading():
    """Run the paper trading script"""
    try:
        # Open log file for appending
        with open('paper_trading.log', 'a') as log_file:
            log_file.write(f"\n{'='*80}\n")
            log_file.write(f"[{datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}] Running paper trading check...\n")
            log_file.write(f"{'='*80}\n")
            
            result = subprocess.run(
                [sys.executable, PAPER_TRADING_SCRIPT],
                cwd=".",
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Write output to log file
            if result.stdout:
                log_file.write(result.stdout)
                log_file.write("\n")
                print(result.stdout)
            if result.stderr:
                log_file.write(result.stderr)
                log_file.write("\n")
                print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⚠️  Paper trading script timed out")
        return False
    except Exception as e:
        print(f"❌ Error running paper trading: {e}")
        return False


def main():
    """Main continuous loop"""
    print("=" * 80)
    print("TRITON73 PAPER TRADING - CONTINUOUS RUNNER")
    print("=" * 80)
    print(f"Script: {PAPER_TRADING_SCRIPT}")
    print(f"Mode: Paper Trading (Virtual Positions)")
    print(f"Interval: {INTERVAL_HOURS}h (4h candles)")
    print(f"Check times: {', '.join(f'{h:02d}:05 UTC' for h in CANDLE_CLOSE_HOURS)}")
    print("=" * 80)
    print()
    
    # Run immediately on start
    print(f"[{datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}] Running initial check...")
    run_paper_trading()
    print()
    
    # Continuous loop
    while True:
        try:
            # Calculate next check time
            next_check = get_next_check_time()
            now = datetime.now(pytz.UTC)
            wait_seconds = (next_check - now).total_seconds()
            
            if wait_seconds < 0:
                wait_seconds = 0
            
            wait_hours = int(wait_seconds // 3600)
            wait_minutes = int((wait_seconds % 3600) // 60)
            
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S UTC')}] Next check: {next_check.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"  Waiting {wait_hours}h {wait_minutes}m...")
            print()
            
            # Wait until next check time
            time.sleep(wait_seconds)
            
            # Run paper trading
            print(f"[{datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}] Running paper trading check...")
            run_paper_trading()
            print()
            
        except KeyboardInterrupt:
            print("\n" + "=" * 80)
            print("Stopped by user (Ctrl+C)")
            print("=" * 80)
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            print("  Waiting 60 seconds before retry...")
            time.sleep(60)


if __name__ == "__main__":
    main()

