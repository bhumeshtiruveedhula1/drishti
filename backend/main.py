import os
import sys
from typing import Optional, List, Dict, Any

print("Starting AppSail server...", flush=True)

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="Drishti Backend API - Final Slices")

# In-memory store fallback for initial validation / offline sync
IN_MEMORY_INCIDENTS: List[Dict[str, Any]] = []
IN_MEMORY_HOTSPOTS: List[Dict[str, Any]] = []
IN_MEMORY_ANOMALIES: List[Dict[str, Any]] = []
IN_MEMORY_ACCUSED: List[Dict[str, Any]] = []
IN_MEMORY_VICTIMS: List[Dict[str, Any]] = []
IN_MEMORY_RESOLUTION: List[Dict[str, Any]] = []

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
