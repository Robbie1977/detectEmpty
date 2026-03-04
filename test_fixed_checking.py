#!/usr/bin/env python3
"""
Quick test of the fixed folder checking logic
"""

import requests
from bs4 import BeautifulSoup

EMPTY_SIGNATURES = {
    'VFB_00101567': 10000,  # Brain - < 10KB
    'VFB_00200000': 4000,   # VNC - < 4KB
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
        return -1

def is_empty_folder(folder_url: str, template_id: str) -> tuple:
    """Check folder, return (is_empty, is_reachable)"""
    wlz_size = get_wlz_size(folder_url)
    
    if wlz_size < 0:
        return (False, False)  # Not reachable
    
    threshold = EMPTY_SIGNATURES.get(template_id, 10000)
    folder_name = folder_url.split('/')[-3]
    
    if wlz_size < threshold:
        print(f"    ✓ [EMPTY] {folder_name}: {wlz_size} bytes < {threshold}")
        return (True, True)
    else:
        print(f"    [DATA] {folder_name}: {wlz_size} bytes")
        return (False, True)

# Query some real folders
query = '''
MATCH (n:Individual)-[r:in_register_with]->(t:Template)
WHERE n.label contains "MaleCNS"
RETURN DISTINCT r.folder[0] as folder, t.short_form as template
LIMIT 30
'''

url = 'http://kb.virtualflybrain.org/db/data/transaction/commit'
data = {
    'statements': [{
        'statement': query,
        'parameters': {},
        'resultDataContents': ['row']
    }]
}

print("Testing folder checking with real KB data...\n")

response = requests.post(url, json=data, auth=('neo4j', 'vfb'))
result = response.json()

empty_count = 0
reachable_count = 0
unreachable_count = 0

if result['results'] and result['results'][0]['data']:
    for i, row in enumerate(result['results'][0]['data']):
        folder, template = row['row']
        
        print(f"Checking {i+1}: {folder.split('/jrmc/')[1]}")
        is_empty, is_reachable = is_empty_folder(folder, template)
        
        if is_reachable:
            reachable_count += 1
            if is_empty:
                empty_count += 1
        else:
            unreachable_count += 1
            print(f"    ✗ [UNREACHABLE]")

print(f"\n" + "="*60)
print(f"Results: {reachable_count} reachable, {empty_count} empty, {unreachable_count} unreachable")
print(f"Empty rate: {100*empty_count/max(1, reachable_count):.1f}% of reachable folders")
