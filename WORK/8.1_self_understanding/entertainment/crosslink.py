"""
Скрипт для расстановки перекрёстных ссылок между статьями энциклопедии.

Для каждого markdown-файла в WEB/8.1_entertainment/articles/:
1. Генерирует все падежные формы из ключевых слов (lemmas) через pymorphy3
2. Ищет вхождения этих форм в текстах других статей
3. Заменяет первое вхождение каждого понятия на markdown-ссылку
4. Не заменяет понятие внутри собственной статьи
5. Не заменяет в заголовках (строки с #) и уже существующих ссылках

Использование:
  python crosslink.py
  python crosslink.py --dry-run  # только показать, какие замены будут сделаны
"""

import json
import os
import re
import sys

import pymorphy3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONCEPTS_PATH = os.path.join(SCRIPT_DIR, "concepts.json")
PAGES_DIR = os.path.join(SCRIPT_DIR, "..", "..", "WEB", "8.1_entertainment", "articles")

morph = pymorphy3.MorphAnalyzer()

# Слишком общие леммы, которые дают много ложных ссылок.
# Для "movie" оставляем кино/фильм и отключаем авто-ссылки по "жанр".
BLOCKED_SINGLE_LEMMAS_BY_CONCEPT = {
    "movie": {"жанр"},
}


def load_concepts() -> list[dict]:
    with open(CONCEPTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["concepts"]


def get_word_forms(word: str) -> set[str]:
    """Получить все падежные формы русского слова через pymorphy3."""
    forms = {word.lower()}
    parsed = morph.parse(word)
    if parsed:
        best = parsed[0]
        for form in best.lexeme:
            forms.add(form.word)
    return forms


def build_form_index(
    concepts: list[dict],
) -> list[tuple[str, str, str]]:
    """
    Строит индекс: [(regex_pattern, concept_name, файл), ...]
    Для каждого ключевого слова (lemma) генерирует все падежные формы
    через pymorphy3. Для многословных фраз склоняет каждое слово
    отдельно и собирает комбинированный regex.
    Сортировка по убыванию длины паттерна.
    """
    raw_index: list[tuple[str, str, str, bool, str | None]] = []
    single_form_concepts: dict[str, set[str]] = {}

    for concept in concepts:
        filename = os.path.basename(concept["file"])
        blocked_single = BLOCKED_SINGLE_LEMMAS_BY_CONCEPT.get(concept["name"], set())
        for lemma in concept["lemmas"]:
            words = lemma.strip().split()
            if len(words) == 1:
                if words[0].lower() in blocked_single:
                    continue
                # Однословная лемма — каждая падежная форма отдельно
                forms = get_word_forms(words[0])
                for form in forms:
                    pattern = re.escape(form)
                    normalized = form.lower()
                    single_form_concepts.setdefault(normalized, set()).add(
                        concept["name"]
                    )
                    raw_index.append(
                        (pattern, concept["name"], filename, True, normalized)
                    )
            else:
                # Многословная фраза — склоняем каждое слово,
                # собираем regex вида (форма1|форма2)\s+(форма1|форма2)
                parts = []
                for w in words:
                    forms = get_word_forms(w)
                    escaped = [
                        re.escape(f) for f in sorted(forms, key=lambda x: -len(x))
                    ]
                    parts.append("(?:" + "|".join(escaped) + ")")
                pattern = r"\s+".join(parts)
                raw_index.append((pattern, concept["name"], filename, False, None))

    index: list[tuple[str, str, str]] = []
    for pattern, concept_id, filename, is_single_form, normalized_form in raw_index:
        # Исключаем неоднозначные однословные формы, которые встречаются
        # сразу у нескольких понятий (например, "кадров").
        if is_single_form and normalized_form is not None:
            if len(single_form_concepts.get(normalized_form, set())) > 1:
                continue
        index.append((pattern, concept_id, filename))

    # Длинные паттерны первыми — чтобы "образовательная игра" матчилась раньше "игра"
    index.sort(key=lambda x: -len(x[0]))
    return index


def build_link_pattern(form_pattern: str) -> re.Pattern:
    """Собрать regex для безопасного поиска формы вне markdown-ссылок."""
    return re.compile(
        r"(?<!\[)(?<!\()"  # не внутри существующей ссылки
        r"\b(" + form_pattern + r")\b"
        r"(?!\]|\))",  # не внутри существующей ссылки
        re.IGNORECASE,
    )


def build_self_word_forms_index(concepts: list[dict]) -> dict[str, set[str]]:
    """Собрать словоформы отдельных слов из лемм для каждого понятия."""
    index: dict[str, set[str]] = {}
    for concept in concepts:
        forms_for_concept: set[str] = set()
        for lemma in concept["lemmas"]:
            for word in lemma.strip().split():
                forms_for_concept.update(get_word_forms(word))
        index[concept["name"]] = forms_for_concept
    return index


def ranges_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)


def get_protected_ranges(
    line: str,
    current_concept_id: str,
    form_index: list,
    self_word_forms_index: dict[str, set[str]],
) -> list[tuple[int, int]]:
    """
    Найти диапазоны в строке, относящиеся к текущему понятию.
    Внутри них нельзя ставить ссылки на другие статьи.
    """
    ranges = []
    for form_pattern, concept_id, _ in form_index:
        if concept_id != current_concept_id:
            continue
        pattern = build_link_pattern(form_pattern)
        for match in pattern.finditer(line):
            ranges.append((match.start(1), match.end(1)))

    # Дополнительно защищаем отдельные слова из лемм текущего понятия,
    # чтобы "Жанры [музыки]" не перекидывало на movie из-за "жанр".
    for form in self_word_forms_index.get(current_concept_id, set()):
        pattern = build_link_pattern(re.escape(form))
        for match in pattern.finditer(line):
            ranges.append((match.start(1), match.end(1)))
    return ranges


def add_crosslinks(
    text: str,
    current_concept_id: str,
    form_index: list,
    self_word_forms_index: dict[str, set[str]],
) -> tuple[str, list[str]]:
    """
    Расставляет ссылки в тексте. Возвращает (новый_текст, список_замен).
    """
    lines = text.split("\n")
    linked_concepts = set()  # понятия, на которые уже поставлена ссылка
    changes = []

    for line_idx, line in enumerate(lines):
        # Пропускаем заголовки
        if line.strip().startswith("#"):
            continue
        # Пропускаем пустые строки
        if not line.strip():
            continue

        for form_pattern, concept_id, filename in form_index:
            # Не ставим ссылку на самого себя
            if concept_id == current_concept_id:
                continue
            # Уже поставили ссылку на это понятие
            if concept_id in linked_concepts:
                continue

            # Ищем форму слова (с границами слов, регистронезависимо)
            # и не трогаем фрагменты, принадлежащие текущей статье.
            pattern = build_link_pattern(form_pattern)
            protected_ranges = get_protected_ranges(
                lines[line_idx],
                current_concept_id,
                form_index,
                self_word_forms_index,
            )

            match = None
            for candidate in pattern.finditer(lines[line_idx]):
                c_start = candidate.start(1)
                c_end = candidate.end(1)
                intersects_self = any(
                    ranges_overlap(c_start, c_end, p_start, p_end)
                    for p_start, p_end in protected_ranges
                )
                if not intersects_self:
                    match = candidate
                    break

            if match:
                original_text = match.group(1)
                replacement = f"[{original_text}]({filename})"
                # Заменяем только первое вхождение в этой строке
                lines[line_idx] = (
                    lines[line_idx][: match.start()]
                    + replacement
                    + lines[line_idx][match.end() :]
                )
                linked_concepts.add(concept_id)
                changes.append(f"  '{original_text}' -> [{original_text}]({filename})")

    return "\n".join(lines), changes


def find_concept_by_file(concepts: list[dict], filename: str) -> dict | None:
    for c in concepts:
        if os.path.basename(c["file"]) == filename:
            return c
    return None


def main():
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(PAGES_DIR):
        print(f"Ошибка: директория {PAGES_DIR} не найдена.")
        print("Сначала запустите generate_pages.py")
        sys.exit(1)

    concepts = load_concepts()
    form_index = build_form_index(concepts)
    self_word_forms_index = build_self_word_forms_index(concepts)

    print(f"Загружено {len(concepts)} понятий, {len(form_index)} падежных форм")
    print(f"Директория статей: {PAGES_DIR}")
    if dry_run:
        print("Режим: dry-run (без записи файлов)\n")
    else:
        print()

    total_changes = 0

    md_files = [
        f for f in os.listdir(PAGES_DIR) if f.endswith(".md") and f != "index.md"
    ]

    for filename in sorted(md_files):
        filepath = os.path.join(PAGES_DIR, filename)
        concept = find_concept_by_file(concepts, filename)

        if not concept:
            print(f"WARN {filename}: не найдено в concepts.json, пропускаю")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            original_text = f.read()

        new_text, changes = add_crosslinks(
            original_text,
            concept["name"],
            form_index,
            self_word_forms_index,
        )

        if changes:
            print(f"EDIT {filename} ({concept['name']}): {len(changes)} ссылок")
            for change in changes:
                print(change)

            if not dry_run:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_text)

            total_changes += len(changes)
        else:
            print(f"  {filename}: без изменений")

    print(
        f"\nИтого: {total_changes} перекрёстных ссылок {'(dry-run)' if dry_run else 'расставлено'}"
    )


if __name__ == "__main__":
    main()
