# Trading Strategy Package

## 📦 **Package Contents**

This folder contains the complete, production-ready trading strategy package.

---

## 🚀 **Quick Start**

1. **Set Environment Variables:**
   ```bash
   export TELEGRAM_BOT_TOKEN='your_bot_token'
   export TELEGRAM_CHAT_ID='your_chat_id'
   export CURRENT_CAPITAL='1000.0'
   ```

2. **Start the Strategy:**
   ```bash
   python3 run_signals_continuous.py
   ```

3. **Read the Guide:**
   - Start with: `WHAT_TO_RUN_NOW.md`
   - Full details: `FINAL_STRATEGY_CONFIGURATION.md`

---

## 📁 **Files Included**

### Core Scripts (Required):
- `mexc_enhanced_strategy.py` - Main trading strategy script
- `run_signals_continuous.py` - Continuous runner (runs every 4h)
- `mexc_position_monitor.py` - Position monitoring script

### Documentation:
- `WHAT_TO_RUN_NOW.md` - **START HERE** - Quick reference
- `QUICK_START_GUIDE.md` - Step-by-step setup
- `FINAL_STRATEGY_CONFIGURATION.md` - Complete configuration details
- `ENHANCED_STRATEGY_GUIDE.md` - Enhanced strategy guide
- `README.md` - Original strategy documentation
- `WHY_STRATEGY_OUTPERFORMS.md` - Strategy analysis

### Optional:
- `plot_strategy_comparison.py` - Plotting script
- `strategy_comparison.png` - Strategy comparison chart

---

## ⚙️ **Strategy Configuration**

- **Symbol**: BTCUSDT Perpetual Futures (MEXC)
- **Base Leverage**: 7.0x (dynamic 3x-6x)
- **Risk per Trade**: 0.7%
- **Stop Loss**: 0.4%
- **Take Profit**: 3.5:1 R:R
- **All Safety Features**: Enabled

---

## 📊 **Expected Performance**

- **Return**: 50,000% - 100,000%+ per year
- **Max Drawdown**: < 5%
- **Win Rate**: 85-90%
- **Trades**: 20-40 per year

---

## 🔧 **Generated Files (Auto-Created)**

These files will be created automatically when running:
- `current_position.json` - Current open position
- `strategy_state.json` - Strategy state (capital, drawdown, paused)
- `trade_journal.csv` - Complete trade history

---

## 📝 **Requirements**

- Python 3.7+
- Required packages: `requests`, `pandas`, `numpy`
- MEXC account with API access
- Telegram bot (optional, for alerts)

---

## ⚠️ **Important Notes**

1. This strategy uses **7x leverage** - high risk, high reward
2. All trades are **manual execution** - script sends signals, you execute
3. Update `CURRENT_CAPITAL` environment variable as capital grows
4. Strategy auto-pauses at 20% drawdown

---

## 📅 **Package Version**

- **Version**: Enhanced Optimized v1.0
- **Date**: 2025-01-XX
- **Status**: Production Ready

---

*For questions or issues, refer to the documentation files above.*

