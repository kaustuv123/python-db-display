"""
Layer 1 — Data access.

Job: open the SQLite file and return port-terminal rows as plain Python dicts.

First principles:
  - ports.db is one file on disk = the whole database.
  - We CONNECT, run SQL, get ROWS, then CLOSE.
  - The rest of the app never talks SQL; it only sees list[dict].
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

# Default: ports.db next to this file. Override with PORTS_DB_PATH.
_DEFAULT_DB = Path(__file__).resolve().parent / "ports.db"
DB_PATH = Path(os.environ.get("PORTS_DB_PATH", str(_DEFAULT_DB)))


def get_connection() -> sqlite3.Connection:
    """Open a connection. row_factory makes each row act like a dict."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_rows() -> list[dict]:
    """
    Read all terminals, largest container count first.

    Returns e.g.:
      [{"port_terminal": "MUN-CT", "containers": 14230}, ...]
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT port_terminal, containers
            FROM port_containers
            ORDER BY containers DESC, port_terminal ASC
            """
        )
        return [
            {
                "port_terminal": str(row["port_terminal"]),
                "containers": int(row["containers"]),
            }
            for row in cur.fetchall()
        ]
    finally:
        conn.close()


if __name__ == "__main__":
    # Smoke test: python db.py
    rows = load_rows()
    print(f"DB: {DB_PATH}")
    print(f"Rows: {len(rows)}")
    print("Top 5:")
    for r in rows[:5]:
        print(f"  {r['port_terminal']:<12} {r['containers']:>8,}")
