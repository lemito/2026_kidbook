"""
Скрипт для экспорта фрагментов графа знаний из WikiData.
Раздел: 3.1 Здоровый образ жизни → Вредные привычки

Для каждого понятия из concepts.json с непустым wikidata_id:
1. Делает SPARQL-запрос к Wikidata Query Service
2. Получает метки, описание, родительские классы и связанные сущности
3. Сохраняет результат в wikidata/{concept_id}.json

Использование:
  python wikidata_extract.py
"""

import json
import os
import sys
import time

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONCEPTS_PATH = os.path.join(SCRIPT_DIR, "concepts.json")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "wikidata")

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

# Прокси через SOCKS5 (V2rayN). Если не нужен — поставить None
PROXIES = {
    "http": "socks5h://127.0.0.1:10808",
    "https": "socks5h://127.0.0.1:10808",
}

HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "KidBook-Encyclopedia/1.0 (student project)",
}


def load_concepts() -> list[dict]:
    with open(CONCEPTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["concepts"]


def run_sparql(query: str) -> dict | None:
    """Выполнить SPARQL-запрос к WikiData."""
    try:
        resp = requests.get(
            WIKIDATA_SPARQL_ENDPOINT,
            params={"query": query},
            headers=HEADERS,
            proxies=PROXIES,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"SPARQL error: {e}")
        return None


def extract_concept(qid: str) -> dict | None:
    """
    Один SPARQL-запрос для получения меток, описания и связей.
    """
    query = f"""
    SELECT ?labelRu ?labelEn ?descRu ?descEn
           ?prop ?propLabel ?value ?valueLabel
    WHERE {{
      OPTIONAL {{ wd:{qid} rdfs:label ?labelRu . FILTER(LANG(?labelRu) = "ru") }}
      OPTIONAL {{ wd:{qid} rdfs:label ?labelEn . FILTER(LANG(?labelEn) = "en") }}
      OPTIONAL {{ wd:{qid} schema:description ?descRu . FILTER(LANG(?descRu) = "ru") }}
      OPTIONAL {{ wd:{qid} schema:description ?descEn . FILTER(LANG(?descEn) = "en") }}
      OPTIONAL {{
        VALUES ?prop {{
          wdt:P279   # подкласс
          wdt:P31    # экземпляр
          wdt:P361   # часть
          wdt:P1542  # имеет следствие
          wdt:P828   # имеет причину
          wdt:P527   # имеет часть
        }}
        wd:{qid} ?prop ?value .
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en" . }}
    }}
    LIMIT 100
    """

    data = run_sparql(query)
    if not data:
        return None

    bindings = data.get("results", {}).get("bindings", [])
    if not bindings:
        return None

    # Извлекаем метки из первого результата
    first = bindings[0]
    label_ru = first.get("labelRu", {}).get("value", "")
    label_en = first.get("labelEn", {}).get("value", "")
    desc_ru = first.get("descRu", {}).get("value", "")
    desc_en = first.get("descEn", {}).get("value", "")

    # Собираем связи
    prop_map = {
        "http://www.wikidata.org/prop/direct/P279": "subclass_of",
        "http://www.wikidata.org/prop/direct/P31": "instance_of",
        "http://www.wikidata.org/prop/direct/P361": "part_of",
        "http://www.wikidata.org/prop/direct/P1542": "has_effect",
        "http://www.wikidata.org/prop/direct/P828": "has_cause",
        "http://www.wikidata.org/prop/direct/P527": "has_part",
    }

    relations = {}
    for b in bindings:
        prop_uri = b.get("prop", {}).get("value", "")
        val_label = b.get("valueLabel", {}).get("value", "")
        val_uri = b.get("value", {}).get("value", "")

        rel_key = prop_map.get(prop_uri)
        if not rel_key or not val_label:
            continue

        val_qid = val_uri.split("/")[-1] if val_uri else ""
        relations.setdefault(rel_key, [])

        # Дедупликация
        entry = {"qid": val_qid, "label": val_label}
        if entry not in relations[rel_key]:
            relations[rel_key].append(entry)

    return {
        "qid": qid,
        "label_ru": label_ru,
        "label_en": label_en,
        "description_ru": desc_ru,
        "description_en": desc_en,
        "url": f"https://www.wikidata.org/wiki/{qid}",
        "relations": relations,
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    concepts = load_concepts()
    concepts_with_qid = [c for c in concepts if c.get("wikidata_id")]

    print(f"Найдено {len(concepts_with_qid)} понятий с WikiData ID")
    print(f"Результаты: {OUTPUT_DIR}\n")

    success = 0

    for concept in concepts_with_qid:
        qid = concept["wikidata_id"]
        name = concept["name"]
        concept_id = concept["id"].split("/")[-1]

        print(f"  {name} ({qid})...", end=" ", flush=True)

        result = extract_concept(qid)
        if not result:
            print("SKIP")
            continue

        result["concept_name"] = name
        result["concept_file"] = concept["file"]

        out_path = os.path.join(OUTPUT_DIR, f"{concept_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        rel_count = sum(len(v) for v in result["relations"].values())
        print(f"OK ({rel_count} связей)")
        success += 1

        time.sleep(1.5)  # пауза — не перегружаем WikiData

    print(f"\nГотово: {success}/{len(concepts_with_qid)} экспортировано")


if __name__ == "__main__":
    main()
