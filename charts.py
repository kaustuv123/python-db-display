"""
Charts (matplotlib → PNG + WebP).

Job: take rows → three chart "recipes" → write fixed filenames under Downloads/pie.

First principles:
  - A pie is only readable with a handful of slices (each = value / total).
  - With ~50 terminals, use a vertical bar chart (categories on X, values on Y).
  - Each chart is saved as .png and .webp (same basename, overwrite in place).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # headless: must be set before pyplot import
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import cm  # noqa: E402

# Default export dir: your Downloads/pie folder
_DEFAULT_EXPORT = Path.home() / "Downloads" / "pie"
EXPORT_DIR = Path(os.environ.get("PNG_EXPORT_DIR", str(_DEFAULT_EXPORT)))

DPI = 120
# Both formats every cycle (WebP needs Pillow — already a matplotlib dependency path)
EXPORT_FORMATS: tuple[str, ...] = ("png", "webp")

# How many largest terminals appear in the pie charts
TOP_N = 25

CHART_IDS: tuple[str, ...] = ("share", "top25", "top25-vs-rest")

TITLES = {
    "share": "Container Share by Terminal (all)",
    "top25": f"Top {TOP_N} Terminal Container Share",
    "top25-vs-rest": f"Top {TOP_N} Terminals vs Rest",
}

# Basename without extension — we write containers-share.png and .webp, etc.
BASENAMES = {
    "share": "containers-share",
    "top25": "containers-top25",
    "top25-vs-rest": "containers-top25-vs-rest",
}


@dataclass(frozen=True)
class Slice:
    label: str
    value: int


def rows_to_slices(rows: Sequence[dict]) -> list[Slice]:
    """Clean + sort largest first."""
    cleaned: list[Slice] = []
    for r in rows:
        name = str(r.get("port_terminal", "")).strip()
        count = int(r["containers"])
        if name and count >= 0:
            cleaned.append(Slice(name, count))
    cleaned.sort(key=lambda s: (-s.value, s.label))
    return cleaned


def slices_for_chart(chart_id: str, slices: Sequence[Slice]) -> list[Slice]:
    """
    Recipes:

      share           → every terminal (vertical bar chart)
      top25           → only the TOP_N largest (pie)
      top25-vs-rest   → TOP_N largest + one "Other" bucket (pie)
    """
    if chart_id == "share":
        return list(slices)
    if chart_id == "top25":
        return list(slices[:TOP_N])
    if chart_id == "top25-vs-rest":
        if not slices:
            return []
        top = list(slices[:TOP_N])
        rest = sum(s.value for s in slices[TOP_N:])
        if rest > 0:
            top.append(Slice("Other", rest))
        return top
    raise ValueError(f"Unknown chart id: {chart_id!r}")


def _atomic_save_formats(fig: plt.Figure, out_dir: Path, basename: str) -> list[Path]:
    """
    Write the same figure as PNG and WebP.
    Atomic: write *.tmp then replace final name.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for fmt in EXPORT_FORMATS:
        dest = out_dir / f"{basename}.{fmt}"
        tmp = dest.with_name(dest.name + ".tmp")
        save_kwargs: dict = {
            "format": fmt,
            "bbox_inches": "tight",
            "facecolor": "white",
            "dpi": DPI,
        }
        if fmt == "webp":
            # Pillow quality for WebP (matplotlib routes through PIL)
            save_kwargs["pil_kwargs"] = {"quality": 90, "method": 4}
        fig.savefig(tmp, **save_kwargs)
        tmp.replace(dest)
        written.append(dest)
    plt.close(fig)
    return written


def _draw_share_bars(series: Sequence[Slice], out_dir: Path, basename: str) -> list[Path]:
    """
    Full share: vertical bars — terminals on X, containers on Y (axes inverted
    vs the previous horizontal layout).
    """
    title = TITLES["share"]
    n = max(len(series), 1)
    # Wide figure so many long terminal names fit when rotated
    width = max(16.0, 0.38 * n + 2.0)
    fig, ax = plt.subplots(figsize=(width, 10.0))

    if not series:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    else:
        # Largest first (left → right)
        labels = [s.label for s in series]
        values = [s.value for s in series]
        total = sum(values) or 1
        percents = [100.0 * v / total for v in values]

        colors = cm.Blues([(0.35 + 0.55 * (v / max(values))) for v in values])
        x = range(len(series))
        ax.bar(x, values, color=colors, edgecolor="white", linewidth=0.4, width=0.8)

        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=7, rotation=90, ha="center")
        ax.set_ylabel("Containers")
        ax.set_xlabel("Port terminal")
        ax.set_title(title, fontsize=14, pad=12)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)

        ymax = max(values) if values else 1
        for i, (val, pct) in enumerate(zip(values, percents)):
            ax.text(
                i,
                val + ymax * 0.015,
                f"{val:,}\n({pct:.1f}%)",
                va="bottom",
                ha="center",
                fontsize=6.5,
                color="#1f2937",
                linespacing=1.1,
            )
        ax.set_ylim(0, ymax * 1.18)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.tight_layout()
    return _atomic_save_formats(fig, out_dir, basename)


def _draw_pie(chart_id: str, series: Sequence[Slice], out_dir: Path, basename: str) -> list[Path]:
    """Pie for top-N charts (legend carries labels; wedges show % only when large enough)."""
    title = TITLES[chart_id]
    n = max(len(series), 1)
    # Extra height/width for long CONCOR names in the legend
    fig, ax = plt.subplots(figsize=(13, max(8.0, 0.28 * n + 4.0)))

    if not series:
        ax.pie([1], labels=["No data"], colors=["#e5e7eb"])
    else:
        labels = [s.label for s in series]
        values = [s.value for s in series]
        # tab20 has 20 distinct colors; cycle if we ever go past that (+ Other)
        cmap = plt.colormaps["tab20"]
        colors = [cmap(i % 20) for i in range(len(series))]

        wedges, texts, autotexts = ax.pie(
            values,
            labels=None,  # names live in the legend; every wedge shows %
            autopct=lambda pct: f"{pct:.1f}%",
            startangle=90,
            colors=colors,
            pctdistance=0.72,
            wedgeprops=dict(width=0.55, edgecolor="white", linewidth=1.0),
            textprops=dict(fontsize=8),
        )
        for t in autotexts:
            t.set_fontsize(7)
            t.set_color("#111827")
            t.set_fontweight("bold")

        ax.legend(
            wedges,
            [f"{lab}: {val:,}" for lab, val in zip(labels, values)],
            title="Terminal (containers)",
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            fontsize=7,
            frameon=False,
        )

    ax.set_title(title, fontsize=14, pad=16)
    fig.tight_layout()
    return _atomic_save_formats(fig, out_dir, basename)


def render_chart(chart_id: str, series: Sequence[Slice], out_dir: Path) -> list[Path]:
    basename = BASENAMES[chart_id]
    if chart_id == "share":
        return _draw_share_bars(series, out_dir, basename)
    return _draw_pie(chart_id, series, out_dir, basename)


def render_all(rows: Sequence[dict], export_dir: Path | None = None) -> list[Path]:
    """Build all charts as PNG + WebP. Fixed basenames, overwrite each cycle."""
    out = Path(export_dir) if export_dir is not None else EXPORT_DIR
    all_slices = rows_to_slices(rows)
    written: list[Path] = []

    for chart_id in CHART_IDS:
        series = slices_for_chart(chart_id, all_slices)
        written.extend(render_chart(chart_id, series, out))

    return written


if __name__ == "__main__":
    from db import load_rows

    rows = load_rows()
    paths = render_all(rows)
    print(f"Export dir: {EXPORT_DIR}")
    for p in paths:
        print(f"  wrote {p} ({p.stat().st_size:,} bytes)")
