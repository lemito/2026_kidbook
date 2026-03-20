"""
Генерация markdown-статей раздела «Почему наука помогает понимать мир»
через GigaChat API.

Использование:
    set GIGACHAT_CREDENTIALS=<base64-ключ>      (Windows)
    export GIGACHAT_CREDENTIALS=<base64-ключ>    (Linux/Mac)
    python WORK/science/generate_articles.py            # генерация + пост-обработка
    python WORK/science/generate_articles.py --fix      # только пост-обработка
"""

import json
import os
import re
import sys
import time
import uuid
import requests
from pathlib import Path

requests.packages.urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent.parent
CONCEPTS_FILE = ROOT / "WORK" / "1.2_natural_sciences" / "why_science_help_understand_world" / "concepts.json"
WIKIDATA_FILE = ROOT / "WORK" / "1.2_natural_sciences" / "why_science_help_understand_world" / "wikidata_extract.json"
OUT_DIR = ROOT / "WEB" / "1.2_natural_sciences" / "why_science_help_understand_world"

GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
MODEL = "GigaChat"

EMOJI_RE = re.compile(
    "[\U00002600-\U000027BF\U0001F300-\U0001F9FF\U0000FE00-\U0000FE0F\U0000200D]+",
    flags=re.UNICODE,
)


def get_access_token(credentials: str) -> str:
    resp = requests.post(
        GIGACHAT_AUTH_URL,
        headers={
            "Authorization": f"Basic {credentials}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"scope": "GIGACHAT_API_PERS"},
        timeout=30,
        verify=False,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def call_gigachat(prompt: str, token: str) -> str:
    resp = requests.post(
        GIGACHAT_API_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.7,
        },
        timeout=60,
        verify=False,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def load_concepts() -> list[dict]:
    with open(CONCEPTS_FILE, encoding="utf-8") as f:
        return json.load(f)["concepts"]


def build_relations(concepts: list[dict]) -> dict[str, list[str]]:
    uri_to_id = {
        f"http://www.wikidata.org/entity/{c['wikidata']}": c["id"]
        for c in concepts if c.get("wikidata")
    }
    adjacency: dict[str, set[str]] = {c["id"]: set() for c in concepts}

    if not WIKIDATA_FILE.exists():
        return {k: [] for k in adjacency}

    with open(WIKIDATA_FILE, encoding="utf-8") as f:
        wikidata = json.load(f)

    for edge in wikidata["results"]["bindings"]:
        src = uri_to_id.get(edge["item"]["value"])
        tgt = uri_to_id.get(edge["target"]["value"])
        if src and tgt and src != tgt:
            adjacency[src].add(tgt)
            adjacency[tgt].add(src)

    return {k: sorted(v) for k, v in adjacency.items()}


def build_prompt(concept: dict, related_names: list[str]) -> str:
    name = concept["ru"]
    related_str = ", ".join(related_names) if related_names else "—"

    return f"""Ты пишешь статью для детской энциклопедии. Читатель — ребёнок 10 лет. Тема раздела: «Почему наука помогает понимать мир».

Тема статьи: «{name}»
Связанные понятия (упомяни их естественно в тексте): {related_str}

Структура строго в формате Markdown:

# {name}

## Что это такое?
3–4 предложения. Простое определение + пример из жизни ребёнка.

## Как это работает?
4–5 абзацев с примерами из повседневности (школа, дом, прогулки, игры, еда, погода).

## Почему это важно для науки?
2–3 абзаца. Как это понятие помогает понимать мир вокруг.

## Интересные примеры
3–4 простых опыта или наблюдения, которые ребёнок может повторить дома.

Не добавляй раздел «Смотри также» — он будет сгенерирован автоматически.
Не используй эмодзи в заголовках.
Язык живой и разговорный, минимум 500 слов."""


def postprocess(text: str, concept_id: str, relations: dict[str, list[str]],
                id_to_name: dict[str, str]) -> str:
    # Убрать эмодзи
    text = EMOJI_RE.sub("", text)
    text = re.sub(r"##  +", "## ", text)

    # Убрать сгенерированный LLM блок «Смотри также»
    text = re.sub(r"\n+---\s*\n+## *Смотри также.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\n+## *Смотри также.*", "", text, flags=re.DOTALL)
    text = text.rstrip()

    # Добавить правильный «Смотри также» из графа знаний
    related = relations.get(concept_id, [])
    if related:
        links = [f"- [{id_to_name[r]}]({r}.md)" for r in related if r in id_to_name]
        text += "\n\n---\n\n## Смотри также\n" + "\n".join(links)

    return text + "\n"


def main() -> None:
    fix_only = "--fix" in sys.argv

    concepts = load_concepts()
    relations = build_relations(concepts)
    id_to_name = {c["id"]: c["ru"] for c in concepts}
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if fix_only:
        print("Режим --fix: пост-обработка существующих статей.\n")
        for concept in concepts:
            filepath = OUT_DIR / f"{concept['id']}.md"
            if not filepath.exists():
                print(f"  [!] Нет файла: {filepath.name}")
                continue
            original = filepath.read_text(encoding="utf-8")
            fixed = postprocess(original, concept["id"], relations, id_to_name)
            filepath.write_text(fixed, encoding="utf-8")
            print(f"  [+] {filepath.name}")
        print("\nПост-обработка завершена.")
        return

    credentials = os.environ.get("GIGACHAT_CREDENTIALS")
    if not credentials:
        sys.exit("Задай GIGACHAT_CREDENTIALS (base64-ключ из developers.sber.ru)")

    print("Получаем access token...")
    token = get_access_token(credentials)
    print("Токен получен.\n")

    for concept in concepts:
        cid = concept["id"]
        out_file = OUT_DIR / f"{cid}.md"

        if out_file.exists():
            print(f"  Пропускаем: {concept['ru']} (файл уже есть)")
            continue

        related_names = [id_to_name[r] for r in relations.get(cid, []) if r in id_to_name]
        prompt = build_prompt(concept, related_names)

        print(f"  Генерируем: {concept['ru']}...")
        try:
            text = call_gigachat(prompt, token)
            text = postprocess(text, cid, relations, id_to_name)
        except Exception as exc:
            print(f"    Ошибка API: {exc}")
            text = f"# {concept['ru']}\n\n> Статья не сгенерирована.\n"

        out_file.write_text(text, encoding="utf-8")
        print(f"    Готово: {out_file.name}")
        time.sleep(1.5)

    print(f"\nСтатьи сохранены в {OUT_DIR}")


if __name__ == "__main__":
    main()
