"""
Layer 1 — Data access.

Toggle backend with DB_BACKEND:
  sqlite (default) — local ports.db + seed_data
  oracle           — server Oracle (table already created/seeded via SQL)

Both return the same shape:
  [{"port_terminal": str, "containers": int}, ...]
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from seed_data import SEED_PORTS

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DB_BACKEND = os.environ.get("DB_BACKEND", "sqlite").strip().lower()

# SQLite
_DEFAULT_DB = Path(__file__).resolve().parent / "ports.db"
DB_PATH = Path(os.environ.get("PORTS_DB_PATH", str(_DEFAULT_DB)))

# Oracle — two ways to connect (thin mode, no tnsnames.ora required):
#   A) DSN-less: ORACLE_HOST + ORACLE_PORT + ORACLE_SERVICE_NAME
#   B) Easy Connect string: ORACLE_DSN=host:port/service_name
ORACLE_USER = os.environ.get("ORACLE_USER", "").strip()
ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "")
ORACLE_HOST = os.environ.get("ORACLE_HOST", "").strip()
ORACLE_PORT = os.environ.get("ORACLE_PORT", "1521").strip()
ORACLE_SERVICE_NAME = os.environ.get("ORACLE_SERVICE_NAME", "").strip()
ORACLE_DSN = os.environ.get("ORACLE_DSN", "").strip()  # optional if host/service set
ORACLE_TABLE = os.environ.get("ORACLE_TABLE", "port_containers").strip()

_SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS port_containers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    port_terminal TEXT NOT NULL UNIQUE,
    containers INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def backend_label() -> str:
    if DB_BACKEND == "oracle":
        if ORACLE_HOST and ORACLE_SERVICE_NAME:
            target = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE_NAME}"
        else:
            target = ORACLE_DSN or "not configured"
        return f"oracle ({target}, table={ORACLE_TABLE})"
    return f"sqlite ({DB_PATH})"


# ---------------------------------------------------------------------------
# SQLite
# ---------------------------------------------------------------------------

def _sqlite_connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db() -> None:
    """SQLite only: create file/table and seed if empty."""
    if DB_BACKEND != "sqlite":
        return
    conn = _sqlite_connect()
    try:
        conn.execute(_SCHEMA_SQLITE)
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


def reseed_db() -> int:
    """SQLite only: replace all rows with SEED_PORTS."""
    if DB_BACKEND != "sqlite":
        raise RuntimeError(
            "reseed_db() is only for SQLite. "
            "For Oracle run sql/oracle_seed.sql on the server."
        )
    conn = _sqlite_connect()
    try:
        conn.execute(_SCHEMA_SQLITE)
        conn.execute("DELETE FROM port_containers")
        conn.executemany(
            "INSERT INTO port_containers (port_terminal, containers) VALUES (?, ?)",
            SEED_PORTS,
        )
        conn.commit()
        return len(SEED_PORTS)
    finally:
        conn.close()


def _load_rows_sqlite() -> list[dict]:
    ensure_db()
    conn = _sqlite_connect()
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


# ---------------------------------------------------------------------------
# Oracle (python-oracledb thin mode — no Instant Client required)
# ---------------------------------------------------------------------------

def _oracle_connect() -> Any:
    """
    Connect without tnsnames.ora.

    Preferred (DSN-less):
      ORACLE_USER, ORACLE_PASSWORD, ORACLE_HOST, ORACLE_PORT, ORACLE_SERVICE_NAME

    Alternative (Easy Connect string as dsn):
      ORACLE_DSN=host:port/service_name
    """
    try:
        import oracledb
    except ImportError as exc:
        raise RuntimeError(
            "oracledb is not installed. Run: pip install oracledb"
        ) from exc

    if not ORACLE_USER:
        raise RuntimeError("Oracle mode needs ORACLE_USER.")

    # A) DSN-less: separate host / port / service_name
    if ORACLE_HOST and ORACLE_SERVICE_NAME:
        return oracledb.connect(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            host=ORACLE_HOST,
            port=int(ORACLE_PORT or "1521"),
            service_name=ORACLE_SERVICE_NAME,
        )

    # B) Easy Connect string in ORACLE_DSN
    if ORACLE_DSN:
        return oracledb.connect(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=ORACLE_DSN,
        )

    raise RuntimeError(
        "Oracle mode needs either:\n"
        "  ORACLE_HOST + ORACLE_SERVICE_NAME (+ optional ORACLE_PORT, default 1521)\n"
        "  OR ORACLE_DSN=host:port/service_name\n"
        "No tnsnames.ora / TNS alias required (thin mode)."
    )


def _row_get(row: Any, *names: str) -> Any:
    """Fetch a column case-insensitively (Oracle often returns UPPER names)."""
    if isinstance(row, dict):
        lower_map = {str(k).lower(): v for k, v in row.items()}
        for n in names:
            if n.lower() in lower_map:
                return lower_map[n.lower()]
    # tuple / sequence from cursor with description
    return None


def _load_rows_oracle() -> list[dict]:
    conn = _oracle_connect()
    try:
        cur = conn.cursor()
        # Unquoted identifiers → Oracle uppercase; alias keeps app keys stable
        sql = f"""
            SELECT port_terminal AS port_terminal,
                   containers    AS containers
            FROM {ORACLE_TABLE}
            ORDER BY containers DESC, port_terminal ASC
        """
        cur.execute(sql)
        colnames = [d[0].lower() for d in cur.description]
        out: list[dict] = []
        for tup in cur:
            rec = dict(zip(colnames, tup))
            out.append(
                {
                    "port_terminal": str(rec["port_terminal"]),
                    "containers": int(rec["containers"]),
                }
            )
        return out
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_rows() -> list[dict]:
    """
    Read all terminals, largest container count first.
    Same dict shape for sqlite and oracle.
    """
    if DB_BACKEND == "oracle":
        return _load_rows_oracle()
    if DB_BACKEND == "sqlite":
        return _load_rows_sqlite()
    raise RuntimeError(
        f"Unknown DB_BACKEND={DB_BACKEND!r}. Use 'sqlite' or 'oracle'."
    )


# Back-compat alias used by older snippets
def get_connection() -> sqlite3.Connection:
    if DB_BACKEND != "sqlite":
        raise RuntimeError("get_connection() is SQLite-only; use load_rows() instead.")
    return _sqlite_connect()


if __name__ == "__main__":
    import sys

    print(f"Backend: {backend_label()}")
    if DB_BACKEND == "sqlite" and "--reseed" in sys.argv:
        n = reseed_db()
        print(f"Reseeded {n} terminals into {DB_PATH}")

    rows = load_rows()
    print(f"Rows: {len(rows)}")
    print("Top 5:")
    for r in rows[:5]:
        print(f"  {r['port_terminal']:<48} {r['containers']:>8,}")
