#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from pathlib import Path

CONCEPTS_FILENAME = "concepts.json"
COMBINED_OUTPUT = "combined_concepts.json"

SKIP_CONCEPT_FILES: frozenset[str] = frozenset({"TUTORIAL/concepts.json"})

_PROTECTED_RE = re.compile(
    r"```[\s\S]*?```"
    r"|`[^`\n]+`"
    r"|!\[[^\]]*\]\([^)]*\)"
    r"|\[[^\]]*\]\([^)]*\)"
    r"|\[[^\]]*\]\[[^\]]*\]"
    r"|<[^>]+>",
    re.DOTALL,
)

_WORD_CHARS = r"а-яёА-ЯЁa-zA-Z0-9\-_"


def _resolve_file_path(raw_path: str, repo_root: Path) -> str | None:
    for candidate in (repo_root / raw_path, repo_root / "WEB" / raw_path):
        if candidate.exists():
            return candidate.relative_to(repo_root).as_posix()
    return (repo_root / raw_path).relative_to(repo_root).as_posix() if raw_path else None


def _rel_link(from_file: Path, to_rel: str, repo_root: Path) -> str:
    return os.path.relpath(repo_root / to_rel, from_file.parent).replace("\\", "/")


def load_all_concepts(repo_root: Path) -> tuple[dict[str, str], list[dict]]:
    lemma_map: dict[str, str] = {}
    all_records: list[dict] = []
    files_scanned = 0

    for concepts_path in sorted(repo_root.rglob(CONCEPTS_FILENAME)):
        rel = concepts_path.relative_to(repo_root).as_posix()
        if rel in SKIP_CONCEPT_FILES:
            continue
        files_scanned += 1

        try:
            data = json.loads(concepts_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[WARN] Cannot parse {rel}: {exc}", file=sys.stderr)
            continue

        sections: list[dict] = data if isinstance(data, list) else [data]

        for section in sections:
            for concept in section.get("concepts", []):
                raw_path: str = concept.get("file", "").strip()
                if not raw_path:
                    continue

                resolved = _resolve_file_path(raw_path, repo_root)
                if not resolved:
                    continue

                enriched = dict(concept)
                enriched["_source_concepts_json"] = rel
                enriched["_resolved_file"] = resolved
                all_records.append(enriched)

                for lemma in concept.get("lemmas", []):
                    key = lemma.lower().strip()
                    if key and key not in lemma_map:
                        lemma_map[key] = resolved

    print(
        f"[INFO] Scanned {files_scanned} concepts.json files → "
        f"{len(lemma_map)} unique lemmas across {len(all_records)} concepts."
    )
    return lemma_map, all_records


def save_combined(records: list[dict], repo_root: Path) -> None:
    out_path = repo_root / COMBINED_OUTPUT
    out_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[INFO] Combined concepts saved → {out_path.relative_to(repo_root)}")


def _split_protected(text: str) -> list[tuple[bool, str]]:
    chunks: list[tuple[bool, str]] = []
    last = 0
    for m in _PROTECTED_RE.finditer(text):
        if m.start() > last:
            chunks.append((False, text[last : m.start()]))
        chunks.append((True, m.group(0)))
        last = m.end()
    if last < len(text):
        chunks.append((False, text[last:]))
    return chunks


def _build_combined_pattern(lemmas: list[str]) -> re.Pattern[str]:
    alternation = "|".join(re.escape(l) for l in lemmas)
    pattern = (
        r"(?<![" + _WORD_CHARS + r"])("
        + alternation
        + r")(?![" + _WORD_CHARS + r"])"
    )
    return re.compile(pattern, re.IGNORECASE)


def linkify(
    text: str,
    lemma_map: dict[str, str],
    article_path: Path,
    repo_root: Path,
) -> tuple[str, int]:
    article_rel = article_path.relative_to(repo_root).as_posix()

    sorted_lemmas = sorted(lemma_map.keys(), key=len, reverse=True)

    link_cache: dict[str, str] = {}
    active_lemmas: list[str] = []
    for lemma in sorted_lemmas:
        if lemma_map[lemma] != article_rel:
            link_cache[lemma] = _rel_link(article_path, lemma_map[lemma], repo_root)
            active_lemmas.append(lemma)

    if not active_lemmas:
        return text, 0

    combined = _build_combined_pattern(active_lemmas)

    replaced: set[str] = set()
    total = 0

    def _repl(m: re.Match) -> str:
        nonlocal total
        original_match = m.group(1)
        lemma_key = original_match.lower()
        if lemma_key not in link_cache or lemma_key in replaced:
            return original_match
        replaced.add(lemma_key)
        total += 1
        return f"[{original_match}]({link_cache[lemma_key]})"

    chunks = _split_protected(text)
    new_chunks: list[str] = []
    for is_protected, chunk_text in chunks:
        new_chunks.append(chunk_text if is_protected else combined.sub(_repl, chunk_text))

    return "".join(new_chunks), total


def process_articles(
    repo_root: Path,
    lemma_map: dict[str, str],
    dry_run: bool,
) -> None:
    web_dir = repo_root / "WEB"
    if not web_dir.exists():
        print(f"[ERROR] WEB/ directory not found at {web_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted(web_dir.rglob("*.md"))
    print(f"[INFO] Processing {len(files)} markdown files in WEB/ ...")

    total_links = 0
    modified_count = 0

    for md_path in files:
        original = md_path.read_text(encoding="utf-8")
        modified, count = linkify(original, lemma_map, md_path, repo_root)
        if modified != original:
            modified_count += 1
            total_links += count
            label = "[DRY]" if dry_run else "[MOD]"
            print(f"{label} {md_path.relative_to(repo_root)}  (+{count} links)")
            if not dry_run:
                md_path.write_text(modified, encoding="utf-8")

    status = "DRY RUN — no files written." if dry_run else f"Modified {modified_count}/{len(files)} files."
    print(f"\n[DONE] {status}  Total links inserted: {total_links}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="KidBook cross-linker: merge concepts.json and insert links into WEB/ articles.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without writing any files.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        metavar="PATH",
        help="Path to the repository root (default: current directory).",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    print(f"[INFO] Repo root: {repo_root}")

    lemma_map, all_records = load_all_concepts(repo_root)

    if not args.dry_run:
        save_combined(all_records, repo_root)

    process_articles(repo_root, lemma_map, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
