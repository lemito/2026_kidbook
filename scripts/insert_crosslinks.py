#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple

IGNORE_DIRS = {
    ".git", ".github", "__pycache__", ".venv", "venv", "node_modules"
}

MD_EXTENSIONS = {".md", ".markdown"}

PROTECTED_RE = re.compile(
    r"(```.*?```|`[^`\n]*`|\[[^\]]+\]\([^)]+\))",
    re.DOTALL
)


@dataclass
class Concept:
    name: str
    file_path: Path
    lemmas: List[str] = field(default_factory=list)
    concept_id: str = ""
    source_json: Path = None

    def aliases(self) -> List[str]:
        vals = []

        if self.name:
            vals.append(self.name.strip())

        for lemma in self.lemmas:
            if isinstance(lemma, str) and lemma.strip():
                vals.append(lemma.strip())

        unique = []
        seen = set()
        for v in vals:
            key = v.lower()
            if key not in seen:
                seen.add(key)
                unique.append(v)

        unique.sort(key=lambda s: (-len(s), s.lower()))
        return unique


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for p in [start] + list(start.parents):
        if (p / ".git").exists():
            return p
    return start


def iter_files(root: Path):
    for p in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        yield p


def is_markdown_file(path: Path) -> bool:
    return path.suffix.lower() in MD_EXTENSIONS


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_concepts_json(path: Path, repo_root: Path) -> List[Concept]:
    data = load_json(path)
    result: List[Concept] = []

    if not isinstance(data, list):
        print(f"[WARN] {path}: expected list in root")
        return result

    for block in data:
        if not isinstance(block, dict):
            continue

        concepts = block.get("concepts", [])
        if not isinstance(concepts, list):
            continue

        for item in concepts:
            if not isinstance(item, dict):
                continue

            name = item.get("name")
            file_rel = item.get("file")
            lemmas = item.get("lemmas", [])
            concept_id = item.get("id", "")

            if not name or not file_rel:
                continue

            if not isinstance(lemmas, list):
                lemmas = []

            abs_file = (repo_root / file_rel).resolve()

            if not abs_file.exists():
                print(f"[WARN] file not found for concept '{name}': {file_rel}")
                continue

            result.append(
                Concept(
                    name=name,
                    file_path=abs_file,
                    lemmas=lemmas,
                    concept_id=concept_id,
                    source_json=path
                )
            )

    return result


def collect_all_concepts(repo_root: Path) -> List[Concept]:
    concepts = []
    for p in iter_files(repo_root):
        if p.is_file() and p.name == "concepts.json":
            if p.resolve() == (repo_root / "TUTORIAL" / "concepts.json").resolve():
                print(f"[INFO] skipped file: {p}")
                continue
            try:
                concepts.extend(parse_concepts_json(p, repo_root))
            except Exception as e:
                print(f"[WARN] failed to parse {p}: {e}")

    unique = []
    seen = set()
    for c in concepts:
        key = (c.name.lower(), str(c.file_path))
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique


def split_protected(text: str):
    parts = []
    last = 0
    for m in PROTECTED_RE.finditer(text):
        if m.start() > last:
            parts.append((False, text[last:m.start()]))
        parts.append((True, m.group(0)))
        last = m.end()
    if last < len(text):
        parts.append((False, text[last:]))
    return parts


def make_relative_link(from_file: Path, to_file: Path) -> str:
    rel = Path(__import__("os").path.relpath(to_file, start=from_file.parent))
    return str(rel).replace("\\", "/")


def build_alias_map(concepts: List[Concept]) -> List[Tuple[str, Concept]]:
    alias_map = []
    seen = set()

    for c in concepts:
        for alias in c.aliases():
            key = (alias.lower(), str(c.file_path))
            if key not in seen:
                seen.add(key)
                alias_map.append((alias, c))

    alias_map.sort(key=lambda x: (-len(x[0]), x[0].lower()))
    return alias_map


def alias_pattern(alias: str) -> re.Pattern:
    escaped = re.escape(alias)
    return re.compile(
        rf"(?<![\wа-яА-ЯёЁ-])({escaped})(?![\wа-яА-ЯёЁ-])",
        flags=re.IGNORECASE
    )


def insert_links_in_text(text: str, current_file: Path, alias_map: List[Tuple[str, Concept]]) -> Tuple[str, int]:
    parts = split_protected(text)
    total_inserted = 0
    used_targets = set()
    rebuilt = []

    for protected, chunk in parts:
        if protected:
            rebuilt.append(chunk)
            continue

        new_chunk = chunk

        for alias, concept in alias_map:
            if concept.file_path.resolve() == current_file.resolve():
                continue

            target_key = str(concept.file_path.resolve())
            if target_key in used_targets:
                continue

            pattern = alias_pattern(alias)
            rel_link = make_relative_link(current_file, concept.file_path)

            def repl(match: re.Match) -> str:
                txt = match.group(1)
                return f"[{txt}]({rel_link})"

            replaced, n = pattern.subn(repl, new_chunk, count=1)
            if n > 0:
                new_chunk = replaced
                total_inserted += n
                used_targets.add(target_key)

        rebuilt.append(new_chunk)

    return "".join(rebuilt), total_inserted


def process_markdown_file(md_file: Path, alias_map: List[Tuple[str, Concept]], dry_run: bool = False) -> int:
    original = md_file.read_text(encoding="utf-8")
    updated, inserted = insert_links_in_text(original, md_file, alias_map)

    if inserted > 0 and not dry_run:
        md_file.write_text(updated, encoding="utf-8")

    return inserted


def find_markdown_files(repo_root: Path) -> List[Path]:
    files = []
    for p in iter_files(repo_root):
        if p.is_file() and is_markdown_file(p):
            files.append(p)
    return files


def main():
    args = sys.argv[1:]

    dry_run = "--dry-run" in args
    root_arg = "."
    for a in args:
        if not a.startswith("--"):
            root_arg = a
            break

    repo_root = find_repo_root(Path(root_arg))
    print(f"[INFO] repo root: {repo_root}")

    concepts = collect_all_concepts(repo_root)
    print(f"[INFO] concepts loaded: {len(concepts)}")

    if not concepts:
        print("[ERROR] concepts not found")
        sys.exit(1)

    alias_map = build_alias_map(concepts)
    print(f"[INFO] aliases loaded: {len(alias_map)}")

    md_files = find_markdown_files(repo_root)
    print(f"[INFO] markdown files found: {len(md_files)}")

    changed = 0
    total_links = 0

    for md in md_files:
        inserted = process_markdown_file(md, alias_map, dry_run=dry_run)
        if inserted > 0:
            changed += 1
            total_links += inserted
            print(f"[OK] {md.relative_to(repo_root)} -> inserted: {inserted}")

    print("-" * 50)
    if dry_run:
        print("[DONE] dry run completed")
    else:
        print("[DONE] files updated")

    print(f"[DONE] changed files: {changed}")
    print(f"[DONE] inserted links: {total_links}")


if __name__ == "__main__":
    main()
