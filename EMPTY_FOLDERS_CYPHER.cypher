// ============================================================================
// VFB KB Empty Image Folder Detection & Blocking Statements
// ============================================================================
// Generated: 2026-03-05
// Analysis: Detection of empty volume.wlz files in registered Male CNS folders
// Scope: 10,000 of 331,182 total Male CNS folders analyzed
// Results: 3,429 empty records found (3,376 unique folders)
//          648 Brain template (VFBc_00101567) empty
//          2,781 VNC template (VFBc_00200000) empty
// ============================================================================

// OPTION 1: Add marker label to empty individuals
UNWIND [
  "VFBc_jrmc0000", "VFBc_jrmc0001", "VFBc_jrmc0002", "VFBc_jrmc0003", 
  "VFBc_jrmc0004", "VFBc_jrmc0009", "VFBc_jrmc000a", "VFBc_jrmc000b",
  "VFBc_jrmc000d", "VFBc_jrmc000e", "VFBc_jrmc000g", "VFBc_jrmc000k",
  // ... (3,429 total VFB IDs from kb_analysis_results.json)
] AS folder_vfb_id
MATCH (i:Individual) WHERE i.vfb_id = folder_vfb_id
SET i:EmptyImages, i.empty_detection_date = "2026-03-05"
RETURN count(i) as marked;

// OPTION 2: Create tracking relationship to EmptyMarker
MATCH (i:Individual) WHERE i:EmptyImages
CREATE (marker:EmptyImageMarker {
  marked_individual_id: i.vfb_id,
  marked_date: "2026-03-05",
  detection_method: "HTTP_folder_volume_size_check",
  brain_template: "VFBc_00101567",
  vnc_template: "VFBc_00200000"
})
CREATE (i)-[:HAS_EMPTY_IMAGES]->(marker)
RETURN count(marker) as markers_created;

// OPTION 3: Exclude empty from queries (Brain template)
MATCH (i:Individual)-[:REGISTERED_IN]->(brain:Channel {vfb_id: "VFBc_00101567"})
WHERE NOT i:EmptyImages
RETURN i.vfb_id, i.label, brain.label;

// OPTION 4: Exclude empty from queries (VNC template)  
MATCH (i:Individual)-[:REGISTERED_IN]->(vnc:Channel {vfb_id: "VFBc_00200000"})
WHERE NOT i:EmptyImages
RETURN i.vfb_id, i.label, vnc.label;

// VALIDATION: Count marked empty
MATCH (i:EmptyImages) RETURN count(i) as total_empty_marked;

// VALIDATION: Show distribution
MATCH (i:EmptyImages)-[:HAS_EMPTY_IMAGES]->(m:EmptyImageMarker)
RETURN count(DISTINCT i) as unique_empty;
