"""Helper to load VFB KB credentials and endpoints.

This module allows storing writable KB credentials in a hidden file (".kbw_credentials")
that is *not* checked into source control.

The file format is simple key=value, and keys can include:
  KBW_USER          - Neo4j username (default: neo4j)
  KBW_PASSWORD      - Neo4j password (default: vfb)
  KBW_HOST          - Hostname for KB (default: kb.virtualflybrain.org)
  KBW_HTTP_ENDPOINT - Full HTTP REST endpoint (default: http://{KBW_HOST}/db/data/transaction/commit)
  KBW_BOLT_URI      - Bolt URI (default: neo4j://{KBW_HOST})

You can also override any of these via environment variables of the same name.

Example ~/.kbw_credentials:
  KBW_USER=neo4j
  KBW_PASSWORD=vfb
  KBW_HOST=kb.virtualflybrain.org
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Tuple


DEFAULT_HOST = os.getenv("KBW_HOST", "kb.virtualflybrain.org")
DEFAULT_HTTP_ENDPOINT = os.getenv("KBW_HTTP_ENDPOINT", f"http://{DEFAULT_HOST}/db/data/transaction/commit")
DEFAULT_BOLT_URI = os.getenv("KBW_BOLT_URI", f"neo4j://{DEFAULT_HOST}")

DEFAULT_PDB_HOST = os.getenv("KBW_PDB_HOST", "pdb.virtualflybrain.org")
DEFAULT_PDB_HTTP_ENDPOINT = os.getenv("KBW_PDB_HTTP_ENDPOINT", f"http://{DEFAULT_PDB_HOST}/db/data/transaction/commit")

DEFAULT_USER = os.getenv("KBW_USER", "neo4j")
DEFAULT_PASSWORD = os.getenv("KBW_PASSWORD", "vfb")


def _find_credentials_file() -> Optional[Path]:
    """Find a local .kbw_credentials file to load overrides from."""

    candidates = [
        Path.cwd() / ".kbw_credentials",
        Path(__file__).resolve().parent / ".kbw_credentials",
        Path.home() / ".kbw_credentials",
    ]

    for p in candidates:
        if p.is_file():
            return p
    return None


def _parse_credentials_file(path: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def _load_settings() -> Dict[str, str]:
    # Base defaults (may be overridden via .kbw_credentials or env vars).
    settings: Dict[str, str] = {
        "KBW_HOST": DEFAULT_HOST,
        "KBW_HTTP_ENDPOINT": DEFAULT_HTTP_ENDPOINT,
        "KBW_BOLT_URI": DEFAULT_BOLT_URI,
        "KBW_PDB_HOST": DEFAULT_PDB_HOST,
        "KBW_PDB_HTTP_ENDPOINT": DEFAULT_PDB_HTTP_ENDPOINT,
        "KBW_USER": DEFAULT_USER,
        "KBW_PASSWORD": DEFAULT_PASSWORD,
    }

    # Track which keys were explicitly provided (file or env) so we can
    # recompute derived endpoints when only the host is set.
    explicit: Set[str] = set()

    # Allow overrides from a local credentials file.
    cred_file = _find_credentials_file()
    if cred_file:
        try:
            parsed = _parse_credentials_file(cred_file)
            settings.update(parsed)
            explicit.update(parsed.keys())
        except Exception:
            # Fail gracefully; keep defaults.
            pass

    # Apply any explicit env var overrides last.
    for key in [
        "KBW_HOST",
        "KBW_HTTP_ENDPOINT",
        "KBW_BOLT_URI",
        "KBW_PDB_HOST",
        "KBW_PDB_HTTP_ENDPOINT",
        "KBW_USER",
        "KBW_PASSWORD",
    ]:
        val = os.getenv(key)
        if val is not None:
            settings[key] = val  # type: ignore[arg-type]
            explicit.add(key)

    # If user only provided KBW_HOST (or KBW_PDB_HOST), derive the endpoints.
    if "KBW_HTTP_ENDPOINT" not in explicit:
        settings["KBW_HTTP_ENDPOINT"] = f"http://{settings['KBW_HOST']}/db/data/transaction/commit"
    if "KBW_BOLT_URI" not in explicit:
        settings["KBW_BOLT_URI"] = f"neo4j://{settings['KBW_HOST']}"
    if "KBW_PDB_HTTP_ENDPOINT" not in explicit:
        settings["KBW_PDB_HTTP_ENDPOINT"] = f"http://{settings['KBW_PDB_HOST']}/db/data/transaction/commit"

    return settings


def get_kbw_settings() -> Dict[str, str]:
    """Return effective KBW settings (host, endpoints, user/password)."""
    return _load_settings()


def get_kb_auth() -> Tuple[str, str]:
    """Return (username, password) to use for Neo4j basic auth."""
    settings = _load_settings()
    return settings.get("KBW_USER", DEFAULT_USER), settings.get("KBW_PASSWORD", DEFAULT_PASSWORD)


def get_kb_http_endpoint() -> str:
    """Return the HTTP REST transaction endpoint for the KB."""
    settings = _load_settings()
    return settings.get("KBW_HTTP_ENDPOINT", DEFAULT_HTTP_ENDPOINT)


def get_kb_bolt_uri() -> str:
    """Return the Bolt URI used to connect to the KB via neo4j driver."""
    settings = _load_settings()
    return settings.get("KBW_BOLT_URI", DEFAULT_BOLT_URI)


def get_pdb_http_endpoint() -> str:
    """Return the HTTP REST transaction endpoint for the pdb (class symbol store)."""
    settings = _load_settings()
    return settings.get("KBW_PDB_HTTP_ENDPOINT", DEFAULT_PDB_HTTP_ENDPOINT)
