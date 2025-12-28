#!/usr/bin/env python3
"""
Continuous Runner for Triton73 Strategy
Runs the Triton73 script at each 4h candle close (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)
"""

import subprocess
import time
import sys
import shutil
import os
from datetime import datetime, timedelta
import pytz

# Script to run - TRITON73 (SAFER VERSION)
SIGNAL_SCRIPT = "Triton73.py"
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
            # Next check is at this hour, 5 minutes past (to ensure candle is closed)
            next_time = now.replace(hour=hour, minute=5, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(hours=INTERVAL_HOURS)
            return next_time
    
    # If no check today, use first check tomorrow
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=0, minute=5, second=0, microsecond=0)


def backup_strategy_state():
    """Backup strategy_state.json before updates"""
    state_file = 'strategy_state.json'
    if os.path.exists(state_file):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f'strategy_state_backup_{timestamp}.json'
            shutil.copy(state_file, backup_file)
            # Keep only last 10 backups
            backups = sorted([f for f in os.listdir('.') if f.startswith('strategy_state_backup_')])
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    try:
                        os.remove(old_backup)
                    except:
                        pass
        except Exception as e:
            print(f"⚠️  Could not backup strategy state: {e}")


def run_signal_script():
    """Run the Triton73 trading signals script"""
    # Backup strategy state before running
    backup_strategy_state()
    
    try:
        result = subprocess.run(
            [sys.executable, SIGNAL_SCRIPT],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⚠️  Signal script timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running signal script: {e}")
        return False


def main():
    """Main continuous loop"""
    print("=" * 80)
    print("TRITON73 CONTINUOUS TRADING SIGNALS RUNNER")
    print("=" * 80)
    print(f"Script: {SIGNAL_SCRIPT}")
    print(f"Configuration: 3.5x base leverage, 0.3% risk, Liquidation Protection ENABLED")
    print(f"Interval: {INTERVAL_HOURS}h (4h candles)")
    print(f"Check times: {', '.join(f'{h:02d}:05 UTC' for h in CANDLE_CLOSE_HOURS)}")
    print("=" * 80)
    print()
    
    # Run immediately on start
    print(f"[{datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}] Running initial check...")
    run_signal_script()
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
            
            # Convert to hours and minutes for display
            wait_hours = int(wait_seconds // 3600)
            wait_minutes = int((wait_seconds % 3600) // 60)
            
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S UTC')}] Next check: {next_check.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"  Waiting {wait_hours}h {wait_minutes}m...")
            print()
            
            # Wait until next check time
            time.sleep(wait_seconds)
            
            # Run signal script
            print(f"[{datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}] Running signal check...")
            run_signal_script()
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

