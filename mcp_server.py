#!/usr/bin/env python3
"""Graze prize-list MCP server — masked mock data only.

Serves a masked prize dataset (names, masked emails/addresses,
PAN last-4 only — NO full PAN, NO CVV) to AI clients over MCP stdio.

Data file: ``data/sample.json`` by default; point at your own masked
export with the ``GRAZE_PRIZE_DATA`` env var. Never point it at a file
containing full PANs or CVVs.

Run:
  pip install -r requirements.txt
  python mcp_server.py
"""
from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

from mcp.server.fastmcp import FastMCP

BASE = Path(__file__).resolve().parent
DATA_FILE = Path(
    os.environ.get("GRAZE_PRIZE_DATA", BASE / "data" / "sample.json")
)

mcp = FastMCP("graze-prize")


def _load() -> list[dict]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"dataset not found: {DATA_FILE} "
            "(set GRAZE_PRIZE_DATA to your masked export)"
        )
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else [data]


@mcp.resource("prize://masked-schema")
def masked_schema() -> str:
    """Field layout of the masked prize dataset (no PAN, no CVV)."""
    return json.dumps(
        {
            "id": "1-based row number",
            "name": "mock full name",
            "email": "masked, first char + ***@domain",
            "address": "digits starred",
            "postalZip": "first 2 chars + ***",
            "pan_last4": "last 4 digits only",
            "lastRx": "mock prescription name",
            "memberid": "masked, *** + last 4",
        },
        indent=2,
    )


@mcp.tool()
def prize_stats() -> str:
    """Dataset overview: record count, distinct Rx count, top Rx values."""
    data = _load()
    top = Counter(r["lastRx"] for r in data).most_common(10)
    return json.dumps(
        {
            "records": len(data),
            "distinct_rx": len({r["lastRx"] for r in data}),
            "top_rx": [{"rx": rx, "count": n} for rx, n in top],
            "privacy": "masked only: no full PAN, no CVV",
            "source": str(DATA_FILE.name),
        },
        indent=2,
    )


@mcp.tool()
def search_records(query: str, limit: int = 10) -> str:
    """Search masked records by name, Rx, email, or PAN last-4."""
    data = _load()
    q = (query or "").lower()
    hits = [
        r
        for r in data
        if q in (f"{r['name']} {r['lastRx']} {r['pan_last4']} {r['email']}").lower()
    ][: max(1, min(limit, 50))]
    return json.dumps({"query": query, "hits": len(hits), "records": hits}, indent=2)


@mcp.tool()
def get_record(record_id: int) -> str:
    """Fetch one masked record by 1-based id."""
    data = _load()
    if not 1 <= record_id <= len(data):
        raise ValueError(f"record_id out of range 1..{len(data)}")
    return json.dumps(data[record_id - 1], indent=2)


@mcp.tool()
def list_rx_values() -> str:
    """List all distinct mock Rx values in the dataset."""
    data = _load()
    return json.dumps(sorted({r["lastRx"] for r in data}), indent=2)


if __name__ == "__main__":
    mcp.run()
