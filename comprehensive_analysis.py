#!/usr/bin/env python3
"""
Comprehensive analysis of all Brain folders to identify empty ones.
Uses file size signatures from known empty folders: 3kle (8.34 MB) and 3ftr (121.27 MB)
"""

import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict

# All 97 Brain folders from the original list
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

def get_directory_size(url):
    """Fetch directory listing and calculate total file size."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        pre_tag = soup.find('pre')
        if not pre_tag:
            return 0
        
        total_size = 0
        lines = pre_tag.get_text().split('\n')
        
        for line in lines:
            if not line.strip() or '../' in line:
                continue
            
            parts = line.split()
            if len(parts) >= 3:
                try:
                    size = int(parts[-1])
                    total_size += size
                except ValueError:
                    pass
        
        return total_size
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_folder_code(url):
    """Extract folder code from URL."""
    match = re.search(r'/jrmc/([^/]+)/', url)
    return match.group(1) if match else None

def main():
    print("Scanning ALL Brain folders for empty signatures")
    print("Empty signatures identified:")
    print("  - 3kle: 8.34 MB (base Brain template, no expression)")
    print("  - 3ftr: 121.27 MB (complete template, no expression)")
    print("=" * 100)
    
    results = {}
    
    for i, url in enumerate(brain_folders, 1):
        folder_code = extract_folder_code(url)
        total_size = get_directory_size(url)
        
        if total_size is not None:
            results[folder_code] = total_size
            mb = total_size / (1024**2)
            print(f"[{i:2d}/97] {folder_code}: {mb:7.2f} MB")
    
    print("\n" + "=" * 100)
    print("EMPTY FOLDER IDENTIFICATION")
    print("=" * 100)
    
    # Known empty sizes (with tolerance for slight variations)
    empty_size_1 = 8.34 * (1024**2)  # 3kle
    empty_size_2 = 121.27 * (1024**2)  # 3ftr
    tolerance = 0.5 * (1024**2)  # ±0.5 MB tolerance
    
    empty_folders = []
    
    for folder_code, size in sorted(results.items()):
        mb = size / (1024**2)
        
        # Check if matches empty signature 1 (base Brain template ~8.34 MB)
        if abs(size - empty_size_1) < tolerance:
            empty_folders.append((folder_code, mb, "Base template (no expression)"))
        # Check if matches empty signature 2 (complete template ~121.27 MB)
        elif abs(size - empty_size_2) < tolerance:
            empty_folders.append((folder_code, mb, "Complete template (no expression)"))
    
    if empty_folders:
        print(f"\nFolders to BLOCK (identified empty):")
        print("-" * 100)
        for folder_code, mb, reason in sorted(empty_folders):
            print(f"{folder_code}: {mb:.2f} MB - {reason}")
        
        print(f"\n\nFinal BLOCK LIST ({len(empty_folders)} folders):")
        print("-" * 100)
        for folder_code, _, _ in sorted(empty_folders):
            print(folder_code)
    else:
        print("\nNo additional empty folders found matching known signatures.")

if __name__ == "__main__":
    main()
