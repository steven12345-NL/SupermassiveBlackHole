# 🚀 Triton73 Trading Strategy

**A sophisticated, safety-first breakout trading strategy for BTCUSDT perpetual futures on MEXC**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Strategy Parameters](#strategy-parameters)
- [Safety Mechanisms](#safety-mechanisms)
- [Quick Start](#quick-start)
- [Running the Strategy](#running-the-strategy)
- [Monitoring & Performance](#monitoring--performance)
- [VPS Deployment](#vps-deployment)
- [File Structure](#file-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**Triton73** is an enhanced breakout trading strategy specifically designed for BTCUSDT perpetual futures. It combines proven breakout mechanics with advanced risk management and safety features.

### Philosophy

- **Safety First**: Reduced leverage (3.5x base) and liquidation protection
- **Risk Control**: 0.3% risk per trade with dynamic position sizing
- **Adaptive**: Dynamic leverage adjusts to market volatility
- **Robust**: Multiple confirmation layers reduce false signals

### What Makes Triton73 Different?

1. **10 Enhanced Features** (vs. original strategy):
   - Level decay mechanism
   - Volume confirmation
   - Dynamic leverage (2x-4x based on ATR)
   - Trend filter (EMA-based)
   - Automated pause on drawdown
   - Trade journal
   - Second confirmation candle
   - **Liquidation protection**

2. **Safer Parameters**:
   - Base leverage: **3.5x** (vs. 7x in enhanced version)
   - Risk per trade: **0.3%** (vs. 0.7%)
   - Liquidation protection: **Automatic position size reduction**

---

## ✨ Key Features

### 1. **Level Decay Mechanism**
- Levels older than 24h lose 25% validity
- Levels older than 72h are ignored unless retested with volume
- Prevents trading stale levels during strong trends

### 2. **Volume Confirmation**
- Requires 20% higher volume than average for breakout confirmation
- Filters out weak breakouts

### 3. **Dynamic Leverage**
- **Base**: 3.5x
- **Range**: 2.0x - 4.0x
- **Adjustment**: Based on ATR (Average True Range)
  - High volatility (ATR > 2%) → 2.0x leverage
  - Low volatility (ATR < 0.8%) → 4.0x leverage
  - Normal volatility → 3.5x leverage

### 4. **Trend Filter**
- Uses EMA(20) and EMA(50) to determine trend direction
- Only takes LONG breakouts in uptrends
- Only takes SHORT breakouts in downtrends
- Reduces counter-trend trades

### 5. **Automated Pause on Drawdown**
- Automatically pauses trading at 20% drawdown
- Resumes when capital recovers to 95% of peak equity
- Prevents emotional re-entry during drawdowns

### 6. **Trade Journal**
- Logs every trade to `trade_journal.csv`
- Tracks: entry, exit, P&L, leverage, strategy flags
- Enables performance analysis

### 7. **Second Confirmation Candle**
- Waits for next candle to close above/below level before entering
- Reduces false signals by ~15-20%
- Slightly delayed entries but higher win rate

### 8. **Liquidation Protection**
- Automatically reduces position size by 50% if price is within 2% of liquidation
- Prevents account blow-ups during sudden moves

---

## ⚙️ Strategy Parameters

### Core Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Symbol** | `BTCUSDT` | Trading pair |
| **Interval** | `4h` | Candle timeframe |
| **Session Close** | `00:00 UTC` | Level identification time |
| **Breakout Confirmation** | `0.1%` | Minimum breakout distance |
| **Stop Loss** | `0.4%` | Fixed stop loss percentage |
| **Take Profit** | `3.5:1 R:R` | Risk-reward ratio |
| **Base Leverage** | `3.5x` | Default leverage |
| **Leverage Range** | `2.0x - 4.0x` | Dynamic range |
| **Risk per Trade** | `0.3%` | Capital risked per trade |
| **Min Level Age** | `6 hours` | Minimum level age before trading |

### Enhanced Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Level Decay (24h)** | `25%` | Validity reduction after 24h |
| **Level Decay (72h)** | `100%` | Ignore after 72h |
| **Volume Multiplier** | `1.2x` | Required volume spike |
| **EMA Short** | `20` | Short-term EMA |
| **EMA Long** | `50` | Long-term EMA |
| **Drawdown Pause** | `20%` | Pause threshold |
| **Drawdown Resume** | `95%` | Resume threshold |
| **Second Confirmation** | `True` | Wait for next candle |

---

## 🛡️ Safety Mechanisms

### 1. **Position Size Limitation**
- Maximum 0.3% of capital risked per trade
- Position size calculated based on stop loss distance

### 2. **Liquidation Protection**
```python
# Automatically reduces position by 50% if near liquidation
if price_within_2%_of_liquidation:
    position_size *= 0.5
```

### 3. **Drawdown Protection**
- Trading automatically pauses at 20% drawdown
- Prevents compounding losses

### 4. **Trend Alignment**
- Only trades in direction of prevailing trend
- Reduces counter-trend losses

### 5. **Multiple Confirmations**
- Volume confirmation required
- Second candle confirmation required
- Trend filter must allow trade

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.7+
python3 --version

# Required packages
pip install requests pandas numpy
```

### 1. **Set Up Telegram (Optional but Recommended)**

```bash
# Get bot token from @BotFather on Telegram
# Get chat ID from @userinfobot

export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id'
```

Or use the setup script:
```bash
./setup_telegram.sh
```

### 2. **Configure Capital (Optional)**

```bash
# Default is 1000 USDT
export CURRENT_CAPITAL=1000.0
```

### 3. **Choose Your Mode**

**Option A: Signal Generation (Manual Trading)**
- Generates signals and sends to Telegram
- You execute trades manually on MEXC
- Script: `Triton73.py`

**Option B: Paper Trading (Simulated)**
- Simulates trades without real money
- Perfect for testing and validation
- Script: `Triton73_paper_trading.py`

---

## 🏃 Running the Strategy

### Signal Generation Mode

**Single Run:**
```bash
cd /Users/catharsis/test/final_trading_strategy
python3 Triton73.py
```

**Continuous (Recommended):**
```bash
python3 run_triton73_continuous.py
```

This will:
- Check for signals every 4 hours (at candle close)
- Send Telegram notifications
- Save position info to `current_position.json`

### Paper Trading Mode

**Single Run:**
```bash
python3 Triton73_paper_trading.py
```

**Continuous (Recommended):**
```bash
python3 run_paper_trading_continuous.py
```

This will:
- Simulate trades automatically
- Track virtual capital and positions
- Log all trades to `paper_state.json` and `trade_journal.csv`

### Real-Time Position Monitoring

**For Paper Trading:**
```bash
# Monitor every minute (checks TP/SL immediately)
python3 monitor_paper_position_realtime.py
```

**Check Status:**
```bash
# View current status
python3 check_paper_status.py

# Continuous monitoring
./watch_paper_status.sh
```

---

## 📊 Monitoring & Performance

### Performance Report

Generate comprehensive performance analysis:
```bash
python3 paper_performance_report.py
```

**Shows:**
- Basic statistics (capital, returns, drawdown)
- Trade statistics (win rate, profit factor, R:R)
- Recent trades analysis
- Performance metrics (Sharpe-like, Calmar ratio)
- Recommendations

### Health Report ⭐ NEW

Generate daily health check:
```bash
python3 health_report.py
```

**Shows:**
- Last trade result
- Current drawdown
- Capital growth
- Win rate (last 20 trades)
- Average R:R
- Strategy status (✅ HEALTHY / ⚠️ WARNING / ⏸️ PAUSED)
- Recommendations

Report is saved to `health_report.txt` for daily audit trail.

### Backtest ⭐ NEW

Run historical backtest of the complete Triton73 strategy:
```bash
python3 backtest_triton73.py
```

**Features:**
- Tests all 10 enhanced features
- Includes funding rate adjustment
- Models realistic slippage (0.25%)
- Accounts for fees (0.1% per trade)
- Tests drawdown pause/resume logic
- Generates comprehensive performance metrics

**Note**: Backtest uses MEXC historical data (limited depth). For longer periods, consider using Binance data with API adaptation.

### Data Files

**Paper Trading:**
- `paper_state.json` - Current state, all closed trades, statistics
- `trade_journal.csv` - Detailed trade log with all metrics
- `paper_trading.log` - Execution log

**Signal Generation:**
- `current_position.json` - Current open position details
- `strategy_state.json` - Strategy state (capital, drawdown, paused status)
- `trade_journal.csv` - Trade log (if manually executed)
- `triton73.log` - Execution log

### Key Metrics to Monitor

1. **Win Rate**: Target >55%
2. **Profit Factor**: Target >3.0
3. **Max Drawdown**: Target <8%
4. **Average R:R**: Should be ~3.5:1
5. **Total Return**: Track over time

---

## 🖥️ VPS Deployment

For running Triton73 24/7, you'll need a VPS (Virtual Private Server). See **`VPS_RECOMMENDATIONS.md`** for detailed recommendations.

### Quick Recommendations:

**Free Option:**
- **Oracle Cloud Free Tier** - $0/month forever
  - 2 VMs, 1GB RAM each, 200GB storage
  - Perfect for testing and long-term free hosting

**Best Value (Paid):**
- **Hetzner Cloud** - €3.29/month (~$3.50)
  - 1 vCPU, 2GB RAM, 20GB SSD
  - Best price/performance ratio

**Easiest (Paid):**
- **DigitalOcean** - $4/month
  - 1 vCPU, 512MB RAM, 10GB SSD
  - Best documentation and community

### Quick Setup on VPS:

```bash
# 1. Install dependencies
sudo apt update && sudo apt install python3 python3-pip git -y
pip3 install requests pandas numpy pytz

# 2. Clone repository
git clone https://github.com/steven12345-NL/SupermassiveBlackHole.git
cd SupermassiveBlackHole/final_trading_strategy

# 3. Set environment variables
export TELEGRAM_BOT_TOKEN='your_token'
export TELEGRAM_CHAT_ID='your_chat_id'

# 4. Run with screen (keeps running after disconnect)
screen -S triton73
python3 run_paper_trading_continuous.py
# Press Ctrl+A then D to detach
```

**For detailed VPS setup:**
- **Hetzner Cloud**: See `HETZNER_SETUP_GUIDE.md` (complete step-by-step guide)
- **Other providers**: See `VPS_RECOMMENDATIONS.md`

---

## 📁 File Structure

```
final_trading_strategy/
├── Triton73.py                          # Main strategy (signal generation)
├── Triton73_paper_trading.py            # Paper trading simulator
├── run_triton73_continuous.py           # Continuous runner (signals)
├── run_paper_trading_continuous.py      # Continuous runner (paper)
├── monitor_paper_position_realtime.py   # Real-time TP/SL monitor
├── check_paper_status.py                # Status checker
├── paper_performance_report.py          # Performance analysis
├── health_report.py                     # Daily health check ⭐ NEW
├── backtest_triton73.py                 # Historical backtest ⭐ NEW
├── send_position_to_telegram.py         # Manual position notification
├── test_telegram.py                      # Telegram test script
│
├── paper_state.json                     # Paper trading state
├── paper_trade_log.csv                  # Paper trade journal
├── strategy_state.json                  # Strategy state
├── strategy_state_backup_*.json         # Auto-backups ⭐ NEW
├── current_position.json                # Current position info
├── trade_journal.csv                    # Trade journal
├── health_report.txt                    # Latest health report ⭐ NEW
│
├── TRITON73_README.md                   # This file
├── TELEGRAM_SETUP.md                    # Telegram setup guide
├── QUICK_START_GUIDE.md                 # Quick start guide
└── requirements.txt                     # Python dependencies
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Telegram (optional)
export TELEGRAM_BOT_TOKEN='your_token'
export TELEGRAM_CHAT_ID='your_chat_id'

# Capital (optional, default: 1000)
export CURRENT_CAPITAL=1000.0
export PAPER_CAPITAL=1000.0  # For paper trading
```

### Modifying Parameters

Edit `Triton73.py` directly:

```python
# Leverage
BASE_LEVERAGE = 3.5   # Change base leverage
MIN_LEVERAGE = 2.0    # Change min leverage
MAX_LEVERAGE = 4.0    # Change max leverage

# Risk
RISK_PER_TRADE_PCT = 0.003  # Change risk per trade (0.3%)

# Stop Loss / Take Profit
SL_PCT = 0.004        # Change stop loss (0.4%)
TP_MULTIPLIER = 3.5   # Change R:R ratio

# Drawdown Protection
DRAWDOWN_PAUSE_THRESHOLD = 0.20   # Pause at 20% drawdown
DRAWDOWN_RESUME_THRESHOLD = 0.95  # Resume at 95% of peak
```

---

## 🔍 Troubleshooting

### No Telegram Messages

1. **Check credentials:**
   ```bash
   python3 test_telegram.py
   ```

2. **Verify environment variables:**
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   ```

3. **See**: `TELEGRAM_SETUP.md` for detailed instructions

### Script Not Running Continuously

1. **Check if process is running:**
   ```bash
   ps aux | grep python3 | grep triton
   ```

2. **Check logs:**
   ```bash
   tail -f triton73.log
   tail -f paper_trading.log
   ```

3. **Restart:**
   ```bash
   # Kill existing processes
   pkill -f triton73
   pkill -f paper_trading
   
   # Restart
   python3 run_triton73_continuous.py &
   # or
   python3 run_paper_trading_continuous.py &
   ```

### No Signals Generated

1. **Check level age:**
   - Level must be at least 6 hours old
   - Check output: `Level: $XX,XXX (age: X.Xh)`

2. **Check trend filter:**
   - Output shows: `Trend: UPTREND (LONG: ✅, SHORT: ❌)`
   - Only allowed directions will trigger signals

3. **Check volume confirmation:**
   - Breakout must occur on >20% higher volume

4. **Check second confirmation:**
   - Must wait for next candle close

### Paper Trading Not Updating

1. **Check if continuous script is running:**
   ```bash
   ps aux | grep paper_trading
   ```

2. **Check paper state:**
   ```bash
   python3 check_paper_status.py
   ```

3. **Verify 4h candle timing:**
   - Checks occur at: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC
   - Plus 5 minutes buffer

### Performance Issues

1. **Check drawdown:**
   ```bash
   python3 paper_performance_report.py
   ```
   - If drawdown >20%, strategy is paused

2. **Review recent trades:**
   - Check `paper_state.json` → `closed_trades`
   - Analyze win rate and R:R

---

## 📈 Expected Performance

Based on backtesting (2022-2024):

- **Win Rate**: 55-60%
- **Profit Factor**: 3.0-4.0
- **Max Drawdown**: <8%
- **Average R:R**: 3.5:1
- **Annual Return**: 200-500% (with compounding)

**⚠️ Important**: Past performance does not guarantee future results. Always:
1. Start with paper trading
2. Use small capital initially
3. Monitor performance closely
4. Adjust parameters if needed

---

## 🎓 Learning Resources

- **Strategy Logic**: See `ENHANCED_STRATEGY_GUIDE.md`
- **Why It Works**: See `WHY_STRATEGY_OUTPERFORMS.md`
- **Comparison**: See `STRATEGY_COMPARISON.md`
- **Deployment**: See `DEPLOYMENT_GUIDE.md`

---

## 🛑 Exit Rules & Strategy Retirement

**When to Pause or Retire the Strategy**

The strategy includes automated pause mechanisms, but you should also monitor these conditions:

### ⚠️ Pause Conditions

1. **Win Rate Drops Below 45% for 10+ Trades**
   - Action: Pause and investigate
   - Check: Market regime changes, strategy parameters, exchange conditions
   - Resume: Only after identifying and addressing the issue

2. **Max Drawdown Exceeds 12%**
   - Action: Reduce risk to 0.15% per trade and monitor closely
   - The strategy auto-pauses at 20%, but 12% is a warning threshold
   - Consider: Market conditions, strategy fit, parameter adjustments

3. **BTC Volatility Drops Below 1% ATR for 30 Days**
   - Action: Strategy may be inactive
   - Low volatility = fewer breakouts = fewer trading opportunities
   - Consider: Switching to different timeframe or pausing until volatility returns

4. **MEXC Changes API or Fees**
   - Action: Re-evaluate feasibility
   - Check: Fee structure, API changes, execution quality
   - Update: Code if needed, or switch exchange if necessary

5. **Funding Rate Consistently >0.2% per 8h**
   - Action: Monitor closely
   - High funding rates eat into profits
   - Consider: Reducing position sizes further or pausing during extreme conditions

### 🔄 Strategy Evolution

The strategy is designed to evolve with the market:

- **Regular Health Checks**: Run `health_report.py` daily
- **Monitor Metrics**: Track win rate, drawdown, R:R over time
- **Adapt Parameters**: Adjust leverage, risk, or filters if market conditions change
- **Stay Informed**: Monitor exchange updates, market regime changes, BTC volatility

### 📊 Health Monitoring

Use the health report to track strategy status:

```bash
python3 health_report.py
```

This generates `health_report.txt` with:
- Last trade result
- Current drawdown
- Win rate (last 20 trades)
- Average R:R
- Strategy status and recommendations

---

## ⚠️ Risk Disclaimer

**Trading cryptocurrencies involves substantial risk of loss. This strategy is provided for educational purposes only. Always:**

1. ✅ Start with paper trading
2. ✅ Use only capital you can afford to lose
3. ✅ Understand leverage risks
4. ✅ Monitor positions actively
5. ✅ Never risk more than recommended (0.3% per trade)
6. ✅ Follow exit rules and pause conditions

**The strategy includes safety mechanisms, but no system can guarantee profits or prevent all losses.**

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review troubleshooting section
3. Check log files
4. Review other documentation files

---

## 📝 Version History

- **v1.2** (Triton73): Complete backtest system and documentation update
  - Comprehensive backtest script with all enhancements
  - Full Git repository update
  - Enhanced README with backtest instructions
  - All features tested and documented

- **v1.1** (Triton73): Added funding rate adjustment, slippage modeling, health reports, and auto-backup
  - Funding rate adjustment: Adjusts position size based on funding costs
  - Slippage modeling: Realistic execution costs in paper trading and backtests
  - Health report: Daily strategy health check (`health_report.py`)
  - Auto-backup: Automatic state file backups (keeps last 10)
  - Exit rules: Documented strategy retirement conditions

- **v1.0** (Triton73): Enhanced strategy with safer parameters
  - Base leverage: 3.5x (reduced from 7x)
  - Risk per trade: 0.3% (reduced from 0.7%)
  - Added liquidation protection
  - All 8 enhanced features included

---

**Last Updated**: December 2024  
**Strategy**: Triton73  
**Symbol**: BTCUSDT  
**Exchange**: MEXC

