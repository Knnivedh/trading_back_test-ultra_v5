"""
V5.0 LIVE PAPER TRADING BOT
Real-time execution of V5.0 Hyper-Growth Strategy on Nifty 50.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI
import sys

# Configuration
SYMBOL = "^NSEI"
INTERVAL = "5m"
CAPITAL = 30000
STATE_FILE = "live_state.json"
TRADES_LOG = "live_trades.csv"

class LiveBotV5:
    def __init__(self):
        self.api_key = os.getenv('CEREBRAS_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key, base_url="https://api.cerebras.ai/v1")
                print("✅ AI Connected: llama-3.3-70b")
            except: print("⚠️ AI Connection Failed")
        
        self.load_state()
    
    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                self.state = json.load(f)
            print(f"✅ State Loaded: Balance ₹{self.state['balance']:.2f}")
        else:
            self.state = {
                "balance": CAPITAL,
                "active_trade": None,
                "trades_today": 0,
                "last_trade_date": None,
                "consecutive_wins": 0,
                "consecutive_losses": 0
            }
            self.save_state()
            print(f"🆕 New Account Started: ₹{CAPITAL}")

    def save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=4)

    def log_trade(self, trade_data):
        df = pd.DataFrame([trade_data])
        header = not os.path.exists(TRADES_LOG)
        df.to_csv(TRADES_LOG, mode='a', header=header, index=False)

    def fetch_live_data(self):
        try:
            # Fetch enough data for indicators (2 days buffer)
            df = yf.download(SYMBOL, period="5d", interval=INTERVAL, progress=False)
            if df.empty: return None
            
            # Clean data
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            df.rename(columns={'Adj Close': 'Close'}, inplace=True)
            
            # Calculate Indicators (V5.0 Logic)
            # EMAs
            df['EMA20'] = df['Close'].ewm(span=20).mean()
            df['EMA50'] = df['Close'].ewm(span=50).mean()
            df['EMA200'] = df['Close'].ewm(span=200).mean()
            
            # ATR
            high, low, close = df['High'], df['Low'], df['Close']
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(14).mean()
            
            # Supertrend
            hl2 = (high + low) / 2
            multiplier = 3
            upper = hl2 + (multiplier * df['ATR'])
            lower = hl2 - (multiplier * df['ATR'])
            st = pd.Series(index=df.index, dtype=float)
            direction = pd.Series(index=df.index, dtype=int)
            
            for i in range(1, len(df)):
                if pd.isna(st.iloc[i-1]):
                    st.iloc[i] = lower.iloc[i]
                    direction.iloc[i] = 1
                else:
                    if close.iloc[i] > st.iloc[i-1]:
                        st.iloc[i] = lower.iloc[i]
                        direction.iloc[i] = 1
                    else:
                        st.iloc[i] = upper.iloc[i]
                        direction.iloc[i] = -1
            df['Supertrend'] = st
            df['Supertrend_Direction'] = direction
            
            # VWAP
            vol_sum = df['Volume'].cumsum().replace(0, 1)
            tp = (high + low + close) / 3
            df['VWAP'] = (tp * df['Volume']).cumsum() / vol_sum
            
            # Bollinger Bands
            sma = close.rolling(20).mean()
            std = close.rolling(20).std()
            df['BB_Upper'] = sma + (std * 2)
            df['BB_Lower'] = sma - (std * 2)
            df['BB_Middle'] = sma
            
            # ADX
            p_dm = high.diff()
            m_dm = -low.diff()
            p_dm[p_dm < 0] = 0
            m_dm[m_dm < 0] = 0
            p_di = 100 * (p_dm.rolling(14).mean() / df['ATR'])
            m_di = 100 * (m_dm.rolling(14).mean() / df['ATR'])
            dx = 100 * abs(p_di - m_di) / (p_di + m_di + 0.0001)
            df['ADX'] = dx.rolling(14).mean()
            
            # StochRSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss + 0.0001)
            rsi = 100 - (100 / (1 + rs))
            stoch = (rsi - rsi.rolling(14).min()) / (rsi.rolling(14).max() - rsi.rolling(14).min() + 0.0001)
            df['Stoch_RSI'] = stoch.rolling(3).mean() * 100
            
            # Volume Ratio
            df['Volume_Ratio'] = df['Volume'] / (df['Volume'].rolling(20).mean() + 0.001)
            
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def get_ai_score(self, signal):
        if not self.client: return 7.5
        
        prompt = f"""Rate Nifty trade 0-10.
Type: {signal['type']} @ {signal['entry']:.0f}
Conf: {signal['confirmations']}/6 ({','.join(signal['reasons'])})
ADX: {signal['adx']:.1f}, VolRatio: {signal['volume_ratio']:.1f}
Trend: {signal['trend']}

Score (0-10) based on probability? JSON: {{"score": 0-10}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=50
            )
            txt = response.choices[0].message.content
            if "{" in txt: txt = txt[txt.find("{"):txt.rfind("}")+1]
            return json.loads(txt)['score']
        except: return 7.5

    def check_signal(self, df):
        current = df.iloc[-1]
        prev = df.iloc[-2] # Confirm candle is closed
        
        # Logic from V5.0
        atr = current['ATR']
        if pd.isna(atr): return None
        
        # BULLISH
        if current['Close'] > current['EMA20']:
            conf = 0
            reasons = []
            if (current['EMA20'] > current['EMA50'] > current['EMA200']): conf+=1; reasons.append("EMA")
            if current['Supertrend_Direction'] == 1: conf+=1; reasons.append("Supertrend")
            if current['Close'] > current['VWAP']: conf+=1; reasons.append("VWAP")
            if current['Close'] > current['BB_Middle']: conf+=1; reasons.append("BB")
            if current['ADX'] > 20: conf+=1; reasons.append("ADX")
            if 20 < current['Stoch_RSI'] < 80: conf+=1; reasons.append("StochRSI")
            
            if conf >= 3:
                entry = current['Close']
                sl = entry - atr * 1.5
                risk = entry - sl
                return {
                    'type': 'BUY', 'entry': entry, 'sl': sl,
                    'tp1': entry + risk*2, 'tp2': entry + risk*3.5,
                    'risk': risk, 'confirmations': conf, 'reasons': reasons,
                    'trend': 'bullish', 'adx': current['ADX'], 'volume_ratio': current['Volume_Ratio']
                }

        # BEARISH
        elif current['Close'] < current['EMA20']:
            conf = 0
            reasons = []
            if (current['EMA20'] < current['EMA50'] < current['EMA200']): conf+=1; reasons.append("EMA")
            if current['Supertrend_Direction'] == -1: conf+=1; reasons.append("Supertrend")
            if current['Close'] < current['VWAP']: conf+=1; reasons.append("VWAP")
            if current['Close'] < current['BB_Middle']: conf+=1; reasons.append("BB")
            if current['ADX'] > 20: conf+=1; reasons.append("ADX")
            if 20 < current['Stoch_RSI'] < 80: conf+=1; reasons.append("StochRSI")
            
            if conf >= 3:
                entry = current['Close']
                sl = entry + atr * 1.5
                risk = sl - entry
                return {
                    'type': 'SELL', 'entry': entry, 'sl': sl,
                    'tp1': entry - risk*2, 'tp2': entry - risk*3.5,
                    'risk': risk, 'confirmations': conf, 'reasons': reasons,
                    'trend': 'bearish', 'adx': current['ADX'], 'volume_ratio': current['Volume_Ratio']
                }
        return None

    def calculate_size(self, signal, ai_score):
        if ai_score >= 9.0: risk_pct = 6.0
        elif ai_score >= 8.0: risk_pct = 4.5
        elif ai_score >= 7.0: risk_pct = 3.0
        else: return 0
        
        # Adjust for streaks
        if self.state['consecutive_losses'] >= 3: risk_pct *= 0.5
        if self.state['consecutive_wins'] >= 2: risk_pct = min(risk_pct + 1.0, 7.0)
        
        risk_amt = self.state['balance'] * (risk_pct / 100)
        qty = int(risk_amt / signal['risk'])
        return qty

    def run(self):
        print("\n🚀 V5.0 LIVE BOT STARTED")
        print(f"💰 Balance: ₹{self.state['balance']:.2f}")
        print("⏳ Waiting for next 5m candle close...")
        
        while True:
            try:
                # 1. Check Active Trade
                if self.state['active_trade']:
                    self.manage_trade()
                
                # 2. Wait for candle close (check every minute)
                now = datetime.now()
                if now.minute % 5 != 0:
                    time.sleep(30)
                    continue
                
                # 3. Fetch Data
                print(f"\n[{now.strftime('%H:%M')}] Fetching Data...")
                df = self.fetch_live_data()
                if df is None: continue
                
                current_price = float(df['Close'].iloc[-1])
                print(f"📊 Nifty: {current_price:.2f} | ADX: {df['ADX'].iloc[-1]:.1f}")
                
                # Update State with Latest Analysis for Dashboard (Always, regardless of trade status)
                self.state['last_analysis'] = {
                    "time": now.strftime('%H:%M:%S'),
                    "price": current_price,
                    "adx": float(df['ADX'].iloc[-1]),
                    "signal": "NONE",
                    "ai_score": 0,
                    "ai_reason": "Monitoring market..."
                }
                
                # 4. Check Signal (Only if no active trade)
                if not self.state['active_trade']:
                    signal = self.check_signal(df)
                    
                    if signal:
                        print(f"🔔 POTENTIAL {signal['type']} SIGNAL!")
                        ai_score = self.get_ai_score(signal)
                        print(f"🤖 AI Score: {ai_score}/10")
                        
                        self.state['last_analysis']['signal'] = signal['type']
                        self.state['last_analysis']['ai_score'] = ai_score
                        self.state['last_analysis']['ai_reason'] = f"Conf: {signal['confirmations']}/6 | {','.join(signal['reasons'])}"
                        
                        if ai_score >= 7.0:
                            qty = self.calculate_size(signal, ai_score)
                            if qty > 0:
                                self.execute_trade(signal, qty, ai_score)
                            else:
                                print("⚠️ Qty 0 (Risk too high/Capital too low)")
                        else:
                            print("❌ AI Rejected (< 7.0)")
                    else:
                        print("💤 No Signal")
                    
                    self.save_state()
                
                # Sleep to avoid double processing same candle
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot Stopped by User")
                break
            except Exception as e:
                print(f"⚠️ Error: {e}")
                time.sleep(60)

    def execute_trade(self, signal, qty, ai_score):
        trade = {
            "entry_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "type": signal['type'],
            "entry_price": signal['entry'],
            "sl": signal['sl'],
            "tp1": signal['tp1'],
            "tp2": signal['tp2'],
            "qty": qty,
            "ai_score": ai_score
        }
        self.state['active_trade'] = trade
        self.save_state()
        print(f"✅ TRADE EXECUTED: {signal['type']} {qty} Qty @ {signal['entry']:.2f}")
        print(f"   SL: {signal['sl']:.2f} | TP2: {signal['tp2']:.2f}")

    def manage_trade(self):
        # Simple management: fetch current price and check SL/TP
        df = yf.download(SYMBOL, period="1d", interval="1m", progress=False)
        if df.empty: return
        
        # Ensure scalar float
        current_price = float(df['Close'].iloc[-1])
        trade = self.state['active_trade']
        
        pnl = 0
        reason = None
        
        if trade['type'] == 'BUY':
            if current_price <= trade['sl']:
                pnl = (trade['sl'] - trade['entry_price']) * trade['qty']
                reason = "SL"
            elif current_price >= trade['tp2']:
                pnl = (trade['tp2'] - trade['entry_price']) * trade['qty']
                reason = "TP2"
        else:
            if current_price >= trade['sl']:
                pnl = (trade['entry_price'] - trade['sl']) * trade['qty']
                reason = "SL"
            elif current_price <= trade['tp2']:
                pnl = (trade['entry_price'] - trade['tp2']) * trade['qty']
                reason = "TP2"
        
        if reason:
            self.close_trade(pnl, reason, current_price)

    def close_trade(self, pnl, reason, exit_price):
        print(f"🚨 TRADE CLOSED ({reason})")
        print(f"   PnL: ₹{pnl:.2f}")
        
        self.state['balance'] += pnl
        self.state['active_trade'] = None
        
        if pnl > 0:
            self.state['consecutive_wins'] += 1
            self.state['consecutive_losses'] = 0
        else:
            self.state['consecutive_losses'] += 1
            self.state['consecutive_wins'] = 0
            
        self.save_state()
        
        # Log
        log_entry = {
            "exit_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "pnl": pnl,
            "reason": reason,
            "balance": self.state['balance']
        }
        self.log_trade(log_entry)

if __name__ == "__main__":
    bot = LiveBotV5()
    bot.run()
