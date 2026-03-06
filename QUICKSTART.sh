#!/bin/bash
# Quick Start Guide for VFB KB Empty Image Blocker

echo "========================================"
echo "VFB KB Empty Image Blocker - Quick Start"
echo "========================================"
echo ""

# Step 1: Check environment
echo "Step 1: Checking Python environment..."
if [ ! -d "venv" ]; then
    echo "  ✗ Virtual environment not found"
    echo "  Creating venv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install requests beautifulsoup4
else
    source venv/bin/activate
    echo "  ✓ Virtual environment ready"
fi

echo ""
echo "Step 2: Test KB connectivity..."
python3 diagnose_kb_connection.py 2>&1 | head -20

echo ""
echo "Step 3: Ready to run full analysis"
echo ""
echo "To start analysis of all 331,182 folders (takes 60-92 hours):"
echo ""
echo "  export DETECTEMPTY_FULL_ANALYSIS=1"
echo "  nohup python3 kb_block_empty_images.py > kb_full_analysis.log 2>&1 &"
echo ""
echo "To monitor progress:"
echo "  tail -f kb_full_analysis.log"
echo ""
echo "Results will be saved to:"
echo "  - kb_analysis_results.json (empty folder records)"
echo "  - kb_full_analysis.log (progress log)"
echo ""
echo "See README.md for complete documentation"
echo "========================================"
