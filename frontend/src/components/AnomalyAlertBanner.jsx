import React, { useState, useEffect } from 'react';
import { RefreshCw, ShieldAlert, X } from 'lucide-react';
import { fetchAnomalies } from '../services/mockData';

export default function AnomalyAlertBanner({ initialAnomalies = [] }) {
  const [anomalies, setAnomalies] = useState(initialAnomalies);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [dismissed, setDismissed] = useState(false);

  // Poll /anomalies every 45 seconds (30-60s range rule)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        setIsRefreshing(true);
        const updated = await fetchAnomalies();
        if (updated && updated.length > 0) {
          setAnomalies(updated);
        }
        setLastUpdated(new Date());
      } catch (err) {
        console.warn('Anomaly polling update failed:', err);
      } finally {
        setTimeout(() => setIsRefreshing(false), 800);
      }
    }, 45000); // 45s polling interval

    return () => clearInterval(interval);
  }, []);

  if (dismissed || !anomalies || anomalies.length === 0) {
    return null;
  }

  const criticalAnomaly = anomalies.find(a => (a.AnomalyScore || 0) >= 3.0) || anomalies[0];
  const totalCount = anomalies.length;

  return (
    <div className="bg-gradient-to-r from-amber-950/95 via-amber-900/90 to-amber-950/95 border-b border-amber-500/40 text-amber-200 px-4 py-2.5 flex items-center justify-between shadow-xl relative z-20 backdrop-blur-md transition-all duration-300">
      <div className="flex items-center space-x-3 truncate">
        <div className="p-1.5 bg-amber-500/20 rounded-lg text-amber-400 shrink-0 relative">
          <div className="absolute inset-0 rounded-lg bg-amber-400/20 animate-ping opacity-75"></div>
          <ShieldAlert className="w-5 h-5 relative z-10 animate-pulse text-amber-300" />
        </div>

        <div className="flex items-center space-x-2 text-xs truncate">
          <span className="font-bold uppercase tracking-wider text-amber-400 shrink-0 flex items-center gap-1.5">
            ANOMALY ALERT
            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
              {totalCount} ACTIVE
            </span>
          </span>

          <span className="text-slate-400 shrink-0">|</span>

          <span className="truncate font-medium text-slate-200">
            {criticalAnomaly.FlagReason || 'Spike in Financial Cyber Fraud (+233% vs baseline)'}
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-4 shrink-0 text-xs">
        {/* Polling Indicator Label - Strictly "Auto-refreshing (45s)" as required */}
        <div className="flex items-center space-x-1.5 text-slate-400 font-mono text-[11px] bg-slate-900/60 px-2.5 py-1 rounded-md border border-amber-500/20">
          <RefreshCw className={`w-3.5 h-3.5 text-amber-400 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span className="text-amber-300/90 font-semibold">Auto-refreshing (45s)</span>
          <span className="text-slate-500">
            • {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
        </div>

        <button
          onClick={() => setDismissed(true)}
          className="text-amber-400/70 hover:text-amber-200 p-1 transition-colors"
          title="Dismiss Alert Banner"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
