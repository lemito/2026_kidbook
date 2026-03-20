#!/usr/bin/env python3
"""
Расстановка перекрёстных ссылок между статьями раздела «Наука».

Зависимости: pip install pymorphy3
"""

import json
import re
import sys
from pathlib import Path

try:
    import pymorphy3
    morph = pymorphy3.MorphAnalyzer()
    USE_MORPH = True
except ImportError:
    USE_MORPH = False
    print("pymorphy3 не установлен — ссылки только для словарной формы.", file=sys.stderr)

_STOP_TOKENS = {"в", "на", "об", "о", "по", "из", "к", "у", "за", "под",
                "над", "с", "и", "или", "а", "но", "же", "то"}

_CASES   = ("nomn", "gent", "datv", "accs", "ablt", "loct")
_NUMBERS = ("sing", "plur")


def _inflect_token(token: str, case: str, number: str) -> str | None:
    """Склонить одно слово в заданный падеж и число."""
    variants = morph.parse(token)
    if not variants:
        return None
    p = variants[0]
    tags = {case, number}
    result = p.inflect(tags)
    if result is None:
        # попробуем без числа
        result = p.inflect({case})
    return result.word if result else None


def phrase_forms(phrase: str) -> set[str]:
    """Вернуть набор всех словоформ для фразы (с учётом падежей и числа)."""
    tokens = phrase.split()

    if len(tokens) == 1:
        if not USE_MORPH:
            return {phrase.lower()}
        p = morph.parse(tokens[0])
        if not p:
            return {phrase.lower()}
        return {f.word for f in p[0].lexeme}

    if not USE_MORPH:
        return {phrase.lower()}

    results: set[str] = set()
    for case in _CASES:
        for number in _NUMBERS:
            form_tokens = []
            ok = True
            for tok in tokens:
                if tok.lower() in _STOP_TOKENS:
                    form_tokens.append(tok.lower())
                else:
                    inflected = _inflect_token(tok, case, number)
                    if inflected is None:
                        ok = False
                        break
                    form_tokens.append(inflected)
            if ok:
                results.add(" ".join(form_tokens))

    results.add(phrase.lower())
    return results


def build_forms_map(concepts: list[dict]) -> dict[str, dict]:
    """Построить словарь {форма -> concept_dict}. Длинные формы приоритетнее."""
    forms_map: dict[str, dict] = {}
    for concept in concepts:
        for form in phrase_forms(concept["ru"]):
            existing = forms_map.get(form)
            if existing is None or len(concept["ru"]) > len(existing["ru"]):
                forms_map[form] = concept
    return forms_map


_LINK_RE = re.compile(r'\[([^\]]+)\]\([^)]+\)')


def _inside_existing_link(text: str, start: int) -> bool:
    for m in _LINK_RE.finditer(text):
        if m.start() <= start < m.end():
            return True
    return False


def apply_links(text: str, forms_map: dict[str, dict], self_id: str) -> str:
    """Заменить первое вхождение каждого понятия (кроме self_id) на ссылку."""
    linked_ids: set[str] = set()
    sorted_forms = sorted(forms_map.keys(), key=len, reverse=True)

    for form in sorted_forms:
        concept = forms_map[form]
        if concept["id"] == self_id or concept["id"] in linked_ids:
            continue

        pattern = re.compile(
            r'(?<!\w)' + re.escape(form) + r'(?!\w)',
            flags=re.IGNORECASE,
        )
        match = pattern.search(text)
        if not match:
            continue
        if _inside_existing_link(text, match.start()):
            continue

        original = match.group(0)
        replacement = f'[{original}]({concept["id"]}.md)'
        text = text[: match.start()] + replacement + text[match.end() :]
        linked_ids.add(concept["id"])

    return text


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    concepts_path = repo_root / "WORK" / "1.2_natural_sciences" / "why_science_help_understand_world" / "concepts.json"
    web_dir = repo_root / "WEB" / "1.2_natural_sciences" / "why_science_help_understand_world"

    if not concepts_path.exists():
        sys.exit(f"Не найден файл понятий: {concepts_path}")
    if not web_dir.is_dir():
        sys.exit(f"Директория статей не существует: {web_dir}")

    with open(concepts_path, encoding="utf-8") as f:
        data = json.load(f)

    concepts: list[dict] = data["concepts"]
    forms_map = build_forms_map(concepts)
    print(f"Загружено понятий: {len(concepts)}, форм: {len(forms_map)}\n")

    changed = 0
    for concept in concepts:
        filepath = web_dir / (concept["id"] + ".md")
        if not filepath.exists():
            print(f"  [!] Не найден файл: {filepath.name}")
            continue

        original = filepath.read_text(encoding="utf-8")
        updated = apply_links(original, forms_map, concept["id"])

        if updated != original:
            filepath.write_text(updated, encoding="utf-8")
            print(f"  [+] Обновлён:   {filepath.name}")
            changed += 1
        else:
            print(f"  [ ] Без изменений: {filepath.name}")

    print(f"\nГотово. Обновлено {changed} из {len(concepts)} файлов.")


if __name__ == "__main__":
    main()
