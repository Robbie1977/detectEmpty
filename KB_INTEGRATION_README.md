# VFB Knowledge Base Integration - Empty Image Folder Blocker

## Overview

This toolkit provides a complete workflow for connecting to the Virtual Fly Brain (VFB) Knowledge Base and marking empty image folders with `block=['No expression in region']` on their `in_register_with` relationship edges.

**Problem**: Some image folders in the VFB data contain no expression signal—they're template-only registrations. These should be excluded from display.

**Solution**: Detect empty folders via volume.wlz file analysis and generate CYPHER statements to block them in the KB.

## Quick Start

### 1. Test Known Empty Folders Locally

```bash
source venv/bin/activate
python batch_test_folders.py --known-only --verbose
# Output: cypher_block_updates.cypher
```

### 2. Get Real Data from KB

```cypher
# Run in Neo4j Browser at http://kb.virtualflybrain.org
MATCH (n:Individual)-[r:in_register_with]->(tc:Template) 
WHERE n.label contains 'MaleCNS' 
RETURN DISTINCT 
    n.short_form,
    n.label,
    r.folder[0],
    tc.short_form
ORDER BY tc.short_form, r.folder[0]
```

Export as CSV from Browser → `kb_registrations.csv`

### 3. Format Results

```bash
python format_kb_results.py --input-file kb_registrations.csv --output kb_regs.tsv
```

### 4. Test All Folders

```bash
python batch_test_folders.py --input-file kb_regs.tsv --verbose
# Output: cypher_block_updates.cypher
```

### 5. Apply to Writable KB

```cypher
# In writable KB instance Neo4j Browser
:open 'path/to/cypher_block_updates.cypher'
# Execute each statement
```

## Tools

### `batch_test_folders.py` ⭐ **USE THIS FIRST**

Primary tool for batch testing folders and generating CYPHER.

**Features:**
- Tests each folder for empty images (non-invasive)
- Generates KB-ready CYPHER statements
- Formats output for manual KB update
- Supports multiple input methods

**Usage:**

```bash
# From known empty folders
python batch_test_folders.py --known-only

# From folder list
python batch_test_folders.py --test-folders 3ler,3ftr,3ftt,3ftv

# From KB export
python batch_test_folders.py --input-file registrations.tsv

# Options
python batch_test_folders.py --help
```

### `kb_block_empty_images.py`

Direct KB connection (requires VFB_neo4j library).

**Usage:**

```bash
# Direct KB query (if VFB_neo4j installed)
python kb_block_empty_images.py

# Save to file
python kb_block_empty_images.py --save-cypher output.cypher
```

**Note:** Falls back gracefully if Neo4j tools unavailable.

### `format_kb_results.py`

Convert Neo4j Browser exports to standardized TSV format.

**Usage:**

```bash
python format_kb_results.py --input-file export.csv --output kb_regs.tsv
```

**Accepts:** CSV, JSON, TSV

## Detection Criteria

### Brain (VFB_00101567)
- **Threshold**: `volume.wlz` < 10 KB
- **Known empty**: `3ler` (1,156 bytes)
- **Method**: Extract file size from HTTP directory listing

### VNC (VFB_00200000)  
- **Threshold**: `volume.wlz` < 4 KB
- **Known empty**: `3ftr`, `3ftt`, `3ftv` (2,404 bytes each)
- **Method**: Extract file size from HTTP directory listing

## Technical Clarification: Template IDs vs Channel Nodes

**Critical distinction for folder URL construction:**

### KB Structure
- **Template Nodes** (VFB_00101567, VFB_00200000): Underlying data templates
- **Channel Nodes** (VFBc_00101567, VFBc_00200000): Display/UI channels in the KB

Individuals are registered to Channel nodes, but their folder URLs reference the actual Template IDs.

### In VFB Data URLs (Apache Directory Listings)
Use **full Template IDs**: `VFB_00101567`, `VFB_00200000`

```
http://www.virtualflybrain.org/data/VFB/i/jrmc/{folder_code}/{VFB_TEMPLATE_ID}/
                                                                  ↑
                                              Full template ID (VFB_...)
                                     Stored in r.folder[0] from KB registrations
```

**Example URLs (from actual KB data):**
- Brain: `http://www.virtualflybrain.org/data/VFB/i/jrmc/0000/VFB_00101567/`
- VNC:   `http://www.virtualflybrain.org/data/VFB/i/jrmc/0000/VFB_00200000/`

**Important:** Individuals are registered to Channel nodes (VFBc_), but the folder URLs in those registrations already contain the full Template IDs (VFB_), so the script uses those directly.

### In KB Cypher Queries for Updates
When generating blocking statements, use the Template ID that appears in the folder URLs:

```cypher
MATCH (n:Individual)-[r:in_register_with]->(tc:Template {short_form: 'VFB_00101567'})
                                                           ↑
                                        Template ID from folder URL
```

### Volume.wlz Size Check
The `volume.wlz` file is accessed via HTTP directory listing at the full URL:

```
GET http://www.virtualflybrain.org/data/VFB/i/jrmc/{folder}/{VFB_TEMPLATE_ID}/
→ Parse HTML directory listing for volume.wlz file size
→ Compare against threshold:
   - Brain (VFB_00101567): < 10 KB = empty
   - VNC (VFB_00200000): < 4 KB = empty
```

## File Formats

### Input: KB Registrations (TSV)

```
short_form        label              folder    template_id
VFB_00012345      Example Neuron     3ler      VFB_00101567
VFB_00012346      Another Neuron     3ler      VFB_00101567
VFB_00020001      VNC Neuron         3ftr      VFB_00200000
```

### Output: CYPHER Statements

```cypher
// VFB KB Update: Block empty image folders
// Generated: 2026-03-03 18:28:06

MATCH (n:Individual {short_form: 'VFB_00012345'})-[r:in_register_with]->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.folder[0] = '3ler'
SET r.block = ['No expression in region']
RETURN n.short_form as individual, r.folder[0] as folder, tc.short_form as template;
```

## Complete Workflow

### 1. **Export from VFB KB**

Use Neo4j Browser at `http://kb.virtualflybrain.org`:

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

Download as CSV.

### 2. **Format Results**

```bash
python format_kb_results.py \
    --input-file kb_export.csv \
    --output kb_registrations.tsv
```

### 3. **Test Folders**

```bash
python batch_test_folders.py \
    --input-file kb_registrations.tsv \
    --output cypher_blocks.cypher \
    --verbose
```

Sample output:
```
Testing 3ler in Brain (VFB_00101567)...
    🚫 3ler: 1,156 bytes (EMPTY)

Testing 3ftr in VNC (VFB_00200000)...
    🚫 3ftr: 2,404 bytes (EMPTY)
```

### 4. **Review CYPHER**

```bash
cat cypher_blocks.cypher
```

### 5. **Connect to Writable KB**

Access the **writable KB instance** (not public read-only):
- Contact VFB team for credentials
- Use Neo4j Browser, command-line client, or API

### 6. **Execute CYPHER**

Option A: One statement at a time
```cypher
// Paste each statement individually
MATCH (n:Individual {short_form: 'VFB_00012345'})...
```

Option B: Batch with transaction
```cypher
:begin
// Paste all statements
:commit
```

Option C: Via apoc procedure
```cypher
CALL apoc.periodic.iterate(
  "UNWIND $stmts AS stmt RETURN stmt",
  "CALL apoc.cypher.run(stmt, {}) YIELD value RETURN 1",
  {batchSize: 10, params: {stmts: [...all_statements...]}}
)
```

### 7. **Verify**

```cypher
// Check count
MATCH (r:in_register_with)
WHERE r.block = ['No expression in region']
RETURN COUNT(r) as blocked_count;

// Check specific
MATCH (n:Individual)-[r:in_register_with]->(tc:Template)
WHERE r.block = ['No expression in region']
RETURN DISTINCT r.folder[0] as blocked_folders;
```

## Examples

### Example 1: Known Empty Folders Only

```bash
$ python batch_test_folders.py --known-only --verbose

======================================================================
TESTING FOLDERS FOR EMPTY IMAGES
======================================================================

Testing 3ler in Brain (VFB_00101567)...
    🚫 3ler: 1,156 bytes (EMPTY)

Testing 3ftv in VNC (VFB_00200000)...
    🚫 3ftv: 2,404 bytes (EMPTY)

[OK] Saved to /Users/rcourt/GIT/detectEmpty/cypher_block_updates.cypher

[SUMMARY] Found 4 empty folder registrations
```

### Example 2: From KB Export

```bash
# 1. Export from Neo4j Browser → kb_regs.csv

# 2. Format
$ python format_kb_results.py --input-file kb_regs.csv --output kb_regs.tsv
[INFO] Reading kb_regs.csv...
[OK] Parsed 87 records
[OK] Saved to kb_regs.tsv

# 3. Test
$ python batch_test_folders.py --input-file kb_regs.tsv --output blocks.cypher
[OK] Loaded 87 registrations from kb_regs.tsv
Testing 3ler in Brain (VFB_00101567)...
    🚫 3ler: 1,156 bytes (EMPTY)
...

# 4. Apply to KB
# Copy blocks.cypher content to writable KB Neo4j Browser
```

### Example 3: Verify Before/After

```cypher
// BEFORE
MATCH (r:in_register_with) RETURN COUNT(r) as total_edges; // Should be some number

// Apply CYPHER updates...

// AFTER
MATCH (r:in_register_with) WHERE r.block = ['No expression in region']
RETURN COUNT(r) as blocked_edges;  // Should match number from script
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "requests module not found" | `pip install requests beautifulsoup4` |
| "Could not fetch size for folder" | Check folder code is correct, verify network access |
| "Neo4j tools not available" | Use `--input-file` method instead |
| "No columns detected" | Ensure input file is valid CSV/TSV with headers |
| "Generated CYPHER doesn't work" | Check VFB IDs match KB (use `n.short_form`) |

## Performance Considerations

- Each folder test makes 1 HTTP request to VFB data server
- ~100 folders = ~100 HTTP requests (~5-10 seconds typical)
- Script includes 10-second timeout per request
- Non-invasive: read-only file size checks only

## Security

- No credentials required for folder testing
- Only writable KB update step requires credentials
- CYPHER statements are declarative (no delete/drop)
- All changes reversible with `REMOVE r.block`

## Related Resources

- **VFB Knowledge Base**: https://kb.virtualflybrain.org
- **VFB_reporting**: https://github.com/VirtualFlyBrain/VFB_reporting
- **Neo4j Documentation**: https://neo4j.com/docs/
- **VFB Data**: http://www.virtualflybrain.org/data/

## Project Files

```
kb_integration/
├── batch_test_folders.py           # ⭐ Main testing tool
├── kb_block_empty_images.py         # Direct KB connection
├── format_kb_results.py             # Format converter
├── KB_INTEGRATION_GUIDE.md          # Detailed guide
├── KB_INTEGRATION_README.md         # This file
├── EXAMPLE_CYPHER_STATEMENTS.cypher # Example output
├── README.md                        # Project overview
└── venv/                            # Virtual environment
```

## Next Steps

1. **Test locally**: `python batch_test_folders.py --known-only`
2. **Get KB data**: Run Cypher query in Neo4j Browser
3. **Format results**: `python format_kb_results.py`
4. **Test all folders**: `python batch_test_folders.py --input-file`
5. **Review output**: `cat cypher_block_updates.cypher`
6. **Apply to KB**: Copy CYPHER to writable KB instance
7. **Verify**: Run verification queries

## Support

For issues or questions:
1. Check [EXAMPLE_CYPHER_STATEMENTS.cypher](EXAMPLE_CYPHER_STATEMENTS.cypher) for working examples
2. Review [KB_INTEGRATION_GUIDE.md](KB_INTEGRATION_GUIDE.md) for detailed workflow
3. Test with `--known-only` flag first to verify setup
4. Use `--verbose` flag for debugging

---

**Status**: Ready for use ✓  
**Last Updated**: 2026-03-03  
**Tested Folders**: Brain (3ler), VNC (3ftr, 3ftt, 3ftv)
