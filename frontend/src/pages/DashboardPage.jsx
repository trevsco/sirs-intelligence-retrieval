import React, { useState, useEffect } from 'react';
import api from '../services/api';

function DashboardPage({ stats = {}, refreshStats }) {
  const [loading, setLoading] = useState(false);
  const [details, setDetails] = useState({
    document_count: 0,
    mcp_tools: [],
    llm: { configured_model: 'N/A' }
  });
  const [config, setConfig] = useState({});

  const loadDashboardDetails = async () => {
    setLoading(true);
    try {
      if (refreshStats) {
        await refreshStats();
      }
      const statusData = await api.getSystemStatus();
      setDetails({
        document_count: statusData.vector_store?.document_count || 0,
        mcp_tools: statusData.mcp_tools || [],
        llm: statusData.llm || {}
      });
      
      const settingsData = await api.getSettings();
      setConfig(settingsData || {});
    } catch (err) {
      console.error("Failed to load dashboard details:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardDetails();
  }, []);

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow flex justify-between items-center border border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
          <p className="text-gray-500 text-sm">System status and configuration overview.</p>
        </div>
        <button
          onClick={loadDashboardDetails}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Refreshing...' : 'Refresh Nodes'}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="text-sm text-gray-500 font-semibold uppercase">Vectors Indexed</div>
          <div className="text-3xl font-bold text-gray-800 mt-2">{stats.chunk_count || 0}</div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="text-sm text-gray-500 font-semibold uppercase">Locked Sources</div>
          <div className="text-3xl font-bold text-gray-800 mt-2">{details.document_count}</div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="text-sm text-gray-500 font-semibold uppercase">MCP Tools</div>
          <div className="text-3xl font-bold text-gray-800 mt-2">{details.mcp_tools.length}</div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="text-sm text-gray-500 font-semibold uppercase">LLM Status</div>
          <div className="mt-2 flex items-center justify-between">
            <span className="font-medium text-gray-800">{details.llm.configured_model || 'Unknown'}</span>
            <span className={`text-sm font-bold px-2 py-1 rounded ${stats.llm_online ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {stats.llm_online ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Tools List */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-bold text-gray-700">Registered MCP Tools</h3>
          </div>
          <div className="p-6">
            {details.mcp_tools.length === 0 ? (
              <p className="text-gray-500">No active tools found.</p>
            ) : (
              <div className="space-y-6">
                {details.mcp_tools.map((tool, idx) => (
                  <div key={tool.name} className={idx !== 0 ? "pt-6 border-t border-gray-100" : ""}>
                    <h4 className="font-bold text-gray-800 text-lg">{tool.name}</h4>
                    <p className="text-gray-600 text-sm mt-1">{tool.description}</p>
                    <div className="mt-3">
                      <span className="text-xs font-semibold text-gray-500 uppercase">Actions Schema:</span>
                      <pre className="bg-gray-100 p-3 rounded-md text-sm mt-1 text-gray-700 overflow-x-auto">
                        {JSON.stringify(tool.actions, null, 2)}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Configuration Overview */}
        <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-bold text-gray-700">Pipeline Config</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex justify-between border-b border-gray-100 pb-2">
                <span className="text-gray-600">Chunk Size</span>
                <span className="font-semibold text-gray-800">{config.CHUNK_SIZE || 512}</span>
              </div>
              <div className="flex justify-between border-b border-gray-100 pb-2">
                <span className="text-gray-600">Chunk Overlap</span>
                <span className="font-semibold text-gray-800">{config.CHUNK_OVERLAP || 64}</span>
              </div>
              <div className="flex justify-between border-b border-gray-100 pb-2">
                <span className="text-gray-600">Sim. Cutoff</span>
                <span className="font-semibold text-gray-800">{config.SIMILARITY_THRESHOLD || '0.0'}</span>
              </div>
              <div className="flex justify-between border-b border-gray-100 pb-2">
                <span className="text-gray-600">Top K</span>
                <span className="font-semibold text-gray-800">{config.TOP_K || 5}</span>
              </div>
              <div className="flex justify-between border-b border-gray-100 pb-2">
                <span className="text-gray-600">Model Space</span>
                <span className="font-semibold text-gray-800">{config.EMBEDDING_MODEL || 'N/A'}</span>
              </div>
              <div className="flex justify-between pb-2">
                <span className="text-gray-600">Temperature</span>
                <span className="font-semibold text-gray-800">{config.LLM_TEMPERATURE || 0.1}</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default DashboardPage;