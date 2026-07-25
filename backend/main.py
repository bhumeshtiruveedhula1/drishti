import os
import sys
import csv
import json
import traceback
from typing import Optional, List, Dict, Any
from datetime import datetime

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
                if v.lower() == "true":
                    parsed[k] = True
                elif v.lower() == "false":
                    parsed[k] = False
                elif v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
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
SEED_CHARGESHEETS = load_seed_csv("batch_d/ChargesheetDetails.csv")

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

def fetch_all_datastore_rows(table: Any, max_rows: int = 200) -> List[Dict[str, Any]]:
    all_rows = []
    next_token = None
    while True:
        try:
            if next_token:
                paged = table.get_paged_rows(max_rows=max_rows, next_token=next_token)
            else:
                paged = table.get_paged_rows(max_rows=max_rows)
        except Exception:
            try:
                paged = table.get_paged_rows(max_rows=max_rows)
            except Exception:
                break
        rows = paged.get("data", [])
        if not rows:
            break
        all_rows.extend(rows)
        if not paged.get("has_more_rows", False):
            break
        next_token = paged.get("next_token")
        if not next_token:
            break
    return all_rows

@app.get("/admin/query_datastore")
@app.post("/admin/query_datastore")
def admin_query_datastore(catalyst_app: Any = Depends(get_catalyst_app)):
    if catalyst_app is None:
        return {"status": "error", "message": "Catalyst SDK initialization returned None"}

    results = {}
    tables = ["CaseMaster", "HotspotCluster", "AnomalyFlag", "Victim", "ChargesheetDetails"]

    for tbl in tables:
        err_msg = None
        rows = []
        total_count = 0
        table_cols = []
        try:
            table = catalyst_app.datastore().table(tbl)
            table_cols = [f"{k}:{v}" for k, v in table.__dict__.items()]
            paged = table.get_paged_rows(max_rows=10)
            rows = paged.get("data", [])
            try:
                all_p = fetch_all_datastore_rows(table, max_rows=200)
                total_count = len(all_p) if all_p else len(rows)
            except Exception:
                total_count = len(rows)
        except Exception as e:
            err_msg = f"Datastore Query Error: {type(e).__name__} - {str(e)}"

        results[tbl] = {
            "total_count": total_count,
            "sample_count": len(rows),
            "columns": table_cols,
            "raw_query_output": rows,
            "error": err_msg
        }

    return {"status": "ok", "data": results}

@app.get("/admin/verify_chargesheets")
def admin_verify_chargesheets(catalyst_app: Any = Depends(get_catalyst_app)):
    if catalyst_app is None:
        return {"status": "error", "message": "Catalyst SDK not initialized"}

    try:
        table = catalyst_app.datastore().table("ChargesheetDetails")
        all_rows = fetch_all_datastore_rows(table, max_rows=200)

        total_count = len(all_rows)
        duplicates_removed = 0

        if total_count > 3997:
            gamma_csids = {int(r["CSID"]): int(r["CaseMasterID"]) for r in SEED_CHARGESHEETS if "CSID" in r and "CaseMasterID" in r}
            seen_csids = set()
            rowids_to_delete = []

            for r in all_rows:
                csid = int(r.get("CSID", 0))
                cmid = int(r.get("CaseMasterID", 0))
                row_id = r.get("ROWID")

                if csid not in gamma_csids or gamma_csids[csid] != cmid or csid in seen_csids:
                    if row_id:
                        rowids_to_delete.append(row_id)
                else:
                    seen_csids.add(csid)

            if rowids_to_delete:
                for i in range(0, len(rowids_to_delete), 100):
                    batch = rowids_to_delete[i:i+100]
                    table.delete_rows(batch)
                duplicates_removed = len(rowids_to_delete)
                total_count = total_count - duplicates_removed

        return {
            "status": "ok",
            "exact_row_count": total_count,
            "duplicates_removed": duplicates_removed,
            "sample_rows": all_rows[:5] if all_rows else []
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.get("/admin/bulk_load_datastore")
@app.post("/admin/bulk_load_datastore")
def admin_bulk_load_datastore(catalyst_app: Any = Depends(get_catalyst_app)):
    if catalyst_app is None:
        return {"status": "error", "message": "Catalyst SDK not initialized"}

    logs = []
    batch_size = 50

    for tbl_name, data in [("HotspotCluster", SEED_HOTSPOTS), ("AnomalyFlag", SEED_ANOMALIES), ("CaseMaster", SEED_CASES), ("Accused", SEED_ACCUSED), ("Victim", SEED_VICTIMS), ("ChargesheetDetails", SEED_CHARGESHEETS)]:
        try:
            table = catalyst_app.datastore().table(tbl_name)
            if tbl_name == "ChargesheetDetails":
                cleared = 0
                try:
                    while True:
                        p_data = table.get_paged_rows(max_rows=100).get("data", [])
                        if not p_data:
                            break
                        row_ids = [r["ROWID"] for r in p_data if "ROWID" in r]
                        if not row_ids:
                            break
                        table.delete_rows(row_ids)
                        cleared += len(row_ids)
                    logs.append(f"Cleared {cleared} existing rows from ChargesheetDetails")
                except Exception as ex_c:
                    logs.append(f"Clear ChargesheetDetails note: {ex_c}")

                clean_data = []
                for r in data:
                    clean_data.append({
                        "CSID": int(r["CSID"]),
                        "CaseMasterID": int(r["CaseMasterID"]),
                        "csdate": str(r["csdate"]),
                        "cstype": str(r["cstype"])
                    })

                inserted = 0
                for i in range(0, len(clean_data), batch_size):
                    chunk = clean_data[i:i + batch_size]
                    table.insert_rows(chunk)
                    inserted += len(chunk)
                logs.append(f"Successfully loaded {inserted} Gamma ChargesheetDetails records into Data Store")
            else:
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

def compute_station_resolution_metrics(cs_list: List[Dict[str, Any]], cases_list: List[Dict[str, Any]], units_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cs_dict = {}
    for c in cs_list:
        if isinstance(c, dict):
            cid = c.get("CaseMasterID")
            if cid is not None:
                try:
                    cs_dict[int(cid)] = c
                except (ValueError, TypeError):
                    pass

    unit_names = {}
    for u in units_list:
        if isinstance(u, dict):
            uid = u.get("UnitID")
            if uid is not None:
                try:
                    unit_names[int(uid)] = u.get("UnitName")
                except (ValueError, TypeError):
                    pass

    station_metrics: Dict[int, Dict[str, Any]] = {}

    for c in cases_list:
        if not isinstance(c, dict):
            continue
        case_id = c.get("CaseMasterID")
        if case_id is None:
            continue
        try:
            case_id = int(case_id)
        except (ValueError, TypeError):
            continue
        unit_id = c.get("PoliceStationID") or c.get("UnitID") or 1
        try:
            unit_id = int(unit_id)
        except (ValueError, TypeError):
            unit_id = 1

        if unit_id not in station_metrics:
            station_metrics[unit_id] = {
                "MetricID": unit_id,
                "UnitID": unit_id,
                "UnitName": unit_names.get(unit_id, f"Station #{unit_id}"),
                "PeriodStart": "2025-01-01",
                "PeriodEnd": "2026-01-31",
                "TotalCases": 0,
                "Chargesheeted": 0,
                "FalseCases": 0,
                "Undetected": 0,
                "TotalDisposalDays": 0.0,
                "DisposalCount": 0
            }

        st = station_metrics[unit_id]
        st["TotalCases"] += 1

        cs = cs_dict.get(case_id)
        if cs:
            cstype = str(cs.get("cstype", "")).strip().upper()
            if cstype in ("A", "CHARGESHEET", "CHARGESHEETED"):
                st["Chargesheeted"] += 1
            elif cstype in ("B", "FALSE CASE"):
                st["FalseCases"] += 1
            elif cstype in ("C", "UNDETECTED"):
                st["Undetected"] += 1

            reg_str = str(c.get("CrimeRegisteredDate", ""))
            cs_str = str(cs.get("csdate", ""))
            if reg_str and cs_str:
                try:
                    reg_dt = datetime.strptime(reg_str.strip().split()[0], "%Y-%m-%d")
                    cs_dt = datetime.strptime(cs_str.strip().split()[0], "%Y-%m-%d")
                    days = (cs_dt - reg_dt).days
                    if days >= 0:
                        st["TotalDisposalDays"] += days
                        st["DisposalCount"] += 1
                except Exception:
                    pass

    result = []
    for u_id, st in sorted(station_metrics.items()):
        total = st["TotalCases"]
        cs_cnt = st["Chargesheeted"]
        fc_cnt = st["FalseCases"]
        disp_cnt = st["DisposalCount"]
        res_pct = round(((cs_cnt + fc_cnt) / total * 100), 2) if total > 0 else 0.0
        avg_days = round(st["TotalDisposalDays"] / disp_cnt, 1) if disp_cnt > 0 else 30.0

        result.append({
            "MetricID": st["MetricID"],
            "UnitID": st["UnitID"],
            "UnitName": st["UnitName"],
            "PeriodStart": st["PeriodStart"],
            "PeriodEnd": st["PeriodEnd"],
            "TotalCases": total,
            "Chargesheeted": cs_cnt,
            "FalseCases": fc_cnt,
            "Undetected": st["Undetected"],
            "AvgDaysToResolution": avg_days,
            "ResolutionRatePct": res_pct
        })

    return result

@app.get("/stations/resolution")
def get_all_stations_resolution(catalyst_app: Any = Depends(get_catalyst_app)):
    cs_rows = []
    if catalyst_app is not None:
        try:
            zcql = catalyst_app.zcql()
            q_res = zcql.execute_query("SELECT * FROM ChargesheetDetails LIMIT 5000")
            cs_rows = [r.get("ChargesheetDetails") for r in q_res if isinstance(r, dict) and "ChargesheetDetails" in r]
        except Exception:
            try:
                t_cs = catalyst_app.datastore().table("ChargesheetDetails")
                cs_rows = t_cs.get_paged_rows(max_rows=5000).get("data", [])
            except Exception:
                pass

    if not cs_rows:
        cs_rows = SEED_CHARGESHEETS

    metrics = compute_station_resolution_metrics(cs_rows, SEED_CASES, SEED_UNITS)
    return {"status": "ok", "data": metrics}

@app.get("/stations/{id}/resolution")
def get_station_resolution(id: int, catalyst_app: Any = Depends(get_catalyst_app)):
    cs_rows = []
    if catalyst_app is not None:
        try:
            zcql = catalyst_app.zcql()
            q_res = zcql.execute_query("SELECT * FROM ChargesheetDetails LIMIT 5000")
            cs_rows = [r.get("ChargesheetDetails") for r in q_res if isinstance(r, dict) and "ChargesheetDetails" in r]
        except Exception:
            try:
                t_cs = catalyst_app.datastore().table("ChargesheetDetails")
                cs_rows = t_cs.get_paged_rows(max_rows=5000).get("data", [])
            except Exception:
                pass

    if not cs_rows:
        cs_rows = SEED_CHARGESHEETS

    metrics = compute_station_resolution_metrics(cs_rows, SEED_CASES, SEED_UNITS)
    st_metric = [m for m in metrics if m["UnitID"] == id]
    if not st_metric:
        st_metric = [{
            "MetricID": id,
            "UnitID": id,
            "UnitName": next((u.get("UnitName") for u in SEED_UNITS if str(u.get("UnitID")) == str(id)), f"Station #{id}"),
            "PeriodStart": "2025-01-01",
            "PeriodEnd": "2026-01-31",
            "TotalCases": 0,
            "Chargesheeted": 0,
            "FalseCases": 0,
            "Undetected": 0,
            "AvgDaysToResolution": 30.0,
            "ResolutionRatePct": 0.0
        }]

    return {"status": "ok", "data": st_metric}

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

def load_network_graph() -> Dict[str, Any]:
    path = os.path.join(SEED_DIR, "batch_e", "network_graph.json")
    if not os.path.exists(path):
        alt_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "drishti_main", "seeds", "batch_e", "network_graph.json"))
        if os.path.exists(alt_path):
            path = alt_path
        else:
            return {"status": "error", "message": "network_graph.json artifact not found"}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"status": "ok", "data": data}

@app.get("/network")
@app.get("/link-analysis")
def get_network_graph():
    res = load_network_graph()
    if res.get("status") == "error":
        raise HTTPException(status_code=404, detail=res["message"])
    return res

if __name__ == "__main__":
    port_env = os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT")
    port = int(port_env) if port_env else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
