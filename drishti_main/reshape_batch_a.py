import os
import json
import pandas as pd

def reshape_batch_a():
    # Base paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    csv_path = os.path.join(script_dir, 'synthetic_incidents.csv')
    if not os.path.exists(csv_path):
        csv_path = os.path.join(project_dir, 'synthetic_incidents.csv')
        
    geojson_path = os.path.join(script_dir, 'karnataka_districts.geojson')
    if not os.path.exists(geojson_path):
        geojson_path = os.path.join(project_dir, 'karnataka_districts.geojson')
        
    output_dir = os.path.join(script_dir, 'seeds', 'batch_a')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading CSV from: {csv_path}")
    print(f"Loading GeoJSON from: {geojson_path}")
    
    df = pd.read_csv(csv_path)
    
    # ----------------------------------------------------
    # Constraint Check: District Names vs GeoJSON
    # ----------------------------------------------------
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
        
    geojson_districts = set()
    for feat in geojson_data.get('features', []):
        props = feat.get('properties', {})
        name = props.get('district') or props.get('district_name') or props.get('dtname') or props.get('NAME_2') or props.get('name')
        if name:
            geojson_districts.add(name)
            
    csv_districts = sorted(df['district'].dropna().unique().tolist())
    
    mismatches = [d for d in csv_districts if d not in geojson_districts]
    
    print("\n" + "="*60)
    print("DISTRICT NAME CROSS-CHECK RESULTS")
    print("="*60)
    print(f"Total Unique Districts in CSV: {len(csv_districts)}")
    print(f"Total Unique Districts in GeoJSON: {len(geojson_districts)}")
    print(f"Number of District Name Mismatches: {len(mismatches)}")
    print("-" * 60)
    print("Mismatched District Names (in CSV, but no exact match in GeoJSON):")
    for m in mismatches:
        print(f" - {m}")
    print("="*60 + "\n")
    
    # ----------------------------------------------------
    # Batch A Table Reshaping & Seed CSV Generation
    # ----------------------------------------------------
    row_counts = {}

    # 1. State
    state_df = pd.DataFrame([
        {'StateID': 1, 'StateName': 'Karnataka', 'NationalityID': 1, 'Active': True}
    ])
    state_df.to_csv(os.path.join(output_dir, 'State.csv'), index=False)
    row_counts['State'] = len(state_df)

    # 2. District
    district_df = pd.DataFrame([
        {'DistrictID': idx + 1, 'DistrictName': dist_name, 'StateID': 1, 'Active': True}
        for idx, dist_name in enumerate(csv_districts)
    ])
    district_df.to_csv(os.path.join(output_dir, 'District.csv'), index=False)
    row_counts['District'] = len(district_df)

    # 3. UnitType
    unit_type_data = [
        {'UnitTypeID': 1, 'UnitTypeName': 'Police Station', 'CityDistState': 'City', 'Hierarchy': 1, 'Active': True},
        {'UnitTypeID': 2, 'UnitTypeName': 'Circle Office', 'CityDistState': 'District', 'Hierarchy': 2, 'Active': True},
        {'UnitTypeID': 3, 'UnitTypeName': 'Sub-Division Office', 'CityDistState': 'District', 'Hierarchy': 3, 'Active': True},
        {'UnitTypeID': 4, 'UnitTypeName': 'District Police Office', 'CityDistState': 'District', 'Hierarchy': 4, 'Active': True},
        {'UnitTypeID': 5, 'UnitTypeName': 'Commissionerate / State HQ', 'CityDistState': 'State', 'Hierarchy': 5, 'Active': True}
    ]
    unit_type_df = pd.DataFrame(unit_type_data)
    unit_type_df.to_csv(os.path.join(output_dir, 'UnitType.csv'), index=False)
    row_counts['UnitType'] = len(unit_type_df)

    # 4. Rank
    rank_data = [
        {'RankID': 1, 'RankName': 'Constable', 'Hierarchy': 1, 'Active': True},
        {'RankID': 2, 'RankName': 'Head Constable', 'Hierarchy': 2, 'Active': True},
        {'RankID': 3, 'RankName': 'Assistant Sub-Inspector (ASI)', 'Hierarchy': 3, 'Active': True},
        {'RankID': 4, 'RankName': 'Sub-Inspector (SI)', 'Hierarchy': 4, 'Active': True},
        {'RankID': 5, 'RankName': 'Inspector of Police', 'Hierarchy': 5, 'Active': True},
        {'RankID': 6, 'RankName': 'Deputy Superintendent of Police (DSP)', 'Hierarchy': 6, 'Active': True},
        {'RankID': 7, 'RankName': 'Superintendent of Police (SP)', 'Hierarchy': 7, 'Active': True}
    ]
    rank_df = pd.DataFrame(rank_data)
    rank_df.to_csv(os.path.join(output_dir, 'Rank.csv'), index=False)
    row_counts['Rank'] = len(rank_df)

    # 5. Designation
    designation_data = [
        {'DesignationID': 1, 'DesignationName': 'Station House Officer', 'Active': True, 'SortOrder': 1},
        {'DesignationID': 2, 'DesignationName': 'Investigating Officer', 'Active': True, 'SortOrder': 2},
        {'DesignationID': 3, 'DesignationName': 'Station Writer', 'Active': True, 'SortOrder': 3},
        {'DesignationID': 4, 'DesignationName': 'Law & Order In-charge', 'Active': True, 'SortOrder': 4},
        {'DesignationID': 5, 'DesignationName': 'Crime Branch In-charge', 'Active': True, 'SortOrder': 5}
    ]
    designation_df = pd.DataFrame(designation_data)
    designation_df.to_csv(os.path.join(output_dir, 'Designation.csv'), index=False)
    row_counts['Designation'] = len(designation_df)

    # 6. CaseCategory
    case_cat_data = [
        {'CaseCategoryID': 1, 'LookupValue': 'FIR'},
        {'CaseCategoryID': 2, 'LookupValue': 'UDR'},
        {'CaseCategoryID': 3, 'LookupValue': 'PAR'},
        {'CaseCategoryID': 4, 'LookupValue': 'Zero FIR'}
    ]
    case_cat_df = pd.DataFrame(case_cat_data)
    case_cat_df.to_csv(os.path.join(output_dir, 'CaseCategory.csv'), index=False)
    row_counts['CaseCategory'] = len(case_cat_df)

    # 7. GravityOffence
    gravity_df = pd.DataFrame([
        {'GravityOffenceID': 1, 'LookupValue': 'Heinous'},
        {'GravityOffenceID': 2, 'LookupValue': 'Non-Heinous'}
    ])
    gravity_df.to_csv(os.path.join(output_dir, 'GravityOffence.csv'), index=False)
    row_counts['GravityOffence'] = len(gravity_df)

    # 8. CrimeHead
    csv_crime_types = sorted(df['crime_type'].dropna().unique().tolist())
    crime_head_df = pd.DataFrame([
        {'CrimeHeadID': idx + 1, 'CrimeGroupName': cname, 'Active': True}
        for idx, cname in enumerate(csv_crime_types)
    ])
    crime_head_df.to_csv(os.path.join(output_dir, 'CrimeHead.csv'), index=False)
    row_counts['CrimeHead'] = len(crime_head_df)

    # 9. CrimeSubHead
    crime_sub_head_data = []
    sub_head_id = 1
    for ch_idx, cname in enumerate(csv_crime_types):
        ch_id = ch_idx + 1
        crime_sub_head_data.append({
            'CrimeSubHeadID': sub_head_id,
            'CrimeHeadID': ch_id,
            'CrimeHeadName': f"{cname} - General",
            'SeqID': 1
        })
        sub_head_id += 1
        crime_sub_head_data.append({
            'CrimeSubHeadID': sub_head_id,
            'CrimeHeadID': ch_id,
            'CrimeHeadName': f"{cname} - Aggravated / Organized",
            'SeqID': 2
        })
        sub_head_id += 1

    crime_sub_head_df = pd.DataFrame(crime_sub_head_data)
    crime_sub_head_df.to_csv(os.path.join(output_dir, 'CrimeSubHead.csv'), index=False)
    row_counts['CrimeSubHead'] = len(crime_sub_head_df)

    # 10. CaseStatusMaster
    csv_statuses = sorted(df['status'].dropna().unique().tolist())
    case_status_df = pd.DataFrame([
        {'CaseStatusID': idx + 1, 'CaseStatusName': sname}
        for idx, sname in enumerate(csv_statuses)
    ])
    case_status_df.to_csv(os.path.join(output_dir, 'CaseStatusMaster.csv'), index=False)
    row_counts['CaseStatusMaster'] = len(case_status_df)

    # 11. CasteMaster
    caste_df = pd.DataFrame([
        {'caste_master_id': 1, 'caste_master_name': 'General'},
        {'caste_master_id': 2, 'caste_master_name': 'OBC'},
        {'caste_master_id': 3, 'caste_master_name': 'Scheduled Caste (SC)'},
        {'caste_master_id': 4, 'caste_master_name': 'Scheduled Tribe (ST)'},
        {'caste_master_id': 5, 'caste_master_name': 'Others'}
    ])
    caste_df.to_csv(os.path.join(output_dir, 'CasteMaster.csv'), index=False)
    row_counts['CasteMaster'] = len(caste_df)

    # 12. ReligionMaster
    religion_df = pd.DataFrame([
        {'ReligionID': 1, 'ReligionName': 'Hindu'},
        {'ReligionID': 2, 'ReligionName': 'Muslim'},
        {'ReligionID': 3, 'ReligionName': 'Christian'},
        {'ReligionID': 4, 'ReligionName': 'Sikh'},
        {'ReligionID': 5, 'ReligionName': 'Jain'},
        {'ReligionID': 6, 'ReligionName': 'Buddhist'},
        {'ReligionID': 7, 'ReligionName': 'Others'}
    ])
    religion_df.to_csv(os.path.join(output_dir, 'ReligionMaster.csv'), index=False)
    row_counts['ReligionMaster'] = len(religion_df)

    # 13. OccupationMaster
    occupation_df = pd.DataFrame([
        {'OccupationID': 1, 'OccupationName': 'Farmer / Agriculturist'},
        {'OccupationID': 2, 'OccupationName': 'Business / Self-Employed'},
        {'OccupationID': 3, 'OccupationName': 'Private Employee'},
        {'OccupationID': 4, 'OccupationName': 'Government Employee'},
        {'OccupationID': 5, 'OccupationName': 'Student'},
        {'OccupationID': 6, 'OccupationName': 'Unemployed'},
        {'OccupationID': 7, 'OccupationName': 'Daily Wage Labourer'},
        {'OccupationID': 8, 'OccupationName': 'Others'}
    ])
    occupation_df.to_csv(os.path.join(output_dir, 'OccupationMaster.csv'), index=False)
    row_counts['OccupationMaster'] = len(occupation_df)

    # 14. Act
    act_df = pd.DataFrame([
        {'ActCode': 'BNS', 'ActDescription': 'Bharatiya Nyaya Sanhita 2023', 'ShortName': 'BNS', 'Active': True},
        {'ActCode': 'IPC', 'ActDescription': 'Indian Penal Code 1860', 'ShortName': 'IPC', 'Active': True},
        {'ActCode': 'IT_ACT', 'ActDescription': 'Information Technology Act 2000', 'ShortName': 'IT Act', 'Active': True},
        {'ActCode': 'NDPS', 'ActDescription': 'Narcotic Drugs and Psychotropic Substances Act 1985', 'ShortName': 'NDPS Act', 'Active': True}
    ])
    act_df.to_csv(os.path.join(output_dir, 'Act.csv'), index=False)
    row_counts['Act'] = len(act_df)

    # 15. Section
    section_df = pd.DataFrame([
        {'ActCode': 'BNS', 'SectionCode': '303', 'SectionDescription': 'Theft (BNS 303)', 'Active': True},
        {'ActCode': 'BNS', 'SectionCode': '309', 'SectionDescription': 'Robbery (BNS 309)', 'Active': True},
        {'ActCode': 'BNS', 'SectionCode': '305', 'SectionDescription': 'Theft in dwelling house (BNS 305)', 'Active': True},
        {'ActCode': 'BNS', 'SectionCode': '331', 'SectionDescription': 'Lurking house-trespass or house-breaking (BNS 331)', 'Active': True},
        {'ActCode': 'BNS', 'SectionCode': '115', 'SectionDescription': 'Voluntarily causing hurt (BNS 115)', 'Active': True},
        {'ActCode': 'IPC', 'SectionCode': '379', 'SectionDescription': 'Theft (IPC 379)', 'Active': True},
        {'ActCode': 'IPC', 'SectionCode': '392', 'SectionDescription': 'Robbery (IPC 392)', 'Active': True},
        {'ActCode': 'IPC', 'SectionCode': '380', 'SectionDescription': 'Theft in dwelling house (IPC 380)', 'Active': True},
        {'ActCode': 'IPC', 'SectionCode': '457', 'SectionDescription': 'Lurking house-trespass or house-breaking by night (IPC 457)', 'Active': True},
        {'ActCode': 'IPC', 'SectionCode': '323', 'SectionDescription': 'Voluntarily causing hurt (IPC 323)', 'Active': True}
    ])
    section_df.to_csv(os.path.join(output_dir, 'Section.csv'), index=False)
    row_counts['Section'] = len(section_df)

    print("\n" + "="*60)
    print("OUTPUT CSV FILES AND ROW COUNTS (BATCH A LOOKUP TABLES)")
    print("="*60)
    for tname, rcount in row_counts.items():
        print(f" - {tname}.csv : {rcount} rows")
    print("="*60 + "\n")
    
    return mismatches, row_counts

if __name__ == '__main__':
    reshape_batch_a()
