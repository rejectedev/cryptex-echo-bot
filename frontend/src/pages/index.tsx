import { useState, useEffect } from 'react';
import Link from 'next/link';
import API_BASE_URL from '../config';

interface RoyaltyEntry {
  timestamp: string;
  trade_id: string;
  asset: string;
  royalty: number;
}

interface ChatEntry {
  sender: 'user' | 'ai';
  text: string;
}

export default function Home() {
  const [pearls, setPearls] = useState('Loading pearls...');
  const [royalties, setRoyalties] = useState<RoyaltyEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  // State for the chat interface
  const [chatHistory, setChatHistory] = useState<ChatEntry[]>([{ sender: 'ai', text: "Hello! I am Graei. How can I help you configure the bot?" }]);
  const [currentMessage, setCurrentMessage] = useState('');

  useEffect(() => {
    // Fetch Pearls
    fetch(`${API_BASE_URL}/pearls`)
      .then(res => {
        if (!res.ok) {
          throw new Error('Failed to fetch pearls');
        }
        return res.json();
      })
      .then(data => setPearls(data.content))
      .catch(err => {
        console.error(err);
        setPearls('Could not load pearl log.');
        setError('Could not connect to the backend. Is it running?');
      });

    // Fetch Royalties
    fetch(`${API_BASE_URL}/royalties`)
      .then(res => {
        if (!res.ok) {
          throw new Error('Failed to fetch royalties');
        }
        return res.json();
      })
      .then(data => {
        if (Array.isArray(data)) {
          setRoyalties(data);
        } else {
          console.error("Backend returned non-array for royalties:", data);
          setRoyalties([{ timestamp: new Date().toISOString(), trade_id: 'N/A', asset: 'Unexpected Data', royalty: 0.0 }]);
          setError(prev => prev || 'Backend returned unexpected data for royalties.');
        }
      })
      .catch(err => {
        console.error(err);
        setRoyalties([{ timestamp: new Date().toISOString(), trade_id: 'N/A', asset: 'Error Loading', royalty: 0.0 }]);
        setError('Could not connect to the backend. Is it running?');
      });
  }, []);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentMessage.trim()) return;

    const userMessage: ChatEntry = { sender: 'user', text: currentMessage };
    setChatHistory(prev => [...prev, userMessage]);
    setCurrentMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        credentials: 'omit',
        body: JSON.stringify({ message: currentMessage }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get response from AI');
      }

      const data = await response.json();
      const aiMessage: ChatEntry = {
        sender: 'ai',
        text: data.reply || "I received your message but couldn't generate a proper response."
      };
      setChatHistory(prev => [...prev, aiMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage: ChatEntry = {
        sender: 'ai',
        text: err instanceof Error ? err.message : "Sorry, I couldn't connect to my brain. Please check the backend."
      };
      setChatHistory(prev => [...prev, errorMessage]);
    }
  };

  return (
    <main className="font-sans bg-gray-900 text-gray-200 min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-cyan-400">🧿 Cryptex Echo Dashboard</h1>
          <p className="text-gray-400 mt-2">A sovereign trading interface</p>
          <div className="mt-4">
            <Link href="/settings" className="text-cyan-400 hover:text-cyan-300">Go to Settings &rarr;</Link>
          </div>
        </header>

        {error && (
          <div className="bg-red-800 border border-red-600 text-white px-4 py-3 rounded-lg relative mb-6" role="alert">
            <strong className="font-bold">Connection Error: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        <section className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-cyan-300">🤖 Graei AI Assistant</h2>
          <div className="bg-gray-900 p-4 rounded-md h-64 overflow-y-auto flex flex-col space-y-4">
            {chatHistory.map((entry, index) => (
              <div key={index} className={`flex ${entry.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${entry.sender === 'user' ? 'bg-cyan-800' : 'bg-gray-700'
                    }`}
                >
                  <p className="text-sm">{entry.text}</p>
                </div>
              </div>
            ))}
          </div>
          <form onSubmit={handleSendMessage} className="mt-4 flex gap-2">
            <input
              type="text"
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              placeholder="Change runner to AAPL..."
              className="flex-grow bg-gray-700 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
            <button type="submit" className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded-md">
              Send
            </button>
          </form>
        </section>

        <div className="grid md:grid-cols-2 gap-8 mt-8">
          <section className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-300">📜 Pearl Log</h2>
            <pre className="bg-gray-900 p-4 rounded-md whitespace-pre-wrap text-sm overflow-x-auto">
              {pearls}
            </pre>
          </section>

          <section className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-300">💰 Royalty Log</h2>
            <div className="space-y-3 text-sm max-h-96 overflow-y-auto pr-2">
              {royalties.map((entry, index) => (
                <div key={index} className="bg-gray-900 p-3 rounded-md">
                  <p><span className="font-mono text-cyan-500">{entry.timestamp}</span> :: Trade ID: {entry.trade_id}, Asset: {entry.asset}, Royalty: ${entry.royalty?.toFixed(2)}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}