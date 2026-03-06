import os
import json
import re

try:
    import pymorphy3 as pymorphy
    MORPHY_VERSION = 3
except ImportError:
    try:
        import pymorphy2 as pymorphy
        MORPHY_VERSION = 2
    except ImportError:
        pymorphy = None
        MORPHY_VERSION = 0


def load_concepts(concepts_file):
    with open(concepts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    concepts_map = {}
    for c in data['concepts']:
        label_lower = c['label'].lower()
        concepts_map[label_lower] = {
            'link': f"./{c['id']}.md",
            'title': c['label'],
            'id': c['id']
        }
        if pymorphy:
            try:
                morph = pymorphy.MorphAnalyzer()
                parse = morph.parse(c['label'])[0]
                for form in parse.lexeme:
                    form_lower = form.word.lower()
                    if form_lower != label_lower and len(form_lower) > 2:
                        concepts_map[form_lower] = {
                            'link': f"./{c['id']}.md",
                            'title': c['label'],
                            'id': c['id']
                        }
            except Exception as e:
                print(f"  ⚠️ Морфология для '{c['label']}': {e}")
    return concepts_map


def escape_existing_links(text):
    """Заменяет все существующие Markdown-ссылки вида [text](url) на временные маркеры."""
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = []
    def repl(match):
        links.append(match.group(0))
        return f"@@LINK_{len(links)-1}@@"
    text = re.sub(link_pattern, repl, text)
    return text, links


def restore_existing_links(text, links):
    """Возвращает маркеры обратно в исходные ссылки."""
    for i, link in enumerate(links):
        text = text.replace(f"@@LINK_{i}@@", link)
    return text


def normalize_paths(text):
    """Исправляет ошибки в путях: .// → ./, ././ → ./"""
    text = re.sub(r'\.//', './', text)
    text = re.sub(r'\./\./', './', text)
    return text


def insert_links(text, concepts):
    """Вставляет ссылки на понятия, избегая конфликтов с уже существующими."""
    # Шаг 1: экранируем существующие ссылки
    text, original_links = escape_existing_links(text)

    # Шаг 2: сортируем ключи по убыванию длины (сначала длинные фразы)
    sorted_keys = sorted(concepts.keys(), key=len, reverse=True)

    # Словарь для временных маркеров, которые заменят вхождения ключей
    phrase_markers = {}
    marker_counter = 0

    # Шаг 3: заменяем каждое вхождение ключа на уникальный маркер
    for key in sorted_keys:
        escaped_key = re.escape(key)
        pattern = r'\b' + escaped_key + r'\b'

        def create_marker(match):
            nonlocal marker_counter
            matched_text = match.group(0)
            marker = f"@@PHRASE_{marker_counter}@@"
            # Сохраняем, какой ссылке соответствует маркер
            phrase_markers[marker] = f"[{matched_text}]({concepts[key]['link']})"
            marker_counter += 1
            return marker

        text = re.sub(pattern, create_marker, text, flags=re.IGNORECASE)

    # Шаг 4: восстанавливаем исходные ссылки
    text = restore_existing_links(text, original_links)

    # Шаг 5: заменяем маркеры на готовые Markdown-ссылки
    for marker, link in phrase_markers.items():
        text = text.replace(marker, link)

    # Шаг 6: нормализуем пути
    text = normalize_paths(text)
    return text


def main():
    concepts_file = '../concepts.json'
    articles_dir = '../../../WEB/14_team/rights_and_responsibilities/articles'

    if not os.path.exists(concepts_file):
        print(f"❌ Файл {concepts_file} не найден!")
        return

    if not os.path.exists(articles_dir):
        print(f"❌ Папка {articles_dir} не найдена!")
        print("   Сначала запустите generate_content.py")
        return

    print("=" * 60)
    print("🔗 Расстановка перекрёстных ссылок")
    print("=" * 60)

    if pymorphy:
        print(f"  ✅ Морфология: pymorphy{MORPHY_VERSION}")
    else:
        print(f"  ⚠️ Морфология: отключена (базовый поиск)")

    concepts = load_concepts(concepts_file)
    print(f"  Загружено форм слов: {len(concepts)}")

    processed = 0
    total_links = 0

    for filename in sorted(os.listdir(articles_dir)):
        if filename.endswith('.md'):
            filepath = os.path.join(articles_dir, filename)

            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()

            original_links = original_content.count('](')
            new_content = insert_links(original_content, concepts)
            new_links = new_content.count('](')
            added_links = new_links - original_links

            if added_links != 0 or new_content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)

            processed += 1
            total_links += added_links
            status = f"+{added_links}" if added_links > 0 else "0"
            print(f"  [{processed}] {filename}: {status} ссылок")

    print()
    print("=" * 60)
    print(f"✅ Готово!")
    print(f"  Файлов обработано: {processed}")
    print(f"  Ссылок добавлено: {total_links}")
    print("=" * 60)


if __name__ == "__main__":
    main()