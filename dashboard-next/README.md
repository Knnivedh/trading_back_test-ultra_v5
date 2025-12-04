# V5.0 ULTRA DASHBOARD

## 🚀 QUICK START

### 1. Start the Trading Bot
```bash
cd ultra_v5
python live_paper_trade_v5.py
```

### 2. Start the API Server
```bash
cd ultra_v5
uvicorn api_server:app --reload --port 8000
```

### 3. Start the Dashboard
```bash
cd ultra_v5/dashboard-next
npm run dev
```

### 4. Open Browser
Navigate to: **http://localhost:3000**

---

## 📊 DASHBOARD FEATURES

- **Real-Time Metrics:** Balance, PnL, Active Trades
- **AI Command Center:** Live AI reasoning and scores
- **Auto-Refresh:** Updates every 2 seconds
- **Premium UI:** Dark mode with glassmorphism effects

---

## 🛠 SYSTEM ARCHITECTURE

1. **Bot** (`live_paper_trade_v5.py`): Executes trades, saves state to JSON
2. **API** (`api_server.py`): Serves data via REST endpoints
3. **UI** (`dashboard-next`): Next.js dashboard consuming the API

All 3 must be running simultaneously!
