import React, { useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, ZoomControl } from 'react-leaflet';
import L from 'leaflet';
import {
  Building2,
  Shield,
  User,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Search,
  FileText,
  MapPin,
  Eye,
  X,
  Phone,
  FilterX,
  RotateCcw
} from 'lucide-react';

// Marker icon for station map
const createStationMarkerIcon = (gravity) => {
  const isHeinous = gravity === 'Heinous';
  const bgClass = isHeinous
    ? 'bg-gradient-to-tr from-red-600 to-rose-400 border-red-200 text-white shadow-red-500/50'
    : 'bg-gradient-to-tr from-amber-500 to-yellow-300 border-amber-100 text-slate-950 shadow-amber-500/50';

  return L.divIcon({
    className: 'custom-station-pin',
    html: `
      <div class="relative flex items-center justify-center w-8 h-8">
        <div class="w-7 h-7 rounded-full ${bgClass} border-2 flex items-center justify-center shadow-lg font-black text-xs">
          ${isHeinous ? '⚡' : '📌'}
        </div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

export default function StationConsole({ incidents }) {
  // Extract unique police stations
  const stationsList = useMemo(() => {
    const map = new Map();
    (incidents || []).forEach((inc) => {
      if (inc && inc.PoliceStationID && !map.has(inc.PoliceStationID)) {
        map.set(inc.PoliceStationID, {
          id: inc.PoliceStationID,
          name: inc.PoliceStationName || `Station #${inc.PoliceStationID}`,
          district: inc.DistrictName || 'Karnataka Police',
          sho: `Insp. R. V. Patil (KGID #${inc.PolicePersonID || 501})`,
          phone: "+91 80 2294 2200"
        });
      }
    });
    return Array.from(map.values()).sort((a, b) => (a.name || '').localeCompare(b.name || ''));
  }, [incidents]);

  // Active Selected Station
  const [selectedStationId, setSelectedStationId] = useState(
    stationsList[0]?.id || 101
  );

  const activeStation = useMemo(() => {
    return (
      stationsList.find((s) => s.id === Number(selectedStationId)) ||
      stationsList[0] || {
        id: 101,
        name: 'Koramangala PS',
        district: 'Bengaluru Urban',
        sho: 'Insp. R. V. Patil (KGID #501)',
        phone: '+91 80 2294 2200'
      }
    );
  }, [stationsList, selectedStationId]);

  // Filter incidents for active station
  const stationIncidents = useMemo(() => {
    return (incidents || []).filter(
      (inc) => inc && Number(inc.PoliceStationID) === Number(activeStation.id)
    );
  }, [incidents, activeStation]);

  // Safeguard coordinates for Leaflet rendering
  const safeStationIncidents = useMemo(() => {
    return stationIncidents.filter(
      (inc) =>
        inc &&
        typeof inc.latitude === 'number' &&
        typeof inc.longitude === 'number' &&
        !isNaN(inc.latitude) &&
        !isNaN(inc.longitude)
    );
  }, [stationIncidents]);

  // Table search & filter
  const [tableSearch, setTableSearch] = useState('');
  const [selectedCaseModal, setSelectedCaseModal] = useState(null);

  const filteredStationIncidents = useMemo(() => {
    return stationIncidents.filter((inc) => {
      if (!tableSearch) return true;
      const q = tableSearch.toLowerCase();
      return (
        (inc.CrimeNo || '').toLowerCase().includes(q) ||
        (inc.CaseNo || '').toLowerCase().includes(q) ||
        (inc.CaseCategoryName || '').toLowerCase().includes(q) ||
        (inc.CrimeMajorHeadName || '').toLowerCase().includes(q) ||
        (inc.BriefFacts || '').toLowerCase().includes(q)
      );
    });
  }, [stationIncidents, tableSearch]);

  // Station Metrics
  const totalCases = stationIncidents.length;
  const heinousCount = stationIncidents.filter(
    (i) => i.GravityOffenceName === 'Heinous'
  ).length;
  const investigatingCount = stationIncidents.filter(
    (i) => i.CaseStatusName === 'Under Investigation'
  ).length;
  const chargesheetedCount = stationIncidents.filter(
    (i) => i.CaseStatusName === 'Chargesheeted'
  ).length;

  // Station Map Center
  const mapCenter = useMemo(() => {
    if (safeStationIncidents.length > 0) {
      return [safeStationIncidents[0].latitude, safeStationIncidents[0].longitude];
    }
    return [12.9348, 77.62]; // Default Koramangala
  }, [safeStationIncidents]);

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-slate-950 text-slate-100 overflow-hidden">
      {/* Top Station Control Bar */}
      <div className="bg-slate-900/90 border-b border-slate-800 px-3 sm:px-6 py-2.5 flex flex-wrap items-center justify-between gap-3 shrink-0 z-20">
        {/* Left: Station Info & Selector */}
        <div className="flex items-center space-x-3 sm:space-x-4">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center shrink-0">
            <Building2 className="w-4 h-4 sm:w-5 sm:h-5 text-cyan-400" />
          </div>
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Police Station Jurisdiction Console
            </div>
            <div className="flex flex-wrap items-center gap-2 mt-0.5">
              <select
                value={selectedStationId}
                onChange={(e) => setSelectedStationId(e.target.value)}
                className="bg-slate-950 border border-cyan-500/40 rounded-lg px-2.5 py-1 text-xs sm:text-sm font-bold text-cyan-300 focus:outline-none focus:border-cyan-400 transition-colors cursor-pointer"
              >
                {stationsList.map((st) => (
                  <option key={st.id} value={st.id}>
                    {st.name} ({st.district})
                  </option>
                ))}
              </select>
              <span className="text-xs text-slate-400 flex items-center space-x-1">
                <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                <span>{activeStation.district}</span>
              </span>
            </div>
          </div>
        </div>

        {/* Middle: Station Officer Metadata */}
        <div className="hidden lg:flex items-center space-x-4 text-xs bg-slate-950/80 px-3.5 py-1.5 rounded-xl border border-slate-800">
          <div className="flex items-center space-x-2">
            <User className="w-4 h-4 text-cyan-400" />
            <div>
              <div className="text-[9px] text-slate-400 uppercase">Station House Officer</div>
              <div className="font-semibold text-slate-200">{activeStation.sho}</div>
            </div>
          </div>
          <div className="h-6 w-px bg-slate-800" />
          <div className="flex items-center space-x-2">
            <Phone className="w-4 h-4 text-emerald-400" />
            <div>
              <div className="text-[10px] text-slate-400 uppercase">PS Desk Line</div>
              <div className="font-semibold text-slate-200">{activeStation.phone}</div>
            </div>
          </div>
        </div>

        {/* Right: Station Incident Counters */}
        <div className="grid grid-cols-2 sm:flex items-center gap-2 text-xs">
          <div className="bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-center min-w-[70px]">
            <div className="text-[9px] text-slate-400 uppercase font-semibold">Station FIRs</div>
            <div className="text-xs sm:text-sm font-bold text-cyan-400 leading-tight">{totalCases}</div>
          </div>
          <div className="bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-center min-w-[70px]">
            <div className="text-[9px] text-slate-400 uppercase font-semibold">Heinous</div>
            <div className="text-xs sm:text-sm font-bold text-red-400 leading-tight">{heinousCount}</div>
          </div>
          <div className="bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-center min-w-[70px]">
            <div className="text-[9px] text-slate-400 uppercase font-semibold">Investigating</div>
            <div className="text-xs sm:text-sm font-bold text-amber-400 leading-tight">{investigatingCount}</div>
          </div>
          <div className="bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-center min-w-[70px]">
            <div className="text-[9px] text-slate-400 uppercase font-semibold">Chargesheeted</div>
            <div className="text-xs sm:text-sm font-bold text-emerald-400 leading-tight">{chargesheetedCount}</div>
          </div>
        </div>
      </div>

      {/* Main Split View: Left Station Map, Right Station Roster */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-0 min-h-0 overflow-y-auto lg:overflow-hidden">
        {/* Left Column: Station Jurisdiction Map (5 cols) */}
        <div className="lg:col-span-5 h-64 sm:h-80 lg:h-full relative border-b lg:border-b-0 lg:border-r border-slate-800">
          <MapContainer
            key={`station-map-${activeStation.id}`}
            center={mapCenter}
            zoom={12}
            zoomControl={false}
            scrollWheelZoom={true}
            className="w-full h-full z-10"
          >
            <ZoomControl position="bottomright" />
            <TileLayer
              attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            {safeStationIncidents.map((incident) => (
              <Marker
                key={incident.CaseMasterID}
                position={[incident.latitude, incident.longitude]}
                icon={createStationMarkerIcon(incident.GravityOffenceName)}
              >
                <Popup>
                  <div className="p-2 text-xs space-y-1.5">
                    <div className="font-bold text-cyan-300">{incident.CrimeNo}</div>
                    <div className="text-slate-200 font-semibold">{incident.CrimeMajorHeadName}</div>
                    <div className="text-slate-400 text-[11px]">{incident.BriefFacts}</div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>

          {/* Map Overlay Badge */}
          <div className="absolute top-3 left-3 z-20 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-800 shadow-xl flex items-center space-x-2 pointer-events-none">
            <Shield className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold text-slate-200">
              {activeStation.name} Local Map
            </span>
          </div>
        </div>

        {/* Right Column: Station Case Roster Table (7 cols) */}
        <div className="lg:col-span-7 h-full flex flex-col bg-slate-900/40 min-h-0 overflow-hidden">
          {/* Table Search & Controls Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between gap-4 bg-slate-900/80">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                Station FIR Roster ({filteredStationIncidents.length} Records)
              </h3>
            </div>
            <div className="relative w-64">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                value={tableSearch}
                onChange={(e) => setTableSearch(e.target.value)}
                placeholder="Filter FIR / Major Head..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>
          </div>

          {/* Table Container */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
            {filteredStationIncidents.length === 0 ? (
              <div className="h-full min-h-[220px] flex flex-col items-center justify-center text-center p-6 bg-slate-950/60 rounded-xl border border-slate-800 space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                  <FilterX className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                    No FIR Records Found for {activeStation.name}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 max-w-sm">
                    {tableSearch
                      ? `No case records match your query "${tableSearch}".`
                      : 'No criminal incidents currently registered under this station jurisdiction.'}
                  </p>
                </div>
                {tableSearch && (
                  <button
                    onClick={() => setTableSearch('')}
                    className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-semibold rounded-lg border border-slate-700 flex items-center space-x-1.5 transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Clear Search Filter</span>
                  </button>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto custom-scrollbar rounded-xl border border-slate-800 bg-slate-950/60 shadow-xl">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
                      <th className="p-3">FIR Number</th>
                      <th className="p-3">Crime Head & Category</th>
                      <th className="p-3">Gravity</th>
                      <th className="p-3">Reg. Date</th>
                      <th className="p-3">Status</th>
                      <th className="p-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredStationIncidents.map((incident) => (
                      <tr
                        key={incident.CaseMasterID}
                        className="hover:bg-slate-900/60 transition-colors group cursor-pointer"
                        onClick={() => setSelectedCaseModal(incident)}
                      >
                        <td className="p-3 font-bold text-cyan-300">
                          {incident.CrimeNo}
                          <div className="text-[10px] font-normal text-slate-500">{incident.CaseNo}</div>
                        </td>
                        <td className="p-3 max-w-xs">
                          <div className="font-semibold text-slate-200 truncate">
                            {incident.CrimeMajorHeadName}
                          </div>
                          <div className="text-[10px] text-cyan-400 font-medium">
                            {incident.CaseCategoryName}
                          </div>
                        </td>
                        <td className="p-3">
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                              incident.GravityOffenceName === 'Heinous'
                                ? 'bg-red-950 text-red-400 border border-red-800/80'
                                : 'bg-amber-950 text-amber-400 border border-amber-800/80'
                            }`}
                          >
                            {incident.GravityOffenceName}
                          </span>
                        </td>
                        <td className="p-3 text-slate-300 font-medium">
                          {incident.CrimeRegisteredDate}
                        </td>
                        <td className="p-3">
                          <span className="font-medium text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-700">
                            {incident.CaseStatusName}
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedCaseModal(incident);
                            }}
                            className="p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-600 text-slate-300 hover:text-white transition-colors"
                            title="View Case Master Details"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Case Details Modal Drawer */}
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
                  Case File: {selectedCaseModal.CaseNo} • {selectedCaseModal.PoliceStationName}
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
