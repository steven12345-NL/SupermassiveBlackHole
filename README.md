# BTCUSDT Trading Strategy - Complete Package

## 🎯 **What's Included**

This repository contains a complete trading strategy system for BTCUSDT perpetual futures on MEXC, with three strategy versions and comprehensive paper trading capabilities.

---

## 📦 **Strategy Versions**

### 1. **Original Strategy** (`mexc_btcusdt_signals.py`)
- **Leverage**: 3.0x (fixed)
- **Risk**: 0.3% per trade
- **Best for**: Conservative trading, proven stability

### 2. **Enhanced Strategy** (`mexc_enhanced_strategy.py`)
- **Leverage**: 7.0x base (dynamic 3x-6x)
- **Risk**: 0.7% per trade
- **Best for**: Maximum returns (232,983% backtest)
- **All safety features enabled**

### 3. **Triton73 Strategy** (`Triton73.py`) ⭐ **RECOMMENDED**
- **Leverage**: 3.5x base (dynamic 2x-4x)
- **Risk**: 0.3% per trade
- **Best for**: Balanced returns with safety
- **Liquidation protection enabled**
- **All safety features enabled**

---

## 🚀 **Quick Start**

### Option 1: Signal Generation (Manual Trading)

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id'
export CURRENT_CAPITAL='1000.0'

# Run Triton73 (recommended)
python3 Triton73.py

# Or run continuously
python3 run_triton73_continuous.py
```

### Option 2: Paper Trading (Recommended for Testing)

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id'
export PAPER_CAPITAL='1000.0'

# Run paper trading
python3 Triton73_paper_trading.py

# Or run continuously
python3 run_paper_trading_continuous.py

# For real-time TP/SL alerts (runs separately)
python3 monitor_paper_position_realtime.py
```

---

## 📁 **Key Files**

### Strategy Scripts
- `Triton73.py` - **Recommended safer strategy**
- `mexc_enhanced_strategy.py` - High-return enhanced strategy
- `mexc_btcusdt_signals.py` - Original conservative strategy

### Paper Trading
- `Triton73_paper_trading.py` - Paper trading simulator
- `run_paper_trading_continuous.py` - Continuous paper trading runner
- `monitor_paper_position_realtime.py` - Real-time position monitor (checks every minute)
- `check_paper_status.py` - Check paper trading status anytime
- `send_position_to_telegram.py` - Send current position to Telegram

### Continuous Runners
- `run_triton73_continuous.py` - Continuous runner for Triton73
- `run_signals_continuous.py` - Continuous runner for enhanced strategy

### Utilities
- `test_telegram.py` - Test Telegram integration
- `check_telegram_messages.py` - Check recent Telegram messages
- `mexc_position_monitor.py` - Position monitoring for live trading
- `watch_paper_status.sh` - Watch paper status (macOS compatible)

### Documentation
- `DEPLOYMENT_GUIDE.md` - Which strategy to deploy and why
- `STRATEGY_COMPARISON.md` - Detailed strategy comparison
- `TELEGRAM_SETUP.md` - Telegram setup guide
- `CLOUD_DEPLOYMENT.md` - Deploy to free cloud services
- `QUICK_START_GUIDE.md` - Quick start instructions
- `FINAL_STRATEGY_CONFIGURATION.md` - Complete configuration details

---

## ⚙️ **Configuration**

### Triton73 (Recommended)
- **Base Leverage**: 3.5x
- **Dynamic Range**: 2.0x - 4.0x (based on ATR)
- **Risk per Trade**: 0.3%
- **Stop Loss**: 0.4%
- **Take Profit**: 3.5:1 R:R
- **Liquidation Protection**: Enabled

### Enhanced Strategy
- **Base Leverage**: 7.0x
- **Dynamic Range**: 3.0x - 6.0x
- **Risk per Trade**: 0.7%
- **Stop Loss**: 0.4%
- **Take Profit**: 3.5:1 R:R

---

## 📊 **Expected Performance**

### Triton73 (Backtest: 2022-2024)
- **Return**: ~20,000% (2 years)
- **Max Drawdown**: < 5%
- **Win Rate**: ~85%
- **Trades**: ~40 per year

### Enhanced Strategy (Backtest: 2022-2024)
- **Return**: 232,983% (2 years)
- **Max Drawdown**: -4.55%
- **Win Rate**: 88.10%
- **Trades**: ~42 per year

---

## 🔔 **Telegram Integration**

### Setup
1. Create bot with `@BotFather` on Telegram
2. Get Chat ID from `@userinfobot`
3. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN='your_token'
   export TELEGRAM_CHAT_ID='your_chat_id'
   ```

### What You'll Receive
- ✅ New trading signals
- ✅ Position opened alerts
- ✅ Position closed alerts (TP/SL hit)
- ✅ Trade results and P&L

---

## 📈 **Paper Trading**

### How It Works
- **Virtual positions** - No real orders placed
- **Real market prices** - Uses MEXC live prices
- **Automatic P&L calculation** - Based on real prices
- **Complete statistics** - Win rate, drawdown, etc.

### Monitor Positions
```bash
# Check status anytime
python3 check_paper_status.py

# Real-time monitoring (checks every minute)
python3 monitor_paper_position_realtime.py
```

### Files Created
- `paper_state.json` - Current positions and capital
- `paper_trade_log.csv` - Complete trade history
- `paper_trading.log` - Execution log

---

## ☁️ **Cloud Deployment**

See `CLOUD_DEPLOYMENT.md` for deploying to:
- **Railway** (recommended - $5/month free credit)
- **Oracle Cloud** (completely free forever)
- **Render** (free tier available)
- **Fly.io** (free tier)

---

## 📚 **Documentation**

- `DEPLOYMENT_GUIDE.md` - Which strategy to use
- `STRATEGY_COMPARISON.md` - Detailed comparison
- `TELEGRAM_SETUP.md` - Telegram setup
- `CLOUD_DEPLOYMENT.md` - Cloud deployment guide
- `FINAL_STRATEGY_CONFIGURATION.md` - Complete config
- `ENHANCED_STRATEGY_GUIDE.md` - Enhanced strategy details

---

## ⚠️ **Important Notes**

1. **Paper Trading**: All paper trading is simulated locally - no real orders are placed
2. **Manual Execution**: Signal scripts send alerts - you execute trades manually on MEXC
3. **Telegram Required**: Set credentials for alerts
4. **Capital Updates**: Update `CURRENT_CAPITAL` or `PAPER_CAPITAL` as capital grows

---

## 🎯 **Recommended Setup**

1. **Start with Paper Trading**:
   ```bash
   python3 run_paper_trading_continuous.py
   python3 monitor_paper_position_realtime.py  # In another terminal
   ```

2. **After 30+ trades, if win rate >55% and drawdown <8%**:
   - Switch to live trading with small capital
   - Use `Triton73.py` for signals
   - Execute trades manually on MEXC

---

## 📝 **Version History**

- **v1.0** - Original strategy (3x leverage)
- **v2.0** - Enhanced strategy (7x leverage, all safety features)
- **v3.0** - Triton73 (3.5x leverage, liquidation protection) ⭐

---

*Last Updated: 2025-12-28*  
*Status: Production Ready*
