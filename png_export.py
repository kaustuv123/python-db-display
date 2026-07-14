"""
Write pie charts as 600x400 PNGs every 2 minutes when data changes.
Set PNG_EXPORT_DIR to enable. Fixed filenames overwrite in place.
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading
from pathlib import Path
from typing import Callable, Sequence

from chart_render import PNG_HEIGHT, PNG_WIDTH, PIE_CHART_IDS, render_all_pie_pngs

logger = logging.getLogger(__name__)

PNG_EXPORT_DIR: str = os.environ.get("PNG_EXPORT_DIR", "").strip()
PNG_EXPORT_INTERVAL_SEC: int = int(os.environ.get("PNG_EXPORT_INTERVAL_SEC", "120"))

PNG_FILENAMES = {cid: f"containers-{cid}.png" for cid in PIE_CHART_IDS}

_lock = threading.Lock()
_last_fingerprint: str | None = None
_stop = threading.Event()
_thread: threading.Thread | None = None


def _fingerprint(rows: Sequence[dict]) -> str:
    items = sorted(
        (str(r["port_terminal"]).strip(), int(r["containers"])) for r in rows
    )
    return hashlib.sha256(repr(items).encode()).hexdigest()


def export_pngs_if_changed(rows: Sequence[dict], export_dir: str | None = None) -> bool:
    """Write PNGs only if data changed. Returns True when files were written."""
    global _last_fingerprint

    out = (export_dir if export_dir is not None else PNG_EXPORT_DIR).strip()
    if not out:
        return False

    fp = _fingerprint(rows)
    with _lock:
        if fp == _last_fingerprint:
            return False

        dest = Path(out)
        dest.mkdir(parents=True, exist_ok=True)

        for chart in render_all_pie_pngs(rows, width=PNG_WIDTH, height=PNG_HEIGHT):
            path = dest / PNG_FILENAMES[chart.id]
            tmp = path.with_suffix(".png.tmp")
            tmp.write_bytes(chart.png)
            tmp.replace(path)
            logger.info("Wrote PNG %s (%d bytes)", path, len(chart.png))

        _last_fingerprint = fp
        return True


def _loop(load_rows: Callable[[], list[dict]]) -> None:
    while not _stop.is_set():
        try:
            export_pngs_if_changed(load_rows())
        except Exception:
            logger.exception("PNG export cycle failed")
        if _stop.wait(PNG_EXPORT_INTERVAL_SEC):
            break


def start_png_export_scheduler(load_rows: Callable[[], list[dict]]) -> None:
    global _thread

    if not PNG_EXPORT_DIR:
        logger.warning(
            "PNG export disabled (set PNG_EXPORT_DIR). "
            "Would write %s every %ss at %dx%d on data change.",
            ", ".join(PNG_FILENAMES.values()),
            PNG_EXPORT_INTERVAL_SEC,
            PNG_WIDTH,
            PNG_HEIGHT,
        )
        return

    if _thread is not None and _thread.is_alive():
        return

    _stop.clear()
    _thread = threading.Thread(
        target=_loop, args=(load_rows,), name="png-export", daemon=True
    )
    _thread.start()
    logger.info(
        "PNG export → %s every %ss (%dx%d, change-only)",
        PNG_EXPORT_DIR,
        PNG_EXPORT_INTERVAL_SEC,
        PNG_WIDTH,
        PNG_HEIGHT,
    )


def stop_png_export_scheduler() -> None:
    _stop.set()
    if _thread is not None and _thread.is_alive():
        _thread.join(timeout=5.0)
