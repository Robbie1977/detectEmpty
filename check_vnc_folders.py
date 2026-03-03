#!/usr/bin/env python3
"""
Check VFB Male CNS VNC image directories to identify empty folders.
"""

import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict

# VNC folders from the user's list - these are the ones with VFB_00200000
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

def main():
    print("Checking VFB Male CNS VNC image directories...")
    print("=" * 100)
    
    size_results = []
    
    for url in vnc_folders:
        folder_code = extract_folder_code(url)
        files, total_size = get_directory_details(url)
        
        if total_size is not None:
            size_results.append({
                'folder': folder_code,
                'url': url,
                'size': total_size,
                'files': files,
                'file_count': len(files)
            })
            print(f"{folder_code} (VNC): {total_size / (1024**2):.2f} MB ({len(files)} files)")
            for fname, fsize in sorted(files.items()):
                print(f"  - {fname}: {fsize / 1024:.1f} KB")
    
    print("\n" + "=" * 100)
    print("Analysis:")
    print("=" * 100)
    
    if size_results:
        # Sort by size
        sorted_results = sorted(size_results, key=lambda x: x['size'])
        
        smallest = sorted_results[0]
        print(f"\nSmallest VNC folder: {smallest['folder']}")
        print(f"Size: {smallest['size'] / (1024**2):.2f} MB")
        print(f"URL: {smallest['url']}")
        print(f"\nFile breakdown:")
        for fname, fsize in sorted(smallest['files'].items()):
            print(f"  {fname}: {fsize / 1024:.1f} KB")
        
        return smallest

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n\nSmallest VNC folder code: {result['folder']}")
