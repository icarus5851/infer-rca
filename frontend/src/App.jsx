import React, { useState } from 'react';
import { ReactFlowProvider } from 'reactflow';
import { Activity, LayoutDashboard, Terminal } from 'lucide-react';
import FlowCanvas from './components/FlowCanvas';
import LiveMonitor from './components/LiveMonitor';
import './index.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('map'); // 'map' or 'monitor'

  return (
    <div className="w-screen h-screen flex flex-col bg-[#000000] font-sans text-gray-200">
      
      {/* Top Navigation Bar */}
      <header className="px-6 py-4 bg-[#111111] border-b border-[#333333] flex justify-between items-center z-10">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-[#222222] rounded-md border border-[#333333]">
              <Activity className="w-5 h-5 text-blue-500" />
            </div>
            <h1 className="text-xl font-semibold tracking-wide text-gray-100">
              Infer
            </h1>
          </div>
          
          {/* Navigation Tabs */}
          <nav className="flex items-center gap-2">
            <button 
              onClick={() => setActiveTab('map')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'map' 
                  ? 'bg-[#222222] text-white border border-[#444444]' 
                  : 'text-gray-400 hover:text-gray-200 hover:bg-[#1a1a1a] border border-transparent'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Architecture Map
            </button>
            <button 
              onClick={() => setActiveTab('monitor')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'monitor' 
                  ? 'bg-[#222222] text-white border border-[#444444]' 
                  : 'text-gray-400 hover:text-gray-200 hover:bg-[#1a1a1a] border border-transparent'
              }`}
            >
              <Terminal className="w-4 h-4" />
              Live Monitor
            </button>
          </nav>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#0a0a0a] rounded-md border border-[#333333]">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-xs text-gray-400 font-mono tracking-wider uppercase">Connected</span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden relative">
        {activeTab === 'map' ? (
          <ReactFlowProvider>
            <FlowCanvas />
          </ReactFlowProvider>
        ) : (
          <LiveMonitor />
        )}
      </div>
    </div>
  );
}