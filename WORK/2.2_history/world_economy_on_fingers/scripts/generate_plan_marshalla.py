from __future__ import annotations

import matplotlib.pyplot as plt

from common import draw_geometry, feature_name, finalize_map, load_world_countries, save_figure, setup_chart

RECIPIENTS = {
    "United Kingdom",
    "France",
    "Italy",
    "Germany",
    "Netherlands",
    "Belgium",
    "Luxembourg",
    "Austria",
    "Denmark",
    "Norway",
    "Sweden",
    "Switzerland",
    "Greece",
    "Turkey",
    "Ireland",
    "Portugal",
    "Iceland",
}
EASTERN_EUROPE = {
    "Poland",
    "Czechia",
    "Slovakia",
    "Hungary",
    "Romania",
    "Bulgaria",
    "Belarus",
    "Ukraine",
    "Russia",
    "Lithuania",
    "Latvia",
    "Estonia",
    "Moldova",
}
TOP_COUNTRIES = ["Великобритания", "Франция", "Италия", "Западная Германия", "Нидерланды"]
TOP_AID = [3189.8, 2713.6, 1508.8, 1390.6, 1083.5]
AID_CATEGORIES = ["Продовольствие", "Топливо", "Сырьё", "Оборудование", "Прочее"]
AID_SHARES = [28, 18, 32, 17, 5]
RECOVERY_LABELS = ["Промышленность", "Сельское хозяйство", "Средний ВНП"]
RECOVERY_VALUES = [55, 37, 33]


def build_map() -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    xlim = (-12, 35)
    ylim = (35, 65)
    for feature in load_world_countries():
        geometry = feature.get("geometry", {})
        name = feature_name(feature)
        facecolor = "#eef1f4"
        edgecolor = "#c8cdd3"
        if name in RECIPIENTS:
            facecolor = "#9ecae1"
            edgecolor = "#3182bd"
        elif name == "Spain":
            facecolor = "#fdd49e"
            edgecolor = "#d95f0e"
        elif name in EASTERN_EUROPE:
            facecolor = "#d9d9d9"
            edgecolor = "#969696"
        draw_geometry(ax, geometry, facecolor=facecolor, edgecolor=edgecolor, linewidth=0.6, alpha=1.0)
    finalize_map(ax, "План Маршалла: страны-получатели помощи", xlim, ylim)
    save_figure(fig, "plan_marshalla_map.png")


def build_aid_structure() -> None:
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(AID_SHARES, labels=AID_CATEGORIES, autopct="%1.0f%%", startangle=90)
    ax.set_title("Структура помощи ERP", fontsize=14, fontweight="bold")
    save_figure(fig, "plan_marshalla_aid_structure.png")


def build_top_recipients() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(TOP_COUNTRIES, TOP_AID, color="#3182bd")
    setup_chart(ax, "Крупнейшие получатели помощи по плану Маршалла", "млн долларов")
    save_figure(fig, "plan_marshalla_aid_by_country.png")


def build_recovery_growth() -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(RECOVERY_LABELS, RECOVERY_VALUES, color=["#31a354", "#74c476", "#a1d99b"])
    setup_chart(ax, "Как росло производство в странах-участницах", "% к 1947 году")
    save_figure(fig, "plan_marshalla_recovery_growth.png")


def main() -> None:
    build_map()
    build_aid_structure()
    build_top_recipients()
    build_recovery_growth()


if __name__ == "__main__":
    main()
