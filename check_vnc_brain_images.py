#!/usr/bin/env python3
"""
Check VFB Male CNS image directories to identify empty folders (no expression data in Brain region).
Compares file sizes to determine which folders contain only the base template with no data.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from collections import defaultdict

# All the folders to check - grouped by template
folders_brain = [
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

def get_directory_details(url):
    """Fetch directory listing and get detailed file information."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the <pre> tag containing the directory listing
        pre_tag = soup.find('pre')
        if not pre_tag:
            return {}, 0
        
        files = {}
        total_size = 0
        
        # Parse Apache directory listing format
        lines = pre_tag.get_text().split('\n')
        
        for line in lines:
            # Skip empty lines and parent directory
            if not line.strip() or '../' in line:
                continue
            
            # Match filename and size
            # Format: filename<spaces>date<spaces>size
            match = re.search(r'<a href="([^"]+)">([^<]+)</a>\s+(\d+-\w+-\d+\s+\d+:\d+)\s+(\d+)', line)
            if not match:
                # Try parsing the text version
                parts = line.split()
                if len(parts) >= 3:
                    # Last part should be size
                    try:
                        size = int(parts[-1])
                        # Filename is usually the first part before whitespace
                        filename_match = re.search(r'^(\S+)', line)
                        if filename_match:
                            filename = filename_match.group(1)
                            files[filename] = size
                            total_size += size
                    except ValueError:
                        pass
            else:
                filename = match.group(1)
                size = int(match.group(4))
                files[filename] = size
                total_size += size
        
        return files, total_size
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}, None

def extract_folder_code(url):
    """Extract folder code from URL (e.g., '3kle' from the URL)."""
    match = re.search(r'/jrmc/([^/]+)/', url)
    return match.group(1) if match else None

def main():
    print("Checking VFB Male CNS image directories...")
    print("=" * 100)
    
    folder_data = {}
    size_distribution = defaultdict(list)
    
    for url in folders_brain:
        folder_code = extract_folder_code(url)
        files, total_size = get_directory_details(url)
        
        if total_size is not None:
            folder_data[folder_code] = {
                'total_size': total_size,
                'files': files,
                'file_count': len(files)
            }
            size_distribution[int(total_size)].append(folder_code)
            print(f"{folder_code}: {total_size / (1024**2):.2f} MB ({len(files)} files)")
    
    print("\n" + "=" * 100)
    print("Analysis:")
    print("=" * 100)
    
    # Show file size distribution
    if size_distribution:
        sorted_sizes = sorted(size_distribution.keys())
        
        print(f"\nTotal folders checked: {len(folder_data)}")
        print(f"Unique total sizes found: {len(sorted_sizes)}")
        
        print("\nSize distribution:")
        print("-" * 100)
        for size in sorted_sizes[:10]:  # Show smallest sizes
            folders = size_distribution[size]
            print(f"Size {size / (1024**2):.2f} MB: {len(folders)} folder(s) - {folders}")
        
        # The smallest size likely represents empty folders (just base template)
        base_size = sorted_sizes[0]
        empty_folders = size_distribution[base_size]
        
        print("\n" + "=" * 100)
        print(f"BASE TEMPLATE SIZE (assumed empty): {base_size / (1024**2):.2f} MB")
        print(f"Number of EMPTY folders to BLOCK: {len(empty_folders)}")
        print("\nFolders to BLOCK (no expression in Brain region):")
        print("-" * 100)
        for folder in sorted(empty_folders):
            print(folder)

if __name__ == "__main__":
    main()
