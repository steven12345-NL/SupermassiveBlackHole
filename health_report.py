#!/usr/bin/env python3
"""
Triton73 Strategy Health Report
Generates daily health check with key metrics and recommendations
"""

import json
import os
from datetime import datetime, timedelta
import csv

PAPER_STATE_FILE = 'paper_state.json'
STRATEGY_STATE_FILE = 'strategy_state.json'
TRADE_JOURNAL_FILE = 'trade_journal.csv'
HEALTH_REPORT_FILE = 'health_report.txt'


def load_paper_state():
    """Load paper trading state"""
    try:
        with open(PAPER_STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def load_strategy_state():
    """Load strategy state"""
    try:
        with open(STRATEGY_STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def load_trade_journal():
    """Load trade journal"""
    if not os.path.exists(TRADE_JOURNAL_FILE):
        return []
    
    trades = []
    try:
        with open(TRADE_JOURNAL_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trades.append(row)
    except:
        pass
    
    return trades


def calculate_metrics(paper_state, strategy_state, journal_trades):
    """Calculate health metrics"""
    metrics = {
        'last_trade_result': 'N/A',
        'drawdown': 0.0,
        'capital_growth': 0.0,
        'win_rate_20': 0.0,
        'avg_rr': 0.0,
        'funding_rate_impact': 0.0,
        'liquidation_protection_triggered': 0,
        'strategy_status': 'UNKNOWN',
        'recommendation': 'Continue monitoring'
    }
    
    # Use paper state if available, otherwise strategy state
    state = paper_state if paper_state else strategy_state
    if not state:
        return metrics
    
    # Last trade result
    closed_trades = state.get('closed_trades', [])
    if closed_trades:
        last_trade = closed_trades[-1]
        metrics['last_trade_result'] = last_trade.get('result', 'N/A')
    
    # Drawdown
    current_capital = state.get('capital', state.get('current_capital', 0))
    max_equity = state.get('max_equity', current_capital)
    if max_equity > 0:
        metrics['drawdown'] = ((current_capital - max_equity) / max_equity) * 100
    
    # Capital growth (this month)
    initial_capital = state.get('initial_capital', 1000)
    if initial_capital > 0:
        metrics['capital_growth'] = ((current_capital / initial_capital) - 1) * 100
    
    # Win rate (last 20 trades)
    if closed_trades:
        last_20 = closed_trades[-20:]
        wins = sum(1 for t in last_20 if t.get('result') == 'WIN')
        if len(last_20) > 0:
            metrics['win_rate_20'] = (wins / len(last_20)) * 100
    
    # Average R:R
    if closed_trades:
        wins = [t for t in closed_trades if t.get('result') == 'WIN']
        losses = [t for t in closed_trades if t.get('result') == 'LOSS']
        if wins and losses:
            avg_win_pct = sum(float(t.get('pnl_pct', 0)) for t in wins) / len(wins)
            avg_loss_pct = abs(sum(float(t.get('pnl_pct', 0)) for t in losses) / len(losses))
            if avg_loss_pct > 0:
                metrics['avg_rr'] = avg_win_pct / avg_loss_pct
    
    # Funding rate impact (simplified - would need actual funding rate history)
    # For now, estimate based on position holding time
    metrics['funding_rate_impact'] = 0.0  # Placeholder
    
    # Liquidation protection triggered (would need to track this)
    metrics['liquidation_protection_triggered'] = 0  # Placeholder
    
    # Strategy status
    if state.get('paused', False):
        metrics['strategy_status'] = '⏸️  PAUSED'
        metrics['recommendation'] = 'Strategy is paused due to drawdown. Wait for recovery.'
    elif metrics['drawdown'] < -12:
        metrics['strategy_status'] = '⚠️  HIGH DRAWDOWN'
        metrics['recommendation'] = 'Reduce risk to 0.15% and monitor closely.'
    elif metrics['win_rate_20'] < 45 and len(closed_trades) >= 10:
        metrics['strategy_status'] = '⚠️  LOW WIN RATE'
        metrics['recommendation'] = 'Win rate below 45% for 10+ trades. Pause and investigate.'
    elif metrics['win_rate_20'] >= 55 and metrics['drawdown'] > -8:
        metrics['strategy_status'] = '✅ HEALTHY'
        metrics['recommendation'] = 'Continue. No changes needed.'
    else:
        metrics['strategy_status'] = '✅ MONITORING'
        metrics['recommendation'] = 'Continue monitoring. Performance within acceptable range.'
    
    return metrics


def generate_health_report():
    """Generate health report"""
    paper_state = load_paper_state()
    strategy_state = load_strategy_state()
    journal_trades = load_trade_journal()
    
    metrics = calculate_metrics(paper_state, strategy_state, journal_trades)
    
    # Generate report
    report = []
    report.append("="*80)
    report.append("TRITON73 STRATEGY HEALTH REPORT")
    report.append("="*80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("📊 KEY METRICS")
    report.append("-"*80)
    report.append(f"Last Trade Result: {metrics['last_trade_result']}")
    report.append(f"Drawdown: {metrics['drawdown']:.2f}%")
    report.append(f"Capital Growth (from start): {metrics['capital_growth']:+.2f}%")
    report.append(f"Win Rate (last 20 trades): {metrics['win_rate_20']:.1f}%")
    report.append(f"Average R:R: {metrics['avg_rr']:.2f}:1")
    report.append(f"Funding Rate Impact: {metrics['funding_rate_impact']:+.2f}%")
    report.append(f"Liquidation Protection Triggered: {metrics['liquidation_protection_triggered']} times")
    report.append("")
    
    report.append("🎯 STRATEGY STATUS")
    report.append("-"*80)
    report.append(f"Status: {metrics['strategy_status']}")
    report.append("")
    
    report.append("💡 RECOMMENDATION")
    report.append("-"*80)
    report.append(metrics['recommendation'])
    report.append("")
    
    # Additional context
    state = paper_state if paper_state else strategy_state
    if state:
        report.append("📈 ADDITIONAL CONTEXT")
        report.append("-"*80)
        current_capital = state.get('capital', state.get('current_capital', 0))
        total_trades = state.get('total_trades', 0)
        winning_trades = state.get('winning_trades', 0)
        losing_trades = state.get('losing_trades', 0)
        
        report.append(f"Current Capital: ${current_capital:,.2f}")
        report.append(f"Total Trades: {total_trades}")
        report.append(f"Winning Trades: {winning_trades}")
        report.append(f"Losing Trades: {losing_trades}")
        
        if total_trades > 0:
            overall_win_rate = (winning_trades / total_trades) * 100
            report.append(f"Overall Win Rate: {overall_win_rate:.1f}%")
        
        open_positions = state.get('open_positions', [])
        if open_positions:
            report.append(f"Open Positions: {len(open_positions)}")
        report.append("")
    
    report.append("="*80)
    report.append(f"Report saved to: {HEALTH_REPORT_FILE}")
    report.append("="*80)
    
    # Write to file
    report_text = "\n".join(report)
    with open(HEALTH_REPORT_FILE, 'w') as f:
        f.write(report_text)
    
    # Also print to console
    print(report_text)
    
    return metrics


if __name__ == "__main__":
    generate_health_report()

