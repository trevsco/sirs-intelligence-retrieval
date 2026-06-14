import React, { useState, useEffect } from 'react';

function Header({ stats = {} }) {
  const [clock, setClock] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // FIX: Show IST time (UTC+5:30) instead of raw UTC
  const formatIST = (date) => {
    return date.toLocaleString('en-GB', {
      timeZone: 'Asia/Kolkata',
      year:     'numeric',
      month:    '2-digit',
      day:      '2-digit',
      hour:     '2-digit',
      minute:   '2-digit',
      second:   '2-digit',
      hour12:   false,
    }).replace(',', '') + ' IST';
  };

  return (
    <div className="w-full flex flex-col select-none font-sans">

      {/* Top accent bar */}
      <div className="bg-[#0a2240] text-white text-[11px] px-6 py-1.5 flex justify-between items-center border-b border-orange-500 font-mono tracking-wide">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-orange-400">GOVERNMENT OF INDIA</span>
          <span className="text-gray-400">|</span>
          <span>MINISTRY OF DEFENCE</span>
        </div>
        <div className="flex items-center space-x-4 text-xs font-sans">
          <span className="text-orange-400 font-bold">{formatIST(clock)}</span>
        </div>
      </div>

      {/* Main operational header */}
      <header className="h-16 bg-white border-b-2 border-gray-300 flex items-center justify-between px-6 shadow-sm">
        <div className="flex items-center space-x-3">

          {/* FIX: Real DRDO logo image — place drdo-logo.png in frontend/public/ */}
          <img
            src="/drdo-logo.png"
            alt="DRDO"
            className="w-10 h-10 object-contain"
            onError={(e) => {
              // Fallback to text box if image not found
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
          {/* Fallback text box — hidden by default, shown if image fails */}
          <div
            style={{ display: 'none' }}
            className="w-10 h-10 border-2 border-[#0a2240] bg-gray-50 items-center justify-center text-center p-1 text-[8px] font-black leading-none text-[#0a2240]"
          >
            DRDO
          </div>

          <div>
            <h1 className="text-base font-black tracking-tight text-[#0a2240] uppercase">
              Secure Intelligence Retrieval System{' '}
              <span className="text-xs font-normal text-gray-500 tracking-normal normal-case">
                (SIRS-01)
              </span>
            </h1>
            <p className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider -mt-0.5">
              Integrated National Security
            </p>
          </div>
        </div>

        {/* Status blocks */}
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