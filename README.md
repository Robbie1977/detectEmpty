# VFB Male CNS Empty Expression Detector

Identifies VFB (Virtual Fly Brain) Male CNS image folders that contain no expression data in the Brain region and should be blocked from display.

## Purpose

When syncing neuronal expression data to the Male CNS template (VFB_00101567), some folders contain expression data only in the VNC template (VFB_00200000) and no expression in the Brain region. These folders should be excluded from the Brain viewer.

This tool analyzes directory listings to identify which folders contain only the base template with no expression data.

## Usage

```bash
# Install dependencies
source venv/bin/activate
pip install requests beautifulsoup4

# Run the analysis
python check_vnc_brain_images.py
```

## Output

The script checks all Male CNS Brain image directories and identifies those with the base template size (no additional expression data). It outputs:

1. All folders with their total sizes
2. Size distribution analysis
3. List of folders to BLOCK (those with no Brain region expression data)

## Methodology

- Fetches Apache directory listings for each folder via HTTP
- Parses file sizes from the directory listing
- Identifies the base template size (smallest folders contain only the template)
- Reports all folders matching the base template size as "empty" (no expression in Brain)

## Files

- `check_vnc_brain_images.py` - Main analysis script
- `venv/` - Python virtual environment

## Example Output

```
BASE TEMPLATE SIZE (assumed empty): 8.34 MB
Number of EMPTY folders to BLOCK: 1

Folders to BLOCK (no expression in Brain region):
3kle
```
