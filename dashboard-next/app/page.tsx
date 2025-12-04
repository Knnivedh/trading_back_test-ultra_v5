'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { TrendingUp, Activity, DollarSign, Brain, Clock } from 'lucide-react';

interface State {
  balance: number;
  active_trade?: {
    type: string;
    entry_price: number;
    qty: number;
    sl: number;
    tp2: number;
    ai_score: number;
  };
  last_analysis?: {
    time: string;
    price: number;
    adx: number;
    signal: string;
    ai_score: number;
    ai_reason: string;
  };
}

export default function Dashboard() {
  const [state, setState] = useState<State | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('https://trading-back-test-ultra-v5.onrender.com/state');
        setState(res.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Load TradingView widget
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => {
      if (typeof window.TradingView !== 'undefined') {
        new window.TradingView.widget({
          autosize: true,
          symbol: 'NSE:NIFTY',
          interval: '5',
          timezone: 'Asia/Kolkata',
          theme: 'dark',
          style: '1',
          locale: 'en',
          toolbar_bg: '#0f172a',
          enable_publishing: false,
          hide_top_toolbar: false,
          hide_legend: false,
          save_image: false,
          container_id: 'tradingview_chart',
          studies: [
            'STD;EMA',
            'STD;Supertrend',
            'STD;Volume'
          ],
          overrides: {
            'mainSeriesProperties.candleStyle.upColor': '#22c55e',
            'mainSeriesProperties.candleStyle.downColor': '#ef4444',
            'mainSeriesProperties.candleStyle.borderUpColor': '#22c55e',
            'mainSeriesProperties.candleStyle.borderDownColor': '#ef4444',
            'mainSeriesProperties.candleStyle.wickUpColor': '#22c55e',
            'mainSeriesProperties.candleStyle.wickDownColor': '#ef4444',
          }
        });
      }
    };
    document.head.appendChild(script);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center">
        <div className="text-2xl text-cyan-400 animate-pulse">Loading V5.0 Ultra...</div>
      </div>
    );
  }

  if (!state) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center">
        <div className="text-xl text-red-400">⚠️ Bot Offline</div>
      </div>
    );
  }

  const pnl = state.balance - 30000;
  const pnlPct = (pnl / 30000) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white p-6">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
          V5.0 ULTRA DASHBOARD
        </h1>
        <p className="text-gray-400 mt-2">Real-Time AI Trading System</p>
      </div>

      {/* Top Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-cyan-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="text-cyan-400" size={24} />
            <span className="text-xs text-gray-400">BALANCE</span>
          </div>
          <div className="text-3xl font-bold">₹{state.balance.toLocaleString()}</div>
          <div className={`text-sm mt-1 ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {pnl >= 0 ? '+' : ''}₹{pnl.toFixed(2)} ({pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(2)}%)
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-purple-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="text-purple-400" size={24} />
            <span className="text-xs text-gray-400">ACTIVE TRADE</span>
          </div>
          {state.active_trade ? (
            <>
              <div className={`text-2xl font-bold ${state.active_trade.type === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                {state.active_trade.type}
              </div>
              <div className="text-sm text-gray-400 mt-1">
                @ ₹{state.active_trade.entry_price.toFixed(0)} | Qty: {state.active_trade.qty}
              </div>
            </>
          ) : (
            <div className="text-xl text-gray-500">Waiting...</div>
          )}
        </div>

        <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-orange-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-2">
            <Activity className="text-orange-400" size={24} />
            <span className="text-xs text-gray-400">LIVE PRICE</span>
          </div>
          <div className="text-3xl font-bold">
            ₹{state.last_analysis?.price.toLocaleString() || '---'}
          </div>
          <div className="text-sm text-gray-400 mt-1">
            ADX: {state.last_analysis?.adx.toFixed(1) || '---'}
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-green-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-2">
            <Brain className="text-green-400" size={24} />
            <span className="text-xs text-gray-400">AI SCORE</span>
          </div>
          <div className="text-3xl font-bold">
            {state.last_analysis?.ai_score.toFixed(1) || '0'}<span className="text-lg">/10</span>
          </div>
          <div className="text-sm text-gray-400 mt-1">
            {state.last_analysis?.signal || 'MONITORING'}
          </div>
        </div>
      </div>

      {/* TradingView Chart */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-cyan-500/30 rounded-xl p-6 mb-8 backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-4">
          <Clock className="text-cyan-400" size={28} />
          <h2 className="text-2xl font-bold">Live TradingView Chart (Nifty 50)</h2>
          <span className="ml-auto text-xs text-gray-400">5-Min | NSE</span>
        </div>

        <div id="tradingview_chart" className="w-full h-[600px] rounded-lg overflow-hidden"></div>
      </div>

      {/* AI Brain Panel */}
      {state.last_analysis && (
        <div className="bg-gradient-to-r from-purple-900/30 to-cyan-900/30 border-2 border-cyan-500/50 rounded-xl p-8 mb-8 backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="text-cyan-400 animate-pulse" size={32} />
            <h2 className="text-2xl font-bold">AI Command Center</h2>
            <Clock className="text-gray-400 ml-auto" size={20} />
            <span className="text-gray-400">{state.last_analysis.time}</span>
          </div>

          <div className="space-y-3">
            <div>
              <span className="text-gray-400">Signal Detected:</span>
              <span className={`ml-2 font-bold text-xl ${state.last_analysis.signal === 'BUY' ? 'text-green-400' :
                state.last_analysis.signal === 'SELL' ? 'text-red-400' : 'text-gray-400'
                }`}>
                {state.last_analysis.signal}
              </span>
            </div>

            <div>
              <span className="text-gray-400">AI Reasoning:</span>
              <p className="text-cyan-400 mt-1 text-lg">{state.last_analysis.ai_reason}</p>
            </div>

            <div className="flex items-center gap-4 mt-4">
              <div className="h-3 flex-1 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${state.last_analysis.ai_score >= 7 ? 'bg-gradient-to-r from-green-400 to-green-600' : 'bg-gradient-to-r from-red-400 to-red-600'
                    }`}
                  style={{ width: `${state.last_analysis.ai_score * 10}%` }}
                />
              </div>
              <span className="text-sm font-bold">
                {state.last_analysis.ai_score >= 7 ? '✅ APPROVED' : '❌ REJECTED'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Status Footer */}
      <div className="text-center text-gray-500 text-sm">
        <div className="inline-flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          System Online | Refreshing every 5s | {state.active_trade ? `Active: 1 ${state.active_trade.type} Trade` : 'No Active Trades'}
        </div>
      </div>
    </div>
  );
}
