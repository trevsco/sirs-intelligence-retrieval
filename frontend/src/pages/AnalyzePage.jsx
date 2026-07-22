import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import api from "../services/api";
import { useTimer } from "../context/TimerContext";
import ProcessingStatus from "../components/ProcessingStatus";

function AnalyzePage() {
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

 const {
  startTimer,
  stopTimer
} = useTimer();

  const runAnalysis = async () => {
    startTimer();

    setLoading(true);
    setError("");
    setAnalysis("");

    try {
      const response = await api.analyzeDocuments();

      // Print the raw response in the browser console
      console.log("===== Analysis Response =====");
      console.log(response.analysis);
      console.log("=============================");

      setAnalysis(response.analysis);
    } catch (err) {
      console.error(err);
      setError(
        "Failed to generate analysis. Ensure your backend is running and documents are indexed."
      );
    } finally {
      stopTimer();
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 flex flex-col h-full">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl shadow border border-gray-200 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">
            Document Analysis
          </h2>
          <p className="text-gray-500 mt-1">
            Generate a comprehensive summary of all indexed intelligence.
          </p>
        </div>

        <button
          onClick={runAnalysis}
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium transition disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Run Full Analysis"}
        </button>
      </div>


      <ProcessingStatus />
      {/* Results */}
      <div className="bg-white rounded-xl shadow border border-gray-200 flex-1 overflow-hidden flex flex-col">
        <div className="bg-gray-50 border-b border-gray-200 px-6 py-4">
          <h3 className="text-lg font-bold text-gray-700">
            Analysis Results
          </h3>
        </div>

        <div className="flex-1 overflow-y-auto p-8 bg-gray-50">

          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500 animate-pulse text-lg">
                Reading and analyzing documents...
              </div>
            </div>
          )}

          {!loading && !analysis && !error && (
            <div className="flex items-center justify-center h-full text-gray-400">
              Click <strong className="mx-1">Run Full Analysis</strong> to
              generate a report.
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          )}

          {analysis && (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
              <ReactMarkdown
                components={{
                  h1: ({ children }) => (
                    <div className="border-b-2 border-blue-200 pb-3 mb-6 mt-8 first:mt-0">
                      <h1 className="text-3xl font-bold text-blue-700">
                        {children}
                      </h1>
                    </div>
                  ),

                  h2: ({ children }) => (
                    <h2 className="text-2xl font-semibold text-gray-800 mt-8 mb-4">
                      {children}
                    </h2>
                  ),

                  h3: ({ children }) => (
                    <h3 className="text-xl font-semibold text-gray-700 mt-6 mb-3">
                      {children}
                    </h3>
                  ),

                  p: ({ children }) => (
                    <p className="text-gray-700 leading-8 mb-4">
                      {children}
                    </p>
                  ),

                  ul: ({ children }) => (
                    <ul className="space-y-3 mb-6">
                      {children}
                    </ul>
                  ),

                  ol: ({ children }) => (
                    <ol className="list-decimal ml-6 space-y-3 mb-6">
                      {children}
                    </ol>
                  ),

                  li: ({ children }) => (
                    <li className="flex items-start gap-3">
                      <span className="text-green-600 font-bold mt-1">✓</span>
                      <span className="text-gray-700 leading-7">
                        {children}
                      </span>
                    </li>
                  ),

                  strong: ({ children }) => (
                    <strong className="font-semibold text-gray-900">
                      {children}
                    </strong>
                  ),

                  code: ({ children }) => (
                    <code className="bg-gray-100 px-1 py-0.5 rounded text-sm text-pink-600">
                      {children}
                    </code>
                  )
                }}
              >
                {analysis}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AnalyzePage;