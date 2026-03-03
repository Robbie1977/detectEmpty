#!/usr/bin/env python3
"""
Analyze both Brain and VNC folders to identify empty ones using a reference empty folder.
Use 3ftr VNC as the baseline for empty folders and find others with same signature.
"""

import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict

# Brain folders (VFB_00101567)
brain_folders = [
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kle/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kjs/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3kjn/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftr/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftt/VFB_00101567/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftv/VFB_00101567/",
]

# VNC folders (VFB_00200000)
vnc_folders = [
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftr/VFB_00200000/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftt/VFB_00200000/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftv/VFB_00200000/",
]

def get_directory_details(url):
    """Fetch directory listing and get detailed file information."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        pre_tag = soup.find('pre')
        if not pre_tag:
            return {}, 0
        
        files = {}
        total_size = 0
        
        lines = pre_tag.get_text().split('\n')
        
        for line in lines:
            if not line.strip() or '../' in line:
                continue
            
            parts = line.split()
            if len(parts) >= 3:
                try:
                    size = int(parts[-1])
                    filename_match = re.search(r'^(\S+)', line)
                    if filename_match:
                        filename = filename_match.group(1)
                        files[filename] = size
                        total_size += size
                except ValueError:
                    pass
        
        return files, total_size
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}, None

def extract_folder_code(url):
    """Extract folder code from URL."""
    match = re.search(r'/jrmc/([^/]+)/', url)
    return match.group(1) if match else None

def extract_template(url):
    """Extract template type from URL (Brain or VNC)."""
    if 'VFB_00101567' in url:
        return 'Brain'
    elif 'VFB_00200000' in url:
        return 'VNC'
    return 'Unknown'

def main():
    print("Analyzing Brain and VNC folders to identify empty ones")
    print("Reference: 3ftr VNC (121.82 MB - confirmed empty)")
    print("=" * 120)
    
    results = defaultdict(dict)
    
    # Check Brain folders
    print("\nBRAIN FOLDERS (VFB_00101567)")
    print("-" * 120)
    for url in brain_folders:
        folder_code = extract_folder_code(url)
        files, total_size = get_directory_details(url)
        
        if total_size is not None:
            results[folder_code]['brain'] = {
                'size': total_size,
                'files': files,
                'file_count': len(files)
            }
            print(f"{folder_code}: {total_size / (1024**2):.2f} MB ({len(files)} files)")
    
    # Check VNC folders
    print("\nVNC FOLDERS (VFB_00200000)")
    print("-" * 120)
    for url in vnc_folders:
        folder_code = extract_folder_code(url)
        files, total_size = get_directory_details(url)
        
        if total_size is not None:
            results[folder_code]['vnc'] = {
                'size': total_size,
                'files': files,
                'file_count': len(files)
            }
            print(f"{folder_code}: {total_size / (1024**2):.2f} MB ({len(files)} files)")
    
    print("\n" + "=" * 120)
    print("EMPTY FOLDER ANALYSIS")
    print("=" * 120)
    
    # Reference empty sizes
    vnc_3ftr_size = 121.82 * (1024**2)  # bytes
    
    print(f"\nReference empty VNC folder: 3ftr = {121.82:.2f} MB = 127,732,395 bytes")
    print("\nLooking for folders with matching signatures...")
    print("-" * 120)
    
    empty_brain_folders = []
    empty_vnc_folders = []
    
    for folder_code, data in sorted(results.items()):
        print(f"\n{folder_code}:")
        
        if 'brain' in data:
            brain_size = data['brain']['size']
            brain_mb = brain_size / (1024**2)
            print(f"  Brain: {brain_mb:.2f} MB")
            
            # Check if size matches empty pattern (only template files, no expression)
            # Empty Brain folders are much smaller (~8-12 MB based on our earlier analysis)
            if brain_mb < 20:  # Small Brain folders are likely empty
                print(f"    -> LIKELY EMPTY (small size)")
                empty_brain_folders.append(folder_code)
        
        if 'vnc' in data:
            vnc_size = data['vnc']['size']
            vnc_mb = vnc_size / (1024**2)
            print(f"  VNC: {vnc_mb:.2f} MB")
            
            # Check if close to reference empty size
            size_diff = abs(vnc_size - vnc_3ftr_size)
            size_diff_pct = (size_diff / vnc_3ftr_size) * 100
            
            if size_diff_pct < 2:  # Within 2% of reference
                print(f"    -> LIKELY EMPTY (matches 3ftr signature)")
                empty_vnc_folders.append(folder_code)
    
    print("\n" + "=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print(f"\nLikely empty Brain folders: {empty_brain_folders if empty_brain_folders else 'None identified in sample'}")
    print(f"Likely empty VNC folders: {empty_vnc_folders if empty_vnc_folders else 'None identified in sample'}")

if __name__ == "__main__":
    main()
