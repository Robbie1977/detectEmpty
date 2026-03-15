#!/usr/bin/env python3
"""Generate Cypher updates to copy class symbols from pdb into the KB.

Some FlyWire Individuals in the KB do not have their `symbol` property set.
This script:
  1) Queries the KB for FlyWire Individuals and their class IDs (via INSTANCEOF)
  2) Queries the pdb Neo4j instance for those classes to get a canonical symbol
  3) Prints compact Cypher statements that update the KB Individuals' `symbol`

The output is intended to be sent through `cypher-shell` or saved to a file.

Example:
    python dump_vfb_symbol_updates.py | tee updates.cypher
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

from kbw_config import get_kb_http_endpoint, get_kb_auth, get_pdb_http_endpoint


def _run_cypher_query(
    endpoint: str,
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    auth: Optional[Tuple[str, str]] = None,
    timeout: int = 30,
) -> List[List[Any]]:
    """Run a Cypher query via the Neo4j HTTP REST transaction endpoint."""

    payload = {
        "statements": [
            {
                "statement": query,
                "parameters": parameters or {},
                "resultDataContents": ["row"],
            }
        ]
    }

    resp = requests.post(endpoint, json=payload, auth=auth, timeout=timeout)
    resp.raise_for_status()

    data = resp.json()
    statements = data.get("results", [])
    if not statements:
        return []

    return [row_obj.get("row", []) for row_obj in statements[0].get("data", [])]


def _chunked(iterable: Iterable[Any], size: int) -> List[List[Any]]:
    """Split an iterable into chunks of roughly `size` items."""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def _fetch_flywire_individual_class_pairs(
    kb_endpoint: str, auth: Tuple[str, str], only_missing_symbol: bool
) -> List[Tuple[str, str]]:
    """Return list of (individual_short_form, class_short_form) pairs."""

    query = """
MATCH (i:Individual)
WHERE i.label CONTAINS 'FlyWire'
  AND i.short_form STARTS WITH 'VFB'
"""
    if only_missing_symbol:
        query += "\n  AND (NOT exists(i.symbol) OR size(i.symbol)=0)\n"

    query += """
MATCH (i)-[:INSTANCEOF]->(c:Class)
RETURN i.short_form AS individual, c.short_form AS class_id
"""

    rows = _run_cypher_query(kb_endpoint, query, auth=auth)
    return [(ind, cls) for ind, cls in rows if ind and cls]


def _fetch_symbols_for_classes(
    pdb_endpoint: str,
    auth: Optional[Tuple[str, str]],
    class_ids: List[str],
    batch_size: int = 250,
) -> Dict[str, str]:
    """Fetch a symbol for each class short_form from pdb."""

    class_to_symbol: Dict[str, str] = {}

    for batch in _chunked(class_ids, batch_size):
        query = """
MATCH (c:Class)
WHERE c.short_form IN $class_ids
RETURN c.short_form AS class_id,
       c.symbol AS symbol,
       c.sl AS sl,
       c.label AS label
"""
        rows = _run_cypher_query(
            pdb_endpoint, query, parameters={"class_ids": batch}, auth=auth
        )

        for class_id, symbol, sl, label in rows:
            # Only use the symbol property when it exists.
            # If symbol is missing, we do not assign one.
            if symbol and isinstance(symbol, list) and symbol:
                best = symbol[0]
            elif symbol and isinstance(symbol, str):
                best = symbol
            else:
                # No symbol present for this class: leave it unset.
                continue

            class_to_symbol[class_id] = best

    return class_to_symbol


def generate_cypher_statements(
    individual_to_symbol: Dict[str, str], batch_size: int = 250
) -> List[str]:
    """Generate grouped Cypher update statements by symbol value."""

    # Group individuals by symbol so we can update many nodes in one statement.
    by_symbol: Dict[str, List[str]] = defaultdict(list)
    for individual, symbol in individual_to_symbol.items():
        by_symbol[symbol].append(individual)

    statements: List[str] = []
    for symbol, individuals in sorted(by_symbol.items()):
        symbol_literal = json.dumps([symbol])
        for chunk in _chunked(individuals, batch_size):
            individuals_literal = json.dumps(chunk)
            stmt = (
                "MATCH (i:Individual)\n"
                f"WHERE i.short_form IN {individuals_literal}\n"
                f"SET i.symbol = {symbol_literal}"
            )
            statements.append(stmt)

    return statements


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dump Cypher updates to set symbol on FlyWire Individuals."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=250,
        help="Maximum number of individuals per Cypher statement.",
    )
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Only update Individuals that are missing a symbol property.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the generated Cypher updates directly to the KB (default is dry-run).",
    )

    args = parser.parse_args(argv)

    kb_endpoint = get_kb_http_endpoint()
    pdb_endpoint = get_pdb_http_endpoint()
    auth = get_kb_auth()

    print(f"Querying KB (endpoint={kb_endpoint}) for FlyWire individuals...")
    pairs = _fetch_flywire_individual_class_pairs(kb_endpoint, auth, args.only_missing)
    if not pairs:
        print("No FlyWire individuals found (or none match filter).")
        return 0

    class_ids = sorted({cls for _, cls in pairs})
    print(f"Found {len(pairs)} individuals across {len(class_ids)} class IDs.")

    print(f"Resolving symbols from pdb (endpoint={pdb_endpoint})...")
    class_symbols = _fetch_symbols_for_classes(pdb_endpoint, auth=None, class_ids=class_ids)

    # Map individuals to resolved symbol.
    individual_to_symbol: Dict[str, str] = {}
    missing_classes = set()

    for individual, class_id in pairs:
        sym = class_symbols.get(class_id)
        if not sym:
            missing_classes.add(class_id)
            continue
        individual_to_symbol[individual] = sym

    if missing_classes:
        # Some classes have no symbol defined in pdb; they are skipped.
        # This is expected for many ontology classes (e.g., abstract classes).
        print(f"Skipped {len(missing_classes)} class IDs with no symbol in pdb")

    if not individual_to_symbol:
        print("No symbols resolved; nothing to do.")
        return 0

    statements = generate_cypher_statements(individual_to_symbol, batch_size=args.batch_size)

    print(f"Generated {len(statements)} Cypher update statements.")

    if args.apply:
        print(f"Applying {len(statements)} statements to KB (endpoint={kb_endpoint})...")
        failed = 0
        for idx, stmt in enumerate(statements, start=1):
            try:
                _run_cypher_query(kb_endpoint, stmt, auth=auth)
            except Exception as e:
                failed += 1
                print(f"[ERROR] Statement {idx} failed: {e}")
        if failed:
            print(f"Completed with {failed} failed statements.")
            return 1
        print("All statements applied successfully.")
    else:
        for stmt in statements:
            print(stmt)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
