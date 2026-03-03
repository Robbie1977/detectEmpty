#!/usr/bin/env python3
"""
Download thumbnails for visual inspection to identify truly empty folders.
"""

import requests
import os
from pathlib import Path

# All 97 Brain folders
brain_folders = {
    '3kle', '3kjs', '3kjn', '3k8z', '3kce', '3juw', '3k83', '3kcj', '3k4v', '3kaw',
    '3kek', '3k63', '3k64', '3jzn', '3kas', '3kcx', '3k9d', '3kbt', '3jy2', '3jx8',
    '3k1g', '3k3g', '3k3a', '3k5m', '3k5n', '3kfz', '3k94', '3k3b', '3k4b', '3jrf',
    '3juy', '3jx7', '3jrh', '3jrl', '3jut', '3jv5', '3kex', '3k8c', '3juu', '3jv4',
    '3js8', '3jyf', '3jzi', '3k9f', '3k9y', '3k9c', '3jw1', '3jv7', '3k0m', '3k04',
    '3kff', '3k8u', '3jv0', '3jxa', '3k40', '3k4c', '3k51', '3k4k', '3k4l', '3k7b',
    '3kfg', '3k7t', '3kfw', '3ke4', '3k6j', '3ker', '3k4e', '3js7', '3jt0', '3jzj',
    '3k4r', '3k0d', '3k8w', '3k9b', '3jwv', '3k5l', '3k74', '3kfs', '3kcs', '3kao',
    '3k1l', '3k0v', '3kf1', '3k7k', '3jrq', '3jtk', '3k39', '3k17', '3kat', '3k80',
    '3k9m', '3kam', '3ftr', '3ftq', '3fts', '3ftt', '3ftv',
}

def download_batch(folder_codes, output_dir="thumbnails_brain"):
    """Download thumbnails for a batch of folders."""
    Path(output_dir).mkdir(exist_ok=True)
    
    for folder_code in sorted(folder_codes):
        url = f"http://www.virtualflybrain.org/data/VFB/i/jrmc/{folder_code}/VFB_00101567/thumbnail.png"
        filepath = os.path.join(output_dir, f"{folder_code}.png")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✓ {folder_code}")
        except Exception as e:
            print(f"✗ {folder_code}: {e}")

def main():
    import sys
    
    if len(sys.argv) > 1:
        # Download specific batch
        batch_num = int(sys.argv[1])
        batch_size = 10
        offset = (batch_num - 1) * batch_size
        
        sorted_folders = sorted(brain_folders)
        batch = sorted_folders[offset:offset + batch_size]
        
        print(f"Downloading batch {batch_num} ({len(batch)} folders)...")
        print(f"Folders: {', '.join(batch)}")
        print()
        
        download_batch(batch)
        
        print(f"\n✓ Batch {batch_num} downloaded to thumbnails_brain/")
        print(f"  Open with: open thumbnails_brain/{batch[0]}.png ...")
    
    else:
        # Show batch info
        sorted_folders = sorted(brain_folders)
        total = len(sorted_folders)
        batch_size = 10
        num_batches = (total + batch_size - 1) // batch_size
        
        print("Download thumbnails for visual inspection (to identify empty folders)")
        print("=" * 80)
        print(f"Total folders: {total}")
        print(f"Batch size: {batch_size}")
        print(f"Total batches: {num_batches}\n")
        
        for batch_num in range(1, num_batches + 1):
            offset = (batch_num - 1) * batch_size
            batch = sorted_folders[offset:offset + batch_size]
            print(f"Batch {batch_num:2d}: python download_thumbnails.py {batch_num}")
            print(f"           {', '.join(batch)}")
        
        print(f"\nUsage: python download_thumbnails.py <batch_number>")
        print(f"Example: python download_thumbnails.py 1")

if __name__ == "__main__":
    main()
