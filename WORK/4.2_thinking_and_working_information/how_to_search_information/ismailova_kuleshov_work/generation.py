import os
import sys
import json
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

import requests
from SPARQLWrapper import SPARQLWrapper, JSON

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "key")
MODEL_NAME = "stepfun/step-3.5-flash:free"
AUTHOR_NAME = os.environ.get("AUTHOR_NAME", "name")
AUTHOR_GITHUB = os.environ.get("AUTHOR_GITHUB", "login")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORK_DIR = BASE_DIR / "WORK"
ARTICLES_DIR = BASE_DIR / "WEB" / "4_2_thinking_and_information" / "psychology_and_tricks"
WORK_DIR.mkdir(exist_ok=True)
ARTICLES_DIR.mkdir(exist_ok=True)

CONCEPTS_LIST_FILE = Path(__file__).parent / "concepts_list.json"
PROMPT_TEMPLATE_FILE = Path(__file__).parent / "prompt_template.txt"
LOG_FILE = Path(__file__).parent / "generation.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_concepts_list(file_path: Path) -> List[tuple]:
    if not file_path.exists():
        logger.error(f"Файл не найден: {file_path}")
        sys.exit(1)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    concepts = []
    for item in data:
        if "name" in item and "wikidata_ids" in item:
            concepts.append((item["name"], item["wikidata_ids"]))
        else:
            logger.warning(f"Пропущен элемент без name или wikidata_ids: {item}")
    
    logger.info(f"Загружено {len(concepts)} понятий из {file_path}")
    return concepts


def query_wikidata(sparql_query: str) -> Optional[List[Dict]]:
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    try:
        return sparql.query().convert()["results"]["bindings"]
    except Exception as e:
        logger.error(f"Ошибка SPARQL: {e}")
        return None


def get_wikidata_facts(entity_ids: List[str]) -> Dict[str, Any]:
    facts = {"description": "", "related_concepts": [], "properties": []}
    for entity_id in entity_ids:
        if not entity_id.startswith('Q'):
            continue
        query = f"""
        SELECT DISTINCT ?property ?propertyLabel ?value ?valueLabel WHERE {{
          wd:{entity_id} ?prop ?value .
          ?property wikibase:directClaim ?prop .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru". }}
        }}
        LIMIT 50
        """
        results = query_wikidata(query)
        
        if results:
            for row in results:
                prop = row.get("propertyLabel", {}).get("value", "")
                val = row.get("valueLabel", {}).get("value", "")
                val_id = row.get("value", {}).get("value", "").replace("http://www.wikidata.org/entity/", "")                
                if prop == "описание" and not facts["description"]:
                    facts["description"] = val
                elif prop in ["экземпляр", "подкласс от"] and val_id.startswith("Q"):
                    if not any(c["id"] == val_id for c in facts["related_concepts"]):
                        facts["related_concepts"].append({"id": val_id, "label": val})
                else:
                    if not any(p["property"] == prop and p["value"] == val for p in facts["properties"]):
                        facts["properties"].append({
                            "property": prop, 
                            "value": val, 
                            "value_id": val_id if val_id.startswith("Q") else None
                        })
        if not facts["description"]:
            desc_query = f"""
            SELECT ?description WHERE {{
              wd:{entity_id} schema:description ?description.
              FILTER(LANG(?description) = "ru")
            }}
            """
            desc_results = query_wikidata(desc_query)
            if desc_results and desc_results[0].get("description", {}).get("value", ""):
                facts["description"] = desc_results[0].get("description", {}).get("value", "")
                break 
    
    return facts


def call_openrouter(prompt: str, max_tokens: int = 4000) -> Optional[str]:
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "key":
        logger.error("Нет API-ключа")
        return None
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Ты пишешь статьи для подротстковой энциклопедии."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        },
        timeout=120
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        logger.error(f"Ошибка API: {response.status_code}")
        return None


def build_prompt(concept_name: str, facts: Dict[str, Any]) -> str:
    with open(PROMPT_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    description = facts.get("description", "Нет описания")
    related = ", ".join([c["label"] for c in facts.get("related_concepts", []) if c.get("label")]) or "нет"
    props = "; ".join([f"{p['property']}: {p['value']}" for p in facts.get("properties", [])[:5] if p.get("property")]) or "нет"

    return template.format(
        concept_name=concept_name,
        description=description,
        related_concepts=related,
        properties=props
    )


def save_article(concept_name: str, text: str):
    filename = f"{concept_name.replace(' ', '_')}.md"
    content = f"""# {concept_name}

{text}

---
Авторы: {AUTHOR_NAME}
GitHub: @{AUTHOR_GITHUB}
*Использованы: OpenRouter ({MODEL_NAME}), Wikidata*
"""
    path = ARTICLES_DIR / filename
    path.write_text(content, encoding="utf-8")
    logger.info(f"Сохранено: {path}")

# def save_related_concepts(concept_name: str, related_concepts: List[Dict]):
#     filename = f"{concept_name.replace(' ', '_')}_related.json"
#     file_path = Path(__file__).parent / filename
#     data = {
#         "concept_name": concept_name,
#         "related_concepts": related_concepts,
#         "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")  
#     }
    
#     if file_path.exists():
#         logger.warning(f"Файл {filename} уже существует. Проверяю содержимое...")
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 existing_data = json.load(f)
#             if existing_data.get("related_concepts") == related_concepts:
#                 logger.info(f"Данные в {filename} совпадают с новыми. Пропускаю сохранение.")
#                 return
#             else:
#                 logger.info(f"Данные отличаются. Создаю резервную копию...")
#                 backup_path = ARTICLES_DIR / f"{filename}.backup_{int(time.time())}"
#                 file_path.rename(backup_path)
#                 logger.info(f"Старый файл сохранён как {backup_path.name}")
#         except Exception as e:
#             logger.warning(f"Не удалось прочитать существующий файл: {e}. Будет создан новый.")

#     try:
#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, ensure_ascii=False, indent=2)
#         logger.info(f"Связанные понятия сохранены: {file_path}")
#     except Exception as e:
#         logger.error(f" Ошибка при сохранении {filename}: {e}")

def main():
    logger.info("=" * 50)
    logger.info("Генерация статей")
    
    concepts = load_concepts_list(CONCEPTS_LIST_FILE)
    for name, qid in concepts:
        logger.info(f"Обработка: {name} ({qid})")
        
        facts = get_wikidata_facts(qid)
        prompt = build_prompt(name, facts)
        text = call_openrouter(prompt)
        
        if text:
            save_article(name, text)
            # if facts.get("related_concepts"):
            #     save_related_concepts(name, facts["related_concepts"])
        time.sleep(2)

    
    logger.info("Готово!")

if __name__ == "__main__":
    main()