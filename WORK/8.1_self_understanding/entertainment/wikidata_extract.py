"""
Скрипт для извлечения данных из WikiData через SPARQL-запросы.
Для каждого понятия из concepts.json получает:
- метку и описание (ru/en)
- подклассы
- связанные сущности
Результаты сохраняются в директорию wikidata/ в формате JSON.
"""

import json
import os
import time
import requests

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
WIKIDATA_DIR = os.path.join(os.path.dirname(__file__), "wikidata")
CONCEPTS_PATH = os.path.join(os.path.dirname(__file__), "concepts.json")


def sparql_query(query: str) -> list[dict]:
    """Выполняет SPARQL-запрос к WikiData и возвращает список результатов."""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "KidBook-Encyclopedia/1.0 (student project)",
    }
    resp = requests.get(
        SPARQL_ENDPOINT,
        params={"query": query},
        headers=headers,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", {}).get("bindings", [])


def get_entity_info(qid: str) -> dict:
    """Получает основную информацию о сущности по QID."""
    query = f"""
    SELECT ?itemLabel ?itemDescription ?itemAltLabel WHERE {{
      BIND(wd:{qid} AS ?item)
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "ru,en".
      }}
    }}
    """
    results = sparql_query(query)
    if results:
        r = results[0]
        return {
            "label": r.get("itemLabel", {}).get("value", ""),
            "description": r.get("itemDescription", {}).get("value", ""),
            "aliases": r.get("itemAltLabel", {}).get("value", ""),
        }
    return {}


def get_subclasses(qid: str, limit: int = 15) -> list[dict]:
    """Получает подклассы сущности (P279 — subclass of)."""
    query = f"""
    SELECT ?item ?itemLabel ?itemDescription WHERE {{
      ?item wdt:P279 wd:{qid} .
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "ru,en".
      }}
    }}
    LIMIT {limit}
    """
    results = sparql_query(query)
    return [
        {
            "qid": r["item"]["value"].split("/")[-1],
            "label": r.get("itemLabel", {}).get("value", ""),
            "description": r.get("itemDescription", {}).get("value", ""),
        }
        for r in results
    ]


def get_instances(qid: str, limit: int = 10) -> list[dict]:
    """Получает экземпляры сущности (P31 — instance of)."""
    query = f"""
    SELECT ?item ?itemLabel ?itemDescription WHERE {{
      ?item wdt:P31 wd:{qid} .
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "ru,en".
      }}
    }}
    LIMIT {limit}
    """
    results = sparql_query(query)
    return [
        {
            "qid": r["item"]["value"].split("/")[-1],
            "label": r.get("itemLabel", {}).get("value", ""),
            "description": r.get("itemDescription", {}).get("value", ""),
        }
        for r in results
    ]


def get_related_properties(qid: str) -> dict:
    """Получает ключевые свойства сущности (жанр, страна, дата и т.д.)."""
    query = f"""
    SELECT ?prop ?propLabel ?val ?valLabel WHERE {{
      wd:{qid} ?propDirect ?val .
      ?property wikibase:directClaim ?propDirect .
      ?property rdfs:label ?propLabel .
      FILTER(LANG(?propLabel) = "ru" || LANG(?propLabel) = "en")
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "ru,en".
      }}
    }}
    LIMIT 30
    """
    results = sparql_query(query)
    props = {}
    for r in results:
        prop_name = r.get("propLabel", {}).get("value", "")
        val_label = r.get("valLabel", {}).get("value", "")
        if prop_name and val_label:
            props.setdefault(prop_name, []).append(val_label)
    return props


def extract_for_concept(concept: dict) -> dict:
    """Извлекает все данные WikiData для одного понятия."""
    qid = concept["wikidata_id"]
    print(f"  Извлекаю данные для {concept['title']} ({qid})...")

    info = get_entity_info(qid)
    time.sleep(1)

    subclasses = get_subclasses(qid)
    time.sleep(1)

    instances = get_instances(qid)
    time.sleep(1)

    properties = get_related_properties(qid)
    time.sleep(1)

    return {
        "concept_id": concept["id"],
        "title": concept["title"],
        "wikidata_id": qid,
        "wikidata_url": f"https://www.wikidata.org/wiki/{qid}",
        "info": info,
        "subclasses": subclasses,
        "instances": instances,
        "properties": properties,
    }


def format_context_for_prompt(wd_data: dict) -> str:
    """Форматирует данные WikiData в текстовую строку для промпта LLM."""
    parts = []

    info = wd_data.get("info", {})
    if info.get("description"):
        parts.append(f"Описание: {info['description']}")
    if info.get("aliases"):
        parts.append(f"Также известно как: {info['aliases']}")

    subclasses = wd_data.get("subclasses", [])
    if subclasses:
        labels = [s["label"] for s in subclasses[:8] if s.get("label")]
        if labels:
            parts.append(f"Разновидности: {', '.join(labels)}")

    instances = wd_data.get("instances", [])
    if instances:
        labels = [i["label"] for i in instances[:8] if i.get("label")]
        if labels:
            parts.append(f"Примеры: {', '.join(labels)}")

    props = wd_data.get("properties", {})
    for prop_name, values in list(props.items())[:5]:
        parts.append(f"{prop_name}: {', '.join(values[:5])}")

    return "; ".join(parts) if parts else ""


def main():
    os.makedirs(WIKIDATA_DIR, exist_ok=True)

    with open(CONCEPTS_PATH, "r", encoding="utf-8") as f:
        concepts = json.load(f)

    print(f"Загружено {len(concepts)} понятий из concepts.json\n")

    all_data = {}

    for concept in concepts:
        try:
            wd_data = extract_for_concept(concept)
            all_data[concept["id"]] = wd_data

            # Сохраняем отдельный файл для каждого понятия
            filepath = os.path.join(WIKIDATA_DIR, f"{concept['id']}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(wd_data, f, ensure_ascii=False, indent=2)
            print(f"  ✓ Сохранено: {filepath}\n")

        except Exception as e:
            print(f"  ✗ Ошибка для {concept['title']}: {e}\n")

    # Сохраняем общий файл со всеми данными
    summary_path = os.path.join(WIKIDATA_DIR, "_all_data.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\nВсе данные сохранены в {summary_path}")

    # Генерируем файл с контекстами для промптов
    contexts = {}
    for cid, data in all_data.items():
        contexts[cid] = format_context_for_prompt(data)
    ctx_path = os.path.join(WIKIDATA_DIR, "_contexts.json")
    with open(ctx_path, "w", encoding="utf-8") as f:
        json.dump(contexts, f, ensure_ascii=False, indent=2)
    print(f"Контексты для промптов сохранены в {ctx_path}")


if __name__ == "__main__":
    main()
