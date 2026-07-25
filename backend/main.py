import os
import sys
import csv
import json
import traceback
from typing import Optional, List, Dict, Any
from datetime import datetime

print("Starting AppSail server...", flush=True)

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, Response
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Drishti Backend API - Catalyst Data Store Integration")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
SEED_OCCUPATIONS = load_seed_csv("batch_a/OccupationMaster.csv")
SEED_COMPLAINANTS = load_seed_csv("batch_bc/ComplainantDetails.csv")
SEED_CRIME_HEADS = load_seed_csv("batch_a/CrimeHead.csv")
SEED_DISTRICTS = load_seed_csv("batch_a/District.csv")
SEED_METHOD_TAGS = load_seed_csv("batch_e/CaseMethodTag.csv")

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
    tables = ["CaseMaster", "HotspotCluster", "AnomalyFlag", "Victim", "ChargesheetDetails", "RiskScore"]

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
        all_rows = []
        try:
            zcql = catalyst_app.zcql()
            offset = 0
            while True:
                q_stmt = f"SELECT ChargesheetDetails.CSID, ChargesheetDetails.CaseMasterID, ChargesheetDetails.ROWID FROM ChargesheetDetails LIMIT 200 OFFSET {offset}"
                q_res = zcql.execute_query(q_stmt)
                batch = [r.get("ChargesheetDetails") for r in q_res if isinstance(r, dict) and "ChargesheetDetails" in r]
                if not batch:
                    break
                all_rows.extend(batch)
                if len(batch) < 200:
                    break
                offset += len(batch)
        except Exception:
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

@app.get("/admin/clear_and_reload_accused")
@app.post("/admin/clear_and_reload_accused")
def admin_clear_and_reload_accused(catalyst_app: Any = Depends(get_catalyst_app)):
    if catalyst_app is None:
        return {"status": "error", "message": "Catalyst SDK not initialized"}

    try:
        table = catalyst_app.datastore().table("Accused")
        cleared = 0
        while True:
            p_data = table.get_paged_rows(max_rows=100).get("data", [])
            if not p_data:
                break
            row_ids = [r["ROWID"] for r in p_data if "ROWID" in r]
            if not row_ids:
                break
            table.delete_rows(row_ids)
            cleared += len(row_ids)

        clean_accused = []
        for r in SEED_ACCUSED:
            clean_accused.append({
                "AccusedMasterID": int(r["AccusedMasterID"]),
                "CaseMasterID": int(r["CaseMasterID"]),
                "AccusedName": str(r["AccusedName"]),
                "AgeYear": int(r["AgeYear"]) if r.get("AgeYear") is not None else 0,
                "GenderID": int(r["GenderID"]) if r.get("GenderID") is not None else 1,
                "PersonID": str(r.get("PersonID", ""))
            })

        batch_size = 50
        inserted = 0
        for i in range(0, len(clean_accused), batch_size):
            chunk = clean_accused[i:i + batch_size]
            table.insert_rows(chunk)
            inserted += len(chunk)

        return {
            "status": "ok",
            "cleared_count": cleared,
            "inserted_count": inserted,
            "sample": clean_accused[:3]
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

@app.get("/alerts")
def get_alerts(
    district_id: Optional[int] = None,
    recent_only: bool = False,
    catalyst_app: Any = Depends(get_catalyst_app)
):
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

    alerts = []
    for row in data_store_rows:
        if not isinstance(row, dict):
            continue

        did = row.get("DistrictID")
        if district_id is not None and str(did) != str(district_id):
            continue

        score = float(row.get("AnomalyScore") or 1.0)
        severity = "CRITICAL" if score >= 2.5 else ("HIGH" if score >= 2.0 else "MEDIUM")
        reason = str(row.get("FlagReason", "Crime anomaly detected"))

        alerts.append({
            "AnomalyID": row.get("AnomalyID"),
            "DistrictID": row.get("DistrictID"),
            "UnitID": row.get("UnitID"),
            "CrimeMajorHeadID": row.get("CrimeMajorHeadID"),
            "ObservedCount": row.get("ObservedCount"),
            "ExpectedCount": row.get("ExpectedCount"),
            "AnomalyScore": score,
            "FlagReason": reason,
            "Severity": severity,
            "WindowStart": str(row.get("WindowStart", "")),
            "WindowEnd": str(row.get("WindowEnd", "")),
            "DetectedAt": str(row.get("WindowEnd", datetime.now().strftime("%Y-%m-%d")))
        })

    if recent_only:
        alerts = sorted(alerts, key=lambda x: str(x.get("WindowEnd", "")), reverse=True)[:10]

    return {
        "status": "ok",
        "data": alerts,
        "count": len(alerts),
        "polling_interval_seconds": 15,
        "mechanism": "frontend_polling"
    }

def compute_occupation_overlay(
    complainants: List[Dict[str, Any]],
    cases: List[Dict[str, Any]],
    occupations: List[Dict[str, Any]],
    crime_heads: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    occ_map = {}
    for o in occupations:
        if isinstance(o, dict) and "OccupationID" in o:
            try:
                occ_map[int(o["OccupationID"])] = str(o.get("OccupationName", f"Occupation #{o['OccupationID']}"))
            except (ValueError, TypeError):
                pass

    head_map = {}
    for h in crime_heads:
        if isinstance(h, dict) and "CrimeHeadID" in h:
            try:
                head_map[int(h["CrimeHeadID"])] = str(h.get("CrimeGroupName", f"Category #{h['CrimeHeadID']}"))
            except (ValueError, TypeError):
                pass

    case_head_map = {}
    for c in cases:
        if isinstance(c, dict) and "CaseMasterID" in c:
            try:
                cmid = int(c["CaseMasterID"])
                hid = c.get("CrimeMajorHeadID")
                if hid is not None:
                    case_head_map[cmid] = int(hid)
            except (ValueError, TypeError):
                pass

    agg: Dict[int, Dict[str, Any]] = {}
    for occ_id, occ_name in occ_map.items():
        agg[occ_id] = {
            "OccupationID": occ_id,
            "OccupationName": occ_name,
            "total_count": 0,
            "categories": {hname: 0 for hname in head_map.values()}
        }

    for comp in complainants:
        if not isinstance(comp, dict):
            continue
        occ_id = comp.get("OccupationID")
        case_id = comp.get("CaseMasterID")
        if occ_id is None:
            continue
        try:
            occ_id = int(occ_id)
        except (ValueError, TypeError):
            continue

        if occ_id not in agg:
            occ_name = occ_map.get(occ_id, f"Occupation #{occ_id}")
            agg[occ_id] = {
                "OccupationID": occ_id,
                "OccupationName": occ_name,
                "total_count": 0,
                "categories": {hname: 0 for hname in head_map.values()}
            }

        agg[occ_id]["total_count"] += 1

        if case_id is not None:
            try:
                case_id = int(case_id)
                hid = case_head_map.get(case_id)
                if hid is not None and hid in head_map:
                    hname = head_map[hid]
                    agg[occ_id]["categories"][hname] = agg[occ_id]["categories"].get(hname, 0) + 1
            except (ValueError, TypeError):
                pass

    result = []
    for occ_id in sorted(agg.keys()):
        result.append(agg[occ_id])
    return result

@app.get("/overlays/occupation")
def get_occupation_overlay(catalyst_app: Any = Depends(get_catalyst_app)):
    comp_rows = []
    case_rows = []
    occ_rows = []
    head_rows = []

    if catalyst_app is not None:
        try:
            zcql = catalyst_app.zcql()
            try:
                q_comp = zcql.execute_query("SELECT ComplainantID, CaseMasterID, OccupationID FROM ComplainantDetails LIMIT 5000")
                comp_rows = [r.get("ComplainantDetails") for r in q_comp if isinstance(r, dict) and "ComplainantDetails" in r]
            except Exception:
                pass

            try:
                q_case = zcql.execute_query("SELECT CaseMasterID, CrimeMajorHeadID FROM CaseMaster LIMIT 5000")
                case_rows = [r.get("CaseMaster") for r in q_case if isinstance(r, dict) and "CaseMaster" in r]
            except Exception:
                pass
        except Exception:
            pass

    if not comp_rows:
        comp_rows = SEED_COMPLAINANTS
    if not case_rows:
        case_rows = SEED_CASES
    if not occ_rows:
        occ_rows = SEED_OCCUPATIONS
    if not head_rows:
        head_rows = SEED_CRIME_HEADS

    overlay_data = compute_occupation_overlay(comp_rows, case_rows, occ_rows, head_rows)
    return {"status": "ok", "data": overlay_data}

def compute_district_report_stats(
    district_id: int,
    cases: List[Dict[str, Any]],
    units: List[Dict[str, Any]],
    chargesheets: List[Dict[str, Any]],
    hotspots: List[Dict[str, Any]],
    crime_heads: List[Dict[str, Any]],
    districts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    dist_name = f"District #{district_id}"
    for d in districts:
        if isinstance(d, dict) and str(d.get("DistrictID")) == str(district_id):
            dist_name = d.get("DistrictName", dist_name)
            break

    unit_ids = set()
    for u in units:
        if isinstance(u, dict) and str(u.get("DistrictID")) == str(district_id):
            try:
                unit_ids.add(int(u["UnitID"]))
            except (ValueError, TypeError):
                pass

    head_map = {}
    for h in crime_heads:
        if isinstance(h, dict) and "CrimeHeadID" in h:
            try:
                head_map[int(h["CrimeHeadID"])] = str(h.get("CrimeGroupName", f"Category #{h['CrimeHeadID']}"))
            except (ValueError, TypeError):
                pass

    dist_cases = []
    cat_counts = {}
    case_ids = set()

    for c in cases:
        if not isinstance(c, dict):
            continue
        psid = c.get("PoliceStationID") or c.get("UnitID")
        try:
            psid = int(psid) if psid is not None else None
        except (ValueError, TypeError):
            psid = None

        if psid in unit_ids or not unit_ids:
            dist_cases.append(c)
            cid = c.get("CaseMasterID")
            if cid is not None:
                try:
                    case_ids.add(int(cid))
                except (ValueError, TypeError):
                    pass

            hid = c.get("CrimeMajorHeadID")
            if hid is not None:
                try:
                    hid_int = int(hid)
                    hname = head_map.get(hid_int, f"Category #{hid_int}")
                    cat_counts[hname] = cat_counts.get(hname, 0) + 1
                except (ValueError, TypeError):
                    pass

    total_incidents = len(dist_cases)
    top_categories = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)

    cs_set = set()
    for cs in chargesheets:
        if isinstance(cs, dict):
            cmid = cs.get("CaseMasterID")
            cstype = str(cs.get("cstype", "")).strip().upper()
            if cmid is not None and cstype in ("A", "CHARGESHEET", "CHARGESHEETED"):
                try:
                    cs_set.add(int(cmid))
                except (ValueError, TypeError):
                    pass

    resolved_count = len(case_ids.intersection(cs_set)) if case_ids else 0
    res_rate = round((resolved_count / total_incidents * 100), 1) if total_incidents > 0 else 0.0

    dist_hotspots = []
    for h in hotspots:
        if not isinstance(h, dict):
            continue
        did = h.get("DistrictID")
        uid = h.get("UnitID")
        if str(did) == str(district_id) or (uid is not None and int(uid) in unit_ids):
            dist_hotspots.append(h)

    return {
        "DistrictID": district_id,
        "DistrictName": dist_name,
        "IncidentCount": total_incidents,
        "TopCategories": top_categories,
        "ResolutionRate": res_rate,
        "ActiveHotspots": dist_hotspots,
        "GeneratedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def generate_pure_pdf_bytes(stats: Dict[str, Any]) -> bytes:
    dist_name = stats.get("DistrictName", "District Report")
    inc_cnt = stats.get("IncidentCount", 0)
    res_rate = stats.get("ResolutionRate", 0.0)
    cats = stats.get("TopCategories", [])
    hotspots = stats.get("ActiveHotspots", [])
    gen_time = stats.get("GeneratedAt", "")

    lines = [
        f"DRISHTI DISTRICT CRIME INTELLIGENCE REPORT",
        f"==================================================================",
        f"District: {dist_name} (ID: {stats.get('DistrictID', 1)})",
        f"Generated At: {gen_time}",
        f"",
        f"SUMMARY METRICS",
        f"------------------------------------------------------------------",
        f"  * Total Incidents Reported: {inc_cnt}",
        f"  * Resolution Rate (Chargesheeted): {res_rate}%",
        f"  * Active Hotspot Clusters: {len(hotspots)}",
        f"",
        f"TOP CRIME CATEGORIES",
        f"------------------------------------------------------------------"
    ]

    for cat_name, cnt in cats:
        pct = round((cnt / inc_cnt * 100), 1) if inc_cnt > 0 else 0.0
        lines.append(f"  * {cat_name}: {cnt} incidents ({pct}%)")

    if not cats:
        lines.append("  * No category breakdown available")

    lines.extend([
        f"",
        f"ACTIVE HOTSPOT CLUSTERS",
        f"------------------------------------------------------------------"
    ])

    for idx, h in enumerate(hotspots[:6], 1):
        cid = h.get("ClusterID", idx)
        lat = h.get("CentroidLat", 0.0)
        lng = h.get("CentroidLng", 0.0)
        icnt = h.get("IncidentCount", 0)
        tw_start = h.get("TimeWindowStart", "")
        tw_end = h.get("TimeWindowEnd", "")
        lines.append(f"  * Cluster #{cid}: Centroid ({lat:.4f}, {lng:.4f}) | Incidents: {icnt} | Window: {tw_start} to {tw_end}")

    if not hotspots:
        lines.append("  * No active hotspots recorded for this district")

    lines.extend([
        f"",
        f"==================================================================",
        f"Karnataka State Police - Official Drishti Analytics Platform"
    ])

    text_cmds = ["BT", "/F1 14 Tf", "36 750 Td", "15 TL"]
    for l in lines:
        safe_l = str(l).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if l.startswith("DRISHTI"):
            text_cmds.append("/F1 16 Tf")
            text_cmds.append(f"({safe_l}) Tj")
            text_cmds.append("T*")
            text_cmds.append("/F1 10 Tf")
        elif "SUMMARY METRICS" in l or "TOP CRIME CATEGORIES" in l or "ACTIVE HOTSPOT CLUSTERS" in l:
            text_cmds.append("/F1 12 Tf")
            text_cmds.append(f"({safe_l}) Tj")
            text_cmds.append("T*")
            text_cmds.append("/F1 10 Tf")
        else:
            text_cmds.append(f"({safe_l}) Tj")
            text_cmds.append("T*")
    text_cmds.append("ET")

    cs = "\n".join(text_cmds).encode('latin-1', 'replace')

    objs = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        f"4 0 obj\n<< /Length {len(cs)} >>\nstream\n".encode('latin-1') + cs + b"\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    ]

    buf = [b"%PDF-1.4\n"]
    offs = []
    c = len(buf[0])
    for o in objs:
        offs.append(c)
        buf.append(o)
        c += len(o)

    xoff = c
    xref = [f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode('latin-1')]
    for off in offs:
        xref.append(f"{off:010d} 00000 n \n".encode('latin-1'))
    buf.extend(xref)
    buf.append(f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xoff}\n%%EOF\n".encode('latin-1'))

    return b"".join(buf)

def generate_report_pdf_bytes(district_id: int, stats: Dict[str, Any], catalyst_app: Any = None) -> bytes:
    dist_name = stats.get("DistrictName", f"District #{district_id}")
    inc_cnt = stats.get("IncidentCount", 0)
    res_rate = stats.get("ResolutionRate", 0.0)
    cats = stats.get("TopCategories", [])
    hotspots = stats.get("ActiveHotspots", [])
    gen_time = stats.get("GeneratedAt", "")

    cat_rows_html = "".join([
        f"<tr><td>{cname}</td><td>{cnt}</td><td>{round((cnt/inc_cnt*100), 1) if inc_cnt > 0 else 0}%</td></tr>"
        for cname, cnt in cats
    ])

    hotspot_rows_html = "".join([
        f"<tr><td>Cluster #{h.get('ClusterID', '-') }</td><td>{h.get('CentroidLat', 0):.4f}, {h.get('CentroidLng', 0):.4f}</td><td>{h.get('IncidentCount', 0)}</td><td>{h.get('TimeWindowStart', '')} - {h.get('TimeWindowEnd', '')}</td></tr>"
        for h in hotspots[:10]
    ])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; margin: 30px; color: #1e293b; }}
  h1 {{ color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; }}
  .metrics {{ display: flex; gap: 20px; margin: 20px 0; }}
  .card {{ background: #f8fafc; border: 1px solid #cbd5e1; padding: 15px; border-radius: 6px; flex: 1; text-align: center; }}
  .card h3 {{ margin: 0; font-size: 12px; color: #64748b; text-transform: uppercase; }}
  .card p {{ margin: 5px 0 0 0; font-size: 22px; font-weight: bold; color: #0f172a; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 25px; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; font-size: 13px; }}
  th {{ background: #f1f5f9; }}
</style>
</head>
<body>
  <h1>Drishti District Crime Intelligence Report</h1>
  <p><strong>District:</strong> {dist_name} (ID: {district_id}) | <strong>Generated:</strong> {gen_time}</p>
  <div class="metrics">
    <div class="card"><h3>Total Incidents</h3><p>{inc_cnt}</p></div>
    <div class="card"><h3>Resolution Rate</h3><p>{res_rate}%</p></div>
    <div class="card"><h3>Active Hotspots</h3><p>{len(hotspots)}</p></div>
  </div>
  <h2>Top Crime Categories</h2>
  <table>
    <thead><tr><th>Category</th><th>Incidents</th><th>Percentage</th></tr></thead>
    <tbody>{cat_rows_html}</tbody>
  </table>
  <h2>Active Hotspots</h2>
  <table>
    <thead><tr><th>Cluster</th><th>Centroid Lat / Lng</th><th>Incidents</th><th>Time Window</th></tr></thead>
    <tbody>{hotspot_rows_html}</tbody>
  </table>
</body>
</html>"""

    pdf_bytes = None
    if catalyst_app is not None:
        try:
            sb = catalyst_app.smartbrowz()
            res = sb.convert_to_pdf(source=html_content)
            if isinstance(res, bytes):
                pdf_bytes = res
            elif hasattr(res, 'content') and isinstance(res.content, bytes):
                pdf_bytes = res.content
            elif hasattr(res, 'read'):
                pdf_bytes = res.read()
            elif isinstance(res, dict) and "content" in res:
                content_val = res["content"]
                pdf_bytes = content_val.encode('utf-8') if isinstance(content_val, str) else content_val
        except Exception as e:
            print(f"SmartBrowz PDF conversion exception: {e}", flush=True)

    if not pdf_bytes or not isinstance(pdf_bytes, bytes) or not pdf_bytes.startswith(b"%PDF"):
        pdf_bytes = generate_pure_pdf_bytes(stats)

    return pdf_bytes

@app.post("/reports/generate")
@app.get("/reports/generate")
def generate_report(district_id: int = 1, catalyst_app: Any = Depends(get_catalyst_app)):
    stats = compute_district_report_stats(
        district_id,
        SEED_CASES,
        SEED_UNITS,
        SEED_CHARGESHEETS,
        SEED_HOTSPOTS,
        SEED_CRIME_HEADS,
        SEED_DISTRICTS
    )
    pdf_bytes = generate_report_pdf_bytes(district_id, stats, catalyst_app)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=drishti_report_district_{district_id}.pdf"
        }
    )

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

def compute_predictive_risk_scores(hotspots: List[Dict[str, Any]], anomalies: List[Dict[str, Any]], resolution_metrics: List[Dict[str, Any]], units: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    res_dict = {m.get("UnitID"): m for m in resolution_metrics if isinstance(m, dict)}

    hotspot_incidents_by_unit: Dict[int, float] = {}
    hotspot_mh_by_unit: Dict[int, int] = {}
    for h in hotspots:
        if not isinstance(h, dict):
            continue
        uid = h.get("UnitID")
        if uid is not None:
            try:
                uid_int = int(uid)
                inc = float(h.get("IncidentCount") or 0)
                hotspot_incidents_by_unit[uid_int] = hotspot_incidents_by_unit.get(uid_int, 0.0) + inc
                if uid_int not in hotspot_mh_by_unit and h.get("CrimeMajorHeadID") is not None:
                    hotspot_mh_by_unit[uid_int] = int(h.get("CrimeMajorHeadID"))
            except (ValueError, TypeError):
                pass

    anomaly_by_unit: Dict[int, float] = {}
    for a in anomalies:
        if not isinstance(a, dict):
            continue
        uid = a.get("UnitID")
        if uid is not None:
            try:
                uid_int = int(uid)
                score = float(a.get("AnomalyScore") or 1.0)
                anomaly_by_unit[uid_int] = max(anomaly_by_unit.get(uid_int, 1.0), score)
            except (ValueError, TypeError):
                pass

    computed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risk_records = []

    for idx, u in enumerate(units):
        if not isinstance(u, dict):
            continue
        uid_raw = u.get("UnitID")
        if uid_raw is None:
            continue
        try:
            uid = int(uid_raw)
        except (ValueError, TypeError):
            continue

        did = u.get("DistrictID") or 1
        try:
            did = int(did)
        except (ValueError, TypeError):
            did = 1

        cmhid = hotspot_mh_by_unit.get(uid, 1)

        h_inc = hotspot_incidents_by_unit.get(uid, 0.0)
        h_score = min(10.0, h_inc / 8.0)

        a_val = anomaly_by_unit.get(uid, 1.0)
        a_score = min(10.0, a_val * 2.2)

        res_m = res_dict.get(uid, {})
        res_rate = float(res_m.get("ResolutionRatePct", 50.0))
        u_score = (100.0 - res_rate) / 10.0

        risk_val = round((0.40 * h_score) + (0.35 * a_score) + (0.25 * u_score), 2)
        if risk_val >= 7.0:
            level = "High"
        elif risk_val >= 4.5:
            level = "Medium"
        else:
            level = "Low"

        risk_records.append({
            "RiskScoreID": idx + 1,
            "DistrictID": did,
            "UnitID": uid,
            "CrimeMajorHeadID": cmhid,
            "RiskLevel": level,
            "RiskValue": risk_val,
            "ModelVersion": "v1.0-weighted",
            "ComputedAt": computed_time
        })

    return risk_records

@app.get("/risk-scores")
def get_risk_scores(catalyst_app: Any = Depends(get_catalyst_app)):
    rows = []
    if catalyst_app is not None:
        try:
            zcql = catalyst_app.zcql()
            q_res = zcql.execute_query("SELECT * FROM RiskScore LIMIT 200")
            rows = [r.get("RiskScore") for r in q_res if isinstance(r, dict) and "RiskScore" in r]
        except Exception:
            try:
                table = catalyst_app.datastore().table("RiskScore")
                rows = table.get_paged_rows(max_rows=200).get("data", [])
            except Exception:
                pass

    if not rows:
        cs_rows = []
        if catalyst_app is not None:
            try:
                zcql = catalyst_app.zcql()
                q_res = zcql.execute_query("SELECT * FROM ChargesheetDetails LIMIT 5000")
                cs_rows = [r.get("ChargesheetDetails") for r in q_res if isinstance(r, dict) and "ChargesheetDetails" in r]
            except Exception:
                pass
        if not cs_rows:
            cs_rows = SEED_CHARGESHEETS

        res_metrics = compute_station_resolution_metrics(cs_rows, SEED_CASES, SEED_UNITS)
        computed_scores = compute_predictive_risk_scores(SEED_HOTSPOTS, SEED_ANOMALIES, res_metrics, SEED_UNITS)

        if catalyst_app is not None:
            try:
                table = catalyst_app.datastore().table("RiskScore")
                for row in computed_scores:
                    try:
                        table.insert_row(row)
                    except Exception:
                        pass
            except Exception:
                pass

        rows = computed_scores

    return {"status": "ok", "data": rows}

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

def compute_mo_matching(
    method_tags: List[Dict[str, Any]],
    cases: List[Dict[str, Any]],
    accused_list: List[Dict[str, Any]],
    units_list: List[Dict[str, Any]],
    target_method_tag: Optional[str] = None,
    limit_per_tag: int = 50
) -> List[Dict[str, Any]]:
    case_map = {}
    for c in cases:
        if isinstance(c, dict) and "CaseMasterID" in c:
            try:
                case_map[int(c["CaseMasterID"])] = c
            except (ValueError, TypeError):
                pass

    accused_map = {}
    for a in accused_list:
        if isinstance(a, dict) and "CaseMasterID" in a:
            try:
                cmid = int(a["CaseMasterID"])
                if cmid not in accused_map:
                    accused_map[cmid] = a.get("AccusedName", "Unknown Accused")
            except (ValueError, TypeError):
                pass

    unit_map = {}
    for u in units_list:
        if isinstance(u, dict) and "UnitID" in u:
            try:
                unit_map[int(u["UnitID"])] = u.get("UnitName", f"Station #{u['UnitID']}")
            except (ValueError, TypeError):
                pass

    grouped_tags: Dict[str, List[Dict[str, Any]]] = {}
    for m in method_tags:
        if not isinstance(m, dict):
            continue
        tag = str(m.get("MethodTag", "")).strip()
        cmid = m.get("CaseMasterID")
        if not tag or cmid is None:
            continue
        try:
            cmid = int(cmid)
        except (ValueError, TypeError):
            continue

        if target_method_tag and tag.lower() != target_method_tag.strip().lower():
            continue

        if tag not in grouped_tags:
            grouped_tags[tag] = []

        c_obj = case_map.get(cmid, {})
        psid = c_obj.get("PoliceStationID") or c_obj.get("UnitID") or 1
        try:
            psid = int(psid)
        except (ValueError, TypeError):
            psid = 1

        grouped_tags[tag].append({
            "CaseMasterID": cmid,
            "CrimeNo": str(c_obj.get("CrimeNo", f"FIR-{cmid}")),
            "CaseNo": str(c_obj.get("CaseNo", f"CASE-{cmid}")),
            "CrimeRegisteredDate": str(c_obj.get("CrimeRegisteredDate", "")),
            "PoliceStationID": psid,
            "PoliceStationName": unit_map.get(psid, f"Station #{psid}"),
            "AccusedName": accused_map.get(cmid, "Unknown Accused"),
            "latitude": float(c_obj.get("latitude") or 0.0),
            "longitude": float(c_obj.get("longitude") or 0.0),
            "BriefFacts": str(c_obj.get("BriefFacts", ""))
        })

    result = []
    for tag in sorted(grouped_tags.keys()):
        item_list = grouped_tags[tag]
        distinct_accused = list(set(x["AccusedName"] for x in item_list))
        distinct_stations = list(set(x["PoliceStationID"] for x in item_list))

        result.append({
            "MethodTag": tag,
            "matched_cases_count": len(item_list),
            "distinct_accused_count": len(distinct_accused),
            "distinct_stations_count": len(distinct_stations),
            "cross_accused": len(distinct_accused) > 1,
            "cross_location": len(distinct_stations) > 1,
            "matching_cases": item_list[:limit_per_tag]
        })

    return result

@app.get("/mo-matching")
@app.get("/cases/mo-matching")
def get_mo_matching(
    method_tag: Optional[str] = None,
    limit: int = 50,
    catalyst_app: Any = Depends(get_catalyst_app)
):
    mt_rows = []
    if catalyst_app is not None:
        try:
            zcql = catalyst_app.zcql()
            q_res = zcql.execute_query("SELECT * FROM CaseMethodTag LIMIT 5000")
            mt_rows = [r.get("CaseMethodTag") for r in q_res if isinstance(r, dict) and "CaseMethodTag" in r]
        except Exception:
            try:
                table = catalyst_app.datastore().table("CaseMethodTag")
                mt_rows = table.get_paged_rows(max_rows=5000).get("data", [])
            except Exception:
                pass

    if not mt_rows:
        mt_rows = SEED_METHOD_TAGS

    mo_results = compute_mo_matching(mt_rows, SEED_CASES, SEED_ACCUSED, SEED_UNITS, target_method_tag=method_tag, limit_per_tag=limit)
    return {
        "status": "ok",
        "method_taxonomy": ["Vehicle Theft", "Break-in", "Pickpocket", "Armed Robbery", "Snatch-and-Run", "Physical Assault", "Armed Attack"],
        "total_mo_cases": len(mt_rows),
        "data": mo_results
    }

@app.get("/incidents/{id}/mo-matches")
def get_incident_mo_matches(id: int, catalyst_app: Any = Depends(get_catalyst_app)):
    mt_rows = []
    if catalyst_app is not None:
        try:
            zcql = catalyst_app.zcql()
            q_res = zcql.execute_query("SELECT * FROM CaseMethodTag LIMIT 5000")
            mt_rows = [r.get("CaseMethodTag") for r in q_res if isinstance(r, dict) and "CaseMethodTag" in r]
        except Exception:
            pass

    if not mt_rows:
        mt_rows = SEED_METHOD_TAGS

    target_tag = None
    for m in mt_rows:
        if isinstance(m, dict) and str(m.get("CaseMasterID")) == str(id):
            target_tag = m.get("MethodTag")
            break

    if not target_tag:
        return {"status": "ok", "CaseMasterID": id, "MethodTag": None, "matching_cases": []}

    mo_results = compute_mo_matching(mt_rows, SEED_CASES, SEED_ACCUSED, SEED_UNITS, target_method_tag=target_tag, limit_per_tag=50)
    matched_cases = mo_results[0]["matching_cases"] if mo_results else []
    filtered_matches = [c for c in matched_cases if str(c.get("CaseMasterID")) != str(id)]

    return {
        "status": "ok",
        "CaseMasterID": id,
        "MethodTag": target_tag,
        "matched_cases_count": len(filtered_matches),
        "matching_cases": filtered_matches
    }

if __name__ == "__main__":
    port_env = os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT")
    port = int(port_env) if port_env else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
