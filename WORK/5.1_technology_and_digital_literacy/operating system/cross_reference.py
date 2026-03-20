import json
import re
from pathlib import Path
import pymorphy3


BASE_DIR = Path(__file__).resolve().parents[3]
CONCEPTS_FILE = BASE_DIR / "WORK" / "5.1_technology_and_digital_literacy" / "operating system" / "concepts.json"
ARTICLES_DIR = BASE_DIR / "WEB" / "5.1_technology_and_digital_literacy" / "operating system" / "articles"

morph = pymorphy3.MorphAnalyzer()


def load_lemmas_from_concepts(filepath):
    """
    Загружает леммы из concepts.json.
    Возвращает:
    - lemma_map: { {name, file, lemma_position} }
    - concept_files
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    concepts = data.get('concepts', data) if isinstance(data, dict) else data

    lemma_map = {}
    concept_files = {}

    for concept in concepts:
        concept_name = concept.get('name', '')
        concept_file = concept.get('file', '').split('/')[-1]
        lemmas = concept.get('lemmas', [])

        concept_files[concept_file] = concept_name

        flat_lemmas = []
        for item in lemmas:
            if isinstance(item, list):
                flat_lemmas.extend(item)
            else:
                flat_lemmas.append(item)

        for idx, lemma in enumerate(flat_lemmas):
            lemma = lemma.strip().lower()
            if lemma:
                # If the lemmas already exists, we leave the one where the
                # position is earlier (the index is smaller)
                if lemma not in lemma_map:
                    lemma_map[lemma] = {
                        'name': concept_name,
                        'file': concept_file,
                        'lemma_position': idx
                    }
                else:
                    existing_pos = lemma_map[lemma]['lemma_position']
                    if idx < existing_pos:
                        lemma_map[lemma] = {
                            'name': concept_name,
                            'file': concept_file,
                            'lemma_position': idx
                        }
    return lemma_map, concept_files


def tokenize_text(text):
    """
    Разбивает текст на слова, оставляя только буквы (кириллица + латиница).
    Возвращает список слов и их позиций.
    """
    pattern = r'[а-яёa-zA-Z]+'
    tokens = []
    for match in re.finditer(pattern, text.lower()):
        word = match.group()
        pos = match.start()
        tokens.append((word, pos))
    return tokens


def normalize_word(word):
    """
    Нормализует слово с помощью pymorphy3.
    """
    parsed = morph.parse(word)[0]
    return parsed.normal_form


def is_inside_link(pos, length, link_regions):
    """
    Проверяет, попадает ли термин (pos, pos+length) внутрь какой-либо ссылки.
    """
    term_end = pos + length
    for link_start, link_end in link_regions:
        if not (term_end <= link_start or pos >= link_end):
            return True
    return False


def find_terms_in_file(filepath, lemma_map, concept_files):
    """
    Ищет вхождения терминов в файле.
    Исключает вхождения терминов, которые принадлежат этому же файлу.
    ИГНОРИРУЕТ термины внутри markdown-ссылок.
    ГРУППИРУЕТ результаты по статьям: одна статья = одна строка в результатах.
    Возвращает список: [(статья, термин, позиция, оригинал, lemma_position), ...]
    """
    current_file = Path(filepath).stem

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    link_regions = find_link_regions(content)

    tokens = tokenize_text(content)

    normalized_tokens = []
    for word, pos in tokens:
        norm_word = normalize_word(word)
        normalized_tokens.append((norm_word, pos, word))

    # { article file: {name, term, pos, orig} }
    found_articles = {}
    for norm_word, pos, orig_word in normalized_tokens:
        if norm_word in lemma_map:
            term_info = lemma_map[norm_word]
            term_file = term_info['file']

            if Path(term_file).stem == current_file:
                continue

            if is_inside_link(pos, len(orig_word), link_regions):
                continue

            if term_file not in found_articles:
                found_articles[term_file] = {
                    'name': term_info['name'],
                    'term': norm_word,
                    'pos': pos,
                    'orig': orig_word,
                    'lemma_position': term_info['lemma_position']
                }

    results = []
    for article_file, data in found_articles.items():
        results.append((
            data['name'],
            data['term'],
            data['pos'],
            data['orig'],
            data['lemma_position']
        ))

    results.sort(key=lambda x: x[2])
    return results


def scan_articles(articles_dir, lemma_map, concept_files):
    """
    Сканирует все .md файлы в папке статей.
    """
    all_results = {}

    for filepath in sorted(articles_dir.glob('*.md')):
        filename = filepath.name
        found = find_terms_in_file(filepath, lemma_map, concept_files)

        if found:
            all_results[filename] = found

    return all_results


def name_to_filename(name, concept_files):
    """
    Преобразует название статьи в имя файла, используя данные из concepts.json.
    Возвращает имя файла как есть (например, 'IPC.md').
    """
    for filename, concept_name in concept_files.items():
        if concept_name == name:
            return filename
    raise ValueError("concept_name")


def find_link_regions(text):
    """
    Находит все области markdown-ссылок в тексте.
    Возвращает список кортежей (start, end) — начала и концы ссылок.
    """
    regions = []
    # [[текст]] или [[текст|алиас]]
    for match in re.finditer(r'\[\[[^\]]+\]\]', text):
        regions.append((match.start(), match.end()))
    # [текст](url)
    for match in re.finditer(r'\[[^\]]+\]\([^\)]+\)', text):
        regions.append((match.start(), match.end()))
    return regions


def add_links_to_articles(articles_dir, results, concept_files):
    """
    Заменяет вхождения терминов на markdown-ссылки в формате [текст](файл.md).
    При этом для простоты ссылкой на файл служит просто само название файла,
    так как все файлы находятся в одной папке.
    """
    for filename, terms in results.items():
        filepath = articles_dir / filename

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        link_regions = find_link_regions(content)

        replacements = []
        for name, term, pos, orig, lemma_pos in terms:
            if is_inside_link(pos, len(orig), link_regions):
                continue

            target_file = name_to_filename(name, concept_files)
            link_text = orig
            link = f"[{link_text}]({target_file})"
            replacements.append((pos, orig, link))

        replacements.sort(key=lambda x: x[0], reverse=True)

        modified_content = content
        for pos, orig_text, link in replacements:
            modified_content = modified_content[:pos] + link + modified_content[pos + len(orig_text):]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        print(f"✅ Обновлена статья {filename} (добавлено ссылок: {len(replacements)})")


if __name__ == "__main__":
    print(f"📂 Базовая директория: {BASE_DIR}")
    print(f"📄 Файл концептов: {CONCEPTS_FILE}")
    print(f"📁 Папка статей: {ARTICLES_DIR}")
    print("-" * 130)

    if not CONCEPTS_FILE.exists():
        print("❌ Файл concepts.json не найден!")
        exit(1)

    if not ARTICLES_DIR.exists():
        print("❌ Папка articles не найдена!")
        exit(1)

    print("🔄 Загрузка терминов из concepts.json...")
    lemma_map, concept_files = load_lemmas_from_concepts(CONCEPTS_FILE)
    print(f"✅ Загружено терминов для поиска: {len(lemma_map)}")
    print(f"✅ Загружено концептов: {len(concept_files)}")
    print("-" * 130)

    print("🔍 Поиск вхождений в статьях (игнорируя markdown-ссылки)...\n")
    results = scan_articles(ARTICLES_DIR, lemma_map, concept_files)

    print("-" * 130)
    print("🔗 Добавление ссылок в статьи...\n")
    add_links_to_articles(ARTICLES_DIR, results, concept_files)
