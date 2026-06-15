import React, { useState, useEffect, useRef } from 'react';
import { Terminal, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function LiveLogs() {
  const [logs, setLogs] = useState([]);
  const logsEndRef = useRef(null);

  useEffect(() => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:5050/live-logs');
        const data = await response.json();
        if (data.logs) {
          setLogs([...data.logs].reverse());
        }
      } catch (error) {
        // Silently fail if down
      }
    }, 1000);
    return () => clearInterval(pollInterval);
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="w-80 border-l border-slate-800 bg-slate-900/50 flex flex-col backdrop-blur-sm z-10 relative shadow-xl">
      <div className="p-4 border-b border-slate-800 flex items-center gap-2 bg-slate-900">
        <Terminal className="w-4 h-4 text-slate-400" />
        <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wide">Live Log Trail</h2>
        <div className="ml-auto flex items-center gap-2">
           <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs">
        {logs.map((log, i) => (
          <div key={i} className={`p-3 rounded border ${log.status === 'ERROR' ? 'bg-red-950/30 border-red-900/50 text-red-200' : 'bg-slate-800/30 border-slate-700/50 text-slate-300'}`}>
            <div className="flex items-center gap-2 mb-1.5 border-b border-white/5 pb-1.5">
              {log.status === 'ERROR' ? <AlertCircle className="w-3 h-3 text-red-500" /> : <CheckCircle2 className="w-3 h-3 text-emerald-500" />}
              <span className="opacity-60">{new Date(log.timestamp * 1000).toLocaleTimeString()}</span>
              <span className={`ml-auto text-[10px] font-bold tracking-wider ${log.status === 'ERROR' ? 'text-red-400' : 'text-emerald-400'}`}>{log.status}</span>
            </div>
            <div className="break-all mt-1 flex flex-col gap-1">
              {log.endpoint && <div><span className="opacity-50">EP:</span> <span className="text-blue-400">{log.endpoint}</span></div>}
              {log.file && <div><span className="opacity-50">FILE:</span> <span className="text-amber-200/80">{log.file}</span></div>}
            </div>
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}
