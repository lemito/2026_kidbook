from __future__ import annotations

import matplotlib.pyplot as plt

from common import draw_feature_collection, draw_world_background, finalize_map, load_local_geojson, save_figure, setup_chart

TRANSIT_YEARS = [2019, 2020, 2021, 2022, 2023]
TRANSIT_VALUES = [13785, 13369, 13342, 14239, 14080]
ROUTES = ["Восточное побережье США → Япония", "Эквадор → Европа"]
DISTANCE_SAVINGS = [4800, 8000]


def build_map() -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    xlim = (-84.5, -76.0)
    ylim = (7.0, 10.8)
    draw_world_background(ax, xlim, ylim)
    draw_feature_collection(ax, load_local_geojson("panamskiy_kanal_map.geojson"), annotate_points=True)
    finalize_map(ax, "Панамский канал: положение на карте Панамы", xlim, ylim)
    save_figure(fig, "panamskiy_kanal_map.png")


def build_transits() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(TRANSIT_YEARS, TRANSIT_VALUES, marker="o", linewidth=2.3, color="#2b8cbe")
    setup_chart(ax, "Панамский канал: число транзитов, 2019–2023", "транзитов")
    save_figure(fig, "panamskiy_kanal_transits_2019_2023.png")


def build_distance_savings() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(ROUTES, DISTANCE_SAVINGS, color=["#74a9cf", "#045a8d"])
    setup_chart(ax, "Сколько пути может сэкономить Панамский канал", "км")
    save_figure(fig, "panamskiy_kanal_distance_savings_examples.png")


def main() -> None:
    build_map()
    build_transits()
    build_distance_savings()


if __name__ == "__main__":
    main()
