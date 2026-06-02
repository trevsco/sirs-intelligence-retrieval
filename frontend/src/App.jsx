import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardPage from './pages/DashboardPage';
import AnalyzePage from './pages/AnalyzePage';
import ChatPage from './pages/ChatPage';
import UploadPage from './pages/UploadPage';
import LogsPage from './pages/LogsPage';
import SettingsPage from './pages/SettingsPage';
import api from './services/api';

function App() {
  const [stats, setStats] = useState({
    status: 'connecting',
    llm_online: false,
    llm_model: 'Unknown',
    chunk_count: 0,
    configured_model_available: false
  });

  const fetchStats = async () => {
    try {
      const data = await api.getHealth();
      setStats({
        status: data.status,
        llm_online: data.llm_online,
        llm_model: data.llm_model,
        chunk_count: data.chunk_count,
        configured_model_available: data.configured_model_available
      });
    } catch (err) {
      console.error("Health polling failed", err);
      setStats(prev => ({ ...prev, status: 'error', llm_online: false }));
    }
  };

  useEffect(() => {
    fetchStats();
    const timer = setInterval(fetchStats, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <Router>
      {/* Official Government Gray Desktop Base Wrapper Layer */}
      <div className="flex h-screen bg-[#f4f6f9] text-gray-900 font-sans overflow-hidden select-none">
        
        {/* Authoritative Saffron-Bordered Navigation Column */}
        <Sidebar />

        {/* Operational View Container */}
        <div className="flex flex-col flex-1 overflow-hidden">
          
          {/* Dual-Tiered National Emblem & Classification Header Assembly */}
          <Header stats={stats} />
          
          {/* Main Bureaucratic Workspace Core */}
          <main className="flex-1 overflow-y-auto p-6 relative">
            <Routes>
              <Route path="/dashboard" element={<DashboardPage stats={stats} refreshStats={fetchStats} />} />
              <Route path="/analyze" element={<AnalyzePage />} />
              <Route path="/chat" element={<ChatPage refreshStats={fetchStats} />} />
              <Route path="/upload" element={<UploadPage refreshStats={fetchStats} />} />
              <Route path="/logs" element={<LogsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
          
        </div>
      </div>
    </Router>
  );
}

export default App;