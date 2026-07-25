import React, { useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import karnatakaGeoJSON from '../data/karnatakaDistricts.json';
import { Shield, MapPin, Building2, FileText, Calendar, Clock, Layers, Flame, AlertCircle, TrendingUp } from 'lucide-react';

// Create custom animated SVG/HTML divIcon pins for Leaflet
const createCustomMarkerIcon = (gravity) => {
  const isHeinous = gravity === 'Heinous';
  const bgClass = isHeinous 
    ? 'bg-gradient-to-tr from-red-600 to-rose-400 border-red-200 text-white shadow-red-500/50' 
    : 'bg-gradient-to-tr from-amber-500 to-yellow-300 border-amber-100 text-slate-950 shadow-amber-500/50';
  const pulseBg = isHeinous ? 'bg-red-500/60' : 'bg-amber-400/60';

  return L.divIcon({
    className: 'custom-map-pin',
    html: `
      <div class="relative flex items-center justify-center w-9 h-9">
        <div class="absolute w-8 h-8 rounded-full ${pulseBg} animate-ping opacity-75"></div>
        <div class="w-8 h-8 rounded-full ${bgClass} border-2 flex items-center justify-center shadow-lg font-black text-xs z-10">
          ${isHeinous ? '⚡' : '📌'}
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18]
  });
};

// Create custom hazard flame marker for DBSCAN Hotspot Clusters
const createHotspotMarkerIcon = () => {
  return L.divIcon({
    className: 'custom-hotspot-pin',
    html: `
      <div class="relative flex items-center justify-center w-10 h-10">
        <div class="absolute w-10 h-10 rounded-full bg-red-600/50 animate-ping"></div>
        <div class="w-9 h-9 rounded-full bg-gradient-to-br from-red-600 via-rose-600 to-amber-600 border-2 border-white flex items-center justify-center shadow-2xl font-black text-xs text-white z-10">
          🔥
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20]
  });
};

// Create custom anomaly warning beacon for Trend Spikes
const createAnomalyMarkerIcon = (severity) => {
  const isCritical = severity === 'CRITICAL';
  return L.divIcon({
    className: 'custom-anomaly-pin',
    html: `
      <div class="relative flex items-center justify-center w-10 h-10">
        <div class="absolute w-10 h-10 rounded-full ${isCritical ? 'bg-rose-500/70' : 'bg-amber-500/70'} animate-ping"></div>
        <div class="w-9 h-9 rounded-full ${isCritical ? 'bg-gradient-to-br from-rose-600 to-red-700' : 'bg-gradient-to-br from-amber-500 to-yellow-600'} border-2 border-white flex items-center justify-center shadow-2xl font-black text-xs text-white z-10">
          🚨
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20]
  });
};

// Helper for choropleth color scale based on incident density
const getChoroplethColor = (count) => {
  if (count >= 2) return '#f59e0b';
  if (count === 1) return '#0284c7';
  return '#0f172a';
};

export default function IncidentMap({
  incidents,
  hotspots = [],
  anomalies = [],
  showChoropleth = true,
  showHotspots = true,
  showAnomalies = true
}) {
  const karnatakaCenter = [14.8, 76.2];

  // Map incident counts by district name
  const districtCounts = useMemo(() => {
    const counts = {};
    incidents.forEach((inc) => {
      if (inc.DistrictName) {
        counts[inc.DistrictName] = (counts[inc.DistrictName] || 0) + 1;
      }
    });
    return counts;
  }, [incidents]);

  // Dynamic GeoJSON polygon styling
  const districtStyle = (feature) => {
    const districtName = feature.properties.DistrictName || '';
    const count = districtCounts[districtName] || 0;
    const fillColor = showChoropleth ? getChoroplethColor(count) : '#0f172a';
    const fillOpacity = showChoropleth ? (count >= 2 ? 0.6 : count === 1 ? 0.45 : 0.2) : 0.15;

    return {
      fillColor,
      weight: 1.5,
      opacity: 0.85,
      color: count >= 2 ? '#fbbf24' : '#0284c7',
      dashArray: count >= 2 ? '' : '4, 4',
      fillOpacity
    };
  };

  // Hover effect & tooltips for District Polygons
  const onEachDistrict = (feature, layer) => {
    const districtName = feature.properties.DistrictName || 'Karnataka District';
    const count = districtCounts[districtName] || 0;

    layer.bindTooltip(
      `<div class="px-1 py-0.5 text-xs font-medium">
        <div class="font-bold text-cyan-300">${districtName}</div>
        <div class="text-slate-300 mt-0.5 font-sans">${count} Incident${count === 1 ? '' : 's'} Logged</div>
      </div>`,
      { sticky: true, direction: 'top' }
    );

    layer.on({
      mouseover: (e) => {
        const l = e.target;
        l.setStyle({
          weight: 2.5,
          color: '#38bdf8',
          fillOpacity: Math.min((districtStyle(feature).fillOpacity || 0.4) + 0.25, 0.8)
        });
      },
      mouseout: (e) => {
        const l = e.target;
        l.setStyle(districtStyle(feature));
      }
    });
  };

  return (
    <div className="w-full h-full relative">
      <MapContainer
        center={karnatakaCenter}
        zoom={7}
        minZoom={6}
        maxZoom={14}
        scrollWheelZoom={true}
        className="w-full h-full z-10"
      >
        {/* Dark Matter Basemap Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Karnataka District GeoJSON Layer */}
        <GeoJSON
          key={`geojson-${showChoropleth}-${JSON.stringify(districtCounts)}`}
          data={karnatakaGeoJSON}
          style={districtStyle}
          onEachFeature={onEachDistrict}
        />

        {/* DBSCAN Hotspot Cluster Overlay Layer */}
        {showHotspots &&
          hotspots.map((hs) => (
            <React.Fragment key={`hotspot-group-${hs.HotspotClusterID}`}>
              {/* Cluster Radius Circle Boundary */}
              <Circle
                center={[hs.latitude, hs.longitude]}
                radius={hs.radius_meters || 2500}
                pathOptions={{
                  fillColor: '#ef4444',
                  fillOpacity: 0.22,
                  color: '#f87171',
                  weight: 2,
                  dashArray: '6, 6'
                }}
              />

              {/* Hazard Center Marker */}
              <Marker
                position={[hs.latitude, hs.longitude]}
                icon={createHotspotMarkerIcon(hs.RiskScore)}
              >
                <Popup className="hotspot-popup">
                  <div className="p-3.5 max-w-sm space-y-2.5">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center space-x-1.5 text-red-400 font-bold text-xs uppercase tracking-wider">
                        <Flame className="w-4 h-4 text-red-500 animate-bounce" />
                        <span>DBSCAN Hotspot Cluster</span>
                      </div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-950 text-red-400 border border-red-800">
                        Risk {hs.RiskScore} / 10
                      </span>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-slate-100 leading-snug">
                        {hs.ClusterName}
                      </h4>
                      <p className="text-[11px] text-cyan-400 font-semibold mt-0.5">
                        Dominant Category: {hs.DominantCategory}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-950/80 p-2 rounded-lg border border-slate-800">
                      <div className="flex items-center space-x-1.5 text-slate-300">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                        <span>{hs.IncidentCount} Cases Clustered</span>
                      </div>
                      <div className="flex items-center space-x-1.5 text-slate-300">
                        <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{(hs.radius_meters / 1000).toFixed(1)} km Radius</span>
                      </div>
                    </div>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          ))}

        {/* Anomaly Baseline Deviation Layer */}
        {showAnomalies &&
          anomalies.map((anom) => (
            <Marker
              key={`anomaly-${anom.AnomalyFlagID}`}
              position={[anom.latitude, anom.longitude]}
              icon={createAnomalyMarkerIcon(anom.Severity)}
            >
              <Popup className="anomaly-popup">
                <div className="p-3.5 max-w-sm space-y-2.5">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <div className="flex items-center space-x-1.5 text-amber-400 font-bold text-xs uppercase tracking-wider">
                      <TrendingUp className="w-4 h-4 text-amber-400 animate-pulse" />
                      <span>Anomaly Baseline Deviation</span>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-950 text-rose-400 border border-rose-800">
                      +{anom.SpikePercentage}% Spike
                    </span>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold text-slate-100 leading-snug">
                      {anom.PoliceStationName} ({anom.DistrictName})
                    </h4>
                    <p className="text-[11px] text-cyan-400 font-semibold mt-0.5">
                      Major Head: {anom.CrimeMajorHeadName}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-950/80 p-2 rounded-lg border border-slate-800">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">Current 7-Day</span>
                      <span className="text-sm font-bold text-amber-400">{anom.CurrentPeriodCount} Cases</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-bold block">Historical Baseline</span>
                      <span className="text-sm font-bold text-slate-300">{anom.BaselineMonthlyAverage} avg/mo</span>
                    </div>
                  </div>

                  <div className="text-xs text-slate-300 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                    <p className="leading-relaxed text-slate-200">{anom.AlertSummary}</p>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}

        {/* Raw Incident Marker Pins */}
        {incidents.map((incident) => (
          <Marker
            key={incident.CaseMasterID}
            position={[incident.latitude, incident.longitude]}
            icon={createCustomMarkerIcon(incident.GravityOffenceName)}
          >
            <Popup className="incident-popup">
              <div className="p-3.5 max-w-sm space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div className="flex items-center space-x-1.5">
                    <Shield className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-bold text-cyan-300 tracking-wide">
                      {incident.CrimeNo}
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                      incident.GravityOffenceName === 'Heinous'
                        ? 'bg-red-950 text-red-400 border border-red-800'
                        : 'bg-amber-950 text-amber-400 border border-amber-800'
                    }`}
                  >
                    {incident.GravityOffenceName}
                  </span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-slate-100 leading-snug">
                    {incident.CrimeMajorHeadName}
                  </h3>
                  <div className="text-xs font-semibold text-slate-400 mt-0.5">
                    Category: <span className="text-cyan-400">{incident.CaseCategoryName}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-950/80 p-2 rounded-lg border border-slate-800/80">
                  <div className="flex items-center space-x-1.5 text-slate-300">
                    <Building2 className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">{incident.PoliceStationName}</span>
                  </div>
                  <div className="flex items-center space-x-1.5 text-slate-300">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">{incident.DistrictName}</span>
                  </div>
                  <div className="flex items-center space-x-1.5 text-slate-300">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>{incident.CrimeRegisteredDate}</span>
                  </div>
                  <div className="flex items-center space-x-1.5 text-slate-300">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">
                      {new Date(incident.IncidentFromDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>

                <div className="text-xs text-slate-300 bg-slate-900/60 p-2 rounded border border-slate-800">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center space-x-1">
                    <FileText className="w-3 h-3 text-cyan-400" />
                    <span>Brief Facts</span>
                  </div>
                  <p className="line-clamp-3 leading-relaxed text-slate-200">
                    {incident.BriefFacts}
                  </p>
                </div>

                <div className="flex items-center justify-between text-[11px] pt-1">
                  <span className="text-slate-400">Status:</span>
                  <span className="font-semibold px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
                    {incident.CaseStatusName}
                  </span>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* District Choropleth Legend Overlay */}
      {showChoropleth && (
        <div className="absolute bottom-6 right-6 z-20 bg-slate-900/90 backdrop-blur-md p-3 rounded-xl border border-slate-800 shadow-2xl text-xs space-y-2 max-w-xs">
          <div className="flex items-center space-x-1.5 font-bold text-slate-200 uppercase tracking-wider text-[11px]">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>District Choropleth Density</span>
          </div>
          <div className="space-y-1.5 pt-1">
            <div className="flex items-center space-x-2 text-[11px] text-slate-300">
              <span className="w-3.5 h-3.5 rounded bg-amber-500 border border-amber-300 shadow-sm"></span>
              <span>2+ Incidents (High Density)</span>
            </div>
            <div className="flex items-center space-x-2 text-[11px] text-slate-300">
              <span className="w-3.5 h-3.5 rounded bg-sky-600 border border-sky-400 shadow-sm"></span>
              <span>1 Incident (Moderate Density)</span>
            </div>
            <div className="flex items-center space-x-2 text-[11px] text-slate-300">
              <span className="w-3.5 h-3.5 rounded bg-slate-800 border border-slate-700"></span>
              <span>0 Incidents (Zero Density)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
