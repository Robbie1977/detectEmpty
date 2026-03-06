#!/usr/bin/env python3
"""
Full KB Empty Folder Analysis with Issue Detection

This script:
1. Analyzes all 331,182 Male CNS folders
2. Detects empty folder patterns with fixed threshold logic
3. Flags any anomalies (e.g., both templates empty)
4. Generates comprehensive report
"""

import json
import sys
import time
from datetime import datetime
from collections import defaultdict
from kb_block_empty_images import (
    neo4j_query, get_wlz_size, is_empty_folder, EMPTY_SIGNATURES
)

def main():
    print("\n" + "="*80)
    print("VFB KB FULL ANALYSIS - Empty Folder Detection (All 331,182 Folders)")
    print("="*80 + "\n")
    
    start_time = time.time()
    
    try:
        # Connect to KB
        print("[INFO] Connecting to VFB Knowledge Base...")
        
        # Query for all MaleCNS individuals and their registrations
        query = """MATCH (n:Individual)-[r:in_register_with]->(tc:Template) 
                   WHERE n.label contains 'MaleCNS' 
                   RETURN distinct n.short_form as short_form, 
                                   n.label as label, 
                                   r.folder[0] as folder, 
                                   tc.short_form as template_id"""
        
        print("[INFO] Querying KB for all MaleCNS registrations...")
        registrations = neo4j_query(query)
        print(f"[OK] Found {len(registrations)} total registrations\n")
        
        # Track unique folders
        unique_folders = set()
        folder_templates = defaultdict(set)
        
        for reg in registrations:
            folder_key = (reg[2], reg[3])  # folder_url, template_id
            unique_folders.add(folder_key)
            folder_templates[reg[2]].add(reg[3])  # Track templates per folder
        
        print(f"[INFO] Processing {len(unique_folders)} unique folder-template pairs\n")
        
        # Analyze each folder
        empty_records = []
        checked_count = 0
        failed_count = 0
        empty_count = 0
        both_empty_count = 0
        
        # Track issues
        issues = {
            'both_empty_folders': [],
            'unreachable': [],
            'size_anomalies': []
        }
        
        for folder_url, template_ids in sorted(folder_templates.items()):
            for template_id in template_ids:
                checked_count += 1
                
                # Progress updates every 1000 folders
                if checked_count % 1000 == 0:
                    elapsed = time.time() - start_time
                    rate = checked_count / elapsed
                    remaining = (len(unique_folders) - checked_count) / rate if rate > 0 else 0
                    print(f"[PROGRESS] {checked_count:7d}/{len(unique_folders):7d} folders checked "
                          f"({empty_count:6d} empty) - "
                          f"Rate: {rate:.1f}/sec, ETA: {remaining/3600:.1f}h")
                
                is_empty, is_reachable = is_empty_folder(folder_url, template_id)
                
                if not is_reachable:
                    failed_count += 1
                    issues['unreachable'].append({
                        'folder': folder_url,
                        'template': template_id
                    })
                elif is_empty:
                    empty_count += 1
                    
                    # Get file size for analysis
                    wlz_size = get_wlz_size(folder_url)
                    folder_name = folder_url.split('/')[-3]
                    
                    # Find the individual(s) with this registration
                    for reg in registrations:
                        if reg[2] == folder_url and reg[3] == template_id:
                            empty_records.append({
                                'short_form': reg[0],
                                'label': reg[1],
                                'folder': reg[2],
                                'template_id': reg[3],
                                'wlz_size': wlz_size
                            })
        
        print(f"\n[ANALYSIS COMPLETE]\n")
        print(f"Total folders checked: {checked_count}")
        print(f"Empty folders found: {empty_count}")
        print(f"Unreachable folders: {failed_count}\n")
        
        # Check for both-empty anomalies
        folder_empty_templates = defaultdict(set)
        for record in empty_records:
            folder_name = record['folder'].split('/')[-3]
            folder_empty_templates[folder_name].add(record['template_id'])
        
        both_empty = [f for f, t in folder_empty_templates.items() if len(t) == 2]
        only_brain = [f for f, t in folder_empty_templates.items() if 'VFBc_00101567' in str(t) and len(t) == 1]
        only_vnc = [f for f, t in folder_empty_templates.items() if 'VFBc_00200000' in str(t) and len(t) == 1]
        
        print(f"[ANOMALY CHECK]")
        print(f"  Folders with BOTH templates empty: {len(both_empty)}")
        if both_empty:
            print(f"  WARNING: Found {len(both_empty)} folders with both templates empty!")
            issues['both_empty_folders'] = both_empty[:20]  # Show first 20
        print(f"  Folders with ONLY Brain empty: {len(only_brain)}")
        print(f"  Folders with ONLY VNC empty: {len(only_vnc)}\n")
        
        # Save results
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_empty_records': len(empty_records),
            'empty_records': empty_records,
            'statistics': {
                'total_checked': checked_count,
                'empty_found': empty_count,
                'unreachable': failed_count,
                'both_templates_empty': len(both_empty),
                'only_brain_empty': len(only_brain),
                'only_vnc_empty': len(only_vnc)
            },
            'issues': issues
        }
        
        # Count by template
        brain_count = sum(1 for r in empty_records if 'VFBc_00101567' in str(r.get('template_id', '')))
        vnc_count = sum(1 for r in empty_records if 'VFBc_00200000' in str(r.get('template_id', '')))
        
        print(f"[RESULTS BY TEMPLATE]")
        print(f"  Brain (VFBc_00101567): {brain_count} empty")
        print(f"  VNC   (VFBc_00200000): {vnc_count} empty")
        print(f"  Total Empty Records: {len(empty_records)}\n")
        
        # Save JSON results
        output_file = f'/Users/rcourt/GIT/detectEmpty/kb_full_analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"[SAVED] Results: {output_file}\n")
        
        # Print issues summary
        if issues['both_empty_folders']:
            print(f"[ALERT] Folders with BOTH templates empty (should be rare):")
            for folder in issues['both_empty_folders'][:10]:
                print(f"  - {folder}")
        
        if len(issues['unreachable']) > 0:
            print(f"[ALERT] {len(issues['unreachable'])} unreachable folder-template pairs")
            print(f"  (sample of first 5):")
            for issue in issues['unreachable'][:5]:
                print(f"  - {issue['folder']} ({issue['template']})")
        
        elapsed = time.time() - start_time
        print(f"\n[TIMING] Analysis completed in {elapsed/3600:.1f} hours\n")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
