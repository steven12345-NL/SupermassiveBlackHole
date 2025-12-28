#!/bin/bash
# Watch paper trading status (macOS compatible)
# Updates every 30 seconds

while true; do
    clear
    echo "=== Paper Trading Status (Updates every 30s, Ctrl+C to exit) ==="
    echo ""
    python3 check_paper_status.py
    echo ""
    echo "Next update in 30 seconds..."
    sleep 30
done

