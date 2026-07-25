import React, { useState, useEffect, useMemo } from 'react';
import Header from './components/Header';
import ControlPanel from './components/ControlPanel';
import IncidentMap from './components/IncidentMap';
import StationConsole from './components/StationConsole';
import CommandConsole from './components/CommandConsole';
import RoleGateLanding from './components/RoleGateLanding';
import {
  fetchIncidents,
  fetchHotspots,
  fetchAnomalies,
  fetchResolutionMetrics,
  fetchNetworkGraph
} from './services/mockData';
import { Loader2, AlertTriangle, Filter } from 'lucide-react';

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [resolutionMetrics, setResolutionMetrics] = useState([]);
  const [networkData, setNetworkData] = useState({ summary: {}, nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // User Auth State from /auth/me?role=<choice>
  const [userAuth, setUserAuth] = useState(null);

  // View Mode: 'stateMap', 'stationConsole', or 'commandConsole'
  const [viewMode, setViewMode] = useState('stateMap');

  // Filter States (for State Map view)
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGravity, setSelectedGravity] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [showChoropleth, setShowChoropleth] = useState(true);
  const [showHotspots, setShowHotspots] = useState(true);
  const [showAnomalies, setShowAnomalies] = useState(true);

  // Mobile Spatial Filter Drawer State
  const [isMobileFiltersOpen, setIsMobileFiltersOpen] = useState(false);

  // Fetch Incidents, Hotspots, Anomalies, Resolution Metrics & Network Graph on Load
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [incData, hsData, anomData, resData, netData] = await Promise.all([
          fetchIncidents(),
          fetchHotspots(),
          fetchAnomalies(),
          fetchResolutionMetrics(),
          fetchNetworkGraph()
        ]);
        setIncidents(incData);
        setHotspots(hsData);
        setAnomalies(anomData);
        setResolutionMetrics(resData);
        setNetworkData(netData);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch data from live backend API:', err);
        setError('Failed to load spatial analytics data. Please try again.');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Unique Categories for dropdown
  const categories = useMemo(() => {
    const set = new Set(incidents.map((i) => i.CaseCategoryName));
    return Array.from(set).sort();
  }, [incidents]);

  // Filtered Incidents computation
  const filteredIncidents = useMemo(() => {
    return (incidents || []).filter((incident) => {
      if (!incident) return false;
      const q = (searchTerm || '').toLowerCase();
      // Search filter
      const matchesSearch =
        !q ||
        (incident.CrimeNo || '').toLowerCase().includes(q) ||
        (incident.DistrictName || '').toLowerCase().includes(q) ||
        (incident.PoliceStationName || '').toLowerCase().includes(q) ||
        (incident.BriefFacts || '').toLowerCase().includes(q) ||
        (incident.CrimeMajorHeadName || '').toLowerCase().includes(q);

      // Gravity filter
      const matchesGravity =
        selectedGravity === 'All' || incident.GravityOffenceName === selectedGravity;

      // Category filter
      const matchesCategory =
        selectedCategory === 'All' || incident.CaseCategoryName === selectedCategory;

      // Status filter
      const matchesStatus =
        selectedStatus === 'All' || incident.CaseStatusName === selectedStatus;

      return matchesSearch && matchesGravity && matchesCategory && matchesStatus;
    });
  }, [incidents, searchTerm, selectedGravity, selectedCategory, selectedStatus]);

  // Operational Metrics
  const heinousCount = useMemo(
    () => incidents.filter((i) => i.GravityOffenceName === 'Heinous').length,
    [incidents]
  );
  const cyberCount = useMemo(
    () => incidents.filter((i) => i.CaseCategoryName === 'Cyber Crime').length,
    [incidents]
  );
  const investigatingCount = useMemo(
    () => incidents.filter((i) => i.CaseStatusName === 'Under Investigation').length,
    [incidents]
  );

  const resetFilters = () => {
    setSearchTerm('');
    setSelectedGravity('All');
    setSelectedCategory('All');
    setSelectedStatus('All');
  };

  if (!userAuth) {
    return (
      <RoleGateLanding
        onAuthenticate={(authData) => {
          setUserAuth(authData);
          if (authData.selectedRole === 'Station') {
            setViewMode('stationConsole');
          } else if (authData.selectedRole === 'Command') {
            setViewMode('commandConsole');
          }
        }}
      />
    );
  }

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Top Header with Navigation Tabs */}
      <Header
        incidentsCount={incidents.length}
        heinousCount={heinousCount}
        cyberCount={cyberCount}
        investigatingCount={investigatingCount}
        viewMode={viewMode}
        setViewMode={setViewMode}
        userAuth={userAuth}
        onSwitchRole={() => setUserAuth(null)}
      />

      {/* Main Content Body */}
      {loading ? (
        <div className="flex-1 bg-slate-950 flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
          <div className="text-sm font-semibold text-slate-300">
            Fetching Live Spatial Incidents, Hotspots, Anomalies & Link-Analysis Graph...
          </div>
        </div>
      ) : error ? (
        <div className="flex-1 bg-slate-950 flex flex-col items-center justify-center space-y-3 p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-red-400" />
          <div className="text-lg font-bold text-slate-200">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-lg shadow-lg"
          >
            Retry Loading
          </button>
        </div>
      ) : viewMode === 'stationConsole' ? (
        <StationConsole incidents={incidents} />
      ) : viewMode === 'commandConsole' ? (
        <CommandConsole
          incidents={incidents}
          anomalies={anomalies}
          resolutionMetrics={resolutionMetrics}
          networkData={networkData}
        />
      ) : (
        <div className="flex flex-1 relative overflow-hidden">
          {/* Mobile Filter Toggle Button */}
          <button
            onClick={() => setIsMobileFiltersOpen(!isMobileFiltersOpen)}
            className="md:hidden absolute top-3 left-3 z-30 bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl shadow-2xl flex items-center space-x-1.5 text-xs font-bold transition-all"
            title="Toggle Spatial Filters"
          >
            <Filter className="w-4 h-4 text-cyan-400" />
            <span>Filters</span>
          </button>

          {/* Left Control Panel */}
          <ControlPanel
            isMobileOpen={isMobileFiltersOpen}
            onCloseMobile={() => setIsMobileFiltersOpen(false)}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            selectedGravity={selectedGravity}
            setSelectedGravity={setSelectedGravity}
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            selectedStatus={selectedStatus}
            setSelectedStatus={setSelectedStatus}
            showChoropleth={showChoropleth}
            setShowChoropleth={setShowChoropleth}
            showHotspots={showHotspots}
            setShowHotspots={setShowHotspots}
            showAnomalies={showAnomalies}
            setShowAnomalies={setShowAnomalies}
            categories={categories}
            onResetFilters={resetFilters}
            totalFilteredCount={filteredIncidents.length}
            totalCount={incidents.length}
          />

          {/* Right Map Canvas */}
          <main className="flex-1 relative h-full">
            <IncidentMap
              incidents={filteredIncidents}
              hotspots={hotspots}
              anomalies={anomalies}
              showChoropleth={showChoropleth}
              showHotspots={showHotspots}
              showAnomalies={showAnomalies}
              onResetFilters={resetFilters}
            />
          </main>
        </div>
      )}
    </div>
  );
}
