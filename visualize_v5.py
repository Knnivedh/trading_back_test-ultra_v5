"""
V5.0 VISUALIZATION SCRIPT
Generates high-quality charts for V5.0 Hyper-Growth System results.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Set non-interactive backend
import matplotlib.pyplot as plt
import os

# Set style
plt.style.use('dark_background')

def load_data(filepath):
    df = pd.read_csv(filepath)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    
    # Calculate Indicators (Same as System V5)
    # EMAs
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    
    # ATR
    high = df['High']
    low = df['Low']
    close = df['Close']
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    df['ATR'] = tr.rolling(window=14).mean()
    
    # Supertrend
    hl2 = (df['High'] + df['Low']) / 2
    multiplier = 3
    upper_band = hl2 + (multiplier * df['ATR'])
    lower_band = hl2 - (multiplier * df['ATR'])
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

    # ADX
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    atr = df['ATR']
    plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 0.0001)
    df['ADX'] = dx.rolling(window=14).mean()

    # StochRSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 0.0001)
    rsi = 100 - (100 / (1 + rs))
    stoch_rsi = (rsi - rsi.rolling(window=14).min()) / (rsi.rolling(window=14).max() - rsi.rolling(window=14).min() + 0.0001)
    df['Stoch_RSI'] = stoch_rsi.rolling(window=3).mean() * 100

    # VWAP
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    volume_sum = df['Volume'].cumsum()
    volume_sum = volume_sum.replace(0, 1)
    df['VWAP'] = (typical_price * df['Volume']).cumsum() / volume_sum

    # Bollinger Bands
    sma = df['Close'].rolling(window=20).mean()
    std_dev = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = sma + (std_dev * 2)
    df['BB_Lower'] = sma - (std_dev * 2)

    return df

def plot_trend_analysis(df, start_idx=-400, end_idx=-100):
    subset = df.iloc[start_idx:end_idx]
    plt.figure(figsize=(15, 8))
    plt.plot(subset.index, subset['Close'], label='Price', color='white', alpha=0.9)
    plt.plot(subset.index, subset['EMA20'], label='EMA20', color='cyan', alpha=0.8)
    plt.plot(subset.index, subset['EMA50'], label='EMA50', color='orange', alpha=0.8)
    plt.plot(subset.index, subset['EMA200'], label='EMA200', color='red', alpha=0.8)
    
    # Supertrend
    plt.scatter(subset[subset['Supertrend_Direction']==1].index, subset[subset['Supertrend_Direction']==1]['Supertrend'], color='green', s=5, label='Bullish Zone')
    plt.scatter(subset[subset['Supertrend_Direction']==-1].index, subset[subset['Supertrend_Direction']==-1]['Supertrend'], color='red', s=5, label='Bearish Zone')
    
    plt.title('1. TREND ANALYSIS: EMAs + Supertrend', fontsize=16, color='gold')
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig('plots/1_trend_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Saved 1_trend_analysis.png")
    plt.close()

def plot_momentum(df, start_idx=-400, end_idx=-100):
    subset = df.iloc[start_idx:end_idx]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
    
    # ADX
    ax1.plot(subset.index, subset['ADX'], color='yellow', label='ADX (Trend Strength)')
    ax1.axhline(y=20, color='white', linestyle='--')
    ax1.fill_between(subset.index, subset['ADX'], 20, where=(subset['ADX']>20), color='yellow', alpha=0.2)
    ax1.set_title('2. MOMENTUM: ADX > 20 = Strong Trend', fontsize=14, color='gold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.2)
    
    # StochRSI
    ax2.plot(subset.index, subset['Stoch_RSI'], color='magenta', label='StochRSI')
    ax2.axhline(y=80, color='red', linestyle='--')
    ax2.axhline(y=20, color='green', linestyle='--')
    ax2.set_title('StochRSI: Overbought/Oversold', fontsize=14, color='gold')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.2)
    
    plt.savefig('plots/2_momentum.png', dpi=300, bbox_inches='tight')
    print("✅ Saved 2_momentum.png")
    plt.close()

def plot_volume_vwap(df, start_idx=-400, end_idx=-100):
    subset = df.iloc[start_idx:end_idx]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    
    # VWAP
    ax1.plot(subset.index, subset['Close'], label='Price', color='white', alpha=0.5)
    ax1.plot(subset.index, subset['VWAP'], label='VWAP (Inst. Price)', color='cyan', linewidth=2)
    ax1.fill_between(subset.index, subset['Close'], subset['VWAP'], where=(subset['Close']>subset['VWAP']), color='green', alpha=0.1, label='Bullish Zone')
    ax1.fill_between(subset.index, subset['Close'], subset['VWAP'], where=(subset['Close']<subset['VWAP']), color='red', alpha=0.1, label='Bearish Zone')
    ax1.set_title('3. VOLUME & VWAP: Institutional Flow', fontsize=16, color='gold')
    ax1.legend()
    ax1.grid(True, alpha=0.2)
    
    # Volume
    colors = ['green' if c > o else 'red' for c, o in zip(subset['Close'], subset['Open'])]
    ax2.bar(subset.index, subset['Volume'], color=colors, alpha=0.8)
    ax2.set_title('Volume Activity', fontsize=12)
    ax2.grid(True, alpha=0.2)
    
    plt.savefig('plots/3_volume_vwap.png', dpi=300, bbox_inches='tight')
    print("✅ Saved 3_volume_vwap.png")
    plt.close()

def plot_execution_zoom(df, start_idx=-150, end_idx=-50):
    subset = df.iloc[start_idx:end_idx]
    plt.figure(figsize=(15, 8))
    
    # Price and Bands
    plt.plot(subset.index, subset['Close'], color='white', linewidth=2, label='Price')
    plt.plot(subset.index, subset['BB_Upper'], color='gray', linestyle='--', alpha=0.5)
    plt.plot(subset.index, subset['BB_Lower'], color='gray', linestyle='--', alpha=0.5)
    plt.fill_between(subset.index, subset['BB_Upper'], subset['BB_Lower'], color='gray', alpha=0.1)
    
    # Signals (Mock visualization of where signals would trigger)
    # Highlight strong trend areas
    strong_trend = subset[subset['ADX'] > 25]
    plt.scatter(strong_trend.index, strong_trend['Close'], color='gold', s=30, alpha=0.3, label='High Momentum Zone')
    
    plt.title('4. TRADE EXECUTION: Zoomed View', fontsize=16, color='gold')
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig('plots/4_execution.png', dpi=300, bbox_inches='tight')
    print("✅ Saved 4_execution.png")
    plt.close()

def plot_drawdown(trades_path):
    if not os.path.exists(trades_path): return
    trades = pd.read_csv(trades_path)
    trades['balance'] = 30000 + trades['pnl'].cumsum()
    trades['peak'] = trades['balance'].cummax()
    trades['drawdown'] = (trades['balance'] - trades['peak']) / trades['peak'] * 100
    
    plt.figure(figsize=(15, 6))
    plt.fill_between(range(len(trades)), trades['drawdown'], 0, color='red', alpha=0.3)
    plt.plot(range(len(trades)), trades['drawdown'], color='red', linewidth=1)
    plt.axhline(y=0, color='white', linestyle='-')
    plt.title('5. RISK ANALYSIS: Drawdown %', fontsize=16, color='gold')
    plt.ylabel('Drawdown %')
    plt.xlabel('Trade Number')
    plt.grid(True, alpha=0.2)
    plt.savefig('plots/5_drawdown.png', dpi=300, bbox_inches='tight')
    print("✅ Saved 5_drawdown.png")
    plt.close()

def plot_growth(trades_path):
    if not os.path.exists(trades_path): return
    trades = pd.read_csv(trades_path)
    trades['balance'] = 30000 + trades['pnl'].cumsum()
    
    plt.figure(figsize=(15, 8))
    plt.plot(range(len(trades)), trades['balance'], color='#00ff00', linewidth=3)
    plt.axhline(y=30000, color='white', linestyle='--', label='Start (₹30k)')
    plt.axhline(y=71671, color='gold', linestyle='--', label='End (₹71k)')
    
    # Annotate big wins
    big_wins = trades[trades['pnl'] > 5000]
    plt.scatter(big_wins.index, big_wins['balance'], color='gold', s=100, zorder=5, label='Sniper Wins')
    
    plt.title('6. GROWTH: Equity Curve (₹30k -> ₹71k)', fontsize=16, color='gold')
    plt.xlabel('Trade Number')
    plt.ylabel('Balance (₹)')
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig('plots/6_growth.png', dpi=300, bbox_inches='tight')
    print("✅ Saved 6_growth.png")
    plt.close()

if __name__ == "__main__":
    print("Generating 6 Detailed Charts...")
    os.makedirs('plots', exist_ok=True)
    
    data_path = "data_nifty_50_5m.csv"
    if os.path.exists(data_path):
        df = load_data(data_path)
        # Generate market charts
        plot_trend_analysis(df)
        plot_momentum(df)
        plot_volume_vwap(df)
        plot_execution_zoom(df)
    
    trades_path = "output_v5/trades.csv"
    if os.path.exists(trades_path):
        plot_drawdown(trades_path)
        plot_growth(trades_path)
        
    print("✅ Done! Check 'ultra_v5/plots/' folder.")
