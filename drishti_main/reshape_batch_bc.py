import os
import pandas as pd
import numpy as np

def reshape_batch_bc():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    seeds_a_dir = os.path.join(script_dir, 'seeds', 'batch_a')
    seeds_bc_dir = os.path.join(script_dir, 'seeds', 'batch_bc')
    os.makedirs(seeds_bc_dir, exist_ok=True)
    
    csv_path = os.path.join(script_dir, 'synthetic_incidents.csv')
    if not os.path.exists(csv_path):
        csv_path = os.path.join(project_dir, 'synthetic_incidents.csv')

    print(f"Loading Batch A seeds from: {seeds_a_dir}")
    print(f"Loading synthetic incidents from: {csv_path}")
    
    # ----------------------------------------------------
    # Load Batch A Lookup Tables
    # ----------------------------------------------------
    district_df = pd.read_csv(os.path.join(seeds_a_dir, 'District.csv'))
    crime_head_df = pd.read_csv(os.path.join(seeds_a_dir, 'CrimeHead.csv'))
    case_status_df = pd.read_csv(os.path.join(seeds_a_dir, 'CaseStatusMaster.csv'))
    state_df = pd.read_csv(os.path.join(seeds_a_dir, 'State.csv'))
    unit_type_df = pd.read_csv(os.path.join(seeds_a_dir, 'UnitType.csv'))
    rank_df = pd.read_csv(os.path.join(seeds_a_dir, 'Rank.csv'))
    designation_df = pd.read_csv(os.path.join(seeds_a_dir, 'Designation.csv'))
    case_cat_df = pd.read_csv(os.path.join(seeds_a_dir, 'CaseCategory.csv'))
    gravity_df = pd.read_csv(os.path.join(seeds_a_dir, 'GravityOffence.csv'))
    crime_sub_head_df = pd.read_csv(os.path.join(seeds_a_dir, 'CrimeSubHead.csv'))
    caste_df = pd.read_csv(os.path.join(seeds_a_dir, 'CasteMaster.csv'))
    religion_df = pd.read_csv(os.path.join(seeds_a_dir, 'ReligionMaster.csv'))
    occupation_df = pd.read_csv(os.path.join(seeds_a_dir, 'OccupationMaster.csv'))
    act_df = pd.read_csv(os.path.join(seeds_a_dir, 'Act.csv'))
    section_df = pd.read_csv(os.path.join(seeds_a_dir, 'Section.csv'))
    
    # Build maps
    district_name_to_id = dict(zip(district_df['DistrictName'], district_df['DistrictID']))
    crime_head_to_id = dict(zip(crime_head_df['CrimeGroupName'], crime_head_df['CrimeHeadID']))
    case_status_to_id = dict(zip(case_status_df['CaseStatusName'], case_status_df['CaseStatusID']))
    
    df = pd.read_csv(csv_path)
    
    # ----------------------------------------------------
    # FK Verification for Input Dataset against Batch A
    # ----------------------------------------------------
    unresolved_districts = [d for d in df['district'].dropna().unique() if d not in district_name_to_id]
    unresolved_crimes = [c for c in df['crime_type'].dropna().unique() if c not in crime_head_to_id]
    unresolved_statuses = [s for s in df['status'].dropna().unique() if s not in case_status_to_id]
    
    print("\n" + "="*60)
    print("INPUT FK RESOLUTION VALIDATION (BEFORE GENERATION)")
    print("="*60)
    print(f"Unresolved Districts: {unresolved_districts if unresolved_districts else 'None (100% Resolved)'}")
    print(f"Unresolved Crime Heads: {unresolved_crimes if unresolved_crimes else 'None (100% Resolved)'}")
    print(f"Unresolved Case Statuses: {unresolved_statuses if unresolved_statuses else 'None (100% Resolved)'}")
    print("="*60 + "\n")
    
    if unresolved_districts or unresolved_crimes or unresolved_statuses:
        raise ValueError("Cannot proceed with Batch B/C generation: Unresolved Batch A FK references found!")

    # ----------------------------------------------------
    # Batch B1: Unit (Police Stations)
    # ----------------------------------------------------
    units_data = []
    unit_id_map = {} # DistrictID -> UnitID
    for idx, row in district_df.iterrows():
        uid = idx + 1
        did = row['DistrictID']
        dname = row['DistrictName']
        unit_id_map[did] = uid
        units_data.append({
            'UnitID': uid,
            'UnitName': f"{dname} Town Police Station",
            'TypeID': 1, # Police Station
            'ParentUnit': 0,
            'NationalityID': 1,
            'StateID': 1,
            'DistrictID': did,
            'Active': True
        })
    unit_df = pd.DataFrame(units_data)
    unit_df.to_csv(os.path.join(seeds_bc_dir, 'Unit.csv'), index=False)

    # ----------------------------------------------------
    # Batch B2: Court
    # ----------------------------------------------------
    court_data = []
    court_id_map = {} # DistrictID -> CourtID
    for idx, row in district_df.iterrows():
        cid = idx + 1
        did = row['DistrictID']
        dname = row['DistrictName']
        court_id_map[did] = cid
        court_data.append({
            'CourtID': cid,
            'CourtName': f"District and Sessions Court, {dname}",
            'DistrictID': did,
            'StateID': 1,
            'Active': True
        })
    court_df = pd.DataFrame(court_data)
    court_df.to_csv(os.path.join(seeds_bc_dir, 'Court.csv'), index=False)

    # ----------------------------------------------------
    # Batch B3: Employee
    # ----------------------------------------------------
    employees_data = []
    unit_to_employee_ids = {} # UnitID -> list of EmployeeIDs
    emp_id_counter = 1
    
    first_names = ["Ramesh", "Suresh", "Mahesh", "Ganesh", "Prakash", "Venkatesh", "Manjunath", "Basavaraj", "Anand", "Vijay"]
    last_names = ["Kumar", "Patil", "Gowda", "Naik", "Rao", "Shetty", "Hegde", "Deshmukh", "Pujari", "Kulkarni"]
    
    for uid, urow in unit_df.iterrows():
        unit_id = urow['UnitID']
        dist_id = urow['DistrictID']
        unit_to_employee_ids[unit_id] = []
        
        # Create 2 officers per station (SHO & IO)
        for officer_idx in range(2):
            emp_id = emp_id_counter
            emp_id_counter += 1
            unit_to_employee_ids[unit_id].append(emp_id)
            
            fn = first_names[(emp_id - 1) % len(first_names)]
            ln = last_names[(emp_id * 3) % len(last_names)]
            full_name = f"{fn} {ln}"
            
            rank_id = 4 if officer_idx == 0 else 3 # SI or ASI
            desig_id = 1 if officer_idx == 0 else 2 # SHO or IO
            
            employees_data.append({
                'EmployeeID': emp_id,
                'DistrictID': dist_id,
                'UnitID': unit_id,
                'RankID': rank_id,
                'DesignationID': desig_id,
                'KGID': f"KGID{10000 + emp_id}",
                'FirstName': full_name,
                'EmployeeDOB': f"198{emp_id % 10}-0{ (emp_id % 9) + 1 }-15",
                'GenderID': 1,
                'BloodGroupID': 1,
                'PhysicallyChallenged': False,
                'AppointmentDate': f"201{emp_id % 9}-0{ (emp_id % 9) + 1 }-01"
            })
            
    employee_df = pd.DataFrame(employees_data)
    employee_df.to_csv(os.path.join(seeds_bc_dir, 'Employee.csv'), index=False)

    # ----------------------------------------------------
    # Batch C1: CaseMaster
    # ----------------------------------------------------
    case_master_data = []
    complainants_data = []
    victims_data = []
    accused_data = []
    act_sec_assoc_data = []

    # Prepare repeat offender names pool for Accused table link analysis (plain realistic names only)
    repeat_offenders = [
        ("Ramesh Gowda", "REC_OFF_001"),
        ("Kiran Kumar", "REC_OFF_002"),
        ("Manjunath Naik", "REC_OFF_003"),
        ("Venkatesh Rao", "REC_OFF_004"),
        ("Basavaraj Patil", "REC_OFF_005"),
        ("Anand Kulkarni", "REC_OFF_006"),
        ("Sunil Shetty", "REC_OFF_007"),
        ("Pradeep Deshmukh", "REC_OFF_008"),
        ("Dharmesh Pujari", "REC_OFF_009"),
        ("Ganesh Hegde", "REC_OFF_010")
    ]

    comp_first_names = ["Priya", "Rahul", "Deepak", "Aisha", "Siddharth", "Meena", "Kavita", "Sanjay", "Rajesh", "Anita"]
    comp_last_names = ["Sharma", "Verma", "Joshi", "Nair", "Reddy", "Chavan", "Bhat", "Menon", "Singh", "Das"]
    accused_first_names = ["Suresh", "Vijay", "Ramesh", "Mahesh", "Ganesh", "Prakash", "Dinesh", "Naveen", "Satish", "Ashok", "Lokesh", "Kishore", "Santosh", "Ravi", "Harish"]

    for idx, row in df.iterrows():
        case_id = int(row['incident_id'])
        dist_name = row['district']
        crime_name = row['crime_type']
        status_name = row['status']
        lat = float(row['latitude'])
        lng = float(row['longitude'])
        date_str = str(row['date'])
        hour_val = int(row['hour'])

        dist_id = district_name_to_id[dist_name]
        unit_id = unit_id_map[dist_id]
        court_id = court_id_map[dist_id]
        assigned_emp_id = unit_to_employee_ids[unit_id][case_id % len(unit_to_employee_ids[unit_id])]
        
        crime_head_id = crime_head_to_id[crime_name]
        status_id = case_status_to_id[status_name]
        
        # Gravity offence (Robbery/Assault = Heinous (1), others Non-Heinous (2))
        gravity_id = 1 if crime_name in ['Robbery', 'Assault'] else 2
        
        # Minor head (1 for General, 2 for Aggravated)
        minor_head_id = (crime_head_id - 1) * 2 + (1 if case_id % 2 == 0 else 2)

        # Datetime formatting (YYYY-MM-DD HH:MM:SS)
        inc_from = f"{date_str} {hour_val:02d}:00:00"
        inc_to = f"{date_str} {hour_val:02d}:30:00"
        info_rec = f"{date_str} {min(hour_val + 1, 23):02d}:15:00"

        case_master_data.append({
            'CaseMasterID': case_id,
            'CrimeNo': f"{case_id:04d}/2025",
            'CaseNo': f"FIR/{case_id:04d}/2025",
            'CrimeRegisteredDate': date_str,
            'PolicePersonID': assigned_emp_id,
            'PoliceStationID': unit_id,
            'CaseCategoryID': 1, # FIR
            'GravityOffenceID': gravity_id,
            'CrimeMajorHeadID': crime_head_id,
            'CrimeMinorHeadID': minor_head_id,
            'CaseStatusID': status_id,
            'CourtID': court_id,
            'IncidentFromDate': inc_from,
            'IncidentToDate': inc_to,
            'InfoReceivedPSDate': info_rec,
            'latitude': lat,
            'longitude': lng,
            'BriefFacts': f"Incident of {crime_name} reported in {dist_name} district at coordinates ({lat:.4f}, {lng:.4f})."
        })

        # ----------------------------------------------------
        # Batch C2: ComplainantDetails
        # ----------------------------------------------------
        c_fn = comp_first_names[case_id % len(comp_first_names)]
        c_ln = comp_last_names[(case_id * 2) % len(comp_last_names)]
        complainants_data.append({
            'ComplainantID': case_id,
            'CaseMasterID': case_id,
            'ComplainantName': f"{c_fn} {c_ln}",
            'AgeYear': 22 + (case_id % 45),
            'OccupationID': (case_id % 8) + 1,
            'ReligionID': (case_id % 7) + 1,
            'CasteID': (case_id % 5) + 1,
            'GenderID': 1 if case_id % 2 == 0 else 2
        })

        # ----------------------------------------------------
        # Batch C3: Victim
        # ----------------------------------------------------
        v_fn = comp_first_names[(case_id + 3) % len(comp_first_names)]
        v_ln = comp_last_names[(case_id * 3) % len(comp_last_names)]
        victims_data.append({
            'VictimMasterID': case_id,
            'CaseMasterID': case_id,
            'VictimName': f"{v_fn} {v_ln}",
            'AgeYear': 18 + (case_id % 50),
            'GenderID': 2 if case_id % 2 == 0 else 1,
            'VictimPolice': False
        })

        # ----------------------------------------------------
        # Batch C4: Accused (Seeding repeat offenders for link analysis)
        # ----------------------------------------------------
        # 15% of cases involve repeat offenders across districts to enable rich network graph joins
        if case_id % 7 == 0:
            ro_name, ro_pid = repeat_offenders[case_id % len(repeat_offenders)]
            accused_name = ro_name
            person_id = ro_pid
        else:
            a_fn = accused_first_names[(case_id * 3) % len(accused_first_names)]
            a_ln = comp_last_names[(case_id * 5) % len(comp_last_names)]
            accused_name = f"{a_fn} {a_ln}"
            person_id = f"A{case_id:04d}"

        accused_data.append({
            'AccusedMasterID': case_id,
            'CaseMasterID': case_id,
            'AccusedName': accused_name,
            'AgeYear': 20 + (case_id % 35),
            'GenderID': 1,
            'PersonID': person_id
        })

        # ----------------------------------------------------
        # Batch C5: ActSectionAssociation
        # ----------------------------------------------------
        act_sec_assoc_data.append({
            'CaseMasterID': case_id,
            'ActID': 1, # BNS
            'SectionID': 303 if crime_name == 'Theft' else (309 if crime_name == 'Robbery' else 115),
            'ActOrderID': 1,
            'SectionOrderID': 1
        })

    # Save Batch C DataFrames to CSV
    case_master_df = pd.DataFrame(case_master_data)
    case_master_df.to_csv(os.path.join(seeds_bc_dir, 'CaseMaster.csv'), index=False)

    complainant_df = pd.DataFrame(complainants_data)
    complainant_df.to_csv(os.path.join(seeds_bc_dir, 'ComplainantDetails.csv'), index=False)

    victim_df = pd.DataFrame(victims_data)
    victim_df.to_csv(os.path.join(seeds_bc_dir, 'Victim.csv'), index=False)

    accused_df = pd.DataFrame(accused_data)
    accused_df.to_csv(os.path.join(seeds_bc_dir, 'Accused.csv'), index=False)

    act_sec_assoc_df = pd.DataFrame(act_sec_assoc_data)
    act_sec_assoc_df.to_csv(os.path.join(seeds_bc_dir, 'ActSectionAssociation.csv'), index=False)

    # CrimeHeadActSection
    crime_head_act_sec_data = [
        {'CrimeHeadID': 1, 'ActCode': 'BNS', 'SectionCode': '303'},
        {'CrimeHeadID': 2, 'ActCode': 'BNS', 'SectionCode': '309'},
        {'CrimeHeadID': 3, 'ActCode': 'BNS', 'SectionCode': '305'},
        {'CrimeHeadID': 4, 'ActCode': 'BNS', 'SectionCode': '331'},
        {'CrimeHeadID': 5, 'ActCode': 'BNS', 'SectionCode': '115'},
    ]
    crime_head_act_sec_df = pd.DataFrame(crime_head_act_sec_data)
    crime_head_act_sec_df.to_csv(os.path.join(seeds_bc_dir, 'CrimeHeadActSection.csv'), index=False)

    # ----------------------------------------------------
    # REFERENTIAL INTEGRITY AUDIT (DEFINTION OF DONE)
    # ----------------------------------------------------
    audit_results = []

    def verify_fk(table_name, col_name, valid_set, ref_table_name):
        df_target = pd.read_csv(os.path.join(seeds_bc_dir, f"{table_name}.csv"))
        missing = [val for val in df_target[col_name].dropna().unique() if val not in valid_set]
        status = "PASSED (100% Resolved)" if len(missing) == 0 else f"FAILED ({len(missing)} missing)"
        audit_results.append({
            'Table': table_name,
            'FK Column': col_name,
            'Referenced Table': ref_table_name,
            'Status': status
        })

    verify_fk('Unit', 'DistrictID', set(district_df['DistrictID']), 'District')
    verify_fk('Unit', 'StateID', set(state_df['StateID']), 'State')
    verify_fk('Unit', 'TypeID', set(unit_type_df['UnitTypeID']), 'UnitType')

    verify_fk('Court', 'DistrictID', set(district_df['DistrictID']), 'District')
    verify_fk('Court', 'StateID', set(state_df['StateID']), 'State')

    verify_fk('Employee', 'DistrictID', set(district_df['DistrictID']), 'District')
    verify_fk('Employee', 'UnitID', set(unit_df['UnitID']), 'Unit')
    verify_fk('Employee', 'RankID', set(rank_df['RankID']), 'Rank')
    verify_fk('Employee', 'DesignationID', set(designation_df['DesignationID']), 'Designation')

    verify_fk('CaseMaster', 'PoliceStationID', set(unit_df['UnitID']), 'Unit')
    verify_fk('CaseMaster', 'PolicePersonID', set(employee_df['EmployeeID']), 'Employee')
    verify_fk('CaseMaster', 'CaseCategoryID', set(case_cat_df['CaseCategoryID']), 'CaseCategory')
    verify_fk('CaseMaster', 'GravityOffenceID', set(gravity_df['GravityOffenceID']), 'GravityOffence')
    verify_fk('CaseMaster', 'CrimeMajorHeadID', set(crime_head_df['CrimeHeadID']), 'CrimeHead')
    verify_fk('CaseMaster', 'CrimeMinorHeadID', set(crime_sub_head_df['CrimeSubHeadID']), 'CrimeSubHead')
    verify_fk('CaseMaster', 'CaseStatusID', set(case_status_df['CaseStatusID']), 'CaseStatusMaster')
    verify_fk('CaseMaster', 'CourtID', set(court_df['CourtID']), 'Court')

    verify_fk('ComplainantDetails', 'CaseMasterID', set(case_master_df['CaseMasterID']), 'CaseMaster')
    verify_fk('ComplainantDetails', 'OccupationID', set(occupation_df['OccupationID']), 'OccupationMaster')
    verify_fk('ComplainantDetails', 'ReligionID', set(religion_df['ReligionID']), 'ReligionMaster')
    verify_fk('ComplainantDetails', 'CasteID', set(caste_df['caste_master_id']), 'CasteMaster')

    verify_fk('Victim', 'CaseMasterID', set(case_master_df['CaseMasterID']), 'CaseMaster')
    verify_fk('Accused', 'CaseMasterID', set(case_master_df['CaseMasterID']), 'CaseMaster')

    print("\n" + "="*70)
    print("REFERENTIAL INTEGRITY AUDIT RESULTS (DEFINITION OF DONE)")
    print("="*70)
    for res in audit_results:
        print(f" - {res['Table']}.{res['FK Column']} -> {res['Referenced Table']} : {res['Status']}")
    print("="*70 + "\n")

    row_counts = {
        'Unit': len(unit_df),
        'Court': len(court_df),
        'Employee': len(employee_df),
        'CaseMaster': len(case_master_df),
        'ComplainantDetails': len(complainant_df),
        'Victim': len(victim_df),
        'Accused': len(accused_df),
        'ActSectionAssociation': len(act_sec_assoc_df),
        'CrimeHeadActSection': len(crime_head_act_sec_df)
    }

    print("\n" + "="*60)
    print("GENERATED BATCH B/C CSV FILES & ROW COUNTS")
    print("="*60)
    for tname, rcount in row_counts.items():
        print(f" - {tname}.csv : {rcount} rows")
    print("="*60 + "\n")

    return row_counts, audit_results

if __name__ == '__main__':
    reshape_batch_bc()
