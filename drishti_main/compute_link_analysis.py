import os
import json
import pandas as pd

def compute_link_analysis():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    seeds_bc_dir = os.path.join(script_dir, 'seeds', 'batch_bc')
    if not os.path.exists(seeds_bc_dir):
        seeds_bc_dir = os.path.join(project_dir, 'drishti_main', 'seeds', 'batch_bc')

    seeds_e_dir = os.path.join(script_dir, 'seeds', 'batch_e')
    os.makedirs(seeds_e_dir, exist_ok=True)

    accused_df = pd.read_csv(os.path.join(seeds_bc_dir, 'Accused.csv'))
    case_master_df = pd.read_csv(os.path.join(seeds_bc_dir, 'CaseMaster.csv'))
    victim_df = pd.read_csv(os.path.join(seeds_bc_dir, 'Victim.csv'))

    # Identify repeat offenders (same AccusedName across multiple CaseMasterIDs)
    acc_counts = accused_df['AccusedName'].value_counts()
    repeat_offender_names = acc_counts[acc_counts > 1].index.tolist()

    nodes = []
    edges = []
    node_set = set()

    # Create network graph for sample repeat offenders
    for off_name in repeat_offender_names[:10]:
        acc_cases = accused_df[accused_df['AccusedName'] == off_name]
        
        # Accused Node
        acc_node_id = f"acc_{off_name.replace(' ', '_')}"
        if acc_node_id not in node_set:
            nodes.append({
                "id": acc_node_id,
                "label": off_name,
                "type": "Accused",
                "person_id": acc_cases.iloc[0]['PersonID']
            })
            node_set.add(acc_node_id)

        for _, acc_row in acc_cases.iterrows():
            cid = int(acc_row['CaseMasterID'])
            case_row = case_master_df[case_master_df['CaseMasterID'] == cid].iloc[0]
            
            # Case Node
            case_node_id = f"case_{cid}"
            if case_node_id not in node_set:
                nodes.append({
                    "id": case_node_id,
                    "label": f"FIR {case_row['CaseNo']}",
                    "type": "CaseMaster",
                    "crime_head_id": int(case_row['CrimeMajorHeadID']),
                    "district_id": int(case_row['DistrictID']) if 'DistrictID' in case_row else 1,
                    "lat": float(case_row['latitude']),
                    "lng": float(case_row['longitude'])
                })
                node_set.add(case_node_id)

            # Edge between Accused and Case
            edges.append({
                "source": acc_node_id,
                "target": case_node_id,
                "relation": "CHARGED_IN"
            })

            # Associated Victims
            v_rows = victim_df[victim_df['CaseMasterID'] == cid]
            for _, v_row in v_rows.iterrows():
                v_name = v_row['VictimName']
                v_node_id = f"vic_{v_name.replace(' ', '_')}"
                if v_node_id not in node_set:
                    nodes.append({
                        "id": v_node_id,
                        "label": v_name,
                        "type": "Victim"
                    })
                    node_set.add(v_node_id)

                edges.append({
                    "source": case_node_id,
                    "target": v_node_id,
                    "relation": "VICTIM_OF"
                })

    graph_data = {
        "summary": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "repeat_offenders_count": len(repeat_offender_names)
        },
        "nodes": nodes,
        "edges": edges
    }

    out_json_path = os.path.join(seeds_e_dir, 'network_graph.json')
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=2)

    print("\n" + "="*70)
    print("NETWORK / LINK ANALYSIS SUMMARY")
    print("="*70)
    print(f"Total Repeat Offenders Found in Seed Data: {len(repeat_offender_names)}")
    print(f"Graph Nodes Created: {len(nodes)}")
    print(f"Graph Edges Created: {len(edges)}")
    print(f"Output Graph File: {out_json_path}")
    print("="*70 + "\n")

    return graph_data

if __name__ == '__main__':
    compute_link_analysis()
