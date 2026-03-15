#!/usr/bin/env python3
"""
Diagnostic script to test VFB KB connectivity and identify hanging/timeout issues.
"""

import requests
import sys
from urllib.parse import urljoin
from datetime import datetime

from kbw_config import get_kb_http_endpoint, get_kbw_settings, get_kb_bolt_uri, get_kb_auth

def test_kb_connectivity():
    """Test various connection methods to VFB KB."""
    
    print("\n" + "="*70)
    print("VFB KB Connectivity Diagnostic")
    print("="*70 + "\n")
    
    kb_settings = get_kbw_settings()
    http_endpoint = get_kb_http_endpoint()
    https_endpoint = http_endpoint
    if https_endpoint.startswith("http://"):
        https_endpoint = https_endpoint.replace("http://", "https://", 1)

    bolt_uri = get_kb_bolt_uri()
    host = kb_settings.get("KBW_HOST", "kb.virtualflybrain.org")

    endpoints = {
        "HTTP REST API (Old)": http_endpoint,
        "HTTPS REST API": https_endpoint,
        "Bolt Protocol": bolt_uri,
        "Base HTTP": f"http://{host}/",
        "Base HTTPS": f"https://{host}/",
    }
    
    results = {}
    
    # Test HTTP endpoints
    for name, endpoint in list(endpoints.items())[:2]:  # Only HTTP/HTTPS
        print(f"\n[TEST] {name}")
        print(f"  URL: {endpoint}")
        
        try:
            # Simple query to test connection
            headers = {'Content-Type': 'application/json'}
            data = {
                'statements': [{
                    'statement': 'RETURN 1',
                    'parameters': {},
                    'resultDataContents': ['row']
                }]
            }
            
            print(f"  Attempting connection (timeout=5s)...")
            response = requests.post(endpoint, json=data, auth=get_kb_auth(), timeout=5)
            
            print(f"  Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ SUCCESS - KB is responsive")
                results[name] = "SUCCESS"
            else:
                print(f"  Response: {response.text[:200]}")
                results[name] = f"HTTP {response.status_code}"
        
        except requests.exceptions.Timeout:
            print(f"  ✗ TIMEOUT - Server not responding (>5 seconds)")
            results[name] = "TIMEOUT"
        except requests.exceptions.ConnectionError as e:
            print(f"  ✗ CONNECTION ERROR - {e}")
            results[name] = "CONNECTION_ERROR"
        except Exception as e:
            print(f"  ✗ ERROR - {type(e).__name__}: {e}")
            results[name] = str(e)
    
    # Test base connectivity
    print(f"\n[TEST] Base HTTP Connectivity")
    try:
        response = requests.get("http://kb.virtualflybrain.org/", timeout=5)
        print(f"  ✓ Base HTTP reachable (Status: {response.status_code})")
    except Exception as e:
        print(f"  ✗ Base HTTP unreachable: {e}")
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    for endpoint, result in results.items():
        status = "✓" if result == "SUCCESS" else "✗"
        print(f"{status} {endpoint}: {result}")
    
    # Recommendations
    print("\n" + "="*70)
    print("Recommendations")
    print("="*70 + "\n")
    
    if results.get("HTTP REST API (Old)") == "SUCCESS":
        print("✓ KB is accessible via old REST API - Script should work")
        return True
    elif results.get("HTTPS REST API") == "SUCCESS":
        print("⚠ KB only accessible via HTTPS - Script needs updating:")
        print("  Change: 'http://kb.virtualflybrain.org/...' → 'https://kb.virtualflybrain.org/...'")
        return False
    else:
        print("✗ KB is not accessible via known methods")
        print("\nPossible issues:")
        print("  1. Network connectivity problem (check firewall/VPN)")
        print("  2. KB REST API endpoint deprecated or moved")
        print("  3. Server is down or undergoing maintenance")
        print("  4. Authentication credentials invalid")
        print("\nSuggested fixes:")
        print("  1. Check network connectivity: ping kb.virtualflybrain.org")
        print("  2. Try connecting directly in browser: http://kb.virtualflybrain.org")
        print("  3. Check if HTTPS is required instead of HTTP")
        print("  4. Verify Neo4j service is running on KB server")
        return False

def test_large_dataset_query():
    """Test if KB can handle large queries (simulating 331k folder check)."""
    
    print("\n\n" + "="*70)
    print("Large Dataset Query Test")
    print("="*70 + "\n")
    
    try:
        endpoint = "http://kb.virtualflybrain.org/db/data/transaction/commit"
        
        # Simple query to get folder count
        headers = {'Content-Type': 'application/json'}
        query = "MATCH (n:Individual)-[r:in_register_with]->(tc:Template) WHERE n.label contains 'MaleCNS' RETURN count(distinct r.folder[0]) as folder_count"
        
        data = {
            'statements': [{
                'statement': query,
                'parameters': {},
                'resultDataContents': ['row']
            }]
        }
        
        print("[TEST] Querying folder count (larger dataset)...")
        print(f"  Query: {query[:60]}...")
        print(f"  Timeout: 10 seconds")
        
        start = datetime.now()
        response = requests.post(endpoint, json=data, auth=get_kb_auth(), timeout=10)
        elapsed = (datetime.now() - start).total_seconds()
        
        if response.status_code == 200:
            result = response.json()
            if result['results'] and result['results'][0]['data']:
                count = result['results'][0]['data'][0]['row'][0]
                print(f"  ✓ Query successful in {elapsed:.2f}s")
                print(f"  Folder count: {count}")
                
                print(f"\n[ESTIMATE] Time to check all {count} folders:")
                avg_per_folder = 1.0  # seconds
                total_est = (count * avg_per_folder) / 3600
                print(f"  ~{total_est:.1f} hours (assuming 1 sec/folder)")
            else:
                print(f"  Response: {response.text}")
        else:
            print(f"  ✗ Error: Status {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"  ✗ Query timed out after 10 seconds")
        print(f"  → This indicates KB would struggle with 331k folder analysis")
    except Exception as e:
        print(f"  ✗ Error: {e}")

if __name__ == '__main__':
    success = test_kb_connectivity()
    
    if success:
        test_large_dataset_query()
    
    sys.exit(0 if success else 1)
