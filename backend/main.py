import os
import sys
import csv
import json
import traceback
from typing import Optional, List, Dict, Any

print("Starting AppSail server...", flush=True)

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="Drishti Backend API - Catalyst Data Store Integration")

SEED_DIR = os.path.join(os.path.dirname(__file__), "seeds")

def load_seed_csv(relative_path: str) -> List[Dict[str, Any]]:
    full_path = os.path.normpath(os.path.join(SEED_DIR, relative_path))
    if not os.path.exists(full_path):
        alt_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "drishti_main", "seeds", relative_path))
        if os.path.exists(alt_path):
            full_path = alt_path
        else:
            return []
    records = []
    with open(full_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {}
            for k, v in row.items():
                if v is None or v == "":
                    parsed[k] = None
                    continue
                if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
                    parsed[k] = int(v)
                else:
                    try:
                        parsed[k] = float(v)
                    except ValueError:
                        parsed[k] = v
            records.append(parsed)
    return records

# Preload Gamma seed data into memory
SEED_HOTSPOTS = load_seed_csv("batch_e/HotspotCluster.csv")
SEED_ANOMALIES = load_seed_csv("batch_e/AnomalyFlag.csv")
SEED_CASES = load_seed_csv("batch_bc/CaseMaster.csv")
SEED_ACCUSED = load_seed_csv("batch_bc/Accused.csv")
SEED_VICTIMS = load_seed_csv("batch_bc/Victim.csv")
SEED_UNITS = load_seed_csv("batch_bc/Unit.csv")

CREATED_INCIDENTS: List[Dict[str, Any]] = []

def get_catalyst_app(request: Request):
    try:
        import zcatalyst_sdk
        return zcatalyst_sdk.initialize(req=request, scope='admin')
    except Exception:
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

@app.get("/admin/list_tables")
@app.post("/admin/list_tables")
def admin_list_tables(catalyst_app: Any = Depends(get_catalyst_app)):
    if catalyst_app is None:
        return {"status": "error", "message": "Catalyst SDK initialization returned None"}
    try:
        tables = catalyst_app.datastore().get_all_tables()
        tbl_info = [{"table_name": getattr(t, "table_name", str(t)), "table_id": getattr(t, "table_id", None)} for t in tables]
        return {"status": "ok", "count": len(tbl_info), "tables": tbl_info}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/admin/create_tables")
@app.post("/admin/create_tables")
def admin_create_tables(catalyst_app: Any = Depends(get_catalyst_app)):
    if catalyst_app is None:
        return {"status": "error", "message": "Catalyst SDK initialization returned None"}

    table_schemas = [
        # Batch A
        {"table_name": "State", "columns": [{"column_name": "StateID", "data_type": "INT"}, {"column_name": "StateName", "data_type": "VARCHAR"}, {"column_name": "NationalityID", "data_type": "INT"}, {"column_name": "Active", "data_type": "BOOLEAN"}]},
        {"table_name": "District", "columns": [{"column_name": "DistrictID", "data_type": "INT"}, {"column_name": "DistrictName", "data_type": "VARCHAR"}, {"column_name": "StateID", "data_type": "INT"}, {"column_name": "Active", "data_type": "BOOLEAN"}]},
        {"table_name": "UnitType", "columns": [{"column_name": "UnitTypeID", "data_type": "INT"}, {"column_name": "UnitTypeName", "data_type": "VARCHAR"}, {"column_name": "CityDistState", "data_type": "VARCHAR"}, {"column_name": "Hierarchy", "data_type": "INT"}, {"column_name": "Active", "data_type": "BOOLEAN"}]},
        {"table_name": "Rank", "columns": [{"column_name": "RankID", "data_type": "INT"}, {"column_name": "RankName", "data_type": "VARCHAR"}, {"column_name": "Hierarchy", "data_type": "INT"}, {"column_name": "Active", "data_type": "BOOLEAN"}]},
        {"table_name": "Designation", "columns": [{"column_name": "DesignationID", "data_type": "INT"}, {"column_name": "DesignationName", "data_type": "VARCHAR"}, {"column_name": "Active", "data_type": "BOOLEAN"}, {"column_name": "SortOrder", "data_type": "INT"}]},
        {"table_name": "CaseCategory", "columns": [{"column_name": "CaseCategoryID", "data_type": "INT"}, {"column_name": "LookupValue", "data_type": "VARCHAR"}]},
        {"table_name": "GravityOffence", "columns": [{"column_name": "GravityOffenceID", "data_type": "INT"}, {"column_name": "LookupValue", "data_type": "VARCHAR"}]},
        {"table_name": "CrimeHead", "columns": [{"column_name": "CrimeHeadID", "data_type": "INT"}, {"column_name": "CrimeGroupName", "data_type": "VARCHAR"}, {"column_name": "Active", "data_type": "BOOLEAN"}]},
        {"table_name": "CrimeSubHead", "columns": [{"column_name": "CrimeSubHeadID", "data_type": "INT"}, {"column_name": "CrimeHeadID", "data_type": "INT"}, {"column_name": "CrimeHeadName", "data_type": "VARCHAR"}, {"column_name": "SeqID", "data_type": "INT"}]},
        {"table_name": "CaseStatusMaster", "columns": [{"column_name": "CaseStatusID", "data_type": "INT"}, {"column_name": "CaseStatusName", "data_type": "VARCHAR"}]},
        {"table_name": "CasteMaster", "columns": [{"column_name": "caste_master_id", "data_type": "INT"}, {"column_name": "caste_master_name", "data_type": "VARCHAR"}]},
        {"table_name": "ReligionMaster", "columns": [{"column_name": "ReligionID", "data_type": "INT"}, {"column_name": "ReligionName", "data_type": "VARCHAR"}]},
        {"table_name": "OccupationMaster", "columns": [{"column_name": "OccupationID", "data_type": "INT"}, {"column_name": "OccupationName", "data_type": "VARCHAR"}]},
        {"table_name": "Act", "columns": [{"column_name": "ActCode", "data_type": "VARCHAR"}, {"column_name": "ActDescription", "data_type": "VARCHAR"}, {"column_name": "ShortName", "data_type": "VARCHAR"}, {"column_name": "Active", "data_type": "BOOLEAN"}]},
        {"table_name": "Section", "columns": [{"column_name": "ActCode", "data_type": "VARCHAR"}, {"column_name": "SectionCode", "data_type": "VARCHAR"}, {"column_name": "SectionDescription", "data_type": "VARCHAR"}, {"column_name": "Active", "data_type": "BOOLEAN"}]},
        # Batch B
        {"table_name": "Unit", "columns": [{"column_name": "UnitID", "data_type": "INT"}, {"column_name": "UnitName", "data_type": "VARCHAR"}, {"column_name": "TypeID", "data_type": "INT"}, {"column_name": "ParentUnit", "data_type": "INT"}, {"column_name": "NationalityID", "data_type": "INT"}, {"column_name": "StateID", "data_type": "INT"}, {"column_name": "DistrictID", "data_type": "INT"}, {"column_name": "Active", "data_type": "BOOLEAN"}]},
        {"table_name": "Employee", "columns": [{"column_name": "EmployeeID", "data_type": "INT"}, {"column_name": "DistrictID", "data_type": "INT"}, {"column_name": "UnitID", "data_type": "INT"}, {"column_name": "RankID", "data_type": "INT"}, {"column_name": "DesignationID", "data_type": "INT"}, {"column_name": "KGID", "data_type": "VARCHAR"}, {"column_name": "FirstName", "data_type": "VARCHAR"}, {"column_name": "EmployeeDOB", "data_type": "DATE"}, {"column_name": "GenderID", "data_type": "INT"}, {"column_name": "BloodGroupID", "data_type": "INT"}, {"column_name": "PhysicallyChallenged", "data_type": "BOOLEAN"}, {"column_name": "AppointmentDate", "data_type": "DATE"}]},
        {"table_name": "Court", "columns": [{"column_name": "CourtID", "data_type": "INT"}, {"column_name": "CourtName", "data_type": "VARCHAR"}, {"column_name": "DistrictID", "data_type": "INT"}, {"column_name": "StateID", "data_type": "INT"}, {"column_name": "Active", "data_type": "BOOLEAN"}]},
        # Batch C
        {"table_name": "CaseMaster", "columns": [{"column_name": "CaseMasterID", "data_type": "INT"}, {"column_name": "CrimeNo", "data_type": "VARCHAR"}, {"column_name": "CaseNo", "data_type": "VARCHAR"}, {"column_name": "CrimeRegisteredDate", "data_type": "DATE"}, {"column_name": "PolicePersonID", "data_type": "INT"}, {"column_name": "PoliceStationID", "data_type": "INT"}, {"column_name": "CaseCategoryID", "data_type": "INT"}, {"column_name": "GravityOffenceID", "data_type": "INT"}, {"column_name": "CrimeMajorHeadID", "data_type": "INT"}, {"column_name": "CrimeMinorHeadID", "data_type": "INT"}, {"column_name": "CaseStatusID", "data_type": "INT"}, {"column_name": "CourtID", "data_type": "INT"}, {"column_name": "IncidentFromDate", "data_type": "DATETIME"}, {"column_name": "IncidentToDate", "data_type": "DATETIME"}, {"column_name": "InfoReceivedPSDate", "data_type": "DATETIME"}, {"column_name": "latitude", "data_type": "DOUBLE"}, {"column_name": "longitude", "data_type": "DOUBLE"}, {"column_name": "BriefFacts", "data_type": "TEXT"}]},
        {"table_name": "ComplainantDetails", "columns": [{"column_name": "ComplainantID", "data_type": "INT"}, {"column_name": "CaseMasterID", "data_type": "INT"}, {"column_name": "ComplainantName", "data_type": "VARCHAR"}, {"column_name": "AgeYear", "data_type": "INT"}, {"column_name": "OccupationID", "data_type": "INT"}, {"column_name": "ReligionID", "data_type": "INT"}, {"column_name": "CasteID", "data_type": "INT"}, {"column_name": "GenderID", "data_type": "INT"}]},
        {"table_name": "Victim", "columns": [{"column_name": "VictimMasterID", "data_type": "INT"}, {"column_name": "CaseMasterID", "data_type": "INT"}, {"column_name": "VictimName", "data_type": "VARCHAR"}, {"column_name": "AgeYear", "data_type": "INT"}, {"column_name": "GenderID", "data_type": "INT"}, {"column_name": "VictimPolice", "data_type": "BOOLEAN"}]},
        {"table_name": "Accused", "columns": [{"column_name": "AccusedMasterID", "data_type": "INT"}, {"column_name": "CaseMasterID", "data_type": "INT"}, {"column_name": "AccusedName", "data_type": "VARCHAR"}, {"column_name": "AgeYear", "data_type": "INT"}, {"column_name": "GenderID", "data_type": "INT"}, {"column_name": "PersonID", "data_type": "VARCHAR"}]},
        {"table_name": "ActSectionAssociation", "columns": [{"column_name": "CaseMasterID", "data_type": "INT"}, {"column_name": "ActID", "data_type": "INT"}, {"column_name": "SectionID", "data_type": "INT"}, {"column_name": "ActOrderID", "data_type": "INT"}, {"column_name": "SectionOrderID", "data_type": "INT"}]},
        {"table_name": "CrimeHeadActSection", "columns": [{"column_name": "CrimeHeadID", "data_type": "INT"}, {"column_name": "ActCode", "data_type": "VARCHAR"}, {"column_name": "SectionCode", "data_type": "VARCHAR"}]},
        # Batch E
        {"table_name": "HotspotCluster", "columns": [{"column_name": "ClusterID", "data_type": "INT"}, {"column_name": "DistrictID", "data_type": "INT"}, {"column_name": "UnitID", "data_type": "INT"}, {"column_name": "CrimeMajorHeadID", "data_type": "INT"}, {"column_name": "CentroidLat", "data_type": "DOUBLE"}, {"column_name": "CentroidLng", "data_type": "DOUBLE"}, {"column_name": "IncidentCount", "data_type": "INT"}, {"column_name": "TimeWindowStart", "data_type": "DATE"}, {"column_name": "TimeWindowEnd", "data_type": "DATE"}, {"column_name": "ComputedAt", "data_type": "DATETIME"}]},
        {"table_name": "AnomalyFlag", "columns": [{"column_name": "AnomalyID", "data_type": "INT"}, {"column_name": "DistrictID", "data_type": "INT"}, {"column_name": "UnitID", "data_type": "INT"}, {"column_name": "CrimeMajorHeadID", "data_type": "INT"}, {"column_name": "ObservedCount", "data_type": "INT"}, {"column_name": "ExpectedCount", "data_type": "DOUBLE"}, {"column_name": "AnomalyScore", "data_type": "DOUBLE"}, {"column_name": "FlagReason", "data_type": "VARCHAR"}, {"column_name": "WindowStart", "data_type": "DATE"}, {"column_name": "WindowEnd", "data_type": "DATE"}]},
        {"table_name": "StationResolutionMetric", "columns": [{"column_name": "MetricID", "data_type": "INT"}, {"column_name": "UnitID", "data_type": "INT"}, {"column_name": "PeriodStart", "data_type": "DATE"}, {"column_name": "PeriodEnd", "data_type": "DATE"}, {"column_name": "TotalCases", "data_type": "INT"}, {"column_name": "Chargesheeted", "data_type": "INT"}, {"column_name": "FalseCases", "data_type": "INT"}, {"column_name": "Undetected", "data_type": "INT"}, {"column_name": "AvgDaysToResolution", "data_type": "DOUBLE"}, {"column_name": "ResolutionRatePct", "data_type": "DOUBLE"}]},
        {"table_name": "RiskScore", "columns": [{"column_name": "RiskScoreID", "data_type": "INT"}, {"column_name": "DistrictID", "data_type": "INT"}, {"column_name": "UnitID", "data_type": "INT"}, {"column_name": "CrimeMajorHeadID", "data_type": "INT"}, {"column_name": "RiskLevel", "data_type": "VARCHAR"}, {"column_name": "RiskValue", "data_type": "DOUBLE"}, {"column_name": "ModelVersion", "data_type": "VARCHAR"}, {"column_name": "ComputedAt", "data_type": "DATETIME"}]}
    ]

    results = []
    requester = catalyst_app.datastore()._requester

    for schema in table_schemas:
        tbl_name = schema["table_name"]
        for col in schema["columns"]:
            if col.get("data_type") == "VARCHAR" and "max_length" not in col:
                col["max_length"] = 255
        try:
            resp = requester.request(
                method="POST",
                path="/table",
                json=schema
            )
            results.append({"table": tbl_name, "status": "created", "response": resp.response_json})
        except Exception as e:
            results.append({"table": tbl_name, "status": "failed", "error": str(e)})

    return {"status": "ok", "results": results}

@app.get("/admin/query_datastore")
@app.post("/admin/query_datastore")
def admin_query_datastore(catalyst_app: Any = Depends(get_catalyst_app)):
    if catalyst_app is None:
        return {"status": "error", "message": "Catalyst SDK initialization returned None"}

    results = {}
    tables = ["CaseMaster", "HotspotCluster", "AnomalyFlag"]

    for tbl in tables:
        err_msg = None
        rows = []
        try:
            table = catalyst_app.datastore().table(tbl)
            paged = table.get_paged_rows(max_rows=10)
            rows = paged.get("data", [])
        except Exception as e:
            err_msg = f"Datastore Query Error: {type(e).__name__} - {str(e)}"

        results[tbl] = {
            "count": len(rows),
            "raw_query_output": rows,
            "error": err_msg
        }

    return {"status": "ok", "data": results}

@app.get("/admin/bulk_load_datastore")
@app.post("/admin/bulk_load_datastore")
def admin_bulk_load_datastore(catalyst_app: Any = Depends(get_catalyst_app)):
    if catalyst_app is None:
        return {"status": "error", "message": "Catalyst SDK not initialized"}

    logs = []
    batch_size = 50

    for tbl_name, data in [("HotspotCluster", SEED_HOTSPOTS), ("AnomalyFlag", SEED_ANOMALIES), ("CaseMaster", SEED_CASES), ("Accused", SEED_ACCUSED), ("Victim", SEED_VICTIMS)]:
        try:
            table = catalyst_app.datastore().table(tbl_name)
            inserted = 0
            for i in range(0, len(data), batch_size):
                chunk = data[i:i + batch_size]
                table.insert_rows(chunk)
                inserted += len(chunk)
            logs.append(f"Successfully inserted {inserted} records into {tbl_name}")
        except Exception as e:
            tb = traceback.format_exc()
            logs.append(f"Failed to insert into {tbl_name}: {str(e)}\nTraceback:\n{tb}")

    return {"status": "ok", "logs": logs}

@app.get("/incidents")
def get_incidents(catalyst_app: Any = Depends(get_catalyst_app)):
    data_store_rows = []
    if catalyst_app is not None:
        try:
            table = catalyst_app.datastore().table("CaseMaster")
            paged_res = table.get_paged_rows(max_rows=200)
            data_store_rows = paged_res.get("data", [])
        except Exception:
            try:
                zcql = catalyst_app.zcql()
                q_res = zcql.execute_query("SELECT * FROM CaseMaster LIMIT 200")
                data_store_rows = [r.get("CaseMaster") for r in q_res if isinstance(r, dict) and "CaseMaster" in r]
            except Exception:
                pass

    if not data_store_rows:
        data_store_rows = SEED_CASES[:200]

    all_rows = CREATED_INCIDENTS + data_store_rows
    return {"status": "ok", "data": all_rows}

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
        if "CaseMasterID" not in payload or payload["CaseMasterID"] is None:
            payload["CaseMasterID"] = 10000 + len(CREATED_INCIDENTS) + 1
        payload["ROWID"] = str(payload["CaseMasterID"])
        CREATED_INCIDENTS.append(payload)
        created_record = payload
    else:
        CREATED_INCIDENTS.append(payload)

    return {"status": "ok", "data": created_record}

@app.get("/hotspots")
def get_hotspots(catalyst_app: Any = Depends(get_catalyst_app)):
    data_store_rows = []
    if catalyst_app is not None:
        try:
            table = catalyst_app.datastore().table("HotspotCluster")
            paged_res = table.get_paged_rows(max_rows=300)
            data_store_rows = paged_res.get("data", [])
        except Exception:
            try:
                zcql = catalyst_app.zcql()
                q_res = zcql.execute_query("SELECT * FROM HotspotCluster LIMIT 300")
                data_store_rows = [r.get("HotspotCluster") for r in q_res if isinstance(r, dict) and "HotspotCluster" in r]
            except Exception:
                pass

    if not data_store_rows:
        data_store_rows = SEED_HOTSPOTS

    return {"status": "ok", "data": data_store_rows}

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

    if not data_store_rows:
        data_store_rows = SEED_ANOMALIES

    return {"status": "ok", "data": data_store_rows}

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

    if not accused_rows:
        accused_rows = [r for r in SEED_ACCUSED if str(r.get("CaseMasterID")) == str(id)]

    return {"status": "ok", "data": accused_rows}

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

    if not victim_rows:
        victim_rows = [r for r in SEED_VICTIMS if str(r.get("CaseMasterID")) == str(id)]

    return {"status": "ok", "data": victim_rows}

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

    if not res_rows:
        station_cases = [c for c in SEED_CASES if str(c.get("PoliceStationID")) == str(id)]
        total = len(station_cases)
        resolved = len([c for c in station_cases if c.get("CaseStatusID") in [2, 3]])
        pending = total - resolved
        conviction_rate = round((resolved / total * 100), 2) if total > 0 else 0.0
        res_rows = [{
            "UnitID": id,
            "TotalCases": total,
            "ResolvedCases": resolved,
            "PendingCases": pending,
            "ConvictionRate": conviction_rate,
            "AvgDisposalDays": 45.5
        }]

    return {"status": "ok", "data": res_rows}

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
