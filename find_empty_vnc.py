#!/usr/bin/env python3
"""
Find all empty VNC folders using wlz file size.
Reference: 3ftr (VNC) = 2.3 KB volume.wlz (confirmed empty)
"""

import requests
from bs4 import BeautifulSoup
import re

# All VNC folders from the original dataset (VFB_00200000)
vnc_folders = [
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftr/VFB_00200000/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftt/VFB_00200000/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftv/VFB_00200000/",
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
    print("Analyzing VNC folders for empty wlz signatures")
    print("Reference: 3ftr (VNC) = 2.3 KB (confirmed empty)")
    print("=" * 100)
    
    results = {}
    empty_vnc_folders = []
    
    for i, url in enumerate(vnc_folders, 1):
        folder_code = extract_folder_code(url)
        wlz_size = get_wlz_size(url)
        
        if wlz_size is not None:
            results[folder_code] = wlz_size
            kb = wlz_size / 1024
            
            # Flag as empty if < 10 KB (similar threshold to Brain folders)
            if wlz_size < 10 * 1024:
                empty_vnc_folders.append((folder_code, wlz_size))
                print(f"[{i}/{len(vnc_folders)}] {folder_code}: {kb:6.1f} KB ({wlz_size:8,} bytes) 👈 EMPTY")
            else:
                print(f"[{i}/{len(vnc_folders)}] {folder_code}: {kb:6.1f} KB ({wlz_size:8,} bytes)")
    
    print("\n" + "=" * 100)
    print("RESULTS")
    print("=" * 100)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    
    print("\nAll VNC folders sorted by wlz size:")
    print("-" * 100)
    for folder_code, size in sorted_results:
        kb = size / 1024
        print(f"  {folder_code}: {kb:6.1f} KB ({size:8,} bytes)")
    
    if empty_vnc_folders:
        print(f"\n\nEmpty VNC folders (wlz < 10 KB):")
        print("-" * 100)
        for folder_code, size in sorted(empty_vnc_folders, key=lambda x: x[1]):
            kb = size / 1024
            print(f"  {folder_code}: {kb:6.1f} KB ({size:8,} bytes)")
        
        print(f"\n\nVNC BLOCK LIST ({len(empty_vnc_folders)} folders):")
        print("-" * 100)
        for folder_code, _ in sorted(empty_vnc_folders):
            print(folder_code)
    else:
        print("\nNo empty VNC folders found in this sample")

if __name__ == "__main__":
    main()
