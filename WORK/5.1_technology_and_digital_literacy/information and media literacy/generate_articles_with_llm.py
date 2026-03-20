"""Generate wiki-style markdown articles from the topic index using an LLM."""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from openai import OpenAI

WORK_SUBPATH = Path("WORK/5.1_technology_and_digital_literacy/information and media literacy")
WEB_SUBPATHS = [
    Path("WEB/5.1_technology_and_digital_literacy/information and media literacy/articles"),
    Path("WEB/5.1_technology_and_digital_literacy/information and media literacy/articles"),
]
TUTORIAL_SUBPATH = Path("TUTORIAL/how_write_articles/README.md")
DEFAULT_INDEX_FILE = "article_index_information_media_literacy.md"


@dataclass
class Config:
    model: str
    max_articles: int
    overwrite: bool
    dry_run: bool
    language: str


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="Generate markdown articles from topic index using OpenAI-compatible API."
    )
    parser.add_argument("--model", default="qwen3-next-80b-a3b-instruct", help="Model name, e.g. qwen3-next-80b-a3b-instruct")
    parser.add_argument("--max-articles", type=int, default=30, help="Maximum number of articles to generate")
    parser.add_argument("--overwrite", action="store_true", help="Rewrite existing article files")
    parser.add_argument("--dry-run", action="store_true", help="Show planned files without API calls")
    parser.add_argument("--language", default="Russian", help="Article language")
    args = parser.parse_args()
    return Config(
        model=args.model,
        max_articles=args.max_articles,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        language=args.language,
    )


def repo_root_from_script() -> Path:
    # Script path: <repo>/WORK/.../information and media literacy/generate_articles_with_llm.py
    return Path(__file__).resolve().parents[3]


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return path.read_text(encoding="utf-8")


def resolve_existing_subpath(repo_root: Path, subpaths: list[Path]) -> Path:
    for subpath in subpaths:
        candidate = repo_root / subpath
        if candidate.exists():
            return candidate
    return repo_root / subpaths[0]


def extract_titles(index_content: str, limit: int) -> list[str]:
    pattern = re.compile(r"^(\d+)\.\s+\*\*(.+?)\*\*", re.MULTILINE)
    matches = list(pattern.finditer(index_content))
    if not matches:
        raise ValueError("No article titles found in index file.")
    topics: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(index_content)
        block = index_content[start:end]

        short_description = ""
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("См. также:"):
                continue
            short_description = line
            break
        topics.append((title, short_description))
    return topics[:limit]


def sanitize_filename(title: str) -> str:
    cleaned = title.strip().lower()
    cleaned = re.sub(r"[\\/:*?\"<>|]", "", cleaned)
    cleaned = re.sub(r"[-\s]+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    cleaned = cleaned[:120].rstrip("._")
    return cleaned or "article"


def build_system_prompt(format_guide: str, language: str) -> str:
    return (
        "You are a professional educational writer for KidBook.\n"
        "KidBook wiki audience: 8th graders (around 13-14 years old).\n"
        f"Write in {language}. Return only markdown article content.\n"
        "Strictly follow markdown formatting conventions from this guide:\n\n"
        f"{format_guide}\n\n"
        "Hard requirements:\n"
        "1) Start with one H1 title matching the topic.\n"
        "2) Use clear sections with H2/H3.\n"
        "3) Include at least one bullet list and one table if relevant.\n"
        "4) Add useful internal anchors/links where meaningful.\n"
        "5) End with exactly this footer style:\n"
        "---\n"
        "Авторы: <names>;  \n"
        "*Ресурсы: LLM - <model>*\n"
        "6) Avoid unsafe or age-inappropriate content.\n"
    )


def build_user_prompt(title: str, topic_description: str) -> str:
    return (
        f"Topic: {title}\n"
        f"Topic brief: {topic_description}\n"
        "Audience: 8th graders, parents, and teachers.\n"
        "Goal: practical wiki-style article with definitions, examples, and actionable tips.\n"
        "Length: 900-1500 words.\n"
        "Include: key terms, common mistakes, mini checklist, and 3-5 reliable external references.\n"
    )


def generate_article(client: Any, model: str, system_prompt: str, user_prompt: str) -> str:
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ],
    )
    text = response.output_text.strip()
    if not text:
        raise RuntimeError("Model returned empty article content.")
    return text + "\n"


def ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def main() -> int:
    cfg = parse_args()
    repo_root = repo_root_from_script()
    work_dir = repo_root / WORK_SUBPATH
    web_dir = resolve_existing_subpath(repo_root, WEB_SUBPATHS)
    index_file = work_dir / DEFAULT_INDEX_FILE
    tutorial_file = repo_root / TUTORIAL_SUBPATH

    try:
        index_content = read_text(index_file)
        format_guide = read_text(tutorial_file)
        topics = extract_titles(index_content, cfg.max_articles)
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    ensure_dirs([web_dir])

    print(f"[info] Found {len(topics)} topics in {index_file}")
    print(f"[info] Output directory: {web_dir}")

    if cfg.dry_run:
        for title, _ in topics:
            stem = sanitize_filename(title)
            print(f"[dry-run] {title} -> {stem}.md")
        return 0

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[error] OPENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    base_url = os.getenv("OPENAI_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    system_prompt = build_system_prompt(format_guide, cfg.language)

    for idx, (title, topic_description) in enumerate(topics, start=1):
        stem = sanitize_filename(title)
        out_file = web_dir / f"{stem}.md"
        if out_file.exists() and not cfg.overwrite:
            print(f"[skip] {idx}/{len(topics)} {out_file.name} (already exists)")
            continue

        print(f"[gen ] {idx}/{len(topics)} {title}")
        try:
            user_prompt = build_user_prompt(title, topic_description)
            content = generate_article(client, cfg.model, system_prompt, user_prompt)
            out_file.write_text(content, encoding="utf-8")
            print(f"[save] {out_file.name}")
        except Exception as exc:
            print(f"[fail] {title}: {exc}", file=sys.stderr)

    print("[done] Generation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
