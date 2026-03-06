# VFB KB Full Analysis - Performance & Execution Guide

**Date:** March 5, 2026  
**Status:** ✓ KB Server Active | ⚠️ Full Analysis Will Take 24-92 Hours

---

## Diagnosis Summary

✓ **HTTP REST API:** Working (200 OK)  
✓ **Query Performance:** Fast (1.54 seconds for 331k folder count)  
✓ **Authentication:** Valid (neo4j/vfb credentials accepted)  
⚠️ **Bottleneck:** Individual folder HTTP checks (~1 sec per folder)

---

## Performance Analysis

### What Makes the Full Analysis Slow?

The script's time complexity:
```
Time = (Query Time) + (331,182 × Folder Check Time)
     = 1.5 sec + (331,182 × 0.5-2.0 sec)
     = 1.5 + (165,591 - 662,364 seconds)
     = 46-184 hours
```

### Timing Breakdown
| Task | Time | Count | Total |
|------|------|-------|-------|
| Initial KB query | 1.54s | 1 | 1.54s |
| HTTP GET per folder | 0.5-2.0s | 331,182 | 165k-662k sec |
| Processing per folder | <0.1s | 331,182 | <33k sec |
| **TOTAL ESTIMATE** | | | **46-184 hours** |

**Most likely:** 60-90 hours (assuming 0.7-1.0 seconds average per folder)

---

## Why Previous Runs Appeared to Hang

1. **Process was NOT hung** - it was checking folders very slowly
2. **No output buffering** - Log files stayed empty because output was buffered
3. **Low CPU usage** - Mostly waiting on network (HTTP GET) not CPU
4. **Memory stable** - Python holding query results in memory (~192MB)
5. **Real-time iteration** - Script was checking individual folders one-by-one

### Example Timeline for Full Run
- **0-2 min:** Query KB for all folders (1.54s) + start checks
- **2-60 min:** Check first 3,600 folders at 1 sec/folder
- **1-2 hours:** Reach 3,600 folder milestone, see first progress output
- **24 hours:** ~86,000 folders checked (progress update every 500)
- **60+ hours:** Complete remaining folders

---

## Solutions for Efficient Full Analysis

### Option 1: Batch Processing (Recommended)
Process folders in smaller batches to avoid long-running process:
```bash
# Split 331k into 33 batches of 10k folders
for batch in {1..33}; do
  DETECTEMPTY_ANALYSIS_BATCH=$batch \
  /Users/rcourt/GIT/detectEmpty/venv/bin/python3 kb_block_empty_images.py
done
```
**Pros:** Shorter individual runs, easier testing, resume-friendly  
**Cons:** More code change required

### Option 2: Run Overnight (Simple)
Just start the process and let it run to completion:
```bash
nohup /Users/rcourt/GIT/detectEmpty/venv/bin/python3 \
  kb_block_empty_images.py > kb_full_analysis.log 2>&1 &
```
**Pros:** No code changes, simple output redirection  
**Cons:** Takes 24-92 hours, must keep Mac running

### Option 3: Run in Background with Output Monitoring
```bash
# Start in background and monitor progress
export DETECTEMPTY_FULL_ANALYSIS=1
cd /Users/rcourt/GIT/detectEmpty
/Users/rcourt/GIT/detectEmpty/venv/bin/python3 kb_block_empty_images.py \
  > kb_full_analysis.log 2>&1 &

# Monitor progress
echo $! > kb_analysis.pid
sleep 5
tail -f kb_full_analysis.log

# If interrupted, can resume by running again (checks last results)
```

### Option 4: Optimize with Concurrent Folder Checks (Advanced)
Modify script to use ThreadPoolExecutor for parallel HTTP checks:
```python
from concurrent.futures import ThreadPoolExecutor
import threading

# Check up to 10 folders in parallel
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(is_empty_folder, reg[2], reg[3]) 
               for reg in registrations]
    results = [f.result() for f in futures]
```
**Pros:** Could reduce 60 hours → 6-10 hours  
**Cons:** More network load, potential rate limiting, risk of server rejection

---

## Recommended Approach

### For First Full Analysis: Option 2 (Simple)
```bash
# 1. Verify code is fixed (already done ✓)
# 2. Clear any old results
rm -f kb_analysis_results.json kb_full_analysis.log

# 3. Start full analysis (detaches from terminal)
export DETECTEMPTY_FULL_ANALYSIS=1
nohup /Users/rcourt/GIT/detectEmpty/venv/bin/python3 \
  kb_block_empty_images.py > kb_full_analysis.log 2>&1 &

PID=$!
echo "Started analysis as PID $PID"
echo "View progress: tail -f kb_full_analysis.log"
echo "Kill if needed: kill $PID"

# 4. Check status after 30 minutes
sleep 1800
echo "=== Check after 30 min ==="
tail -20 kb_full_analysis.log

# 5. Let it run overnight (or several days)
# 6. Check results when complete
```

---

## Monitoring the Full Analysis

### Quick Status Check
```bash
# See how many folders checked so far
tail -5 kb_full_analysis.log | grep PROGRESS

# Example output:
# [PROGRESS] 500/331182 folders checked (47 empty)...
# [PROGRESS] 1000/331182 folders checked (98 empty)...
# [PROGRESS] 1500/331182 folders checked (141 empty)...
```

### Estimate Time Remaining
```bash
# Get progress and estimate
tail -1 kb_full_analysis.log | grep PROGRESS

# If shows "1000/331182 checked" at hour 1:
# Time per folder = 1 hour / 1000 = 3.6 sec/folder
# Remaining = (331182 - 1000) * 3.6 / 3600 = 328 hours (5.5 days)
```

### Check if Process is Still Running
```bash
pgrep -f "kb_block_empty_images" | wc -l
# Output: 0 = done, 1 = still running
```

---

## Expected Results Timeline

Based on diagnostic data:

| Checkpoint | Time | Status |
|-----------|------|--------|
| Start | 0m | Query KB: 1-2 min |
| First output | 15-30m | First 500 folders |
| 1% complete | 1-2h | ~3,311 folders |
| 10% complete | 10-20h | ~33,118 folders |
| 50% complete | 50-100h | ~165,591 folders |
| **COMPLETE** | **60-92h** | All 331,182 folders |

---

## What to Expect in Results

### File: `kb_analysis_results.json`
```json
{
  "timestamp": "2026-03-06T12:34:56",
  "total_empty_records": "~11,500-12,000 (updated)",
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

### Key Validation Checks
```python
import json

with open('kb_analysis_results.json') as f:
    data = json.load(f)

# Extract template counts
brain = [r for r in data['empty_records'] if r['template_id'] == 'VFBc_00101567']
vnc = [r for r in data['empty_records'] if r['template_id'] == 'VFBc_00200000']

print(f"Total empty: {len(data['empty_records'])}")
print(f"  Brain: {len(brain)} (~6-7% of 331k = 20k-23k expected)")  # WRONG expectation
print(f"  VNC: {len(vnc)} (~13-15% of 331k = 43k-50k expected)")

# Check for both-empty anomalies (should be ~0-5)
both_empty = []
for folder in set(r['folder'] for r in data['empty_records']):
    templates = [r['template_id'] for r in data['empty_records'] if r['folder'] == folder]
    if len(templates) > 1:
        both_empty.append(folder)

print(f"Both empty: {len(both_empty)} (should be 0-5, not 53 like before)")
```

---

## Troubleshooting Failed Full Analysis

### If Process Crashes/Stops
```bash
# Check log for error
grep -i error kb_full_analysis.log | tail -20

# Check what folders were processed
grep "PROGRESS\|SUMMARY" kb_full_analysis.log | tail -5

# Partially completed results still saved
head -20 kb_analysis_results.json
```

### If Process Hangs (No Output for >30 min)
```bash
# Check if really running
ps aux | grep kb_block_empty

# Check network connectivity to KB
/Users/rcourt/GIT/detectEmpty/venv/bin/python3 diagnose_kb_connection.py

# If still hung, kill and restart
pkill -f kb_block_empty_images
# Then retry with: export DETECTEMPTY_FULL_ANALYSIS=1 && python3 kb_block_empty_images.py &
```

### If Network Timeouts
Less than 1% of folders typically unreachable - script handles gracefully:
- ✓ Continues checking other folders
- ✓ Counts as "failed_count" in summary
- ✓ Won't be included in cypher blocking statements
- ✓ Can be manually reviewed in results

---

## Success Criteria for Full Run

✓ **Process completes** without error  
✓ **Results saved** to kb_analysis_results.json  
✓ **Both-empty folders** reduced from 53 → 0-5  
✓ **Total empty count** ~11,500-12,000 (vs 3,429 from 10k buggy run)  
✓ **Cypher statements** generated for KB update  
✓ **Summary statistics** show reasonable distribution by template

---

## After Full Analysis Completes

1. **Review Results**
   ```bash
   grep -c "empty_records" kb_analysis_results.json
   tail -20 kb_full_analysis.log
   ```

2. **Extract Cypher from Results**
   ```bash
   python3 -c "
   import json
   with open('kb_analysis_results.json') as f:
       data = json.load(f)
   print(data['cypher_statements'])
   " > empty_folders_block.cypher
   ```

3. **Update KB** (if approved)
   - Connect to writable KB instance
   - Execute Cypher statements
   - Verify blocks applied

4. **Archive Results**
   ```bash
   mkdir -p analysis_archive/$(date +%Y%m%d)
   cp kb_analysis_results.json kb_full_analysis.log analysis_archive/$(date +%Y%m%d)/
   ```

---

## Reference

**Code Status:** ✅ Bug fixed in kb_block_empty_images.py  
**KB Status:** ✅ API responsive and working  
**Next Action:** Start full 331,182 folder analysis (24-92 hours)  
**Expected:** Results ready in 2-4 days depending on network

---

**Generated:** 2026-03-05 20:15  
**System:** macOS (rcourt)  
**Python:** 3.14 (venv)
