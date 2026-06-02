import React, { useState, useEffect } from 'react';

function Header({ stats = {} }) {
  const [clock, setClock] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full flex flex-col select-none font-sans">
      
      {/* 1. Indian Gov Top Accent Bar (Cleaned) */}
      <div className="bg-[#0a2240] text-white text-[11px] px-6 py-1.5 flex justify-between items-center border-b border-orange-500 font-mono tracking-wide">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-orange-400">GOVERNMENT OF INDIA</span>
          <span className="text-gray-400">|</span>
          <span>MINISTRY OF DEFENCE</span>
        </div>
        <div className="flex items-center space-x-4 text-xs font-sans">
          <span className="text-orange-400 font-bold">{clock.toISOString().replace('T', ' ').substring(0, 19)} UTC</span>
        </div>
      </div>

      {/* 3. Main Operational Header */}
      <header className="h-16 bg-white border-b-2 border-gray-300 flex items-center justify-between px-6 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 border-2 border-[#0a2240] bg-gray-50 flex items-center justify-center text-center p-1 text-[8px] font-black leading-none text-[#0a2240]">
            DRDO
          </div>
          <div>
            <h1 className="text-base font-black tracking-tight text-[#0a2240] uppercase">
              Secure Intelligence Retrieval System <span className="text-xs font-normal text-gray-500 tracking-normal text-transform-none">(SIRS-01)</span>
            </h1>
            <p className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider -mt-0.5">
              Integrated National Security
            </p>
          </div>
        </div>
        
        {/* Connection status blocks */}
        <div className="flex items-center space-x-4 text-xs">
          <div className="bg-gray-100 border border-gray-300 px-3 py-1 text-gray-700 font-mono rounded-none">
            System: <span className="text-green-700 font-bold">SECURE</span>
          </div>
          <div className="bg-gray-100 border border-gray-300 px-3 py-1 text-gray-700 font-mono rounded-none">
            LLM: <span className="font-bold text-blue-800 uppercase">{stats.llm_model || 'OFFLINE'}</span>
          </div>
        </div>
      </header>
    </div>
  );
}

export default Header;