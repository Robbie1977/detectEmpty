#!/usr/bin/env python3
"""
Check what template IDs are in the folder URLs
"""

import requests

# Query registrations from VFBc channel nodes
query = '''
MATCH (n:Individual)-[r:in_register_with]->(tc:Template)
WHERE n.label contains "MaleCNS" AND tc.short_form = "VFBc_00101567"
RETURN DISTINCT r.folder[0] as folder
LIMIT 10
'''

url = 'http://kb.virtualflybrain.org/db/data/transaction/commit'
data = {
    'statements': [{
        'statement': query,
        'parameters': {},
        'resultDataContents': ['row']
    }]
}

response = requests.post(url, json=data, auth=('neo4j', 'vfb'))
result = response.json()

print('Brain Channel (VFBc_00101567) folder URLs:')
if result['results'] and result['results'][0]['data']:
    for row in result['results'][0]['data']:
        folder = row['row'][0]
        if 'VFB_00101567' in folder:
            print(f'✅ Uses VFB_00101567: {folder}')
        elif 'VFBc_' in folder:
            print(f'❌ Uses VFBc_: {folder}')
        else:
            print(f'? Unknown: {folder}')
else:
    print('No data found')
