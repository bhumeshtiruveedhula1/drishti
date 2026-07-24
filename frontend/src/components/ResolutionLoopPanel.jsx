import React, { useMemo } from 'react';
import {
  CheckCircle2,
  Clock,
  Award,
  TrendingUp,
  FileCheck,
  Star,
  Activity,
  Building2,
  ChevronRight,
  Sparkles
} from 'lucide-react';

export default function ResolutionLoopPanel({ resolutionMetrics = [] }) {
  // Aggregate Statewide Summary KPIs
  const summaryMetrics = useMemo(() => {
    if (!resolutionMetrics || resolutionMetrics.length === 0) {
      return {
        avgResolutionRate: 78.0,
        avgDisposalDays: 21.8,
        totalRegistered: 105,
        totalChargesheeted: 77,
        totalDisposed: 83,
        avgFeedback: 4.6
      };
    }

    const totalReg = resolutionMetrics.reduce((acc, m) => acc + (m.TotalCasesRegistered || 0), 0);
    const totalCS = resolutionMetrics.reduce((acc, m) => acc + (m.ChargesheetedCount || 0), 0);
    const totalDisp = resolutionMetrics.reduce((acc, m) => acc + (m.DisposedCount || 0), 0);
    const avgResRate = (resolutionMetrics.reduce((acc, m) => acc + (m.ResolutionRate || 0), 0) / resolutionMetrics.length).toFixed(1);
    const avgDays = (resolutionMetrics.reduce((acc, m) => acc + (m.AverageDisposalDays || 0), 0) / resolutionMetrics.length).toFixed(1);
    const avgFb = (resolutionMetrics.reduce((acc, m) => acc + (m.FeedbackScore || 0), 0) / resolutionMetrics.length).toFixed(1);

    return {
      avgResolutionRate: avgResRate,
      avgDisposalDays: avgDays,
      totalRegistered: totalReg,
      totalChargesheeted: totalCS,
      totalDisposed: totalDisp,
      avgFeedback: avgFb
    };
  }, [resolutionMetrics]);

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-5 shadow-2xl">
      {/* Panel Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 p-0.5 shadow-lg shadow-emerald-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-extrabold text-slate-100 uppercase tracking-wider">
                Resolution Feedback Loop Console
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
                SCHEMA MOCK DATA (Awaiting AppSail Deploy)
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Per-Station Case Disposal Efficiency, Chargesheet Velocity & Public Feedback Index
            </p>
          </div>
        </div>
      </div>

      {/* Top 4 Executive Resolution KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-1.5 shadow-md">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider">Resolution Rate</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400">
            {summaryMetrics.avgResolutionRate}%
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-800">
            <span>Statewide Target: 75.0%</span>
            <span className="text-emerald-400 font-bold">+3.0% vs Target</span>
          </div>
        </div>

        <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-1.5 shadow-md">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider">Disposal Velocity</span>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-cyan-300">
            {summaryMetrics.avgDisposalDays} Days
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-800">
            <span>Average Time to Charge-Sheet</span>
            <span className="text-cyan-400 font-bold">Fast-Tracked</span>
          </div>
        </div>

        <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-1.5 shadow-md">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider">Cases Disposed</span>
            <FileCheck className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400">
            {summaryMetrics.totalDisposed} / {summaryMetrics.totalRegistered}
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-800">
            <span>Chargesheeted: {summaryMetrics.totalChargesheeted}</span>
            <span className="text-amber-400 font-bold">
              {Math.round((summaryMetrics.totalChargesheeted / summaryMetrics.totalRegistered) * 100)}% Conversion
            </span>
          </div>
        </div>

        <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-1.5 shadow-md">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider">Public Satisfaction</span>
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
          </div>
          <div className="text-2xl font-black text-yellow-300">
            {summaryMetrics.avgFeedback} / 5.0
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-800">
            <span>Complainant Feedback Index</span>
            <span className="text-yellow-400 font-bold">⭐ Excellent</span>
          </div>
        </div>
      </div>

      {/* Station Resolution Leaderboard Table */}
      <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="p-3.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Building2 className="w-4 h-4 text-cyan-400" />
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Police Station Resolution Performance Leaderboard
            </h4>
          </div>
          <span className="text-[11px] text-slate-400 font-medium">
            {resolutionMetrics.length} Station Jurisdictions Tracked
          </span>
        </div>

        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-950 text-slate-400 border-b border-slate-800 text-[10px] uppercase font-bold tracking-wider">
                <th className="p-3">Police Station</th>
                <th className="p-3 text-center">District</th>
                <th className="p-3 text-center">Cases Logged</th>
                <th className="p-3 text-center">Chargesheeted</th>
                <th className="p-3 text-center">Resolution Rate</th>
                <th className="p-3 text-center">Avg Velocity</th>
                <th className="p-3 text-center">Feedback Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {resolutionMetrics.map((m) => (
                <tr key={`res-row-${m.MetricID}`} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3">
                    <div className="font-bold text-slate-100 flex items-center space-x-1.5">
                      <Building2 className="w-3.5 h-3.5 text-cyan-400" />
                      <span>{m.PoliceStationName}</span>
                    </div>
                  </td>
                  <td className="p-3 text-center text-slate-400">{m.DistrictName}</td>
                  <td className="p-3 text-center font-bold text-slate-200">{m.TotalCasesRegistered}</td>
                  <td className="p-3 text-center text-emerald-400 font-bold">
                    {m.ChargesheetedCount} ({Math.round((m.ChargesheetedCount / m.TotalCasesRegistered) * 100)}%)
                  </td>
                  <td className="p-3 text-center">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-20 bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                        <div
                          className="bg-emerald-500 h-full rounded-full"
                          style={{ width: `${Math.min(m.ResolutionRate, 100)}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-emerald-300">{m.ResolutionRate}%</span>
                    </div>
                  </td>
                  <td className="p-3 text-center font-bold text-cyan-300">
                    {m.AverageDisposalDays} Days
                  </td>
                  <td className="p-3 text-center">
                    <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-yellow-950/80 text-yellow-300 border border-yellow-800 text-[11px] font-bold">
                      <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      <span>{m.FeedbackScore}</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
