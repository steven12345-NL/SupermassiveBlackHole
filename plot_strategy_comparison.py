#!/usr/bin/env python3
"""
Plot key metrics comparison for Original vs Markov Chain strategies
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Strategy metrics
original = {
    'name': 'Original Strategy',
    'return': 20659.89,  # %
    'win_rate': 55.48,  # %
    'profit_factor': 3.64,
    'drawdown': -6.14,  # %
    'trades': 456,
    'final_capital': 207599,  # from €1,000
    'color': '#2E86AB'  # Blue
}

markov = {
    'name': 'Markov Chain Strategy',
    'return': 112334.42,  # %
    'win_rate': 49.60,  # %
    'profit_factor': 2.44,
    'drawdown': -9.45,  # %
    'trades': 752,
    'final_capital': 1124344,  # from €1,000
    'color': '#A23B72'  # Purple
}

# Create figure with subplots
fig = plt.figure(figsize=(16, 10))
fig.suptitle('Strategy Comparison: Original vs Markov Chain\n(2 Years, 4h Timeframe, 3x Leverage)', 
             fontsize=16, fontweight='bold', y=0.98)

# 1. Return Comparison (Bar Chart)
ax1 = plt.subplot(2, 3, 1)
strategies = [original['name'], markov['name']]
returns = [original['return'], markov['return']]
colors = [original['color'], markov['color']]
bars = ax1.bar(strategies, returns, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('Total Return (%)', fontsize=11, fontweight='bold')
ax1.set_title('Total Return (2 Years)', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.set_yscale('log')  # Log scale for better visualization

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, returns)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:,.0f}%',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# 2. Win Rate Comparison
ax2 = plt.subplot(2, 3, 2)
win_rates = [original['win_rate'], markov['win_rate']]
bars2 = ax2.bar(strategies, win_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('Win Rate (%)', fontsize=11, fontweight='bold')
ax2.set_title('Win Rate', fontsize=12, fontweight='bold')
ax2.set_ylim(0, 60)
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Break-even')

for i, (bar, val) in enumerate(zip(bars2, win_rates)):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.2f}%',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# 3. Profit Factor Comparison
ax3 = plt.subplot(2, 3, 3)
profit_factors = [original['profit_factor'], markov['profit_factor']]
bars3 = ax3.bar(strategies, profit_factors, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax3.set_ylabel('Profit Factor', fontsize=11, fontweight='bold')
ax3.set_title('Profit Factor', fontsize=12, fontweight='bold')
ax3.set_ylim(0, 4)
ax3.grid(axis='y', alpha=0.3, linestyle='--')
ax3.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='Break-even')

for i, (bar, val) in enumerate(zip(bars3, profit_factors)):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.2f}',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# 4. Drawdown Comparison (negative values)
ax4 = plt.subplot(2, 3, 4)
drawdowns = [original['drawdown'], markov['drawdown']]
bars4 = ax4.bar(strategies, drawdowns, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax4.set_ylabel('Max Drawdown (%)', fontsize=11, fontweight='bold')
ax4.set_title('Maximum Drawdown', fontsize=12, fontweight='bold')
ax4.set_ylim(-12, 0)
ax4.grid(axis='y', alpha=0.3, linestyle='--')

for i, (bar, val) in enumerate(zip(bars4, drawdowns)):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.2f}%',
             ha='center', va='top', fontsize=10, fontweight='bold')

# 5. Trade Frequency Comparison
ax5 = plt.subplot(2, 3, 5)
trades = [original['trades'], markov['trades']]
bars5 = ax5.bar(strategies, trades, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax5.set_ylabel('Number of Trades', fontsize=11, fontweight='bold')
ax5.set_title('Total Trades (2 Years)', fontsize=12, fontweight='bold')
ax5.grid(axis='y', alpha=0.3, linestyle='--')

for i, (bar, val) in enumerate(zip(bars5, trades)):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(val)}',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# 6. Final Capital Comparison (from €1,000)
ax6 = plt.subplot(2, 3, 6)
final_capitals = [original['final_capital'], markov['final_capital']]
bars6 = ax6.bar(strategies, final_capitals, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax6.set_ylabel('Final Capital (€)', fontsize=11, fontweight='bold')
ax6.set_title('Final Capital (from €1,000)', fontsize=12, fontweight='bold')
ax6.set_yscale('log')  # Log scale for better visualization
ax6.grid(axis='y', alpha=0.3, linestyle='--')

for i, (bar, val) in enumerate(zip(bars6, final_capitals)):
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
             f'€{val:,.0f}',
             ha='center', va='bottom', fontsize=9, fontweight='bold', rotation=0)

# Add summary text box
summary_text = f"""
Summary:
• Original: {original['return']:,.0f}% return, {original['win_rate']:.2f}% win rate
• Markov: {markov['return']:,.0f}% return, {markov['win_rate']:.2f}% win rate
• Original has better risk metrics (win rate, PF, drawdown)
• Markov has higher absolute returns
"""

fig.text(0.5, 0.02, summary_text, ha='center', fontsize=10, 
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout(rect=[0, 0.05, 1, 0.97])
output_file = 'strategy_comparison.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✅ Plot saved as '{output_file}'")
plt.close()  # Close to free memory

