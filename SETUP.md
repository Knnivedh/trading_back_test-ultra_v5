# V8 Trading Bot - Setup Guide

## Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** and npm installed
3. **Cerebras API Key** (get free at [https://cloud.cerebras.ai/](https://cloud.cerebras.ai/))

## Installation Steps

### 1. Configure Environment Variables

Edit the `.env` file and add your Cerebras API key:

```bash
CEREBRAS_API_KEY=your_actual_api_key_here
```

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Install Dashboard Dependencies

```bash
cd dashboard-next
npm install
cd ..
```

## Running the System

### Option 1: Run All Services (Recommended)

Use the automated startup script:

```bash
./start.sh
```

This will start:
- API Server on `http://localhost:8000`
- Trading Bot (running in background)
- Dashboard on `http://localhost:3000`

### Option 2: Run Services Manually

**Terminal 1 - API Server:**
```bash
python3 api_server.py
```

**Terminal 2 - Trading Bot:**
```bash
python3 live_paper_trade_v8.py
```

**Terminal 3 - Dashboard:**
```bash
cd dashboard-next
npm run dev
```

## Accessing the System

- **Dashboard:** Open [http://localhost:3000](http://localhost:3000) in your browser
- **API Docs:** Visit [http://localhost:8000/docs](http://localhost:8000/docs) for API documentation
- **API Status:** Check [http://localhost:8000](http://localhost:8000) for API health

## Understanding the Components

### 1. Trading Bot (`live_paper_trade_v8.py`)
- Fetches live market data every 5 minutes
- Analyzes 9 technical indicators
- Uses Cerebras AI to score trades (0-10)
- Executes trades with AI score ≥ 8.0
- Manages risk with partial profit-taking and breakeven stops

### 2. API Server (`api_server.py`)
- Serves trading data to the dashboard
- Endpoints:
  - `GET /` - Health check
  - `GET /state` - Current bot state and active trades
  - `GET /trades` - Trade history
  - `GET /chart` - Live chart data with indicators

### 3. Dashboard (Next.js)
- Real-time monitoring interface
- Live chart with TradingView integration
- Performance metrics and statistics
- Trade history and active positions
- Auto-refreshes every 10 seconds

## Configuration

### Trading Bot Parameters

Edit `live_paper_trade_v8.py` to customize:

```python
MIN_AI_SCORE = 8.0          # Minimum AI confidence to trade
MIN_CONFLUENCE = 4          # Minimum indicators required
MIN_ADX = 25                # Minimum trend strength
MIN_VOLUME_RATIO = 1.3      # Minimum volume threshold
MAX_DAILY_TRADES = 12       # Maximum trades per day
MAX_DAILY_LOSS_PCT = 0.10   # Maximum 10% daily loss
```

### Position Sizing

The bot automatically adjusts position size based on AI confidence:
- AI Score ≥ 9.0: Risk 10% of capital
- AI Score ≥ 8.5: Risk 8% of capital
- AI Score ≥ 8.0: Risk 6% of capital

## Troubleshooting

### Bot Not Trading
- Check if market is open (Mon-Fri, 9:15 AM - 3:30 PM IST)
- Verify CEREBRAS_API_KEY is set correctly
- Ensure internet connection for market data
- Check that AI confidence score meets minimum threshold (≥8.0)

### Dashboard Shows "Bot Offline"
- Make sure API server is running on port 8000
- Check that `live_state.json` exists
- Verify no firewall blocking localhost:8000

### API Connection Errors
- Restart the API server
- Check if port 8000 is already in use
- Ensure `.env` file is in project root

### No Trades Appearing
- The bot only trades when all conditions are met
- Market may not have suitable setups
- Check bot logs for signal analysis
- Verify ADX ≥ 25 and confluence ≥ 4 indicators

## Safety Features

1. **Paper Trading**: No real money involved - purely simulated
2. **Daily Limits**: Max 12 trades per day, max 10% daily loss
3. **AI Filter**: Only high-confidence trades (≥8.0/10) executed
4. **Risk Management**: Automatic stop losses and profit taking
5. **State Persistence**: Bot state saved to disk, survives restarts

## Performance Monitoring

The dashboard provides real-time insights:
- Current balance and P&L
- Win rate and trade statistics
- Active trade details with entry/exit levels
- AI analysis and confidence scores
- Live price chart with indicators
- Complete trade history

## Market Hours

- **Trading Days**: Monday to Friday
- **Trading Hours**: 9:15 AM - 3:30 PM IST
- **Symbol**: Nifty 50 (^NSEI)
- **Interval**: 5-minute candles

## Support

For issues or questions:
- GitHub Issues: [https://github.com/Knnivedh/v8/issues](https://github.com/Knnivedh/v8/issues)
- Documentation: See `STRATEGY_GUIDE.md` for detailed strategy info
- README: See `README.md` for project overview

## Next Steps

1. ✅ Monitor the dashboard for first 1-2 days
2. ✅ Review trade history to understand bot behavior
3. ✅ Adjust parameters based on performance
4. ✅ Consider getting a real Cerebras API key for production use
5. ✅ Review the AI reasoning for each trade decision

---

**Note**: This is an aggressive trading strategy. Start with paper trading to understand the bot's behavior before considering any real trading.
