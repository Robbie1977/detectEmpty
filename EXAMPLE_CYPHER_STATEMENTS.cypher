// VFB Knowledge Base - Empty Image Folder Block Statements
// 
// This file contains CYPHER UPDATE statements that add block=['No expression in region']
// to in_register_with relationships for folders detected as empty (no expression data).
//
// IMPORTANT: These are example statements based on analysis of known empty folders.
//            You MUST query your KB instance and generate real statements using:
//            python batch_test_folders.py --input-file your_kb_registrations.tsv
//
// Empty Folders Detected:
//   - Brain (VFB_00101567): 3ler (1,156 bytes volume.wlz)
//   - VNC (VFB_00200000): 3ftr, 3ftt, 3ftv (2,404 bytes volume.wlz each)
//
// To apply these updates:
// 1. Connect to writable KB instance
// 2. Copy each statement below
// 3. Execute in Neo4j Browser or terminal client
// 4. Verify with: MATCH (r:in_register_with) WHERE r.block=['No expression in region'] RETURN count(r)
//
// ============================================================================

// EXAMPLE: Consolidated Brain empty folder block
// Single statement targets all empty folders in Brain template
// Uses VFBc_ (channel) nodes for efficiency
//
MATCH (c:Individual)-[r:in_register_with]->(tc:Template)
WHERE tc.short_form = 'VFB_00101567'
  AND r.folder[0] IN [
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ler/VFB_00101567/"
  ]
SET r.block = ['No expression in region']
RETURN 
    c.short_form as channel,
    r.folder[0] as folder,
    tc.label as template,
    r.block as block_reason;

// EXAMPLE: Consolidated VNC empty folders block
// Single statement targets all empty folders in VNC template
// Much more efficient than individual statements per folder
//
MATCH (c:Individual)-[r:in_register_with]->(tc:Template)
WHERE tc.short_form = 'VFB_00200000'
  AND r.folder[0] IN [
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftr/VFB_00200000/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftt/VFB_00200000/",
    "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftv/VFB_00200000/"
  ]
SET r.block = ['No expression in region']
RETURN 
    c.short_form as channel,
    r.folder[0] as folder,
    tc.label as template,
    r.block as block_reason;

// ============================================================================
// VERIFICATION QUERIES - Run these to confirm blocks were applied
// ============================================================================

// Count blocks applied
MATCH (r:in_register_with)
WHERE r.block = ['No expression in region']
RETURN 
    COUNT(r) as total_blocked_edges,
    COLLECT(DISTINCT 
        CASE 
            WHEN r.folder[0] CONTAINS '/3ler/' THEN '3ler'
            WHEN r.folder[0] CONTAINS '/3ftr/' THEN '3ftr'
            WHEN r.folder[0] CONTAINS '/3ftt/' THEN '3ftt'
            WHEN r.folder[0] CONTAINS '/3ftv/' THEN '3ftv'
            ELSE 'other'
        END
    ) as blocked_folders;

// Show all blocked registrations
MATCH (n:Individual)-[r:in_register_with]->(tc:Template)
WHERE r.block = ['No expression in region']
RETURN 
    n.short_form,
    n.label,
    r.folder[0] as folder,
    tc.label as template,
    r.block as block_reason
ORDER BY tc.label, r.folder[0];

// Check specific template
MATCH (r:in_register_with)->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.block = ['No expression in region']
RETURN COUNT(r) as brain_blocked_count;

// Check specific folder - Brain
MATCH (r:in_register_with)
WHERE r.folder[0] CONTAINS '/3ler/'
  AND r.block = ['No expression in region']
RETURN COUNT(r) as folder_3ler_blocked;

// Check specific folder - VNC
MATCH (r:in_register_with)
WHERE r.folder[0] CONTAINS '/3ftr/' OR r.folder[0] CONTAINS '/3ftt/' OR r.folder[0] CONTAINS '/3ftv/'
  AND r.block = ['No expression in region']
RETURN COUNT(r) as vnc_blocked_count;

// ============================================================================
// REVERTING CHANGES (if needed)
// ============================================================================

// Remove block from specific folder
MATCH (r:in_register_with)
WHERE r.folder[0] = '3ler'
  AND r.block = ['No expression in region']
REMOVE r.block
RETURN COUNT(r) as unblocked_count;

// Remove all expression blocks
MATCH (r:in_register_with)
WHERE r.block = ['No expression in region']
REMOVE r.block
RETURN COUNT(r) as total_unblocked;

// ============================================================================
// NOTES
// ============================================================================

// The block property is added as a list: ['No expression in region']
// This follows VFB KB conventions for blocking reasons
// 
// Alternatives (for reference):
//   - 'No segmentation available'
//   - 'Deprecated'
//   - 'Data removed'
//   - 'Template mismatch'
//
// All changes are reversible by REMOVE r.block
//
// For more information, see VFB_reporting GitHub:
// https://github.com/VirtualFlyBrain/VFB_reporting/blob/main/src/get_catmaid_papers.py#L537
