"""
Chart render — Plotly pie charts exported as SVG via Kaleido.

Reads plain country/population rows (from the DB) and returns SVG strings.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock
from typing import Mapping, Sequence

import plotly.express as px
import plotly.graph_objects as go

# Matches the Streamlit dashboard palette.
_COLORS = px.colors.qualitative.Pastel

# Kaleido spawns a browser; serialize exports to avoid subprocess races.
_SVG_LOCK = Lock()
_SVG_MAX_ATTEMPTS = 3

PIE_SHARE = "share"
PIE_TOP5 = "top5"
PIE_TOP5_VS_REST = "top5-vs-rest"

PIE_CHART_IDS: tuple[str, ...] = (PIE_SHARE, PIE_TOP5, PIE_TOP5_VS_REST)

_PIE_TITLES: Mapping[str, str] = {
    PIE_SHARE: "Population Share",
    PIE_TOP5: "Top 5 Population Share",
    PIE_TOP5_VS_REST: "Top 5 vs Rest",
}


@dataclass(frozen=True, slots=True)
class PopSlice:
    country: str
    population: int


@dataclass(frozen=True, slots=True)
class PieChartSvg:
    """One rendered pie chart as SVG."""

    id: str
    title: str
    svg: str


class UnknownPieChart(ValueError):
    """chart_id is not one of the supported pie variants."""


def pie_title(chart_id: str) -> str:
    if chart_id not in _PIE_TITLES:
        raise UnknownPieChart(
            f"Unknown pie chart id {chart_id!r}; expected one of {list(PIE_CHART_IDS)}"
        )
    return _PIE_TITLES[chart_id]


def rows_to_slices(rows: Sequence[dict]) -> list[PopSlice]:
    """
    Map DB/API-style rows to slices ordered by population DESC, country ASC.
    Each row needs keys: country, population.
    """
    cleaned: list[PopSlice] = []
    for r in rows:
        country = str(r["country"]).strip()
        population = int(r["population"])
        if not country or population < 0:
            continue
        cleaned.append(PopSlice(country=country, population=population))
    cleaned.sort(key=lambda s: (-s.population, s.country))
    return cleaned


def _slices_for_pie(chart_id: str, slices: Sequence[PopSlice]) -> list[PopSlice]:
    if chart_id == PIE_SHARE:
        return list(slices)

    if chart_id == PIE_TOP5:
        return list(slices[:5])

    if chart_id == PIE_TOP5_VS_REST:
        if not slices:
            return []
        top = list(slices[:5])
        rest_pop = sum(s.population for s in slices[5:])
        if rest_pop > 0:
            top.append(PopSlice(country="Other", population=rest_pop))
        return top

    raise UnknownPieChart(
        f"Unknown pie chart id {chart_id!r}; expected one of {list(PIE_CHART_IDS)}"
    )


def build_pie_figure(chart_id: str, slices: Sequence[PopSlice]) -> go.Figure:
    """Build a Plotly pie figure for the given chart id and slice series."""
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
            names=[s.country for s in series],
            values=[s.population for s in series],
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


def figure_to_svg(fig: go.Figure) -> str:
    """Render a Plotly figure to an SVG document string via Kaleido."""
    last_err: Exception | None = None
    with _SVG_LOCK:
        for attempt in range(_SVG_MAX_ATTEMPTS):
            try:
                raw = fig.to_image(format="svg")
                if isinstance(raw, bytes):
                    return raw.decode("utf-8")
                return str(raw)
            except RuntimeError as exc:
                last_err = exc
                if attempt + 1 < _SVG_MAX_ATTEMPTS:
                    time.sleep(0.15 * (attempt + 1))
                    continue
                raise
    assert last_err is not None  # pragma: no cover
    raise last_err


def render_pie_svg(chart_id: str, rows: Sequence[dict]) -> PieChartSvg:
    """Render one named pie chart from DB rows."""
    slices = rows_to_slices(rows)
    fig = build_pie_figure(chart_id, slices)
    return PieChartSvg(id=chart_id, title=pie_title(chart_id), svg=figure_to_svg(fig))


def render_all_pie_svgs(rows: Sequence[dict]) -> tuple[PieChartSvg, ...]:
    """Render all supported pie charts from DB rows."""
    return tuple(render_pie_svg(chart_id, rows) for chart_id in PIE_CHART_IDS)
