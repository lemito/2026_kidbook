from __future__ import annotations

import matplotlib.pyplot as plt

from common import draw_feature_collection, draw_world_background, finalize_map, load_local_geojson, save_figure, setup_chart

COUNTRIES = ["Южная Корея", "Сингапур", "Гонконг", "Тайвань"]
GDP_PC_1960 = [1548, 3464, 5088, 2157]
GDP_PC_2022 = [41321, 80320, 48289, 53143]
GDP_TOTAL_1960 = [38.4, 5.7, 15.4, 23.4]
GDP_TOTAL_2022 = [2137.6, 461.8, 356.7, 1247.9]
GDP_PC_MULTIPLIERS = [26.7, 23.2, 9.5, 24.6]


def build_map() -> None:
    fig, ax = plt.subplots(figsize=(8, 8))
    xlim = (100, 132)
    ylim = (0, 42)
    draw_world_background(ax, xlim, ylim)
    draw_feature_collection(ax, load_local_geojson("aziatskie_tigry_map.geojson"))
    finalize_map(ax, "Азиатские тигры: расположение на карте", xlim, ylim)
    save_figure(fig, "aziatskie_tigry_map.png")


def build_gdppc() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    xs = range(len(COUNTRIES))
    width = 0.38
    ax.bar([x - width / 2 for x in xs], GDP_PC_1960, width=width, label="1960", color="#9ecae1")
    ax.bar([x + width / 2 for x in xs], GDP_PC_2022, width=width, label="2022", color="#3182bd")
    ax.set_xticks(list(xs), COUNTRIES, rotation=12)
    ax.legend()
    setup_chart(ax, "ВВП на душу населения: 1960 и 2022", "международные доллары 2011 года")
    save_figure(fig, "aziatskie_tigry_gdppc_1960_2022.png")


def build_gdppc_index() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    index_values = [round(v * 100, 1) for v in GDP_PC_MULTIPLIERS]
    ax.bar(COUNTRIES, index_values, color="#74c476")
    setup_chart(ax, "Индекс роста ВВП на душу населения (1960 = 100)", "индекс")
    save_figure(fig, "aziatskie_tigry_gdppc_index_1960_2022.png")


def build_total_gdp() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    xs = range(len(COUNTRIES))
    width = 0.38
    ax.bar([x - width / 2 for x in xs], GDP_TOTAL_1960, width=width, label="1960", color="#fdd0a2")
    ax.bar([x + width / 2 for x in xs], GDP_TOTAL_2022, width=width, label="2022", color="#e6550d")
    ax.set_xticks(list(xs), COUNTRIES, rotation=12)
    ax.legend()
    setup_chart(ax, "Общий ВВП: 1960 и 2022", "млрд международных долларов")
    save_figure(fig, "aziatskie_tigry_total_gdp_1960_2022.png")


def build_growth_multipliers() -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(COUNTRIES, GDP_PC_MULTIPLIERS, color="#756bb1")
    setup_chart(ax, "Во сколько раз вырос ВВП на душу населения", "раз")
    save_figure(fig, "aziatskie_tigry_gdppc_growth_multipliers.png")


def main() -> None:
    build_map()
    build_gdppc()
    build_gdppc_index()
    build_total_gdp()
    build_growth_multipliers()


if __name__ == "__main__":
    main()
