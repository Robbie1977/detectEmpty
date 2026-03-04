#!/usr/bin/env python3
"""
Complete VFB KB empty folder blocker - End-to-end workflow orchestrator.

This script serves as a master tool to:
1. Query the KB for MaleCNS registrations (if connection available)
2. Test all folders for empty images
3. Generate CYPHER update statements
4. Save output file

Usage:
    python kb_workflow.py [--output-cypher file.cypher] [--output-report file.txt]
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

def print_banner(text: str):
    """Print formatted banner."""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")

def print_step(number: int, text: str):
    """Print step indicator."""
    print(f"\n[STEP {number}] {text}")
    print("-" * 70)

def get_kb_credentials() -> Tuple[str, str, str]:
    """Get KB connection details - using defaults automatically."""
    kb_url = "http://kb.virtualflybrain.org"
    kb_user = "neo4j"
    kb_pwd = "vfb"
    
    print("\nVFB Knowledge Base Connection Details:")
    print(f"Using defaults: {kb_url} / {kb_user}")
    
    return kb_url, kb_user, kb_pwd

def generate_workflow_report(
    tested_folders: Dict,
    empty_folders: List[str],
    output_file: Path = None
) -> str:
    """Generate a summary report of the workflow."""
    
    report = f"""
VFB Knowledge Base Empty Folder Detector - Workflow Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
=======

Total folders tested: {len(tested_folders)}
Empty folders found: {len(empty_folders)}

EMPTY FOLDERS DETECTED
======================

Brain (VFB_00101567):
"""
    
    brain_empty = [f for f in empty_folders if 'VFB_00101567' in tested_folders.get(f, {}).get('template', '')]
    if brain_empty:
        for folder in brain_empty:
            report += f"  - {folder}\n"
    else:
        report += "  (none)\n"
    
    report += f"""

VNC (VFB_00200000):
"""
    
    vnc_empty = [f for f in empty_folders if 'VFB_00200000' in tested_folders.get(f, {}).get('template', '')]
    if vnc_empty:
        for folder in vnc_empty:
            report += f"  - {folder}\n"
    else:
        report += "  (none)\n"
    
    report += f"""

NEXT STEPS
==========

1. Review the generated CYPHER statements:
   cat cypher_block_updates.cypher

2. Connect to writable KB instance:
   - Access Neo4j Browser
   - Provide credentials to write KB admin

3. Execute CYPHER statements:
   - Copy each statement from the file
   - Paste into Neo4j Browser
   - Execute in a transaction

4. Verify updates:
   MATCH (r:in_register_with)
   WHERE r.block = ['No expression in region']
   RETURN COUNT(r) as blocked_count

DETECTION CRITERIA
==================

Empty folder determination based on volume.wlz file size:
  - Brain (VFB_00101567): < 10 KB threshold
  - VNC (VFB_00200000): < 4 KB threshold

Files marked as empty indicate template-only registrations
with no actual expression data.

OUTPUT FILES
============

cypher_block_updates.cypher - Ready-to-execute CYPHER statements
kb_workflow_report.txt      - This report

For more details, see:
  - KB_INTEGRATION_README.md
  - KB_INTEGRATION_GUIDE.md
  - batch_test_folders.py --help
"""
    
    if output_file:
        try:
            Path(output_file).write_text(report)
            print(f"\n[OK] Report saved to {output_file}")
        except Exception as e:
            print(f"\n[WARN] Could not save report: {e}")
    
    return report

def main():
    """Main workflow."""
    
    print_banner("VFB KB Empty Folder Blocker - Workflow")
    
    print("""
This tool helps you:
1. Identify empty image folders in VFB
2. Generate CYPHER statements to block them
3. Apply updates to the Knowledge Base

Options:
  --help              Show this help
  --direct-kb         Use direct KB connection (if VFB_neo4j available)
  --from-file FILE    Use pre-exported KB registrations
  --known-only        Test known empty folders only (no KB needed)
""")
    
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='store_true')
    parser.add_argument('--direct-kb', action='store_true')
    parser.add_argument('--from-file')
    parser.add_argument('--known-only', action='store_true')
    parser.add_argument('--output-cypher', default='cypher_block_updates.cypher')
    parser.add_argument('--output-report', default='kb_workflow_report.txt')
    
    args = parser.parse_args()
    
    if args.help:
        print(__doc__)
        sys.exit(0)
    
    # Determine workflow path
    if args.known_only:
        print("\n[MODE] Testing known empty folders (local only)")
        mode = "known"
    elif args.from_file:
        print(f"\n[MODE] Testing from KB export file: {args.from_file}")
        mode = "file"
    elif args.direct_kb:
        print("\n[MODE] Direct KB connection")
        mode = "kb"
    else:
        print("\nChoose workflow:")
        print("1. Direct KB connection (requires credentials)")
        print("2. From exported KB registrations file")
        print("3. Test known empty folders only (no KB needed)")
        
        choice = input("\nEnter choice (1-3, default: 3): ").strip() or "3"
        
        if choice == "1":
            mode = "kb"
        elif choice == "2":
            mode = "file"
            args.from_file = input("Enter path to registrations file: ").strip()
        else:
            mode = "known"
    
    # Execute appropriate workflow
    if mode == "kb":
        print_step(1, "Connect to VFB Knowledge Base")
        kb_url, kb_user, kb_pwd = get_kb_credentials()
        
        # Run KB blocker and capture output to file
        print(f"\nRunning: {sys.executable} kb_block_empty_images.py")
        print(f"  Host: {kb_url}")
        print(f"  User: {kb_user}")
        import subprocess
        
        # Capture output to a temp file
        temp_output = "kb_checking_output.txt"
        with open(temp_output, 'w') as f:
            result = subprocess.run(
                [sys.executable, "kb_block_empty_images.py"],
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True
            )
        
        # Display output
        with open(temp_output, 'r') as f:
            output = f.read()
            print(output)
        
        if result.returncode != 0:
            print("\n[ERROR] KB script failed")
            sys.exit(1)
    
    elif mode == "file":
        if not Path(args.from_file).exists():
            print(f"\n[ERROR] File not found: {args.from_file}")
            sys.exit(1)
        
        print_step(1, "Format KB registrations")
        print(f"Converting {args.from_file}...")
        
        formatted_file = "kb_registrations_formatted.tsv"
        import subprocess
        result = subprocess.run(
            [sys.executable, "format_kb_results.py",
             "--input-file", args.from_file,
             "--output", formatted_file],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"[ERROR] {result.stderr}")
            sys.exit(1)
        
        print_step(2, "Test all folders")
        print(f"Testing folders from {formatted_file}...")
        
        result = subprocess.run(
            [sys.executable, "batch_test_folders.py",
             "--input-file", formatted_file,
             "--output", args.output_cypher,
             "--verbose"],
            capture_output=False
        )
        if result.returncode != 0:
            print("\n[ERROR] Batch test failed")
            sys.exit(1)
    
    else:  # mode == "known"
        print_step(1, "Test known empty folders")
        
        import subprocess
        result = subprocess.run(
            [sys.executable, "batch_test_folders.py",
             "--known-only",
             "--output", args.output_cypher,
             "--verbose"],
            capture_output=False
        )
        if result.returncode != 0:
            print("\n[ERROR] Batch test failed")
            sys.exit(1)
    
    # Final steps
    print_step(2 if mode != "kb" else 3, "Review generated CYPHER")
    
    cypher_file = Path(args.output_cypher)
    if cypher_file.exists():
        print(f"\n✓ Generated: {cypher_file.absolute()}")
        
        with open(cypher_file) as f:
            content = f.read()
            lines = content.split('\n')
            print(f"  Lines: {len(lines)}")
            print(f"  Size: {len(content)} bytes")
            
            # Count MATCH statements
            match_count = content.count('MATCH')
            print(f"  Statements: {match_count}")
    else:
        print("[WARN] CYPHER file not generated")
    
    # Generate report
    print_step(3 if mode != "kb" else 4, "Generate workflow report")
    
    # Try to read actual results from kb_analysis_results.json
    tested_folders = {}
    empty_folders = []
    
    results_file = Path("kb_analysis_results.json")
    if results_file.exists():
        try:
            import json
            with open(results_file) as f:
                results = json.load(f)
                empty_folders = [f"{rec['folder']} ({rec['template_id']})" for rec in results.get('empty_records', [])]
                print(f"[OK] Loaded {len(empty_folders)} empty folders from results file")
        except Exception as e:
            print(f"[WARN] Could not read results file: {e}")
    
    generate_workflow_report(tested_folders, empty_folders, Path(args.output_report))
    
    # Summary
    print_banner("Workflow Complete")
    
    print(f"""
✓ Output files:
  - {args.output_cypher}       (CYPHER statements for KB update)
  - {args.output_report}        (This workflow report)

📋 Next Steps:

1. Review CYPHER statements:
   cat {args.output_cypher}

2. Connect to writable KB instance:
   https://kb.virtualflybrain.org
   (Request write access from VFB team)

3. Execute CYPHER statements in Neo4j Browser:
   - Copy content from {args.output_cypher}
   - Paste into Browser console
   - Execute with :play cypher

4. Verify updates:
   MATCH (r:in_register_with) WHERE r.block=['No expression in region']
   RETURN COUNT(r)

📚 Documentation:
   - KB_INTEGRATION_README.md (complete guide)
   - KB_INTEGRATION_GUIDE.md (detailed workflow)
   - EXAMPLE_CYPHER_STATEMENTS.cypher (working examples)

For questions or issues, see the troubleshooting section in
KB_INTEGRATION_README.md
""")

if __name__ == '__main__':
    main()
