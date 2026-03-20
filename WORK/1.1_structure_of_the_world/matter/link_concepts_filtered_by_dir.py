import os
import json
import re
import pymorphy2
import urllib.parse
from difflib import unified_diff

# --- Configuration ---
# Базовая директория проекта
BASE_DIR = "/Users/kirill/2026_kidbook"
# Директория, где искать все файлы concepts.json (сканируем весь WORK_DIR)
WORK_DIR = os.path.join(BASE_DIR, "WORK")
# Директория, где искать все Markdown-файлы (сканируем весь WEB_DIR)
WEB_DIR = os.path.join(BASE_DIR, "WEB")
# Конкретная директория, Markdown-файлы из которой МОЖНО ИЗМЕНЯТЬ
# Файлы из других директорий будут просканированы, но не изменены.
TARGET_MODIFICATION_DIR = os.path.join(BASE_DIR, "WEB", "1.1_structure_of_the_world", "matter", "articles")

# --- Global Morph Analyzer ---
# Инициализируем pymorphy2.MorphAnalyzer один раз для повышения производительности
morph = pymorphy2.MorphAnalyzer()

# --- Helper Functions ---
def get_section_topic_from_path(file_path, base_dir_type):
    """
    Извлекает часть 'section/topic' из пути к файлу.
    Например, для WEB/2.1_society/rights_and_responsibilities/articles/duty_study.md
    вернет "2.1_society/rights_and_responsibilities"
    """
    if base_dir_type == 'WEB':
        relative_path = os.path.relpath(file_path, WEB_DIR)
        parts = relative_path.split(os.sep)
        try:
            # Предполагаем, что статьи всегда находятся в подпапке 'articles'
            articles_idx = parts.index('articles')
            return os.path.join(*parts[:articles_idx])
        except ValueError:
            # Если папка 'articles' не найдена, предполагаем, что тема - это родительская папка файла
            return os.path.join(*parts[:-1])
    elif base_dir_type == 'WORK':
        relative_path = os.path.relpath(file_path, WORK_DIR)
        parts = relative_path.split(os.sep)
        # Предполагаем структуру WORK: section/topic/raw_data/concepts.json или section/topic/concepts.json
        # Берем первые две части пути после WORK_DIR
        if len(parts) >= 2:
            return os.path.join(parts[0], parts[1])
        elif len(parts) == 1 and parts[0].endswith('.json'): # Если concepts.json прямо в WORK/section/concepts.json
            return parts[0].replace('/concepts.json', '')
    return None

def lemmatize_phrase(phrase):
    """
    Лемматизирует данную фразу (строку), лемматизируя каждое слово в ней.
    Возвращает лемматизированную фразу как одну строку со словами, разделенными пробелами.
    """
    # Извлекаем только слова, игнорируя пунктуацию, и приводим к нижнему регистру
    words = re.findall(r'\b\w+\b', phrase.lower())
    lemmas = [morph.parse(word)[0].normal_form for word in words]
    return ' '.join(lemmas)

def load_concepts(work_dir):
    """
    Сканирует work_dir на наличие файлов concepts.json, парсит их и строит карту
    лемматизированных фраз к информации о понятии.
    """
    # concept_data: {лемматизированная_фраза: {'id': ..., 'name': ..., 'file': ..., 'section_topic': ..., 'raw_forms': set()}}
    concept_data = {} 
    # all_lemmas_for_matching: Список лемматизированных фраз (однословных или многословных) для сортировки
    all_lemmas_for_matching = [] 

    for root, _, files in os.walk(work_dir):
        if 'concepts.json' in files:
            json_path = os.path.join(root, 'concepts.json')
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    concepts_list = []
                    # Обработка разных структур concepts.json (список словарей или один словарь)
                    if isinstance(data, list): 
                        if data and 'concepts' in data[0]:
                            concepts_list = data[0]['concepts']
                    elif isinstance(data, dict): 
                        if 'concepts' in data:
                            concepts_list = data['concepts']
                    
                    if not concepts_list:
                        continue

                    # section_topic для концептов из этого файла concepts.json
                    # Например, для WORK/1.1_structure_of_the_world/matter/concepts.json
                    # хотим получить "1.1_structure_of_the_world/matter"
                    relative_json_path_from_work_root = os.path.relpath(json_path, work_dir)
                    # Удаляем 'concepts.json' и 'raw_data/' если есть
                    concept_section_topic = os.path.dirname(relative_json_path_from_work_root)
                    if concept_section_topic.endswith('raw_data'):
                        concept_section_topic = os.path.dirname(concept_section_topic)
                    
                    if not concept_section_topic:
                        print(f"Warning: Could not determine section_topic for {json_path}. Skipping concepts from this file.")
                        continue

                    for concept in concepts_list:
                        concept_id = concept.get('id')
                        concept_name = concept.get('name')
                        md_file_rel_path = concept.get('file')
                        # Проверяем наличие всех необходимых полей для создания ссылки
                        if not (concept_id and concept_name and md_file_rel_path):
                            # print(f"Debug: Skipping concept '{concept_name}' from {json_path} due to missing 'id', 'name', or 'file'.")
                            continue

                        md_file_abs_path = os.path.join(BASE_DIR, md_file_rel_path)
                        # Дополнительная проверка: существует ли файл, на который ссылается понятие
                        if not os.path.exists(md_file_abs_path):
                            print(f"Warning: Concept '{concept_name}' in {json_path} points to non-existent file: {md_file_abs_path}. Skipping this concept for linking.")
                            continue

                        # Собираем все исходные формы (название понятия и его леммы)
                        raw_forms_to_process = {concept_name}
                        raw_forms_to_process.update(concept.get('lemmas', []))

                        md_file_abs_path = os.path.join(BASE_DIR, md_file_rel_path)

                        # Собираем все исходные формы (название понятия и его леммы)
                        raw_forms_to_process = {concept_name}
                        raw_forms_to_process.update(concept.get('lemmas', []))
                        
                        for raw_form in raw_forms_to_process:
                            lemmatized_form = lemmatize_phrase(raw_form)
                            if lemmatized_form: # Убеждаемся, что после лемматизации строка не пуста
                                if lemmatized_form not in concept_data:
                                    concept_data[lemmatized_form] = {
                                        'id': concept_id,
                                        'name': concept_name,
                                        'file': md_file_abs_path,
                                        'section_topic': concept_section_topic,
                                        'raw_forms': set() # Храним все исходные формы, которые соответствуют этой лемматизированной форме
                                    }
                                concept_data[lemmatized_form]['raw_forms'].add(raw_form)
                                all_lemmas_for_matching.append(lemmatized_form)

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {json_path}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {json_path}: {e}")

    # Сортируем уникальные лемматизированные фразы по длине в порядке убывания,
    # чтобы сначала обрабатывались более длинные совпадения (например, "обязанность учиться" до "учиться")
    all_lemmas_for_matching = sorted(list(set(all_lemmas_for_matching)), key=len, reverse=True)
    return concept_data, all_lemmas_for_matching

def process_markdown_file(md_file_path, concept_data, all_lemmas_for_matching):
    """
    Обрабатывает один Markdown-файл для добавления перекрестных ссылок.
    """
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Находим области, которые нужно пропустить: существующие ссылки, блоки кода, инлайн-код
        skip_regions = []
        # Блоки кода (```...```)
        for m in re.finditer(r'```.*?```', original_content, re.DOTALL):
            skip_regions.append(m.span())
        # Инлайн-код (`...`)
        for m in re.finditer(r'`[^`\n]*`', original_content):
            skip_regions.append(m.span())
        # Существующие Markdown-ссылки (текст)
        for m in re.finditer(r'\[[^\]]+\]\([^)]+\)', original_content):
            skip_regions.append(m.span())
        
        # Сортируем и объединяем перекрывающиеся области пропуска
        skip_regions.sort()
        merged_skip_regions = []
        if skip_regions:
            current_start, current_end = skip_regions[0]
            for i in range(1, len(skip_regions)):
                next_start, next_end = skip_regions[i]
                if next_start <= current_end: # Перекрытие или касание
                    current_end = max(current_end, next_end)
                else:
                    merged_skip_regions.append((current_start, current_end))
                    current_start, current_end = next_start, next_end
            merged_skip_regions.append((current_start, current_end))
        skip_regions = merged_skip_regions

        replacements = [] # Список (начало, конец, строка_замены)
        linked_spans = [] # Список (начало, конец) уже связанных областей (этим скриптом)

        # Токенизируем содержимое на слова и не-слова, сохраняя исходный текст и диапазоны
        tokens_with_spans = []
        for match in re.finditer(r'(\b\w+\b|[^\w\s]|\s+)', original_content):
            tokens_with_spans.append({
                'text': match.group(0),
                'start': match.start(),
                'end': match.end(),
                'is_word': bool(re.match(r'\b\w+\b', match.group(0)))
            })

        # Строим список лемматизированных слов и их исходных форм/диапазонов
        lemmatized_words_info = [] # [{'lemma': 'слово', 'original': 'Слова', 'start': 0, 'end': 5, 'token_idx': 0}]
        for idx, token in enumerate(tokens_with_spans):
            if token['is_word']:
                lemmatized_words_info.append({
                    'lemma': morph.parse(token['text'].lower())[0].normal_form,
                    'original': token['text'],
                    'start': token['start'],
                    'end': token['end'],
                    'token_idx': idx # Сохраняем исходный индекс токена для реконструкции фразы
                })
        
        # Итерируем по all_lemmas_for_matching (сначала самые длинные)
        # и пытаемся найти их в списке lemmatized_words_info.
        for target_lemmatized_phrase in all_lemmas_for_matching:
            concept_info = concept_data[target_lemmatized_phrase]

            # Пропускаем, если это понятие относится к текущему файлу
            # (чтобы не создавать ссылки на саму себя)
            if concept_info['file'] == md_file_path:
                continue

            target_lemmas_list = target_lemmatized_phrase.split()
            target_len = len(target_lemmas_list)

            # Ищем target_lemmatized_phrase в списке lemmatized_words_info
            for i in range(len(lemmatized_words_info) - target_len + 1):
                current_phrase_lemmas = [lw['lemma'] for lw in lemmatized_words_info[i : i + target_len]]
                
                if current_phrase_lemmas == target_lemmas_list:
                    # Найдено совпадение!
                    match_start_idx = lemmatized_words_info[i]['start']
                    match_end_idx = lemmatized_words_info[i + target_len - 1]['end']
                    
                    # Реконструируем исходный текст найденной фразы, включая промежуточные не-слова
                    original_matched_text_tokens = tokens_with_spans[lemmatized_words_info[i]['token_idx'] : lemmatized_words_info[i + target_len - 1]['token_idx'] + 1]
                    original_matched_text = "".join([t['text'] for t in original_matched_text_tokens])

                    # Проверяем, находится ли это совпадение в какой-либо из предопределенных областей пропуска
                    is_in_skip_region = False
                    for s_start, s_end in skip_regions:
                        if s_start <= match_start_idx < match_end_idx <= s_end:
                            is_in_skip_region = True
                            break
                    if is_in_skip_region:
                        continue
                    
                    # Проверяем, перекрывается ли это совпадение с какой-либо уже связанной областью (этим скриптом)
                    is_overlapping_linked = False
                    for l_start, l_end in linked_spans:
                        if max(match_start_idx, l_start) < min(match_end_idx, l_end): # Перекрытие
                            is_overlapping_linked = True
                            break
                    if is_overlapping_linked:
                        continue

                    # Строим ссылку, сохраняя оригинальный падеж и форму
                    relative_link_path = os.path.relpath(concept_info['file'], os.path.dirname(md_file_path))
                    # URL-кодируем путь, чтобы правильно обрабатывать пробелы и спецсимволы
                    encoded_relative_link_path = urllib.parse.quote(relative_link_path.replace('\\', '/')) # Заменяем обратные слеши на прямые для URL
                    link = f"[{original_matched_text}]({encoded_relative_link_path})"
                    replacements.append((match_start_idx, match_end_idx, link))
                    linked_spans.append((match_start_idx, match_end_idx)) # Отмечаем эту область как связанную
        
        # Применяем замены справа налево, чтобы избежать проблем с индексами
        replacements.sort(key=lambda x: x[0], reverse=True)
        modified_content = original_content
        for start, end, link in replacements:
            modified_content = modified_content[:start] + link + modified_content[end:]

        if modified_content != original_content:
            return modified_content
        return None # Изменений нет
    except Exception as e:
        print(f"Error processing {md_file_path}: {e}")
        return None

def main():
    print("Checking for pymorphy2 installation...")
    try:
        import pymorphy2
    except ImportError:
        print("Error: pymorphy2 is not installed.")
        print("Please install it using: pip install pymorphy2")
        exit(1)
    print("pymorphy2 is installed.")

    print(f"Loading concepts from all concepts.json files in {WORK_DIR}...")
    concept_data, all_lemmas_for_matching = load_concepts(WORK_DIR)
    if not concept_data:
        print("No concepts loaded. Exiting.")
        return
    print(f"Loaded {len(concept_data)} unique lemmatized concepts.")
    print(f"Sorted {len(all_lemmas_for_matching)} lemmatized phrases for matching.")

    markdown_files_to_scan = []
    for root, _, files in os.walk(WEB_DIR):
        for file in files:
            if file.endswith('.md'):
                markdown_files_to_scan.append(os.path.join(root, file))

    print(f"Found {len(markdown_files_to_scan)} Markdown files in {WEB_DIR} to scan.")
    print(f"Only files in {TARGET_MODIFICATION_DIR} will be modified.")

    diffs = []
    for md_file_path in markdown_files_to_scan:
        # Проверяем, находится ли файл в целевой директории для модификации
        if not md_file_path.startswith(TARGET_MODIFICATION_DIR):
            # print(f"Skipping modification for {md_file_path} (not in target directory).")
            continue

        original_content = None
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            print(f"Could not read original content of {md_file_path}: {e}")
            continue

        modified_content = process_markdown_file(md_file_path, concept_data, all_lemmas_for_matching)

        if modified_content is not None and modified_content != original_content:
            print(f"Changes detected in {md_file_path}. Generating diff...")
            diff = unified_diff(
                original_content.splitlines(keepends=True),
                modified_content.splitlines(keepends=True),
                fromfile=os.path.relpath(md_file_path, BASE_DIR),
                tofile=os.path.relpath(md_file_path, BASE_DIR),
                lineterm=''
            )
            diffs.append("".join(diff))
            # Если вы хотите, чтобы скрипт автоматически записывал изменения в файлы,
            # раскомментируйте следующие строки:
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"Updated {md_file_path}")
        # else:
        #     print(f"No changes for {md_file_path}")

    if diffs:
        print("\n--- Generated Diffs ---")
        for d in diffs:
            print(d)
    else:
        print(f"\nNo changes were generated for any Markdown file in {TARGET_MODIFICATION_DIR}.")

if __name__ == "__main__":
    main()
