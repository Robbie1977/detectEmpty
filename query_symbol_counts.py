#!/usr/bin/env python3

import json
import requests
from kbw_config import get_kb_http_endpoint, get_kb_auth

endpoint = get_kb_http_endpoint()
auth = get_kb_auth()

queries = {
    'total_with_symbol': "MATCH (i:Individual) WHERE exists(i.symbol) RETURN count(i) AS c",
    'total_flywire_label': "MATCH (i:Individual) WHERE i.label CONTAINS 'FlyWire' RETURN count(i) AS c",
    'total_fw_shortform': "MATCH (i:Individual) WHERE i.short_form STARTS WITH 'VFB_fw' RETURN count(i) AS c",
    'fw_with_symbol': "MATCH (i:Individual) WHERE i.short_form STARTS WITH 'VFB_fw' AND exists(i.symbol) RETURN count(i) AS c",
    'fw_missing_symbol': "MATCH (i:Individual) WHERE i.short_form STARTS WITH 'VFB_fw' AND NOT exists(i.symbol) RETURN count(i) AS c",
    'total_flywire_prefix': "MATCH (i:Individual) WHERE i.short_form STARTS WITH 'flywire' RETURN count(i) AS c",
    'flywire_prefix_with_symbol': "MATCH (i:Individual) WHERE i.short_form STARTS WITH 'flywire' AND exists(i.symbol) RETURN count(i) AS c",
}

out = {}

for name, q in queries.items():
    resp = requests.post(
        endpoint,
        json={'statements': [{'statement': q, 'parameters': {}, 'resultDataContents': ['row']}],},
        auth=auth,
        timeout=60,
    )
    resp.raise_for_status()
    out[name] = resp.json()['results'][0]['data'][0]['row'][0]

# Also grab a small sample of FlyWire individuals with symbol
q = """MATCH (i:Individual) WHERE i.short_form STARTS WITH 'VFB_fw' AND exists(i.symbol) RETURN i.short_form AS id, i.label AS label, i.symbol AS symbol LIMIT 10"""
resp = requests.post(
    endpoint,
    json={'statements': [{'statement': q, 'parameters': {}, 'resultDataContents': ['row']}],},
    auth=auth,
    timeout=60,
)
resp.raise_for_status()
out['sample'] = resp.json()

print(json.dumps(out, indent=2))
