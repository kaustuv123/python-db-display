"""
Standalone script to add / update population data in the database.
Use this to change rows; pie SVG endpoints re-read the DB on each request.

Usage:
    python add_data.py                          # Interactive mode
    python add_data.py "France" 68              # Quick add via CLI args
    python add_data.py --update "India" 1500    # Update existing country
"""

import sys
import os

# Add project root to path so we can import database module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_connection, init_db


def add_or_update(country: str, population: int, force_update: bool = False):
    """Insert a new country or update an existing one."""
    conn = get_connection()
    cursor = conn.cursor()

    if force_update:
        cursor.execute(
            "UPDATE population SET population = ?, updated_at = CURRENT_TIMESTAMP WHERE country = ?",
            (population, country),
        )
        if cursor.rowcount == 0:
            print(f"Country '{country}' not found. Use without --update to add it.")
            conn.close()
            return
        action = "Updated"
    else:
        cursor.execute(
            "INSERT OR REPLACE INTO population (country, population, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (country, population),
        )
        action = "Added/replaced"

    conn.commit()
    conn.close()
    print(f"✅ {action}: {country} → {population}M")


def list_all():
    """Show all current data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT country, population, updated_at FROM population ORDER BY population DESC")
    rows = cursor.fetchall()
    conn.close()

    print(f"\n{'Country':<25} {'Population (M)':>15} {'Updated At':>22}")
    print("─" * 65)
    for r in rows:
        print(f"{r['country']:<25} {r['population']:>15,} {r['updated_at']:>22}")
    print()


def interactive_mode():
    """Simple interactive loop for adding data."""
    print("\n╔══════════════════════════════════════════╗")
    print("║   Population Data Manager                ║")
    print("╠══════════════════════════════════════════╣")
    print("║  Commands:                               ║")
    print("║    add <country> <population>            ║")
    print("║    update <country> <population>         ║")
    print("║    list                                  ║")
    print("║    quit                                  ║")
    print("╚══════════════════════════════════════════╝\n")

    while True:
        try:
            cmd = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not cmd:
            continue

        parts = cmd.split(maxsplit=2)
        action = parts[0].lower()

        if action in ("quit", "exit", "q"):
            print("Bye!")
            break
        elif action == "list":
            list_all()
        elif action in ("add", "update") and len(parts) == 3:
            country = parts[1].replace("_", " ").title()
            try:
                population = int(parts[2])
            except ValueError:
                print("Population must be a number.")
                continue
            add_or_update(country, population, force_update=(action == "update"))
        else:
            print("Usage: add <country> <population>  |  update <country> <population>  |  list  |  quit")


if __name__ == "__main__":
    init_db()

    args = sys.argv[1:]
    if not args:
        interactive_mode()
    elif args[0] == "--update" and len(args) == 3:
        add_or_update(args[1], int(args[2]), force_update=True)
    elif len(args) == 2:
        add_or_update(args[0], int(args[1]))
    else:
        print("Usage:")
        print('  python add_data.py                        # Interactive')
        print('  python add_data.py "France" 68            # Quick add')
        print('  python add_data.py --update "India" 1500  # Update')
