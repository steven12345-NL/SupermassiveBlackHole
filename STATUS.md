# Strategy Status & What to Expect

## ✅ **Current Status**

Your **Enhanced Trading Strategy** is configured and ready to run.

---

## 📅 **When Will You Get Signals?**

The strategy checks for signals **every 4 hours** at these times (UTC):
- **00:05 UTC** (after 00:00 candle close)
- **04:05 UTC** (after 04:00 candle close)
- **08:05 UTC** (after 08:00 candle close)
- **12:05 UTC** (after 12:00 candle close)
- **16:05 UTC** (after 16:00 candle close)
- **20:05 UTC** (after 20:00 candle close)

*Note: The script waits 5 minutes after candle close to ensure data is available.*

---

## 🔔 **What Happens When a Signal is Found?**

When the strategy detects a valid breakout signal, you'll receive a Telegram message with:

### Signal Information:
- **Side**: LONG or SHORT
- **Entry Price**: Exact price to enter
- **Stop Loss**: Price to exit if trade goes against you
- **Take Profit**: Price to exit when target is reached
- **Position Size**: How many units to trade
- **Leverage**: Dynamic leverage (3x-6x based on volatility)
- **Risk Amount**: Dollar amount at risk
- **Margin Required**: Capital needed for the position

### Example Telegram Message:
```
🚀 TRADING SIGNAL - BTCUSDT

📊 Signal: LONG
💰 Entry: $87,850.00
🛑 Stop Loss: $87,498.60
🎯 Take Profit: $88,904.20

📈 Position Details:
• Units: 0.0285 BTC
• Position Value: $2,503.75
• Leverage: 6.0x
• Margin Required: $417.29
• Risk Amount: $7.00 (0.7% of capital)

⏰ Entry Time: 2025-01-XX XX:XX:XX UTC
```

---

## ⚙️ **Strategy Configuration**

- **Strategy**: Enhanced Breakout
- **Base Leverage**: 7.0x (dynamically adjusts 3x-6x)
- **Risk per Trade**: 0.7% of current capital
- **Stop Loss**: 0.4% from entry
- **Take Profit**: 3.5:1 Risk/Reward ratio

### Safety Features (All Enabled):
- ✅ Trend Filter (only trade with trend)
- ✅ Volume Confirmation (20%+ volume spike)
- ✅ Second Confirmation (wait for next candle)
- ✅ Level Decay (filters stale levels)
- ✅ Dynamic Leverage (adjusts to volatility)
- ✅ Auto-Pause on 20% drawdown

---

## 📊 **What to Do When You Get a Signal**

1. **Check Telegram** for the signal message
2. **Review the details** (entry, SL, TP, position size)
3. **Open MEXC** and navigate to BTCUSDT Perpetual Futures
4. **Place the order**:
   - Side: LONG or SHORT (as indicated)
   - Entry: Use the entry price (or market if close)
   - Leverage: Set to the indicated leverage
   - Quantity: Use the position units shown
5. **Set Stop Loss** at the indicated SL price
6. **Set Take Profit** at the indicated TP price

---

## ⏰ **Next Check Time**

The strategy will automatically check at the next 4h candle close.

To see when the next check will be, check the log:
```bash
tail -f /Users/catharsis/test/final_trading_strategy/strategy.log
```

---

## 🔍 **Monitor Your Strategy**

### Check if it's running:
```bash
ps aux | grep run_signals_continuous
```

### View the log:
```bash
tail -f /Users/catharsis/test/final_trading_strategy/strategy.log
```

### Run a manual check:
```bash
cd /Users/catharsis/test/final_trading_strategy
python3 mexc_enhanced_strategy.py
```

---

## 📝 **Important Notes**

1. **Signals are not guaranteed** - The strategy only signals when all safety filters pass
2. **Manual execution** - You must execute trades manually on MEXC
3. **Capital updates** - Update `CURRENT_CAPITAL` environment variable as your capital grows
4. **Telegram required** - Make sure Telegram credentials are set for alerts

---

## 🚨 **If You Don't Get Signals**

The strategy is very selective and only signals when:
- ✅ Price breaks through a valid level
- ✅ Trend filter allows the trade
- ✅ Volume confirms the breakout
- ✅ Second confirmation candle validates
- ✅ Level is not too old (decay check)

This means you might not get signals every day. **This is normal and good** - it means the strategy is being selective and only trading high-probability setups.

---

## ✅ **You're All Set!**

The strategy is configured and will automatically check for signals every 4 hours. Just wait for Telegram notifications and execute trades when signals arrive.

*Happy trading! 🚀*

