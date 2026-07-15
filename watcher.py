"""
Layer 3 — Watcher (process entrypoint).

Job: every 2 minutes, load DB → always redraw the three PNGs.

First principles:
  - A "watcher" is just a loop + sleep — not magic events from SQLite.
  - Every cycle rewrites the same three filenames (overwrite in place).
  - Ctrl+C stops cleanly.
"""

from __future__ import annotations

import logging
import os
import time

from charts import EXPORT_DIR, render_all
from db import DB_PATH, load_rows

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("watcher")

INTERVAL_SEC = int(os.environ.get("PNG_EXPORT_INTERVAL_SEC", "120"))


def run_once() -> None:
    """One cycle: load rows and write all three PNGs."""
    rows = load_rows()
    paths = render_all(rows)
    logger.info(
        "Wrote %d PNG(s) from %d rows → %s",
        len(paths),
        len(rows),
        EXPORT_DIR,
    )
    for p in paths:
        logger.info("  %s", p)


def main() -> None:
    logger.info("DB:       %s", DB_PATH)
    logger.info("Export:   %s", EXPORT_DIR)
    logger.info("Interval: %ss (always rewrite)", INTERVAL_SEC)
    logger.info("Press Ctrl+C to stop.")

    # First cycle runs immediately.
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
