#!/usr/bin/env python3
"""
Convert Neo4j Browser query results to TSV format for batch_test_folders.py

This helper script takes raw output from Neo4j Browser and converts it to
a clean TSV file that can be used as input to batch_test_folders.py

Usage:
    1. In Neo4j Browser, run this query:
    
       MATCH (n:Individual)-[r:in_register_with]->(tc:Template) 
       WHERE n.label contains 'MaleCNS' 
       RETURN DISTINCT 
           n.short_form,
           n.label,
           r.folder[0],
           tc.short_form
       ORDER BY tc.short_form, r.folder[0]
    
    2. Export results as CSV/JSON from the Browser
    
    3. Convert and format:
       python format_kb_results.py --input-file exported.csv --output kb_registrations.tsv
    
    4. Test folders:
       python batch_test_folders.py --input-file kb_registrations.tsv
"""

import sys
import csv
import json
from pathlib import Path
from typing import List, Dict
import argparse

def parse_csv_export(filepath: Path) -> List[Dict]:
    """Parse CSV exported from Neo4j Browser."""
    records = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle various column name variations
                record = {
                    'short_form': row.get('n.short_form', row.get('short_form', '')).split('/')[-1],
                    'label': row.get('n.label', row.get('label', '')),
                    'folder': row.get('r.folder[0]', row.get('folder', '')),
                    'template_id': row.get('tc.short_form', row.get('template_id', '')).split('/')[-1],
                }
                
                if all([record['short_form'], record['folder'], record['template_id']]):
                    records.append(record)
    
    except Exception as e:
        print(f"[ERROR] Failed to parse CSV: {e}")
        return []
    
    return records

def parse_json_export(filepath: Path) -> List[Dict]:
    """Parse JSON exported from Neo4j Browser."""
    records = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Handle different JSON structures
            results = data
            if isinstance(data, dict):
                if 'results' in data:
                    results = data['results']
                elif 'data' in data:
                    results = data['data']
            
            if isinstance(results, list):
                for item in results:
                    # Extract fields from various possible locations
                    if isinstance(item, dict):
                        record = {
                            'short_form': item.get('short_form', item.get('n.short_form', '')).split('/')[-1],
                            'label': item.get('label', item.get('n.label', '')),
                            'folder': item.get('folder', item.get('r.folder[0]', '')),
                            'template_id': item.get('template_id', item.get('tc.short_form', '')).split('/')[-1],
                        }
                        if all([record['short_form'], record['folder'], record['template_id']]):
                            records.append(record)
    
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON: {e}")
        return []
    
    return records

def save_as_tsv(records: List[Dict], filepath: Path) -> bool:
    """Save records as TSV file."""
    try:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['short_form', 'label', 'folder', 'template_id'],
                delimiter='\t'
            )
            writer.writeheader()
            writer.writerows(records)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save TSV: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Convert Neo4j Browser query results to TSV format'
    )
    parser.add_argument('--input-file', required=True,
                       help='Input file (CSV or JSON from Neo4j Browser)')
    parser.add_argument('--output', default='kb_registrations.tsv',
                       help='Output TSV file')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {args.input_file}")
        sys.exit(1)
    
    print(f"[INFO] Reading {input_path}...")
    
    # Try JSON first, then CSV
    records = []
    if input_path.suffix.lower() == '.json':
        records = parse_json_export(input_path)
    else:
        records = parse_csv_export(input_path)
    
    if not records:
        print("[ERROR] Could not parse any records from input file")
        sys.exit(1)
    
    print(f"[OK] Parsed {len(records)} records")
    
    # Save as TSV
    if save_as_tsv(records, output_path):
        print(f"[OK] Saved to {output_path.absolute()}")
        
        # Show sample
        print("\n[SAMPLE] First 3 records:")
        print("-" * 80)
        for i, rec in enumerate(records[:3]):
            print(f"{i+1}. {rec['short_form']:15} {rec['folder']:8} {rec['template_id']:20} {rec['label']}")
        
        print(f"\n[READY] Use with:"  )
        print(f"  python batch_test_folders.py --input-file {output_path}")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
