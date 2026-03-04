# VFB KB Empty Image Blocker - Implementation Guide

## Overview

This suite of tools connects to the VirtualFlyBrain (VFB) Knowledge Base and identifies empty image folders that should be blocked from display. Empty folders are detected based on `volume.wlz` file size signatures.

## Tools

### 1. `batch_test_folders.py` - Primary Batch Testing Tool

Test folders for empty images and generate CYPHER update statements.

**Usage:**

```bash
# Test known empty folders
python batch_test_folders.py --known-only --output cypher_updates.cypher

# Test specific folders
python batch_test_folders.py --test-folders 3ler,3ftr --output updates.cypher

# Test from KB query results file
python batch_test_folders.py --input-file kb_registrations.txt --output cypher_updates.cypher

# Verbose output
python batch_test_folders.py --known-only --verbose
```

### 2. `kb_block_empty_images.py` - Direct KB Connection Tool

Connects to VFB KB directly to query MaleCNS individuals and test their registered folders.

**Requirements:**
- Must have `uk.ac.ebi.vfb.neo4j.neo4j_tools` available (from VFB_neo4j package)

**Usage:**

```bash
# Connect to KB and test all MaleCNS registrations
python kb_block_empty_images.py

# Save output to file
python kb_block_empty_images.py --save-cypher empty_blocks.cypher
```

## Workflow

### Step 1: Get Registrations from KB

Connect to VFB Knowledge Base and run this Cypher query:

```cypher
MATCH (n:Individual)-[r:in_register_with]->(tc:Template) 
WHERE n.label contains 'MaleCNS' 
RETURN DISTINCT 
    n.short_form as short_form,
    n.label as label,
    r.folder[0] as folder,
    tc.short_form as template_id
ORDER BY tc.short_form, r.folder[0]
```

Export results as TSV/CSV.

### Step 2: Test Folders for Empty Images

```bash
python batch_test_folders.py \
    --input-file kb_registrations.tsv \
    --output cypher_block_updates.cypher \
    --verbose
```

The script will:
1. Parse the KB registration file
2. Test each unique folder/template combination
3. Identify folders with `volume.wlz` size below threshold:
   - Brain (VFB_00101567): < 10 KB
   - VNC (VFB_00200000): < 4 KB
4. Generate CYPHER `SET` statements for empty folders

### Step 3: Review Generated CYPHER

```bash
cat cypher_block_updates.cypher
```

Expected format:

```cypher
// VFB KB Update: Block empty image folders
// Generated: 2026-03-03 18:28:06
// Total registrations to block: N

MATCH (n:Individual {short_form: 'VFB_00101234'})-[r:in_register_with]->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.folder[0] = '3ler'
SET r.block = ['No expression in region']
RETURN n.short_form as individual, r.folder[0] as folder, tc.short_form as template;
```

### Step 4: Apply Updates to KB

1. Connect to **writable KB instance** using Neo4j Browser or command-line client
2. Copy and paste the CYPHER statements
3. Execute each statement individually or wrap in a transaction:

```cypher
CALL apoc.periodic.iterate(
  "UNWIND $statements AS stmt RETURN stmt",
  "CALL apoc.cypher.run(stmt, {}) YIELD value RETURN value",
  {batchSize: 100, params: {statements: [statements...]}}
)
```

### Step 5: Verify Updates

Query the KB to confirm blocks were applied:

```cypher
MATCH (r:in_register_with)
WHERE r.block = ['No expression in region']
RETURN 
    COUNT(r) as blocked_count,
    COLLECT(DISTINCT r.folder[0]) as blocked_folders
```

## Empty Folder Thresholds

Determined through analysis of actual VFB image data:

### Brain (VFB_00101567)
- **Empty signature**: `volume.wlz` = 1,156 bytes
- **Threshold**: < 10 KB
- **Known empty**: 3ler
- **Reason**: Template-only, no expression data

### VNC (VFB_00200000)
- **Empty signature**: `volume.wlz` = 2,404 bytes
- **Threshold**: < 4 KB
- **Known empty**: 3ftr, 3ftt, 3ftv
- **Reason**: Template-only, no expression data

## Template ID Reference

**IMPORTANT:** Clarifying the distinction between Channel nodes and Template IDs in folder URLs.

### KB Structure
- Individuals are registered to **Channel nodes** (VFBc_00101567, VFBc_00200000)
- Channel nodes maintain **folder URLs** that reference the actual **Template IDs** (VFB_00101567, VFB_00200000)
- When checking folders via HTTP, the URLs ALWAYS use the actual Template IDs

### Folder URL Construction
The folder URLs stored in KB registrations already contain the correct full Template IDs:

```
Folder URL format (as stored in KB):
http://www.virtualflybrain.org/data/VFB/i/jrmc/{folder_code}/VFB_00101567/
                                                                 ↑
                                        Always the actual Template ID
```

**Example:**
- Correct:   `http://www.virtualflybrain.org/data/VFB/i/jrmc/0000/VFB_00101567/`
- Incorrect: `http://www.virtualflybrain.org/data/VFB/i/jrmc/0000/VFBc_00101567/`

The script uses the folder URLs directly from KB registrations—they already have the right Template IDs embedded.

### Cypher Query for Blocking
When generating Cypher to block empty folders, use the Template ID from the folder URL:

```cypher
MATCH (n:Individual)-[r:in_register_with]->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.folder[0] IN [...folder URLs...]
SET r.block = ['No expression in region']
```

The Template node matched must have the short_form that corresponds to the IDs in the folder URLs.

## Expected CYPHER Output

When folders are identified as empty, the scripts generate statements like:

```cypher
MATCH (n:Individual {short_form: 'VFB_0050XXXX'})-[r:in_register_with]->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.folder[0] = '3ler'
SET r.block = ['No expression in region']
RETURN n.short_form as individual, r.folder[0] as folder, tc.short_form as template;
```

This will:
1. Find the Individual node by its VFB ID
2. Match the `in_register_with` relationship to the Brain template
3. Filter for the specific empty folder
4. Set the block property on the relationship
5. Return confirmation of the update

## File Formats

### Input: KB Registration Export (TSV)

```
short_form          label              folder  template_id
VFB_00101234        Example Neuron     3ler    VFB_00101567
VFB_00101235        Another Neuron     3ler    VFB_00101567
VFB_00200001        VNC Neuron         3ftr    VFB_00200000
```

### Output: CYPHER Statements

Generated file with ready-to-execute CYPHER statements for KB updates.

## Troubleshooting

### Issue: "Could not fetch size for folder/template"

**Cause**: Network error or folder doesn't exist at that URL
**Solution**: Verify folder code and template ID are correct

### Issue: "Neo4j tools not available"

**Cause**: `uk.ac.ebi.vfb.neo4j.neo4j_tools` not installed
**Solution**: 
```bash
# Either provide KB query results manually (use --input-file)
# Or install VFB_neo4j package
pip install VFB_neo4j
```

### Issue: Script detects too many empty folders

**Cause**: Thresholds may need adjustment for new templates
**Solution**: Check EMPTY_THRESHOLDS dictionary and adjust based on actual folder analysis

## Project Structure

```
detectEmpty/
├── batch_test_folders.py          # Batch folder testing tool
├── kb_block_empty_images.py        # Direct KB connection tool
├── KB_INTEGRATION_GUIDE.md         # This file
├── find_empty_brain.py             # Original Brain folder analysis
├── find_empty_vnc.py               # Original VNC folder analysis
├── analyze_wlz.py                  # WLZ file analysis
└── README.md                       # Project overview
```

## References

- VFB Knowledge Base: https://kb.virtualflybrain.org
- VFB Data: http://www.virtualflybrain.org/data/
- VFB_reporting: https://github.com/VirtualFlyBrain/VFB_reporting
- Neo4j Cypher: https://neo4j.com/docs/cypher-manual/

## Examples

### Example 1: Test known empty folders only

```bash
source venv/bin/activate
python batch_test_folders.py --known-only --verbose
```

### Example 2: Test folders from KB export

```bash
# 1. Export from Neo4j Browser query and save as kb_export.tsv
# 2. Run batch test
python batch_test_folders.py \
    --input-file kb_export.tsv \
    --output brain_vnc_blocks.cypher \
    --verbose

# 3. Review generated file
cat brain_vnc_blocks.cypher
```

### Example 3: Using Direct KB Connection (if VFB_neo4j installed)

```bash
# Gets all MaleCNS registrations directly
python kb_block_empty_images.py

# Saves to file
python kb_block_empty_images.py --save-cypher male_cns_blocks.cypher
```

## Notes

- All CYPHER statements set `r.block = ['No expression in region']`
- This marks the relationship as blocked but does not delete data
- Changes can be reverted by removing the block property
- Verify with manual visual inspection of thumbnail images when possible
- Testing is non-invasive (read-only file size checks)

## Next Steps

1. Run folder tests: `python batch_test_folders.py --known-only`
2. Review generated CYPHER: `cat cypher_block_updates.cypher`
3. Connect to writable KB instance
4. Execute CYPHER statements
5. Verify updates complete successfully
