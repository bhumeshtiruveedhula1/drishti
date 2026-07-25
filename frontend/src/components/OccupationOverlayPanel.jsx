import React, { useState } from 'react';
import { Briefcase, ChevronRight, UserCheck, BarChart2, Layers } from 'lucide-react';

const CATEGORY_COLORS = {
  'Theft': 'bg-cyan-500 text-cyan-400 border-cyan-500/30',
  'Assault': 'bg-red-500 text-red-400 border-red-500/30',
  'Burglary': 'bg-amber-500 text-amber-400 border-amber-500/30',
  'Robbery': 'bg-purple-500 text-purple-400 border-purple-500/30',
  'Chain Snatching': 'bg-emerald-500 text-emerald-400 border-emerald-500/30'
};

const CATEGORY_BAR_BG = {
  'Theft': 'bg-cyan-500',
  'Assault': 'bg-red-500',
  'Burglary': 'bg-amber-500',
  'Robbery': 'bg-purple-500',
  'Chain Snatching': 'bg-emerald-500'
};

export default function OccupationOverlayPanel({ occupationData = [] }) {
  const [selectedOccupation, setSelectedOccupation] = useState(null);

  if (!occupationData || occupationData.length === 0) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 text-center text-slate-400">
        <Briefcase className="w-8 h-8 text-cyan-400 mx-auto mb-2 opacity-50" />
        <p className="text-sm font-medium">Loading Occupation Demographics Overlay...</p>
      </div>
    );
  }

  const activeOccupation = selectedOccupation || occupationData[0];
  const totalOverlayIncidents = occupationData.reduce((acc, curr) => acc + (curr.total_count || 0), 0);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-cyan-400">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
              Socio-Economic Intelligence: Occupation Breakdown
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                LIVE OVERLAY
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Crime distribution aggregated across complainant & suspect occupation profiles ({totalOverlayIncidents.toLocaleString()} records)
            </p>
          </div>
        </div>
      </div>

      {/* Grid Content */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 mt-4">
        {/* Left Column: Occupation List */}
        <div className="lg:col-span-5 space-y-2 max-h-72 overflow-y-auto pr-1 custom-scrollbar">
          {occupationData.map((occ) => {
            const isSelected = activeOccupation.OccupationID === occ.OccupationID;
            const pctOfTotal = totalOverlayIncidents ? Math.round((occ.total_count / totalOverlayIncidents) * 100) : 0;

            return (
              <button
                key={occ.OccupationID}
                onClick={() => setSelectedOccupation(occ)}
                className={`w-full text-left p-3 rounded-xl transition-all border flex items-center justify-between group ${
                  isSelected
                    ? 'bg-cyan-950/50 border-cyan-500/50 text-cyan-200 shadow-md shadow-cyan-950/30'
                    : 'bg-slate-950/40 border-slate-800/80 hover:bg-slate-800/50 text-slate-300'
                }`}
              >
                <div className="flex items-center space-x-3 truncate">
                  <UserCheck className={`w-4 h-4 shrink-0 ${isSelected ? 'text-cyan-400' : 'text-slate-500 group-hover:text-slate-400'}`} />
                  <div className="truncate">
                    <div className="text-xs font-semibold truncate">{occ.OccupationName}</div>
                    <div className="text-[10px] text-slate-500">{occ.total_count} Incidents recorded</div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <span className="text-xs font-bold font-mono text-cyan-400">{pctOfTotal}%</span>
                  <ChevronRight className={`w-4 h-4 transition-transform ${isSelected ? 'text-cyan-400 translate-x-0.5' : 'text-slate-600'}`} />
                </div>
              </button>
            );
          })}
        </div>

        {/* Right Column: Selected Occupation Category Bar Breakdown */}
        <div className="lg:col-span-7 bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
              <div className="flex items-center space-x-2">
                <BarChart2 className="w-4 h-4 text-cyan-400" />
                <h4 className="text-xs font-bold text-slate-200">
                  {activeOccupation.OccupationName} — Category Breakdown
                </h4>
              </div>
              <span className="text-xs font-mono font-bold text-slate-400">
                Total: {activeOccupation.total_count}
              </span>
            </div>

            {/* Stacked Proportional Bar */}
            <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden flex mb-4 border border-slate-800">
              {Object.entries(activeOccupation.categories || {}).map(([cat, count]) => {
                const pct = activeOccupation.total_count ? ((count / activeOccupation.total_count) * 100).toFixed(1) : 0;
                const barColor = CATEGORY_BAR_BG[cat] || 'bg-slate-600';

                return (
                  <div
                    key={cat}
                    style={{ width: `${pct}%` }}
                    className={`${barColor} h-full transition-all duration-500`}
                    title={`${cat}: ${count} (${pct}%)`}
                  />
                );
              })}
            </div>

            {/* Category Breakdown Rows */}
            <div className="space-y-2.5">
              {Object.entries(activeOccupation.categories || {}).map(([cat, count]) => {
                const pct = activeOccupation.total_count ? Math.round((count / activeOccupation.total_count) * 100) : 0;
                const barBg = CATEGORY_BAR_BG[cat] || 'bg-slate-500';

                return (
                  <div key={cat} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-2">
                        <span className={`w-2 h-2 rounded-full ${barBg}`} />
                        <span className="font-medium text-slate-300">{cat}</span>
                      </div>
                      <div className="font-mono text-slate-400 text-[11px]">
                        <span className="font-semibold text-slate-200">{count}</span> ({pct}%)
                      </div>
                    </div>

                    <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${barBg} rounded-full transition-all duration-500`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              Source: Karnataka State Data Store Occupation Overlays
            </span>
            <span className="font-mono text-slate-400">API: /overlays/occupation</span>
          </div>
        </div>
      </div>
    </div>
  );
}
