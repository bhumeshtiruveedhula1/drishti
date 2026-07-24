import json
import math
from typing import List, Dict, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two lat/lng coordinate pairs."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def perform_link_analysis(accused_records: List[Dict[str, Any]],
                          case_records: List[Dict[str, Any]],
                          victim_records: List[Dict[str, Any]] = None,
                          unit_records: List[Dict[str, Any]] = None,
                          proximity_threshold_km: float = 5.0) -> Dict[str, Any]:
    """
    On-demand query for identifying:
    1. Repeat offenders (same AccusedName appearing across multiple CaseMasterIDs)
    2. Shared-location clusters (multiple CaseMasterIDs with close lat/lng and overlapping Accused)
    
    Output format: JSON Graph (nodes: Accused/Victim/Unit/CaseMaster, edges: shared CaseMasterID & proximity).
    """
    if victim_records is None:
        victim_records = []
    if unit_records is None:
        unit_records = []

    cases_by_id = {c["CaseMasterID"]: c for c in case_records if "CaseMasterID" in c}

    # Step 1: Group cases by AccusedName to find Repeat Offenders
    accused_by_name: Dict[str, List[int]] = {}
    for acc in accused_records:
        name = acc.get("AccusedName")
        case_id = acc.get("CaseMasterID")
        if name and case_id:
            accused_by_name.setdefault(name, []).append(case_id)

    repeat_offenders = {name: list(set(c_ids)) for name, c_ids in accused_by_name.items() if len(set(c_ids)) > 1}

    nodes = []
    edges = []
    node_ids = set()

    def add_node(node_id: str, label: str, node_type: str, metadata: Dict[str, Any]):
        if node_id not in node_ids:
            node_ids.add(node_id)
            nodes.append({
                "id": node_id,
                "label": label,
                "type": node_type,
                "metadata": metadata
            })

    def add_edge(source: str, target: str, relationship: str, metadata: Dict[str, Any] = None):
        edges.append({
            "source": source,
            "target": target,
            "relationship": relationship,
            "metadata": metadata or {}
        })

    cluster_id_counter = 1

    # Step 2: Build nodes and edges for repeat offender clusters
    for offender_name, case_ids in repeat_offenders.items():
        offender_node_id = f"accused_{offender_name.replace(' ', '_').lower()}"
        add_node(offender_node_id, offender_name, "Accused", {
            "is_repeat_offender": True,
            "total_incidents": len(case_ids)
        })

        cluster_cases = []
        for case_id in case_ids:
            case_data = cases_by_id.get(case_id, {})
            case_node_id = f"case_{case_id}"
            add_node(case_node_id, case_data.get("CrimeNo", f"Case #{case_id}"), "CaseMaster", {
                "CaseMasterID": case_id,
                "CaseNo": case_data.get("CaseNo"),
                "CrimeRegisteredDate": case_data.get("CrimeRegisteredDate"),
                "latitude": case_data.get("latitude"),
                "longitude": case_data.get("longitude")
            })
            add_edge(offender_node_id, case_node_id, "ACCUSED_IN", {"case_id": case_id})

            # Associated Victims
            for vic in victim_records:
                if vic.get("CaseMasterID") == case_id:
                    vic_name = vic.get("VictimName", f"Victim_{vic.get('VictimMasterID')}")
                    vic_node_id = f"victim_{vic.get('VictimMasterID', vic_name.replace(' ', '_'))}"
                    add_node(vic_node_id, vic_name, "Victim", {
                        "VictimMasterID": vic.get("VictimMasterID"),
                        "CaseMasterID": case_id
                    })
                    add_edge(case_node_id, vic_node_id, "VICTIM_OF", {"case_id": case_id})

            # Associated Police Station Unit
            unit_id = case_data.get("PoliceStationID")
            if unit_id:
                unit_node_id = f"unit_{unit_id}"
                unit_name = next((u.get("UnitName") for u in unit_records if u.get("UnitID") == unit_id), f"Station #{unit_id}")
                add_node(unit_node_id, unit_name, "Unit", {"UnitID": unit_id})
                add_edge(case_node_id, unit_node_id, "JURISDICTION_UNIT", {"unit_id": unit_id})

            if case_data.get("latitude") is not None and case_data.get("longitude") is not None:
                cluster_cases.append(case_data)

        # Step 3: Shared-location spatial proximity check
        for i in range(len(cluster_cases)):
            for j in range(i + 1, len(cluster_cases)):
                c1 = cluster_cases[i]
                c2 = cluster_cases[j]
                dist = haversine_distance(c1["latitude"], c1["longitude"], c2["latitude"], c2["longitude"])
                if dist <= proximity_threshold_km:
                    add_edge(
                        f"case_{c1['CaseMasterID']}",
                        f"case_{c2['CaseMasterID']}",
                        "SPATIAL_PROXIMITY_CLUSTER",
                        {
                            "distance_km": round(dist, 2),
                            "cluster_id": f"cluster_{cluster_id_counter}",
                            "offender_name": offender_name
                        }
                    )
        cluster_id_counter += 1

    return {
        "graph": {
            "summary": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "repeat_offenders_count": len(repeat_offenders)
            },
            "nodes": nodes,
            "edges": edges
        }
    }

# Demo seed dataset representing 2 real example clusters (Cluster 1: Bengaluru Robbery Gang, Cluster 2: Mysuru Burglary Ring)
SAMPLE_UNITS = [
    {"UnitID": 101, "UnitName": "Koramangala Police Station"},
    {"UnitID": 102, "UnitName": "Indiranagar Police Station"},
    {"UnitID": 201, "UnitName": "Vidyaranyapuram Police Station"}
]

SAMPLE_CASES = [
    # Cluster 1: Bengaluru Urban (Koramangala / Indiranagar) - ~2.5 km apart
    {
        "CaseMasterID": 5001,
        "CrimeNo": "FIR-2026-BLR-001",
        "CaseNo": "CASE-5001",
        "CrimeRegisteredDate": "2026-06-10",
        "PoliceStationID": 101,
        "latitude": 12.9352,
        "longitude": 77.6245
    },
    {
        "CaseMasterID": 5002,
        "CrimeNo": "FIR-2026-BLR-045",
        "CaseNo": "CASE-5002",
        "CrimeRegisteredDate": "2026-07-02",
        "PoliceStationID": 102,
        "latitude": 12.9719,
        "longitude": 77.6412
    },
    # Cluster 2: Mysuru (Vidyaranyapuram / Kuvempunagar) - ~1.8 km apart
    {
        "CaseMasterID": 6001,
        "CrimeNo": "FIR-2026-MYS-012",
        "CaseNo": "CASE-6001",
        "CrimeRegisteredDate": "2026-05-15",
        "PoliceStationID": 201,
        "latitude": 12.2831,
        "longitude": 76.6432
    },
    {
        "CaseMasterID": 6002,
        "CrimeNo": "FIR-2026-MYS-089",
        "CaseNo": "CASE-6002",
        "CrimeRegisteredDate": "2026-07-18",
        "PoliceStationID": 201,
        "latitude": 12.2965,
        "longitude": 76.6501
    }
]

SAMPLE_ACCUSED = [
    # Cluster 1 Repeat Offender: Ramesh Kumar
    {"AccusedMasterID": 101, "CaseMasterID": 5001, "AccusedName": "Ramesh Kumar", "AgeYear": 32, "GenderID": 1},
    {"AccusedMasterID": 102, "CaseMasterID": 5002, "AccusedName": "Ramesh Kumar", "AgeYear": 32, "GenderID": 1},
    # Cluster 2 Repeat Offender: Suresh Gowda
    {"AccusedMasterID": 201, "CaseMasterID": 6001, "AccusedName": "Suresh Gowda", "AgeYear": 28, "GenderID": 1},
    {"AccusedMasterID": 202, "CaseMasterID": 6002, "AccusedName": "Suresh Gowda", "AgeYear": 28, "GenderID": 1}
]

SAMPLE_VICTIMS = [
    {"VictimMasterID": 301, "CaseMasterID": 5001, "VictimName": "Anand Rao"},
    {"VictimMasterID": 302, "CaseMasterID": 5002, "VictimName": "Priya Sharma"},
    {"VictimMasterID": 401, "CaseMasterID": 6001, "VictimName": "Mahadevappa"},
    {"VictimMasterID": 402, "CaseMasterID": 6002, "VictimName": "Sunitha Patel"}
]

if __name__ == "__main__":
    result = perform_link_analysis(
        accused_records=SAMPLE_ACCUSED,
        case_records=SAMPLE_CASES,
        victim_records=SAMPLE_VICTIMS,
        unit_records=SAMPLE_UNITS,
        proximity_threshold_km=5.0
    )
    print(json.dumps(result, indent=2))
