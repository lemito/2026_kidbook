from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole


SCRIPT_DIR = Path(__file__).resolve().parent
WORK_DIR = SCRIPT_DIR.parent
REPO_ROOT = WORK_DIR.parent.parent.parent

DEFAULT_CONCEPTS_PATH = REPO_ROOT / "WEB" / "4.1" / "how_to_learn_effectively" / "concepts.json"
DEFAULT_OUTPUT_DIR = WORK_DIR / "generated_articles_api"


@dataclass
class GigaChatSettings:
    credentials: str | None
    access_token: str | None
    model: str
    timeout_seconds: int
    verify_ssl_certs: bool


def parse_bool(raw_value: str | None, default: bool) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate article drafts via GigaChat API without touching WEB articles."
    )
    parser.add_argument(
        "--only",
        nargs="*",
        default=[],
        help="Generate only these stems, for example curiosity note_taking.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Generate only first N concepts after filtering. 0 means all.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated drafts in WORK/generated_articles_api.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print target files and prompts without calling GigaChat.",
    )
    return parser.parse_args()


def load_settings() -> GigaChatSettings:
    load_dotenv(WORK_DIR / ".env")

    credentials = (os.getenv("GIGACHAT_CREDENTIALS") or "").strip() or None
    access_token = (os.getenv("GIGACHAT_ACCESS_TOKEN") or "").strip() or None
    if not credentials and not access_token:
        raise RuntimeError(
            "Set GIGACHAT_CREDENTIALS or GIGACHAT_ACCESS_TOKEN in WORK/4.1/how_to_learn_effectively/.env"
        )

    return GigaChatSettings(
        credentials=credentials,
        access_token=access_token,
        model=(os.getenv("GIGACHAT_MODEL") or "GigaChat-2-Max").strip(),
        timeout_seconds=int((os.getenv("GIGACHAT_TIMEOUT_SECONDS") or "180").strip()),
        verify_ssl_certs=parse_bool(os.getenv("GIGACHAT_VERIFY_SSL_CERTS"), default=True),
    )


def create_client(settings: GigaChatSettings) -> GigaChat:
    kwargs: dict[str, Any] = {
        "model": settings.model,
        "timeout": settings.timeout_seconds,
        "verify_ssl_certs": settings.verify_ssl_certs,
    }
    if settings.credentials:
        kwargs["credentials"] = settings.credentials
    if settings.access_token:
        kwargs["access_token"] = settings.access_token
    return GigaChat(**kwargs)


def load_concepts(concepts_path: Path) -> list[dict[str, Any]]:
    data = json.loads(concepts_path.read_text(encoding="utf-8"))
    concepts: list[dict[str, Any]] = []
    for section in data:
        concepts.extend(section.get("concepts", []))
    return concepts


def concept_stem(concept: dict[str, Any]) -> str:
    file_path = concept.get("file", "")
    name = Path(file_path).stem
    if name:
        return name
    concept_id = concept.get("id", "")
    return concept_id.rsplit("/", 1)[-1]


def filter_concepts(concepts: list[dict[str, Any]], only: set[str], limit: int) -> list[dict[str, Any]]:
    filtered = [concept for concept in concepts if not only or concept_stem(concept) in only]
    if limit > 0:
        filtered = filtered[:limit]
    return filtered


def clean_filename(raw_name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "_", raw_name).strip("._")
    return normalized or "article"


def build_prompt(concept: dict[str, Any]) -> str:
    title = concept.get("name", concept_stem(concept))
    description = concept.get("description", "")
    lemmas = ", ".join(concept.get("lemmas", [])[:8])
    author = concept.get("author", "unknown")
    return (
        "Напиши markdown-статью для детской энциклопедии.\n"
        "Целевая аудитория: школьники 10-16 лет.\n"
        "Стиль: простой, дружелюбный, объясни для десятилетнего ребенка, "
        "но без слишком примитивного тона.\n"
        "Структура: заголовок H1, короткое введение, 4-6 разделов H2, "
        "примеры, практические советы, мини-итог.\n"
        "Можно использовать списки и таблицы.\n"
        "Не добавляй HTML. Пиши только markdown.\n"
        f"Понятие: {title}\n"
        f"Описание: {description}\n"
        f"Ключевые слова: {lemmas}\n"
        f"Автор в concepts.json: {author}\n"
    )


def extract_content_text(completion: Any) -> str:
    choices = getattr(completion, "choices", None) or []
    for choice in choices:
        message = getattr(choice, "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, str) and content.strip():
            return content.strip()
    return ""


def ensure_title(text: str, concept: dict[str, Any]) -> str:
    if re.search(r"^\s*#\s+", text, flags=re.MULTILINE):
        return text
    title = concept.get("name", concept_stem(concept))
    return f"# {title}\n\n{text}"


def build_output_text(concept: dict[str, Any], body: str) -> str:
    stem = concept_stem(concept)
    metadata = [
        "<!-- Generated with GigaChat API for coursework evidence. -->",
        f"<!-- Concept stem: {stem} -->",
        f"<!-- Source concept file: {concept.get('file', '')} -->",
        "",
    ]
    return "\n".join(metadata) + ensure_title(body.strip(), concept).rstrip() + "\n"


def generate_article_text(concept: dict[str, Any], settings: GigaChatSettings) -> str:
    prompt = build_prompt(concept)
    with create_client(settings) as giga:
        completion = giga.chat(
            Chat(
                model=settings.model,
                messages=[
                    Messages(
                        role=MessagesRole.SYSTEM,
                        content=(
                            "Ты помогаешь автоматически генерировать черновики статей "
                            "для детской энциклопедии в формате markdown."
                        ),
                    ),
                    Messages(role=MessagesRole.USER, content=prompt),
                ],
            )
        )
    content = extract_content_text(completion)
    if not content:
        raise RuntimeError(f"Empty completion for concept {concept_stem(concept)}")
    return content


def main() -> int:
    args = parse_args()
    concepts = load_concepts(DEFAULT_CONCEPTS_PATH)
    targets = filter_concepts(concepts, set(args.only), args.limit)

    print(f"Concepts: {len(targets)}")
    print(f"Output dir: {DEFAULT_OUTPUT_DIR}")

    if args.dry_run:
        for concept in targets:
            stem = concept_stem(concept)
            target = DEFAULT_OUTPUT_DIR / f"{clean_filename(stem)}.md"
            print(f"[dry-run] {stem} -> {target}")
            print(build_prompt(concept)[:250] + "...")
        return 0

    settings = load_settings()
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for index, concept in enumerate(targets, start=1):
        stem = concept_stem(concept)
        output_file = DEFAULT_OUTPUT_DIR / f"{clean_filename(stem)}.md"
        if output_file.exists() and not args.force:
            print(f"[{index}/{len(targets)}] SKIP {stem} (exists)")
            continue

        print(f"[{index}/{len(targets)}] GENERATE {stem}")
        article_text = generate_article_text(concept, settings)
        output_file.write_text(build_output_text(concept, article_text), encoding="utf-8")
        time.sleep(0.3)

    print("Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
