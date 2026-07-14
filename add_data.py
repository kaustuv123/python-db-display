"""
Add / update port-terminal container rows.

  python add_data.py
  python add_data.py JNPT-CT 13000
  python add_data.py --update JNPT-CT 13000
"""

import sys

from database import get_connection, init_db


def add_or_update(port_terminal: str, containers: int, *, update_only: bool = False) -> None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if update_only:
            cur.execute(
                "UPDATE port_containers SET containers = ?, "
                "updated_at = CURRENT_TIMESTAMP WHERE port_terminal = ?",
                (containers, port_terminal),
            )
            if cur.rowcount == 0:
                print(f"Not found: {port_terminal} (use without --update to insert)")
                return
            action = "Updated"
        else:
            cur.execute(
                "INSERT OR REPLACE INTO port_containers "
                "(port_terminal, containers, updated_at) "
                "VALUES (?, ?, CURRENT_TIMESTAMP)",
                (port_terminal, containers),
            )
            action = "Saved"
        conn.commit()
        print(f"{action}: {port_terminal} → {containers:,}")
    finally:
        conn.close()


def list_all() -> None:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT port_terminal, containers, updated_at FROM port_containers "
            "ORDER BY containers DESC"
        ).fetchall()
    finally:
        conn.close()

    print(f"\n{'Port Terminal':<16} {'Containers':>12} {'Updated At':>22}")
    print("-" * 54)
    for r in rows:
        print(f"{r['port_terminal']:<16} {r['containers']:>12,} {r['updated_at']:>22}")
    print()


def interactive() -> None:
    print("Commands: add <terminal> <n> | update <terminal> <n> | list | quit\n")
    while True:
        try:
            cmd = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not cmd:
            continue
        parts = cmd.split()
        action = parts[0].lower()
        if action in ("quit", "exit", "q"):
            break
        if action == "list":
            list_all()
            continue
        if action in ("add", "update") and len(parts) == 3:
            try:
                n = int(parts[2])
            except ValueError:
                print("containers must be an integer")
                continue
            add_or_update(parts[1].upper(), n, update_only=(action == "update"))
            continue
        print("Usage: add|update <terminal> <containers> | list | quit")


if __name__ == "__main__":
    init_db()
    args = sys.argv[1:]
    if not args:
        interactive()
    elif args[0] == "--update" and len(args) == 3:
        add_or_update(args[1], int(args[2]), update_only=True)
    elif len(args) == 2:
        add_or_update(args[0], int(args[1]))
    else:
        print(__doc__)
