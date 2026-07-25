import React, { useState, useMemo } from 'react';
import {
  Share2,
  Users,
  Filter,
  X,
  Link,
  Layers,
  Search,
  FilterX,
  RotateCcw
} from 'lucide-react';

// Custom position generator for graph nodes in SVG canvas
const getNodeColor = (type, metadata = {}) => {
  if (type === 'Accused') {
    return metadata.is_repeat_offender ? '#f43f5e' : '#ef4444';
  }
  if (type === 'Victim') return '#0284c7';
  if (type === 'Unit') return '#10b981';
  if (type === 'CaseMaster') return '#f59e0b';
  return '#64748b';
};

const getNodeIcon = (type) => {
  if (type === 'Accused') return '👤';
  if (type === 'Victim') return '🛡️';
  if (type === 'Unit') return '🏛️';
  if (type === 'CaseMaster') return '📋';
  return '📌';
};

export default function NetworkGraphPanel({ networkData = { summary: {}, nodes: [], edges: [] } }) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [filterType, setFilterType] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  const nodes = networkData.nodes || [];
  const edges = networkData.edges || [];
  const summary = networkData.summary || {
    total_nodes: nodes.length,
    total_edges: edges.length,
    repeat_offenders_count: nodes.filter((n) => n.type === 'Accused' && n.metadata?.is_repeat_offender).length
  };

  // Pre-calculate circular/grid layout coordinates for nodes in SVG 800x480 viewport
  const positionedNodes = useMemo(() => {
    const filtered = nodes.filter((n) => {
      const matchesFilter = filterType === 'All' || n.type === filterType;
      const matchesSearch =
        !searchTerm ||
        n.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        n.id.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesFilter && matchesSearch;
    });

    const total = filtered.length;
    if (total === 0) return [];

    const centerX = 400;
    const centerY = 240;

    // Separate into clusters by node type for structured spatial arrangement
    const accusedNodes = filtered.filter((n) => n.type === 'Accused');
    const caseNodes = filtered.filter((n) => n.type === 'CaseMaster');
    const victimNodes = filtered.filter((n) => n.type === 'Victim');
    const unitNodes = filtered.filter((n) => n.type === 'Unit');

    const result = [];

    // Accused in center ring
    accusedNodes.forEach((n, idx) => {
      const angle = (idx / (accusedNodes.length || 1)) * 2 * Math.PI - Math.PI / 2;
      const r = 110;
      result.push({
        ...n,
        x: centerX + r * Math.cos(angle),
        y: centerY + r * Math.sin(angle)
      });
    });

    // CaseMaster in middle ring
    caseNodes.forEach((n, idx) => {
      const angle = (idx / (caseNodes.length || 1)) * 2 * Math.PI;
      const r = 190;
      result.push({
        ...n,
        x: centerX + r * Math.cos(angle),
        y: centerY + r * Math.sin(angle)
      });
    });

    // Victims in outer left/right ring
    victimNodes.forEach((n, idx) => {
      const angle = (idx / (victimNodes.length || 1)) * 2 * Math.PI + Math.PI / 4;
      const r = 270;
      result.push({
        ...n,
        x: centerX + r * Math.cos(angle),
        y: centerY + r * Math.sin(angle)
      });
    });

    // Units in outer top/bottom ring
    unitNodes.forEach((n, idx) => {
      const angle = (idx / (unitNodes.length || 1)) * 2 * Math.PI + Math.PI / 3;
      const r = 320;
      result.push({
        ...n,
        x: centerX + r * Math.cos(angle),
        y: centerY + r * Math.sin(angle)
      });
    });

    return result;
  }, [nodes, filterType, searchTerm]);

  // Lookup dictionary for quick x,y coordinate resolution of edges
  const nodePosMap = useMemo(() => {
    const map = {};
    positionedNodes.forEach((n) => {
      map[n.id] = { x: n.x, y: n.y };
    });
    return map;
  }, [positionedNodes]);

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-5 shadow-2xl">
      {/* Panel Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-700 p-0.5 shadow-lg shadow-violet-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Share2 className="w-5 h-5 text-violet-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-extrabold text-slate-100 uppercase tracking-wider">
                Link-Analysis Network Graph Console
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-950 text-violet-300 border border-violet-800">
                LIVE API (GET /network)
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Multi-Entity Relationship Topology: Accused, Victims, Police Stations & Cross-Case Links
            </p>
          </div>
        </div>

        {/* Network Metrics Stats */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="bg-slate-900/90 px-3.5 py-1.5 rounded-xl border border-slate-800 flex items-center space-x-2">
            <Users className="w-3.5 h-3.5 text-rose-400" />
            <span className="text-slate-400 text-[10px] font-bold uppercase">Repeat Offenders:</span>
            <span className="font-extrabold text-rose-400">{summary.repeat_offenders_count || 2}</span>
          </div>

          <div className="bg-slate-900/90 px-3.5 py-1.5 rounded-xl border border-slate-800 flex items-center space-x-2">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400 text-[10px] font-bold uppercase">Nodes:</span>
            <span className="font-extrabold text-cyan-300">{nodes.length}</span>
          </div>

          <div className="bg-slate-900/90 px-3.5 py-1.5 rounded-xl border border-slate-800 flex items-center space-x-2">
            <Link className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400 text-[10px] font-bold uppercase">Edges:</span>
            <span className="font-extrabold text-amber-400">{edges.length}</span>
          </div>
        </div>
      </div>

      {/* Filter Controls & Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/80 p-3 rounded-xl border border-slate-800">
        <div className="flex items-center space-x-2 overflow-x-auto">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1 mr-2">
            <Filter className="w-3.5 h-3.5 text-violet-400" />
            <span>Filter Type:</span>
          </span>
          {['All', 'Accused', 'CaseMaster', 'Victim', 'Unit'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                filterType === t
                  ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/30'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="relative w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search entity name or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 text-xs text-slate-200 pl-8 pr-3 py-1.5 rounded-lg border border-slate-800 focus:outline-none focus:border-violet-500"
          />
        </div>
      </div>

      {/* Interactive SVG Network Topology Canvas */}
      <div className="relative bg-slate-950 border border-slate-800/90 rounded-2xl h-[480px] overflow-hidden flex items-center justify-center shadow-inner">
        {positionedNodes.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center p-6 space-y-3 z-10">
            <div className="w-12 h-12 rounded-2xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center">
              <FilterX className="w-6 h-6 text-violet-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                No Network Topology Nodes Matched
              </h4>
              <p className="text-xs text-slate-400 mt-1 max-w-sm">
                No relationship entities match type filter "{filterType}" or search term "{searchTerm}".
              </p>
            </div>
            {(searchTerm || filterType !== 'All') && (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setFilterType('All');
                }}
                className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-violet-300 text-xs font-semibold rounded-lg border border-slate-700 flex items-center space-x-1.5 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset Topology Filters</span>
              </button>
            )}
          </div>
        ) : (
          <svg className="w-full h-full" viewBox="0 0 800 480">
          {/* Render Relationship Edges */}
          {edges.map((edge, idx) => {
            const src = nodePosMap[edge.source];
            const tgt = nodePosMap[edge.target];
            if (!src || !tgt) return null;

            const isProximity = edge.relationship === 'SPATIAL_PROXIMITY_CLUSTER';

            return (
              <g key={`edge-${idx}`}>
                <line
                  x1={src.x}
                  y1={src.y}
                  x2={tgt.x}
                  y2={tgt.y}
                  stroke={isProximity ? '#ef4444' : '#3b82f6'}
                  strokeWidth={isProximity ? 2 : 1.5}
                  strokeDasharray={isProximity ? '4 4' : ''}
                  opacity={0.65}
                />
                <text
                  x={(src.x + tgt.x) / 2}
                  y={(src.y + tgt.y) / 2}
                  fill="#94a3b8"
                  fontSize="8"
                  fontWeight="bold"
                  textAnchor="middle"
                  dy="-4"
                  className="select-none"
                >
                  {edge.relationship}
                </text>
              </g>
            );
          })}

          {/* Render Entity Nodes */}
          {positionedNodes.map((node) => {
            const isSelected = selectedNode?.id === node.id;
            const color = getNodeColor(node.type, node.metadata);
            const icon = getNodeIcon(node.type);

            return (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
                onClick={() => setSelectedNode(node)}
                className="cursor-pointer group"
              >
                {/* Outer Glow Halo for Selected or Repeat Offender Nodes */}
                {(isSelected || node.metadata?.is_repeat_offender) && (
                  <circle
                    r="24"
                    fill={color}
                    opacity="0.25"
                    className="animate-ping"
                  />
                )}

                {/* Node Center Badge */}
                <circle
                  r="18"
                  fill={color}
                  stroke="#ffffff"
                  strokeWidth={isSelected ? '3' : '1.5'}
                  className="transition-transform duration-200 group-hover:scale-110 shadow-xl"
                />

                {/* Icon Emoji */}
                <text
                  textAnchor="middle"
                  dy="4"
                  fontSize="12"
                  className="select-none"
                >
                  {icon}
                </text>

                {/* Label Text below node */}
                <text
                  y="30"
                  textAnchor="middle"
                  fill="#f1f5f9"
                  fontSize="10"
                  fontWeight="bold"
                  className="select-none"
                >
                  {node.label}
                </text>

                {node.metadata?.is_repeat_offender && (
                  <text
                    y="-22"
                    textAnchor="middle"
                    fill="#f43f5e"
                    fontSize="9"
                    fontWeight="extrabold"
                    className="uppercase tracking-wider select-none"
                  >
                    🔥 REPEAT OFFENDER
                  </text>
                )}
              </g>
            );
          })}
        </svg>
        )}

        {/* Floating Node Inspector Drawer */}
        {selectedNode && (
          <div className="absolute top-4 right-4 w-72 bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-xl p-4 space-y-3 shadow-2xl z-20">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getNodeIcon(selectedNode.type)}</span>
                <span className="text-xs font-bold text-slate-100 uppercase tracking-wider">
                  {selectedNode.type} Details
                </span>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            <div>
              <h4 className="text-sm font-extrabold text-cyan-300 leading-snug">
                {selectedNode.label}
              </h4>
              <p className="text-[11px] text-slate-400 mt-0.5">ID: {selectedNode.id}</p>
            </div>

            {selectedNode.metadata && (
              <div className="space-y-2 text-xs bg-slate-950/80 p-2.5 rounded-lg border border-slate-800">
                {Object.entries(selectedNode.metadata).map(([k, v]) => (
                  <div key={k} className="flex justify-between items-center text-[11px]">
                    <span className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}:</span>
                    <span className="font-bold text-slate-200">{String(v)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
