import os
import csv
import random

def generate_chargesheet_details():
    base_dir = os.path.dirname(__file__)
    casemaster_path = os.path.join(base_dir, "seeds", "batch_bc", "CaseMaster.csv")
    if not os.path.exists(casemaster_path):
        casemaster_path = os.path.join(base_dir, "..", "drishti_main", "seeds", "batch_bc", "CaseMaster.csv")

    rows = []
    with open(casemaster_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            case_id = int(row["CaseMasterID"])
            status_id = int(row.get("CaseStatusID", 1)) if row.get("CaseStatusID") else 1
            reg_date = row.get("CrimeRegisteredDate", "2025-06-01")
            
            # Distribution: A=Chargesheet, B=False Case, C=Undetected
            if status_id in [2, 3]:
                cstype = "A"
            elif status_id == 4:
                cstype = "B"
            elif status_id == 5:
                cstype = "C"
            else:
                # Random distribution: 80% A, 10% B, 10% C
                rand_val = random.random()
                if rand_val < 0.8:
                    cstype = "A"
                elif rand_val < 0.9:
                    cstype = "B"
                else:
                    cstype = "C"

            csdate = f"{reg_date} 10:00:00"
            police_person_id = (case_id % 50) + 1  # 1 to 50

            rows.append({
                "CSID": idx,
                "CaseMasterID": case_id,
                "csdate": csdate,
                "cstype": cstype,
                "PolicePersonID": police_person_id
            })

    output_dir = os.path.join(base_dir, "seeds", "batch_d")
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "ChargesheetDetails.csv")
    
    with open(out_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["CSID", "CaseMasterID", "csdate", "cstype", "PolicePersonID"])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Generated {len(rows)} ChargesheetDetails records to {out_file}")

if __name__ == "__main__":
    generate_chargesheet_details()
