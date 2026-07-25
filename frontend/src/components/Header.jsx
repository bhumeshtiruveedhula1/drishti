import React from 'react';
import { Shield, Radio, Activity, AlertTriangle, Database, Map, Building2, LayoutDashboard, User, LogOut } from 'lucide-react';

export default function Header({
  incidentsCount,
  heinousCount,
  cyberCount,
  investigatingCount,
  viewMode,
  setViewMode,
  userAuth,
  onSwitchRole
}) {
  return (
    <header className="h-16 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between z-30 relative shadow-xl">
      {/* Brand & Navigation Tabs */}
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-700 p-0.5 shadow-lg shadow-cyan-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Shield className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-bold tracking-wider text-slate-100 uppercase">
                DRISHTI <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60 ml-1">v0.1</span>
              </h1>
            </div>
            <p className="text-[11px] text-slate-400 font-medium tracking-wide">
              Karnataka Police Spatial Command
            </p>
          </div>
        </div>

        {/* View Mode Navigation Tabs */}
        <div className="flex items-center bg-slate-950/80 p-1 rounded-xl border border-slate-800 space-x-1">
          <button
            onClick={() => setViewMode('stateMap')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'stateMap'
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Map className="w-3.5 h-3.5" />
            <span>State Spatial Map</span>
          </button>

          <button
            onClick={() => setViewMode('stationConsole')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'stationConsole'
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Station Console</span>
          </button>

          <button
            onClick={() => setViewMode('commandConsole')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'commandConsole'
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Command Console</span>
          </button>
        </div>
      </div>

      {/* Live Operational Metrics HUD */}
      <div className="hidden xl:flex items-center space-x-4">
        <div className="flex items-center space-x-2.5 bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <Activity className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <div>
            <div className="text-[9px] text-slate-400 uppercase font-semibold">Total Pinned</div>
            <div className="text-xs font-bold text-cyan-300 leading-tight">{incidentsCount}</div>
          </div>
        </div>

        <div className="flex items-center space-x-2.5 bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
          <div>
            <div className="text-[9px] text-slate-400 uppercase font-semibold">Heinous Crimes</div>
            <div className="text-xs font-bold text-red-400 leading-tight">{heinousCount}</div>
          </div>
        </div>

        <div className="flex items-center space-x-2.5 bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <Radio className="w-3.5 h-3.5 text-amber-400" />
          <div>
            <div className="text-[9px] text-slate-400 uppercase font-semibold">Cyber & Financial</div>
            <div className="text-xs font-bold text-amber-400 leading-tight">{cyberCount}</div>
          </div>
        </div>

        <div className="flex items-center space-x-2.5 bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <div>
            <div className="text-[9px] text-slate-400 uppercase font-semibold">Under Investigation</div>
            <div className="text-xs font-bold text-emerald-400 leading-tight">{investigatingCount}</div>
          </div>
        </div>
      </div>

      {/* Authenticated User Badge & Connection Mode Indicator */}
      <div className="flex items-center space-x-3">
        {userAuth && (
          <div className="flex items-center space-x-2 bg-slate-950 px-3 py-1 rounded-xl border border-slate-800">
            <User className="w-3.5 h-3.5 text-cyan-400" />
            <div className="text-[11px] leading-tight">
              <span className="text-slate-300 font-medium block">{userAuth.email || 'officer@drishti.gov.in'}</span>
              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">
                Role: {userAuth.selectedRole || userAuth.role}
              </span>
            </div>
            {onSwitchRole && (
              <button
                onClick={onSwitchRole}
                title="Switch Operational Role"
                className="ml-2 p-1 text-slate-400 hover:text-red-400 hover:bg-slate-900 rounded-lg transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        )}

        <div className="flex items-center space-x-2 bg-emerald-950/50 border border-emerald-800/80 px-3 py-1 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span className="text-xs font-semibold text-emerald-300">Live API Feed (GET /incidents)</span>
        </div>
      </div>
    </header>
  );
}
