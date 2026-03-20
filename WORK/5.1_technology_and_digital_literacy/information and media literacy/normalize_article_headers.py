from pathlib import Path
import re


ARTICLES_DIR = Path(
    "WEB/5.1_technology_and_digital_literacy/information and media literacy/articles"
)
PARENT_TOPIC = "Информационная и медиаграмотность"


def main() -> int:
    updated = 0
    for path in sorted(ARTICLES_DIR.glob("*.md")):
        src = path.read_text(encoding="utf-8")
        lines = src.splitlines()
        if not lines:
            continue

        title_idx = 0
        if not lines[0].startswith("# "):
            title_idx = next((i for i, line in enumerate(lines) if line.startswith("# ")), -1)
            if title_idx < 0:
                continue
        title_line = lines[title_idx]

        wiki_match = re.search(r"\[Wikidata\]\((https?://[^)]+)\)", src)
        wiki_url = wiki_match.group(1) if wiki_match else ""

        image_line = ""
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("![") and "../images/" in stripped and ".png" in stripped:
                image_line = stripped
                break
        if not image_line:
            slug = path.stem
            image_line = (
                f'![Иллюстрация: {slug.replace("_", " ")}]'
                f'(../images/{slug}.png "Иллюстрация к статье")'
            )

        body_start = title_idx + 1
        while body_start < len(lines):
            stripped = lines[body_start].strip()
            if (
                not stripped
                or stripped.startswith("![")
                or stripped.startswith("[Wikidata]")
                or stripped.startswith("**Wiki**")
                or stripped.startswith("**Parent topic**")
            ):
                body_start += 1
                continue
            break

        body = "\n".join(lines[body_start:]).lstrip("\n")
        wiki_line = f"**Wiki** [Wikidata]({wiki_url})  " if wiki_url else "**Wiki**  "
        parent_line = f"**Parent topic** {PARENT_TOPIC}  "

        header = "\n".join(
            [
                title_line,
                "",
                wiki_line,
                parent_line,
                "",
                image_line,
                "",
            ]
        )
        new_text = header + ("\n" + body if body else "\n")
        if not new_text.endswith("\n"):
            new_text += "\n"

        if new_text != src:
            path.write_text(new_text, encoding="utf-8")
            updated += 1

    print(f"updated {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
