# VFB KB Empty Image Folder Blocker - Implementation Summary

**Status**: ✅ **READY FOR USE**  
**Date**: March 3, 2026  
**Purpose**: Connect to VFB Knowledge Base and block empty image folders

---

## What This Does

Provides a **complete toolkit** to identify empty image folders in the VirtualFlyBrain Knowledge Base (no expression signal, template-only) and generate CYPHER statements to block them with `r.block = ['No expression in region']`.

## Key Findings

### Empty Folders Identified

Through analysis of `volume.wlz` file sizes:

| Template | Folder | Size | Status |
|----------|--------|------|--------|
| Brain (VFB_00101567) | 3ler | 1,156 bytes | ✓ Empty |
| VNC (VFB_00200000) | 3ftr | 2,404 bytes | ✓ Empty |
| VNC (VFB_00200000) | 3ftt | 2,404 bytes | ✓ Empty |
| VNC (VFB_00200000) | 3ftv | 2,404 bytes | ✓ Empty |

---

## Complete Workflow

### 1. **Export Data from KB** (5 min)

Run this Cypher query in Neo4j Browser at `http://kb.virtualflybrain.org`:

```cypher
MATCH (n:Individual)-[r:in_register_with]->(tc:Template) 
WHERE n.label contains 'MaleCNS' 
RETURN DISTINCT 
    n.short_form,
    n.label,
    r.folder[0],
    tc.short_form
ORDER BY tc.short_form, r.folder[0]
```

Export as CSV → `kb_registrations.csv`

### 2. **Format Results** (< 1 min)

```bash
python format_kb_results.py --input-file kb_registrations.csv --output kb_regs.tsv
```

**Output**: Standardized TSV file with columns: `short_form`, `label`, `folder`, `template_id`

### 3. **Test All Folders** (5-10 min)

```bash
python batch_test_folders.py \
    --input-file kb_regs.tsv \
    --output cypher_updates.cypher \
    --verbose
```

**Action**: Tests each folder for empty images by checking `volume.wlz` file size  
**Output**: `cypher_updates.cypher` with ready-to-use UPDATE statements

### 4. **Review Generated CYPHER** (2 min)

```bash
cat cypher_updates.cypher
```

Expected format:
```cypher
MATCH (n:Individual {short_form: 'VFB_...'})
  -[r:in_register_with]
  ->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.folder[0] = '3ler'
SET r.block = ['No expression in region']
RETURN n.short_form, r.folder[0], tc.short_form;
```

### 5. **Apply to KB** (Requires Write Access)

Connect to **writable KB instance** and execute:

```cypher
// Copy each statement from cypher_updates.cypher
// Paste and execute in Neo4j Browser
```

### 6. **Verify** (1 min)

```cypher
// Check blocks applied
MATCH (r:in_register_with)
WHERE r.block = ['No expression in region']
RETURN COUNT(r) as blocked_count
```

---

## Available Tools

### Main Scripts

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `batch_test_folders.py` | Test folders + generate CYPHER | TSV file or folder list | CYPHER file |
| `kb_block_empty_images.py` | Direct KB connection | (KB connection) | CYPHER file |
| `format_kb_results.py` | Convert Neo4j exports | CSV/JSON | TSV file |
| `kb_workflow.py` | Guided end-to-end workflow | User input | CYPHER + report |

### Helper Scripts

- `find_empty_brain.py` - Original Brain folder analysis
- `find_empty_vnc.py` - Original VNC folder analysis
- `analyze_wlz.py` - WLZ file analysis

---

## Quick Test Commands

### Test Known Folders (No KB Needed)

```bash
source venv/bin/activate
python batch_test_folders.py --known-only --verbose
```

**Output**: CYPHER statements for the 4 known empty folders (immediate)

### Test from KB Export

```bash
# Format export
python format_kb_results.py --input-file kb_export.csv --output kb_regs.tsv

# Test all folders
python batch_test_folders.py --input-file kb_regs.tsv --verbose
```

### Guided Workflow

```bash
python kb_workflow.py
# Follows you through all steps interactively
```

---

## File Structure

```
detectEmpty/
├── batch_test_folders.py          # ⭐ Primary tool
├── kb_block_empty_images.py       # Direct KB connection
├── format_kb_results.py           # Format converter
├── kb_workflow.py                 # Guided workflow
│
├── KB_INTEGRATION_README.md       # 📖 START HERE
├── KB_INTEGRATION_GUIDE.md        # Detailed guide
├── IMPLEMENTATION_SUMMARY.md      # This file
├── EXAMPLE_CYPHER_STATEMENTS.cypher
├── SAMPLE_GENERATED_CYPHER.cypher
│
├── find_empty_brain.py            # Original analysis
├── find_empty_vnc.py
├── analyze_wlz.py
├── compare_brain_vnc.py
│
├── README.md                      # Project overview
└── venv/                          # Virtual environment
```

---

## Key Concepts

### Empty Folder Detection

Uses **`volume.wlz` file size** percentile analysis:

- **Brain Template (VFB_00101567)**
  - Threshold: < 10 KB
  - Empty signature: ~1,156 bytes (template only)
  - All other folders: > 21 KB (contain expression data)

- **VNC Template (VFB_00200000)**
  - Threshold: < 4 KB  
  - Empty signature: ~2,404 bytes (template only)
  - Data folders: > 100 KB

### CYPHER Block Property

Sets relationship property:
```cypher
r.block = ['No expression in region']
```

Properties:
- Reversible: Can remove with `REMOVE r.block`
- Non-destructive: Only marks relationship, doesn't delete
- Follows VFB conventions for blocking reasons

---

## Example Output

### Input File (TSV)

```
short_form        label                folder    template_id
VFB_00001234      Example Neuron       3ler      VFB_00101567
VFB_00001235      Brain Neuron         3ler      VFB_00101567
VFB_00005678      VNC Female           3ftr      VFB_00200000
```

### Generated CYPHER

```cypher
// VFB KB Update: Block empty image folders
// Generated: 2026-03-03 18:28:06
// Total registrations to block: 3

MATCH (n:Individual {short_form: 'VFB_00001234'})-[r:in_register_with]->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.folder[0] = '3ler'
SET r.block = ['No expression in region']
RETURN n.short_form, r.folder[0], tc.short_form;

MATCH (n:Individual {short_form: 'VFB_00001235'})-[r:in_register_with]->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.folder[0] = '3ler'
SET r.block = ['No expression in region']
RETURN n.short_form, r.folder[0], tc.short_form;

MATCH (n:Individual {short_form: 'VFB_00005678'})-[r:in_register_with]->(tc:Template {short_form: 'VFB_00200000'})
WHERE r.folder[0] = '3ftr'
SET r.block = ['No expression in region']
RETURN n.short_form, r.folder[0], tc.short_form;

// Summary: 3 registrations blocked
```

---

## How To Use

### Scenario 1: Quick Local Test (2 minutes)

```bash
cd /Users/rcourt/GIT/detectEmpty
source venv/bin/activate
python batch_test_folders.py --known-only
# Outputs: cypher_block_updates.cypher
cat cypher_block_updates.cypher
```

✓ Verify it works without any KB connection

### Scenario 2: Test Real KB Data (15 minutes)

```bash
# 1. Export from KB Neo4j Browser → kb_export.csv

# 2. Format
python format_kb_results.py --input-file kb_export.csv --output kb_regs.tsv

# 3. Test
python batch_test_folders.py --input-file kb_regs.tsv --verbose

# 4. Review
cat cypher_block_updates.cypher
```

✓ Outputs CYPHER with real VFB IDs from your KB

### Scenario 3: Guided Workflow (20 minutes)

```bash
python kb_workflow.py
# Prompts you through all steps
# Generates CYPHER + report
```

✓ Complete end-to-end with progress tracking

---

## Technical Details

### Detection Method

1. **HTTP Request**: Fetch directory listing from VFB data server
   ```
   http://www.virtualflybrain.org/data/VFB/i/jrmc/{folder}/{template}/
   ```

2. **HTML Parse**: Extract `volume.wlz` file size from Apache directory listing

3. **Size Comparison**: Check against template-specific thresholds

4. **Result**: Classify as empty or data-containing

### Performance

- ~100 folders = ~100 HTTP requests
- ~10 seconds for complete scan (with 10s timeout per request)
- Non-invasive: read-only, no KB connections required

### Thresholds

Determined through statistical analysis:
- **Brain**: 1,156 bytes (empty) to 21-400+ KB (data)
- **VNC**: 2,404 bytes (empty) to 100+ KB (data)

Thresholds chosen at **significant bimodal gap** to ensure reliability.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'requests'` | `pip install requests beautifulsoup4` in venv |
| Cannot connect to KB | Use `--input-file` method with exported CSV |
| "Neo4j tools not available" | `pip install VFB_neo4j` or use batch tool |
| CYPHER doesn't execute | Check VFB IDs match KB (use `short_form` exactly) |
| Script too slow | Network latency; 10-second timeout per request is normal |

See **KB_INTEGRATION_README.md** for full troubleshooting guide.

---

## Security & Safety

✓ **Non-invasive**: Tests only read file sizes, no KB writes  
✓ **Reversible**: All changes can be undone with `REMOVE r.block`  
✓ **Validated**: CYPHER reviewed before execution  
✓ **Documented**: All statements include comments with reasoning  

---

## Next Steps

1. **Read**: [KB_INTEGRATION_README.md](KB_INTEGRATION_README.md) for complete details
2. **Test**: `python batch_test_folders.py --known-only` to verify setup
3. **Export**: Get KB registrations from Neo4j Browser
4. **Format**: `python format_kb_results.py` to standardize
5. **Analyze**: `python batch_test_folders.py --input-file` to test
6. **Review**: Check generated CYPHER statements
7. **Apply**: Copy to writable KB instance
8. **Verify**: Run verification queries

---

## References

- **VFB KB**: https://kb.virtualflybrain.org
- **VFB Data**: http://www.virtualflybrain.org/data/
- **VFB_reporting**: https://github.com/VirtualFlyBrain/VFB_reporting
- **Neo4j**: https://neo4j.com/docs/

---

## Support

- See **KB_INTEGRATION_README.md** for detailed guide
- Check **EXAMPLE_CYPHER_STATEMENTS.cypher** for working examples
- Review **SAMPLE_GENERATED_CYPHER.cypher** for expected output format

---

**Ready to use** ✅ All tools tested and validated  
**Last updated**: March 3, 2026
