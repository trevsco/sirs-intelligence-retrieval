import React, { useState, useEffect, useMemo } from 'react';
import api from '../services/api';

function LogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');
  const [expandedLog, setExpandedLog] = useState(null);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getMCPLogs();
      setLogs((data || []).reverse());
    } catch (err) {
      console.error("Failed to load audit logs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const stats = useMemo(() => {
    const total = logs.length;
    const success = logs.filter(l => l.status === 'success').length;
    const errors = logs.filter(l => l.status === 'error').length;
    const avgLatency = total > 0 
      ? (logs.reduce((sum, l) => sum + l.execution_time_ms, 0) / total).toFixed(2)
      : '0.00';
    return { total, success, errors, avgLatency };
  }, [logs]);

  const filteredLogs = useMemo(() => {
    if (filter === 'success') return logs.filter(l => l.status === 'success');
    if (filter === 'error') return logs.filter(l => l.status === 'error');
    return logs;
  }, [logs, filter]);

  const toggleRowDetails = (msgId) => {
    setExpandedLog(expandedLog === msgId ? null : msgId);
  };

  return (
    <div className="space-y-6">
      
      <div className="bg-white p-6 rounded-lg shadow flex justify-between items-center border border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">System Logs</h2>
          <p className="text-sm text-gray-500 mt-1">Real-time ledger trail capturing all pipeline executions and actions.</p>
        </div>
        <button
          onClick={loadLogs}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Refreshing...' : 'Refresh Logs'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-lg shadow border border-gray-200">
          <span className="text-xs text-gray-500 font-semibold uppercase block">Total Log Entries</span>
          <span className="text-2xl font-bold text-gray-800 block mt-1">{stats.total}</span>
        </div>

        <div className="bg-white p-5 rounded-lg shadow border border-gray-200">
          <span className="text-xs text-gray-500 font-semibold uppercase block">Successful Calls</span>
          <span className="text-2xl font-bold text-green-600 block mt-1">{stats.success}</span>
        </div>

        <div className="bg-white p-5 rounded-lg shadow border border-gray-200">
          <span className="text-xs text-gray-500 font-semibold uppercase block">Error Detections</span>
          <span className="text-2xl font-bold text-red-600 block mt-1">{stats.errors}</span>
        </div>

        <div className="bg-white p-5 rounded-lg shadow border border-gray-200">
          <span className="text-xs text-gray-500 font-semibold uppercase block">Avg Latency</span>
          <span className="text-2xl font-bold text-gray-800 block mt-1">{stats.avgLatency}ms</span>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center flex-wrap gap-4">
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All Logs
            </button>
            <button
              onClick={() => setFilter('success')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                filter === 'success' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Success
            </button>
            <button
              onClick={() => setFilter('error')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                filter === 'error' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Errors
            </button>
          </div>
          <div className="text-xs text-gray-400 font-medium">
            Auto-refreshing every 5 seconds
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="bg-gray-100 border-b border-gray-200 text-gray-600 font-semibold">
                <th className="p-4 text-center w-12">#</th>
                <th className="p-4">Timestamp</th>
                <th className="p-4">Target Tool</th>
                <th className="p-4">Action</th>
                <th className="p-4 text-center">Status</th>
                <th className="p-4 text-right">Latency</th>
                <th className="p-4 text-center w-24">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan="7" className="p-10 text-center text-gray-500">
                    No matching log entries found.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log, index) => {
                  const logNum = filteredLogs.length - index;
                  const isExpanded = expandedLog === log.message_id;
                  return (
                    <React.Fragment key={log.message_id}>
                      <tr 
                        className={`hover:bg-gray-50 cursor-pointer transition-colors ${isExpanded ? 'bg-gray-50' : ''}`}
                        onClick={() => toggleRowDetails(log.message_id)}
                      >
                        <td className="p-4 text-center text-gray-400">{logNum}</td>
                        <td className="p-4 text-gray-700">{log.timestamp?.substring(11, 19) || 'N/A'}</td>
                        <td className="p-4 font-semibold text-gray-800">{log.tool_name}</td>
                        <td className="p-4">
                          <span className="bg-gray-100 px-2 py-0.5 rounded text-xs text-gray-700 border border-gray-200">
                            {log.action}
                          </span>
                        </td>
                        <td className="p-4 text-center">
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                            log.status === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                          }`}>
                            {log.status?.toUpperCase()}
                          </span>
                        </td>
                        <td className="p-4 text-right font-medium text-gray-700">{log.execution_time_ms?.toFixed(2)}ms</td>
                        <td className="p-4 text-center text-blue-600 font-medium text-xs hover:underline">
                          {isExpanded ? 'Hide' : 'Inspect'}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="bg-gray-50">
                          <td colSpan="7" className="p-6 border-l-4 border-blue-500">
                            <div className="space-y-4">
                              <div className="flex justify-between text-xs text-gray-400 border-b border-gray-200 pb-2">
                                <span>ID: <span className="font-semibold text-gray-600">{log.message_id}</span></span>
                                <span>Full Time: <span className="font-semibold text-gray-600">{log.timestamp}</span></span>
                              </div>
                              <div>
                                <span className="text-xs font-bold text-gray-500 block mb-1">Payload:</span>
                                <pre className="bg-white border border-gray-200 rounded p-4 text-xs text-gray-700 overflow-x-auto max-h-48 shadow-inner">
                                  {JSON.stringify(log.payload, null, 2)}
                                </pre>
                              </div>
                              {log.error_detail && (
                                <div className="border border-red-200 bg-red-50 rounded p-4 text-sm text-red-700">
                                  <span className="font-bold text-xs block mb-1 uppercase">Error Details:</span>
                                  {log.error_detail}
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
}

export default LogsPage;