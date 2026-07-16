"""
Watcher (process entrypoint).

Job: every 2 minutes, load rows from SQLite or Oracle → always redraw charts.
"""

from __future__ import annotations

import logging
import os
import time

from charts import EXPORT_DIR, render_all
from db import backend_label, load_rows

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("watcher")

INTERVAL_SEC = int(os.environ.get("PNG_EXPORT_INTERVAL_SEC", "120"))


def run_once() -> None:
    """One cycle: load rows and write all chart PNGs/WebPs."""
    rows = load_rows()
    paths = render_all(rows)
    logger.info(
        "Wrote %d file(s) from %d rows → %s",
        len(paths),
        len(rows),
        EXPORT_DIR,
    )
    for p in paths:
        logger.info("  %s", p)


def main() -> None:
    logger.info("Backend:  %s", backend_label())
    logger.info("Export:   %s", EXPORT_DIR)
    logger.info("Interval: %ss (always rewrite)", INTERVAL_SEC)
    logger.info("Press Ctrl+C to stop.")

    try:
        while True:
            try:
                run_once()
            except Exception:
                logger.exception("Cycle failed; will retry after interval")
            time.sleep(INTERVAL_SEC)
    except KeyboardInterrupt:
        logger.info("Stopped.")


if __name__ == "__main__":
    main()
