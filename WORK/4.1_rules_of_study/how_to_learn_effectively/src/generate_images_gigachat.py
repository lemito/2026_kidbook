from __future__ import annotations

import argparse
import base64
import os
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole


SCRIPT_DIR = Path(__file__).resolve().parent
WORK_DIR = SCRIPT_DIR
REPO_ROOT = WORK_DIR.parent.parent.parent

DEFAULT_ARTICLES_DIR = REPO_ROOT / "WEB" / "4.1" / "how_to_learn_effectively" / "articles"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "WEB" / "4.1" / "how_to_learn_effectively" / "images"


@dataclass
class GigaChatSettings:
    credentials: str | None
    access_token: str | None
    model: str
    timeout_seconds: int
    attempts: int
    backoff_base_seconds: float
    verify_ssl_certs: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate header illustrations for learning articles with GigaChat."
    )
    parser.add_argument(
        "--style",
        default=(
            "Мягкая детская энциклопедическая иллюстрация, яркие, но спокойные цвета, "
            "чистая композиция, дружелюбная атмосфера."
        ),
        help="Additional style instructions for prompts.",
    )
    parser.add_argument(
        "--update-md",
        action="store_true",
        help="Insert or replace the header image in each article markdown file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate files even if the target image already exists.",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        default=[],
        help="Generate only these article stems, for example curiosity note_taking.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts and target files without calling the API.",
    )
    return parser.parse_args()


def env_path(raw_value: str | None, fallback: Path) -> Path:
    if not raw_value:
        return fallback
    path = Path(raw_value)
    if not path.is_absolute():
        path = (WORK_DIR / path).resolve()
    return path


def parse_bool(raw_value: str | None, default: bool) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_settings() -> GigaChatSettings:
    load_dotenv(WORK_DIR / ".env")

    credentials = (os.getenv("GIGACHAT_CREDENTIALS") or "").strip() or None
    access_token = (os.getenv("GIGACHAT_ACCESS_TOKEN") or "").strip() or None
    if not credentials and not access_token:
        raise RuntimeError(
            "Set GIGACHAT_CREDENTIALS or GIGACHAT_ACCESS_TOKEN in WORK/4.1/how_to_learn_effectively/.env"
        )

    model = (os.getenv("GIGACHAT_MODEL") or "GigaChat-2-Max").strip()
    timeout_seconds = int((os.getenv("GIGACHAT_TIMEOUT_SECONDS") or "180").strip())
    attempts = int((os.getenv("GIGACHAT_MAX_ATTEMPTS") or "6").strip())
    backoff_base_seconds = float((os.getenv("GIGACHAT_BACKOFF_BASE") or "2.0").strip())
    verify_ssl_certs = parse_bool(os.getenv("GIGACHAT_VERIFY_SSL_CERTS"), default=True)

    return GigaChatSettings(
        credentials=credentials,
        access_token=access_token,
        model=model,
        timeout_seconds=timeout_seconds,
        attempts=max(attempts, 1),
        backoff_base_seconds=max(backoff_base_seconds, 0.5),
        verify_ssl_certs=verify_ssl_certs,
    )


def list_articles(articles_dir: Path) -> list[Path]:
    return sorted(p for p in articles_dir.glob("*.md") if p.name != "index.md")


def markdown_to_plain_text(markdown: str) -> str:
    text = re.sub(r"```[\s\S]*?```", " ", markdown)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[`*_>~#-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_prompt(article_stem: str, title: str, plain_text: str, style: str) -> str:
    excerpt = plain_text[:1400]
    return (
        "Нарисуй горизонтальную иллюстрацию для шапки детской энциклопедической статьи. "
        "Аудитория: школьники 10-16 лет. "
        "Покажи главную идею статьи через понятную сцену, метафору или учебную ситуацию. "
        "Изображение должно быть безопасным, дружелюбным и наглядным, без перегруза мелкими деталями. "
        "Без текста, без букв, без цифр, без интерфейсов, без логотипов, без водяных знаков. "
        f"Тема файла: {article_stem}. "
        f"Заголовок статьи: {title}. "
        f"Контекст статьи: {excerpt}. "
        f"Стиль: {style.strip()}"
    )


def extract_attachments(completion: Any) -> list[str]:
    attachment_ids: list[str] = []
    choices = getattr(completion, "choices", None) or []
    for choice in choices:
        message = getattr(choice, "message", None)
        attachments = getattr(message, "attachments", None) or []
        for file_id in attachments:
            if isinstance(file_id, str) and file_id.strip():
                attachment_ids.append(file_id.strip())
        content = getattr(message, "content", None)
        if isinstance(content, str) and content.strip():
            for match in re.finditer(r'<img\s+src="([^"]+)"', content):
                file_id = match.group(1).strip()
                if file_id:
                    attachment_ids.append(file_id)
    return attachment_ids


def extract_content_text(completion: Any) -> str:
    choices = getattr(completion, "choices", None) or []
    for choice in choices:
        message = getattr(choice, "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, str) and content.strip():
            return content.strip()
    return ""


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


def gigachat_generate_image_bytes(prompt: str, settings: GigaChatSettings) -> bytes:
    last_error: Exception | None = None

    for attempt in range(1, settings.attempts + 1):
        try:
            with create_client(settings) as giga:
                completion = giga.chat(
                    Chat(
                        model=settings.model,
                        messages=[
                            Messages(
                                role=MessagesRole.SYSTEM,
                                content=(
                                    "Ты создаёшь безопасные детские иллюстрации для энциклопедии. "
                                    "Старайся возвращать именно изображение, а не только текстовое описание."
                                ),
                            ),
                            Messages(role=MessagesRole.USER, content=prompt),
                        ],
                        function_call="auto",
                    )
                )

                attachments = extract_attachments(completion)
                if not attachments:
                    content = extract_content_text(completion)
                    raise RuntimeError(
                        f"GigaChat returned no image attachment. Reply: {content[:280]}"
                    )

                image_obj = giga.get_image(attachments[0])
                content_b64 = getattr(image_obj, "content", None)
                if not isinstance(content_b64, str) or not content_b64.strip():
                    raise RuntimeError("GigaChat get_image returned empty content.")

                return base64.b64decode(content_b64)
        except Exception as exc:
            last_error = exc
            if attempt >= settings.attempts:
                break
            delay = settings.backoff_base_seconds * (2 ** (attempt - 1))
            jitter = random.uniform(0.0, 0.2 * settings.backoff_base_seconds)
            total_delay = delay + jitter
            print(f"    retry gigachat in {total_delay:.1f}s")
            time.sleep(total_delay)

    assert last_error is not None
    raise last_error


def save_image(image_bytes: bytes, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(image_bytes)


def update_markdown_image_link(article_file: Path, relative_image_path: str) -> None:
    content = article_file.read_text(encoding="utf-8")
    image_line = f"![Иллюстрация к статье]({relative_image_path})"

    if re.search(r"!\[[^\]]*\]\([^)]*\)", content):
        updated = re.sub(r"!\[[^\]]*\]\([^)]*\)", image_line, content, count=1)
    else:
        updated = f"{image_line}\n\n{content}"

    article_file.write_text(updated, encoding="utf-8")


def iter_target_articles(all_articles: Iterable[Path], only: set[str]) -> list[Path]:
    if not only:
        return list(all_articles)
    return [article for article in all_articles if article.stem in only]


def main() -> None:
    args = parse_args()
    articles_dir = env_path(os.getenv("GIGACHAT_ARTICLES_DIR"), DEFAULT_ARTICLES_DIR)
    output_dir = env_path(os.getenv("GIGACHAT_OUTPUT_DIR"), DEFAULT_OUTPUT_DIR)

    articles = list_articles(articles_dir)
    targets = iter_target_articles(articles, set(args.only))

    print(f"Articles: {len(targets)}")
    print(f"Articles dir: {articles_dir}")
    print(f"Output dir: {output_dir}")
    print(f"Force: {args.force}")

    settings: GigaChatSettings | None = None
    if not args.dry_run:
        settings = load_settings()
        print(
            "GigaChat settings: "
            f"model={settings.model}, "
            f"timeout={settings.timeout_seconds}s, "
            f"attempts={settings.attempts}, "
            f"backoff_base={settings.backoff_base_seconds:.1f}s"
        )

    for index, article_file in enumerate(targets, start=1):
        stem = article_file.stem
        output_file = output_dir / f"{stem}.jpg"

        if output_file.exists() and not args.force:
            print(f"[{index}/{len(targets)}] SKIP {stem} (exists)")
            continue

        markdown = article_file.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
        title = (
            title_match.group(1).strip()
            if title_match
            else stem.replace("-", " ").replace("_", " ")
        )
        plain_text = markdown_to_plain_text(markdown)
        prompt = build_prompt(stem, title, plain_text, args.style)

        if args.dry_run:
            print(f"[{index}/{len(targets)}] DRY {stem} -> {output_file.name}")
            print(prompt[:400] + ("..." if len(prompt) > 400 else ""))
            continue

        assert settings is not None
        print(f"[{index}/{len(targets)}] GENERATE {stem}")
        image_bytes = gigachat_generate_image_bytes(prompt, settings)
        save_image(image_bytes, output_file)

        if args.update_md:
            update_markdown_image_link(article_file, f"../images/{stem}.jpg")

    print("Done")


if __name__ == "__main__":
    main()
