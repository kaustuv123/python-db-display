"""Port containers API — JSON + SVG pie charts; optional PNG export on change."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from chart_render import PIE_CHART_IDS, pie_title, render_all_pie_svgs, render_pie_svg
from database import get_connection, init_db, seed_data
from png_export import start_png_export_scheduler, stop_png_export_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

init_db()
seed_data()


def _load_port_rows() -> list[dict]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT port_terminal, containers, updated_at FROM port_containers "
            "ORDER BY containers DESC, port_terminal ASC"
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_png_export_scheduler(_load_port_rows)
    try:
        yield
    finally:
        stop_png_export_scheduler()


app = FastAPI(title="Port Containers Dashboard API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/ports")
def get_ports():
    return {"data": _load_port_rows()}


@app.get("/api/charts/pies")
def get_all_pie_svgs():
    charts = render_all_pie_svgs(_load_port_rows())
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
    if chart_id not in PIE_CHART_IDS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown pie chart {chart_id!r}. Valid: {', '.join(PIE_CHART_IDS)}",
        )
    rendered = render_pie_svg(chart_id, _load_port_rows())
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
