import React, { useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from 'react-leaflet';
import L from 'leaflet';
import karnatakaGeoJSON from '../data/karnatakaDistricts.json';
import ResolutionLoopPanel from './ResolutionLoopPanel';
import NetworkGraphPanel from './NetworkGraphPanel';
import {
  Shield,
  Activity,
  AlertTriangle,
  Building2,
  MapPin,
  Search,
  FileText,
  BarChart3,
  Layers,
  X,
  TrendingUp,
  Radio,
  CheckCircle2,
  Calendar,
  FilterX,
  RotateCcw
} from 'lucide-react';

const createMiniMarkerIcon = (gravity) => {
  const isHeinous = gravity === 'Heinous';
  const bg = isHeinous ? 'bg-red-500 shadow-red-500/50' : 'bg-amber-400 shadow-amber-500/50';

  return L.divIcon({
    className: 'custom-mini-pin',
    html: `<div class="w-3.5 h-3.5 rounded-full ${bg} border border-white shadow-md"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7]
  });
};

export default function CommandConsole({
  incidents = [],
  anomalies = [],
  resolutionMetrics = [],
  networkData = { summary: {}, nodes: [], edges: [] }
}) {
  const [streamSearch, setStreamSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [selectedCaseModal, setSelectedCaseModal] = useState(null);

  // Safeguard incident coordinates
  const safeIncidents = useMemo(() => {
    return (incidents || []).filter(
      (i) =>
        i &&
        typeof i.latitude === 'number' &&
        typeof i.longitude === 'number' &&
        !isNaN(i.latitude) &&
        !isNaN(i.longitude)
    );
  }, [incidents]);

  // Executive Statewide Metrics
  const totalIncidents = incidents.length;
  const heinousCount = useMemo(
    () => incidents.filter((i) => i.GravityOffenceName === 'Heinous').length,
    [incidents]
  );
  const heinousRatio = totalIncidents ? Math.round((heinousCount / totalIncidents) * 100) : 0;
  const investigatingCount = useMemo(
    () => incidents.filter((i) => i.CaseStatusName === 'Under Investigation').length,
    [incidents]
  );
  const investigatingRate = totalIncidents ? Math.round((investigatingCount / totalIncidents) * 100) : 0;

  // District Performance Aggregation
  const districtPerformance = useMemo(() => {
    const districts = {};
    incidents.forEach((inc) => {
      const dName = inc.DistrictName || 'Unknown';
      if (!districts[dName]) {
        districts[dName] = {
          name: dName,
          total: 0,
          heinous: 0,
          cyber: 0,
          underInv: 0
        };
      }
      districts[dName].total += 1;
      if (inc.GravityOffenceName === 'Heinous') districts[dName].heinous += 1;
      if (inc.CaseCategoryName === 'Cyber Crime') districts[dName].cyber += 1;
      if (inc.CaseStatusName === 'Under Investigation') districts[dName].underInv += 1;
    });

    return Object.values(districts).sort((a, b) => b.total - a.total);
  }, [incidents]);

  // Category Distribution Aggregation
  const categoryDistribution = useMemo(() => {
    const counts = {};
    incidents.forEach((inc) => {
      counts[inc.CaseCategoryName] = (counts[inc.CaseCategoryName] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([name, count]) => ({
        name,
        count,
        pct: Math.round((count / totalIncidents) * 100)
      }))
      .sort((a, b) => b.count - a.count);
  }, [incidents, totalIncidents]);

  // Unique Categories
  const categoriesList = useMemo(() => {
    return Array.from(new Set(incidents.map((i) => i.CaseCategoryName))).sort();
  }, [incidents]);

  // Filtered Master FIR Stream
  const filteredStream = useMemo(() => {
    return incidents.filter((inc) => {
      const matchesSearch =
        !streamSearch ||
        (inc.CrimeNo || '').toLowerCase().includes(streamSearch.toLowerCase()) ||
        (inc.DistrictName || '').toLowerCase().includes(streamSearch.toLowerCase()) ||
        (inc.PoliceStationName || '').toLowerCase().includes(streamSearch.toLowerCase()) ||
        (inc.BriefFacts || '').toLowerCase().includes(streamSearch.toLowerCase()) ||
        (inc.CrimeMajorHeadName || '').toLowerCase().includes(streamSearch.toLowerCase());

      const matchesCat =
        categoryFilter === 'All' || inc.CaseCategoryName === categoryFilter;

      return matchesSearch && matchesCat;
    });
  }, [incidents, streamSearch, categoryFilter]);

  const karnatakaCenter = [14.8, 76.2];

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-slate-950 text-slate-100 overflow-y-auto custom-scrollbar">
      {/* Executive Command Banner */}
      <div className="bg-slate-900/90 border-b border-slate-800 px-3 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3 z-20">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 p-0.5 shadow-lg shadow-cyan-500/20 flex items-center justify-center shrink-0">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Shield className="w-4 h-4 text-cyan-400" />
            </div>
          </div>
          <div>
            <h2 className="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
              Statewide Command Console
            </h2>
            <p className="text-[10px] sm:text-[11px] text-slate-400">
              Karnataka Police HQ • Operational Oversight
            </p>
          </div>
        </div>

        {/* High-Level Executive Metrics */}
        <div className="grid grid-cols-2 sm:flex items-center gap-2 text-xs">
          <div className="bg-slate-950/80 px-2.5 py-1.5 rounded-xl border border-slate-800 flex items-center space-x-2">
            <Activity className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <div>
              <div className="text-[9px] text-slate-400 uppercase font-semibold">Active Districts</div>
              <div className="text-xs font-bold text-cyan-300">{districtPerformance.length} Districts</div>
            </div>
          </div>

          <div className="bg-slate-950/80 px-2.5 py-1.5 rounded-xl border border-slate-800 flex items-center space-x-2">
            <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0" />
            <div>
              <div className="text-[9px] text-slate-400 uppercase font-semibold">Heinous Ratio</div>
              <div className="text-xs font-bold text-red-400">{heinousRatio}% of Cases</div>
            </div>
          </div>

          <div className="bg-slate-950/80 px-2.5 py-1.5 rounded-xl border border-slate-800 flex items-center space-x-2">
            <TrendingUp className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <div>
              <div className="text-[9px] text-slate-400 uppercase font-semibold">Anomaly Spikes</div>
              <div className="text-xs font-bold text-amber-400">{anomalies.length} Critical Alerts</div>
            </div>
          </div>

          <div className="bg-slate-950/80 px-2.5 py-1.5 rounded-xl border border-slate-800 flex items-center space-x-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <div>
              <div className="text-[9px] text-slate-400 uppercase font-semibold">Active Investigations</div>
              <div className="text-xs font-bold text-emerald-400">{investigatingRate}% Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid Layout: 3 Columns */}
      <div className="min-h-[500px] shrink-0 grid grid-cols-1 lg:grid-cols-12 gap-0 overflow-hidden">
        {/* Left Column: District Performance & Crime Category Analytics (4 cols) */}
        <div className="lg:col-span-4 h-full border-r border-slate-800 bg-slate-900/40 p-4 space-y-4 overflow-y-auto custom-scrollbar">
          
          {/* Emerging Anomaly & Trend Spikes Alert Banner */}
          {anomalies.length > 0 && (
            <div className="bg-gradient-to-r from-amber-950/80 to-slate-950 p-3.5 rounded-xl border border-amber-800/80 shadow-lg space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase tracking-wider">
                  <TrendingUp className="w-4 h-4 text-amber-400 animate-bounce" />
                  <span>Gamma Anomaly Spikes ({anomalies.length})</span>
                </div>
                <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-700">
                  LIVE GET /anomalies
                </span>
              </div>

              <div className="space-y-2">
                {anomalies.map((anom) => (
                  <div
                    key={`cmd-anom-${anom.AnomalyFlagID}`}
                    className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-100">
                        {anom.PoliceStationName} ({anom.DistrictName})
                      </span>
                      <span className="text-[10px] font-extrabold text-rose-400 bg-rose-950/80 px-1.5 py-0.5 rounded border border-rose-800">
                        +{anom.SpikePercentage}% Spike
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300 leading-snug">
                      {anom.AlertSummary}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 1: District Performance Matrix */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
                <Building2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>District Operational Summary</span>
              </h3>
              <span className="text-[10px] text-slate-400 font-semibold">{districtPerformance.length} Jurisdictions</span>
            </div>

            <div className="space-y-2">
              {districtPerformance.map((dp) => (
                <div
                  key={dp.district}
                  className="bg-slate-950/80 border border-slate-800 rounded-xl p-3 hover:border-cyan-500/40 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-cyan-300 flex items-center space-x-1.5">
                      <MapPin className="w-3 h-3 text-cyan-400" />
                      <span>{dp.district}</span>
                    </span>
                    <span className="text-xs font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded">
                      {dp.total} FIR{dp.total > 1 ? 's' : ''}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 mt-2 text-[11px]">
                    <div className="flex items-center justify-between text-slate-400 bg-slate-900/60 px-2 py-1 rounded">
                      <span>Heinous:</span>
                      <span className={`font-bold ${dp.heinous > 0 ? 'text-red-400' : 'text-slate-300'}`}>
                        {dp.heinous}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-slate-400 bg-slate-900/60 px-2 py-1 rounded">
                      <span>Investigating:</span>
                      <span className="font-bold text-amber-400">{dp.underInvestigation}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 2: Category Distribution */}
          <div className="space-y-2 pt-2 border-t border-slate-800/80">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
              <BarChart3 className="w-3.5 h-3.5 text-amber-400" />
              <span>Statewide Crime Composition</span>
            </h3>

            <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 space-y-2.5">
              {categoryDistribution.map((cat) => (
                <div key={cat.name} className="space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="font-semibold text-slate-300 truncate max-w-[180px]">
                      {cat.name}
                    </span>
                    <span className="font-bold text-cyan-400">
                      {cat.count} ({cat.pct}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-cyan-500 to-blue-600 h-full rounded-full transition-all"
                      style={{ width: `${Math.max(cat.pct, 8)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Middle Column: Master Cross-Station FIR Stream (5 cols) */}
        <div className="lg:col-span-5 h-full border-r border-slate-800 flex flex-col bg-slate-950/60 overflow-hidden">
          {/* Header & Filter Search */}
          <div className="p-4 border-b border-slate-800 space-y-3 bg-slate-900/80">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                  Master Cross-Station FIR Stream
                </h3>
              </div>
              <span className="text-xs font-semibold text-slate-400">
                {filteredStream.length} / {totalIncidents} Records
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
                <input
                  type="text"
                  value={streamSearch}
                  onChange={(e) => setStreamSearch(e.target.value)}
                  placeholder="Search Crime No / Facts..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="All">All Categories</option>
                {categoriesList.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* FIR Stream Feed List */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3">
            {filteredStream.length === 0 ? (
              <div className="h-full min-h-[250px] flex flex-col items-center justify-center text-center p-6 bg-slate-900/60 rounded-xl border border-slate-800 space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                  <FilterX className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                    No Statewide FIR Stream Matches
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 max-w-sm">
                    No crime records match your current search query or category filter.
                  </p>
                </div>
                {(streamSearch || categoryFilter !== 'All') && (
                  <button
                    onClick={() => {
                      setStreamSearch('');
                      setCategoryFilter('All');
                    }}
                    className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-semibold rounded-lg border border-slate-700 flex items-center space-x-1.5 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Reset Stream Filters</span>
                  </button>
                )}
              </div>
            ) : (
              filteredStream.map((incident) => (
                <div
                  key={incident.CaseMasterID}
                  onClick={() => setSelectedCaseModal(incident)}
                  className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 hover:border-cyan-500/50 transition-all cursor-pointer space-y-2 group shadow-md"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Shield className="w-3.5 h-3.5 text-cyan-400" />
                      <span className="text-xs font-bold text-cyan-300 group-hover:text-cyan-200">
                        {incident.CrimeNo}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                        incident.GravityOffenceName === 'Heinous'
                          ? 'bg-red-950 text-red-400 border border-red-800/80'
                          : 'bg-amber-950 text-amber-400 border border-amber-800/80'
                      }`}
                    >
                      {incident.GravityOffenceName}
                    </span>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold text-slate-200 leading-snug">
                      {incident.CrimeMajorHeadName}
                    </h4>
                    <div className="text-[11px] font-medium text-cyan-400 mt-0.5">
                      {incident.CaseCategoryName}
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
                    <span className="flex items-center space-x-1">
                      <Building2 className="w-3 h-3 text-slate-500" />
                      <span className="truncate max-w-[150px]">{incident.PoliceStationName} ({incident.DistrictName})</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      <span>{incident.CrimeRegisteredDate}</span>
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Statewide Spatial Minimap (3 cols) */}
        <div className="lg:col-span-3 h-64 sm:h-80 lg:h-full relative flex flex-col bg-slate-950">
          <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                State Spatial Minimap
              </h3>
            </div>
          </div>

          <div className="flex-1 relative">
            <MapContainer
              center={karnatakaCenter}
              zoom={6}
              scrollWheelZoom={false}
              className="w-full h-full z-10"
            >
              <TileLayer
                attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              />
              <GeoJSON
                data={karnatakaGeoJSON}
                style={{
                  fillColor: '#0f172a',
                  weight: 1,
                  color: '#0284c7',
                  dashArray: '3',
                  fillOpacity: 0.2
                }}
              />
              {safeIncidents.map((incident) => (
                <Marker
                  key={incident.CaseMasterID}
                  position={[incident.latitude, incident.longitude]}
                  icon={createMiniMarkerIcon(incident.GravityOffenceName)}
                >
                  <Popup>
                    <div className="text-xs font-bold text-cyan-300">{incident.CrimeNo}</div>
                    <div className="text-[11px] text-slate-300">{incident.PoliceStationName}</div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>
      </div>

      {/* Resolution Feedback Loop Section */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/60 overflow-y-auto">
        <ResolutionLoopPanel resolutionMetrics={resolutionMetrics} />
      </div>

      {/* Link-Analysis Network Graph Section */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/80 overflow-y-auto">
        <NetworkGraphPanel networkData={networkData} />
      </div>

      {/* Case Details Inspection Drawer Modal */}
      {selectedCaseModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-2xl relative">
            <button
              onClick={() => setSelectedCaseModal(null)}
              className="absolute top-4 right-4 p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Modal Header */}
            <div className="flex items-center space-x-3 border-b border-slate-800 pb-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                <Shield className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-100">
                  {selectedCaseModal.CrimeNo}
                </h3>
                <p className="text-xs text-slate-400">
                  Case File: {selectedCaseModal.CaseNo} • {selectedCaseModal.PoliceStationName} ({selectedCaseModal.DistrictName})
                </p>
              </div>
            </div>

            {/* Case Details Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">Major Head</span>
                <span className="font-semibold text-slate-200">{selectedCaseModal.CrimeMajorHeadName}</span>
              </div>
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">Category</span>
                <span className="font-semibold text-cyan-400">{selectedCaseModal.CaseCategoryName}</span>
              </div>
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">Offence Gravity</span>
                <span className={`font-semibold ${selectedCaseModal.GravityOffenceName === 'Heinous' ? 'text-red-400' : 'text-amber-400'}`}>
                  {selectedCaseModal.GravityOffenceName}
                </span>
              </div>
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-400 text-[10px] uppercase font-bold block">Current Status</span>
                <span className="font-semibold text-emerald-400">{selectedCaseModal.CaseStatusName}</span>
              </div>
            </div>

            {/* Brief Facts */}
            <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-1">
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1">
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                <span>Brief Facts of the Incident</span>
              </div>
              <p className="text-xs text-slate-200 leading-relaxed">
                {selectedCaseModal.BriefFacts}
              </p>
            </div>

            {/* Modal Action Footer */}
            <div className="flex items-center justify-end pt-2">
              <button
                onClick={() => setSelectedCaseModal(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg"
              >
                Close File Inspection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
