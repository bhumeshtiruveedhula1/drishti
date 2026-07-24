/**
 * mockData.js - Isolated Schema-Compatible Mock Data Source for Drishti Spatial Portal.
 * Complies strictly with drishti_catalyst_schema.md & BETA_TRD.md.
 * 
 * NOTE: Beta Frontend is blocked waiting for Alpha's deployed AppSail backend endpoints for:
 * - GET /stations/{id}/resolution or GET /resolution/metrics
 * - GET /network or GET /link-analysis
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
    total_nodes: 14,
    total_edges: 13,
    repeat_offenders_count: 2
  },
  nodes: [
    { id: "accused_ramesh_kumar", label: "Ramesh Kumar", type: "Accused", metadata: { is_repeat_offender: true, total_incidents: 2 } },
    { id: "case_1001", label: "FIR-2026-00101", type: "CaseMaster", metadata: { CaseMasterID: 1001, CaseNo: "BLR-URB-2026-014", CrimeRegisteredDate: "2026-07-20", latitude: 12.9348, longitude: 77.6200 } },
    { id: "victim_201", label: "Anand Rao", type: "Victim", metadata: { VictimMasterID: 201, CaseMasterID: 1001 } },
    { id: "unit_101", label: "Koramangala PS", type: "Unit", metadata: { UnitID: 101 } },
    { id: "case_1002", label: "FIR-2026-00102", type: "CaseMaster", metadata: { CaseMasterID: 1002, CaseNo: "BLR-URB-2026-022", CrimeRegisteredDate: "2026-07-21", latitude: 12.9698, longitude: 77.7499 } },
    { id: "victim_202", label: "Priya Sharma", type: "Victim", metadata: { VictimMasterID: 202, CaseMasterID: 1002 } },
    { id: "unit_102", label: "Whitefield PS", type: "Unit", metadata: { UnitID: 102 } },
    { id: "accused_suresh_gowda", label: "Suresh Gowda", type: "Accused", metadata: { is_repeat_offender: true, total_incidents: 2 } },
    { id: "case_1003", label: "FIR-2026-00103", type: "CaseMaster", metadata: { CaseMasterID: 1003, CaseNo: "MYS-2026-089", CrimeRegisteredDate: "2026-07-18", latitude: 12.3052, longitude: 76.6552 } },
    { id: "victim_203", label: "Mahadevappa", type: "Victim", metadata: { VictimMasterID: 203, CaseMasterID: 1003 } },
    { id: "unit_105", label: "Devaraja PS", type: "Unit", metadata: { UnitID: 105 } },
    { id: "case_1006", label: "FIR-2026-00106", type: "CaseMaster", metadata: { CaseMasterID: 1006, CaseNo: "BGM-2026-034", CrimeRegisteredDate: "2026-07-17", latitude: 15.8497, longitude: 74.5086 } },
    { id: "victim_204", label: "Silk Warehouse Corp", type: "Victim", metadata: { VictimMasterID: 204, CaseMasterID: 1006 } },
    { id: "unit_120", label: "Market PS", type: "Unit", metadata: { UnitID: 120 } }
  ],
  edges: [
    { source: "accused_ramesh_kumar", target: "case_1001", relationship: "ACCUSED_IN", metadata: { case_id: 1001 } },
    { source: "case_1001", target: "victim_201", relationship: "VICTIM_OF", metadata: { case_id: 1001 } },
    { source: "case_1001", target: "unit_101", relationship: "JURISDICTION_UNIT", metadata: { unit_id: 101 } },
    { source: "accused_ramesh_kumar", target: "case_1002", relationship: "ACCUSED_IN", metadata: { case_id: 1002 } },
    { source: "case_1002", target: "victim_202", relationship: "VICTIM_OF", metadata: { case_id: 1002 } },
    { source: "case_1002", target: "unit_102", relationship: "JURISDICTION_UNIT", metadata: { unit_id: 102 } },
    { source: "case_1001", target: "case_1002", relationship: "SPATIAL_PROXIMITY_CLUSTER", metadata: { distance_km: 14.6, cluster_id: "cluster_1", offender_name: "Ramesh Kumar" } },
    { source: "accused_suresh_gowda", target: "case_1003", relationship: "ACCUSED_IN", metadata: { case_id: 1003 } },
    { source: "case_1003", target: "victim_203", relationship: "VICTIM_OF", metadata: { case_id: 1003 } },
    { source: "case_1003", target: "unit_105", relationship: "JURISDICTION_UNIT", metadata: { unit_id: 105 } },
    { source: "accused_suresh_gowda", target: "case_1006", relationship: "ACCUSED_IN", metadata: { case_id: 1006 } },
    { source: "case_1006", target: "victim_204", relationship: "VICTIM_OF", metadata: { case_id: 1006 } },
    { source: "case_1006", target: "unit_120", relationship: "JURISDICTION_UNIT", metadata: { unit_id: 120 } }
  ]
};

/**
 * Fetch incident records from Alpha's backend endpoint if deployed, or return isolated mock data.
 */
export async function fetchIncidents() {
  const API_URL = import.meta.env.VITE_API_URL;
  if (!API_URL) return MOCK_INCIDENTS;

  try {
    const res = await fetch(API_URL, { method: 'GET', headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`API returned HTTP status ${res.status}`);
    const json = await res.json();
    return json.data || json || MOCK_INCIDENTS;
  } catch (err) {
    console.warn('Failed to fetch from live backend API, falling back to mock incidents:', err.message);
    return MOCK_INCIDENTS;
  }
}

/**
 * Fetch DBSCAN hotspot clusters from backend endpoint if deployed, or return empty array.
 */
export async function fetchHotspots() {
  const API_URL = import.meta.env.VITE_HOTSPOTS_API_URL;
  if (!API_URL) return [];

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
 * Fetch Anomaly baseline deviation flags from backend endpoint if deployed, or return empty array.
 */
export async function fetchAnomalies() {
  const API_URL = import.meta.env.VITE_ANOMALIES_API_URL;
  if (!API_URL) return [];

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
 * Returns station resolution feedback loop metrics from schema-compatible mock data source.
 * NOTE: Beta Frontend is blocked waiting for Alpha's deployed AppSail endpoints.
 */
export async function fetchResolutionMetrics() {
  const API_URL = import.meta.env.VITE_RESOLUTION_API_URL;
  if (!API_URL) return MOCK_RESOLUTION_METRICS;

  try {
    const res = await fetch(API_URL, { method: 'GET', headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`API returned status ${res.status}`);
    const json = await res.json();
    return json.data || json || MOCK_RESOLUTION_METRICS;
  } catch (err) {
    return MOCK_RESOLUTION_METRICS;
  }
}

/**
 * Returns link-analysis network graph topology from schema-compatible mock data source.
 * NOTE: Beta Frontend is blocked waiting for Alpha's deployed AppSail endpoints.
 */
export async function fetchNetworkGraph() {
  const API_URL = import.meta.env.VITE_NETWORK_API_URL;
  if (!API_URL) return MOCK_NETWORK_GRAPH;

  try {
    const res = await fetch(API_URL, { method: 'GET', headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`API returned status ${res.status}`);
    const json = await res.json();
    return json.data || json || MOCK_NETWORK_GRAPH;
  } catch (err) {
    return MOCK_NETWORK_GRAPH;
  }
}
