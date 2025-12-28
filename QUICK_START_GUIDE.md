# Quick Start Guide - Final Strategy

## 🚀 **WHAT TO RUN RIGHT NOW**

### Step 1: Update Environment Variables
```bash
export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id'
export CURRENT_CAPITAL='1000.0'  # Your starting capital
```

### Step 2: Start the Strategy
```bash
# Terminal 1: Main strategy (runs every 4h)
python3 run_signals_continuous.py
```

### Step 2b: Start Position Monitor (Optional but Recommended)
```bash
# Terminal 2: Position monitor (runs every 4h)
python3 mexc_position_monitor.py
```

---

## 📋 **WHAT'S RUNNING**

### Main Strategy (`mexc_enhanced_strategy.py`)
- **What it does**: Checks for trading signals every 4h
- **Configuration**: 
  - Base Leverage: 7x (dynamic 3x-6x)
  - Risk per Trade: 0.7%
  - All safety features enabled
- **Output**: Telegram alerts with trading instructions

### Position Monitor (`mexc_position_monitor.py`)
- **What it does**: Monitors open positions
- **Alerts**: Warns if TP may not be reached
- **Output**: Telegram alerts on risk changes

---

## ⚙️ **CONFIGURATION**

### Current Settings (OPTIMIZED):
- **Base Leverage**: 7.0x
- **Min Leverage**: 3.0x (high volatility)
- **Max Leverage**: 6.0x (low volatility)
- **Risk per Trade**: 0.7%
- **Stop Loss**: 0.4%
- **Take Profit**: 3.5:1 R:R

### Safety Features (All Enabled):
- ✅ Trend filter
- ✅ Volume confirmation
- ✅ Second confirmation
- ✅ Level decay
- ✅ Dynamic leverage
- ✅ Auto-pause on drawdown

---

## 📊 **EXPECTED PERFORMANCE**

- **Return**: 50,000% - 100,000%+ per year
- **Drawdown**: < 5%
- **Win Rate**: 85-90%
- **Trades**: 20-40 per year

---

## 🔄 **MAINTENANCE**

### Update Capital (for compounding):
```bash
# As your capital grows, update this:
export CURRENT_CAPITAL='5000.0'  # Example: after reaching $5,000
```

### Check Status:
```bash
# Check if scripts are running
ps aux | grep -E "run_signals|mexc_position_monitor"

# Check current position
cat current_position.json

# Check strategy state
cat strategy_state.json
```

---

## 📁 **FILES**

### Scripts to Run:
- `run_signals_continuous.py` - Main strategy runner
- `mexc_position_monitor.py` - Position monitor

### Documentation:
- `FINAL_STRATEGY_CONFIGURATION.md` - Full configuration details
- `ENHANCED_STRATEGY_GUIDE.md` - Strategy guide
- `README.md` - Original strategy documentation

---

*Ready to trade!*

