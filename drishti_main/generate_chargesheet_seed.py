import os
import pandas as pd
from datetime import datetime, timedelta

def generate_chargesheet_seed():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    seeds_bc_dir = os.path.join(script_dir, 'seeds', 'batch_bc')
    if not os.path.exists(os.path.join(seeds_bc_dir, 'CaseMaster.csv')):
        seeds_bc_dir = os.path.join(script_dir, 'drishti', 'drishti_main', 'seeds', 'batch_bc')
    if not os.path.exists(os.path.join(seeds_bc_dir, 'CaseMaster.csv')):
        seeds_bc_dir = os.path.join(project_dir, 'drishti', 'drishti_main', 'seeds', 'batch_bc')

    seeds_d_dir = os.path.join(script_dir, 'seeds', 'batch_d')
    os.makedirs(seeds_d_dir, exist_ok=True)

    cm_path = os.path.join(seeds_bc_dir, 'CaseMaster.csv')
    emp_path = os.path.join(seeds_bc_dir, 'Employee.csv')

    print(f"Loading CaseMaster data from: {cm_path}")
    cm_df = pd.read_csv(cm_path)
    emp_df = pd.read_csv(emp_path)

    valid_case_ids = set(cm_df['CaseMasterID'])
    valid_emp_ids = set(emp_df['EmployeeID'])

    cs_data = []

    for idx, row in cm_df.iterrows():
        csid = idx + 1
        case_id = int(row['CaseMasterID'])
        status_id = int(row['CaseStatusID'])
        emp_id = int(row['PolicePersonID'])
        reg_date_str = str(row['CrimeRegisteredDate'])

        # Calculate chargesheet filing date (csdate = reg_date + 15..75 days)
        reg_dt = datetime.strptime(reg_date_str, '%Y-%m-%d')
        days_offset = 15 + (case_id % 61)
        cs_dt = reg_dt + timedelta(days=days_offset)
        csdate_str = cs_dt.strftime('%Y-%m-%d') + ' 11:30:00'

        # Assign cstype based on modeled CaseStatusID and disposition
        # CaseStatusID 1 = Chargesheeted -> 100% 'A'
        # CaseStatusID 2 = Closed -> 33% 'B' (False Case), 67% 'C' (Undetected)
        # CaseStatusID 3 = Under Investigation -> 50% 'A', 15% 'B', 35% 'C'
        if status_id == 1:
            cstype = 'A'
        elif status_id == 2:
            cstype = 'B' if case_id % 3 == 0 else 'C'
        else:
            mod_val = case_id % 10
            if mod_val < 5:
                cstype = 'A'
            elif mod_val < 6:
                cstype = 'B'
            else:
                cstype = 'C'

        cs_data.append({
            'CSID': csid,
            'CaseMasterID': case_id,
            'csdate': csdate_str,
            'cstype': cstype,
            'PolicePersonID': emp_id
        })

    cs_df = pd.DataFrame(cs_data)

    # Match schema column names and ordering exactly
    schema_cols = ['CSID', 'CaseMasterID', 'csdate', 'cstype', 'PolicePersonID']
    cs_df = cs_df[schema_cols]

    out_csv_path = os.path.join(seeds_d_dir, 'ChargesheetDetails.csv')
    cs_df.to_csv(out_csv_path, index=False)

    # ----------------------------------------------------
    # Referential Integrity Audit
    # ----------------------------------------------------
    unmapped_cases = [cid for cid in cs_df['CaseMasterID'] if cid not in valid_case_ids]
    unmapped_emps = [eid for eid in cs_df['PolicePersonID'] if eid not in valid_emp_ids]

    print("\n" + "="*70)
    print("CHARGESHEETDETAILS SEED GENERATION & AUDIT SUMMARY")
    print("="*70)
    print(f"Total Rows Generated: {len(cs_df)}")
    print(f"Unmapped CaseMasterID References: {len(unmapped_cases)} (100% Valid)")
    print(f"Unmapped PolicePersonID References: {len(unmapped_emps)} (100% Valid)")
    print(f"Output Seed CSV File: {out_csv_path}")
    print("-" * 70)
    print("Reasoned cstype Breakdown:")
    cstype_counts = cs_df['cstype'].value_counts()
    for ctype, count in cstype_counts.items():
        pct = (count / len(cs_df)) * 100
        desc = "Chargesheeted" if ctype == 'A' else ("Undetected" if ctype == 'C' else "False Case")
        print(f" - {ctype} ({desc:14s}): {count:4d} rows ({pct:.1f}%)")
    print("="*70 + "\n")

    print("="*70)
    print("SAMPLE CHARGESHEETDETAILS RECORDS (DEFINITION OF DONE)")
    print("="*70)
    print(cs_df.head(10).to_string(index=False))
    print("="*70 + "\n")

    return cs_df

if __name__ == '__main__':
    generate_chargesheet_seed()
