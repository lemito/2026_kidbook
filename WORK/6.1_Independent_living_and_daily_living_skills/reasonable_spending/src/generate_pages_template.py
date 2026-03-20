import json
import os
from pathlib import Path
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

# Скрипт генерации черновиков статей через совместимый LLM endpoint.
# Перед публикацией тексты обязательно проходят ручную вычитку команды.

ROOT = Path(__file__).resolve().parents[3]
CONCEPTS_PATH = ROOT / "WORK" / "6.1_reasonable_spending" / "concepts.json"
OUTPUT_DIR = ROOT / "WEB" / "6.1_reasonable_spending" / "articles"

LLM_API_URL = os.getenv("LLM_API_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
MODEL_NAME = os.getenv("LLM_MODEL", "model-name")

SYSTEM_PROMPT = (
    "Ты пишешь детскую энциклопедию. Пиши просто, доброжелательно и точно. "
    "Всегда объясняй для десятилетнего ребенка."
)

USER_PROMPT_TEMPLATE = """
Сгенерируй markdown-страницу для детской энциклопедии.
Тема: разумные траты денег.
Понятие: {concept_name}

Требования:
1) Объясни для десятилетнего ребенка.
2) Дай определение в 1-2 предложениях.
3) Добавь разделы:
   - Зачем это важно
   - Пример из жизни школьника
   - 3 практических совета
   - Связанные понятия
4) Объем: 120-220 слов.
5) Без сложных экономических терминов без объяснения.
6) Формат ответа: чистый markdown.
""".strip()


def load_concepts():
    data = json.loads(CONCEPTS_PATH.read_text(encoding="utf-8"))
    return data["concepts"]


def call_llm(user_prompt: str) -> str:
    if not LLM_API_URL or not LLM_API_KEY:
        raise RuntimeError(
            "Set LLM_API_URL and LLM_API_KEY environment variables before running."
        )

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
    }

    req = urllib_request.Request(
        LLM_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM API HTTP error {exc.code}: {details}") from exc
    except URLError as exc:
        raise RuntimeError(f"LLM API connection error: {exc}") from exc

    # OpenAI-compatible format fallback.
    return body["choices"][0]["message"]["content"].strip()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    concepts = load_concepts()

    for concept in concepts:
        file_path = OUTPUT_DIR / Path(concept["file"]).name
        if file_path.exists():
            # Skip existing files to avoid accidental overwrite.
            continue

        prompt = USER_PROMPT_TEMPLATE.format(concept_name=concept["name"])
        markdown = call_llm(prompt)
        file_path.write_text(markdown + "\n", encoding="utf-8")
        print(f"Created: {file_path.name}")


if __name__ == "__main__":
    main()
