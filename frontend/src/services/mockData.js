/**
 * mockData.js / apiService.js - Live Endpoint Data Service for Drishti Spatial Portal.
 * Connects directly to Alpha's GET /incidents, GET /hotspots, GET /anomalies, GET /resolution/metrics & GET /network live backend APIs.
 */

export const MOCK_INCIDENTS = [
  {
    CaseMasterID: 1001,
    CrimeNo: "FIR-2026-00101",
    CaseNo: "BLR-URB-2026-014",
    CrimeRegisteredDate: "2026-07-20",
    PolicePersonID: 501,
    PoliceStationID: 101,
    PoliceStationName: "Koramangala PS",
    DistrictName: "Bengaluru Urban",
    CaseCategoryID: 1,
    CaseCategoryName: "Cyber Crime",
    GravityOffenceID: 1,
    GravityOffenceName: "Heinous",
    CrimeMajorHeadID: 10,
    CrimeMajorHeadName: "Financial Cyber Fraud & Phishing",
    CrimeMinorHeadID: 102,
    CaseStatusID: 1,
    CaseStatusName: "Under Investigation",
    CourtID: 12,
    IncidentFromDate: "2026-07-19T22:15:00",
    IncidentToDate: "2026-07-20T01:30:00",
    InfoReceivedPSDate: "2026-07-20T08:00:00",
    latitude: 12.9348,
    longitude: 77.6200,
    BriefFacts: "LIVE API: Unauthorized transfer of ₹45 Lakhs via SIM-swapping and spoofed OTP portal targeting tech executive."
  }
];

/**
 * Fetch incident records directly from live backend endpoint.
 * TARGET: GET /incidents (Alpha's FastAPI endpoint on port 8000 or AppSail URL)
 */
export async function fetchIncidents() {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/incidents';
  
  try {
    const res = await fetch(API_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!res.ok) {
      throw new Error(`Live API server returned HTTP status ${res.status}`);
    }

    const json = await res.json();

    if (json && Array.isArray(json.data) && json.data.length > 0) {
      return json.data;
    } else if (Array.isArray(json) && json.length > 0) {
      return json;
    }

    throw new Error('Live API returned empty incident list');
  } catch (err) {
    console.error('Failed to fetch from live backend API:', err);
    throw err;
  }
}

/**
 * Fetch DBSCAN hotspot clusters directly from live backend endpoint.
 * TARGET: GET /hotspots (Gamma's DBSCAN cluster output from Alpha's endpoint)
 */
export async function fetchHotspots() {
  const API_URL = import.meta.env.VITE_HOTSPOTS_API_URL || 'http://localhost:8000/hotspots';
  
  try {
    const res = await fetch(API_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!res.ok) {
      throw new Error(`Hotspots API returned status ${res.status}`);
    }

    const json = await res.json();
    if (json && Array.isArray(json.data) && json.data.length > 0) {
      return json.data;
    } else if (Array.isArray(json) && json.length > 0) {
      return json;
    }
    return [];
  } catch (err) {
    console.error('Failed to fetch hotspots from live API:', err);
    return [];
  }
}

/**
 * Fetch Anomaly baseline deviation flags directly from live backend endpoint.
 * TARGET: GET /anomalies (Gamma's anomaly spike detector output from Alpha's endpoint)
 */
export async function fetchAnomalies() {
  const API_URL = import.meta.env.VITE_ANOMALIES_API_URL || 'http://localhost:8000/anomalies';
  
  try {
    const res = await fetch(API_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!res.ok) {
      throw new Error(`Anomalies API returned status ${res.status}`);
    }

    const json = await res.json();
    if (json && Array.isArray(json.data) && json.data.length > 0) {
      return json.data;
    } else if (Array.isArray(json) && json.length > 0) {
      return json;
    }
    return [];
  } catch (err) {
    console.error('Failed to fetch anomalies from live API:', err);
    return [];
  }
}

/**
 * Fetch Station Resolution Feedback Loop metrics from live backend endpoint.
 * TARGET: GET /resolution/metrics (Alpha's resolution performance endpoint)
 */
export async function fetchResolutionMetrics() {
  const API_URL = import.meta.env.VITE_RESOLUTION_API_URL || 'http://localhost:8000/resolution/metrics';
  
  try {
    const res = await fetch(API_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!res.ok) {
      throw new Error(`Resolution API returned status ${res.status}`);
    }

    const json = await res.json();
    if (json && Array.isArray(json.data) && json.data.length > 0) {
      return json.data;
    } else if (Array.isArray(json) && json.length > 0) {
      return json;
    }
    return [];
  } catch (err) {
    console.error('Failed to fetch resolution metrics from live API:', err);
    return [];
  }
}

/**
 * Fetch Link-Analysis Network Graph from live backend endpoint.
 * TARGET: GET /network (Gamma's link analysis engine output from Alpha's endpoint)
 */
export async function fetchNetworkGraph() {
  const API_URL = import.meta.env.VITE_NETWORK_API_URL || 'http://localhost:8000/network';
  
  try {
    const res = await fetch(API_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!res.ok) {
      throw new Error(`Network API returned status ${res.status}`);
    }

    const json = await res.json();
    if (json && json.data) {
      return json.data;
    }
    return { summary: { total_nodes: 0, total_edges: 0 }, nodes: [], edges: [] };
  } catch (err) {
    console.error('Failed to fetch network graph from live API:', err);
    return { summary: { total_nodes: 0, total_edges: 0 }, nodes: [], edges: [] };
  }
}
