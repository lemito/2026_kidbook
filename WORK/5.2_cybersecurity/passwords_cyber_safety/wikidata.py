import json
import re
import requests
from pathlib import Path
from datetime import datetime

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"

def fetch_entity_data(qid: str) -> dict:
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "languages": "ru|en",
        "props": "labels|descriptions",
        "format": "json"
    }
    headers = {"User-Agent": "KidBook/1.0"}
    
    try:
        resp = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        entity = data.get("entities", {}).get(qid, {})
        
        ru_label = entity.get("labels", {}).get("ru", {}).get("value", "Нет названия")
        ru_desc = entity.get("descriptions", {}).get("ru", {}).get("value", "Нет описания")
        en_label = entity.get("labels", {}).get("en", {}).get("value", "")
        
        return {
            "success": True,
            "label_ru": ru_label,
            "desc_ru": ru_desc,
            "label_en": en_label
        }
    except Exception as err:
        return {"success": False, "error": str(err)}

def main():
    print("Инициализация парсера WikiData...")
    
    # Используем pathlib для путей (отличается от os.path в примере)
    base_path = Path(__file__).resolve().parent.parent.parent
    articles_path = base_path / "WEB" / "5.2_cybersecurity" / "passwords_cyber_safety" / "articles"
    output_path = base_path / "WORK" / "5.2_cybersecurity" / "passwords_cyber_safety" / "knowledge_graph.json"
    
    if not articles_path.exists():
        print(f"Директория со статьями не найдена: {articles_path}")
        return

    extracted_nodes = []
    regex_qid = re.compile(r'\*\*WikiData:\*\* \[([Q\d]+)\]')
    
    stats = {"ok": 0, "fail": 0}

    for file_path in articles_path.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")
        match = regex_qid.search(content)
        
        if match:
            qid = match.group(1)
            term_id = file_path.stem
            
            print(f"Обработка {term_id} (ID: {qid})...", end=" ")
            
            info = fetch_entity_data(qid)
            if info["success"]:
                print(f"ОК -> {info['label_ru']}")
                stats["ok"] += 1
                extracted_nodes.append({
                    "term": term_id,
                    "qid": qid,
                    "ru_name": info["label_ru"],
                    "ru_definition": info["desc_ru"],
                    "en_name": info["label_en"]
                })
            else:
                print(f"ОШИБКА ({info.get('error')})")
                stats["fail"] += 1
        else:
            print(f"Пропуск {file_path.name} (нет Q-ID)")

    # Сохранение результатов в новом формате
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    final_report = {
        "statistics": stats,
        "nodes": extracted_nodes
    }
    
    output_path.write_text(json.dumps(final_report, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"\nСбор данных завершен. Результат сохранен в: {output_path.name}")

if __name__ == "__main__":
    main()