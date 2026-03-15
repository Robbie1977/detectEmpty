#!/usr/bin/env python3
"""Generate Cypher to unblock folders that are currently blocked but not actually empty.

This script:
1. Queries the KB for all currently blocked folders (r.block = ['No expression in region'])
2. Checks each folder's volume.wlz size
3. Generates Cypher to REMOVE r.block for folders that are not empty

Usage:
  python unblock_false_blocks.py [--dry-run] [--save-cypher filename.cypher]
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from kbw_config import get_kb_http_endpoint, get_kb_auth

EMPTY_SIGNATURES = {
    'VFB_00101567': 1156,   # Brain template - empty is 1156 bytes
    'VFB_00200000': 2404,   # VNC template - empty is 2404 bytes
    'VFBc_00101567': 1156,
    'VFBc_00200000': 2404,
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

def neo4j_query(query):
    """Query the VFB KB via HTTP API."""
    url = get_kb_http_endpoint()
    headers = {'Content-Type': 'application/json'}
    data = {
        'statements': [{
            'statement': query,
            'parameters': {},
            'resultDataContents': ['row']
        }]
    }
    response = requests.post(url, json=data, auth=('neo4j', 'vfb'), timeout=20)
    response.raise_for_status()
    result = response.json()
    if result['results'] and result['results'][0]['data']:
        return [record['row'] for record in result['results'][0]['data']]
    return []

def main():
    print("Querying KB for currently blocked folders...")

    # Get all currently blocked folders
    query = """
    MATCH (c:Individual)-[r:in_register_with]->(t:Template)
    WHERE r.block = ['No expression in region']
    RETURN c.short_form as channel, r.folder[0] as folder, t.short_form as template
    """

    blocked = neo4j_query(query)
    print(f"Found {len(blocked)} currently blocked folders")

    unblock_candidates = []

    for channel, folder, template in blocked:
        print(f"Checking {channel} ({folder})...")

        # Determine expected empty size
        expected_empty_size = EMPTY_SIGNATURES.get(template)
        if expected_empty_size is None:
            print(f"  Unknown template {template}, skipping")
            continue

        # Check actual size
        actual_size = get_wlz_size(folder)
        if actual_size < 0:
            print(f"  Unreachable, skipping")
            continue

        print(f"  Size: {actual_size} bytes (empty would be {expected_empty_size})")

        if actual_size != expected_empty_size:
            print(f"  → CANDIDATE FOR UNBLOCK (not empty)")
            unblock_candidates.append({
                'channel': channel,
                'folder': folder,
                'template': template,
                'actual_size': actual_size,
                'expected_empty': expected_empty_size
            })
        else:
            print(f"  → CORRECTLY BLOCKED (is empty)")

    print(f"\nFound {len(unblock_candidates)} folders to unblock")

    if not unblock_candidates:
        print("No false blocks found.")
        return

    # Generate Cypher
    cypher = "// Unblock folders that are blocked but not actually empty\n"
    cypher += f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    cypher += f"// Total to unblock: {len(unblock_candidates)}\n\n"

    # Group by template
    by_template = {}
    for rec in unblock_candidates:
        by_template.setdefault(rec['template'], []).append(rec['folder'])

    for template, folders in sorted(by_template.items()):
        template_name = "Brain" if template == 'VFBc_00101567' else "VNC" if template == 'VFBc_00200000' else template
        folder_codes = ', '.join(url.split('/jrmc/')[1].split('/')[0] for url in folders)
        folder_list = json.dumps(sorted(folders))

        cypher += f"// Unblock {template_name} folders: {folder_codes}\n"
        cypher += f"MATCH (c:Individual)-[r:in_register_with]->(t:Template {{short_form: '{template}'}})\n"
        cypher += f"WHERE r.folder[0] IN {folder_list}\n"
        cypher += "REMOVE r.block\n"
        cypher += "RETURN c.short_form as channel, r.folder[0] as folder\n\n"

    print("\nGenerated Cypher:")
    print("=" * 50)
    print(cypher)

    # Save to file if requested
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--save-cypher':
        filename = sys.argv[2] if len(sys.argv) > 2 else 'unblock_false_blocks.cypher'
        with open(filename, 'w') as f:
            f.write(cypher)
        print(f"Saved to {filename}")

if __name__ == '__main__':
    main()
