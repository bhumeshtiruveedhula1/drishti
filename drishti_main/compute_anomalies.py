import os
import pandas as pd
import numpy as np

def compute_anomalies():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    seeds_a_dir = os.path.join(script_dir, 'seeds', 'batch_a')
    seeds_bc_dir = os.path.join(script_dir, 'seeds', 'batch_bc')
    seeds_e_dir = os.path.join(script_dir, 'seeds', 'batch_e')
    os.makedirs(seeds_e_dir, exist_ok=True)

    cm_path = os.path.join(seeds_bc_dir, 'CaseMaster.csv')
    unit_path = os.path.join(seeds_bc_dir, 'Unit.csv')
    crime_head_path = os.path.join(seeds_a_dir, 'CrimeHead.csv')

    print(f"Loading CaseMaster data from: {cm_path}")
    cm_df = pd.read_csv(cm_path)
    unit_df = pd.read_csv(unit_path)
    crime_head_df = pd.read_csv(crime_head_path)

    unit_to_dist = dict(zip(unit_df['UnitID'], unit_df['DistrictID']))
    crime_head_name_map = dict(zip(crime_head_df['CrimeHeadID'], crime_head_df['CrimeGroupName']))

    cm_df['Month'] = pd.to_datetime(cm_df['CrimeRegisteredDate']).dt.to_period('M')

    # Calculate monthly counts per station and crime head
    monthly_counts = cm_df.groupby(['PoliceStationID', 'CrimeMajorHeadID', 'Month']).size().reset_index(name='count')

    anomalies = []
    anomaly_counter = 1

    # Perform statistical anomaly detection
    for (unit_id, crime_head_id), group in monthly_counts.groupby(['PoliceStationID', 'CrimeMajorHeadID']):
        counts = group['count'].values
        if len(counts) < 3:
            continue
            
        mean_exp = float(counts.mean())
        std_dev = float(counts.std(ddof=0))
        if std_dev == 0:
            std_dev = 1.0

        for _, row in group.iterrows():
            obs = int(row['count'])
            z_score = (obs - mean_exp) / std_dev
            pct_dev = ((obs - mean_exp) / mean_exp) * 100.0 if mean_exp > 0 else 0.0

            # Threshold: Z-score >= 1.6 and Observed >= Expected + 3
            if z_score >= 1.6 and obs >= mean_exp + 3:
                m_str = str(row['Month'])
                w_start = f"{m_str}-01"
                w_end = f"{m_str}-28"
                cname = crime_head_name_map.get(crime_head_id, 'Crime')

                anomalies.append({
                    'AnomalyID': anomaly_counter,
                    'DistrictID': int(unit_to_dist[unit_id]),
                    'UnitID': int(unit_id),
                    'CrimeMajorHeadID': int(crime_head_id),
                    'ObservedCount': obs,
                    'ExpectedCount': round(mean_exp, 2),
                    'AnomalyScore': round(z_score, 2),
                    'FlagReason': f"Spike in {cname}: {obs} cases vs baseline {mean_exp:.1f} (Z-Score: +{z_score:.2f}, +{pct_dev:.1f}%)",
                    'WindowStart': w_start,
                    'WindowEnd': w_end
                })
                anomaly_counter += 1

    anomaly_df = pd.DataFrame(anomalies)

    # Match schema column names and ordering exactly
    schema_cols = [
        'AnomalyID', 'DistrictID', 'UnitID', 'CrimeMajorHeadID',
        'ObservedCount', 'ExpectedCount', 'AnomalyScore',
        'FlagReason', 'WindowStart', 'WindowEnd'
    ]
    anomaly_df = anomaly_df[schema_cols]

    out_csv_path = os.path.join(seeds_e_dir, 'AnomalyFlag.csv')
    anomaly_df.to_csv(out_csv_path, index=False)

    print("\n" + "="*70)
    print("ANOMALY DETECTION SUMMARY")
    print("="*70)
    print(f"Total Station/Crime-Head/Month Windows Evaluated: {len(monthly_counts)}")
    print(f"Total Anomalies Flagged (Exceeding Threshold): {len(anomaly_df)}")
    print(f"Output File: {out_csv_path}")
    print("="*70 + "\n")

    print("="*70)
    print("SAMPLE ANOMALY FLAG RECORDS (DEFINITION OF DONE)")
    print("="*70)
    print(anomaly_df.head(10).to_string(index=False))
    print("="*70 + "\n")

    return anomaly_df

if __name__ == '__main__':
    compute_anomalies()
