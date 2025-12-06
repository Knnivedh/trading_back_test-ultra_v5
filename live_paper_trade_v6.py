import os
import time
import json
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SYMBOL = "^NSEI"
INTERVAL = "5m"
CAPITAL = 30000
# V6.0 Parameters
MIN_AI_SCORE = 7.5
MIN_CONFLUENCE = 4
MIN_ADX = 22
MIN_VOLUME_RATIO = 1.1
MAX_DAILY_TRADES = 8
MAX_DAILY_LOSS_PCT = 0.07

class LiveBotV6:
    def __init__(self):
        self.state_file = "live_state.json"
        self.trades_file = "live_trades.csv"
        self.client = self._init_llm_client()
        self.state = self._load_state()
        self.daily_stats = self._reset_daily_stats()

    def _init_llm_client(self):
        """Initialize Cerebras LLM client"""
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            print("⚠️ CEREBRAS_API_KEY not found. AI scoring will be simulated.")
            return None
        return OpenAI(
            base_url="https://api.cerebras.ai/v1",
            api_key=api_key
        )

    def _load_state(self):
        """Load or initialize bot state"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "balance": CAPITAL,
            "active_trade": None,
            "consecutive_wins": 0,
            "consecutive_losses": 0,
            "last_update": str(datetime.now())
        }

    def _reset_daily_stats(self):
        return {
            "trades_count": 0,
            "pnl": 0,
            "date": datetime.now().date()
        }

    def save_state(self):
        """Save current state to file"""
        self.state['last_update'] = str(datetime.now())
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=4)

    def log_trade(self, trade_data):
        """Log completed trade to CSV"""
        df = pd.DataFrame([trade_data])
        if not os.path.exists(self.trades_file):
            df.to_csv(self.trades_file, index=False)
        else:
            df.to_csv(self.trades_file, mode='a', header=False, index=False)

    def fetch_data(self):
        """Fetch latest market data"""
        try:
            df = yf.download(SYMBOL, period="5d", interval=INTERVAL, progress=False)
            if df.empty:
                return None
            
            # Clean columns
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            df.reset_index(inplace=True)
            
            # Calculate Indicators
            # EMAs
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
            
            # ATR
            df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
            
            # ADX
            adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            if adx is not None:
                df['ADX'] = adx['ADX_14']
            
            # VWAP
            df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
            
            # Bollinger Bands
            bb = ta.bbands(df['Close'], length=20, std=2)
            if bb is not None:
                df['BB_LOWER'] = bb['BBL_20_2.0']
                df['BB_MID'] = bb['BBM_20_2.0']
                df['BB_UPPER'] = bb['BBU_20_2.0']
            
            # Supertrend
            st = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
            if st is not None:
                df['Supertrend_Direction'] = st['SUPERTd_10_3.0']
            
            # RSI & Stoch RSI
            df['RSI'] = ta.rsi(df['Close'], length=14)
            stoch = ta.stochrsi(df['Close'], length=14, rsi_length=14, k=3, d=3)
            if stoch is not None:
                df['Stoch_RSI'] = stoch['STOCHRSIk_14_14_3_3']
            
            # Volume Ratio
            df['Volume_Ratio'] = df['Volume'] / (df['Volume'].rolling(20).mean() + 1)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def get_ai_score(self, signal):
        """Get AI confidence score from Cerebras"""
        if not self.client:
            # Simulation fallback
            score = 5.0 + (signal['confluence'] * 0.7)
            if signal.get('adx', 0) > 25: score += 1.0
            return min(9.5, score)

        prompt = f"""
        Analyze this Nifty 50 trade setup (V6.0 Strategy):
        Type: {signal['type']} @ {signal['entry']:.2f}
        Confluence: {signal['confluence']}/9 factors
        Reasons: {', '.join(signal['reasons'])}
        ADX: {signal.get('adx', 0):.1f} (Trend Strength)
        Volume Ratio: {signal.get('volume_ratio', 0):.1f}x
        
        Rate confidence 0-10. Be strict. >8.0 requires strong trend & volume.
        Return JSON: {{"score": float, "reasoning": "short explanation"}}
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            content = json.loads(response.choices[0].message.content)
            return content.get('score', 5.0), content.get('reasoning', 'No reasoning')
        except Exception as e:
            print(f"AI Error: {e}")
            return 7.5, "AI Error - Default Score"

    def check_signal(self, df):
        """V6.0 Signal Detection Logic"""
        current = df.iloc[-1]
        
        if pd.isna(current['ATR']) or current['ATR'] <= 0:
            return None
            
        price = current['Close']
        
        # BULLISH
        if price > current['EMA20']:
            confluence = 0
            reasons = []
            
            # REQUIRED: EMA20 > EMA50
            if not (current['EMA20'] > current['EMA50']): return None
            confluence += 1; reasons.append("EMA")
            
            # Bonus: EMA50 > EMA200
            if not pd.isna(current['EMA200']) and current['EMA50'] > current['EMA200']:
                confluence += 1; reasons.append("EMA200")
            
            # REQUIRED: Supertrend
            if current['Supertrend_Direction'] != 1: return None
            confluence += 1; reasons.append("Supertrend")
            
            # REQUIRED: ADX
            if pd.isna(current['ADX']) or current['ADX'] < MIN_ADX: return None
            confluence += 1; reasons.append("ADX")
            
            # Bonus: Volume
            if current['Volume_Ratio'] > MIN_VOLUME_RATIO:
                confluence += 1; reasons.append("Volume")
                
            # Bonus: VWAP
            if price > current['VWAP']:
                confluence += 1; reasons.append("VWAP")
                
            # Bonus: BB
            if current['BB_LOWER'] < price < current['BB_MID']:
                confluence += 1; reasons.append("BB")
                
            # Bonus: StochRSI
            if 20 < current['Stoch_RSI'] < 80:
                confluence += 1; reasons.append("StochRSI")
            
            if confluence >= MIN_CONFLUENCE:
                entry = price
                sl = entry - current['ATR'] * 1.2
                risk = entry - sl
                return {
                    'type': 'BUY',
                    'entry': entry,
                    'sl': sl,
                    'tp1': entry + risk * 2.0,
                    'tp2': entry + risk * 3.0,
                    'risk': risk,
                    'confluence': confluence,
                    'reasons': reasons,
                    'adx': current['ADX'],
                    'volume_ratio': current['Volume_Ratio']
                }

        # BEARISH
        elif price < current['EMA20']:
            confluence = 0
            reasons = []
            
            # REQUIRED: EMA20 < EMA50
            if not (current['EMA20'] < current['EMA50']): return None
            confluence += 1; reasons.append("EMA")
            
            # Bonus: EMA50 < EMA200
            if not pd.isna(current['EMA200']) and current['EMA50'] < current['EMA200']:
                confluence += 1; reasons.append("EMA200")
            
            # REQUIRED: Supertrend
            if current['Supertrend_Direction'] != -1: return None
            confluence += 1; reasons.append("Supertrend")
            
            # REQUIRED: ADX
            if pd.isna(current['ADX']) or current['ADX'] < MIN_ADX: return None
            confluence += 1; reasons.append("ADX")
            
            # Bonus: Volume
            if current['Volume_Ratio'] > MIN_VOLUME_RATIO:
                confluence += 1; reasons.append("Volume")
                
            # Bonus: VWAP
            if price < current['VWAP']:
                confluence += 1; reasons.append("VWAP")
                
            # Bonus: BB
            if current['BB_UPPER'] > price > current['BB_MID']:
                confluence += 1; reasons.append("BB")
                
            # Bonus: StochRSI
            if 20 < current['Stoch_RSI'] < 80:
                confluence += 1; reasons.append("StochRSI")
            
            if confluence >= MIN_CONFLUENCE:
                entry = price
                sl = entry + current['ATR'] * 1.2
                risk = sl - entry
                return {
                    'type': 'SELL',
                    'entry': entry,
                    'sl': sl,
                    'tp1': entry - risk * 2.0,
                    'tp2': entry - risk * 3.0,
                    'risk': risk,
                    'confluence': confluence,
                    'reasons': reasons,
                    'adx': current['ADX'],
                    'volume_ratio': current['Volume_Ratio']
                }
        
        return None

    def calculate_qty(self, signal, ai_score):
        """V6.0 Position Sizing"""
        if ai_score >= 9.0: risk_pct = 4.0
        elif ai_score >= 8.5: risk_pct = 3.0
        elif ai_score >= 7.5: risk_pct = 2.0
        else: return 0
        
        # Streak adjustments
        if self.state['consecutive_losses'] >= 3: risk_pct *= 0.5
        if self.state['consecutive_wins'] >= 2: risk_pct = min(risk_pct + 0.5, 5.0)
        
        risk_amt = self.state['balance'] * (risk_pct / 100)
        return int(risk_amt / signal['risk'])

    def execute_trade(self, signal, qty, ai_score, reasoning):
        """Execute and record trade"""
        self.state['active_trade'] = {
            "entry_time": str(datetime.now()),
            "type": signal['type'],
            "entry": signal['entry'],
            "sl": signal['sl'],
            "tp1": signal['tp1'],
            "tp2": signal['tp2'],
            "qty": qty,
            "original_qty": qty,
            "tp1_hit": False,
            "ai_score": ai_score,
            "ai_reasoning": reasoning
        }
        self.save_state()
        print(f"🚀 TRADE EXECUTED: {signal['type']} {qty} Qty @ {signal['entry']:.2f}")

    def manage_trade(self, current_price, high, low):
        """Manage active trade with TP1 and Trailing SL"""
        trade = self.state['active_trade']
        if not trade: return

        exit_reason = None
        pnl = 0
        
        if trade['type'] == 'BUY':
            # Check TP1
            if not trade['tp1_hit'] and high >= trade['tp1']:
                # Close 50%
                half_qty = trade['original_qty'] // 2
                partial_pnl = (trade['tp1'] - trade['entry']) * half_qty
                
                self.state['balance'] += partial_pnl
                self.daily_stats['pnl'] += partial_pnl
                
                trade['tp1_hit'] = True
                trade['qty'] -= half_qty
                trade['sl'] = trade['entry'] # Move SL to Breakeven
                self.save_state()
                print(f"💰 TP1 HIT! Secured ₹{partial_pnl:.2f}, SL moved to BE")
                
            # Check SL
            if low <= trade['sl']:
                exit_reason = "SL"
                exit_price = trade['sl']
            # Check TP2
            elif high >= trade['tp2']:
                exit_reason = "TP2"
                exit_price = trade['tp2']
                
        elif trade['type'] == 'SELL':
            # Check TP1
            if not trade['tp1_hit'] and low <= trade['tp1']:
                # Close 50%
                half_qty = trade['original_qty'] // 2
                partial_pnl = (trade['entry'] - trade['tp1']) * half_qty
                
                self.state['balance'] += partial_pnl
                self.daily_stats['pnl'] += partial_pnl
                
                trade['tp1_hit'] = True
                trade['qty'] -= half_qty
                trade['sl'] = trade['entry'] # Move SL to Breakeven
                self.save_state()
                print(f"💰 TP1 HIT! Secured ₹{partial_pnl:.2f}, SL moved to BE")
                
            # Check SL
            if high >= trade['sl']:
                exit_reason = "SL"
                exit_price = trade['sl']
            # Check TP2
            elif low <= trade['tp2']:
                exit_reason = "TP2"
                exit_price = trade['tp2']

        if exit_reason:
            # Close remaining position
            if trade['type'] == 'BUY':
                pnl = (exit_price - trade['entry']) * trade['qty']
            else:
                pnl = (trade['entry'] - exit_price) * trade['qty']
            
            self.state['balance'] += pnl
            self.daily_stats['pnl'] += pnl
            self.daily_stats['trades_count'] += 1
            
            # Update streaks
            total_trade_pnl = pnl
            if trade['tp1_hit']:
                # Add previous partial profit for streak calculation logic
                # (Actual balance already updated)
                pass
            
            if total_trade_pnl > 0:
                self.state['consecutive_wins'] += 1
                self.state['consecutive_losses'] = 0
            else:
                self.state['consecutive_losses'] += 1
                self.state['consecutive_wins'] = 0
            
            # Log trade
            self.log_trade({
                "exit_time": str(datetime.now()),
                "type": trade['type'],
                "pnl": total_trade_pnl,
                "reason": exit_reason,
                "balance": self.state['balance']
            })
            
            self.state['active_trade'] = None
            self.save_state()
            print(f"🏁 TRADE CLOSED ({exit_reason}): PnL ₹{pnl:.2f}")

    def run(self):
        print("🤖 V6.0 LIVE BOT STARTED")
        print(f"💰 Balance: ₹{self.state['balance']:.2f}")
        
        while True:
            try:
                # Check daily reset
                if self.daily_stats['date'] != datetime.now().date():
                    self.daily_stats = self._reset_daily_stats()
                
                # Circuit Breakers
                if self.daily_stats['trades_count'] >= MAX_DAILY_TRADES:
                    print("🛑 Max daily trades reached. Sleeping...")
                    time.sleep(300)
                    continue
                    
                if self.daily_stats['pnl'] < -(self.state['balance'] * MAX_DAILY_LOSS_PCT):
                    print("🛑 Max daily loss reached. Sleeping...")
                    time.sleep(300)
                    continue

                # Fetch Data
                df = self.fetch_data()
                if df is None:
                    time.sleep(60)
                    continue
                
                current_price = df['Close'].iloc[-1]
                
                # Manage Active Trade
                if self.state['active_trade']:
                    self.manage_trade(current_price, df['High'].iloc[-1], df['Low'].iloc[-1])
                
                # Look for New Trades
                else:
                    signal = self.check_signal(df)
                    if signal:
                        ai_score, reasoning = self.get_ai_score(signal)
                        print(f"🔎 Signal Found: {signal['type']} | AI: {ai_score}/10")
                        
                        if ai_score >= MIN_AI_SCORE:
                            qty = self.calculate_qty(signal, ai_score)
                            if qty > 0:
                                self.execute_trade(signal, qty, ai_score, reasoning)
                            else:
                                print("⚠️ Qty 0 - Risk too high or balance too low")
                        else:
                            print(f"⚠️ Rejected by AI (<{MIN_AI_SCORE})")
                
                time.sleep(60) # Check every minute
                
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = LiveBotV6()
    bot.run()
