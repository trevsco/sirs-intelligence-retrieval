import React, { useState } from 'react';
import api from '../services/api';

function AnalyzePage() {
  const [analysis, setAnalysis] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const runAnalysis = async () => {
    setLoading(true);
    setError('');
    setAnalysis('');
    
    try {
      // Triggering a broad query to the backend to summarize the vector store
      const response = await api.query(
        "Please analyze the indexed documents and provide a comprehensive summary and key takeaways of their contents.", 
        5, 
        0.0
      );
      setAnalysis(response.answer);
    } catch (err) {
      console.error(err);
      setError('Failed to generate analysis. Ensure your backend is running and documents are indexed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="bg-white p-6 rounded-lg shadow flex justify-between items-center border border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Document Analysis</h2>
          <p className="text-sm text-gray-500 mt-1">Generate a comprehensive summary of all indexed intelligence.</p>
        </div>
        <button
          onClick={runAnalysis}
          disabled={loading}
          className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors font-medium shadow-sm"
        >
          {loading ? 'Analyzing...' : 'Run Full Analysis'}
        </button>
      </div>

      <div className="bg-white flex-1 rounded-lg shadow border border-gray-200 overflow-hidden flex flex-col">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-700">Analysis Results</h3>
        </div>
        <div className="p-6 flex-1 overflow-y-auto">
          {loading && (
            <div className="flex items-center justify-center h-full text-gray-500 space-x-2">
              <div className="animate-pulse">Reading and summarizing documents...</div>
            </div>
          )}
          
          {!loading && !analysis && !error && (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 mt-10">
              <p>Click "Run Full Analysis" to generate a summary of your database.</p>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-md">
              {error}
            </div>
          )}

          {analysis && (
            <div className="prose max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed text-sm">
              {analysis}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AnalyzePage;