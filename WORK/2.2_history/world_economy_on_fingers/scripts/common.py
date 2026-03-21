from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import requests
from matplotlib.patches import Polygon

ROOT = Path(__file__).resolve().parents[4]
WORK_DIR = ROOT / "WORK/2.2_history/world_economy_on_fingers"
WEB_IMAGES_DIR = ROOT / "WEB/2.2_history/world_economy_on_fingers/images"
MAPS_DIR = WORK_DIR / "assets/maps"
CACHE_DIR = WORK_DIR / "assets/cache"
WORLD_COUNTRIES_URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"


def ensure_dirs() -> None:
    WEB_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def save_figure(fig, filename: str) -> None:
    ensure_dirs()
    fig.tight_layout()
    fig.savefig(WEB_IMAGES_DIR / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def setup_chart(ax, title: str, ylabel: str = "") -> None:
    ax.set_title(title, fontsize=14, fontweight="bold")
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def download_text(url: str, cache_name: str) -> str:
    ensure_dirs()
    path = CACHE_DIR / cache_name
    if not path.exists():
        response = requests.get(url, timeout=90)
        response.raise_for_status()
        path.write_text(response.text, encoding="utf-8")
    return path.read_text(encoding="utf-8")


def download_json(url: str, cache_name: str) -> dict:
    return json.loads(download_text(url, cache_name))


def load_local_geojson(filename: str) -> dict:
    return json.loads((MAPS_DIR / filename).read_text(encoding="utf-8"))


def load_world_countries() -> list[dict]:
    data = download_json(WORLD_COUNTRIES_URL, "world_countries.geojson")
    return data["features"]


def feature_name(feature: dict) -> str:
    props = feature.get("properties", {})
    for key in ("ADMIN", "NAME", "name", "name_long"):
        value = props.get(key)
        if value:
            return str(value)
    return ""


def _collect_points(coords, out: list[tuple[float, float]]) -> None:
    if not coords:
        return
    if isinstance(coords[0], (int, float)):
        out.append((float(coords[0]), float(coords[1])))
        return
    for item in coords:
        _collect_points(item, out)


def geometry_points(geometry: dict) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    _collect_points(geometry.get("coordinates", []), points)
    return points


def geometry_in_bbox(geometry: dict, xlim: tuple[float, float], ylim: tuple[float, float]) -> bool:
    for lon, lat in geometry_points(geometry):
        if xlim[0] <= lon <= xlim[1] and ylim[0] <= lat <= ylim[1]:
            return True
    return False


def draw_world_background(ax, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    for feature in load_world_countries():
        geometry = feature.get("geometry", {})
        if not geometry_in_bbox(geometry, xlim, ylim):
            continue
        draw_geometry(
            ax,
            geometry,
            facecolor="#eef1f4",
            edgecolor="#c8cdd3",
            linewidth=0.6,
            alpha=1.0,
        )


def draw_geometry(ax, geometry: dict, facecolor: str | None = None, edgecolor: str = "#333333", linewidth: float = 1.0, alpha: float = 1.0) -> None:
    gtype = geometry.get("type")
    coords = geometry.get("coordinates", [])

    if gtype == "Polygon":
        rings = coords[:1]
        for ring in rings:
            patch = Polygon(ring, closed=True, facecolor=facecolor or "none", edgecolor=edgecolor, linewidth=linewidth, alpha=alpha)
            ax.add_patch(patch)
    elif gtype == "MultiPolygon":
        for polygon in coords:
            for ring in polygon[:1]:
                patch = Polygon(ring, closed=True, facecolor=facecolor or "none", edgecolor=edgecolor, linewidth=linewidth, alpha=alpha)
                ax.add_patch(patch)
    elif gtype == "LineString":
        xs = [pt[0] for pt in coords]
        ys = [pt[1] for pt in coords]
        ax.plot(xs, ys, color=edgecolor, linewidth=linewidth, alpha=alpha)
    elif gtype == "MultiLineString":
        for line in coords:
            xs = [pt[0] for pt in line]
            ys = [pt[1] for pt in line]
            ax.plot(xs, ys, color=edgecolor, linewidth=linewidth, alpha=alpha)
    elif gtype == "Point":
        ax.scatter([coords[0]], [coords[1]], color=edgecolor, s=20, alpha=alpha, zorder=5)
    elif gtype == "MultiPoint":
        xs = [pt[0] for pt in coords]
        ys = [pt[1] for pt in coords]
        ax.scatter(xs, ys, color=edgecolor, s=20, alpha=alpha, zorder=5)


def draw_feature_collection(ax, data: dict, annotate_points: bool = False) -> None:
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        fill = props.get("fill")
        fill_alpha = float(props.get("fill-opacity", 0.35))
        stroke = props.get("stroke", props.get("marker-color", "#b22222"))
        stroke_alpha = float(props.get("stroke-opacity", 0.9))
        stroke_width = float(props.get("stroke-width", 2))
        draw_geometry(
            ax,
            geometry,
            facecolor=fill,
            edgecolor=stroke,
            linewidth=stroke_width,
            alpha=fill_alpha if fill else stroke_alpha,
        )
        if annotate_points and geometry.get("type") == "Point" and props.get("title"):
            lon, lat = geometry["coordinates"]
            ax.text(lon + 0.5, lat + 0.3, props["title"], fontsize=7, color=stroke)


def finalize_map(ax, title: str, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor("#f8fbff")
    ax.grid(alpha=0.15)
    ax.set_xlabel("Долгота")
    ax.set_ylabel("Широта")
