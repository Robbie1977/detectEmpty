#!/bin/bash

# Full KB Analysis with Monitoring
# Runs the complete empty folder detection for all 331,182 folders

cd /Users/rcourt/GIT/detectEmpty

echo "========================================================================"
echo "Starting Full VFB KB Empty Folder Analysis"
echo "========================================================================"
echo ""
echo "Time: $(date)"
echo "Folders to analyze: 331,182"
echo ""

# Make sure environment is set
export DETECTEMPTY_FULL_ANALYSIS=1

# Run the analysis and capture output
/Users/rcourt/GIT/detectEmpty/venv/bin/python3 kb_block_empty_images.py | tee kb_full_analysis.log

ANALYSIS_PID=$!

echo ""
echo "========================================================================"
echo "Analysis process started with PID: $ANALYSIS_PID"
echo "Log file: $(pwd)/kb_full_analysis.log"
echo "========================================================================"
echo ""
echo "To monitor progress:"
echo "  tail -f kb_full_analysis.log"
echo ""
echo "To wait for completion:"
echo "  wait $ANALYSIS_PID"
echo ""
