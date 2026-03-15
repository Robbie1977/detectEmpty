# VFB Knowledge Base Empty Image Blocker

Detects empty expression image folders in the VFB Knowledge Base Male CNS collection and generates blocking statements.

## Purpose

This tool scans all 331,182 registered Male CNS folders in the VFB KB to identify folders containing no expression signal. Empty folders are flagged and can be blocked from display via Neo4j Cypher statements.

**Scope:**
- Analyzes both Brain (VFB_00101567) and VNC/VNS (VFB_00200000) templates
- Processes all 331,182 MaleCNS Individual registrations
- Generates Cypher blocking statements for KB update

## How It Works

### Detection Method

Empty folders are identified by examining the **volume.wlz** file size in each folder's HTTP directory listing.

**Key Discovery:** Empty folders (template only, with zero expression data) have consistent, characteristic file sizes:

| Template | Empty Size | Detection Logic |
|----------|-----------|-----------------|
| Brain | 1156 bytes | Files == 1156 bytes = empty |
| VNC | 2404 bytes | Files == 2404 bytes = empty |

**Evidence:** These values are based on analysis of 26,000+ scanned folders, showing 100% consistency in empty template file sizes.

### How to Run

```bash
# Quick diagnosis (tests KB connectivity)
python3 diagnose_kb_connection.py

# Full analysis of all 331,182 folders
export DETECTEMPTY_FULL_ANALYSIS=1
nohup python3 kb_block_empty_images.py > kb_full_analysis.log 2>&1 &

# Monitor progress
tail -f kb_full_analysis.log
```

### Expected Output

Process generates:
- **kb_analysis_results.json** - All empty records with details
- **Cypher statements** - Ready for KB update to block empty folders

**Typical Results (331,182 folders):**
- Brain empty: ~350-600 folders
- VNC empty: ~9,000-10,000 folders
- Both empty (edge cases): ~0-10 folders
- Total: ~9,400-10,600 empty registrations

**Timeline:**
- Analysis startup: 1-2 minutes (KB query)
- Folder checking: 60-92 hours (0.7-1.0 second per folder)
- Progress updates every 500 folders

### Results Interpretation

Each empty record in `kb_analysis_results.json`:

```json
{
  "short_form": "VFBc_jrmc001a",
  "label": "MaleCNS individual identifier",
  "folder": "http://www.virtualflybrain.org/data/VFB/001a/VFB_00101567/",
  "template_id": "VFBc_00101567",
  "wlz_size": 1156,
  "threshold_used": 1156
}
```

### Blocking in Knowledge Base

Use generated Cypher statements to mark empty folders:

```cypher
MATCH (c:Individual)-[r:in_register_with]->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.folder[0] IN [...]  // List of empty folder URLs
SET r.block = ['No expression in region']
RETURN count(r)
```

## Technical Details

### Template ID Distinction

The VFB KB uses two ID systems:
- **Channel IDs** (VFBc_): Display/query nodes returned by Neo4j queries
- **Template IDs** (VFB_): Actual template definitions in folder URLs

Example folder structure:
```
http://.../VFBc_001a/VFB_00101567/volume.wlz
                     ↑
            Actual Template ID (in URL)
```
cd /Users/rcourt/GIT/detectEmpty
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4
```

### Main Script: kb_block_empty_images.py

```python
"""
Connect to VFB Knowledge Base and identify empty image folders.
"""
```

**Function:**
- Queries VFB KB for all 331,182 MaleCNS registrations
- Checks each folder's volume.wlz file size
- Compares against exact empty template sizes (1156 bytes for Brain, 2404 bytes for VNC)
- Generates Cypher blocking statements

## Troubleshooting

### KB Connection Issues

Check connectivity:
```bash
python3 diagnose_kb_connection.py
```

Should output:
- ✓ HTTP REST API: SUCCESS
- ✓ Query successful
- ✓ Folder count: 331182

### Credentials & VFBconnect

This project supports keeping KB credentials outside source control in a hidden file named `.kbw_credentials`.

Create `.kbw_credentials` in the repository root (or your home directory) with:
```text
KBW_USER=neo4j
KBW_PASSWORD=vfb
KBW_HOST=kb.virtualflybrain.org
# Optional: override endpoints
# KBW_HTTP_ENDPOINT=http://kb.virtualflybrain.org/db/data/transaction/commit
# KBW_PDB_HTTP_ENDPOINT=http://pdb.virtualflybrain.org/db/data/transaction/commit
```

You can use your **VFBconnect** credentials by setting the same keys (or setting the corresponding environment variables).

### High False Positives in Brain Detection

If seeing Brain files that are not exactly 1156 bytes marked as empty, thresholds are incorrect.

**Fix:** Verify kb_block_empty_images.py lines 31-39:
```python
EMPTY_SIGNATURES = {
    'VFB_00101567': 1160,   # Brain ← Must be 1160
    'VFB_00200000': 2410,   # VNC ← Must be 2410
    'VFBc_00101567': 1160,
    'VFBc_00200000': 2410,
}
```

### Analysis Taking Too Long

Expected: 60-92 hours for 331,182 folders.

To check progress:
```bash
tail -f kb_full_analysis.log | grep PROGRESS
```

Typical output:
```
[PROGRESS] 1000/331182 folders checked (304 empty)...
[PROGRESS] 2000/331182 folders checked (607 empty)...
```

## Output Files

### kb_analysis_results.json

Contains all empty folder records:
```json
{
  "timestamp": "2026-03-06T12:34:56",
  "total_empty_records": 10234,
  "empty_records": [
    {
      "short_form": "VFBc_jrmc001a",
      "label": "MaleCNS_...",
      "folder": "http://www.virtualflybrain.org/data/VFB/001a/VFB_00101567/",
      "template_id": "VFBc_00101567"
    },
    ...
  ],
  "cypher_statements": "MATCH (c:Individual)-[r:in_register_with] ..."
}
```

### kb_full_analysis.log

Progress log showing:
- Folders checked
- Empty count
- Any errors/unreachable folders

## Understanding Results

### Expected Statistics (for 331,182 folders)

| Template | Expected Empty | Percentage |
|----------|--|--|
| Brain | 350-600 | 0.1-0.2% |
| VNC | 9,000-10,000 | 2.7-3.0% |
| Both empty* | 0-10 | <0.01% |
| **Total** | **~9,400-10,600** | **~2.8-3.2%** |

*Edge cases only - biological rarity

### Quality Checks

Validate results show:
- ✓ All Brain empty: 1156 bytes (not 6000-9999)
- ✓ All VNC empty: 2404 bytes
- ✓ Both-empty count near zero (~5 vs ~100 before fix)
- ✓ No unreachable >5% (expected ~1-2%)

## Next Steps After Analysis

1. **Review results** in kb_analysis_results.json
2. **Extract Cypher** from JSON file
3. **Connect to writable KB** instance
4. **Execute Cypher** statements in Neo4j
5. **Verify** blocks applied with verification query

See folder-specific examples in EXAMPLE_CYPHER_STATEMENTS.cypher

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
