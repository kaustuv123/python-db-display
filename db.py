"""
Layer 1 — Data access.

Job: open the SQLite file and return port-terminal rows as plain Python dicts.

First principles:
  - ports.db is one file on disk = the whole database.
  - If the file is missing/empty (e.g. fresh git clone), we create the table
    and seed from seed_data.py (which IS in git).
  - We CONNECT, run SQL, get ROWS, then CLOSE.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from seed_data import SEED_PORTS

# Default: ports.db next to this file. Override with PORTS_DB_PATH.
_DEFAULT_DB = Path(__file__).resolve().parent / "ports.db"
DB_PATH = Path(os.environ.get("PORTS_DB_PATH", str(_DEFAULT_DB)))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS port_containers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    port_terminal TEXT NOT NULL UNIQUE,
    containers INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def get_connection() -> sqlite3.Connection:
    """Open a connection. row_factory makes each row act like a dict."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db() -> None:
    """
    Make sure ports.db exists, has the table, and has rows.

    - CREATE TABLE IF NOT EXISTS (safe every time)
    - INSERT OR IGNORE seed rows only when the table is empty
      so local edits are never wiped on restart
    """
    conn = get_connection()
    try:
        conn.execute(_SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM port_containers").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT OR IGNORE INTO port_containers (port_terminal, containers) "
                "VALUES (?, ?)",
                SEED_PORTS,
            )
            conn.commit()
    finally:
        conn.close()


def load_rows() -> list[dict]:
    """
    Read all terminals, largest container count first.

    Returns e.g.:
      [{"port_terminal": "MUN-CT", "containers": 14230}, ...]
    """
    ensure_db()
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
    print(f"Exists: {DB_PATH.exists()}  size={DB_PATH.stat().st_size if DB_PATH.exists() else 0}")
    print(f"Rows: {len(rows)}")
    print("Top 5:")
    for r in rows[:5]:
        print(f"  {r['port_terminal']:<12} {r['containers']:>8,}")
