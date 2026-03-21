"""Cross-link concepts in Markdown articles.

Usage:
    python crosslink_concepts.py --concepts /path/to/WORK/2.2_history/world_economy_on_fingers/concepts.json --apply
    python crosslink_concepts.py --concepts /path/to/concepts.json WEB/2.2_history/world_economy_on_fingers/articles

The script reads concept metadata from the section concepts.json file, scans
Markdown articles for Russian concepts and their inflected forms, and replaces
the first suitable plain-text occurrence with a Markdown link to the concept
article. When links_from_article is present for a concept, only those target
concepts are considered for cross-links.

It skips headings, fenced code blocks, inline code, URLs, and existing Markdown
links/images. By default it prints a dry-run summary; pass --apply to rewrite
files in place.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from pymorphy3 import MorphAnalyzer  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    MorphAnalyzer = None  # type: ignore


WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+(?:-[A-Za-zА-Яа-яЁё0-9]+)*")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
URL_RE = re.compile(r"https?://\S+")
HTML_TAG_RE = re.compile(r"<[^>\n]+>")
MARKDOWN_LINK_RE = re.compile(r"!\[[^\]\n]*\]\([^\n]*?\)|\[[^\]\n]*\]\([^\n]*?\)")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
DEFAULT_CONCEPTS_PATH = Path(__file__).resolve().parent.parent / "concepts.json"


@dataclass(frozen=True)
class PatternVariant:
    tokens: tuple[str, ...]
    priority: int


@dataclass(frozen=True)
class ConceptPattern:
    name: str
    lookup_name: str
    target: Path
    patterns: tuple[PatternVariant, ...]
    first_tokens: frozenset[str]


@dataclass(frozen=True)
class Match:
    start: int
    end: int
    text: str
    priority: int


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "WEB").exists() and (candidate / "WORK").exists():
            return candidate
    return start.resolve()


def normalize_word(word: str, morph: MorphAnalyzer | None) -> str:
    cleaned = word.replace("Ё", "Е").replace("ё", "е")
    if "-" in cleaned:
        return "-".join(normalize_word(part, morph) for part in cleaned.split("-"))
    if morph is not None and re.search(r"[А-Яа-я]", cleaned):
        parsed = morph.parse(cleaned)[0]
        return parsed.normal_form.replace("ё", "е")
    return cleaned.lower()


def normalize_phrase(phrase: str, morph: MorphAnalyzer | None) -> tuple[str, ...]:
    return tuple(normalize_word(token, morph) for token in WORD_RE.findall(phrase))


def normalize_lookup_value(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("Ё", "Е").replace("ё", "е")).strip().lower()


def is_safe_lemma_phrase(
    phrase: str,
    concept_name_tokens: frozenset[str],
    morph: MorphAnalyzer | None,
) -> tuple[str, ...] | None:
    normalized = normalize_phrase(phrase, morph)
    if not normalized:
        return None
    if any(token in concept_name_tokens for token in normalized):
        return normalized
    return None


def merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []
    spans.sort()
    merged = [spans[0]]
    for start, end in spans[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def blocked_spans(line: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for pattern in (HTML_COMMENT_RE, INLINE_CODE_RE, MARKDOWN_LINK_RE, URL_RE, HTML_TAG_RE):
        spans.extend(match.span() for match in pattern.finditer(line))
    return merge_spans(spans)


def is_span_blocked(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    for span_start, span_end in spans:
        if end <= span_start:
            break
        if start >= span_end:
            continue
        if start < span_end and end > span_start:
            return True
    return False


def is_allowed_token(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    return not is_span_blocked(start, end, spans)


def load_concepts(
    concepts_path: Path,
    repo_root: Path,
    morph: MorphAnalyzer | None,
) -> tuple[list[ConceptPattern], dict[Path, frozenset[str] | None]]:
    raw = json.loads(concepts_path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        if isinstance(raw.get("concepts"), list):
            raw = [raw]
        else:
            raw = [value for value in raw.values() if isinstance(value, dict) and isinstance(value.get("concepts"), list)]

    concepts: list[ConceptPattern] = []
    allowed_targets_by_source: dict[Path, frozenset[str] | None] = {}
    for block in raw if isinstance(raw, list) else []:
        if not isinstance(block, dict):
            continue
        for concept in block.get("concepts", []):
            if not isinstance(concept, dict):
                continue
            file_value = concept.get("file")
            if not file_value:
                continue
            target = (repo_root / file_value).resolve()
            name = str(concept.get("name") or concept.get("label") or concept.get("title") or target.stem)
            lookup_name = normalize_lookup_value(name)
            name_tokens = frozenset(normalize_phrase(name, morph))
            raw_allowed_targets = concept.get("links_from_article")
            allowed_targets = (
                frozenset(
                    normalize_lookup_value(str(item))
                    for item in raw_allowed_targets
                    if isinstance(item, str) and item.strip()
                )
                if isinstance(raw_allowed_targets, list)
                else None
            )
            allowed_targets_by_source[target] = allowed_targets or None

            patterns: list[PatternVariant] = []
            seen: set[tuple[int, tuple[str, ...]]] = set()

            def add_pattern(priority: int, phrase: str, normalized: tuple[str, ...] | None = None) -> None:
                value = normalized if normalized is not None else normalize_phrase(phrase, morph)
                if not value:
                    return
                key = (priority, value)
                if key in seen:
                    return
                seen.add(key)
                patterns.append(PatternVariant(tokens=value, priority=priority))

            add_pattern(0, name)

            for alias in concept.get("aliases", []):
                if isinstance(alias, str) and alias.strip():
                    add_pattern(1, alias)

            for lemma in concept.get("lemmas", []):
                if not isinstance(lemma, str) or not lemma.strip():
                    continue
                safe_lemma = is_safe_lemma_phrase(lemma, name_tokens, morph)
                if safe_lemma is not None:
                    add_pattern(2, lemma, safe_lemma)

            if patterns:
                sorted_patterns = tuple(
                    sorted(patterns, key=lambda item: (item.priority, -len(item.tokens), item.tokens))
                )
                first_tokens = frozenset(pattern.tokens[0] for pattern in sorted_patterns if pattern.tokens)
                concepts.append(
                    ConceptPattern(
                        name=name,
                        lookup_name=lookup_name,
                        target=target,
                        patterns=sorted_patterns,
                        first_tokens=first_tokens,
                    )
                )
    return concepts, allowed_targets_by_source


def iter_markdown_files(paths: list[Path], repo_root: Path, default_files: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    if paths:
        for raw_path in paths:
            path = raw_path if raw_path.is_absolute() else (repo_root / raw_path).resolve()
            if path.is_dir():
                candidates = sorted(path.rglob("*.md"))
            elif path.suffix.lower() == ".md":
                candidates = [path]
            else:
                candidates = []
            for candidate in candidates:
                resolved = candidate.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    files.append(resolved)
    else:
        for candidate in default_files:
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                files.append(resolved)
    return files


def default_article_files(concepts: list[ConceptPattern]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for concept in concepts:
        if concept.target.suffix.lower() != ".md":
            continue
        if concept.target not in seen:
            seen.add(concept.target)
            files.append(concept.target)
    return files


def build_first_token_index(concepts: list[ConceptPattern]) -> dict[str, list[ConceptPattern]]:
    index: dict[str, list[ConceptPattern]] = defaultdict(list)
    for concept in concepts:
        for token in concept.first_tokens:
            index[token].append(concept)
    return index


def tokenize_line(line: str, morph: MorphAnalyzer | None) -> tuple[list[tuple[int, int]], list[tuple[int, int, str]]]:
    blocked = blocked_spans(line)
    tokens: list[tuple[int, int, str]] = []
    for token in WORD_RE.finditer(line):
        start, end = token.span()
        if is_allowed_token(start, end, blocked):
            tokens.append((start, end, normalize_word(token.group(0), morph)))
    return blocked, tokens


def find_candidate_in_tokens(
    line: str,
    tokens: list[tuple[int, int, str]],
    concept: ConceptPattern,
) -> Match | None:
    if not tokens:
        return None

    for start_idx in range(len(tokens)):
        for pattern in concept.patterns:
            length = len(pattern.tokens)
            if start_idx + length > len(tokens):
                continue
            window = tokens[start_idx : start_idx + length]
            if tuple(item[2] for item in window) != pattern.tokens:
                continue
            start = window[0][0]
            end = window[-1][1]
            matched_text = line[start:end]
            return Match(start=start, end=end, text=matched_text, priority=pattern.priority)
    return None


def process_article(
    path: Path,
    concepts_by_first_token: dict[str, list[ConceptPattern]],
    allowed_targets_by_source: dict[Path, frozenset[str] | None],
    morph: MorphAnalyzer | None,
    apply: bool,
) -> tuple[bool, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    source_path = path.resolve()
    allowed_target_names = allowed_targets_by_source.get(source_path)
    in_code_block = False
    footer_index = len(lines)
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("***Автор:"):
            footer_index = index
            break
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block or stripped.startswith("#"):
            continue

    in_code_block = False
    matches: list[tuple[int, Match, ConceptPattern]] = []
    linked_targets: set[Path] = set()
    for line_index in range(footer_index):
        line = lines[line_index]
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block or stripped.startswith("#"):
            continue

        _, tokens = tokenize_line(line, morph)
        if not tokens:
            continue

        candidate_concepts: list[ConceptPattern] = []
        seen_candidates: set[Path] = set()
        for _, _, token in tokens:
            for concept in concepts_by_first_token.get(token, []):
                if concept.target == source_path or concept.target in seen_candidates or concept.target in linked_targets:
                    continue
                if allowed_target_names is not None and concept.lookup_name not in allowed_target_names:
                    continue
                seen_candidates.add(concept.target)
                candidate_concepts.append(concept)

        for concept in candidate_concepts:
            match = find_candidate_in_tokens(line, tokens, concept)
            if match is not None:
                matches.append((line_index, match, concept))
                linked_targets.add(concept.target)

    if not matches:
        return False, []

    chosen: list[tuple[int, Match, ConceptPattern]] = []
    occupied: dict[int, list[tuple[int, int]]] = {}
    for line_index, match, concept in sorted(
        matches,
        key=lambda item: (item[0], item[1].start, item[1].priority, -(item[1].end - item[1].start)),
    ):
        spans = occupied.setdefault(line_index, [])
        if any(match.start < end and match.end > start for start, end in spans):
            continue
        spans.append((match.start, match.end))
        chosen.append((line_index, match, concept))

    if not chosen:
        return False, []

    for line_index, match, concept in sorted(chosen, key=lambda item: (item[0], item[1].start), reverse=True):
        line = lines[line_index]
        href = Path(os.path.relpath(concept.target, start=path.parent)).as_posix()
        replacement = f"[{match.text}]({href})"
        lines[line_index] = line[: match.start] + replacement + line[match.end :]

    changed = "".join(lines)
    if changed != text and apply:
        path.write_text(changed, encoding="utf-8")

    return changed != text, [concept.name for _, _, concept in chosen]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--concepts",
        type=Path,
        default=DEFAULT_CONCEPTS_PATH,
        help="Path to the concepts.json file for this section.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite files in place instead of running in dry-run mode.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Markdown file(s) or directory(ies) to process. If omitted, all article files from concepts.json are used.",
    )
    args = parser.parse_args()

    concepts_path = args.concepts if args.concepts.is_absolute() else args.concepts.resolve()
    repo_root = find_repo_root(concepts_path.parent)
    morph = MorphAnalyzer() if MorphAnalyzer is not None else None
    concepts, allowed_targets_by_source = load_concepts(concepts_path, repo_root, morph)
    concepts_by_first_token = build_first_token_index(concepts)
    files = iter_markdown_files(args.paths, repo_root, default_article_files(concepts))

    if not files:
        print("No Markdown files found.", flush=True)
        return 1

    changed_files: list[Path] = []
    total_links = 0
    for path in files:
        if not path.exists():
            print(f"skip missing: {path}", flush=True)
            continue
        changed, linked_concepts = process_article(
            path,
            concepts_by_first_token,
            allowed_targets_by_source,
            morph,
            args.apply,
        )
        if changed:
            changed_files.append(path)
            total_links += len(linked_concepts)
            print(f"{'updated' if args.apply else 'would update'}: {path} -> {', '.join(linked_concepts)}", flush=True)

    print(
        f"{'applied' if args.apply else 'dry-run'}: {len(changed_files)} file(s), {total_links} link(s)",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
