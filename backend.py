"""
FastAPI backend — read-only API for population data.

Also exposes live Plotly pie charts as SVG (Kaleido). Each request re-reads
SQLite so charts update when the DB changes.
"""

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from chart_render import (
    PIE_CHART_IDS,
    UnknownPieChart,
    pie_title,
    render_all_pie_svgs,
    render_pie_svg,
)
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


def _load_population_rows() -> list[dict]:
    """Read current population rows from SQLite (no cache)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT country, population, updated_at FROM population "
            "ORDER BY population DESC, country ASC"
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


@app.get("/api/population")
def get_population():
    """Return all population data sorted by population descending."""
    return {"data": _load_population_rows()}


@app.get("/api/charts/pies")
def get_all_pie_svgs():
    """
    Render all three pie charts as SVG from the current DB state.

    No caching: each request re-reads SQLite and re-renders via Kaleido.
    """
    rows = _load_population_rows()
    charts = render_all_pie_svgs(rows)
    return {
        "charts": [
            {
                "id": c.id,
                "title": c.title,
                "content_type": "image/svg+xml",
                "svg": c.svg,
            }
            for c in charts
        ]
    }


@app.get("/api/charts/pies/{chart_id}")
def get_pie_svg(chart_id: str):
    """
    Render one pie chart as raw SVG (image/svg+xml).

    chart_id: share | top5 | top5-vs-rest
    """
    if chart_id not in PIE_CHART_IDS:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unknown pie chart {chart_id!r}. "
                f"Valid ids: {', '.join(PIE_CHART_IDS)}"
            ),
        )
    try:
        rendered = render_pie_svg(chart_id, _load_population_rows())
    except UnknownPieChart as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return Response(
        content=rendered.svg,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "no-store",
            "X-Pie-Chart-Id": rendered.id,
            "X-Pie-Chart-Title": pie_title(chart_id),
        },
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}
