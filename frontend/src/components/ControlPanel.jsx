import React from 'react';
import { Search, Filter, ShieldAlert, Tag, CheckCircle2, RotateCcw, MapPin, TrendingUp } from 'lucide-react';

export default function ControlPanel({
  searchTerm,
  setSearchTerm,
  selectedGravity,
  setSelectedGravity,
  selectedCategory,
  setSelectedCategory,
  selectedStatus,
  setSelectedStatus,
  showChoropleth,
  setShowChoropleth,
  showHotspots,
  setShowHotspots,
  showAnomalies,
  setShowAnomalies,
  categories,
  onResetFilters,
  totalFilteredCount,
  totalCount
}) {
  return (
    <aside className="w-80 bg-slate-900/95 backdrop-blur-xl border-r border-slate-800 flex flex-col h-[calc(100vh-4rem)] z-20 shadow-2xl">
      {/* Panel Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Spatial Filters</h2>
        </div>
        <button
          onClick={onResetFilters}
          className="text-xs text-slate-400 hover:text-cyan-400 flex items-center space-x-1 transition-colors px-2 py-1 rounded bg-slate-800/60 hover:bg-slate-800 border border-slate-700/50"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>

      <div className="p-4 space-y-5 overflow-y-auto flex-1 custom-scrollbar">
        {/* Layer Toggles */}
        <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 space-y-2.5">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Map Layer Options</div>
          
          <label className="flex items-center justify-between cursor-pointer text-xs font-semibold text-slate-200">
            <span className="flex items-center space-x-2">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              <span>District Choropleth</span>
            </span>
            <input
              type="checkbox"
              checked={showChoropleth}
              onChange={(e) => setShowChoropleth(e.target.checked)}
              className="w-4 h-4 rounded accent-cyan-500 bg-slate-900 border-slate-700"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer text-xs font-semibold text-slate-200">
            <span className="flex items-center space-x-2">
              <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
              <span>DBSCAN Hotspot Clusters</span>
            </span>
            <input
              type="checkbox"
              checked={showHotspots}
              onChange={(e) => setShowHotspots(e.target.checked)}
              className="w-4 h-4 rounded accent-red-500 bg-slate-900 border-slate-700"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer text-xs font-semibold text-slate-200">
            <span className="flex items-center space-x-2">
              <TrendingUp className="w-3.5 h-3.5 text-amber-400" />
              <span>Anomaly Trend Spikes</span>
            </span>
            <input
              type="checkbox"
              checked={showAnomalies}
              onChange={(e) => setShowAnomalies(e.target.checked)}
              className="w-4 h-4 rounded accent-amber-500 bg-slate-900 border-slate-700"
            />
          </label>
        </div>
        {/* Search Bar */}
        <div>
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
            Search District / FIR / Facts
          </label>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="e.g. Koramangala, Cyber, FIR..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
        </div>

        {/* Gravity Filter */}
        <div>
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1 mb-2">
            <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
            <span>Offence Gravity</span>
          </label>
          <div className="grid grid-cols-3 gap-1.5 bg-slate-950/80 p-1 rounded-lg border border-slate-800">
            {['All', 'Heinous', 'Non-Heinous'].map((gravity) => (
              <button
                key={gravity}
                onClick={() => setSelectedGravity(gravity)}
                className={`py-1.5 text-[11px] font-semibold rounded-md transition-all ${
                  selectedGravity === gravity
                    ? gravity === 'Heinous'
                      ? 'bg-red-500/20 text-red-400 border border-red-500/40 shadow-sm'
                      : gravity === 'Non-Heinous'
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40 shadow-sm'
                      : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {gravity}
              </button>
            ))}
          </div>
        </div>

        {/* Category Filter */}
        <div>
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1 mb-2">
            <Tag className="w-3.5 h-3.5 text-cyan-400" />
            <span>Crime Category</span>
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
          >
            <option value="All">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        {/* Case Status Filter */}
        <div>
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1 mb-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Investigation Status</span>
          </label>
          <div className="space-y-1">
            {['All', 'Under Investigation', 'Chargesheeted', 'Disposed', 'Pending'].map((status) => (
              <button
                key={status}
                onClick={() => setSelectedStatus(status)}
                className={`w-full text-left px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center justify-between ${
                  selectedStatus === status
                    ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                    : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'
                }`}
              >
                <span>{status}</span>
                {selectedStatus === status && <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Panel Footer Stats */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-1.5 text-slate-400">
          <MapPin className="w-3.5 h-3.5 text-cyan-400" />
          <span>Active Map Pins:</span>
        </div>
        <span className="font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
          {totalFilteredCount} / {totalCount}
        </span>
      </div>
    </aside>
  );
}
