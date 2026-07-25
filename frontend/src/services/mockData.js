/**
 * mockData.js - Live Endpoint Data Service & Mock Data Source for Drishti Spatial Portal.
 * Complies strictly with drishti_catalyst_schema.md & BETA_TRD.md.
 * 
 * Network Graph: Connected to Alpha's real deployed AppSail URL (https://drishti-backend-50044277235.development.catalystappsail.in/network).
 * Resolution Feedback Loop: Holding on mock data waiting for Alpha's new GET /stations/resolution endpoint deployment.
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
    BriefFacts: "Unauthorized transfer of ₹45 Lakhs via SIM-swapping and spoofed OTP portal targeting tech executive."
  },
  {
    CaseMasterID: 1002,
    CrimeNo: "FIR-2026-00102",
    CaseNo: "BLR-URB-2026-022",
    CrimeRegisteredDate: "2026-07-21",
    PolicePersonID: 502,
    PoliceStationID: 102,
    PoliceStationName: "Whitefield PS",
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
    IncidentFromDate: "2026-07-21T09:00:00",
    IncidentToDate: "2026-07-21T11:00:00",
    InfoReceivedPSDate: "2026-07-21T14:00:00",
    latitude: 12.9698,
    longitude: 77.7499,
    BriefFacts: "Phishing attack targeting software firm employee resulting in unauthorized access to corporate accounts."
  },
  {
    CaseMasterID: 1003,
    CrimeNo: "FIR-2026-00103",
    CaseNo: "MYS-2026-089",
    CrimeRegisteredDate: "2026-07-18",
    PolicePersonID: 505,
    PoliceStationID: 105,
    PoliceStationName: "Devaraja PS",
    DistrictName: "Mysuru",
    CaseCategoryID: 2,
    CaseCategoryName: "Property Crime",
    GravityOffenceID: 2,
    GravityOffenceName: "Non-Heinous",
    CrimeMajorHeadID: 20,
    CrimeMajorHeadName: "Commercial Burglary & Theft",
    CrimeMinorHeadID: 201,
    CaseStatusID: 2,
    CaseStatusName: "Chargesheeted",
    CourtID: 14,
    IncidentFromDate: "2026-07-17T23:00:00",
    IncidentToDate: "2026-07-18T04:00:00",
    InfoReceivedPSDate: "2026-07-18T07:30:00",
    latitude: 12.3052,
    longitude: 76.6552,
    BriefFacts: "Break-in at jewelry retail shop near Devaraja Market; stolen items recovered during investigation."
  },
  {
    CaseMasterID: 1006,
    CrimeNo: "FIR-2026-00106",
    CaseNo: "BGM-2026-034",
    CrimeRegisteredDate: "2026-07-17",
    PolicePersonID: 512,
    PoliceStationID: 120,
    PoliceStationName: "Market PS",
    DistrictName: "Belagavi",
    CaseCategoryID: 2,
    CaseCategoryName: "Property Crime",
    GravityOffenceID: 2,
    GravityOffenceName: "Non-Heinous",
    CrimeMajorHeadID: 20,
    CrimeMajorHeadName: "Commercial Burglary & Theft",
    CrimeMinorHeadID: 201,
    CaseStatusID: 2,
    CaseStatusName: "Chargesheeted",
    CourtID: 18,
    IncidentFromDate: "2026-07-16T22:00:00",
    IncidentToDate: "2026-07-17T02:00:00",
    InfoReceivedPSDate: "2026-07-17T08:00:00",
    latitude: 15.8497,
    longitude: 74.5086,
    BriefFacts: "Theft at textile warehouse premises in industrial estate corridor."
  }
];

export const MOCK_RESOLUTION_METRICS = [
  {
    MetricID: 301,
    UnitID: 101,
    PoliceStationID: 101,
    PoliceStationName: "Koramangala PS",
    DistrictName: "Bengaluru Urban",
    PeriodMonth: "2026-07",
    TotalCasesRegistered: 42,
    ChargesheetedCount: 31,
    ConvictedCount: 8,
    DisposedCount: 33,
    ResolutionRate: 78.5,
    AverageDisposalDays: 18,
    DischargeRate: 4.2,
    FeedbackScore: 4.7
  },
  {
    MetricID: 302,
    UnitID: 105,
    PoliceStationID: 105,
    PoliceStationName: "Devaraja PS",
    DistrictName: "Mysuru",
    PeriodMonth: "2026-07",
    TotalCasesRegistered: 28,
    ChargesheetedCount: 22,
    ConvictedCount: 6,
    DisposedCount: 24,
    ResolutionRate: 85.7,
    AverageDisposalDays: 14,
    DischargeRate: 3.5,
    FeedbackScore: 4.9
  },
  {
    MetricID: 303,
    UnitID: 110,
    PoliceStationID: 110,
    PoliceStationName: "Pandeshwar PS",
    DistrictName: "Dakshina Kannada",
    PeriodMonth: "2026-07",
    TotalCasesRegistered: 19,
    ChargesheetedCount: 14,
    ConvictedCount: 4,
    DisposedCount: 15,
    ResolutionRate: 78.9,
    AverageDisposalDays: 21,
    DischargeRate: 5.1,
    FeedbackScore: 4.5
  },
  {
    MetricID: 304,
    UnitID: 115,
    PoliceStationID: 115,
    PoliceStationName: "Suburban PS",
    DistrictName: "Dharwad",
    PeriodMonth: "2026-07",
    TotalCasesRegistered: 16,
    ChargesheetedCount: 10,
    ConvictedCount: 3,
    DisposedCount: 11,
    ResolutionRate: 68.7,
    AverageDisposalDays: 32,
    DischargeRate: 6.2,
    FeedbackScore: 4.2
  }
];

export const MOCK_NETWORK_GRAPH = {
  summary: {
    total_nodes: 591,
    total_edges: 1142,
    repeat_offenders_count: 10
  },
  nodes: [],
  edges: []
};

/**
 * Fetch incident records directly from live backend API or fallback mock.
 */
export async function fetchIncidents() {
  const API_URL = import.meta.env.VITE_API_URL || 'https://drishti-backend-50044277235.development.catalystappsail.in/incidents';

  try {
    const res = await fetch(API_URL, { method: 'GET', headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`API returned HTTP status ${res.status}`);
    const json = await res.json();
    return json.data || json || MOCK_INCIDENTS;
  } catch (err) {
    return MOCK_INCIDENTS;
  }
}

/**
 * Fetch DBSCAN hotspot clusters from backend endpoint.
 */
export async function fetchHotspots() {
  const API_URL = import.meta.env.VITE_HOTSPOTS_API_URL || 'https://drishti-backend-50044277235.development.catalystappsail.in/hotspots';

  try {
    const res = await fetch(API_URL, { method: 'GET', headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`API returned status ${res.status}`);
    const json = await res.json();
    return json.data || json || [];
  } catch (err) {
    return [];
  }
}

/**
 * Fetch Anomaly baseline deviation flags from backend endpoint.
 */
export async function fetchAnomalies() {
  const API_URL = import.meta.env.VITE_ANOMALIES_API_URL || 'https://drishti-backend-50044277235.development.catalystappsail.in/anomalies';

  try {
    const res = await fetch(API_URL, { method: 'GET', headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`API returned status ${res.status}`);
    const json = await res.json();
    return json.data || json || [];
  } catch (err) {
    return [];
  }
}

/**
 * Holding ResolutionLoopPanel on mock data waiting for Alpha's new GET /stations/resolution endpoint.
 */
export async function fetchResolutionMetrics() {
  const API_URL = import.meta.env.VITE_STATION_RESOLUTION_API_URL || 
                  'https://drishti-backend-50044277235.development.catalystappsail.in/stations/resolution';

  try {
    const res = await fetch(API_URL, { method: 'GET', headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`API returned status ${res.status}`);
    const json = await res.json();
    return json.data || json || MOCK_RESOLUTION_METRICS;
  } catch (err) {
    console.warn('Live AppSail resolution endpoint unreachable:', err.message);
    return MOCK_RESOLUTION_METRICS;
  }
}

/**
 * Fetch link-analysis network graph topology directly from Alpha's REAL deployed AppSail endpoint:
 * https://drishti-backend-50044277235.development.catalystappsail.in/network
 */
export async function fetchNetworkGraph() {
  const APPSAIL_URL = import.meta.env.VITE_NETWORK_API_URL || 
                      'https://drishti-backend-50044277235.development.catalystappsail.in/network';
  
  try {
    const res = await fetch(APPSAIL_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!res.ok) {
      throw new Error(`Live AppSail API returned status ${res.status}`);
    }

    const json = await res.json();
    return json.data || json;
  } catch (err) {
    console.warn('Live AppSail network endpoint unreachable:', err.message);
    return MOCK_NETWORK_GRAPH;
  }
}
