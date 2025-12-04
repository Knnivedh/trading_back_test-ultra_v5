"""
V5.0 DASHBOARD API SERVER
Serves live trading data to the Next.js Frontend.
Run: uvicorn api_server:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import pandas as pd
import os
import yfinance as yf
from typing import Dict, Any, List

app = FastAPI()

# Enable CORS for Next.js (running on port 3000 and Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://trading-back-test-ultra-v5.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE_FILE = "live_state.json"
TRADES_FILE = "live_trades.csv"

@app.get("/")
def read_root():
    return {"status": "online", "system": "V5.0 Ultra"}

@app.get("/state")
def get_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    return {"error": "State file not found"}

@app.get("/trades")
def get_trades():
    if os.path.exists(TRADES_FILE):
        try:
            df = pd.read_csv(TRADES_FILE)
            return df.to_dict(orient="records")
        except Exception as e:
            return {"error": str(e)}
    return []

@app.get("/chart")
def get_chart_data() -> List[Dict]:
    """Fetch live chart data from Yahoo Finance with indicators"""
    try:
        df = yf.download("^NSEI", period="1d", interval="5m", progress=False)
        if df.empty:
            return []
        
        # Clean columns
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df.reset_index(inplace=True)
        
        # Calculate EMAs
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        
        # Calculate ATR for Supertrend
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(14).mean()
        
        # Supertrend
        hl2 = (df['High'] + df['Low']) / 2
        multiplier = 3
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        supertrend = pd.Series(index=df.index, dtype=float)
        for i in range(1, len(df)):
            if pd.isna(supertrend.iloc[i-1]):
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                if df['Close'].iloc[i] > supertrend.iloc[i-1]:
                    supertrend.iloc[i] = lower_band.iloc[i]
                else:
                    supertrend.iloc[i] = upper_band.iloc[i]
        
        df['Supertrend'] = supertrend
        
        # Convert to dict
        result = []
        for _, row in df.iterrows():
            result.append({
                "time": row['Datetime'].strftime('%H:%M') if 'Datetime' in row else str(row.name),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume']),
                "ema20": float(row['EMA20']) if not pd.isna(row['EMA20']) else None,
                "ema50": float(row['EMA50']) if not pd.isna(row['EMA50']) else None,
                "supertrend": float(row['Supertrend']) if not pd.isna(row['Supertrend']) else None
            })
        return result
    except Exception as e:
        print(f"Chart error: {e}")
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
