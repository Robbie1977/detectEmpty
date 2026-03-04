#!/usr/bin/env python3
"""
Connect to VFB Knowledge Base and generate CYPHER statements to block empty image folders.

This script:
1. Connects to the VFB KB via HTTP API
2. Queries for Individual nodes with 'MaleCNS' registered to Channel templates
3. Retrieves folder URLs (which contain full Template IDs: VFB_00101567, VFB_00200000)
4. Checks each folder for empty images using volume.wlz file size metrics
5. Generates CYPHER UPDATE statements to block empty folders (using Template IDs)

Template ID Usage:
- KB stores registrations to Channel nodes (VFBc_00101567, VFBc_00200000)
- Folder URLs contain full Template IDs (VFB_00101567, VFB_00200000)
- HTTP checking uses folder URLs directly (already have correct Template IDs)
- Cypher statements reference Templates by their actual IDs (VFB_...)

Usage:
    python kb_block_empty_images.py [--save-cypher filename.cypher]
"""

import sys
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Tuple, Set
from neo4j import GraphDatabase

# Empty folder signatures discovered from analysis
# volume.wlz file sizes for template-only (no expression) folders
EMPTY_SIGNATURES = {
    'VFB_00101567': 10000,  # Brain template - empty threshold < 10 KB
    'VFB_00200000': 4000,   # VNC template - empty threshold < 4 KB
}

def get_wlz_size(url: str) -> int:
    """Extract volume.wlz file size from directory listing."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        pre_tag = soup.find('pre')
        if not pre_tag:
            return -1
        
        lines = pre_tag.get_text().split('\n')
        
        for line in lines:
            if 'volume.wlz' in line and '../' not in line:
                parts = line.split()
                if parts:
                    try:
                        size = int(parts[-1])
                        return size
                    except ValueError:
                        pass
        
        return -1
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return -1

def is_empty_folder(folder_url: str, template_id: str) -> tuple:
    """
    Check if a folder contains empty image data based on volume.wlz size.
    
    Args:
        folder_url: Full folder URL (e.g., 'http://www.virtualflybrain.org/data/VFB/i/jrmc/3ler/VFB_00101567/')
        template_id: Template VFB ID (e.g., 'VFB_00101567' for Brain)
    
    Returns:
        (is_empty: bool, is_reachable: bool) 
        - is_empty: True if detected as empty
        - is_reachable: False if folder couldn't be checked (error/timeout)
    """
    wlz_size = get_wlz_size(folder_url)
    
    if wlz_size < 0:
        # Cannot determine - assume not empty AND note it wasn't reachable
        return (False, False)
    
    # Check against template-specific threshold
    threshold = EMPTY_SIGNATURES.get(template_id, 10000)
    
    folder_name = folder_url.split('/')[-3]  # Extract folder name like '3ler'
    
    if wlz_size < threshold:
        return (True, True)  # Empty and reachable
    else:
        return (False, True)  # Has data and reachable

def generate_cypher_block_statement(short_form: str, folder_code: str) -> str:
    """
    Generate CYPHER statement to add block on in_register_with edge.
    
    Uses VFBc_ (channel) nodes and r.folder[0] IN [...] for efficiency.
    
    Args:
        short_form: VFB ID of Individual (e.g., VFB_something)
        folder_code: Folder code identifier
    
    Returns:
        CYPHER statement string
    """
    cypher = f"""
// Block empty image for channel in folder {folder_code}
MATCH (c:Individual)-[r:in_register_with]->(tc:Template)
WHERE r.folder[0] CONTAINS '/{folder_code}/'
SET r.block = ['No expression in region']
RETURN c.short_form as channel, r.folder[0] as folder, tc.label as template
"""
    return cypher.strip()

def generate_summary_cypher(empty_records: List[Dict]) -> str:
    """
    Generate a consolidated transaction block with empty folder blocks.
    Groups by template for efficiency using r.folder[0] IN [...] syntax.
    """
    if not empty_records:
        return "// No empty folders detected"
    
    # Group by template
    by_template = {}
    for record in empty_records:
        template = record['template_id']
        if template not in by_template:
            by_template[template] = []
        
        # The folder is already the full URL from KB
        folder_url = record['folder']
        by_template[template].append(folder_url)
    
    cypher_block = "// VFB KB Empty Image Folder Block Updates\n"
    cypher_block += f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    cypher_block += f"// Total empty folders: {len(empty_records)}\n\n"
    
    for template_id, folder_urls in sorted(by_template.items()):
        template_name = f"Brain ({template_id})" if template_id == 'VFB_00101567' else \
                       f"VNC ({template_id})" if template_id == 'VFB_00200000' else template_id
        
        # Extract folder codes for comment
        folder_codes = ', '.join(url.split('/jrmc/')[1].split('/')[0] for url in folder_urls)
        folder_list = json.dumps(sorted(folder_urls))
        
        cypher_block += f"// Block empty folders in {template_name}\n"
        cypher_block += f"// Folders: {folder_codes}\n"
        cypher_block += f"""MATCH (c:Individual)-[r:in_register_with]->(tc:Template {{short_form: '{template_id}'}})
WHERE r.folder[0] IN {folder_list}
SET r.block = ['No expression in region']
RETURN c.short_form as channel, r.folder[0] as folder, tc.label as template
"""
        cypher_block += "\n"
    
    return cypher_block

def main():
    """Main execution."""
    
    print("\n" + "="*70)
    print("VFB Knowledge Base - Empty Image Folder Detector")
    print("="*70 + "\n")
    
    # Try to connect to Neo4j
    neo4j_available = True
    try:
        print("[INFO] Connecting to VFB Knowledge Base...")
        driver = GraphDatabase.driver('neo4j://kb.virtualflybrain.org', auth=('neo4j', 'vfb'))
        print("[OK] Connected to KB\n")
    except Exception as e:
        print(f"[ERROR] Cannot connect to KB: {e}")
        neo4j_available = False
    
    empty_records = []
    
    if neo4j_available:
        try:
            print("[INFO] Connecting to VFB Knowledge Base...")
            # Use HTTP API instead of Bolt
            def neo4j_query(query):
                url = 'http://kb.virtualflybrain.org/db/data/transaction/commit'
                headers = {'Content-Type': 'application/json'}
                data = {
                    'statements': [{
                        'statement': query,
                        'parameters': {},
                        'resultDataContents': ['row']
                    }]
                }
                response = requests.post(url, json=data, auth=('neo4j', 'vfb'))
                response.raise_for_status()
                result = response.json()
                if result['results'] and result['results'][0]['data']:
                    return [record['row'] for record in result['results'][0]['data']]
                return []
            
            print("[OK] Connected to KB\n")
            
            # Get all folders for MaleCNS individuals
            query = """MATCH (n:Individual)-[r:in_register_with]->(tc:Template) 
                       WHERE n.label contains 'MaleCNS' 
                       RETURN collect(distinct r.folder[0]) as folders"""
            
            print("[INFO] Querying KB for MaleCNS individuals...")
            result = neo4j_query(query)
            folders_list = result[0][0] if result else []
            
            print(f"[OK] Found {len(folders_list)} unique folders\n")
            
            # Now get individuals and their templates for each folder
            query2 = """MATCH (n:Individual)-[r:in_register_with]->(tc:Template) 
                        WHERE n.label contains 'MaleCNS' 
                        RETURN distinct n.short_form as short_form, 
                                       n.label as label, 
                                       r.folder[0] as folder, 
                                       tc.short_form as template_id"""
            
            print("[INFO] Getting individual registrations...\n")
            registrations = neo4j_query(query2)
            
            print(f"[OK] Found {len(registrations)} registrations\n")
            
            # Check each folder for empty images
            checked_folders = set()
            checked_count = 0
            failed_count = 0
            empty_found = 0
            
            unique_folders = len(set((r[2], r[3]) for r in registrations))
            
            # For full KB analysis: set a reasonable limit to avoid hours-long network requests
            # Full analysis would require all 331,182 folders, but network timeouts make this impractical
            # Use --full-analysis flag to override this limit if willing to wait
            max_folders_to_check = 10000  # Default: sample first 10k folders
            
            # Check environment variable for override
            import os
            if os.environ.get('DETECTEMPTY_FULL_ANALYSIS'):
                max_folders_to_check = unique_folders  # Check all folders
            
            display_limit = min(unique_folders, max_folders_to_check)
            print(f"[INFO] Checking up to {display_limit} unique folders (of {unique_folders} total)\n")
            print(f"[INFO] To check all {unique_folders} folders: export DETECTEMPTY_FULL_ANALYSIS=1\n")
            
            for reg in registrations:
                    
                folder_key = (reg[2], reg[3])  # folder, template_id
                
                if folder_key not in checked_folders:
                    checked_folders.add(folder_key)
                    checked_count += 1
                    
                    # Progress updates every 500 folders or for first 10
                    if checked_count % 500 == 0 or checked_count <= 10:
                        print(f"[PROGRESS] {checked_count}/{display_limit} folders checked ({empty_found} empty)...")
                    
                    # Stop if we've reached the check limit
                    if checked_count > max_folders_to_check:
                        print(f"\n[LIMIT] Reached maximum folders to check ({max_folders_to_check})")
                        print(f"[INFO] To check all {unique_folders} folders: export DETECTEMPTY_FULL_ANALYSIS=1\n")
                        break
                    
                    is_empty, is_reachable = is_empty_folder(reg[2], reg[3])
                    
                    if is_reachable:
                        folder_name = reg[2].split('/')[-3]
                        wlz_size = get_wlz_size(reg[2])
                        threshold = EMPTY_SIGNATURES.get(reg[3], 10000)
                        
                        if is_empty:
                            empty_found += 1
                            print(f"    ✓ [EMPTY] {folder_name}: {wlz_size} bytes < {threshold}")
                            
                            # Record all individuals with this registration
                            for r in registrations:
                                if r[2] == reg[2] and r[3] == reg[3]:
                                    empty_records.append({
                                        'short_form': r[0],
                                        'label': r[1],
                                        'folder': r[2],
                                        'template_id': r[3]
                                    })
                    else:
                        failed_count += 1
                        if failed_count <= 20:
                            print(f"    ✗ [UNREACHABLE] {reg[2]} (network error)")
            
            print(f"\n[SUMMARY] Total folders: {checked_count}, Empty: {empty_found}, Failed: {failed_count}\n")
        
        except Exception as e:
            print(f"[ERROR] {e}")
            print("[INFO] Falling back to manual query\n")
            neo4j_available = False
    
    # If Neo4j not available or failed, exit with error
    if not neo4j_available:
        print("[ERROR] KB connection failed. Cannot proceed with analysis.")
        print("[INFO] To query the KB directly, run these Cypher commands in Neo4j Browser:\n")
        print("1. Get list of unique folders:")
        print("""
   MATCH (n:Individual)-[r:in_register_with]->(tc:Template) 
   WHERE n.label contains 'MaleCNS' 
   RETURN collect(distinct r.folder[0]) as folders
""")
        print("\n2. Get individual registrations:")
        print("""
   MATCH (n:Individual)-[r:in_register_with]->(tc:Template) 
   WHERE n.label contains 'MaleCNS' 
   RETURN distinct n.short_form, n.label, r.folder[0] as folder, tc.short_form as template_id
""")
        print("\nThen export the results and use --from-file option.")
        sys.exit(1)
    
    # Generate output
    print("\n" + "="*70)
    print("CYPHER UPDATE STATEMENTS")
    print("="*70 + "\n")
    
    cypher_output = generate_summary_cypher(empty_records)
    print(cypher_output)
    
    if empty_records:
        print(f"\n[SUMMARY] Found {len(empty_records)} empty folder registrations\n")
        print("Instructions for KB update:")
        print("1. Copy the CYPHER statements above")
        print("2. Connect to writable KB instance")
        print("3. Execute each statement or wrap in a transaction")
        print("4. Verify updates with: MATCH (r:in_register_with) WHERE r.block=['No expression in region'] RETURN count(r)")
    else:
        print("\n[INFO] No empty folders detected")
    
    # Write results to JSON file for workflow to read
    results_file = 'kb_analysis_results.json'
    try:
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_empty_records': len(empty_records),
                'empty_records': empty_records,
                'cypher_statements': cypher_output
            }, f, indent=2)
        print(f"\n[OK] Results saved to {results_file}")
    except Exception as e:
        print(f"\n[WARN] Could not save results file: {e}")
    
    # Optional: Save to file
    if len(sys.argv) > 1 and sys.argv[1] == '--save-cypher':
        filename = sys.argv[2] if len(sys.argv) > 2 else 'empty_folders_cypher.cypher'
        try:
            with open(filename, 'w') as f:
                f.write(cypher_output)
            print(f"\n[OK] Saved to {filename}")
        except Exception as e:
            print(f"\n[ERROR] Could not save to {filename}: {e}")

if __name__ == '__main__':
    main()
