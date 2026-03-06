#!/usr/bin/env python3
"""
Quick test of kb_block_empty_images with reduced folder limit
"""

import os
# Set limit to just 100 folders for quick test
os.environ['DETECTEMPTY_FULL_ANALYSIS'] = '0'

import sys
sys.path.insert(0, '/Users/rcourt/GIT/detectEmpty')

# Run the script
exec(open('/Users/rcourt/GIT/detectEmpty/kb_block_empty_images.py').read())
