# 🚀 V8.0 Ultra - AI-Powered Trading Bot

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()

**High-Performance Algorithmic Trading System for Nifty 50**

Achieve **158%+ returns** in 60 days with AI-driven decision making and advanced risk management.

---

## 📊 Performance

| Metric | Result |
|:-------|:-------|
| **Verified Return (60 Days)** | **+158.19%** |
| **Starting Capital** | ₹30,000 |
| **Final Balance** | ₹77,456 |
| **Win Rate** | 37.6% |
| **Total Trades** | 141 |
| **Avg Trades/Day** | 2.35 |
| **Projected Annual Return** | **~300-350%** |

---

## ✨ Key Features

### 🧠 AI-Powered Decision Making
- **Cerebras Llama 3.3 70B** evaluates every trade
- Confidence scoring (0-10) filters low-quality setups
- Only trades with AI score ≥ 8.0 are executed

### 📈 9-Indicator Technical Analysis
1. **EMA (20/50/200)** - Trend Direction
2. **Supertrend** - Dynamic Support/Resistance
3. **ADX** - Trend Strength Filter
4. **MACD** - Momentum Confirmation
5. **Volume Ratio** - Smart Money Detection
6. **VWAP** - Institutional Price Level
7. **Bollinger Bands** - Volatility Analysis
8. **RSI** - Momentum Oscillator
9. **Stochastic RSI** - Fine-tuned Momentum

### 🎯 Advanced Risk Management
- **Partial Profit Taking:** TP1 (50%) + TP2 (50%)
- **Breakeven Stop Loss:** Risk-free after TP1
- **Dynamic Position Sizing:** 6-10% based on AI confidence
- **Circuit Breakers:** Max 12 trades/day, 10% daily loss limit

### 🔄 Real-Time Execution
- **5-Minute Candles** for precise entries
- **Live Market Data** via Yahoo Finance
- **State Persistence** across restarts
- **API Dashboard** for monitoring

---

## 🛠️ Tech Stack

- **Python 3.11**
- **yfinance** - Market data
- **pandas-ta** - Technical indicators
- **Cerebras AI** - LLM decision engine
- **FastAPI** - REST API
- **Docker** - Containerization
- **Render** - Cloud deployment

---

## 📂 Project Structure

```
ultra_v8/
├── live_paper_trade_v8.py    # Main trading bot
├── api_server.py              # REST API server
├── STRATEGY_GUIDE.md          # Complete strategy documentation
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── render.yaml                # Deployment config
├── live_state.json            # Bot state (balance, trades)
├── live_trades.csv            # Trade history
└── dashboard-next/            # Next.js monitoring dashboard
```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Knnivedh/v8.git
cd v8
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:

```env
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

**Get Free API Key:** [Cerebras Cloud](https://cloud.cerebras.ai/)

### 4. Run Bot

```bash
python live_paper_trade_v8.py
```

### 5. Access Dashboard (Optional)

```bash
# Start API server
uvicorn api_server:app --host 0.0.0.0 --port 8000

# Open browser
# http://localhost:8000
```

---

## 🎓 How It Works

### Entry Logic

**Required Conditions (All 3):**
1. ✅ EMA20 > EMA50 (Uptrend)
2. ✅ Supertrend = Bullish
3. ✅ ADX ≥ 25 (Strong Trend)

**Bonus Factors (Need ≥1 More):**
- EMA50 > EMA200
- MACD > Signal
- Volume > 1.3x Average
- Price > VWAP
- Bollinger Band Position
- Stoch RSI 20-80

**Minimum Confluence:** 4 out of 9 indicators

### AI Scoring

```python
# Send signal to Cerebras AI
{
  "type": "BUY",
  "entry": 25000,
  "confluence": 6,
  "reasons": ["EMA", "Supertrend", "ADX", "MACD", "Volume", "VWAP"],
  "adx": 32.5
}

# AI Response
{
  "score": 9.2,
  "reasoning": "Strong uptrend with volume confirmation"
}

# Position Size Calculation
if score >= 9.0: risk = 10%
elif score >= 8.5: risk = 8%
elif score >= 8.0: risk = 6%
else: reject_trade
```

### Exit Strategy

1. **TP1 (2.0x ATR):**
   - Close 50% of position
   - Move stop loss to breakeven
   - Lock in profits

2. **TP2 (4.0x ATR):**
   - Close remaining 50%
   - Extended target for big wins

3. **Stop Loss:**
   - Initial: Entry ± 1.2 ATR
   - After TP1: Moved to breakeven (risk-free)

---

## 📊 Strategy Evolution

| Version | Return | Drawdown | Status |
|:--------|:-------|:---------|:-------|
| V5.0 | +305% | 53% 🔴 | Too Risky |
| V6.0 | +102% | 20% 🟢 | Safe |
| V7.0 | +130% | 22% 🟢 | Balanced |
| **V8.0** | **+158%** | **~22%** 🟢 | ✅ **Deployed** |

**V8.0 Improvements:**
- 🔺 Risk: 3-5% → **6-10%**
- 🎯 TP2: 3.0x → **4.0x** ATR
- 🧠 MACD: Added as bonus filter
- 📊 Volume: Raised to 1.3x threshold

---

## 📈 Backtest Results

**Testing Period:** 60 Days (Maximum available 5-minute data)  
**Symbol:** ^NSEI (Nifty 50)  
**Interval:** 5 Minutes

### Equity Curve

![V8 Equity Curve](docs/v8_ultra_results.png)

### Trade Distribution

- **Winners:** 53 trades (37.6%)
- **Losers:** 88 trades
- **Profit Factor:** >1.5
- **Risk/Reward:** 1:2 (TP1) and 1:4 (TP2)

---

## 🔧 Configuration

**Edit these parameters in `live_paper_trade_v8.py`:**

```python
# Strategy Parameters
MIN_AI_SCORE = 8.0          # Min AI confidence
MIN_CONFLUENCE = 4          # Min indicators required
MIN_ADX = 25                # Min trend strength
MIN_VOLUME_RATIO = 1.3      # Min volume threshold

# Risk Management
MAX_DAILY_TRADES = 12       # Max trades per day
MAX_DAILY_LOSS_PCT = 0.10   # Max 10% daily loss

# Position Sizing
# AI 9.0+: 10% risk
# AI 8.5+: 8% risk
# AI 8.0+: 6% risk
```

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t v8-trading-bot .
```

### Run Container

```bash
docker run -d \
  --name v8-bot \
  -e CEREBRAS_API_KEY=your_key_here \
  -p 8000:8000 \
  v8-trading-bot
```

---

## ☁️ Deploy to Render

1. **Fork this repository**

2. **Create New Web Service** on [Render](https://render.com)

3. **Connect GitHub repo**

4. **Add Environment Variable:**
   ```
   CEREBRAS_API_KEY = your_key_here
   ```

5. **Deploy!** 🚀

Render will auto-detect `Dockerfile` and deploy the bot.

---

## 📚 Documentation

- **[STRATEGY_GUIDE.md](STRATEGY_GUIDE.md)** - Complete strategy breakdown
- **[Walkthrough](docs/walkthrough.md)** - Development journey
- **[API Docs](http://localhost:8000/docs)** - FastAPI interactive docs

---

## ⚠️ Risk Disclaimer

**IMPORTANT:** This is an **AGGRESSIVE** trading strategy with:
- High position sizes (6-10% per trade)
- Potential for rapid gains AND losses
- Not suitable for beginners

**Recommendations:**
- ✅ Start with paper trading
- ✅ Use only risk capital
- ✅ Monitor daily for first week
- ✅ Understand all indicators before live trading

**Past performance does not guarantee future results.**

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Knnivedh/v8/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Knnivedh/v8/discussions)

---

## 🎯 Roadmap

- [ ] Multi-symbol support (BankNifty, FinNifty)
- [ ] Telegram notifications
- [ ] Advanced dashboard with charts
- [ ] Portfolio optimization
- [ ] Backtesting framework improvements

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Knnivedh/v8&type=Date)](https://star-history.com/#Knnivedh/v8&Date)

---

## 📊 Status

**Last Updated:** 2025-12-07  
**Status:** ✅ Production Ready  
**Version:** 8.0 Ultra  

---

<div align="center">

**Built with ❤️ for Indian Stock Market Traders**

[⬆ Back to Top](#-v80-ultra---ai-powered-trading-bot)

</div>
