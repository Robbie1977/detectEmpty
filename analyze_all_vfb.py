#!/usr/bin/env python3
"""
Analyze all VFB data folders containing volume.wlz files.
Recursively crawls VFB data directory to find all folders with volume.wlz
and checks their file sizes to identify potentially empty ones.
"""

import requests
from bs4 import BeautifulSoup
import time
from collections import deque

def get_directory_contents(url):
    """Get list of files and subdirs from a directory URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        pre_tag = soup.find('pre')
        if not pre_tag:
            return []
        
        items = []
        lines = pre_tag.get_text().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('../') and line != 'Parent Directory':
                parts = line.split()
                if parts:
                    name = parts[-1] if len(parts) > 1 else parts[0]
                    is_dir = name.endswith('/')
                    items.append((name.rstrip('/'), is_dir))
        return items
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return []

def find_wlz_sizes(base_url='http://www.virtualflybrain.org/data/VFB/', max_depth=5):
    """Recursively find all folders with volume.wlz and get their sizes."""
    results = []
    visited = set()
    queue = deque([(base_url, 0)])  # (url, depth)
    
    while queue:
        current_url, depth = queue.popleft()
        
        if depth > max_depth or current_url in visited:
            continue
        visited.add(current_url)
        
        print(f"Scanning depth {depth}: {current_url}")
        
        items = get_directory_contents(current_url)
        
        has_wlz = False
        wlz_size = -1
        
        for name, is_dir in items:
            if name == 'volume.wlz':
                # Get size
                try:
                    response = requests.head(f"{current_url}volume.wlz", timeout=10)
                    if 'content-length' in response.headers:
                        wlz_size = int(response.headers['content-length'])
                    has_wlz = True
                except:
                    pass
            elif is_dir and depth < max_depth:
                queue.append((f"{current_url}{name}/", depth + 1))
        
        if has_wlz:
            results.append((current_url, wlz_size))
            print(f"Found volume.wlz: {wlz_size} bytes at {current_url}")
        
        # Rate limiting
        time.sleep(0.1)
    
    return results

if __name__ == '__main__':
    print("Starting comprehensive VFB data analysis...")
    print("This will recursively scan all VFB data directories for volume.wlz files")
    print("This may take a very long time and make many requests to VFB servers.")
    print()
    
    results = find_wlz_sizes(max_depth=5)
    
    print(f"\nFound {len(results)} folders with volume.wlz")
    
    # Sort by size
    results.sort(key=lambda x: x[1])
    
    print("\nSmallest wlz files (potentially empty):")
    for url, size in results[:20]:
        print(f"{size:>10} bytes: {url}")
    
    print("\nAll results:")
    for url, size in results:
        print(f"{size:>10} bytes: {url}")