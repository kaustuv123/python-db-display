"""
FastAPI backend — read-only API for population data.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection, init_db, seed_data

# Ensure DB is ready on startup
init_db()
seed_data()

app = FastAPI(title="Population Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/population")
def get_population():
    """Return all population data sorted by population descending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT country, population, updated_at FROM population ORDER BY population DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"data": rows}


@app.get("/api/health")
def health():
    return {"status": "ok"}
