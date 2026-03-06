# Repository Structure

```
detectEmpty/
├── README.md                          ← START HERE: Main user guide
├── QUICKSTART.sh                      ← Quick setup and verification
├── DEVELOPMENT.md                     ← Technical context for developers
├── DOCUMENTATION.md                   ← Which docs are current vs archived
│
├── kb_block_empty_images.py           ← MAIN SCRIPT: Analyzes KB folders
├── diagnose_kb_connection.py          ← Utility: Test KB connectivity
│
├── kb_full_analysis.log               ← Output: Progress log (generated)
├── kb_analysis_results.json           ← Output: Empty folder results (generated)
│
├── EXAMPLE_CYPHER_STATEMENTS.cypher   ← Reference: Example Cypher output
├── SAMPLE_GENERATED_CYPHER.cypher     ← Reference: Sample output
│
└── [ARCHIVED DOCS]                    ← Historical analysis docs
    ├── BUG_FIX_VALIDATION_REPORT.md
    ├── BUG_FIX_SUMMARY.md
    ├── FULL_ANALYSIS_EXECUTION_GUIDE.md
    ├── IMMEDIATE_ACTION_REQUIRED.md
    ├── PROJECT_STATUS_SUMMARY.md
    ├── QUICK_SUMMARY.md
    ├── THRESHOLD_REFINEMENT_CRITICAL_UPDATE.md
    └── (and others - see DOCUMENTATION.md)
```

## Key Files by Purpose

### 👤 For Users

| File | Purpose |
|------|---------|
| README.md | **Start here** - Complete guide to run analysis |
| QUICKSTART.sh | One-command setup verification |
| DOCUMENTATION.md | Which docs to use |

### 🔧 For Running Analysis

| File | Purpose |
|------|---------|
| kb_block_empty_images.py | Main analysis script - queries KB, checks folders, generates Cypher |
| diagnose_kb_connection.py | Test KB connectivity before running full analysis |

### 📊 For Results

| File | Purpose |
|------|---------|
| kb_analysis_results.json | All 331,182 folder analysis results (generated) |
| kb_full_analysis.log | Detailed progress log (generated) |
| EXAMPLE_CYPHER_STATEMENTS.cypher | Reference examples for blocking syntax |

### 💻 For Developers

| File | Purpose |
|------|---------|
| DEVELOPMENT.md | Code structure, bug history, technical decisions |
| kb_block_empty_images.py | Well-commented source with thresholds and logic |

---

## Workflow

1. **Read:** README.md (understand project)
2. **Test:** Run QUICKSTART.sh (verify KB connectivity)  
3. **Run:** `python3 kb_block_empty_images.py` with `DETECTEMPTY_FULL_ANALYSIS=1`
4. **Check:** kb_analysis_results.json (review empty folders)
5. **Apply:** Use Cypher statements to update KB

---

## Project Summary

**Purpose:** Detect and block empty expression folders in VFB Knowledge Base  
**Scope:** All 331,182 Male CNS registrations  
**Detection:** File size analysis (1156 bytes = Brain empty, 2404 = VNC empty)  
**Output:** Cypher statements for Neo4j KB blocking  
**Runtime:** 60-92 hours for full analysis

---

**Status:** Production Ready  
**Last Updated:** March 6, 2026
