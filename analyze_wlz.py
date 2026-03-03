#!/usr/bin/env python3
"""
Analyze volume.wlz file sizes across all Brain folders.
Empty folders should have very small wlz files (just template),
while folders with expression data will have much larger wlz files.
"""

import requests
from bs4 import BeautifulSoup
import re

# All 97 Brain folders
brain_folders = [
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kle/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kjs/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kjn/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k8z/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kce/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3juw/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k83/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kcj/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k4v/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kaw/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kek/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k63/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k64/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jzn/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kas/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kcx/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k9d/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kbt/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jy2/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jx8/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k1g/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k3g/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k3a/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k5m/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k5n/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kfz/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k94/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k3b/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k4b/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jrf/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3juy/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jx7/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jrh/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jrl/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jut/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jv5/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kex/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k8c/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3juu/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jv4/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3js8/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jyf/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jzi/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k9f/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k9y/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k9c/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jw1/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jv7/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k0m/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k04/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kff/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k8u/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jv0/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jxa/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k40/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k4c/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k51/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k4k/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k4l/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k7b/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kfg/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k7t/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kfw/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ke4/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k6j/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ker/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k4e/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3js7/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jt0/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jzj/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k4r/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k0d/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k8w/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k9b/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jwv/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k5l/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k74/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kfs/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kcs/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kao/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k1l/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k0v/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kf1/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k7k/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jrq/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3jtk/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k39/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k17/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kat/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k80/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3k9m/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kam/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftr/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftq/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3fts/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftt/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftv/VFB_00101567/",
]

def get_wlz_size(url):
    """Extract volume.wlz file size from directory listing."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        pre_tag = soup.find('pre')
        if not pre_tag:
            return None
        
        lines = pre_tag.get_text().split('\n')
        
        for line in lines:
            if 'volume.wlz' in line and '../' not in line:
                # Extract the size (last number on the line)
                parts = line.split()
                if parts:
                    try:
                        size = int(parts[-1])
                        return size
                    except ValueError:
                        pass
        
        return None
    except Exception as e:
        print(f"Error: {url} - {e}")
        return None

def extract_folder_code(url):
    """Extract folder code from URL."""
    match = re.search(r'/jrmc/([^/]+)/', url)
    return match.group(1) if match else None

def main():
    print("Analyzing volume.wlz file sizes across all Brain folders")
    print("=" * 90)
    print("(Empty folders should have tiny wlz files, folders with data will be much larger)")
    print("=" * 90)
    
    results = {}
    
    for i, url in enumerate(brain_folders, 1):
        folder_code = extract_folder_code(url)
        wlz_size = get_wlz_size(url)
        
        if wlz_size is not None:
            results[folder_code] = wlz_size
            mb = wlz_size / (1024**2)
            kb = wlz_size / 1024
            if mb > 0.1:
                print(f"[{i:2d}/97] {folder_code}: {mb:7.2f} MB ({wlz_size:>12,} bytes)")
            else:
                print(f"[{i:2d}/97] {folder_code}: {kb:7.1f} KB ({wlz_size:>12,} bytes)")
    
    print("\n" + "=" * 90)
    print("ANALYSIS")
    print("=" * 90)
    
    # Sort by size
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    
    print(f"\nSmallest 10 volume.wlz files (likely EMPTY folders):")
    print("-" * 90)
    for folder_code, size in sorted_results[:10]:
        kb = size / 1024
        print(f"  {folder_code}: {kb:7.1f} KB ({size:,} bytes)")
    
    print(f"\nLargest 10 volume.wlz files (have expression data):")
    print("-" * 90)
    for folder_code, size in sorted_results[-10:]:
        mb = size / (1024**2)
        print(f"  {folder_code}: {mb:7.2f} MB ({size:,} bytes)")
    
    # Find the natural gap in the data
    print(f"\n\nDetailed size distribution of volume.wlz:")
    print("-" * 90)
    
    # Group by size ranges
    tiny = [x for x in sorted_results if x[1] < 50 * 1024]  # < 50 KB
    small = [x for x in sorted_results if 50 * 1024 <= x[1] < 500 * 1024]  # 50 KB - 500 KB
    medium = [x for x in sorted_results if 500 * 1024 <= x[1] < 5 * 1024**2]  # 500 KB - 5 MB
    large = [x for x in sorted_results if x[1] >= 5 * 1024**2]  # >= 5 MB
    
    print(f"Tiny (<50 KB):        {len(tiny):2d} folders - LIKELY EMPTY")
    print(f"Small (50KB-500KB):   {len(small):2d} folders")
    print(f"Medium (500KB-5MB):   {len(medium):2d} folders")
    print(f"Large (>5MB):         {len(large):2d} folders - HAS EXPRESSION DATA")
    
    if tiny:
        print(f"\n\nFOLDERS TO BLOCK (volume.wlz < 50 KB - empty/template only):")
        print("-" * 90)
        for folder_code, size in tiny:
            kb = size / 1024
            print(folder_code)

if __name__ == "__main__":
    main()
