#!/usr/bin/env python3
"""Insert cross-links between how_universe_works Markdown articles.

Default mode is a dry run. Use --write to update files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ARTICLES_DIR = Path("WEB/1.1_structure_of_the_world/how_universe_works/articles")
DEFAULT_CONCEPTS = Path("WORK/1.1_structure_of_the_world/how_universe_works/concepts.json")
WORD_CHARS = r"A-Za-zА-Яа-яЁё0-9_-"
PROTECTED_RE = re.compile(
    r"```[\s\S]*?```"
    r"|`[^`\n]+`"
    r"|!\[[^\]]*\]\([^)]*\)"
    r"|\[[^\]]*\]\([^)]*\)"
    r"|<https?://[^>]+>"
    r"|https?://\S+",
    re.MULTILINE,
)
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class Concept:
    name: str
    file: Path
    terms: tuple[str, ...]


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "WEB").exists() and (candidate / "WORK").exists():
            return candidate
    return start


def read_concepts(path: Path) -> list[Concept]:
    data = json.loads(path.read_text(encoding="utf-8"))
    sections = data if isinstance(data, list) else [data]
    concepts: list[Concept] = []

    for section in sections:
        for item in section.get("concepts", []):
            file_value = item.get("file")
            if not file_value:
                continue

            raw_terms = [item.get("name", ""), *item.get("lemmas", [])]
            seen: set[str] = set()
            terms: list[str] = []
            for raw_term in raw_terms:
                term = " ".join(str(raw_term).strip().split())
                key = term.casefold()
                if term and key not in seen:
                    seen.add(key)
                    terms.append(term)

            concepts.append(
                Concept(
                    name=item.get("name", file_value),
                    file=Path(file_value),
                    terms=tuple(sorted(terms, key=len, reverse=True)),
                )
            )

    return concepts


def split_protected(text: str) -> list[tuple[bool, str]]:
    chunks: list[tuple[bool, str]] = []
    last = 0
    for match in PROTECTED_RE.finditer(text):
        if match.start() > last:
            chunks.append((False, text[last : match.start()]))
        chunks.append((True, match.group(0)))
        last = match.end()
    if last < len(text):
        chunks.append((False, text[last:]))
    return chunks


def link_to(from_file: Path, target_file: Path) -> str:
    return os.path.relpath(target_file, from_file.parent).replace("\\", "/")


def existing_link_targets(text: str, article: Path) -> set[Path]:
    targets: set[Path] = set()
    for match in LINK_RE.finditer(text):
        href = match.group(1).split("#", 1)[0].strip()
        if not href or href.startswith(("http://", "https://", "mailto:")):
            continue
        targets.add((article.parent / href).resolve())
    return targets


def build_pattern(terms: list[str]) -> re.Pattern[str]:
    alternatives = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
    return re.compile(rf"(?<![{WORD_CHARS}])({alternatives})(?![{WORD_CHARS}])", re.IGNORECASE)


def linkify_article(text: str, article: Path, concepts: list[Concept], repo_root: Path) -> tuple[str, int]:
    article_resolved = article.resolve()
    already_linked = existing_link_targets(text, article)
    term_targets: dict[str, Path] = {}

    for concept in concepts:
        target = (repo_root / concept.file).resolve()
        if target == article_resolved or target in already_linked:
            continue
        for term in concept.terms:
            term_targets.setdefault(term.casefold(), target)

    if not term_targets:
        return text, 0

    pattern = build_pattern(list(term_targets.keys()))
    inserted_targets: set[Path] = set()
    inserted_count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal inserted_count
        original = match.group(1)
        target = term_targets.get(original.casefold())
        if target is None or target in inserted_targets:
            return original
        inserted_targets.add(target)
        inserted_count += 1
        return f"[{original}]({link_to(article, target)})"

    output: list[str] = []
    for is_protected, chunk in split_protected(text):
        output.append(chunk if is_protected else pattern.sub(replace, chunk))

    return "".join(output), inserted_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root. Default: current directory.")
    parser.add_argument("--concepts", default=str(DEFAULT_CONCEPTS), help="Path to concepts.json.")
    parser.add_argument("--articles-dir", default=str(DEFAULT_ARTICLES_DIR), help="Directory with Markdown articles.")
    parser.add_argument("--write", action="store_true", help="Rewrite Markdown files in place.")
    args = parser.parse_args()

    repo_root = find_repo_root(Path(args.repo_root).resolve())
    concepts_path = (repo_root / args.concepts).resolve()
    articles_dir = (repo_root / args.articles_dir).resolve()
    concepts = read_concepts(concepts_path)

    total = 0
    changed = 0
    for article in sorted(articles_dir.glob("*.md")):
        old_text = article.read_text(encoding="utf-8")
        new_text, count = linkify_article(old_text, article, concepts, repo_root)
        if new_text == old_text:
            continue
        changed += 1
        total += count
        mode = "WRITE" if args.write else "DRY"
        print(f"[{mode}] {article.relative_to(repo_root)} (+{count})")
        if args.write:
            article.write_text(new_text, encoding="utf-8")

    if args.write:
        print(f"Done. Changed files: {changed}. Links inserted: {total}.")
    else:
        print(f"Dry run. Changed files: {changed}. Links that would be inserted: {total}.")
        print("Run again with --write to update Markdown files.")


if __name__ == "__main__":
    main()
