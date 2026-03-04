#!/usr/bin/env python3
"""
Batch test image folders and generate CYPHER update statements.

This script takes a list of folder/individual mappings and:
1. Tests each for empty images using volume.wlz size detection
2. Generates CYPHER block statements for confirmed empty folders
3. Outputs a ready-to-use CYPHER file

Usage:
    # From manual KB query results (copy-paste from neo4j browser)
    python batch_test_folders.py --input-file kb_registrations.txt --output cypher_updates.cypher
    
    # Or directly test a list of folders
    python batch_test_folders.py --test-folders 3ler,3ftr --templates VFB_00101567,VFB_00200000
"""

import sys
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse

# Empty folder signatures 
EMPTY_THRESHOLDS = {
    'VFB_00101567': 10000,       # Brain template threshold
    'VFB_00200000': 4000,        # VNC template threshold  
}

# Known empty folders from analysis
KNOWN_EMPTY_FOLDERS = {
    'VFB_00101567': {'3ler'},                    # Brain
    'VFB_00200000': {'3ftr', '3ftt', '3ftv'},    # VNC
}

def get_wlz_size(folder_code: str, template_id: str) -> int:
    """
    Fetch volume.wlz file size for a folder/template combination.
    
    Args:
        folder_code: Short folder code (e.g., '3ler')
        template_id: VFB template ID (e.g., 'VFB_00101567')
    
    Returns:
        File size in bytes, or -1 if not found/error
    """
    url = f"http://www.virtualflybrain.org/data/VFB/i/jrmc/{folder_code}/{template_id}/"
    
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
                # Try to extract file size (last number in the line)
                parts = line.split()
                if parts:
                    try:
                        size = int(parts[-1])
                        return size
                    except ValueError:
                        pass
        
        return -1
    
    except Exception as e:
        print(f"  [ERROR] {folder_code}/{template_id}: {e}", file=sys.stderr)
        return -1

def is_empty_folder(folder_code: str, template_id: str, verbose: bool = True) -> bool:
    """
    Determine if a folder is empty based on volume.wlz size.
    
    Args:
        folder_code: Short folder code
        template_id: VFB template ID
        verbose: Print debug info
    
    Returns:
        True if detected as empty
    """
    wlz_size = get_wlz_size(folder_code, template_id)
    
    if wlz_size < 0:
        if verbose:
            print(f"    ⚠  Could not fetch size for {folder_code}/{template_id}")
        return False
    
    threshold = EMPTY_THRESHOLDS.get(template_id, 10000)
    is_empty = wlz_size < threshold
    
    symbol = "🚫" if is_empty else "✓"
    if verbose:
        print(f"    {symbol} {folder_code}: {wlz_size:,} bytes {'(EMPTY)' if is_empty else '(OK)'}")
    
    return is_empty

def generate_consolidated_cypher_blocks(empty_blocks: List[Dict]) -> str:
    """
    Generate consolidated CYPHER statements grouped by template.
    
    Uses VFBc_ (channel) nodes and r.folder[0] IN [...] for efficiency.
    One statement per template instead of one per individual.
    
    Args:
        empty_blocks: List of dicts with 'folder', 'template_id', 'short_form'
    
    Returns:
        CYPHER statement(s) as string
    """
    if not empty_blocks:
        return "// No empty folders to block"
    
    # Group by template
    by_template = {}
    for block in empty_blocks:
        template = block['template_id']
        if template not in by_template:
            by_template[template] = []
        
        # Build full folder URL
        folder_code = block['folder']
        folder_url = f"http://www.virtualflybrain.org/data/VFB/i/jrmc/{folder_code}/{template}/"
        by_template[template].append(folder_url)
    
    # Generate consolidated statements
    statements = []
    
    for template_id, folder_urls in sorted(by_template.items()):
        template_name = f"Brain ({template_id})" if template_id == 'VFB_00101567' else \
                       f"VNC ({template_id})" if template_id == 'VFB_00200000' else template_id
        
        # Build the IN clause with proper JSON formatting
        folder_list = json.dumps(sorted(folder_urls))
        
        cypher = f"""// Block empty folders in {template_name}
// Empty folders: {', '.join(url.split('/jrmc/')[1].split('/')[0] for url in folder_urls)}
MATCH (c:Individual)-[r:in_register_with]->(tc:Template {{short_form: '{template_id}'}})
WHERE r.folder[0] IN {folder_list}
SET r.block = ['No expression in region']
RETURN c.short_form as channel, r.folder[0] as folder, tc.label as template, COUNT(r) as blocked_count"""
        
        statements.append(cypher)
    
    return "\n\n".join(statements)

def parse_kb_registration_file(filepath: Path) -> List[Dict[str, str]]:
    """
    Parse a text file with KB registrations (TSV or CSV format).
    
    Expected columns: short_form, label, folder, template_id
    (or similar variations)
    """
    registrations = []
    
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if not lines:
        return []
    
    # Try to detect format from first line
    header = lines[0].lower()
    is_csv = ',' in lines[0]
    is_tsv = '\t' in lines[0]
    
    delimiter = ',' if is_csv else ('\t' if is_tsv else None)
    
    if delimiter is None:
        # Try to parse space-separated with visual alignment
        print("[WARN] Could not detect delimiter, attempting manual parse...")
        return registrations
    
    # Parse header to find column indices
    if is_csv or is_tsv:
        headers = [h.strip() for h in lines[0].split(delimiter)]
        
        col_short = None
        col_label = None
        col_folder = None
        col_template = None
        
        for i, h in enumerate(headers):
            if 'short_form' in h.lower() or 'id' in h.lower():
                col_short = i
            elif 'label' in h.lower():
                col_label = i
            elif 'folder' in h.lower():
                col_folder = i
            elif 'template' in h.lower():
                col_template = i
        
        # Parse data rows
        for line in lines[1:]:
            if not line.strip():
                continue
            
            parts = [p.strip() for p in line.split(delimiter)]
            
            reg = {}
            if col_short is not None and col_short < len(parts):
                reg['short_form'] = parts[col_short]
            if col_label is not None and col_label < len(parts):
                reg['label'] = parts[col_label]
            if col_folder is not None and col_folder < len(parts):
                reg['folder'] = parts[col_folder]
            if col_template is not None and col_template < len(parts):
                reg['template_id'] = parts[col_template]
            
            if 'short_form' in reg and 'folder' in reg and 'template_id' in reg:
                registrations.append(reg)
    
    return registrations

def main():
    parser = argparse.ArgumentParser(
        description="Test folders for empty images and generate CYPHER update statements"
    )
    parser.add_argument('--input-file', help='Text file with KB registrations (TSV/CSV)')
    parser.add_argument('--output', default='cypher_block_updates.cypher',
                       help='Output CYPHER file (default: cypher_block_updates.cypher)')
    parser.add_argument('--test-folders', help='Comma-separated folder codes to test')
    parser.add_argument('--template', default='VFB_00101567,VFB_00200000',
                       help='Comma-separated template IDs')
    parser.add_argument('--known-only', action='store_true',
                       help='Only test known empty folders')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    registrations: List[Dict[str, str]] = []
    
    # Load registrations from file if provided
    if args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"[ERROR] File not found: {args.input_file}")
            sys.exit(1)
        
        registrations = parse_kb_registration_file(input_path)
        if registrations:
            print(f"[OK] Loaded {len(registrations)} registrations from {args.input_file}")
        else:
            print(f"[WARN] Could not parse registrations from {args.input_file}")
    
    # Or use command-line arguments
    elif args.test_folders:
        folders = args.test_folders.split(',')
        templates = args.template.split(',')
        
        for folder in folders:
            for template in templates:
                registrations.append({
                    'short_form': f'VFB_TEST_{folder}',
                    'label': f'Test folder {folder}',
                    'folder': folder.strip(),
                    'template_id': template.strip()
                })
    
    # Or use known empty folders
    elif args.known_only:
        for template_id, folders in KNOWN_EMPTY_FOLDERS.items():
            for folder in folders:
                registrations.append({
                    'short_form': f'VFB_KNOWN_{folder}',
                    'label': f'Known empty {folder}',
                    'folder': folder,
                    'template_id': template_id
                })
    
    if not registrations:
        print("[ERROR] No registrations to test. Use --input-file, --test-folders, or --known-only")
        parser.print_help()
        sys.exit(1)
    
    # Test folders
    print("\n" + "="*70)
    print("TESTING FOLDERS FOR EMPTY IMAGES")
    print("="*70 + "\n")
    
    empty_blocks = []
    tested = set()
    
    for reg in registrations:
        folder = reg['folder']
        template = reg['template_id']
        folder_key = (folder, template)
        
        # Only test each folder/template once
        if folder_key in tested:
            continue
        
        tested.add(folder_key)
        
        template_name = f"Brain ({template})" if template == 'VFB_00101567' else \
                       f"VNC ({template})" if template == 'VFB_00200000' else template
        
        if args.verbose:
            print(f"\nTesting {folder} in {template_name}...")
        
        if is_empty_folder(folder, template, verbose=args.verbose):
            # Collect all registrations for this folder/template
            for r in registrations:
                if r['folder'] == folder and r['template_id'] == template:
                    empty_blocks.append(r)
    
    # Generate CYPHER
    print("\n" + "="*70)
    print("CYPHER UPDATE STATEMENTS")
    print("="*70 + "\n")
    
    cypher_output = f"""// VFB KB Update: Block empty image folders
// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
//
// Consolidated statements grouped by template
// Uses VFBc_ (channel) nodes with r.folder[0] IN [list of URLs]
// Total empty folders to block: {len(empty_blocks)}

"""
    
    if empty_blocks:
        consolidated = generate_consolidated_cypher_blocks(empty_blocks)
        cypher_output += consolidated + "\n"
    else:
        cypher_output += "// No empty folders detected\n"
    
    print(cypher_output)
    
    # Save to file
    try:
        output_path = Path(args.output)
        output_path.write_text(cypher_output)
        print(f"\n[OK] Saved to {output_path.absolute()}")
    except Exception as e:
        print(f"\n[ERROR] Could not save to {args.output}: {e}")
        sys.exit(1)
    
    # Summary
    if empty_blocks:
        print(f"\n[SUMMARY] Found {len(empty_blocks)} empty folder registrations")
        print("\nNext steps:")
        print(f"1. Review {args.output}")
        print("2. Connect to writable KB instance")
        print("3. Execute CYPHER statements")
    else:
        print("\n[INFO] No empty folders detected")

if __name__ == '__main__':
    main()
