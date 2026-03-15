#!/usr/bin/env python3
"""Dump Cypher update statements for FlyWire Individuals from Neo4j (pdb).

This script connects to the VFB KB Neo4j HTTP REST endpoint and runs a
read-only Cypher query to find Individuals whose label starts with
"FlyWire:" and have a symbol set. It then prints a compact set of Cypher
statements that update those Individuals to use the Class symbol.

Because many FlyWire Individuals share the same Class symbol, this script
groups updates by symbol and emits fewer Cypher statements using
`WHERE i.short_form IN [...]`.

You can pipe the output into `cypher-shell` or load it into another tool.

Example:
    python dump_vfb_symbol_updates.py | tee updates.cypher
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

import requests


def _run_cypher_query(query: str) -> List[Dict[str, Any]]:
    """Run a Cypher query via the Neo4j HTTP REST transaction endpoint."""

    endpoint = "http://kb.virtualflybrain.org/db/data/transaction/commit"
    auth = ("neo4j", "vfb")
    payload = {
        "statements": [
            {
                "statement": query,
                "parameters": {},
                "resultDataContents": ["row"],
            }
        ]
    }

    resp = requests.post(endpoint, json=payload, auth=auth, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    statements = data.get("results", [])
    if not statements:
        return []

    # Each statement may return multiple rows.
    return [row_obj.get("row", []) for row_obj in statements[0].get("data", [])]


def main() -> int:
    cypher_query = """
MATCH (i:Individual)
WHERE i.label CONTAINS 'FlyWire'
  AND i.short_form STARTS WITH 'VFB_'
  AND exists(i.symbol)
RETURN i.symbol[0] AS symbol, collect(i.short_form) AS individuals
"""

    try:
        rows = _run_cypher_query(cypher_query)
    except Exception as e:
        print("ERROR: failed to query Neo4j:", e, file=sys.stderr)
        return 1

    if not rows:
        print("No results returned. Check Neo4j connection and query.")
        return 1

    for row in rows:
        # Each row is a list matching the projected columns.
        class_symbol, individuals = row
        if not class_symbol or not individuals:
            continue

        # Escape values into valid Cypher list literals.
        symbol_literal = json.dumps([class_symbol])
        individuals_literal = json.dumps(individuals)

        cypher = (
            "MATCH (i:Individual)\n"
            f"WHERE i.short_form IN {individuals_literal}\n"
            f"SET i.symbol = {symbol_literal} WITH 0 as dummy"
        )

        print(cypher)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
