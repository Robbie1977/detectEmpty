# VFB Male CNS Empty Expression Detector

Identifies VFB (Virtual Fly Brain) Male CNS image folders that contain no expression data and should be blocked from display.

## Purpose

Analyzes neuronal expression image folders for Male CNS connectome to identify:
- **Brain folders** (VFB_00101567) with no expression signal
- **VNC folders** (VFB_00200000) with no expression signal

These empty folders should be excluded from the respective viewers to avoid displaying blank templates.

## Key Findings

### Detection Method: volume.wlz File Size
The **volume.wlz** file is the compressed volumetric data representation. Empty folders (template only, no expression data) have characteristic minimal wlz sizes:

**Brain Template Empty Signature:**
- **3ler**: volume.wlz = 1,156 bytes
- All other Brain folders: wlz ≥ 21.4 KB (contain expression signal)

**VNC Template Empty Signature:**
- **3ftr, 3ftt, 3ftv**: volume.wlz = 2.3 KB (2,404 bytes) each
- All have confirmed empty thumbnails (blank template with zero signal)

### Block Lists

**Brain folders to block (1 folder):**
```
3ler
```

**VNC folders to block (3 folders):**
```
3ftr
3ftt
3ftv
```

## Methodology

### Approach Evolution
1. **Total folder size**: Initial hypothesis failed - total size didn't correlate with empty status
2. **Small wlz files**: Tested 52 folders with wlz < 50 KB - all had visible expression signal
3. **Tiny wlz files**: Identified folders with < 10 KB wlz files
4. **Visual verification**: Thumbnails confirmed only the smallest wlz files were truly empty
5. **Final discovery**: volume.wlz size alone is the reliable marker for empty folders

## Scripts

### Main Analysis Tools

- **`find_empty_brain.py`** - Scan all Brain folders for empty signatures (wlz < 10 KB)
  ```bash
  python find_empty_brain.py
  ```

- **`find_empty_vnc.py`** - Scan VNC folders for empty signatures (wlz < 10 KB)
  ```bash
  python find_empty_vnc.py
  ```

- **`analyze_wlz.py`** - Detailed analysis of volume.wlz file sizes across all folders
  ```bash
  python analyze_wlz.py
  ```

- **`download_thumbnails.py`** - Download thumbnail images for visual verification
  ```bash
  python download_thumbnails.py 1  # Download batch 1
  open thumbnails_brain/           # View the thumbnails
  ```

### Supporting Scripts

- `check_vnc_brain_images.py` - Early total folder size analysis
- `check_vnc_folders.py` - VNC folder analysis
- `find_empty_folders.py` - Comparative Brain vs VNC analysis
- `comprehensive_analysis.py` - All 97 Brain folders scanned for size patterns

## Installation & Usage

```bash
# Setup
cd ~/GIT/detectEmpty
source venv/bin/activate

# Run analysis
python find_empty_brain.py   # Find empty Brain folders
python find_empty_vnc.py     # Find empty VNC folders

# Download visual samples
python download_thumbnails.py 1
open empty_candidates/       # View the smallest wlz thumbnails
```

## Analysis Results

### Brain Folders Analyzed: 98 total
- Empty (wlz < 10 KB): **1 folder** (3ler)
- Has expression (wlz ≥ 21 KB): 97 folders
- Size distribution: 1,156 bytes → 210.8 KB wlz files

### VNC Folders Analyzed: 3 total  
- Empty (wlz ≤ 10 KB): **3 folders** (3ftr, 3ftt, 3ftv)
- All confirmed empty by visual thumbnail inspection

## Key References

### Empty Folder Examples
- **3ler (Brain)**: wlz = 1,156 bytes - blank template thumbnail
- **3ftr (VNC)**: wlz = 2.3 KB - blank template thumbnail (reference for "empty" appearance)

### Non-Empty Comparative Examples  
- **3js7 (Brain)**: wlz = 21.4 KB - has expression signal
- **3ftt (VNC)**: wlz = 2.3 KB (empty volume.wlz) but 718 MB total with _bounded files
- **3ftv (VNC)**: wlz = 2.3 KB (empty volume.wlz) but 154.56 MB total with data

## Technical Notes

- Apache directory listings provide file sizes via HTTP GET
- BeautifulSoup parses HTML directory listings
- volume.wlz is the compressed volumetric representation (Woolz format)
- Empty templates have wlz file sizes under 3 KB due to no expression data
- Total folder size can be misleading (other files like .obj, thumbnails vary)
- Visual thumbnail inspection confirms empty status when wlz suggests empty

## Files in Repository

- Analysis scripts (*.py)
- BLOCK_LIST.txt - Final consolidated block list
- empty_candidates/ - Sample Brain thumbnails from smallest wlz folders
- *.png - Reference thumbnails for empty folders (3ler, 3ftr, 3kle)
- README.md - This file

## Output Files

See [BLOCK_LIST.txt](BLOCK_LIST.txt) for the final consolidated block list ready for deployment.
