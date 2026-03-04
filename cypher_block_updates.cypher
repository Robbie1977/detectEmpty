// VFB KB Update: Block empty image folders
// Generated: 2026-03-03 18:54:26
//
// Consolidated statements grouped by template
// Uses VFBc_ (channel) nodes with r.folder[0] IN [list of URLs]
// Total empty folders to block: 4

// Block empty folders in Brain (VFB_00101567)
// Empty folders: 3ler
MATCH (c:Individual)-[r:in_register_with]->(tc:Template {short_form: 'VFB_00101567'})
WHERE r.folder[0] IN ["http://www.virtualflybrain.org/data/VFB/i/jrmc/3ler/VFB_00101567/"]
SET r.block = ['No expression in region']
RETURN c.short_form as channel, r.folder[0] as folder, tc.label as template, COUNT(r) as blocked_count

// Block empty folders in VNC (VFB_00200000)
// Empty folders: 3ftr, 3ftt, 3ftv
MATCH (c:Individual)-[r:in_register_with]->(tc:Template {short_form: 'VFB_00200000'})
WHERE r.folder[0] IN ["http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftr/VFB_00200000/", "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftt/VFB_00200000/", "http://www.virtualflybrain.org/data/VFB/i/jrmc/3ftv/VFB_00200000/"]
SET r.block = ['No expression in region']
RETURN c.short_form as channel, r.folder[0] as folder, tc.label as template, COUNT(r) as blocked_count
