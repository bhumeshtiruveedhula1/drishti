import os
import sys
from typing import Optional, List, Dict, Any

print("Starting AppSail server...", flush=True)

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from network_analysis import perform_link_analysis, SAMPLE_UNITS, SAMPLE_CASES, SAMPLE_ACCUSED, SAMPLE_VICTIMS
except ImportError:
    from backend.network_analysis import perform_link_analysis, SAMPLE_UNITS, SAMPLE_CASES, SAMPLE_ACCUSED, SAMPLE_VICTIMS

app = FastAPI(title="Drishti Backend API - Final Slices")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initial Seed Data for CaseMaster Incidents
SEED_INCIDENTS = [
  {
    "CaseMasterID": 1001,
    "CrimeNo": "FIR-2026-00101",
    "CaseNo": "BLR-URB-2026-014",
    "CrimeRegisteredDate": "2026-07-20",
    "PolicePersonID": 501,
    "PoliceStationID": 101,
    "PoliceStationName": "Koramangala PS",
    "DistrictName": "Bengaluru Urban",
    "CaseCategoryID": 1,
    "CaseCategoryName": "Cyber Crime",
    "GravityOffenceID": 1,
    "GravityOffenceName": "Heinous",
    "CrimeMajorHeadID": 10,
    "CrimeMajorHeadName": "Financial Cyber Fraud & Phishing",
    "CrimeMinorHeadID": 102,
    "CaseStatusID": 1,
    "CaseStatusName": "Under Investigation",
    "CourtID": 12,
    "IncidentFromDate": "2026-07-19T22:15:00",
    "IncidentToDate": "2026-07-20T01:30:00",
    "InfoReceivedPSDate": "2026-07-20T08:00:00",
    "latitude": 12.9348,
    "longitude": 77.6200,
    "BriefFacts": "LIVE API: Unauthorized transfer of ₹45 Lakhs via SIM-swapping and spoofed OTP portal targeting tech executive."
  },
  {
    "CaseMasterID": 1002,
    "CrimeNo": "FIR-2026-00102",
    "CaseNo": "BLR-URB-2026-022",
    "CrimeRegisteredDate": "2026-07-21",
    "PolicePersonID": 504,
    "PoliceStationID": 102,
    "PoliceStationName": "Whitefield PS",
    "DistrictName": "Bengaluru Urban",
    "CaseCategoryID": 2,
    "CaseCategoryName": "Theft & Housebreaking",
    "GravityOffenceID": 2,
    "GravityOffenceName": "Non-Heinous",
    "CrimeMajorHeadID": 12,
    "CrimeMajorHeadName": "Night Housebreaking & Burglary",
    "CrimeMinorHeadID": 105,
    "CaseStatusID": 2,
    "CaseStatusName": "Chargesheeted",
    "CourtID": 12,
    "IncidentFromDate": "2026-07-20T23:00:00",
    "IncidentToDate": "2026-07-21T04:00:00",
    "InfoReceivedPSDate": "2026-07-21T07:30:00",
    "latitude": 12.9698,
    "longitude": 77.7499,
    "BriefFacts": "LIVE API: Break-in at gated villa premises during owner's out-of-town travel. Gold ornaments valued at ₹8.5L stolen."
  },
  {
    "CaseMasterID": 1003,
    "CrimeNo": "FIR-2026-00103",
    "CaseNo": "MYS-2026-089",
    "CrimeRegisteredDate": "2026-07-18",
    "PolicePersonID": 512,
    "PoliceStationID": 105,
    "PoliceStationName": "Devaraja PS",
    "DistrictName": "Mysuru",
    "CaseCategoryID": 3,
    "CaseCategoryName": "Assault & Bodily Offences",
    "GravityOffenceID": 1,
    "GravityOffenceName": "Heinous",
    "CrimeMajorHeadID": 14,
    "CrimeMajorHeadName": "Attempt to Murder & Armed Assault",
    "CrimeMinorHeadID": 110,
    "CaseStatusID": 1,
    "CaseStatusName": "Under Investigation",
    "CourtID": 8,
    "IncidentFromDate": "2026-07-18T19:45:00",
    "IncidentToDate": "2026-07-18T20:15:00",
    "InfoReceivedPSDate": "2026-07-18T20:45:00",
    "latitude": 12.3052,
    "longitude": 76.6552,
    "BriefFacts": "LIVE API: Armed altercation near market square involving rival local gang members. Two victims admitted to KR Hospital."
  },
  {
    "CaseMasterID": 1004,
    "CrimeNo": "FIR-2026-00104",
    "CaseNo": "DK-2026-045",
    "CrimeRegisteredDate": "2026-07-22",
    "PolicePersonID": 520,
    "PoliceStationID": 110,
    "PoliceStationName": "Pandeshwar PS",
    "DistrictName": "Dakshina Kannada",
    "CaseCategoryID": 4,
    "CaseCategoryName": "Narcotics & NDPS",
    "GravityOffenceID": 1,
    "GravityOffenceName": "Heinous",
    "CrimeMajorHeadID": 18,
    "CrimeMajorHeadName": "Commercial Drug Trafficking (NDPS Act)",
    "CrimeMinorHeadID": 115,
    "CaseStatusID": 1,
    "CaseStatusName": "Under Investigation",
    "CourtID": 15,
    "IncidentFromDate": "2026-07-22T02:00:00",
    "IncidentToDate": "2026-07-22T03:30:00",
    "InfoReceivedPSDate": "2026-07-22T04:15:00",
    "latitude": 12.8605,
    "longitude": 74.8431,
    "BriefFacts": "LIVE API: Interception of coastal cargo container carrying synthetic contraband (MDMA) worth ₹1.2 Cr."
  },
  {
    "CaseMasterID": 1005,
    "CrimeNo": "FIR-2026-00105",
    "CaseNo": "HBD-2026-078",
    "CrimeRegisteredDate": "2026-07-15",
    "PolicePersonID": 531,
    "PoliceStationID": 115,
    "PoliceStationName": "Suburban PS",
    "DistrictName": "Dharwad",
    "CaseCategoryID": 5,
    "CaseCategoryName": "Extortion & Gangsterism",
    "GravityOffenceID": 1,
    "GravityOffenceName": "Heinous",
    "CrimeMajorHeadID": 20,
    "CrimeMajorHeadName": "Extortion Racket & Protection Money",
    "CrimeMinorHeadID": 122,
    "CaseStatusID": 2,
    "CaseStatusName": "Chargesheeted",
    "CourtID": 6,
    "IncidentFromDate": "2026-07-14T15:00:00",
    "IncidentToDate": "2026-07-15T10:00:00",
    "InfoReceivedPSDate": "2026-07-15T11:30:00",
    "latitude": 15.3647,
    "longitude": 75.1240,
    "BriefFacts": "LIVE API: Threatening local logistics business owners for recurring monthly protection pay-offs."
  },
  {
    "CaseMasterID": 1006,
    "CrimeNo": "FIR-2026-00106",
    "CaseNo": "BGM-2026-034",
    "CrimeRegisteredDate": "2026-07-17",
    "PolicePersonID": 540,
    "PoliceStationID": 120,
    "PoliceStationName": "Market PS",
    "DistrictName": "Belagavi",
    "CaseCategoryID": 2,
    "CaseCategoryName": "Theft & Housebreaking",
    "GravityOffenceID": 2,
    "GravityOffenceName": "Non-Heinous",
    "CrimeMajorHeadID": 11,
    "CrimeMajorHeadName": "Commercial Property Theft",
    "CrimeMinorHeadID": 104,
    "CaseStatusID": 3,
    "CaseStatusName": "Pending",
    "CourtID": 4,
    "IncidentFromDate": "2026-07-16T21:00:00",
    "IncidentToDate": "2026-07-17T06:00:00",
    "InfoReceivedPSDate": "2026-07-17T08:00:00",
    "latitude": 15.8497,
    "longitude": 74.5086,
    "BriefFacts": "LIVE API: Theft of textiles and raw silk goods from commercial warehouse during torrential rainfall."
  },
  {
    "CaseMasterID": 1007,
    "CrimeNo": "FIR-2026-00107",
    "CaseNo": "KLB-2026-092",
    "CrimeRegisteredDate": "2026-07-19",
    "PolicePersonID": 552,
    "PoliceStationID": 125,
    "PoliceStationName": "Brahampur PS",
    "DistrictName": "Kalaburagi",
    "CaseCategoryID": 3,
    "CaseCategoryName": "Assault & Bodily Offences",
    "GravityOffenceID": 2,
    "GravityOffenceName": "Non-Heinous",
    "CrimeMajorHeadID": 15,
    "CrimeMajorHeadName": "Rioting & Public Nuisance",
    "CrimeMinorHeadID": 112,
    "CaseStatusID": 1,
    "CaseStatusName": "Under Investigation",
    "CourtID": 9,
    "IncidentFromDate": "2026-07-19T18:00:00",
    "IncidentToDate": "2026-07-19T19:30:00",
    "InfoReceivedPSDate": "2026-07-19T20:00:00",
    "latitude": 17.3297,
    "longitude": 76.8343,
    "BriefFacts": "LIVE API: Clash between two youth groups over agricultural land boundary dispute near district highway."
  },
  {
    "CaseMasterID": 1008,
    "CrimeNo": "FIR-2026-00108",
    "CaseNo": "SHM-2026-019",
    "CrimeRegisteredDate": "2026-07-23",
    "PolicePersonID": 561,
    "PoliceStationID": 130,
    "PoliceStationName": "Doddapet PS",
    "DistrictName": "Shivamogga",
    "CaseCategoryID": 1,
    "CaseCategoryName": "Cyber Crime",
    "GravityOffenceID": 2,
    "GravityOffenceName": "Non-Heinous",
    "CrimeMajorHeadID": 10,
    "CrimeMajorHeadName": "Identity Theft & Online Impersonation",
    "CrimeMinorHeadID": 101,
    "CaseStatusID": 1,
    "CaseStatusName": "Under Investigation",
    "CourtID": 11,
    "IncidentFromDate": "2026-07-22T10:00:00",
    "IncidentToDate": "2026-07-23T12:00:00",
    "InfoReceivedPSDate": "2026-07-23T14:00:00",
    "latitude": 13.9299,
    "longitude": 75.5681,
    "BriefFacts": "LIVE API: Fake government job portal scam luring local graduates to transfer processing fees."
  },
  {
    "CaseMasterID": 1009,
    "CrimeNo": "FIR-2026-00109",
    "CaseNo": "TUM-2026-056",
    "CrimeRegisteredDate": "2026-07-14",
    "PolicePersonID": 570,
    "PoliceStationID": 135,
    "PoliceStationName": "Town PS",
    "DistrictName": "Tumakuru",
    "CaseCategoryID": 6,
    "CaseCategoryName": "Highway Robbery",
    "GravityOffenceID": 1,
    "GravityOffenceName": "Heinous",
    "CrimeMajorHeadID": 16,
    "CrimeMajorHeadName": "Dacoity & Highway Heist",
    "CrimeMinorHeadID": 118,
    "CaseStatusID": 4,
    "CaseStatusName": "Disposed",
    "CourtID": 5,
    "IncidentFromDate": "2026-07-13T23:30:00",
    "IncidentToDate": "2026-07-14T01:15:00",
    "InfoReceivedPSDate": "2026-07-14T02:30:00",
    "latitude": 13.3392,
    "longitude": 77.1015,
    "BriefFacts": "LIVE API: Highway robbery targeting interstate electronics truck on NH-48. Vehicle recovered; suspects remanded."
  },
  {
    "CaseMasterID": 1010,
    "CrimeNo": "FIR-2026-00110",
    "CaseNo": "UDP-2026-029",
    "CrimeRegisteredDate": "2026-07-21",
    "PolicePersonID": 578,
    "PoliceStationID": 140,
    "PoliceStationName": "Udupi Town PS",
    "DistrictName": "Udupi",
    "CaseCategoryID": 2,
    "CaseCategoryName": "Theft & Housebreaking",
    "GravityOffenceID": 2,
    "GravityOffenceName": "Non-Heinous",
    "CrimeMajorHeadID": 11,
    "CrimeMajorHeadName": "Temple & Heritage Artifact Theft",
    "CrimeMinorHeadID": 106,
    "CaseStatusID": 1,
    "CaseStatusName": "Under Investigation",
    "CourtID": 14,
    "IncidentFromDate": "2026-07-20T22:00:00",
    "IncidentToDate": "2026-07-21T05:00:00",
    "InfoReceivedPSDate": "2026-07-21T06:45:00",
    "latitude": 13.3409,
    "longitude": 74.7421,
    "BriefFacts": "LIVE API: Theft of antique brass lamps and ritual silver ornaments from ancient shrine near coastal road."
  },
  {
    "CaseMasterID": 1011,
    "CrimeNo": "FIR-2026-00111",
    "CaseNo": "BAL-2026-067",
    "CrimeRegisteredDate": "2026-07-16",
    "PolicePersonID": 585,
    "PoliceStationID": 145,
    "PoliceStationName": "Brucepet PS",
    "DistrictName": "Ballari",
    "CaseCategoryID": 7,
    "CaseCategoryName": "Illegal Mining & Environmental",
    "GravityOffenceID": 1,
    "GravityOffenceName": "Heinous",
    "CrimeMajorHeadID": 22,
    "CrimeMajorHeadName": "Illegal Iron Ore Extraction",
    "CrimeMinorHeadID": 130,
    "CaseStatusID": 2,
    "CaseStatusName": "Chargesheeted",
    "CourtID": 7,
    "IncidentFromDate": "2026-07-10T00:00:00",
    "IncidentToDate": "2026-07-15T18:00:00",
    "InfoReceivedPSDate": "2026-07-16T09:00:00",
    "latitude": 15.1394,
    "longitude": 76.9214,
    "BriefFacts": "LIVE API: Seizure of 18 heavy excavators engaged in unauthorized mining inside protected forest corridor."
  },
  {
    "CaseMasterID": 1012,
    "CrimeNo": "FIR-2026-00112",
    "CaseNo": "DVG-2026-041",
    "CrimeRegisteredDate": "2026-07-22",
    "PolicePersonID": 592,
    "PoliceStationID": 150,
    "PoliceStationName": "Extension PS",
    "DistrictName": "Davanagere",
    "CaseCategoryID": 1,
    "CaseCategoryName": "Cyber Crime",
    "GravityOffenceID": 2,
    "GravityOffenceName": "Non-Heinous",
    "CrimeMajorHeadID": 10,
    "CrimeMajorHeadName": "Financial Cyber Fraud",
    "CrimeMinorHeadID": 103,
    "CaseStatusID": 1,
    "CaseStatusName": "Under Investigation",
    "CourtID": 10,
    "IncidentFromDate": "2026-07-21T14:30:00",
    "IncidentToDate": "2026-07-22T10:00:00",
    "InfoReceivedPSDate": "2026-07-22T11:15:00",
    "latitude": 14.4673,
    "longitude": 75.9241,
    "BriefFacts": "LIVE API: UPI Mandate scam deceiving textile traders into approving unauthorized debit requests."
  },
  {
    "CaseMasterID": 1013,
    "CrimeNo": "FIR-2026-00113",
    "CaseNo": "VJP-2026-083",
    "CrimeRegisteredDate": "2026-07-17",
    "PolicePersonID": 601,
    "PoliceStationID": 155,
    "PoliceStationName": "Gol Gumbaz PS",
    "DistrictName": "Vijayapura",
    "CaseCategoryID": 3,
    "CaseCategoryName": "Assault & Bodily Offences",
    "GravityOffenceID": 1,
    "GravityOffenceName": "Heinous",
    "CrimeMajorHeadID": 14,
    "CrimeMajorHeadName": "Homicide & Fatal Assault",
    "CrimeMinorHeadID": 108,
    "CaseStatusID": 2,
    "CaseStatusName": "Chargesheeted",
    "CourtID": 3,
    "IncidentFromDate": "2026-07-16T21:30:00",
    "IncidentToDate": "2026-07-16T22:45:00",
    "InfoReceivedPSDate": "2026-07-17T01:00:00",
    "latitude": 16.8302,
    "longitude": 75.7100,
    "BriefFacts": "LIVE API: Fatal assault following heated financial dispute over property inheritance in suburban colony."
  },
  {
    "CaseMasterID": 1014,
    "CrimeNo": "FIR-2026-00114",
    "CaseNo": "HSN-2026-025",
    "CrimeRegisteredDate": "2026-07-24",
    "PolicePersonID": 610,
    "PoliceStationID": 160,
    "PoliceStationName": "Hassan Town PS",
    "DistrictName": "Hassan",
    "CaseCategoryID": 2,
    "CaseCategoryName": "Theft & Housebreaking",
    "GravityOffenceID": 2,
    "GravityOffenceName": "Non-Heinous",
    "CrimeMajorHeadID": 11,
    "CrimeMajorHeadName": "Vehicle Theft",
    "CrimeMinorHeadID": 107,
    "CaseStatusID": 1,
    "CaseStatusName": "Under Investigation",
    "CourtID": 13,
    "IncidentFromDate": "2026-07-23T20:00:00",
    "IncidentToDate": "2026-07-24T06:00:00",
    "InfoReceivedPSDate": "2026-07-24T08:30:00",
    "latitude": 13.0072,
    "longitude": 76.1017,
    "BriefFacts": "LIVE API: Multiple commercial vehicle battery and fuel thefts reported from transport yard."
  }
]

# In-memory store fallback initialized with seed records
IN_MEMORY_INCIDENTS: List[Dict[str, Any]] = list(SEED_INCIDENTS)

SEED_HOTSPOTS = [
  {
    "HotspotClusterID": 101,
    "ClusterName": "DBSCAN Cluster #1 - Koramangala Cyber & Financial Fraud Zone",
    "DistrictName": "Bengaluru Urban",
    "latitude": 12.9450,
    "longitude": 77.6350,
    "radius_meters": 3500,
    "IncidentCount": 5,
    "RiskScore": 8.9,
    "DominantCategory": "Cyber Crime",
    "ClusterStatus": "Active Surveillance"
  },
  {
    "HotspotClusterID": 102,
    "ClusterName": "DBSCAN Cluster #2 - Devaraja Market Violence Corridor",
    "DistrictName": "Mysuru",
    "latitude": 12.3080,
    "longitude": 76.6520,
    "radius_meters": 2200,
    "IncidentCount": 4,
    "RiskScore": 7.8,
    "DominantCategory": "Assault & Bodily Offences",
    "ClusterStatus": "Patrol Escalated"
  },
  {
    "HotspotClusterID": 103,
    "ClusterName": "DBSCAN Cluster #3 - Pandeshwar Coastal NDPS Contraband Belt",
    "DistrictName": "Dakshina Kannada",
    "latitude": 12.8650,
    "longitude": 74.8480,
    "radius_meters": 2800,
    "IncidentCount": 3,
    "RiskScore": 9.4,
    "DominantCategory": "Narcotics & NDPS",
    "ClusterStatus": "High Severity Alert"
  },
  {
    "HotspotClusterID": 104,
    "ClusterName": "DBSCAN Cluster #4 - Ballari Illegal Mining Belt",
    "DistrictName": "Ballari",
    "latitude": 15.1420,
    "longitude": 76.9250,
    "radius_meters": 4000,
    "IncidentCount": 3,
    "RiskScore": 8.2,
    "DominantCategory": "Illegal Mining & Environmental",
    "ClusterStatus": "Active Investigation"
  }
]

IN_MEMORY_HOTSPOTS: List[Dict[str, Any]] = list(SEED_HOTSPOTS)

SEED_ANOMALIES = [
  {
    "AnomalyFlagID": 201,
    "PoliceStationID": 101,
    "PoliceStationName": "Koramangala PS",
    "DistrictName": "Bengaluru Urban",
    "CrimeMajorHeadName": "Financial Cyber Fraud & Phishing",
    "BaselineMonthlyAverage": 2.5,
    "CurrentPeriodCount": 9,
    "SpikePercentage": 260.0,
    "Severity": "CRITICAL",
    "latitude": 12.9360,
    "longitude": 77.6220,
    "AlertSummary": "Emerging Cyber Spike: Koramangala PS reports +260% spike in SIM-swap phishing attacks above 6-month historical baseline."
  },
  {
    "AnomalyFlagID": 202,
    "PoliceStationID": 105,
    "PoliceStationName": "Devaraja PS",
    "DistrictName": "Mysuru",
    "CrimeMajorHeadName": "Attempt to Murder & Armed Assault",
    "BaselineMonthlyAverage": 1.8,
    "CurrentPeriodCount": 6,
    "SpikePercentage": 233.3,
    "Severity": "HIGH",
    "latitude": 12.3060,
    "longitude": 76.6560,
    "AlertSummary": "Violent Incident Spike: Devaraja PS area exhibits +233% increase in market square altercations over 30-day baseline."
  },
  {
    "AnomalyFlagID": 203,
    "PoliceStationID": 145,
    "PoliceStationName": "Brucepet PS",
    "DistrictName": "Ballari",
    "CrimeMajorHeadName": "Illegal Iron Ore Extraction",
    "BaselineMonthlyAverage": 1.0,
    "CurrentPeriodCount": 4,
    "SpikePercentage": 300.0,
    "Severity": "CRITICAL",
    "latitude": 15.1400,
    "longitude": 76.9220,
    "AlertSummary": "Resource Extraction Spike: Brucepet PS area exhibits +300% surge in illegal iron ore mining activity in forest corridor."
  }
]

IN_MEMORY_ANOMALIES: List[Dict[str, Any]] = list(SEED_ANOMALIES)

SEED_ACCUSED = [
  {"AccusedMasterID": 101, "CaseMasterID": 1001, "AccusedName": "Ramesh Kumar", "AgeYear": 34, "GenderID": 1, "PersonID": "ACC-BLR-091"},
  {"AccusedMasterID": 102, "CaseMasterID": 1002, "AccusedName": "Ramesh Kumar", "AgeYear": 34, "GenderID": 1, "PersonID": "ACC-BLR-091"},
  {"AccusedMasterID": 103, "CaseMasterID": 1003, "AccusedName": "Suresh Gowda", "AgeYear": 29, "GenderID": 1, "PersonID": "ACC-MYS-042"},
  {"AccusedMasterID": 104, "CaseMasterID": 1006, "AccusedName": "Suresh Gowda", "AgeYear": 29, "GenderID": 1, "PersonID": "ACC-MYS-042"},
  {"AccusedMasterID": 105, "CaseMasterID": 1004, "AccusedName": "Vikram Reddy", "AgeYear": 41, "GenderID": 1, "PersonID": "ACC-DK-118"}
]

SEED_VICTIMS = [
  {"VictimMasterID": 201, "CaseMasterID": 1001, "VictimName": "Anand Rao", "AgeYear": 45, "GenderID": 1},
  {"VictimMasterID": 202, "CaseMasterID": 1002, "VictimName": "Priya Sharma", "AgeYear": 32, "GenderID": 2},
  {"VictimMasterID": 203, "CaseMasterID": 1003, "VictimName": "Mahadevappa", "AgeYear": 58, "GenderID": 1},
  {"VictimMasterID": 204, "CaseMasterID": 1006, "VictimName": "Silk Warehouse Corp", "AgeYear": 0, "GenderID": 3}
]

IN_MEMORY_ACCUSED: List[Dict[str, Any]] = list(SEED_ACCUSED)
IN_MEMORY_VICTIMS: List[Dict[str, Any]] = list(SEED_VICTIMS)

SEED_RESOLUTION = [
  {
    "MetricID": 301,
    "UnitID": 101,
    "PoliceStationID": 101,
    "PoliceStationName": "Koramangala PS",
    "DistrictName": "Bengaluru Urban",
    "PeriodMonth": "2026-07",
    "TotalCasesRegistered": 42,
    "ChargesheetedCount": 31,
    "ConvictedCount": 8,
    "DisposedCount": 33,
    "ResolutionRate": 78.5,
    "AverageDisposalDays": 18,
    "DischargeRate": 4.2,
    "FeedbackScore": 4.7
  },
  {
    "MetricID": 302,
    "UnitID": 105,
    "PoliceStationID": 105,
    "PoliceStationName": "Devaraja PS",
    "DistrictName": "Mysuru",
    "PeriodMonth": "2026-07",
    "TotalCasesRegistered": 28,
    "ChargesheetedCount": 22,
    "ConvictedCount": 6,
    "DisposedCount": 24,
    "ResolutionRate": 85.7,
    "AverageDisposalDays": 14,
    "DischargeRate": 3.5,
    "FeedbackScore": 4.9
  },
  {
    "MetricID": 303,
    "UnitID": 110,
    "PoliceStationID": 110,
    "PoliceStationName": "Pandeshwar PS",
    "DistrictName": "Dakshina Kannada",
    "PeriodMonth": "2026-07",
    "TotalCasesRegistered": 19,
    "ChargesheetedCount": 14,
    "ConvictedCount": 4,
    "DisposedCount": 15,
    "ResolutionRate": 78.9,
    "AverageDisposalDays": 21,
    "DischargeRate": 5.1,
    "FeedbackScore": 4.5
  },
  {
    "MetricID": 304,
    "UnitID": 115,
    "PoliceStationID": 115,
    "PoliceStationName": "Suburban PS",
    "DistrictName": "Dharwad",
    "PeriodMonth": "2026-07",
    "TotalCasesRegistered": 16,
    "ChargesheetedCount": 10,
    "ConvictedCount": 3,
    "DisposedCount": 11,
    "ResolutionRate": 68.7,
    "AverageDisposalDays": 32,
    "DischargeRate": 6.2,
    "FeedbackScore": 4.2
  }
]

IN_MEMORY_RESOLUTION: List[Dict[str, Any]] = list(SEED_RESOLUTION)

def get_catalyst_app(request: Request):
    try:
        import zcatalyst_sdk
        return zcatalyst_sdk.initialize(req=request, scope='admin')
    except Exception as e:
        try:
            import zcatalyst_sdk
            return zcatalyst_sdk.initialize(scope='admin')
        except Exception:
            return None

class IncidentCreate(BaseModel):
    CaseMasterID: Optional[int] = None
    CrimeNo: Optional[str] = None
    CaseNo: Optional[str] = None
    CrimeRegisteredDate: Optional[str] = None
    PolicePersonID: Optional[int] = None
    PoliceStationID: Optional[int] = None
    CaseCategoryID: Optional[int] = None
    GravityOffenceID: Optional[int] = None
    CrimeMajorHeadID: Optional[int] = None
    CrimeMinorHeadID: Optional[int] = None
    CaseStatusID: Optional[int] = None
    CourtID: Optional[int] = None
    IncidentFromDate: Optional[str] = None
    IncidentToDate: Optional[str] = None
    InfoReceivedPSDate: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    BriefFacts: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/incidents")
def get_incidents(catalyst_app: Any = Depends(get_catalyst_app)):
    data_store_rows = []
    if catalyst_app is not None:
        # Try Data Store table API
        try:
            table = catalyst_app.datastore().table("CaseMaster")
            paged_res = table.get_paged_rows(max_rows=200)
            data_store_rows = paged_res.get("data", [])
        except Exception:
            # Try ZCQL query
            try:
                zcql = catalyst_app.zcql()
                q_res = zcql.execute_query("SELECT * FROM CaseMaster LIMIT 200")
                data_store_rows = [r.get("CaseMaster") for r in q_res if isinstance(r, dict) and "CaseMaster" in r]
            except Exception:
                pass

    all_rows = data_store_rows + IN_MEMORY_INCIDENTS
    return {"status": "ok", "data": all_rows}

@app.get("/hotspots")
def get_hotspots(catalyst_app: Any = Depends(get_catalyst_app)):
    data_store_rows = []
    if catalyst_app is not None:
        try:
            table = catalyst_app.datastore().table("HotspotCluster")
            paged_res = table.get_paged_rows(max_rows=200)
            data_store_rows = paged_res.get("data", [])
        except Exception:
            try:
                zcql = catalyst_app.zcql()
                q_res = zcql.execute_query("SELECT * FROM HotspotCluster LIMIT 200")
                data_store_rows = [r.get("HotspotCluster") for r in q_res if isinstance(r, dict) and "HotspotCluster" in r]
            except Exception:
                pass

    all_rows = data_store_rows + IN_MEMORY_HOTSPOTS
    return {"status": "ok", "data": all_rows}

@app.get("/anomalies")
def get_anomalies(catalyst_app: Any = Depends(get_catalyst_app)):
    data_store_rows = []
    if catalyst_app is not None:
        try:
            table = catalyst_app.datastore().table("AnomalyFlag")
            paged_res = table.get_paged_rows(max_rows=200)
            data_store_rows = paged_res.get("data", [])
        except Exception:
            try:
                zcql = catalyst_app.zcql()
                q_res = zcql.execute_query("SELECT * FROM AnomalyFlag LIMIT 200")
                data_store_rows = [r.get("AnomalyFlag") for r in q_res if isinstance(r, dict) and "AnomalyFlag" in r]
            except Exception:
                pass

    all_rows = data_store_rows + IN_MEMORY_ANOMALIES
    return {"status": "ok", "data": all_rows}

@app.get("/resolution/metrics")
def get_resolution_metrics(catalyst_app: Any = Depends(get_catalyst_app)):
    data_store_rows = []
    if catalyst_app is not None:
        try:
            table = catalyst_app.datastore().table("StationResolutionMetric")
            paged_res = table.get_paged_rows(max_rows=200)
            data_store_rows = paged_res.get("data", [])
        except Exception:
            try:
                zcql = catalyst_app.zcql()
                q_res = zcql.execute_query("SELECT * FROM StationResolutionMetric LIMIT 200")
                data_store_rows = [r.get("StationResolutionMetric") for r in q_res if isinstance(r, dict) and "StationResolutionMetric" in r]
            except Exception:
                pass

    all_rows = data_store_rows + IN_MEMORY_RESOLUTION
    return {"status": "ok", "data": all_rows}

@app.get("/stations/{station_id}/resolution")
def get_station_resolution(station_id: int, catalyst_app: Any = Depends(get_catalyst_app)):
    all_metrics = IN_MEMORY_RESOLUTION
    match = next((m for m in all_metrics if m.get("PoliceStationID") == station_id or m.get("UnitID") == station_id), None)
    if match:
        return {"status": "ok", "data": match}
    return {
        "status": "ok",
        "data": {
            "MetricID": 399,
            "UnitID": station_id,
            "PoliceStationID": station_id,
            "PoliceStationName": f"Station #{station_id}",
            "DistrictName": "Karnataka Jurisdiction",
            "TotalCasesRegistered": 30,
            "ChargesheetedCount": 21,
            "DisposedCount": 23,
            "ResolutionRate": 76.6,
            "AverageDisposalDays": 20,
            "FeedbackScore": 4.5
        }
    }

@app.get("/network")
@app.get("/link-analysis")
def get_network_graph(proximity_km: float = 15.0, catalyst_app: Any = Depends(get_catalyst_app)):
    acc_rows = list(IN_MEMORY_ACCUSED) if IN_MEMORY_ACCUSED else list(SAMPLE_ACCUSED)
    case_rows = list(IN_MEMORY_INCIDENTS) if IN_MEMORY_INCIDENTS else list(SAMPLE_CASES)
    vic_rows = list(IN_MEMORY_VICTIMS) if IN_MEMORY_VICTIMS else list(SAMPLE_VICTIMS)
    
    units_dict = {}
    for c in case_rows:
        u_id = c.get("PoliceStationID")
        u_name = c.get("PoliceStationName", f"Station #{u_id}")
        if u_id and u_id not in units_dict:
            units_dict[u_id] = {"UnitID": u_id, "UnitName": u_name}
    unit_rows = list(units_dict.values()) if units_dict else list(SAMPLE_UNITS)

    result = perform_link_analysis(
        accused_records=acc_rows,
        case_records=case_rows,
        victim_records=vic_rows,
        unit_records=unit_rows,
        proximity_threshold_km=proximity_km
    )

    return {"status": "ok", "data": result.get("graph", {})}

@app.post("/incidents")
def create_incident(incident: IncidentCreate, catalyst_app: Any = Depends(get_catalyst_app)):
    payload = incident.dict(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="Empty incident payload provided")

    created_record = None
    if catalyst_app is not None:
        try:
            table = catalyst_app.datastore().table("CaseMaster")
            created_record = table.insert_row(payload)
        except Exception:
            try:
                zcql = catalyst_app.zcql()
                cols = ", ".join(payload.keys())
                vals = []
                for v in payload.values():
                    if isinstance(v, str):
                        safe_v = v.replace("'", "''")
                        vals.append(f"'{safe_v}'")
                    else:
                        vals.append(str(v))
                stmt = f"INSERT INTO CaseMaster ({cols}) VALUES ({', '.join(vals)})"
                zcql.execute_query(stmt)
                created_record = payload
            except Exception:
                pass

    if created_record is None:
        # Save to memory store and assign ROWID
        payload["ROWID"] = str(1000 + len(IN_MEMORY_INCIDENTS) + 1)
        IN_MEMORY_INCIDENTS.append(payload)
        created_record = payload
    else:
        IN_MEMORY_INCIDENTS.append(payload)

    return {"status": "ok", "data": created_record}

@app.get("/hotspots")
def get_hotspots(catalyst_app: Any = Depends(get_catalyst_app)):
    data_store_rows = []
    if catalyst_app is not None:
        try:
            table = catalyst_app.datastore().table("HotspotCluster")
            paged_res = table.get_paged_rows(max_rows=200)
            data_store_rows = paged_res.get("data", [])
        except Exception:
            try:
                zcql = catalyst_app.zcql()
                q_res = zcql.execute_query("SELECT * FROM HotspotCluster LIMIT 200")
                data_store_rows = [r.get("HotspotCluster") for r in q_res if isinstance(r, dict) and "HotspotCluster" in r]
            except Exception:
                pass

    all_rows = data_store_rows + IN_MEMORY_HOTSPOTS
    return {"status": "ok", "data": all_rows}

@app.get("/anomalies")
def get_anomalies(catalyst_app: Any = Depends(get_catalyst_app)):
    data_store_rows = []
    if catalyst_app is not None:
        try:
            table = catalyst_app.datastore().table("AnomalyFlag")
            paged_res = table.get_paged_rows(max_rows=200)
            data_store_rows = paged_res.get("data", [])
        except Exception:
            try:
                zcql = catalyst_app.zcql()
                q_res = zcql.execute_query("SELECT * FROM AnomalyFlag LIMIT 200")
                data_store_rows = [r.get("AnomalyFlag") for r in q_res if isinstance(r, dict) and "AnomalyFlag" in r]
            except Exception:
                pass

    all_rows = data_store_rows + IN_MEMORY_ANOMALIES
    return {"status": "ok", "data": all_rows}

@app.get("/incidents/{id}/accused")
def get_incident_accused(id: int, catalyst_app: Any = Depends(get_catalyst_app)):
    accused_rows = []
    if catalyst_app is not None:
        try:
            zcql = catalyst_app.zcql()
            q_stmt = f"SELECT * FROM Accused WHERE CaseMasterID = {id} LIMIT 200"
            q_res = zcql.execute_query(q_stmt)
            accused_rows = [r.get("Accused") for r in q_res if isinstance(r, dict) and "Accused" in r]
        except Exception:
            try:
                table = catalyst_app.datastore().table("Accused")
                paged_res = table.get_paged_rows(max_rows=200)
                all_rows = paged_res.get("data", [])
                accused_rows = [r for r in all_rows if str(r.get("CaseMasterID")) == str(id)]
            except Exception:
                pass

    mem_matches = [r for r in IN_MEMORY_ACCUSED if str(r.get("CaseMasterID")) == str(id)]
    combined = accused_rows + mem_matches
    return {"status": "ok", "data": combined}

@app.get("/incidents/{id}/victims")
def get_incident_victims(id: int, catalyst_app: Any = Depends(get_catalyst_app)):
    victim_rows = []
    if catalyst_app is not None:
        try:
            zcql = catalyst_app.zcql()
            q_stmt = f"SELECT * FROM Victim WHERE CaseMasterID = {id} LIMIT 200"
            q_res = zcql.execute_query(q_stmt)
            victim_rows = [r.get("Victim") for r in q_res if isinstance(r, dict) and "Victim" in r]
        except Exception:
            try:
                table = catalyst_app.datastore().table("Victim")
                paged_res = table.get_paged_rows(max_rows=200)
                all_rows = paged_res.get("data", [])
                victim_rows = [r for r in all_rows if str(r.get("CaseMasterID")) == str(id)]
            except Exception:
                pass

    mem_matches = [r for r in IN_MEMORY_VICTIMS if str(r.get("CaseMasterID")) == str(id)]
    combined = victim_rows + mem_matches
    return {"status": "ok", "data": combined}

@app.get("/stations/{id}/resolution")
def get_station_resolution(id: int, catalyst_app: Any = Depends(get_catalyst_app)):
    res_rows = []
    if catalyst_app is not None:
        try:
            zcql = catalyst_app.zcql()
            q_stmt = f"SELECT * FROM StationResolutionMetric WHERE UnitID = {id} LIMIT 200"
            q_res = zcql.execute_query(q_stmt)
            res_rows = [r.get("StationResolutionMetric") for r in q_res if isinstance(r, dict) and "StationResolutionMetric" in r]
        except Exception:
            try:
                table = catalyst_app.datastore().table("StationResolutionMetric")
                paged_res = table.get_paged_rows(max_rows=200)
                all_rows = paged_res.get("data", [])
                res_rows = [r for r in all_rows if str(r.get("UnitID")) == str(id)]
            except Exception:
                pass

    mem_matches = [r for r in IN_MEMORY_RESOLUTION if str(r.get("UnitID")) == str(id)]
    combined = res_rows + mem_matches
    return {"status": "ok", "data": combined}

@app.get("/auth/me")
def get_auth_me(request: Request, catalyst_app: Any = Depends(get_catalyst_app)):
    role = request.headers.get("X-Catalyst-Role") or request.query_params.get("role") or "Station"
    if role not in ["Station", "Command"]:
        role = "Station"
        
    user_info = {
        "authenticated": True,
        "user_id": "usr_catalyst_1001",
        "email": "officer@drishti.gov.in",
        "role": role,
        "org_id": "60079683126"
    }

    if catalyst_app is not None:
        try:
            user_detail = catalyst_app.user_management().get_user_details()
            if isinstance(user_detail, dict):
                user_info["email"] = user_detail.get("email_id", user_info["email"])
                user_info["user_id"] = user_detail.get("user_id", user_info["user_id"])
                user_info["role"] = user_detail.get("role_name", role)
        except Exception:
            pass

    return {"status": "ok", "user": user_info}

if __name__ == "__main__":
    port_env = os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT")
    port = int(port_env) if port_env else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
