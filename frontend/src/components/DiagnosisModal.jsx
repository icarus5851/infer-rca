import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { X, Cpu, Database, Activity, FileSearch, Copy, Check } from 'lucide-react';

const CodeBlock = ({ language, value }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group mb-6">
      <div className="absolute right-2 top-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#222222] hover:bg-[#333333] text-gray-300 rounded-md border border-[#444444] text-xs font-medium transition-all shadow-sm"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <SyntaxHighlighter
        children={value}
        style={vscDarkPlus}
        language={language}
        PreTag="div"
        className="rounded-lg border border-[#333333] !bg-[#111111] !m-0 shadow-inner"
      />
    </div>
  );
};

export default function DiagnosisModal({ isOpen, onClose, traceId, loading, result }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-[#000000]/80 backdrop-blur-sm flex items-center justify-center z-50 p-6">
      <div className="bg-[#111111] border border-[#333333] rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden ring-1 ring-white/10">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#333333] flex justify-between items-center bg-[#181818]">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-blue-500" />
            <h2 className="text-lg font-medium text-gray-100">Root Cause Analysis</h2>
            {traceId && (
              <span className="ml-3 px-2.5 py-1 rounded-md bg-[#222222] text-xs font-mono text-gray-400 border border-[#333333] shadow-inner">
                Trace: <span className="text-blue-400">{traceId}</span>
              </span>
            )}
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-[#222222] rounded-lg text-gray-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 relative bg-[#0a0a0a]">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[400px] space-y-6 text-gray-400">
               <div className="relative">
                 <div className="absolute inset-0 bg-blue-500/20 rounded-full blur-xl animate-pulse"></div>
                 <Cpu className="w-12 h-12 text-blue-500 relative z-10 animate-bounce" />
               </div>
               <div className="flex flex-col items-center gap-2">
                 <p className="text-lg font-medium text-gray-200 animate-pulse">Querying Splunk History & AI Engine...</p>
                 <p className="text-sm text-gray-500">Cross-referencing telemetry data with codebase state.</p>
               </div>
            </div>
          ) : result ? (
            <div className="space-y-8 max-w-4xl mx-auto">
              {/* Splunk Context Section */}
              {result.historical_context && (
                <div className="bg-[#111111] rounded-lg border border-[#333333] shadow-sm overflow-hidden">
                  <div className="bg-[#1a1a1a] px-4 py-3 border-b border-[#333333] flex items-center gap-2">
                    <Database className="w-4 h-4 text-emerald-500" />
                    <span className="text-xs font-semibold text-gray-300 uppercase tracking-widest">Splunk Historical Context</span>
                  </div>
                  <div className="p-4 overflow-x-auto">
                    <pre className="text-sm text-emerald-400/90 font-mono leading-relaxed whitespace-pre-wrap">
                      {result.historical_context}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* AI Analysis Section */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <FileSearch className="w-4 h-4 text-blue-500" />
                  <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-widest">AI Analysis & Resolution</h3>
                </div>
                
                {/* Custom Markdown Styling */}
                <div className="text-gray-300 text-[15px] leading-relaxed
                  [&>h1]:text-2xl [&>h1]:font-bold [&>h1]:text-white [&>h1]:mb-5 [&>h1]:pb-2 [&>h1]:border-b [&>h1]:border-[#333333]
                  [&>h2]:text-xl [&>h2]:font-semibold [&>h2]:text-white [&>h2]:mb-4 [&>h2]:mt-8
                  [&>h3]:text-lg [&>h3]:font-medium [&>h3]:text-gray-200 [&>h3]:mb-3 [&>h3]:mt-6
                  [&>p]:mb-5
                  [&>ul]:list-disc [&>ul]:pl-6 [&>ul]:mb-5 [&>ul>li]:mb-1.5 [&>ul>li::marker]:text-gray-500
                  [&>ol]:list-decimal [&>ol]:pl-6 [&>ol]:mb-5 [&>ol>li]:mb-1.5
                  [&>blockquote]:border-l-4 [&>blockquote]:border-blue-500/50 [&>blockquote]:bg-blue-500/5 [&>blockquote]:py-2 [&>blockquote]:pr-4 [&>blockquote]:pl-5 [&>blockquote]:italic [&>blockquote]:text-gray-400 [&>blockquote]:rounded-r-lg [&>blockquote]:mb-5
                  [&>a]:text-blue-500 [&>a]:hover:underline [&>a]:hover:text-blue-400
                ">
                  <ReactMarkdown
                    components={{
                      code({node, inline, className, children, ...props}) {
                        const match = /language-(\w+)/.exec(className || '');
                        const codeString = String(children).replace(/\n$/, '');
                        return !inline && match ? (
                          <CodeBlock language={match[1]} value={codeString} />
                        ) : (
                          <code {...props} className="bg-[#222222] px-1.5 py-0.5 rounded text-blue-300 font-mono text-sm border border-[#333333]">
                            {children}
                          </code>
                        )
                      }
                    }}
                  >
                    {result.analysis}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 space-y-4">
              <Activity className="w-10 h-10 text-gray-600" />
              <p className="text-gray-500">No diagnostic information available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
