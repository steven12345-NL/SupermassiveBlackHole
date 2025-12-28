#!/usr/bin/env python3
"""
Paper Trading Performance Report
Generates comprehensive performance analysis from paper trading data
"""

import json
import csv
import os
from datetime import datetime

PAPER_STATE_FILE = 'paper_state.json'
TRADE_JOURNAL_FILE = 'trade_journal.csv'


def load_paper_state():
    """Load paper trading state"""
    try:
        with open(PAPER_STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Paper trading state file not found")
        return None


def load_trade_journal():
    """Load trade journal CSV"""
    if not os.path.exists(TRADE_JOURNAL_FILE):
        return []
    
    trades = []
    try:
        with open(TRADE_JOURNAL_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trades.append(row)
        return trades
    except Exception as e:
        print(f"⚠️  Error reading trade journal: {e}")
        return []


def generate_performance_report():
    """Generate comprehensive performance report"""
    print("="*80)
    print("PAPER TRADING PERFORMANCE REPORT")
    print("="*80)
    print()
    
    # Load data
    state = load_paper_state()
    if not state:
        return
    
    journal_trades = load_trade_journal()
    
    # Basic Statistics
    print("📊 BASIC STATISTICS")
    print("-"*80)
    initial_capital = state.get('initial_capital', 1000)
    current_capital = state['capital']
    total_pnl = state['total_pnl']
    return_pct = ((current_capital / initial_capital) - 1) * 100
    
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Current Capital: ${current_capital:,.2f}")
    print(f"Total P&L: ${total_pnl:+,.2f}")
    print(f"Return: {return_pct:+.2f}%")
    print(f"Max Equity: ${state['max_equity']:,.2f}")
    drawdown = (current_capital - state['max_equity']) / state['max_equity'] * 100
    print(f"Current Drawdown: {drawdown:.2f}%")
    print()
    
    # Trade Statistics
    print("📈 TRADE STATISTICS")
    print("-"*80)
    total_trades = state['total_trades']
    winning_trades = state['winning_trades']
    losing_trades = state['losing_trades']
    
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Loss Rate: {(losing_trades / total_trades) * 100:.2f}%")
    print()
    
    # Closed Trades Analysis
    closed_trades = state.get('closed_trades', [])
    if closed_trades:
        print("💰 CLOSED TRADES ANALYSIS")
        print("-"*80)
        
        # Calculate metrics
        wins = [t for t in closed_trades if t['result'] == 'WIN']
        losses = [t for t in closed_trades if t['result'] == 'LOSS']
        
        if wins:
            avg_win = sum(float(t['pnl']) for t in wins) / len(wins)
            max_win = max(float(t['pnl']) for t in wins)
            print(f"Average Win: ${avg_win:+,.2f}")
            print(f"Max Win: ${max_win:+,.2f}")
        
        if losses:
            avg_loss = sum(float(t['pnl']) for t in losses) / len(losses)
            max_loss = min(float(t['pnl']) for t in losses)
            print(f"Average Loss: ${avg_loss:+,.2f}")
            print(f"Max Loss: ${max_loss:+,.2f}")
        
        if wins and losses:
            total_wins = sum(float(t['pnl']) for t in wins)
            total_losses = abs(sum(float(t['pnl']) for t in losses))
            profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
            print(f"Profit Factor: {profit_factor:.2f}")
        
        # R:R Analysis
        if wins and losses:
            avg_win_pct = sum(float(t['pnl_pct']) for t in wins) / len(wins)
            avg_loss_pct = abs(sum(float(t['pnl_pct']) for t in losses) / len(losses))
            rr_ratio = avg_win_pct / avg_loss_pct if avg_loss_pct > 0 else 0
            print(f"Average R:R: {rr_ratio:.2f}:1")
        print()
        
        # Recent Trades
        print("📋 RECENT TRADES (Last 10)")
        print("-"*80)
        for i, trade in enumerate(reversed(closed_trades[-10:]), 1):
            try:
                entry_time = datetime.fromisoformat(trade['entry_time'].replace('Z', '+00:00'))
                exit_time = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                duration = exit_time - entry_time
                duration_str = f"{duration.days}d {duration.seconds//3600}h"
            except:
                duration_str = "N/A"
            
            result_emoji = "✅" if trade['result'] == 'WIN' else "❌"
            pnl = float(trade['pnl'])
            pnl_pct = float(trade['pnl_pct'])
            print(f"{i}. {result_emoji} {trade['side']} | Entry: ${float(trade['entry']):,.2f} | Exit: ${float(trade['exit']):,.2f}")
            print(f"   P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%) | {trade['reason']} | Duration: {duration_str}")
        print()
    
    # Open Positions
    open_positions = state.get('open_positions', [])
    if open_positions:
        print("🔄 OPEN POSITIONS")
        print("-"*80)
        for i, pos in enumerate(open_positions, 1):
            print(f"Position #{i}: {pos['side']} | Entry: ${float(pos['entry']):,.2f} | Leverage: {pos['leverage']}x")
        print()
    
    # Trade Journal Analysis (if available)
    if journal_trades:
        print("📊 TRADE JOURNAL ANALYSIS")
        print("-"*80)
        print(f"Total entries in journal: {len(journal_trades)}")
        
        journal_pnl = sum(float(t.get('pnl', 0)) for t in journal_trades)
        print(f"Total P&L from journal: ${journal_pnl:+,.2f}")
        
        journal_wins = sum(1 for t in journal_trades if t.get('result') == 'WIN')
        if len(journal_trades) > 0:
            print(f"Win Rate from journal: {(journal_wins / len(journal_trades)) * 100:.2f}%")
        print()
    
    # Performance Metrics
    if total_trades >= 10:
        print("📈 PERFORMANCE METRICS")
        print("-"*80)
        
        if closed_trades:
            returns = [float(t['pnl_pct']) for t in closed_trades]
            avg_return = sum(returns) / len(returns)
            if len(returns) > 1:
                variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
                volatility = variance ** 0.5
                sharpe_like = avg_return / volatility if volatility > 0 else 0
                print(f"Average Return per Trade: {avg_return:+.2f}%")
                print(f"Return Volatility: {volatility:.2f}%")
                print(f"Risk-Adjusted Return: {sharpe_like:.2f}")
        
        if state['max_equity'] > 0:
            max_dd = abs((current_capital - state['max_equity']) / state['max_equity'] * 100)
            calmar = return_pct / max_dd if max_dd > 0 else 0
            print(f"Calmar Ratio: {calmar:.2f}")
        print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS")
    print("-"*80)
    if total_trades == 0:
        print("⚠️  No trades completed yet. Continue paper trading to gather data.")
    elif total_trades < 30:
        print(f"📊 You have {total_trades} trades. Continue to 30+ trades for reliable statistics.")
    else:
        win_rate = (winning_trades / total_trades) * 100
        if win_rate >= 55 and drawdown > -8:
            print("✅ Performance looks good!")
            print("   - Win rate > 55%")
            print("   - Drawdown < 8%")
            print("   - Consider moving to live trading with small capital")
        else:
            print("⚠️  Continue paper trading:")
            if win_rate < 55:
                print(f"   - Win rate is {win_rate:.1f}% (target: >55%)")
            if drawdown < -8:
                print(f"   - Drawdown is {drawdown:.1f}% (target: <8%)")
    
    print()
    print("="*80)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    print("📁 DATA FILES:")
    print(f"   - {PAPER_STATE_FILE} - Current state and all closed trades")
    print(f"   - {TRADE_JOURNAL_FILE} - Detailed trade journal (if exists)")
    print("="*80)


if __name__ == "__main__":
    generate_performance_report()
