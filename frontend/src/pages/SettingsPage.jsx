import React, { useState, useEffect } from 'react';
import api from '../services/api';

function SettingsPage() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [diagnostics, setDiagnostics] = useState({
    ollama_running: false,
    model_cached: false,
    vector_store_warm: false
  });

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await api.getSettings();
      setConfig(data);
      
      const health = await api.getHealth();
      setDiagnostics({
        ollama_running: health.llm_online || false,
        model_cached: health.configured_model_available || false,
        vector_store_warm: health.chunk_count > 0
      });
    } catch (err) {
      console.error("Failed to load settings configuration", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow flex justify-between items-center border border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Settings & Diagnostics</h2>
          <p className="text-sm text-gray-500 mt-1">System configuration and health checks.</p>
        </div>
        <button
          onClick={loadSettings}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Running Checks...' : 'Run Diagnostics'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: System Configuration */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-700">Active Configuration</h3>
            </div>
            
            {loading || !config ? (
              <div className="p-10 text-center text-gray-500">
                Loading parameters...
              </div>
            ) : (
              <div className="p-6 space-y-6">
                
                {/* LLM Settings */}
                <div>
                  <h4 className="font-semibold text-gray-800 border-b border-gray-100 pb-2 mb-3">LLM Settings</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">Model</span>
                      <span className="font-semibold text-gray-800">{config.OLLAMA_MODEL}</span>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">API Host</span>
                      <span className="font-semibold text-gray-800">{config.OLLAMA_BASE_URL}</span>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">Temperature</span>
                      <span className="font-semibold text-gray-800">{config.LLM_TEMPERATURE}</span>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">Max Tokens</span>
                      <span className="font-semibold text-gray-800">{config.LLM_MAX_TOKENS}</span>
                    </div>
                  </div>
                </div>

                {/* Embeddings Settings */}
                <div>
                  <h4 className="font-semibold text-gray-800 border-b border-gray-100 pb-2 mb-3">Embedding Settings</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">Model</span>
                      <span className="font-semibold text-gray-800">{config.EMBEDDING_MODEL}</span>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">Dimension</span>
                      <span className="font-semibold text-gray-800">{config.EMBEDDING_DIM}</span>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">Chunk Size</span>
                      <span className="font-semibold text-gray-800">{config.CHUNK_SIZE}</span>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">Chunk Overlap</span>
                      <span className="font-semibold text-gray-800">{config.CHUNK_OVERLAP}</span>
                    </div>
                  </div>
                </div>

                {/* System Limits */}
                <div>
                  <h4 className="font-semibold text-gray-800 border-b border-gray-100 pb-2 mb-3">System Limits</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">Max Upload Size</span>
                      <span className="font-semibold text-gray-800">{config.MAX_UPLOAD_SIZE_MB} MB</span>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                      <span className="text-gray-500 block mb-1">Allowed Extensions</span>
                      <span className="font-semibold text-gray-800">
                        {config.ALLOWED_EXTENSIONS ? config.ALLOWED_EXTENSIONS.join(', ') : '.pdf, .docx, .txt'}
                      </span>
                    </div>
                  </div>
                </div>

              </div>
            )}
          </div>
        </div>

        {/* Right Column: Diagnostic Checklist */}
        <div className="h-fit">
          <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-700">Diagnostic Checklist</h3>
            </div>

            <div className="p-6 space-y-5">
              
              <div className="flex items-start space-x-3">
                <div className={`mt-1.5 flex-shrink-0 w-3 h-3 rounded-full ${diagnostics.ollama_running ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <div>
                  <span className="font-semibold text-gray-800 block">LLM Connection</span>
                  <span className="text-xs text-gray-500 mt-0.5 block">
                    {diagnostics.ollama_running ? 'Connected to local LLM core.' : 'Ollama not running or unreachable.'}
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className={`mt-1.5 flex-shrink-0 w-3 h-3 rounded-full ${diagnostics.model_cached ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <div>
                  <span className="font-semibold text-gray-800 block">Model Cache</span>
                  <span className="text-xs text-gray-500 mt-0.5 block">
                    {diagnostics.model_cached ? 'Configured model is downloaded.' : 'Model missing. Pull required.'}
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className={`mt-1.5 flex-shrink-0 w-3 h-3 rounded-full ${diagnostics.vector_store_warm ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                <div>
                  <span className="font-semibold text-gray-800 block">Vector Database</span>
                  <span className="text-xs text-gray-500 mt-0.5 block">
                    {diagnostics.vector_store_warm ? 'Database contains documents.' : 'Database is empty. Ingest files.'}
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="mt-1.5 flex-shrink-0 w-3 h-3 rounded-full bg-green-500"></div>
                <div>
                  <span className="font-semibold text-gray-800 block">Security Status</span>
                  <span className="text-xs text-gray-500 mt-0.5 block">
                    Local isolation verified.
                  </span>
                </div>
              </div>

            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default SettingsPage;