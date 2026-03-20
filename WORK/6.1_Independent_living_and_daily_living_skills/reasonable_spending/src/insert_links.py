import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONCEPTS_PATH = ROOT / "WORK" / "6.1_reasonable_spending" / "concepts.json"
PAGES_DIR = ROOT / "WEB" / "6.1_reasonable_spending" / "articles"


def load_concepts():
    data = json.loads(CONCEPTS_PATH.read_text(encoding="utf-8"))
    concepts = []
    for c in data["concepts"]:
        article_name = Path(c["file"]).name
        concepts.append(
            {
                "name": c["name"],
                "file": article_name,
                "aliases": sorted(c["aliases"], key=len, reverse=True),
            }
        )
    return concepts


def is_inside_markdown_link(line: str, start: int, end: int) -> bool:
    before = line[:start]
    after = line[end:]
    open_bracket = before.rfind("[")
    close_bracket = before.rfind("]")
    open_paren_after = after.find("(")
    close_paren_after = after.find(")")

    if open_bracket != -1 and (close_bracket == -1 or open_bracket > close_bracket):
        if open_paren_after != -1 and close_paren_after != -1 and open_paren_after < close_paren_after:
            return True
    return False


def link_line(line: str, current_file: str, concepts):
    # Do not modify headings.
    if line.lstrip().startswith("#"):
        return line

    for concept in concepts:
        concept_file = concept["file"]
        target = f"./{concept_file}"
        if concept_file == current_file:
            continue

        for alias in concept["aliases"]:
            pattern = rf"(?<![\w\]])({re.escape(alias)})(?![\w\[])"
            while True:
                match = re.search(pattern, line, flags=re.IGNORECASE)
                if not match:
                    break

                start, end = match.span(1)
                if is_inside_markdown_link(line, start, end):
                    # Skip and continue search after this match.
                    next_pos = end
                    tail = line[next_pos:]
                    next_match = re.search(pattern, tail, flags=re.IGNORECASE)
                    if not next_match:
                        break
                    abs_start = next_pos + next_match.start(1)
                    abs_end = next_pos + next_match.end(1)
                    found = line[abs_start:abs_end]
                    link = f"[{found}]({target})"
                    line = line[:abs_start] + link + line[abs_end:]
                    continue

                found = line[start:end]
                link = f"[{found}]({target})"
                line = line[:start] + link + line[end:]
                break
    return line


def process_file(path: Path, concepts):
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines(keepends=True)
    linked = []
    for line in lines:
        linked.append(link_line(line, path.name, concepts))
    updated = "".join(linked)
    path.write_text(updated, encoding="utf-8")


def main():
    concepts = load_concepts()
    files = sorted(PAGES_DIR.glob("*.md"))
    for file in files:
        process_file(file, concepts)
    print(f"Processed {len(files)} files in {PAGES_DIR}")


if __name__ == "__main__":
    main()
