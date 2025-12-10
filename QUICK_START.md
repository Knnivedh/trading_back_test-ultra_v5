# 🚀 Quick Start Guide - V8 Trading Bot

Your Cerebras API key has been configured! The system is ready to run on your local machine.

## ⚡ Run Everything (One Command)

```bash
./start.sh
```

This starts all three services:
- ✅ API Server (port 8000)
- ✅ Trading Bot (background)
- ✅ Dashboard (port 3000)

## 📋 Prerequisites Check

Before running, ensure you have:

```bash
# Check Python (need 3.11+)
python3 --version

# Check Node.js (need 18+)
node --version

# Check pip
python3 -m pip --version
```

## 🔧 First Time Setup

### 1. Install Python Dependencies

```bash
# If you have pip
pip3 install -r requirements.txt

# OR if you need to create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Dashboard Dependencies

```bash
cd dashboard-next
npm install
cd ..
```

### 3. Verify API Key

Your `.env` file is already configured with:
```
CEREBRAS_API_KEY=csk-dkrp84em2e9e64neydcmr8txdvrcrpv9ey5edkpdr6n6x3xd
```

## 🎮 Running the System

### Option A: Automated (Recommended)

```bash
chmod +x start.sh
./start.sh
```

### Option B: Manual Control

**Terminal 1 - API Server:**
```bash
python3 api_server.py
```
✅ API running at: http://localhost:8000

**Terminal 2 - Trading Bot:**
```bash
python3 live_paper_trade_v8.py
```
✅ Bot analyzing market every 5 minutes

**Terminal 3 - Dashboard:**
```bash
cd dashboard-next
npm run dev
```
✅ Dashboard at: http://localhost:3000

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | Main monitoring interface |
| **API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |

## 🔍 What You'll See

### Dashboard Features:
- 💰 Live balance and P&L tracking
- 📊 Real-time Nifty 50 chart with indicators
- 🤖 AI confidence scores (0-10)
- 📈 Active trade monitoring
- 📋 Complete trade history
- 🎯 Win rate and performance stats

### Trading Bot Behavior:
- Analyzes market every **5 minutes**
- Only trades during **market hours** (9:15 AM - 3:30 PM IST)
- Requires **AI score ≥ 8.0** to execute
- Uses **6-10% position sizing** based on confidence
- Implements **partial profit-taking** (TP1 at 2x ATR, TP2 at 4x ATR)
- Protects with **breakeven stops** after TP1

## 📊 System Status

Check if everything is running:

```bash
# Check API Server
curl http://localhost:8000

# Should return: {"status":"online","system":"V5.0 Ultra"}
```

```bash
# Check bot state
curl http://localhost:8000/state

# Should return current balance and trade status
```

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
```

### Port already in use
```bash
# Kill existing processes
lsof -ti:8000 | xargs kill -9  # API Server
lsof -ti:3000 | xargs kill -9  # Dashboard
```

### Dashboard shows "Bot Offline"
1. Ensure API server is running on port 8000
2. Check that `live_state.json` exists
3. Restart API server: `python3 api_server.py`

### No trades executing
- Market must be open (Mon-Fri, 9:15 AM - 3:30 PM IST)
- AI score must be ≥ 8.0
- Check bot terminal for analysis logs

## 📈 Expected Behavior

### First 5 Minutes:
- Bot fetches market data
- Calculates all 9 indicators
- Sends signal to AI for scoring
- Logs analysis to terminal

### If Signal Score ≥ 8.0:
- **Entry:** Bot enters position
- **Dashboard:** Shows active trade card
- **Monitoring:** Bot checks price every minute

### If Price Hits TP1 (2x ATR):
- **Action:** Closes 50% position
- **Protection:** Moves stop loss to breakeven
- **Result:** Risk-free trade

### If Price Hits TP2 (4x ATR):
- **Action:** Closes remaining 50%
- **Result:** Maximum profit captured
- **Status:** Trade appears in history

## 🎯 Next Steps

1. ✅ **Monitor First Hour**: Watch the dashboard to understand bot behavior
2. ✅ **Review AI Reasoning**: Check why trades are accepted/rejected
3. ✅ **Track Performance**: Observe win rate and P&L trends
4. ✅ **Adjust Parameters**: Modify settings in `live_paper_trade_v8.py` if needed

## 📚 Additional Resources

- **Strategy Details**: See `STRATEGY_GUIDE.md`
- **Complete Setup**: See `SETUP.md`
- **Project Overview**: See `README.md`

## ⚠️ Important Notes

- This is **paper trading** - no real money involved
- Bot only trades during **Indian market hours**
- Aggressive strategy with **6-10% position sizes**
- Maximum **12 trades per day**, max **10% daily loss**
- AI scores below 8.0 are automatically rejected

## 🔥 Ready to Trade!

Your system is configured and ready. Simply run:

```bash
./start.sh
```

Then open http://localhost:3000 in your browser!

---

**Happy Trading! 🚀📈**
