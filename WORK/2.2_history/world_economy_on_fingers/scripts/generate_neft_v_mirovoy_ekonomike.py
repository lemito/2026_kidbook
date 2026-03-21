from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from io import StringIO

import matplotlib.pyplot as plt

from common import download_text, draw_feature_collection, draw_world_background, finalize_map, load_local_geojson, save_figure, setup_chart

FRED_BRENT_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU"
CHOKEPOINTS = ["Малакка", "Ормуз", "Суэц+SUMED", "Баб-эль-Мандеб", "Дарданеллы", "Босфор", "Панама"]
CHOKEPOINTS_1H25 = [23.2, 20.9, 4.9, 4.2, 3.7, 3.3, 2.3]
CHOKEPOINTS_2020 = [23.7, 18.5, 7.0, 6.2, 2.9, 2.8, 1.8]
PRODUCERS = ["США", "Россия", "Саудовская Аравия", "Канада", "Иран", "Ирак", "Китай", "Бразилия", "ОАЭ", "Кувейт"]
PRODUCER_SHARES = [18.9, 11.6, 11.2, 6.4, 5.2, 4.8, 4.7, 4.0, 4.0, 2.9]


def load_brent_daily() -> list[tuple[datetime, float]]:
    rows = csv.DictReader(StringIO(download_text(FRED_BRENT_URL, "fred_brent_daily.csv")))
    data: list[tuple[datetime, float]] = []
    for row in rows:
        value = row["DCOILBRENTEU"]
        if value == ".":
            continue
        data.append((datetime.strptime(row["DATE"], "%Y-%m-%d"), float(value)))
    return data


def build_yearly_brent() -> None:
    yearly = defaultdict(list)
    for dt, value in load_brent_daily():
        yearly[dt.year].append(value)
    years = sorted(y for y in yearly if 1987 <= y <= 2025)
    values = [sum(yearly[y]) / len(yearly[y]) for y in years]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, values, color="#8c2d04", linewidth=2.3)
    setup_chart(ax, "Brent: средняя годовая цена нефти", "долларов за баррель")
    save_figure(fig, "neft_brent_1987_2025.png")


def build_quarterly_brent() -> None:
    quarterly = defaultdict(list)
    for dt, value in load_brent_daily():
        if dt.year not in (2024, 2025):
            continue
        quarter = (dt.month - 1) // 3 + 1
        quarterly[(dt.year, quarter)].append(value)
    labels = []
    values = []
    for key in sorted(quarterly):
        labels.append(f"{key[0]} Q{key[1]}")
        values.append(sum(quarterly[key]) / len(quarterly[key]))

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(labels, values, color="#d94801")
    setup_chart(ax, "Brent: квартальная средняя цена", "долларов за баррель")
    save_figure(fig, "neft_brent_quarters_2024_2025.png")


def build_map() -> None:
    fig, ax = plt.subplots(figsize=(12, 6.5))
    xlim = (-180, 180)
    ylim = (-60, 85)
    draw_world_background(ax, xlim, ylim)
    draw_feature_collection(ax, load_local_geojson("neft_v_mirovoy_ekonomike_map.geojson"), annotate_points=True)
    finalize_map(ax, "Нефть в мировой экономике: маршруты и трубопроводы", xlim, ylim)
    save_figure(fig, "neft_v_mirovoy_ekonomike_map.png")


def build_chokepoints_current() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh(CHOKEPOINTS, CHOKEPOINTS_1H25, color="#3182bd")
    setup_chart(ax, "Сколько нефти проходит через ключевые узкие места, 1H25 / FY2025", "млн баррелей в день")
    save_figure(fig, "neft_chokepoints_1h25.png")


def build_chokepoints_trends() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    xs = range(len(CHOKEPOINTS))
    width = 0.38
    ax.bar([x - width / 2 for x in xs], CHOKEPOINTS_2020, width=width, label="2020", color="#9ecae1")
    ax.bar([x + width / 2 for x in xs], CHOKEPOINTS_1H25, width=width, label="1H25", color="#08519c")
    ax.set_xticks(list(xs), CHOKEPOINTS, rotation=20)
    ax.legend()
    setup_chart(ax, "Главные нефтяные узкие места: 2020 и 1H25", "млн баррелей в день")
    save_figure(fig, "neft_chokepoints_trends_2020_1h25.png")


def build_producers() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh(PRODUCERS, PRODUCER_SHARES, color="#31a354")
    setup_chart(ax, "Крупнейшие производители нефти в 2024 году", "% мировой добычи")
    save_figure(fig, "neft_top_producers_2024.png")


def main() -> None:
    build_map()
    build_yearly_brent()
    build_quarterly_brent()
    build_chokepoints_trends()
    build_chokepoints_current()
    build_producers()


if __name__ == "__main__":
    main()
