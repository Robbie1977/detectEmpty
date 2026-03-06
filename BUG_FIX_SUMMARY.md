# Bug Fix: Empty Folder Detection Threshold Mismatch

## Issue Identified
User reported: **"Something is wrong as no image could have both regions empty"**

Analysis revealed that **53 folders were incorrectly marked as having both Brain AND VNC templates empty**, which is statistically unlikely and indicated a systematic error.

## Root Cause
The code was retrieving **Channel IDs (VFBc_)** from the KB query but the thresholds dictionary was defined with **Template IDs (VFB_)**:

```python
# BEFORE (Buggy)
EMPTY_SIGNATURES = {
    'VFB_00101567': 10000,  # Brain
    'VFB_00200000': 4000,   # VNC
}

# Query returns Channel IDs:
template_id = 'VFBc_00200000'  # VNC Channel ID

# Lookup fails, returns default:
threshold = EMPTY_SIGNATURES.get('VFBc_00200000', 10000)  # Returns 10000!
```

### Impact
- **VNC folders** were checked against Brain threshold (10000 bytes) instead of correct threshold (4000 bytes)
- **Result**: Many valid VNC folders (4000-10000 bytes) were incorrectly marked as **empty**
- **Consequence**: 53 folders were marked with BOTH templates empty when only one was actually empty

## Solution Implemented

### 1. Extract Template ID from Folder URL
The folder URL already contains the correct Template ID:
```
http://www.virtualflybrain.org/data/VFB/i/jrmc/015l/VFB_00200000/
                                                        ↓
                                            Actual Template ID
```

### 2. Updated Code
```python
# Extract actual template ID from folder URL (more reliable)
actual_template_id = None
if '/VFB_00101567/' in folder_url:
    actual_template_id = 'VFB_00101567'
elif '/VFB_00200000/' in folder_url:
    actual_template_id = 'VFB_00200000'

# Use correct threshold
threshold = EMPTY_SIGNATURES.get(actual_template_id, 10000)
```

### 3. Added Channel IDs for Backward Compatibility
```python
EMPTY_SIGNATURES = {
    # Template IDs (primary - from folder URLs)
    'VFB_00101567': 10000,  # Brain
    'VFB_00200000': 4000,   # VNC
    # Channel IDs (fallback - from KB queries)
    'VFBc_00101567': 10000,
    'VFBc_00200000': 4000,
}
```

## Data Quality Impact
**Previous Results (Incorrect)**
- Total Empty Records: 3,429
- Both templates empty: 53 ❌ (ERROR - should be 0-5 max)
- Brain only empty: 648
- VNC only empty: 2,781

**Next Run (After Fix)**
- Expected: False positives in VNC should decrease
- Folders with 4000-10000 byte VNC files should NO LONGER be marked empty
- "Both empty" count should drop significantly (likely to near zero)

## Testing the Fix
Run the analyzer again with the fixed code to regenerate results:
```bash
python kb_block_empty_images.py
```

Validation:
```bash
jq '.empty_records | group_by(.short_form) | map(select(length > 1)) | length' kb_analysis_results.json
```
Expected output: Should be 0 or < 5 (physically possible cases only)

## Files Modified
- `kb_block_empty_images.py`: Fixed threshold lookup logic and added Channel ID support
