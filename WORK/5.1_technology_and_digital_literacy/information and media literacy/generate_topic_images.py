"""Generate one cover image per topic from the media literacy index."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

WORK_SUBPATH = Path("WORK/5.1_technology_and_digital_literacy/information and media literacy")
WEB_SUBPATHS = [
    Path("WEB/5.1_technology_and_digital_literacy/information and media literacy"),
    Path("WEB/5.1_technology_and_digital_literacy / information and media literacy"),
]
DEFAULT_INDEX_FILE = "article_index_information_media_literacy.md"
DEFAULT_BASE_URL = "https://api.naga.ac/v1"

TOPIC_SCENE_BRIEFS: dict[str, str] = {
    "Что такое информационная и медиаграмотность": "Teen students in a bright classroom analyze news cards with magnifying glasses and tablets, showing careful thinking and digital awareness.",
    "Как устроена современная информационная среда": "A visual ecosystem of phones, social apps, search icons, and message streams connected by arrows, showing information flow.",
    "Критическое мышление в онлайн-среде": "A student comparing multiple screens with question marks, evidence icons, and check marks, symbolizing evaluation before trust.",
    "Надежные и ненадежные источники": "Two side-by-side web pages, one with clear verification badges and citations, one with warning symbols and broken trust signals.",
    "Фактчекинг пошагово": "Step-by-step path with footprints from claim to source to evidence to conclusion, with check icons at each stage.",
    "Первоисточник и пересказ": "A primary document highlighted in the center, surrounded by simplified repost bubbles that fade with distance.",
    "Логические ошибки в медиа": "Puzzle pieces that almost fit but fail logically, with bias traps and shortcut arrows around them.",
    "Алгоритмы и пузырь фильтров": "A student inside a transparent bubble seeing only similar content cards while diverse content remains outside.",
    "Как работают новостные ленты": "Vertical feed cards ranked by engagement symbols like hearts and comments, with sorting arrows and timeline layers.",
    "Кликбейт и заголовки-ловушки": "A flashy trap-like thumbnail pulling attention while a calm verified article stands nearby.",
    "Манипуляции и пропаганда": "Megaphones repeating simplified messages while a student separates facts from emotional pressure with a shield icon.",
    "Дезинформация и фейки": "False stories branching rapidly across a network while a verification team blocks spread with fact-check stamps.",
    "Информационная безопасность для детей": "Teen using a laptop with protective icons for safe sharing, caution in chats, and privacy boundaries.",
    "Приватность и цифровой след": "Footprints made of data icons across a digital path, with privacy locks and controlled sharing settings.",
    "Кибербуллинг: как распознать и действовать": "Supportive school scene where a teen reports harmful messages to trusted adults and receives help.",
    "Пароли и двухфакторная защита": "Strong password vault, two-factor phone confirmation, and security layers around student accounts.",
    "Авторское право и честное использование": "Creative work with author attribution tags and license symbols, balancing sharing and respect.",
    "Как правильно оформлять ссылки и источники": "Neat research board with connected source cards, author/date markers, and citation structure.",
    "Роль поисковых систем": "Student refining search queries with filters and operators, finding better results from trusted sources.",
    "Оценка качества изображений и видео": "Media forensics desk checking shadows, reflections, compression artifacts, and metadata clues.",
    "Геолокация и проверка контекста": "Detective-style map comparison with landmarks matched to photo details and time-of-day clues.",
    "Проверка фото на манипуляции": "Reverse image search workflow with duplicate matches and edited fragments highlighted.",
    "Проверка цитат и статистики": "Large quotation marks and percentage charts being verified against original reports and datasets.",
    "Эмоциональные триггеры в контенте": "Content cards triggering strong emotions while a student pauses and analyzes before reacting.",
    "Информационная диета": "Balanced plate made of media types with healthy limits, calm routine, and reduced overload symbols.",
    "Этика общения в сети": "Respectful online discussion circles with empathy icons, polite tone cues, and thoughtful replies.",
    "Цифровая репутация": "Timeline of posts shaping a student's future opportunities, with positive choices lighting the path.",
    "Семейные правила потребления контента": "Family planning screen-time and source-check habits together using a simple household chart.",
    "Карта компетенций по возрастам": "Progress ladder for ages 7-9, 10-12, 13-16 with skill milestones and activity icons.",
    "Шаблон урока по медиаграмотности": "Class lesson board with clear stages: warm-up, case study, fact-check practice, reflection.",
}


@dataclass
class Config:
    model: str
    image_size: str
    max_topics: int
    overwrite: bool
    dry_run: bool
    index_file: str
    base_url: str
    export_prompts: bool


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="Generate topic images using OpenAI-compatible image API.")
    parser.add_argument("--model", default="flux-1-kontext-pro", help="Image model name.")
    parser.add_argument(
        "--image-size",
        default="1024x1024",
        choices=["1024x1024", "1536x1024", "1024x1536", "auto"],
        help="Generated image size.",
    )
    parser.add_argument("--max-topics", type=int, default=30, help="Maximum number of topics to process.")
    parser.add_argument("--overwrite", action="store_true", help="Rewrite existing image files.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without API calls.")
    parser.add_argument("--index-file", default=DEFAULT_INDEX_FILE, help="Index markdown filename in WORK folder.")
    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL),
        help="OpenAI-compatible API base URL.",
    )
    parser.add_argument(
        "--export-prompts",
        action="store_true",
        help="Save all generated prompts to topic_image_prompts.json in WORK folder.",
    )
    args = parser.parse_args()
    return Config(
        model=args.model,
        image_size=args.image_size,
        max_topics=args.max_topics,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        index_file=args.index_file,
        base_url=args.base_url,
        export_prompts=args.export_prompts,
    )


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_existing_subpath(repo_root: Path, subpaths: list[Path]) -> Path:
    for subpath in subpaths:
        candidate = repo_root / subpath
        if candidate.exists():
            return candidate
    return repo_root / subpaths[0]


def extract_titles(index_content: str, limit: int) -> list[str]:
    pattern = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*", re.MULTILINE)
    titles = pattern.findall(index_content)
    if not titles:
        raise ValueError("No topic titles found in index file.")
    return titles[:limit]


def sanitize_filename(title: str) -> str:
    cleaned = title.strip().lower()
    cleaned = re.sub(r"[\\/:*?\"<>|]", "", cleaned)
    cleaned = re.sub(r"[-\s]+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    cleaned = cleaned[:120].rstrip("._")
    return cleaned or "topic"


def build_prompt(title: str) -> str:
    scene = TOPIC_SCENE_BRIEFS.get(
        title,
        "Clear educational scene for middle-school students using symbols of analysis, safety, and critical thinking.",
    )
    return (
        f"Scene direction: {scene}\n"
        "Visual style: modern flat illustration, bright balanced colors, simple readable composition, strong contrast.\n"
        "Quality: crisp details, no blur, no noise, high visual clarity.\n"
        "Safety: child-safe and school-appropriate.\n"
        "Hard constraints: no text, no letters, no numbers, no typography, no logos, no watermarks, no UI screenshots.\n"
    )


def build_prompt_payload(title: str) -> dict[str, str]:
    description = TOPIC_SCENE_BRIEFS.get(
        title,
        "Clear educational scene for middle-school students using symbols of analysis, safety, and critical thinking.",
    )
    return {
        "description": description,
        "prompt": build_prompt(title),
    }


def decode_image_item(image_item: object) -> bytes:
    if isinstance(image_item, dict):
        image_url = image_item.get("url")
        b64_value = image_item.get("b64_json")
    else:
        image_url = getattr(image_item, "url", None)
        b64_value = getattr(image_item, "b64_json", None)

    if image_url:
        with urllib.request.urlopen(image_url, timeout=60) as response:
            return response.read()
    if b64_value:
        return base64.b64decode(b64_value)
    raise RuntimeError("Image response item does not include url or b64_json.")


def generate_image(client: Any, model: str, prompt: str, size: str) -> bytes:
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        n=1,
        response_format="b64_json",
    )
    data = getattr(response, "data", None)
    if not data:
        raise RuntimeError("Image generation returned empty data.")
    return decode_image_item(data[0])


def main() -> int:
    cfg = parse_args()
    repo_root = repo_root_from_script()
    work_dir = repo_root / WORK_SUBPATH
    web_dir = resolve_existing_subpath(repo_root, WEB_SUBPATHS)
    index_path = work_dir / cfg.index_file

    if not index_path.exists():
        print(f"[error] Missing index file: {index_path}", file=sys.stderr)
        return 1
    index_content = index_path.read_text(encoding="utf-8")
    titles = extract_titles(index_content, cfg.max_topics)

    web_dir.mkdir(parents=True, exist_ok=True)
    print(f"[info] Topics found: {len(titles)}")
    print(f"[info] Output directory: {web_dir}")
    print(f"[info] Base URL: {cfg.base_url}")

    prompts_by_title = {title: build_prompt(title) for title in titles}
    if cfg.export_prompts:
        prompts_path = work_dir / "topic_image_prompts.json"
        prompt_items = []
        for title in titles:
            stem = sanitize_filename(title)
            payload = build_prompt_payload(title)
            prompt_items.append(
                {
                    "topic": title,
                    "image_filename": f"{stem}.png",
                    "description": payload["description"],
                    "prompt": payload["prompt"],
                }
            )
        prompts_path.write_text(
            json.dumps(prompt_items, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[save] {prompts_path}")

    if cfg.dry_run:
        for title in titles:
            stem = sanitize_filename(title)
            print(f"[dry-run] {title} -> {stem}.png")
        return 0

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[error] OPENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        print("[error] Python package 'openai' is not installed. Install it with: uv sync", file=sys.stderr)
        return 1

    client = OpenAI(api_key=api_key, base_url=cfg.base_url)

    for idx, title in enumerate(titles, start=1):
        stem = sanitize_filename(title)
        image_path = web_dir / f"{stem}.png"
        if image_path.exists() and not cfg.overwrite:
            print(f"[skip] {idx}/{len(titles)} {image_path.name} (already exists)")
            continue

        prompt = prompts_by_title[title]
        print(f"[gen ] {idx}/{len(titles)} {title}")
        try:
            image_bytes = generate_image(client, cfg.model, prompt, cfg.image_size)
            image_path.write_bytes(image_bytes)
            print(f"[save] {image_path.name}")
        except Exception as exc:
            print(f"[fail] {title}: {exc}", file=sys.stderr)

    print("[done] Image generation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
