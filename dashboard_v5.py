"""
V5.0 LIVE DASHBOARD
Real-time UI for V5.0 Trading Bot using Streamlit.
Run: streamlit run dashboard_v5.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
import time
from datetime import datetime

# Config
st.set_page_config(page_title="V5.0 Ultra Dashboard", layout="wide", page_icon="🚀")
STATE_FILE = "live_state.json"
TRADES_FILE = "live_trades.csv"

# Auto-refresh
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return None

def load_trades():
    if os.path.exists(TRADES_FILE):
        return pd.read_csv(TRADES_FILE)
    return pd.DataFrame()

# Header
st.title("🚀 V5.0 ULTRA LIVE DASHBOARD")
state = load_state()

if not state:
    st.error("⚠️ Bot is not running! (State file not found)")
    st.stop()

# Top Metrics
col1, col2, col3, col4 = st.columns(4)
balance = state.get('balance', 30000)
pnl_pct = ((balance - 30000) / 30000) * 100
active_trade = state.get('active_trade')

col1.metric("💰 Balance", f"₹{balance:,.2f}", f"{pnl_pct:+.2f}%")
col2.metric("📈 Active Trade", 
            f"{active_trade['type']} @ {active_trade['entry_price']:.0f}" if active_trade else "WAITING",
            f"Qty: {active_trade['qty']}" if active_trade else "---")

last_analysis = state.get('last_analysis', {})
col3.metric("📊 Last Price", f"₹{last_analysis.get('price', 0):,.2f}")
col4.metric("🤖 AI Score", f"{last_analysis.get('ai_score', 0)}/10", last_analysis.get('signal', 'NONE'))

# Main Chart (Mockup for now, real implementation would fetch yfinance data)
st.subheader("📉 Live Market Analysis")
st.info(f"Last Analysis Time: {last_analysis.get('time', '---')} | ADX: {last_analysis.get('adx', 0):.1f}")

if last_analysis.get('ai_reason'):
    st.success(f"🧠 **AI Reasoning:** {last_analysis['ai_reason']}")

# Trade History
st.subheader("📜 Recent Trades")
trades_df = load_trades()
if not trades_df.empty:
    st.dataframe(trades_df.sort_index(ascending=False).head(10), use_container_width=True)
else:
    st.info("No trades executed yet.")

# Auto-refresh logic
time.sleep(2)
st.rerun()
