import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import type { EditorProps } from '@monaco-editor/react';
import API_BASE_URL from '../config';

interface SimulationResult {
  roi: number;
  trades: number;
  winRate: number;
  drawdown: number;
  equity: number[];
}

interface ChatMessage {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
  type: 'text' | 'code' | 'system';
}

const MonacoEditor = dynamic<EditorProps>(
  () => import('@monaco-editor/react'),
  { ssr: false }
);

export default function AlgoLab() {
  const [code, setCode] = useState<string>(`# Echo Trading Algorithm Template
def initialize():
    """Set up your algorithm parameters here"""
    pass

def analyze_market(prices):
    """Analyze market conditions"""
    return {
        'signal': 'neutral',
        'confidence': 0.0
    }

def should_trade(analysis):
    """Define trading logic"""
    return False

def execute_trade(signal):
    """Execute trading decision"""
    pass`);

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [simResult, setSimResult] = useState<SimulationResult | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleRunSimulation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/algo/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      const result = await response.json();
      setSimResult(result);
    } catch (error) {
      console.error('Simulation failed:', error);
    }
  };

  const handleAIAssist = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/algo/ai-assist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, request: newMessage })
      });
      const { suggestion, explanation } = await response.json();

      setChatMessages(prev => [...prev,
      {
        id: Date.now().toString(),
        sender: 'user',
        content: newMessage,
        timestamp: new Date().toISOString(),
        type: 'text'
      },
      {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: explanation,
        timestamp: new Date().toISOString(),
        type: 'text'
      },
      {
        id: (Date.now() + 2).toString(),
        sender: 'ai',
        content: suggestion,
        timestamp: new Date().toISOString(),
        type: 'code'
      }
      ]);
      setNewMessage('');
    } catch (error) {
      console.error('AI assistance failed:', error);
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 text-gray-200 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-cyan-400">Algorithm Laboratory</h1>
          <nav className="space-x-4">
            <Link href="/dashboard" className="text-cyan-400 hover:text-cyan-300">
              Dashboard
            </Link>
            <Link href="/community" className="text-cyan-400 hover:text-cyan-300">
              Community
            </Link>
          </nav>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Code Editor */}
          <section className="bg-gray-800 rounded-lg shadow-lg">
            <div className="p-4 border-b border-gray-700">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-cyan-300">Algorithm Editor</h2>
                <button
                  onClick={handleRunSimulation}
                  className="bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded-md"
                >
                  Run Simulation
                </button>
              </div>
            </div>
            <div className="h-[600px]">
              <MonacoEditor
                defaultLanguage="python"
                theme="vs-dark"
                value={code}
                onChange={(value: string | undefined) => setCode(value || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                }}
              />
            </div>
          </section>

          {/* AI Assistant & Results */}
          <div className="space-y-8">
            {/* Simulation Results */}
            {simResult && (
              <section className="bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 className="text-xl font-semibold mb-4 text-cyan-300">Simulation Results</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-700 p-4 rounded-md">
                    <div className="text-sm text-gray-400">ROI</div>
                    <div className="text-2xl font-mono">{simResult.roi.toFixed(2)}%</div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-md">
                    <div className="text-sm text-gray-400">Win Rate</div>
                    <div className="text-2xl font-mono">{simResult.winRate.toFixed(2)}%</div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-md">
                    <div className="text-sm text-gray-400">Total Trades</div>
                    <div className="text-2xl font-mono">{simResult.trades}</div>
                  </div>
                  <div className="bg-gray-700 p-4 rounded-md">
                    <div className="text-sm text-gray-400">Max Drawdown</div>
                    <div className="text-2xl font-mono">{simResult.drawdown.toFixed(2)}%</div>
                  </div>
                </div>
              </section>
            )}

            {/* AI Assistant Chat */}
            <section className="bg-gray-800 rounded-lg shadow-lg">
              <div className="p-4 border-b border-gray-700">
                <h2 className="text-xl font-semibold text-cyan-300">AI Algorithm Assistant</h2>
              </div>
              <div className="h-[400px] flex flex-col">
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {chatMessages.map(msg => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] rounded-lg p-3 ${msg.sender === 'user' ? 'bg-cyan-800' : 'bg-gray-700'
                        }`}>
                        {msg.type === 'code' ? (
                          <pre className="text-sm font-mono bg-gray-900 p-2 rounded">
                            {msg.content}
                          </pre>
                        ) : (
                          <p className="text-sm">{msg.content}</p>
                        )}
                      </div>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>
                <div className="p-4 border-t border-gray-700">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={e => setNewMessage(e.target.value)}
                      onKeyPress={e => e.key === 'Enter' && handleAIAssist()}
                      placeholder="Ask for algorithm improvements..."
                      className="flex-1 bg-gray-700 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    />
                    <button
                      onClick={handleAIAssist}
                      className="bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded-md"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}