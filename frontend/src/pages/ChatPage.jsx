
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import IEEEComplianceReport from '../components/IEEEComplianceReport';

function ChatPage({ refreshStats }) {

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  // Document selection
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState("");

  useEffect(() => {

    async function loadDocuments() {

      try {

        const data = await api.getDocuments();

        setDocuments(data);

        if (data.length > 0) {
          setSelectedDoc(data[0].doc_id);
        }

      } catch (err) {

        console.error(
          "Could not load documents",
          err
        );

      }

    }

    loadDocuments();

  }, []);

  const handleSend = async (e, overrideText = null) => {

    if (e) e.preventDefault();

    const currentQuery = overrideText || query;

    if (!currentQuery.trim() || !selectedDoc)
      return;

    setHistory(prev => [
      ...prev,
      {
        role: 'user',
        content: currentQuery
      }
    ]);

    if (!overrideText)
      setQuery('');

    setLoading(true);

    try {
      const topK = overrideText ? 10 : 6;

      const response = await api.query(
        currentQuery,
        selectedDoc,
        topK,
        0.0
      );

      if (refreshStats) {
        await refreshStats();
      }

      setHistory(prev => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          compliance_report: response.compliance_report || null
        }
      ]);

    } catch (err) {

      console.error(err);

      setHistory(prev => [
        ...prev,
        {
          role: 'assistant',
          error: true,
          content: 'Error: Could not get a response.'
        }
      ]);

    } finally {

      setLoading(false);

    }
  };

  const handleAnalyze = () => {

    const analysisPrompt =
      "Give a concise summary of the selected document. Then list definitions or explicitly explained technical terms from the retrieved context only. Keep each definition brief.";

    handleSend(
      null,
      analysisPrompt
    );

  };

  return (

    <div className="flex flex-col h-full bg-white rounded-lg shadow overflow-hidden">

      {/* Header */}
      <div className="bg-gray-50 border-b border-gray-200 p-4 flex justify-between items-center gap-4">

        <div className="flex items-center gap-4">

          <h2 className="text-lg font-bold text-gray-700">
            Intelligence Query
          </h2>

          <select
            value={selectedDoc}
            onChange={(e) => setSelectedDoc(e.target.value)}
            disabled={loading || documents.length === 0}
            className="border border-gray-300 rounded px-3 py-2 text-sm bg-white"
          >

            {
              documents.length === 0
                ? (
                  <option value="">
                    No documents available
                  </option>
                )
                : (
                  documents.map(doc => (

                    <option
                      key={doc.doc_id}
                      value={doc.doc_id}
                    >
                      {doc.filename}
                    </option>

                  ))
                )
            }

          </select>

        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading || !selectedDoc}
          className="bg-indigo-100 text-indigo-700 hover:bg-indigo-200 px-4 py-2 rounded-md text-sm font-semibold transition-colors disabled:opacity-50"
        >
          {
            loading
              ? "Processing..."
              : "Analyze & Summarize Data"
          }
        </button>

      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">

        {
          history.length === 0
            ? (
              <div className="text-center text-gray-500 mt-10">

                <h3 className="text-lg font-semibold text-gray-700">
                  Ready to query your documents.
                </h3>

                <p className="mt-2 text-sm">
                  Type a question below, or click
                  <strong> Analyze & Summarize </strong>
                  to get an overview first.
                </p>

              </div>
            )
            : (
              history.map((msg, idx) => (

                <div
                  key={idx}
                  className={`flex ${
                    msg.role === 'user'
                      ? 'justify-end'
                      : 'justify-start'
                  }`}
                >

                  <div
                    className={`max-w-[75%] ${
                      msg.role === 'user'
                        ? ''
                        : 'w-full'
                    }`}
                  >

                    <div
                      className={`rounded-lg px-4 py-3 ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : msg.error
                            ? 'bg-red-50 text-red-600 border border-red-200'
                            : 'bg-gray-100 text-gray-800'
                      }`}
                    >

                      <div className="text-xs font-semibold mb-1 opacity-75">
                        {
                          msg.role === 'user'
                            ? 'You'
                            : 'System'
                        }
                      </div>

                      <div className="whitespace-pre-wrap text-sm">
                        {msg.content}
                      </div>

                    </div>

                    {
                      msg.role === 'assistant'
                      &&
                      !msg.error
                      &&
                      msg.compliance_report
                      &&
                      (
                        <div className="mt-3">

                          <IEEEComplianceReport
                            report={msg.compliance_report}
                          />

                        </div>
                      )
                    }

                  </div>

                </div>

              ))
            )
        }

        {
          loading && (

            <div className="flex justify-start">

              <div className="bg-gray-100 text-gray-500 rounded-lg px-4 py-3 text-sm">
                Analyzing...
              </div>

            </div>

          )
        }

      </div>

      {/* Input */}
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
          disabled={
            loading
            ||
            !query.trim()
            ||
            !selectedDoc
          }
          className="bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          Send
        </button>

      </form>

    </div>

  );
}

export default ChatPage;

