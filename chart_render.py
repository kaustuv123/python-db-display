"""Plotly pie charts → SVG/PNG via Kaleido."""

from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock
from typing import Sequence

import plotly.express as px
import plotly.graph_objects as go

_COLORS = px.colors.qualitative.Pastel
_LOCK = Lock()
_MAX_ATTEMPTS = 3

PNG_WIDTH = 600
PNG_HEIGHT = 400

PIE_CHART_IDS: tuple[str, ...] = ("share", "top5", "top5-vs-rest")

_PIE_TITLES = {
    "share": "Container Share by Terminal",
    "top5": "Top 5 Terminal Container Share",
    "top5-vs-rest": "Top 5 Terminals vs Rest",
}


@dataclass(frozen=True, slots=True)
class Slice:
    port_terminal: str
    containers: int


@dataclass(frozen=True, slots=True)
class PieChartSvg:
    id: str
    title: str
    svg: str


@dataclass(frozen=True, slots=True)
class PieChartPng:
    id: str
    title: str
    png: bytes


class UnknownPieChart(ValueError):
    pass


def pie_title(chart_id: str) -> str:
    try:
        return _PIE_TITLES[chart_id]
    except KeyError as exc:
        raise UnknownPieChart(
            f"Unknown pie chart id {chart_id!r}; expected one of {list(PIE_CHART_IDS)}"
        ) from exc


def rows_to_slices(rows: Sequence[dict]) -> list[Slice]:
    """Map rows (port_terminal, containers) → sorted slices."""
    cleaned = [
        Slice(str(r["port_terminal"]).strip(), int(r["containers"]))
        for r in rows
        if str(r.get("port_terminal", "")).strip() and int(r["containers"]) >= 0
    ]
    cleaned.sort(key=lambda s: (-s.containers, s.port_terminal))
    return cleaned


def _slices_for_pie(chart_id: str, slices: Sequence[Slice]) -> list[Slice]:
    if chart_id == "share":
        return list(slices)
    if chart_id == "top5":
        return list(slices[:5])
    if chart_id == "top5-vs-rest":
        if not slices:
            return []
        top = list(slices[:5])
        rest = sum(s.containers for s in slices[5:])
        if rest > 0:
            top.append(Slice("Other", rest))
        return top
    raise UnknownPieChart(chart_id)


def _build_figure(chart_id: str, slices: Sequence[Slice]) -> go.Figure:
    title = pie_title(chart_id)
    series = _slices_for_pie(chart_id, slices)

    if not series:
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["No data"],
                    values=[1],
                    hole=0.4,
                    textinfo="label",
                    marker=dict(colors=["#e5e7eb"]),
                )
            ]
        )
    else:
        fig = px.pie(
            names=[s.port_terminal for s in series],
            values=[s.containers for s in series],
            color_discrete_sequence=_COLORS,
            hole=0.4,
            title=title,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif"),
        margin=dict(t=48, b=16, l=16, r=16),
        legend=dict(font=dict(size=10)),
        title=dict(text=title, x=0.5, xanchor="center"),
    )
    return fig


def _to_image(fig: go.Figure, **kwargs) -> bytes:
    """Kaleido export with retries (browser subprocess can flake)."""
    with _LOCK:
        for attempt in range(_MAX_ATTEMPTS):
            try:
                raw = fig.to_image(**kwargs)
                return raw if isinstance(raw, bytes) else bytes(raw)
            except RuntimeError:
                if attempt + 1 >= _MAX_ATTEMPTS:
                    raise
                time.sleep(0.15 * (attempt + 1))
    raise RuntimeError("image export failed")  # pragma: no cover


def render_pie_svg(chart_id: str, rows: Sequence[dict]) -> PieChartSvg:
    fig = _build_figure(chart_id, rows_to_slices(rows))
    svg = _to_image(fig, format="svg").decode("utf-8")
    return PieChartSvg(chart_id, pie_title(chart_id), svg)


def render_all_pie_svgs(rows: Sequence[dict]) -> tuple[PieChartSvg, ...]:
    return tuple(render_pie_svg(cid, rows) for cid in PIE_CHART_IDS)


def render_pie_png(
    chart_id: str,
    rows: Sequence[dict],
    *,
    width: int = PNG_WIDTH,
    height: int = PNG_HEIGHT,
) -> PieChartPng:
    fig = _build_figure(chart_id, rows_to_slices(rows))
    png = _to_image(fig, format="png", width=width, height=height)
    return PieChartPng(chart_id, pie_title(chart_id), png)


def render_all_pie_pngs(
    rows: Sequence[dict],
    *,
    width: int = PNG_WIDTH,
    height: int = PNG_HEIGHT,
) -> tuple[PieChartPng, ...]:
    return tuple(
        render_pie_png(cid, rows, width=width, height=height) for cid in PIE_CHART_IDS
    )
