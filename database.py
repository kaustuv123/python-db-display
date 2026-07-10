"""
Database setup and seed data for the population dashboard.
Uses SQLite with an abstraction layer that can be swapped for Oracle later.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "population.db")


def get_connection():
    """Get a SQLite connection. Replace this function for Oracle support later."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS population (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL UNIQUE,
            population INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def seed_data():
    """Insert initial dummy population data (in millions)."""
    countries = [
        ("China", 1425),
        ("India", 1417),
        ("United States", 333),
        ("Indonesia", 275),
        ("Pakistan", 230),
        ("Nigeria", 219),
        ("Brazil", 215),
        ("Bangladesh", 171),
        ("Russia", 145),
        ("Mexico", 128),
        ("Japan", 125),
        ("Ethiopia", 123),
        ("Philippines", 115),
        ("Egypt", 104),
        ("Germany", 84),
    ]

    conn = get_connection()
    cursor = conn.cursor()
    for country, pop in countries:
        cursor.execute(
            "INSERT OR IGNORE INTO population (country, population) VALUES (?, ?)",
            (country, pop),
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database initialized and seeded successfully.")
