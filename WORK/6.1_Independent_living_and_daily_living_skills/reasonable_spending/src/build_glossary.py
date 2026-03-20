import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONCEPTS_PATH = ROOT / "WORK" / "6.1_reasonable_spending" / "concepts.json"
OUTPUT_PATH = ROOT / "WEB" / "6.1_reasonable_spending" / "glossary.md"


def main():
    data = json.loads(CONCEPTS_PATH.read_text(encoding="utf-8"))
    concepts = sorted(data["concepts"], key=lambda c: c["name"].lower())

    lines = [
        "# Словарь терминов: разумные траты",
        "",
        "Алфавитный список терминов раздела 6.1.",
        "",
    ]

    for c in concepts:
        article_name = Path(c["file"]).name
        lines.append(f"- [{c['name']}](./articles/{article_name})")

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Glossary created: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
