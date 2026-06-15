import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  applyNodeChanges, 
  applyEdgeChanges,
  useReactFlow
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Stethoscope } from 'lucide-react';
import DiagnosisModal from './DiagnosisModal';

export default function FlowCanvas() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [crashedState, setCrashedState] = useState(null); 
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { fitView } = useReactFlow();

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  useEffect(() => {
    async function fetchGraphData() {
      try {
        const response = await fetch('http://localhost:5050/graph-data');
        const data = await response.json();

        if (data.error || !data.nodes) return;

        const styledNodes = data.nodes.map((node, index) => {
          const isEntryPoint = node.id === 'target_app.py';
          
          return {
            ...node,
            position: { x: isEntryPoint ? 100 : 400 + (index * 20), y: 150 + (index * 100) },
            sourcePosition: 'right',
            targetPosition: 'left',
            style: {
              background: isEntryPoint ? '#111111' : '#0a0a0a', 
              color: '#ffffff',
              border: isEntryPoint ? '1px solid #3b82f6' : '1px solid #333333', 
              borderRadius: '6px',
              padding: '16px',
              width: 220,
            },
            data: {
              label: (
                <div className="flex flex-col text-left">
                  {isEntryPoint && (
                    <span className="text-xs font-semibold text-blue-500 mb-1 uppercase tracking-wider">
                      Entry Point
                    </span>
                  )}
                  <span className="font-mono text-[15px] truncate text-gray-200">{node.id}</span>
                </div>
              )
            }
          };
        });

        const styledEdges = data.edges.map((edge) => ({
          ...edge,
          animated: true,
          style: { stroke: '#444444', strokeWidth: 2 },
        }));

        setNodes(styledNodes);
        setEdges(styledEdges);
        
        // Auto-fit the view once data loads
        setTimeout(() => fitView({ padding: 0.2 }), 100);
        
      } catch (error) {
        console.error("Failed to connect to Infer Agent:", error);
      }
    }
    fetchGraphData();
  }, [fitView]);

  // Polling mechanism to check for crashes
  useEffect(() => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:5050/latest-crash');
        const data = await response.json();

        // If the backend reports a crashed node, update the UI
        if (data.crashed_node) {
          setCrashedState({ node: data.crashed_node, traceId: data.trace_id });
          setNodes((currentNodes) => 
            currentNodes.map((node) => {
              if (node.id === data.crashed_node) {
                return {
                  ...node,
                  style: {
                    ...node.style,
                    background: '#2b0a0a',       // Dark Red Background
                    border: '1px solid #ef4444', // Bright Red Border
                    color: '#ffffff',
                  },
                };
              }
              // Reset all other nodes to default (in case the crash moves)
              return {
                ...node,
                style: {
                  ...node.style,
                  background: node.id === 'target_app.py' ? '#111111' : '#0a0a0a',
                  border: node.id === 'target_app.py' ? '1px solid #3b82f6' : '1px solid #333333',
                }
              };
            })
          );
        } else {
          setCrashedState(null);
          setNodes((currentNodes) => 
            currentNodes.map((node) => ({
              ...node,
              style: {
                ...node.style,
                background: node.id === 'target_app.py' ? '#111111' : '#0a0a0a',
                border: node.id === 'target_app.py' ? '1px solid #3b82f6' : '1px solid #333333',
              }
            }))
          );
        }
      } catch (error) {
        // Silently fail if the agent is down so it doesn't clutter the console
      }
    }, 2000); // Poll every 2000 milliseconds (2 seconds)

    // Cleanup interval on unmount
    return () => clearInterval(pollInterval);
  }, [setNodes]);

  const handleDiagnose = async () => {
    if (!crashedState?.traceId) return;
    
    setIsDiagnosing(true);
    setDiagnosisResult(null);
    setIsModalOpen(true);
    
    try {
      const res = await fetch(`http://localhost:5050/diagnose/${crashedState.traceId}`, {
        method: 'POST'
      });
      const data = await res.json();
      setDiagnosisResult(data);
    } catch (error) {
      console.error("Diagnosis failed:", error);
      setDiagnosisResult({ 
        analysis: "### Error\n\nFailed to connect to the diagnostic service or analyze the issue.", 
        historical_context: null 
      });
    } finally {
      setIsDiagnosing(false);
    }
  };

  return (
    <div className="w-full h-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        className="bg-[#050505]" // Very dark monochrome background
      >
        <Background color="#222222" gap={24} size={1} />
        <Controls showInteractive={false} className="bg-[#111111] border-[#333333] shadow-lg" />
      </ReactFlow>
      
      {/* Floating Diagnose Button */}
      {crashedState && (
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20 animate-in slide-in-from-bottom-4 fade-in duration-300">
          <button
            onClick={handleDiagnose}
            className="flex items-center gap-3 px-8 py-3 bg-red-600 hover:bg-red-500 text-white rounded shadow-[0_0_15px_rgba(220,38,38,0.3)] transition-all transform hover:scale-105 border border-red-500 font-semibold tracking-wide"
          >
            <Stethoscope className="w-5 h-5" />
            Diagnose Issue ({crashedState.node})
          </button>
        </div>
      )}

      {/* Diagnosis Modal */}
      <DiagnosisModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        traceId={crashedState?.traceId}
        loading={isDiagnosing}
        result={diagnosisResult}
      />
    </div>
  );
}
