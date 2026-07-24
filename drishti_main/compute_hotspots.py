import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.cluster import DBSCAN

def compute_hotspots():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    seeds_bc_dir = os.path.join(script_dir, 'seeds', 'batch_bc')
    if not os.path.exists(seeds_bc_dir):
        seeds_bc_dir = os.path.join(project_dir, 'drishti_main', 'seeds', 'batch_bc')
        
    seeds_e_dir = os.path.join(script_dir, 'seeds', 'batch_e')
    os.makedirs(seeds_e_dir, exist_ok=True)
    
    cm_path = os.path.join(seeds_bc_dir, 'CaseMaster.csv')
    unit_path = os.path.join(seeds_bc_dir, 'Unit.csv')
    
    print(f"Loading CaseMaster data from: {cm_path}")
    cm_df = pd.read_csv(cm_path)
    unit_df = pd.read_csv(unit_path)
    
    # Build mappings
    unit_to_dist = dict(zip(unit_df['UnitID'], unit_df['DistrictID']))
    dist_to_unit = dict(zip(unit_df['DistrictID'], unit_df['UnitID']))
    
    cm_df['DistrictID'] = cm_df['PoliceStationID'].map(unit_to_dist)
    
    # Earth radius in kilometers for haversine metric
    EARTH_RADIUS_KM = 6371.0088
    # Epsilon = 8 km radius, Min samples = 4
    EPSILON_RAD = 8.0 / EARTH_RADIUS_KM
    MIN_SAMPLES = 4
    
    current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    clusters = []
    cluster_counter = 1
    total_noise_points = 0
    total_clustered_incidents = 0
    
    # Perform DBSCAN clustering per (DistrictID, CrimeMajorHeadID)
    grouped = cm_df.groupby(['DistrictID', 'CrimeMajorHeadID'])
    
    for (dist_id, crime_head_id), group in grouped:
        if len(group) < MIN_SAMPLES:
            total_noise_points += len(group)
            continue
            
        coords = group[['latitude', 'longitude']].values
        coords_rad = np.radians(coords)
        
        db = DBSCAN(eps=EPSILON_RAD, min_samples=MIN_SAMPLES, metric='haversine').fit(coords_rad)
        labels = db.labels_
        
        for lbl in set(labels):
            if lbl == -1:
                total_noise_points += list(labels).count(-1)
                continue # Constraint: Exclude noise (-1) label
                
            cluster_mask = (labels == lbl)
            cluster_pts = group[cluster_mask]
            
            centroid_lat = float(cluster_pts['latitude'].mean())
            centroid_lng = float(cluster_pts['longitude'].mean())
            inc_count = int(len(cluster_pts))
            total_clustered_incidents += inc_count
            
            time_start = str(cluster_pts['IncidentFromDate'].min())[:10]
            time_end = str(cluster_pts['IncidentFromDate'].max())[:10]
            
            clusters.append({
                'ClusterID': cluster_counter,
                'DistrictID': int(dist_id),
                'UnitID': int(dist_to_unit[dist_id]),
                'CrimeMajorHeadID': int(crime_head_id),
                'CentroidLat': round(centroid_lat, 6),
                'CentroidLng': round(centroid_lng, 6),
                'IncidentCount': inc_count,
                'TimeWindowStart': time_start,
                'TimeWindowEnd': time_end,
                'ComputedAt': current_time_str
            })
            cluster_counter += 1
            
    cluster_df = pd.DataFrame(clusters)
    
    # Match schema column ordering exactly
    schema_cols = [
        'ClusterID', 'DistrictID', 'UnitID', 'CrimeMajorHeadID',
        'CentroidLat', 'CentroidLng', 'IncidentCount',
        'TimeWindowStart', 'TimeWindowEnd', 'ComputedAt'
    ]
    cluster_df = cluster_df[schema_cols]
    
    out_csv_path = os.path.join(seeds_e_dir, 'HotspotCluster.csv')
    cluster_df.to_csv(out_csv_path, index=False)
    
    print("\n" + "="*70)
    print("DBSCAN HOTSPOT CLUSTERING SUMMARY")
    print("="*70)
    print(f"Total Incidents Processed: {len(cm_df)}")
    print(f"Clustered Incidents: {total_clustered_incidents}")
    print(f"Noise Incidents Excluded (-1 label): {total_noise_points}")
    print(f"Total Hotspot Clusters Identified: {len(cluster_df)}")
    print(f"Output File: {out_csv_path}")
    print("="*70 + "\n")
    
    print("="*70)
    print("SAMPLE HOTSPOT CLUSTER RESULTS (DEFINITION OF DONE)")
    print("="*70)
    print(cluster_df.head(10).to_string(index=False))
    print("="*70 + "\n")
    
    return cluster_df

if __name__ == '__main__':
    compute_hotspots()
