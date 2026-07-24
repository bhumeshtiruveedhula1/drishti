import os
import csv
import json
from typing import List, Dict, Any

SEED_DIR = os.path.join(os.path.dirname(__file__), "..", "drishti_main", "seeds")

def load_csv_data(filepath: str) -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return []
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed_row = {}
            for k, v in row.items():
                if v is None or v == "":
                    parsed_row[k] = None
                    continue
                # Parse numeric types
                if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
                    parsed_row[k] = int(v)
                else:
                    try:
                        parsed_row[k] = float(v)
                    except ValueError:
                        parsed_row[k] = v
            records.append(parsed_row)
    return records

def get_hotspot_clusters() -> List[Dict[str, Any]]:
    path = os.path.join(SEED_DIR, "batch_e", "HotspotCluster.csv")
    return load_csv_data(path)

def get_anomaly_flags() -> List[Dict[str, Any]]:
    path = os.path.join(SEED_DIR, "batch_e", "AnomalyFlag.csv")
    return load_csv_data(path)

def get_case_master() -> List[Dict[str, Any]]:
    path = os.path.join(SEED_DIR, "batch_bc", "CaseMaster.csv")
    return load_csv_data(path)

def get_accused() -> List[Dict[str, Any]]:
    path = os.path.join(SEED_DIR, "batch_bc", "Accused.csv")
    return load_csv_data(path)

def get_victims() -> List[Dict[str, Any]]:
    path = os.path.join(SEED_DIR, "batch_bc", "Victim.csv")
    return load_csv_data(path)

def get_units() -> List[Dict[str, Any]]:
    path = os.path.join(SEED_DIR, "batch_bc", "Unit.csv")
    return load_csv_data(path)

if __name__ == "__main__":
    hotspots = get_hotspot_clusters()
    anomalies = get_anomaly_flags()
    cases = get_case_master()
    accused = get_accused()
    victims = get_victims()
    print(f"Loaded {len(hotspots)} Hotspot Clusters")
    print(f"Loaded {len(anomalies)} Anomaly Flags")
    print(f"Loaded {len(cases)} CaseMaster Records")
    print(f"Loaded {len(accused)} Accused Records")
    print(f"Loaded {len(victims)} Victim Records")
