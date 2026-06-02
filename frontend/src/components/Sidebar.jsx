import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Terminal, 
  UploadCloud, 
  ShieldAlert, 
  Cpu,
  FileSearch 
} from 'lucide-react';

function Sidebar() {
  // Reordered: Upload/Ingestion is now directly underneath the Dashboard
  const links = [
    { to: '/dashboard', label: 'SYSTEM OVERVIEW', icon: LayoutDashboard },
    { to: '/upload', label: 'DOCUMENT INGESTION', icon: UploadCloud },
    { to: '/analyze', label: 'INTELLIGENCE SUMMARY', icon: FileSearch },
    { to: '/chat', label: 'SECURE AGENT QUERY', icon: Terminal },
    { to: '/logs', label: 'ACCESS SYSTEM LOGS', icon: ShieldAlert },
    { to: '/settings', label: 'NODE CONFIGURATION', icon: Cpu }
  ];

  return (
    <aside className="w-64 bg-[#0a2240] text-white flex flex-col h-full font-sans border-r-4 border-orange-500">
      
      {/* Sidebar Header Brand Area */}
      <div className="p-5 border-b border-slate-700 bg-slate-900/40 text-center">
        <div className="text-orange-400 font-black text-xs tracking-widest uppercase">SIRS</div>
        <div className="text-[10px] text-gray-400 tracking-wider uppercase mt-0.5">AI INTELLIGENCE SYSTEM</div>
      </div>
      
      {/* Rigid Grid Links */}
      <nav className="flex-1 py-4 space-y-0.5">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-5 py-3 text-xs font-bold tracking-wide transition-all ${
                  isActive 
                    ? 'bg-white/10 text-orange-400 border-l-4 border-orange-500' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white border-l-4 border-transparent'
                }`
              }
            >
              <Icon className="h-4 w-4 text-slate-400 flex-shrink-0" />
              <span>{link.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Security Classification Footer */}
      <div className="p-4 bg-slate-950 border-t border-slate-800 text-[9px] text-gray-400 font-mono space-y-1">
        <div>IP ACCESS LOCKED: INTERNAL</div>
        <div className="text-red-400 font-bold">CLASSIFICATION: RESTRICTED</div>
      </div>
    </aside>
  );
}

export default Sidebar;