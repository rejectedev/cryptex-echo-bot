import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import API_BASE_URL from '../config';

interface Trade {
  id: string;
  timestamp: string;
  asset: string;
  type: 'buy' | 'sell';
  price: number;
  status: 'active' | 'completed' | 'pending';
  algorithm: string;
}

interface AlgorithmOption {
  id: string;
  name: string;
  description: string;
  performance: {
    roi: number;
    winRate: number;
    trades: number;
  };
}

export default function Dashboard() {
  const [activeTrades, setActiveTrades] = useState<Trade[]>([]);
  const [tradeHistory, setTradeHistory] = useState<Trade[]>([]);
  const [selectedAlgo, setSelectedAlgo] = useState<string>('echo');
  const [algorithms, setAlgorithms] = useState<AlgorithmOption[]>([
    {
      id: 'echo',
      name: 'Echo Trading',
      description: 'Original Echo trading algorithm using price relationship analysis',
      performance: { roi: 0, winRate: 0, trades: 0 }
    }
  ]);

  useEffect(() => {
    // Fetch active trades
    fetch(`${API_BASE_URL}/trades/active`)
      .then(res => res.json())
      .then(data => setActiveTrades(data))
      .catch(console.error);

    // Fetch trade history
    fetch(`${API_BASE_URL}/trades/history`)
      .then(res => res.json())
      .then(data => setTradeHistory(data))
      .catch(console.error);

    // Fetch algorithm performance
    fetch(`${API_BASE_URL}/algorithms/performance`)
      .then(res => res.json())
      .then(data => {
        setAlgorithms(prev => prev.map(algo => ({
          ...algo,
          performance: data[algo.id] || algo.performance
        })));
      })
      .catch(console.error);
  }, []);

  const handleAlgoChange = async (algoId: string) => {
    try {
      await fetch(`${API_BASE_URL}/algorithms/select`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ algorithmId: algoId })
      });
      setSelectedAlgo(algoId);
    } catch (error) {
      console.error('Failed to switch algorithm:', error);
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 text-gray-200 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-cyan-400">Trading Dashboard</h1>
          <nav className="space-x-4">
            <Link href="/algo-lab" className="text-cyan-400 hover:text-cyan-300">
              Algo Lab
            </Link>
            <Link href="/community" className="text-cyan-400 hover:text-cyan-300">
              Community
            </Link>
          </nav>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Active Trades */}
          <section className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-300">Active Trades</h2>
            <div className="space-y-4">
              {activeTrades.map(trade => (
                <div key={trade.id} className="bg-gray-700 p-4 rounded-md">
                  <div className="flex justify-between items-center">
                    <span className="font-mono">{trade.asset}</span>
                    <span className={trade.type === 'buy' ? 'text-green-400' : 'text-red-400'}>
                      {trade.type.toUpperCase()}
                    </span>
                  </div>
                  <div className="mt-2 text-sm text-gray-400">
                    Price: ${trade.price.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Algorithm Selection */}
          <section className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-300">Trading Algorithm</h2>
            <div className="space-y-4">
              {algorithms.map(algo => (
                <div key={algo.id} className="bg-gray-700 p-4 rounded-md">
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      name="algorithm"
                      checked={selectedAlgo === algo.id}
                      onChange={() => handleAlgoChange(algo.id)}
                      className="text-cyan-500"
                    />
                    <div>
                      <h3 className="font-semibold">{algo.name}</h3>
                      <p className="text-sm text-gray-400">{algo.description}</p>
                    </div>
                  </div>
                  <div className="mt-2 grid grid-cols-3 gap-2 text-sm">
                    <div>ROI: {algo.performance.roi}%</div>
                    <div>Win Rate: {algo.performance.winRate}%</div>
                    <div>Trades: {algo.performance.trades}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Trade History */}
          <section className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-300">Trade History</h2>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {tradeHistory.map(trade => (
                <div key={trade.id} className="bg-gray-700 p-3 rounded-md text-sm">
                  <div className="flex justify-between">
                    <span>{trade.asset}</span>
                    <span className={`font-mono ${trade.type === 'buy' ? 'text-green-400' : 'text-red-400'
                      }`}>
                      ${trade.price.toFixed(2)}
                    </span>
                  </div>
                  <div className="text-gray-400 text-xs mt-1">
                    {new Date(trade.timestamp).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}