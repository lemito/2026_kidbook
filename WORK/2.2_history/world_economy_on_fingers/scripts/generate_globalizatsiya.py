from __future__ import annotations

import matplotlib.pyplot as plt

from common import draw_feature_collection, draw_world_background, finalize_map, load_local_geojson, save_figure, setup_chart

TRADE_YEARS = [1970, 1990, 2000, 2010, 2020, 2024]
TRADE_VALUES = [25.8, 38.0, 50.3, 56.4, 52.0, 56.8]
INTERNET_YEARS = [2005, 2015, 2020, 2025]
INTERNET_VALUES = [15.6, 39.9, 60.1, 73.6]
AIR_YEARS = [1970, 1990, 2000, 2019, 2020, 2023]
AIR_VALUES = [0.31, 1.02, 1.67, 4.46, 1.77, 4.27]
CONTAINER_YEARS = [2000, 2010, 2020, 2022]
CONTAINER_VALUES = [224.8, 549.0, 793.6, 839.8]


def build_map() -> None:
    fig, ax = plt.subplots(figsize=(12, 6.5))
    xlim = (-180, 180)
    ylim = (-60, 85)
    draw_world_background(ax, xlim, ylim)
    draw_feature_collection(ax, load_local_geojson("globalizatsiya_map.geojson"), annotate_points=True)
    finalize_map(ax, "Глобализация: маршруты, узкие места и торговые узлы", xlim, ylim)
    save_figure(fig, "globalizatsiya_map.png")


def build_line_chart(years, values, title, ylabel, filename, color) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(years, values, marker="o", linewidth=2.5, color=color)
    setup_chart(ax, title, ylabel)
    save_figure(fig, filename)


def main() -> None:
    build_map()
    build_line_chart(
        TRADE_YEARS,
        TRADE_VALUES,
        "Мировая торговля как доля мирового ВВП",
        "% мирового ВВП",
        "globalizatsiya_trade_world_1970_2024.png",
        "#1f77b4",
    )
    build_line_chart(
        INTERNET_YEARS,
        INTERNET_VALUES,
        "Пользователи интернета в мире",
        "% населения",
        "globalizatsiya_internet_world_2005_2025.png",
        "#2ca02c",
    )
    build_line_chart(
        AIR_YEARS,
        AIR_VALUES,
        "Мировые авиапассажиры",
        "млрд пассажиров",
        "globalizatsiya_air_world_1970_2023.png",
        "#ff7f0e",
    )
    build_line_chart(
        CONTAINER_YEARS,
        CONTAINER_VALUES,
        "Мировой контейнерный портовый трафик",
        "млн TEU",
        "globalizatsiya_container_world_2000_2022.png",
        "#9467bd",
    )


if __name__ == "__main__":
    main()
