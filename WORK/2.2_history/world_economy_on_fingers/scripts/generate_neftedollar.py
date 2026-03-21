from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from io import StringIO

import matplotlib.pyplot as plt

from common import download_text, save_figure, setup_chart

FRED_BRENT_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU"
YEARS = [1995, 2000, 2005, 2010, 2015, 2020, 2024]
USD = [59.0, 71.0, 66.0, 61.0, 65.0, 59.0, 57.8]
EUR = [0.0, 18.0, 24.5, 26.0, 20.5, 21.0, 19.8]
JPY = [6.8, 6.0, 3.8, 3.7, 4.0, 6.0, 5.8]
GBP = [2.1, 2.7, 3.5, 4.0, 4.5, 4.5, 4.7]
CNY = [0.0, 0.0, 0.0, 0.0, 1.1, 2.3, 2.2]
OTHER = [100 - (a + b + c + d + e) for a, b, c, d, e in zip(USD, EUR, JPY, GBP, CNY)]
REGIONS = ["Европа", "Азия", "Северная Америка", "Латинская Америка", "Африка / Ближний Восток"]
USD_INVOICING = [74, 79, 76, 83, 86]
EUR_INVOICING = [22, 10, 9, 7, 6]
OTHER_INVOICING = [4, 11, 15, 10, 8]


def load_brent_daily() -> list[tuple[datetime, float]]:
    rows = csv.DictReader(StringIO(download_text(FRED_BRENT_URL, "fred_brent_daily.csv")))
    data: list[tuple[datetime, float]] = []
    for row in rows:
        value = row["DCOILBRENTEU"]
        if value == ".":
            continue
        data.append((datetime.strptime(row["DATE"], "%Y-%m-%d"), float(value)))
    return data


def build_brent_yearly() -> None:
    yearly = defaultdict(list)
    for dt, value in load_brent_daily():
        yearly[dt.year].append(value)
    years = sorted(y for y in yearly if 1987 <= y <= 2025)
    values = [sum(yearly[y]) / len(yearly[y]) for y in years]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, values, color="#8c2d04", linewidth=2.3)
    setup_chart(ax, "Brent: среднегодовая цена, 1987–2025", "долларов за баррель")
    save_figure(fig, "neftedollar_brent_1987_2025.png")


def build_reserves_chart() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.stackplot(
        YEARS,
        USD,
        EUR,
        JPY,
        GBP,
        CNY,
        OTHER,
        labels=["USD", "EUR", "JPY", "GBP", "CNY", "Other"],
        colors=["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#bab0ac"],
    )
    ax.legend(loc="upper right", ncol=3, fontsize=8)
    setup_chart(ax, "Доли валют в мировых официальных резервах, 1995–2024", "%")
    save_figure(fig, "neftedollar_reserves_1995_2024.png")


def build_invoicing_chart() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(REGIONS, USD_INVOICING, label="USD", color="#4c78a8")
    ax.bar(REGIONS, EUR_INVOICING, bottom=USD_INVOICING, label="EUR", color="#f58518")
    stacked = [u + e for u, e in zip(USD_INVOICING, EUR_INVOICING)]
    ax.bar(REGIONS, OTHER_INVOICING, bottom=stacked, label="Other", color="#bab0ac")
    ax.legend()
    setup_chart(ax, "В какой валюте выставляют экспортные счета по регионам", "%")
    save_figure(fig, "neftedollar_export_invoicing_regions.png")


def main() -> None:
    build_brent_yearly()
    build_reserves_chart()
    build_invoicing_chart()


if __name__ == "__main__":
    main()
