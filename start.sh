#!/bin/bash

# V8 Trading Bot Startup Script
echo "🚀 Starting V8 Trading Bot System..."

# Check if Python packages are installed
if ! python3 -c "import pandas" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Start API Server in background
echo "🔧 Starting API Server on port 8000..."
python3 api_server.py &
API_PID=$!

# Wait for API server to start
sleep 3

# Start Trading Bot in background
echo "🤖 Starting Trading Bot..."
python3 live_paper_trade_v8.py &
BOT_PID=$!

# Start Next.js Dashboard
echo "📊 Starting Dashboard on port 3000..."
cd dashboard-next
npm run dev &
DASH_PID=$!

echo ""
echo "✅ All services started!"
echo "   - API Server: http://localhost:8000"
echo "   - Dashboard: http://localhost:3000"
echo "   - Trading Bot: Running in background"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $API_PID $BOT_PID $DASH_PID 2>/dev/null; exit" INT
wait
