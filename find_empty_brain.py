#!/usr/bin/env python3
"""
Find all Brain folders with very small wlz files (< 10 KB), similar to 3ler (1.156 KB)
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
    # Also check 3ler
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ler/VFB_00101567/",
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
                parts = line.split()
                if parts:
                    try:
                        size = int(parts[-1])
                        return size
                    except ValueError:
                        pass
        
        return None
    except Exception as e:
        return None

def extract_folder_code(url):
    """Extract folder code from URL."""
    match = re.search(r'/jrmc/([^/]+)/', url)
    return match.group(1) if match else None

def main():
    print("Finding all Brain folders with very small wlz files (< 10 KB)")
    print("Reference: 3ler = 1,156 bytes (confirmed empty)")
    print("=" * 100)
    
    results = {}
    tiny_folders = []
    
    for i, url in enumerate(brain_folders, 1):
        folder_code = extract_folder_code(url)
        wlz_size = get_wlz_size(url)
        
        if wlz_size is not None:
            results[folder_code] = wlz_size
            
            # Flag folders with < 10 KB wlz
            if wlz_size < 10 * 1024:
                tiny_folders.append((folder_code, wlz_size))
                kb = wlz_size / 1024
                print(f"[{i:2d}/98] {folder_code}: {kb:6.1f} KB ({wlz_size:8,} bytes) 👈 TINY")
            else:
                kb = wlz_size / 1024
                if i % 10 == 0:
                    print(f"[{i:2d}/98] {folder_code}: {kb:6.1f} KB")
    
    print("\n" + "=" * 100)
    print("RESULTS")
    print("=" * 100)
    
    if tiny_folders:
        sorted_tiny = sorted(tiny_folders, key=lambda x: x[1])
        print(f"\nFolders with wlz < 10 KB (likely empty):")
        print("-" * 100)
        for folder_code, size in sorted_tiny:
            kb = size / 1024
            print(f"{folder_code}: {kb:6.1f} KB ({size:8,} bytes)")
        
        print(f"\n\nFINAL BLOCK LIST ({len(sorted_tiny)} folders):")
        print("-" * 100)
        for folder_code, _ in sorted(sorted_tiny):
            print(folder_code)
    else:
        print("\nNo folders found with wlz < 10 KB")

if __name__ == "__main__":
    main()
