import React, { useState, useEffect, useRef } from 'react';
import {
  Share2,
  Filter,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  FileText,
  StickyNote,
  Tag as TagIcon,
  Info,
  Sparkles,
  X
} from 'lucide-react';
import { api } from '../services/api';
import { GraphData, GraphNode } from '../types';

export const KnowledgeGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedGroup, setSelectedGroup] = useState<string>('all');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        setLoading(true);
        const data = await api.getGraph();
        setGraphData(data);
      } catch (err: any) {
        console.error('Failed to load graph data', err);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, []);

  // Initialize and run simple circular / force layout
  useEffect(() => {
    if (!graphData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Filter nodes
    const filteredNodes = graphData.nodes.filter(
      (n) => selectedGroup === 'all' || n.group === selectedGroup
    );
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    const filteredLinks = graphData.links.filter(
      (l) => nodeIds.has(l.source) && nodeIds.has(l.target)
    );

    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;

    // Compute positions in circle layout with force repulsion
    filteredNodes.forEach((node, i) => {
      if (node.x === undefined || node.y === undefined) {
        const angle = (i / filteredNodes.length) * 2 * Math.PI;
        const radius = node.group === 'tag' ? 120 : 220;
        node.x = centerX + radius * Math.cos(angle);
        node.y = centerY + radius * Math.sin(angle);
      }
    });

    const render = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.save();
      ctx.translate(offset.x, offset.y);
      ctx.scale(zoom, zoom);

      // Draw links
      filteredLinks.forEach((link) => {
        const sourceNode = filteredNodes.find((n) => n.id === link.source);
        const targetNode = filteredNodes.find((n) => n.id === link.target);
        if (!sourceNode || !targetNode || sourceNode.x === undefined || targetNode.x === undefined)
          return;

        ctx.beginPath();
        ctx.moveTo(sourceNode.x, sourceNode.y!);
        ctx.lineTo(targetNode.x, targetNode.y!);
        ctx.strokeStyle =
          link.relation === 'semantic_similarity'
            ? 'rgba(16, 185, 129, 0.4)'
            : 'rgba(148, 163, 184, 0.3)';
        ctx.lineWidth = link.weight || 1;
        ctx.stroke();
      });

      // Draw nodes
      filteredNodes.forEach((node) => {
        if (node.x === undefined || node.y === undefined) return;

        const isSelected = selectedNode?.id === node.id;
        const radius = node.group === 'tag' ? 14 : node.group === 'document' ? 20 : 16;

        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);

        if (node.group === 'tag') {
          ctx.fillStyle = '#059669'; // Emerald
        } else if (node.group === 'document') {
          ctx.fillStyle = '#2563eb'; // Blue
        } else {
          ctx.fillStyle = '#9333ea'; // Purple
        }

        ctx.fill();

        if (isSelected) {
          ctx.lineWidth = 3;
          ctx.strokeStyle = '#f59e0b'; // Amber ring
          ctx.stroke();
        }

        // Draw node labels
        ctx.fillStyle = '#0f172a';
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'center';
        const label = node.label.length > 18 ? node.label.slice(0, 15) + '...' : node.label;
        ctx.fillText(label, node.x, node.y + radius + 14);
      });

      ctx.restore();
    };

    render();
  }, [graphData, selectedGroup, zoom, offset, selectedNode]);

  // Canvas interaction handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging) return;
    setOffset({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!graphData || !canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const clickX = (e.clientX - rect.left - offset.x) / zoom;
    const clickY = (e.clientY - rect.top - offset.y) / zoom;

    const clicked = graphData.nodes.find((node) => {
      if (node.x === undefined || node.y === undefined) return false;
      const dx = node.x - clickX;
      const dy = node.y - clickY;
      return Math.sqrt(dx * dx + dy * dy) <= 22;
    });

    setSelectedNode(clicked || null);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Interactive Knowledge Graph</h1>
          <p className="text-sm text-slate-500">
            Visualize relationships between documents, notes, tags, and conceptual connections.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center space-x-2">
          {['all', 'document', 'note', 'tag'].map((group) => (
            <button
              key={group}
              onClick={() => setSelectedGroup(group)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize transition-all ${
                selectedGroup === group
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
              }`}
            >
              {group === 'all' ? 'All Nodes' : `${group}s`}
            </button>
          ))}
        </div>
      </div>

      {/* Main Canvas & Details Panel Container */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm relative overflow-hidden h-[620px] flex">
        {/* Canvas Area */}
        <div className="flex-1 relative bg-slate-50/60">
          <canvas
            ref={canvasRef}
            width={900}
            height={600}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onClick={handleCanvasClick}
            className="w-full h-full cursor-grab active:cursor-grabbing"
          />

          {/* Zoom & Reset Controls Overlay */}
          <div className="absolute bottom-5 left-5 bg-white/90 backdrop-blur-md border border-slate-200 rounded-2xl shadow-md p-1.5 flex items-center space-x-1">
            <button
              onClick={() => setZoom((z) => Math.min(z + 0.2, 2.5))}
              className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => setZoom((z) => Math.max(z - 0.2, 0.4))}
              className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                setZoom(1);
                setOffset({ x: 0, y: 0 });
              }}
              className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
              title="Reset View"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          {/* Legend Overlay */}
          <div className="absolute top-5 left-5 bg-white/90 backdrop-blur-md border border-slate-200 rounded-2xl shadow-sm p-3 text-xs space-y-2">
            <p className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">Legend</p>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-blue-600" />
              <span className="text-slate-600">Documents</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-purple-600" />
              <span className="text-slate-600">Notes</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-emerald-600" />
              <span className="text-slate-600">Tags / Topics</span>
            </div>
          </div>
        </div>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="w-80 border-l border-slate-200 bg-white p-6 overflow-y-auto space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                {selectedNode.group}
              </span>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div>
              <h3 className="font-bold text-slate-900 text-lg leading-snug">{selectedNode.label}</h3>
              {selectedNode.meta?.category && (
                <p className="text-xs text-slate-500 mt-1">Category: {selectedNode.meta.category}</p>
              )}
            </div>

            {selectedNode.meta?.summary && (
              <div className="space-y-1.5">
                <p className="text-xs font-semibold text-slate-700">Summary:</p>
                <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                  {selectedNode.meta.summary}
                </p>
              </div>
            )}

            <div className="pt-2">
              <p className="text-xs text-slate-400 font-mono">Node ID: {selectedNode.id}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
