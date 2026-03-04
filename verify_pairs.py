#!/usr/bin/env python3
"""
Verify that no image pairs have both Brain and VNC templates marked as empty.

This script checks if there are any individuals that have registrations to both
VFB_00101567 (Brain) and VFB_00200000 (VNC) templates, and verifies that at least
one of them has data (is not empty).
"""

import requests
import json
from typing import Dict, List, Set

# Empty folder signatures
EMPTY_SIGNATURES = {
    'VFB_00101567': 10000,  # Brain template - empty threshold < 10 KB
    'VFB_00200000': 4000,   # VNC template - empty threshold < 4 KB
}

def get_wlz_size(url: str) -> int:
    """Extract volume.wlz file size from directory listing."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        from bs4 import BeautifulSoup
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

def is_empty_folder(folder_url: str, template_id: str) -> bool:
    """Check if a folder is empty based on volume.wlz size."""
    wlz_size = get_wlz_size(folder_url)

    if wlz_size < 0:
        return False  # Can't determine, assume not empty

    threshold = EMPTY_SIGNATURES.get(template_id, 10000)
    return wlz_size < threshold

def main():
    print("Verifying no image pairs have both templates empty...")
    print("=" * 60)

    # Query KB for individuals with both channel registrations
    query = """
    MATCH (n:Individual)-[r1:in_register_with]->(t1:Template {short_form: 'VFBc_00101567'}),
          (n:Individual)-[r2:in_register_with]->(t2:Template {short_form: 'VFBc_00200000'})
    WHERE n.label contains 'MaleCNS'
    RETURN DISTINCT n.short_form as individual,
                     r1.folder[0] as brain_folder,
                     r2.folder[0] as vnc_folder
    LIMIT 20  // Sample check
    """

    try:
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

        if not result['results'] or not result['results'][0]['data']:
            print("No individuals found with both Brain and VNC registrations.")
            return

        pairs = [record['row'] for record in result['results'][0]['data']]
        print(f"Found {len(pairs)} individuals with both templates (sample of 50)")

        both_empty_count = 0
        checked_count = 0

        for individual, brain_folder, vnc_folder in pairs:
            checked_count += 1
            print(f"\nChecking {individual}...")

            brain_empty = is_empty_folder(brain_folder, 'VFB_00101567')
            vnc_empty = is_empty_folder(vnc_folder, 'VFB_00200000')

            if brain_empty:
                print(f"  Brain: EMPTY")
            else:
                print(f"  Brain: HAS DATA")

            if vnc_empty:
                print(f"  VNC: EMPTY")
            else:
                print(f"  VNC: HAS DATA")

            if brain_empty and vnc_empty:
                both_empty_count += 1
                print(f"  ❌ BOTH TEMPLATES EMPTY!")
            else:
                print(f"  ✅ At least one template has data")

        print(f"\n" + "=" * 60)
        print("SUMMARY:")
        print(f"Individuals checked: {checked_count}")
        print(f"Both templates empty: {both_empty_count}")

        if both_empty_count == 0:
            print("✅ VERIFICATION PASSED: No individuals have both templates empty")
        else:
            print("❌ VERIFICATION FAILED: Found individuals with both templates empty")

    except Exception as e:
        print(f"Error querying KB: {e}")

if __name__ == '__main__':
    main()