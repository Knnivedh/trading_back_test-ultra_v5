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

# V8.0 ULTRA PARAMETERS
MIN_AI_SCORE = 8.0
MIN_CONFLUENCE = 4
MIN_ADX = 25
MIN_VOLUME_RATIO = 1.3
MAX_DAILY_TRADES = 12
MAX_DAILY_LOSS_PCT = 0.10

class LiveBotV8:
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
            df['EMA20'] = ta.ema(df['Close'], length=20)
            df['EMA50'] = ta.ema(df['Close'], length=50)
            df['EMA200'] = ta.ema(df['Close'], length=200)
            df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
            
            # ADX
            adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            if adx is not None:
                df['ADX'] = adx['ADX_14']
            
            # MACD
            macd = ta.macd(df['Close'])
            if macd is not None:
                df = pd.concat([df, macd], axis=1)
                macd_col = [c for c in df.columns if 'MACD_' in c and 'h' not in c and 's' not in c][0]
                signal_col = [c for c in df.columns if 'MACDs_' in c][0]
                df['MACD'] = df[macd_col]
                df['MACD_SIGNAL'] = df[signal_col]
            
            df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
            
            # Bollinger Bands
            bb = ta.bbands(df['Close'], length=20, std=2)
            if bb is not None:
                df = pd.concat([df, bb], axis=1)
                bb_cols = [c for c in df.columns if 'BBL' in c]
                if bb_cols:
                    df['BB_LOWER'] = df[bb_cols[0]]
                    df['BB_MID'] = df[[c for c in df.columns if 'BBM' in c][0]]
                    df['BB_UPPER'] = df[[c for c in df.columns if 'BBU' in c][0]]
            
            # Supertrend
            st = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
            if st is not None:
                df = pd.concat([df, st], axis=1)
                st_dir_col = [c for c in df.columns if 'SUPERTd' in c][0]
                df['Supertrend_Direction'] = df[st_dir_col]
            
            df['RSI'] = ta.rsi(df['Close'], length=14)
            stoch = ta.stochrsi(df['Close'], length=14, rsi_length=14, k=3, d=3)
            if stoch is not None:
                df['Stoch_RSI'] = stoch['STOCHRSIk_14_14_3_3']
            
            df['Volume_Ratio'] = df['Volume'] / (df['Volume'].rolling(20).mean() + 1)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def get_ai_score(self, signal):
        """Get AI confidence score from Cerebras"""
        if not self.client:
            # Simulation fallback
            score = 6.0 + (signal['confluence'] * 0.6)
            if signal.get('adx', 0) > 30: score += 1.0
            if 'MACD' in signal['reasons']: score += 1.0
            return min(10.0, score), "Simulated Score"

        prompt = f"""
        Analyze this Nifty 50 trade setup (V8.0 Ultra Strategy):
        Type: {signal['type']} @ {signal['entry']:.2f}
        Confluence: {signal['confluence']}/9 factors
        Reasons: {', '.join(signal['reasons'])}
        ADX: {signal.get('adx', 0):.1f} (Trend Strength)
        
        Rate confidence 0-10. Be strict. >9.0 requires perfect setup.
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
            return 8.0, "AI Error - Default Score"

    def check_signal(self, df):
        """V8.0 Signal Detection Logic"""
        current = df.iloc[-1]
        
        if pd.isna(current['ATR']) or current['ATR'] <= 0:
            return None
            
        price = current['Close']
        
        # BULLISH
        if not pd.isna(current['EMA20']) and price > current['EMA20']:
            confluence = 0
            reasons = []
            
            if not pd.isna(current['EMA50']) and current['EMA20'] > current['EMA50']:
                confluence += 1; reasons.append("EMA")
            else: return None
            
            if not pd.isna(current['EMA200']) and not pd.isna(current['EMA50']) and current['EMA50'] > current['EMA200']:
                confluence += 1; reasons.append("EMA200")
            
            if not pd.isna(current['Supertrend_Direction']) and current['Supertrend_Direction'] == 1:
                confluence += 1; reasons.append("Supertrend")
            else: return None
            
            if pd.isna(current['ADX']) or current['ADX'] < MIN_ADX: return None
            confluence += 1; reasons.append("ADX")
            
            if not pd.isna(current['MACD']) and not pd.isna(current['MACD_SIGNAL']) and current['MACD'] > current['MACD_SIGNAL']:
                confluence += 1; reasons.append("MACD")
            
            if not pd.isna(current['Volume_Ratio']) and current['Volume_Ratio'] > MIN_VOLUME_RATIO:
                confluence += 1; reasons.append("Volume")
                
            if not pd.isna(current['VWAP']) and price > current['VWAP']:
                confluence += 1; reasons.append("VWAP")
                
            if not pd.isna(current['BB_LOWER']) and not pd.isna(current['BB_MID']) and current['BB_LOWER'] < price < current['BB_MID']:
                confluence += 1; reasons.append("BB")
                
            if not pd.isna(current['Stoch_RSI']) and 20 < current['Stoch_RSI'] < 80:
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
                    'tp2': entry + risk * 4.0,  # Extended
                    'risk': risk,
                    'confluence': confluence,
                    'reasons': reasons,
                    'adx': current['ADX'],
                    'volume_ratio': current['Volume_Ratio']
                }

        # BEARISH
        elif not pd.isna(current['EMA20']) and price < current['EMA20']:
            confluence = 0
            reasons = []
            
            if not pd.isna(current['EMA50']) and current['EMA20'] < current['EMA50']:
                confluence += 1; reasons.append("EMA")
            else: return None
            
            if not pd.isna(current['EMA200']) and not pd.isna(current['EMA50']) and current['EMA50'] < current['EMA200']:
                confluence += 1; reasons.append("EMA200")
            
            if not pd.isna(current['Supertrend_Direction']) and current['Supertrend_Direction'] == -1:
                confluence += 1; reasons.append("Supertrend")
            else: return None
            
            if pd.isna(current['ADX']) or current['ADX'] < MIN_ADX: return None
            confluence += 1; reasons.append("ADX")
            
            if not pd.isna(current['MACD']) and not pd.isna(current['MACD_SIGNAL']) and current['MACD'] < current['MACD_SIGNAL']:
                confluence += 1; reasons.append("MACD")
            
            if not pd.isna(current['Volume_Ratio']) and current['Volume_Ratio'] > MIN_VOLUME_RATIO:
                confluence += 1; reasons.append("Volume")
                
            if not pd.isna(current['VWAP']) and price < current['VWAP']:
                confluence += 1; reasons.append("VWAP")
                
            if not pd.isna(current['BB_UPPER']) and not pd.isna(current['BB_MID']) and current['BB_UPPER'] > price > current['BB_MID']:
                confluence += 1; reasons.append("BB")
                
            if not pd.isna(current['Stoch_RSI']) and 20 < current['Stoch_RSI'] < 80:
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
                    'tp2': entry - risk * 4.0,
                    'risk': risk,
                    'confluence': confluence,
                    'reasons': reasons,
                    'adx': current['ADX'],
                    'volume_ratio': current['Volume_Ratio']
                }
        
        return None

    def calculate_qty(self, signal, ai_score):
        """V8.0 Ultra Aggressive Position Sizing"""
        if ai_score >= 9.0: risk_pct = 10.0
        elif ai_score >= 8.5: risk_pct = 8.0
        elif ai_score >= 8.0: risk_pct = 6.0
        else: return 0
        
        # Streak adjustments
        if self.state['consecutive_losses'] >= 2: risk_pct = 4.0
        if self.state['consecutive_wins'] >= 3: risk_pct = min(risk_pct + 2.0, 12.0)
        
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
        """Manage active trade with TP1 and TP2"""
        trade = self.state['active_trade']
        if not trade: return

        exit_reason = None
        pnl = 0
        
        if trade['type'] == 'BUY':
            if not trade['tp1_hit'] and high >= trade['tp1']:
                half_qty = trade['original_qty'] // 2
                partial_pnl = (trade['tp1'] - trade['entry']) * half_qty
                
                self.state['balance'] += partial_pnl
                self.daily_stats['pnl'] += partial_pnl
                
                trade['tp1_hit'] = True
                trade['qty'] -= half_qty
                trade['sl'] = trade['entry']
                self.save_state()
                print(f"💰 TP1 HIT! Secured ₹{partial_pnl:.2f}, SL moved to BE")
                
            if low <= trade['sl']: exit_reason = "SL"; exit_price = trade['sl']
            elif high >= trade['tp2']: exit_reason = "TP2"; exit_price = trade['tp2']
                
        elif trade['type'] == 'SELL':
            if not trade['tp1_hit'] and low <= trade['tp1']:
                half_qty = trade['original_qty'] // 2
                partial_pnl = (trade['entry'] - trade['tp1']) * half_qty
                
                self.state['balance'] += partial_pnl
                self.daily_stats['pnl'] += partial_pnl
                
                trade['tp1_hit'] = True
                trade['qty'] -= half_qty
                trade['sl'] = trade['entry']
                self.save_state()
                print(f"💰 TP1 HIT! Secured ₹{partial_pnl:.2f}, SL moved to BE")
                
            if high >= trade['sl']: exit_reason = "SL"; exit_price = trade['sl']
            elif low <= trade['tp2']: exit_reason = "TP2"; exit_price = trade['tp2']

        if exit_reason:
            pnl = (exit_price - trade['entry']) * trade['qty'] if trade['type'] == 'BUY' else (trade['entry'] - exit_price) * trade['qty']
            
            self.state['balance'] += pnl
            self.daily_stats['pnl'] += pnl
            self.daily_stats['trades_count'] += 1
            
            total_trade_pnl = pnl
            if total_trade_pnl > 0:
                self.state['consecutive_wins'] += 1
                self.state['consecutive_losses'] = 0
            else:
                self.state['consecutive_losses'] += 1
                self.state['consecutive_wins'] = 0
            
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
        print("🤖 V8.0 ULTRA LIVE BOT STARTED")
        print(f"💰 Balance: ₹{self.state['balance']:.2f}")
        
        while True:
            try:
                if self.daily_stats['date'] != datetime.now().date():
                    self.daily_stats = self._reset_daily_stats()
                
                if self.daily_stats['trades_count'] >= MAX_DAILY_TRADES:
                    print("🛑 Max daily trades reached. Sleeping...")
                    time.sleep(300)
                    continue
                    
                if self.daily_stats['pnl'] < -(self.state['balance'] * MAX_DAILY_LOSS_PCT):
                    print("🛑 Max daily loss reached. Sleeping...")
                    time.sleep(300)
                    continue

                df = self.fetch_data()
                if df is None:
                    time.sleep(60)
                    continue
                
                current_price = df['Close'].iloc[-1]
                
                if self.state['active_trade']:
                    self.manage_trade(current_price, df['High'].iloc[-1], df['Low'].iloc[-1])
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
                
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = LiveBotV8()
    bot.run()
