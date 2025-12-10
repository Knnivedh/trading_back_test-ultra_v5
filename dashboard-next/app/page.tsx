'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { TrendingUp, Activity, DollarSign, Brain, Clock, RefreshCw, AlertTriangle, Table, Trophy, Target } from 'lucide-react';

interface Trade {
  entry_time?: string;
  exit_time?: string;
  type?: string;
  entry_price?: number;
  exit_price?: number;
  qty?: number;
  pnl?: number;
  reason?: string;
  balance?: number;
  ai_score?: number;
}

interface ActiveTrade {
  entry_time: string;
  type: string;
  entry_price: number;
  sl: number;
  tp1: number;
  tp2: number;
  qty: number;
  ai_score: number;
}

interface State {
  balance: number;
  active_trade?: ActiveTrade;
  trades_today: number;
  consecutive_wins: number;
  consecutive_losses: number;
  last_analysis?: {
    time: string;
    price: number;
    adx: number;
    signal: string;
    ai_score: number;
    ai_reason: string;
  };
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://trading-back-test-ultra-v5.onrender.com';
const STARTING_BALANCE = 30000;

export default function Dashboard() {
  const [state, setState] = useState<State | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retrying, setRetrying] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  const fetchData = async () => {
    try {
      setError(null);
      const [stateRes, tradesRes] = await Promise.all([
        axios.get(`${API_URL}/state`, { timeout: 30000 }),
        axios.get(`${API_URL}/trades`, { timeout: 30000 })
      ]);
      setState(stateRes.data);
      setTrades(Array.isArray(tradesRes.data) ? tradesRes.data : []);
      setLoading(false);
      setLastUpdate(new Date().toLocaleTimeString('en-IN'));
    } catch (err: any) {
      console.error('Error fetching data:', err);
      setLoading(false);
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        setError('Bot is waking up... (Render free tier sleeps after 15 min)');
      } else {
        setError('Cannot connect to trading bot. Click Wake Up to retry.');
      }
    }
  };

  const wakeUpBot = async () => {
    setRetrying(true);
    setError('Waking up bot... Please wait 30-60 seconds.');
    try {
      await axios.get(`${API_URL}/`, { timeout: 60000 });
      await fetchData();
    } catch (err) {
      setError('Bot is still starting. Please wait and try again.');
    }
    setRetrying(false);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
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
          container_id: 'tradingview_chart',
          studies: ['STD;EMA', 'STD;Supertrend', 'STD;Volume'],
          overrides: {
            'mainSeriesProperties.candleStyle.upColor': '#22c55e',
            'mainSeriesProperties.candleStyle.downColor': '#ef4444',
            'mainSeriesProperties.candleStyle.borderUpColor': '#22c55e',
            'mainSeriesProperties.candleStyle.borderDownColor': '#ef4444',
          }
        });
      }
    };
    document.head.appendChild(script);
  }, []);

  // Calculate stats
  const balance = state?.balance || STARTING_BALANCE;
  const totalPnl = balance - STARTING_BALANCE;
  const totalPnlPct = (totalPnl / STARTING_BALANCE) * 100;
  const totalTrades = trades.length + (state?.active_trade ? 1 : 0);
  const winningTrades = trades.filter(t => (t.pnl || 0) > 0).length;
  const losingTrades = trades.filter(t => (t.pnl || 0) < 0).length;
  const winRate = totalTrades > 0 ? ((winningTrades / trades.length) * 100) || 0 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white p-4 md:p-6">
      {/* Header */}
      <div className="mb-6 flex flex-wrap items-center justify-between">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
            V5.0 ULTRA DASHBOARD
          </h1>
          <p className="text-gray-400 mt-1">Real-Time AI Trading System</p>
        </div>
        <div className="text-right text-sm text-gray-400">
          <div>Last Update: {lastUpdate || '---'}</div>
          <div className={`flex items-center gap-2 ${state ? 'text-green-400' : 'text-yellow-400'}`}>
            <div className={`w-2 h-2 rounded-full animate-pulse ${state ? 'bg-green-400' : 'bg-yellow-400'}`} />
            {state ? 'Bot Online' : 'Bot Offline'}
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mb-6 bg-yellow-900/30 border border-yellow-500/50 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-yellow-400" size={24} />
            <span className="text-yellow-200">{error}</span>
          </div>
          <button
            onClick={wakeUpBot}
            disabled={retrying}
            className="flex items-center gap-2 bg-yellow-600 hover:bg-yellow-500 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
          >
            <RefreshCw className={`${retrying ? 'animate-spin' : ''}`} size={18} />
            {retrying ? 'Waking...' : 'Wake Up Bot'}
          </button>
        </div>
      )}

      {/* Summary Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-6">
        <div className="bg-gradient-to-br from-cyan-900/50 to-gray-900 border border-cyan-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 text-cyan-400 text-sm mb-1">
            <DollarSign size={16} /> BALANCE
          </div>
          <div className="text-2xl font-bold">₹{balance.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
        </div>

        <div className="bg-gradient-to-br from-green-900/50 to-gray-900 border border-green-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 text-green-400 text-sm mb-1">
            <Trophy size={16} /> TOTAL P&L
          </div>
          <div className={`text-2xl font-bold ${totalPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {totalPnl >= 0 ? '+' : ''}₹{totalPnl.toFixed(0)}
          </div>
          <div className={`text-xs ${totalPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ({totalPnlPct >= 0 ? '+' : ''}{totalPnlPct.toFixed(2)}%)
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-900/50 to-gray-900 border border-purple-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 text-purple-400 text-sm mb-1">
            <Table size={16} /> TRADES
          </div>
          <div className="text-2xl font-bold">{totalTrades}</div>
          <div className="text-xs text-gray-400">Total Executed</div>
        </div>

        <div className="bg-gradient-to-br from-blue-900/50 to-gray-900 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 text-blue-400 text-sm mb-1">
            <Target size={16} /> WIN RATE
          </div>
          <div className="text-2xl font-bold">{winRate.toFixed(0)}%</div>
          <div className="text-xs text-gray-400">{winningTrades}W / {losingTrades}L</div>
        </div>

        <div className="bg-gradient-to-br from-orange-900/50 to-gray-900 border border-orange-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 text-orange-400 text-sm mb-1">
            <Activity size={16} /> LIVE PRICE
          </div>
          <div className="text-2xl font-bold">₹{state?.last_analysis?.price?.toLocaleString() || '---'}</div>
        </div>

        <div className="bg-gradient-to-br from-pink-900/50 to-gray-900 border border-pink-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 text-pink-400 text-sm mb-1">
            <Brain size={16} /> AI SCORE
          </div>
          <div className="text-2xl font-bold">{state?.last_analysis?.ai_score?.toFixed(1) || '0'}/10</div>
          <div className="text-xs text-gray-400">{state?.last_analysis?.signal || 'MONITORING'}</div>
        </div>
      </div>

      {/* Active Trade Card */}
      {state?.active_trade && (
        <div className="mb-6 bg-gradient-to-r from-green-900/40 to-blue-900/40 border-2 border-green-500/50 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="text-green-400 animate-pulse" size={28} />
            <h2 className="text-xl font-bold">🔥 ACTIVE TRADE</h2>
            <span className={`ml-auto px-3 py-1 rounded-full text-sm font-bold ${state.active_trade.type === 'BUY' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
              {state.active_trade.type}
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
            <div>
              <div className="text-gray-400">Entry Price</div>
              <div className="text-lg font-bold">₹{state.active_trade.entry_price.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-gray-400">Quantity</div>
              <div className="text-lg font-bold">{state.active_trade.qty}</div>
            </div>
            <div>
              <div className="text-gray-400">Stop Loss</div>
              <div className="text-lg font-bold text-red-400">₹{state.active_trade.sl.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-gray-400">Target (TP2)</div>
              <div className="text-lg font-bold text-green-400">₹{state.active_trade.tp2.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-gray-400">AI Score</div>
              <div className="text-lg font-bold text-cyan-400">{state.active_trade.ai_score}/10</div>
            </div>
          </div>
          <div className="mt-3 text-xs text-gray-400">Entry Time: {state.active_trade.entry_time}</div>
        </div>
      )}

      {/* AI Analysis Panel */}
      {state?.last_analysis && (
        <div className="mb-6 bg-gradient-to-r from-purple-900/30 to-cyan-900/30 border border-cyan-500/30 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <Brain className="text-cyan-400" size={24} />
            <h2 className="text-lg font-bold">AI Analysis</h2>
            <span className="ml-auto text-sm text-gray-400">{state.last_analysis.time}</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-gray-400">Signal</div>
              <div className={`text-lg font-bold ${state.last_analysis.signal === 'BUY' ? 'text-green-400' :
                  state.last_analysis.signal === 'SELL' ? 'text-red-400' : 'text-gray-400'
                }`}>{state.last_analysis.signal}</div>
            </div>
            <div>
              <div className="text-gray-400">Price</div>
              <div className="text-lg font-bold">₹{state.last_analysis.price.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-gray-400">ADX</div>
              <div className="text-lg font-bold">{state.last_analysis.adx.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-gray-400">AI Score</div>
              <div className={`text-lg font-bold ${state.last_analysis.ai_score >= 7 ? 'text-green-400' : 'text-red-400'}`}>
                {state.last_analysis.ai_score}/10 {state.last_analysis.ai_score >= 7 ? '✅' : '❌'}
              </div>
            </div>
          </div>
          <div className="mt-3 p-3 bg-black/30 rounded-lg">
            <div className="text-gray-400 text-xs mb-1">AI Reasoning:</div>
            <div className="text-cyan-400">{state.last_analysis.ai_reason}</div>
          </div>
        </div>
      )}

      {/* TradingView Chart */}
      <div className="mb-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-cyan-500/30 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-3">
          <Clock className="text-cyan-400" size={24} />
          <h2 className="text-lg font-bold">Live Chart (Nifty 50 - 5 Min)</h2>
        </div>
        <div id="tradingview_chart" className="w-full h-[400px] rounded-lg overflow-hidden"></div>
      </div>

      {/* Trade History Table */}
      <div className="mb-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-purple-500/30 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-4">
          <Table className="text-purple-400" size={24} />
          <h2 className="text-lg font-bold">Trade History</h2>
          <span className="ml-auto text-sm text-gray-400">{trades.length} trades</span>
        </div>

        {trades.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-400 border-b border-gray-700">
                  <th className="pb-2 pr-4">Exit Time</th>
                  <th className="pb-2 pr-4">P&L</th>
                  <th className="pb-2 pr-4">Reason</th>
                  <th className="pb-2 pr-4">Balance After</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade, idx) => (
                  <tr key={idx} className="border-b border-gray-800 hover:bg-gray-800/50">
                    <td className="py-3 pr-4">{trade.exit_time || '---'}</td>
                    <td className={`py-3 pr-4 font-bold ${(trade.pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {(trade.pnl || 0) >= 0 ? '+' : ''}₹{(trade.pnl || 0).toFixed(2)}
                    </td>
                    <td className="py-3 pr-4">
                      <span className={`px-2 py-1 rounded text-xs ${trade.reason === 'TP2' ? 'bg-green-500/20 text-green-400' :
                          trade.reason === 'TP1' ? 'bg-blue-500/20 text-blue-400' :
                            trade.reason === 'SL' ? 'bg-red-500/20 text-red-400' :
                              'bg-gray-500/20 text-gray-400'
                        }`}>
                        {trade.reason || 'Closed'}
                      </span>
                    </td>
                    <td className="py-3 pr-4">₹{(trade.balance || 0).toFixed(0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center text-gray-500 py-8">
            No completed trades yet. Trades will appear here after they close.
          </div>
        )}
      </div>

      {/* Performance Summary */}
      <div className="mb-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-green-500/30 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-4">
          <Trophy className="text-green-400" size={24} />
          <h2 className="text-lg font-bold">Performance Summary</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-gray-400 text-xs">Starting Balance</div>
            <div className="text-lg font-bold">₹{STARTING_BALANCE.toLocaleString()}</div>
          </div>
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-gray-400 text-xs">Current Balance</div>
            <div className="text-lg font-bold text-cyan-400">₹{balance.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
          </div>
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-gray-400 text-xs">Total Profit/Loss</div>
            <div className={`text-lg font-bold ${totalPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {totalPnl >= 0 ? '+' : ''}₹{totalPnl.toFixed(0)} ({totalPnlPct.toFixed(2)}%)
            </div>
          </div>
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-gray-400 text-xs">Win Streak</div>
            <div className="text-lg font-bold">
              🔥 {state?.consecutive_wins || 0} wins | 💀 {state?.consecutive_losses || 0} losses
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center text-gray-500 text-xs">
        V5.0 Ultra AI Trading System | Auto-refreshing every 10s | Market Hours: Mon-Fri 9:15 AM - 3:30 PM IST
      </div>
    </div>
  );
}
