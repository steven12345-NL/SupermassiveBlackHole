#!/bin/bash
# Start Enhanced Trading Strategy

echo "=========================================="
echo "Starting Enhanced BTCUSDT Trading Strategy"
echo "=========================================="
echo ""

# Kill any existing processes
echo "Stopping any existing processes..."
pkill -f "mexc_btcusdt_signals.py" 2>/dev/null
pkill -f "mexc_enhanced_strategy.py" 2>/dev/null
pkill -f "run_signals_continuous.py" 2>/dev/null
pkill -f "mexc_position_monitor.py" 2>/dev/null
sleep 2

# Check if environment variables are set
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "⚠️  WARNING: Telegram environment variables not set"
    echo "   Set them with:"
    echo "   export TELEGRAM_BOT_TOKEN='your_token'"
    echo "   export TELEGRAM_CHAT_ID='your_chat_id'"
    echo ""
fi

if [ -z "$CURRENT_CAPITAL" ]; then
    echo "⚠️  WARNING: CURRENT_CAPITAL not set, using default 1000.0"
    echo "   Set it with: export CURRENT_CAPITAL='1000.0'"
    echo ""
fi

# Start the enhanced strategy
echo "✅ Starting Enhanced Strategy..."
echo "   Script: mexc_enhanced_strategy.py"
echo "   Configuration: 7x leverage (dynamic 3x-6x), 0.7% risk"
echo "   All safety features: ENABLED"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

cd "$(dirname "$0")"
python3 run_signals_continuous.py

