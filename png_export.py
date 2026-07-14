"""
Periodic PNG export of pie charts.

- Size: 600x400 px
- Interval: every 2 minutes
- Fixed filenames (overwrite in place)
- Writes only when population data has changed
- Output directory: set PNG_EXPORT_DIR (env or constant below)
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading
from pathlib import Path
from typing import Callable, Sequence

from chart_render import (
    PNG_HEIGHT,
    PNG_WIDTH,
    PIE_CHART_IDS,
    render_all_pie_pngs,
)

logger = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────────────────────────
# Set the directory where PNGs are written. Prefer env so Docker/host can inject it.
# Example: r"C:\Users\kaust\charts" or "/data/charts"
PNG_EXPORT_DIR: str = os.environ.get("PNG_EXPORT_DIR", "").strip()

# Seconds between export checks (2 minutes)
PNG_EXPORT_INTERVAL_SEC: int = int(os.environ.get("PNG_EXPORT_INTERVAL_SEC", "120"))

# Fixed basenames — always the same file, replaced on each successful write
PNG_FILENAMES: dict[str, str] = {
    "share": "population-share.png",
    "top5": "population-top5.png",
    "top5-vs-rest": "population-top5-vs-rest.png",
}

_state_lock = threading.Lock()
_last_fingerprint: str | None = None
_stop_event = threading.Event()
_thread: threading.Thread | None = None


def data_fingerprint(rows: Sequence[dict]) -> str:
    """Stable hash of country/population pairs (order-independent for equality)."""
    items = sorted(
        (str(r["country"]).strip(), int(r["population"])) for r in rows
    )
    payload = repr(items).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def export_pngs_if_changed(
    rows: Sequence[dict],
    *,
    export_dir: str | None = None,
) -> bool:
    """
    Render and write PNGs only if population data changed since last write.

    Returns True if files were written, False if skipped (no change / disabled).
    """
    global _last_fingerprint

    out = (export_dir if export_dir is not None else PNG_EXPORT_DIR).strip()
    if not out:
        logger.debug("PNG export skipped: PNG_EXPORT_DIR is not set")
        return False

    fingerprint = data_fingerprint(rows)

    with _state_lock:
        if fingerprint == _last_fingerprint:
            logger.debug("PNG export skipped: data unchanged (%s…)", fingerprint[:12])
            return False

        dest = Path(out)
        dest.mkdir(parents=True, exist_ok=True)

        charts = render_all_pie_pngs(rows, width=PNG_WIDTH, height=PNG_HEIGHT)
        for chart in charts:
            name = PNG_FILENAMES.get(chart.id, f"{chart.id}.png")
            path = dest / name
            # Write via temp + replace for atomic overwrite on same name
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_bytes(chart.png)
            tmp.replace(path)
            logger.info(
                "Wrote PNG %s (%dx%d, %d bytes)",
                path,
                chart.width,
                chart.height,
                len(chart.png),
            )

        _last_fingerprint = fingerprint
        return True


def _loop(load_rows: Callable[[], list[dict]]) -> None:
    """Background loop: check every interval; write only on data change."""
    # Run once immediately so a path set at startup produces files without waiting.
    while not _stop_event.is_set():
        try:
            rows = load_rows()
            export_pngs_if_changed(rows)
        except Exception:
            logger.exception("PNG export cycle failed")

        # Wait interval or exit early on stop
        if _stop_event.wait(PNG_EXPORT_INTERVAL_SEC):
            break


def start_png_export_scheduler(load_rows: Callable[[], list[dict]]) -> None:
    """Start the 2-minute PNG export background thread (idempotent)."""
    global _thread

    if not PNG_EXPORT_DIR:
        logger.warning(
            "PNG export disabled: set PNG_EXPORT_DIR to a folder path to enable "
            "(files: %s; size %dx%d; every %ss; write only on data change)",
            ", ".join(PNG_FILENAMES[c] for c in PIE_CHART_IDS),
            PNG_WIDTH,
            PNG_HEIGHT,
            PNG_EXPORT_INTERVAL_SEC,
        )
        return

    if _thread is not None and _thread.is_alive():
        return

    _stop_event.clear()
    _thread = threading.Thread(
        target=_loop,
        args=(load_rows,),
        name="png-export",
        daemon=True,
    )
    _thread.start()
    logger.info(
        "PNG export scheduler started → %s every %ss (%dx%d, change-only)",
        PNG_EXPORT_DIR,
        PNG_EXPORT_INTERVAL_SEC,
        PNG_WIDTH,
        PNG_HEIGHT,
    )


def stop_png_export_scheduler() -> None:
    """Signal the background exporter to stop."""
    _stop_event.set()
    t = _thread
    if t is not None and t.is_alive():
        t.join(timeout=5.0)
