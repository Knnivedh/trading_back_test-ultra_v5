"""
V5.0 HYPER-GROWTH SYSTEM - 100% TARGET
Optimized Frequency + Aggressive Risk + AI Sniper Mode

TARGET: ₹30,000 → ₹60,000+ in 3 months
CHANGES:
- Confluence: 3/6 (was 4/6) -> More trades
- Risk: 3-6% (was 2-5%) -> Higher growth
- Targets: Volatility adjusted -> Bigger wins
"""

import pandas as pd
import numpy as np
import os
import json
from openai import OpenAI

class HyperSystemV5:
    def __init__(self, initial_capital=30000, api_key=None):
        self.initial_capital = initial_capital
        self.balance = initial_capital
        self.peak_balance = initial_capital
        self.equity_curve = [initial_capital]
        self.trades = []
        self.rejected_trades = []
        
        # Aggressive Risk Settings
        self.base_risk_pct = 3.0
        self.max_risk_pct = 6.0
        self.min_risk_pct = 2.0
        
        # Risk controls
        self.max_drawdown_pct = 10.0  # Slightly looser for growth
        self.daily_loss_limit_pct = 4.0
        self.max_trades_per_day = 4
        self.max_consecutive_losses = 4
        
        # Tracking
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        self.trades_today = 0
        self.daily_pnl = 0
        self.current_day = None
        
        # LLM Setup
        self.api_key = api_key or os.getenv('CEREBRAS_API_KEY')
        if not self.api_key:
            self.llm_enabled = False
        else:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.cerebras.ai/v1"
                )
                self.llm_enabled = True
                self.model_name = "llama-3.3-70b"
                print(f"✅ LLM Active: {self.model_name}")
            except Exception as e:
                self.llm_enabled = False
    
    def load_data(self, filepath):
        """Load and prepare data with ALL indicators"""
        # Read CSV with Datetime column
        df = pd.read_csv(filepath)
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df.set_index('Datetime', inplace=True)
        self.data = df
        
        # Core indicators
        self.data['ATR'] = self._calculate_atr()
        self.data['EMA20'] = self.data['Close'].ewm(span=20).mean()
        self.data['EMA50'] = self.data['Close'].ewm(span=50).mean()
        self.data['EMA200'] = self.data['Close'].ewm(span=200).mean()
        self.data['RSI'] = self._calculate_rsi()
        
        # Advanced indicators
        self.data = self._calculate_supertrend(self.data)
        self.data['VWAP'] = self._calculate_vwap()
        self.data = self._calculate_bollinger_bands(self.data)
        self.data['ADX'] = self._calculate_adx()
        self.data['Stoch_RSI'] = self._calculate_stochastic_rsi()
        
        # Volume
        self.data['Volume_MA'] = self.data['Volume'].rolling(20).mean()
        self.data['Volume_Ratio'] = self.data['Volume'] / (self.data['Volume_MA'] + 0.001)
        
        self.data.dropna(inplace=True)
        print(f"✅ Loaded {len(self.data)} bars with ALL indicators")
        return self
    
    def _calculate_atr(self, period=14):
        high = self.data['High']
        low = self.data['Low']
        close = self.data['Close']
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
        return tr.rolling(window=period).mean()
    
    def _calculate_rsi(self, period=14):
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 0.0001)
        return 100 - (100 / (1 + rs))
    
    def _calculate_supertrend(self, df, period=10, multiplier=3):
        hl2 = (df['High'] + df['Low']) / 2
        atr = df['ATR']
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)
        
        for i in range(1, len(df)):
            if pd.isna(supertrend.iloc[i-1]):
                supertrend.iloc[i] = lower_band.iloc[i]
                direction.iloc[i] = 1
            else:
                if df['Close'].iloc[i] > supertrend.iloc[i-1]:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 1
                else:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    direction.iloc[i] = -1
        
        df['Supertrend'] = supertrend
        df['Supertrend_Direction'] = direction
        return df
    
    def _calculate_vwap(self):
        typical_price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
        volume_sum = self.data['Volume'].cumsum()
        volume_sum = volume_sum.replace(0, 1)
        return (typical_price * self.data['Volume']).cumsum() / volume_sum
    
    def _calculate_bollinger_bands(self, df, period=20, std=2):
        sma = df['Close'].rolling(window=period).mean()
        std_dev = df['Close'].rolling(window=period).std()
        df['BB_Upper'] = sma + (std_dev * std)
        df['BB_Lower'] = sma - (std_dev * std)
        df['BB_Middle'] = sma
        return df
    
    def _calculate_adx(self, period=14):
        high = self.data['High']
        low = self.data['Low']
        close = self.data['Close']
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        tr = pd.DataFrame({'hl': high - low, 'hc': abs(high - close.shift()), 'lc': abs(low - close.shift())}).max(axis=1)
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 0.0001)
        return dx.rolling(window=period).mean()
    
    def _calculate_stochastic_rsi(self, period=14, smooth_k=3, smooth_d=3):
        rsi = self.data['RSI']
        stoch_rsi = (rsi - rsi.rolling(window=period).min()) / (rsi.rolling(window=period).max() - rsi.rolling(window=period).min() + 0.0001)
        return stoch_rsi.rolling(window=smooth_k).mean() * 100
    
    def detect_signal(self, index):
        """
        V5.0: Relaxed Confluence (3 of 6)
        """
        if index < 210: return None
        current = self.data.iloc[index]
        atr = current['ATR']
        if atr == 0 or pd.isna(atr): return None
        
        # BULLISH
        if current['Close'] > current['EMA20']:
            confirmations = 0
            reasons = []
            if (current['EMA20'] > current['EMA50'] and current['EMA50'] > current['EMA200']): confirmations += 1; reasons.append("EMA_trend")
            if current['Supertrend_Direction'] == 1: confirmations += 1; reasons.append("Supertrend_bull")
            if current['Close'] > current['VWAP']: confirmations += 1; reasons.append("Above_VWAP")
            if current['Close'] > current['BB_Middle']: confirmations += 1; reasons.append("BB_upper")
            if current['ADX'] > 20: confirmations += 1; reasons.append("Trend_strength") # Lowered ADX threshold
            if 20 < current['Stoch_RSI'] < 80: confirmations += 1; reasons.append("Stoch_RSI")
            
            if confirmations >= 3: # V5.0: 3 of 6
                entry = current['Close']
                sl = entry - atr * 1.5
                risk = entry - sl
                if risk > 0:
                    return {
                        'type': 'BUY', 'entry': entry, 'sl': sl,
                        'tp1': entry + risk * 2.0, 'tp2': entry + risk * 3.5, 'tp3': entry + risk * 5.0, # Extended targets
                        'risk': risk, 'rr': 3.5, 'confirmations': confirmations, 'reasons': reasons,
                        'trend': 'bullish', 'adx': current['ADX'], 'volume_ratio': current['Volume_Ratio']
                    }
        
        # BEARISH
        elif current['Close'] < current['EMA20']:
            confirmations = 0
            reasons = []
            if (current['EMA20'] < current['EMA50'] and current['EMA50'] < current['EMA200']): confirmations += 1; reasons.append("EMA_trend")
            if current['Supertrend_Direction'] == -1: confirmations += 1; reasons.append("Supertrend_bear")
            if current['Close'] < current['VWAP']: confirmations += 1; reasons.append("Below_VWAP")
            if current['Close'] < current['BB_Middle']: confirmations += 1; reasons.append("BB_lower")
            if current['ADX'] > 20: confirmations += 1; reasons.append("Trend_strength")
            if 20 < current['Stoch_RSI'] < 80: confirmations += 1; reasons.append("Stoch_RSI")
            
            if confirmations >= 3:
                entry = current['Close']
                sl = entry + atr * 1.5
                risk = sl - entry
                if risk > 0:
                    return {
                        'type': 'SELL', 'entry': entry, 'sl': sl,
                        'tp1': entry - risk * 2.0, 'tp2': entry - risk * 3.5, 'tp3': entry - risk * 5.0,
                        'risk': risk, 'rr': 3.5, 'confirmations': confirmations, 'reasons': reasons,
                        'trend': 'bearish', 'adx': current['ADX'], 'volume_ratio': current['Volume_Ratio']
                    }
        return None
    
    def get_ai_score(self, signal, index):
        """Simplified AI Score for speed and cost"""
        if not self.llm_enabled: return 8.0
        
        current = self.data.iloc[index]
        prompt = f"""Rate Nifty trade 0-10.
{signal['type']} @ {signal['entry']:.0f}
Conf: {signal['confirmations']}/6 ({','.join(signal['reasons'])})
ADX: {signal['adx']:.1f}, VolRatio: {signal['volume_ratio']:.1f}
Trend: {signal['trend']}

Score (0-10) based on probability? JSON: {{"score": 0-10}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=50
            )
            txt = response.choices[0].message.content
            if "{" in txt: txt = txt[txt.find("{"):txt.rfind("}")+1]
            return json.loads(txt)['score']
        except: return 7.5

    def calculate_size(self, signal, ai_score):
        """Aggressive Scaling"""
        if ai_score >= 9.0: risk_pct = 6.0
        elif ai_score >= 8.0: risk_pct = 4.5
        elif ai_score >= 7.0: risk_pct = 3.0
        else: return 0, 0 # Reject < 7.0
        
        if self.consecutive_losses >= 3: risk_pct *= 0.5
        if self.consecutive_wins >= 2: risk_pct = min(risk_pct + 1.0, 7.0)
        
        risk_amt = self.balance * (risk_pct / 100)
        qty = int(risk_amt / signal['risk'])
        return qty, risk_pct

    def backtest(self):
        print("\n🚀 V5.0 HYPER-GROWTH SYSTEM START")
        current_trade = None
        approved = 0
        
        for i in range(210, len(self.data)-5):
            try:
                row = self.data.iloc[i]
                ts = self.data.index[i]
                
                # Trade Management
                if current_trade:
                    # Trailing Stop Logic
                    if current_trade['type'] == 'BUY':
                        if row['High'] > current_trade['tp1']:
                            current_trade['sl'] = current_trade['entry_price'] # Breakeven
                        
                        if row['Low'] <= current_trade['sl']:
                            pnl = (current_trade['sl'] - current_trade['entry_price']) * current_trade['qty']
                            self._close(current_trade, pnl, 'SL')
                            current_trade = None
                        elif row['High'] >= current_trade['tp2']:
                            pnl = (current_trade['tp2'] - current_trade['entry_price']) * current_trade['qty']
                            self._close(current_trade, pnl, 'TP2')
                            current_trade = None
                    else:
                        if row['Low'] < current_trade['tp1']:
                            current_trade['sl'] = current_trade['entry_price']
                            
                        if row['High'] >= current_trade['sl']:
                            pnl = (current_trade['entry_price'] - current_trade['sl']) * current_trade['qty']
                            self._close(current_trade, pnl, 'SL')
                            current_trade = None
                        elif row['Low'] <= current_trade['tp2']:
                            pnl = (current_trade['entry_price'] - current_trade['tp2']) * current_trade['qty']
                            self._close(current_trade, pnl, 'TP2')
                            current_trade = None
                    continue
                
                # Signal
                signal = self.detect_signal(i)
                if signal:
                    ai_score = self.get_ai_score(signal, i)
                    if ai_score >= 7.0:
                        qty, risk = self.calculate_size(signal, ai_score)
                        if qty > 0:
                            current_trade = {
                                'type': signal['type'], 'entry_time': ts, 'entry_price': signal['entry'],
                                'sl': signal['sl'], 'tp1': signal['tp1'], 'tp2': signal['tp2'],
                                'qty': qty, 'ai': ai_score, 'risk': risk
                            }
                            approved += 1
                            print(f"✅ {signal['type']} @ {signal['entry']:.0f} | AI: {ai_score} | Risk: {risk}%")
            except: pass
            
        self._report()

    def _close(self, trade, pnl, reason):
        self.balance += pnl
        if pnl > 0: 
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else: 
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        self.trades.append({'pnl': pnl, 'reason': reason})
        print(f"   {'✅' if pnl>0 else '❌'} {reason}: {pnl:+.0f} | Bal: {self.balance:.0f}")

    def _report(self):
        df = pd.DataFrame(self.trades)
        if df.empty: return
        net = df['pnl'].sum()
        ret = (self.balance/self.initial_capital - 1)*100
        print(f"\n📊 RESULT: ₹{self.initial_capital} -> ₹{self.balance:.0f} ({ret:+.1f}%)")
        
        # Projection
        m3 = self.balance * (1 + ret/200)
        print(f"🔮 3M PROJECTION: ₹{m3:.0f} (+{((m3/30000)-1)*100:.1f}%)")
        
        os.makedirs('output_v5', exist_ok=True)
        df.to_csv('output_v5/trades.csv')

if __name__ == "__main__":
    s = HyperSystemV5()
    s.load_data("data_nifty_50_5m.csv")
    s.backtest()
