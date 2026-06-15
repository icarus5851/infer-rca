import React, { useState, useEffect } from 'react';
import { Terminal, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function LiveMonitor() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:5050/live-logs');
        const data = await response.json();
        if (data.logs) {
          setLogs([...data.logs]);
        }
      } catch (error) {
        // Silently fail if down
      }
    }, 1000);
    return () => clearInterval(pollInterval);
  }, []);

  return (
    <div className="w-full h-full bg-[#0a0a0a] flex flex-col font-mono text-sm">
      <div className="p-4 border-b border-[#333333] flex items-center gap-3 bg-[#111111]">
        <Terminal className="w-5 h-5 text-gray-400" />
        <h2 className="text-sm font-semibold text-gray-200 uppercase tracking-widest">Live Execution Logs</h2>
        <div className="ml-auto flex items-center gap-2">
           <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-xs text-gray-500 uppercase tracking-wide">Monitoring</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto bg-[#0a0a0a]">
        <table className="w-full text-left text-sm text-gray-400">
          <thead className="text-xs uppercase bg-[#181818] text-gray-500 sticky top-0 border-b border-[#333333] z-10">
            <tr>
              <th className="px-6 py-4 font-medium border-b border-[#333333]">Timestamp</th>
              <th className="px-6 py-4 font-medium border-b border-[#333333]">Status</th>
              <th className="px-6 py-4 font-medium border-b border-[#333333]">Endpoint</th>
              <th className="px-6 py-4 font-medium border-b border-[#333333]">File</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, i) => (
              <tr 
                key={i} 
                className={`border-b border-[#222222] hover:bg-[#151515] transition-colors
                  ${log.status === 'ERROR' ? 'bg-[#3b0d0d]/10 hover:bg-[#3b0d0d]/30' : ''}
                `}
              >
                <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                  {new Date(log.timestamp * 1000).toISOString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    {log.status === 'ERROR' ? (
                      <><AlertCircle className="w-4 h-4 text-red-500" /><span className="text-red-500 font-semibold">{log.status}</span></>
                    ) : (
                      <><CheckCircle2 className="w-4 h-4 text-emerald-500" /><span className="text-emerald-500 font-semibold">{log.status}</span></>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 font-mono text-blue-400">
                  {log.endpoint || '-'}
                </td>
                <td className="px-6 py-4 font-mono text-gray-300">
                  {log.file || '-'}
                </td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan="4" className="px-6 py-8 text-center text-gray-600">Waiting for incoming logs...</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
