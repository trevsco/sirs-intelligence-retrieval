import React, { useState } from 'react';
import api from '../services/api';

function ChatPage({ refreshStats }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  // Updated to accept an optional 'overrideText' for our Analyze button
  const handleSend = async (e, overrideText = null) => {
    if (e) e.preventDefault();
    
    const currentQuery = overrideText || query;
    if (!currentQuery.trim()) return;

    setHistory((prev) => [...prev, { role: 'user', content: currentQuery }]);
    if (!overrideText) setQuery(''); // Only clear input if typed manually
    setLoading(true);

    try {
      const response = await api.query(currentQuery, 5, 0.0);
      
      if (refreshStats) {
        await refreshStats();
      }
      
      setHistory((prev) => [
        ...prev, 
        { role: 'assistant', content: response.answer }
      ]);
    } catch (err) {
      console.error(err);
      setHistory((prev) => [
        ...prev, 
        { role: 'assistant', error: true, content: 'Error: Could not get a response.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Dedicated function for the Analyze button
  const handleAnalyze = () => {
    const analysisPrompt = "Please analyze the indexed documents and provide a comprehensive summary of their contents.";
    handleSend(null, analysisPrompt);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow overflow-hidden">
      
      {/* Header Toolbar with Analyze Button */}
      <div className="bg-gray-50 border-b border-gray-200 p-4 flex justify-between items-center">
        <h2 className="text-lg font-bold text-gray-700">Intelligence Query</h2>
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="bg-indigo-100 text-indigo-700 hover:bg-indigo-200 px-4 py-2 rounded-md text-sm font-semibold transition-colors disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Analyze & Summarize Data'}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {history.length === 0 ? (
          <div className="text-center text-gray-500 mt-10">
            <h3 className="text-lg font-semibold text-gray-700">Ready to query your documents.</h3>
            <p className="mt-2 text-sm">Type a question below, or click <strong>Analyze & Summarize</strong> to get an overview first.</p>
          </div>
        ) : (
          history.map((msg, idx) => (
            <div 
              key={idx} 
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[75%] rounded-lg px-4 py-3 ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : msg.error 
                      ? 'bg-red-50 text-red-600 border border-red-200' 
                      : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="text-xs font-semibold mb-1 opacity-75">
                  {msg.role === 'user' ? 'You' : 'System'}
                </div>
                <div className="whitespace-pre-wrap text-sm">
                  {msg.content}
                </div>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-500 rounded-lg px-4 py-3 text-sm">
              Analyzing...
            </div>
          </div>
        )}
      </div>

      <form 
        onSubmit={handleSend}
        className="border-t border-gray-200 p-4 bg-gray-50 flex space-x-2"
      >
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
          placeholder="Ask a question about your documents..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          Send
        </button>
      </form>
      
    </div>
  );
}

export default ChatPage;