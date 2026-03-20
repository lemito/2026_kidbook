#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from collections import defaultdict

# Пытаемся импортировать pymorphy (сначала версию 3, потом 2)
try:
    import pymorphy3 as pymorphy
    MORPHY_VERSION = 3
    print(f"✅ Используется pymorphy3")
except ImportError:
    try:
        import pymorphy2 as pymorphy
        MORPHY_VERSION = 2
        print(f"✅ Используется pymorphy2")
    except ImportError:
        pymorphy = None
        MORPHY_VERSION = 0
        print(f"⚠️ pymorphy не установлен, будет использован только точный поиск")

# Конфигурация путей
CONCEPTS_FILE = '../concepts.json'
ARTICLES_BASE_DIR = '../../../../WEB/7.2_media/Computer_games/articles'

# Соответствие разделов и папок
SECTION_FOLDERS = {
    'Технологии внутри': 'technologies_inside',
    'История игр': 'how_it_all_started',
    'Жанры и миры': 'genres_and_worlds',
    'Герои и злодеи': 'heroes_and_villains',
    'Создание игр': 'dream_team',
    'Игровая культура': 'game_culture',
    'Здоровье и этикет': 'useful_tips'
}

# Словарь синонимов и сокращений
SYNONYMS = {
    'комп': 'компьютер',
    'пк': 'компьютер',
    'геймпад': 'джойстик',
    'андроид': 'Android',
    'майнкрафт': 'Minecraft',
    'гта': 'GTA',
    'злодей': 'антагонист',
    'злодеи': 'антагонист',
    'спорт': 'спортивные игры',
    'гонки': 'Racing'
}


def load_concepts(concepts_file):
    """
    Загрузка всех понятий и генерация всех возможных форм слов
    """
    with open(concepts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    concepts_map = {}  # слово -> информация о понятии
    concept_forms = defaultdict(set)  # понятие -> все его формы
    
    print(f"📚 Загружено понятий: {len(data.get('concepts', []))}")

    for concept in data['concepts']:
        label = concept['label']
        label_lower = label.lower()
        section = concept.get('section', 'Общее')
        folder = SECTION_FOLDERS.get(section, section.lower().replace(' ', '_'))
        
        # Сохраняем информацию о понятии
        concept_info = {
            'link': f"./{folder}/{concept['concept_id']}.md",
            'title': label,
            'id': concept['concept_id'],
            'section': section,
            'folder': folder
        }
        
        # Добавляем точное название
        concepts_map[label_lower] = concept_info
        concept_forms[label].add(label_lower)
        
        # Добавляем синонимы из словаря
        for synonym, original in SYNONYMS.items():
            if label_lower == original.lower() or synonym == label_lower:
                concepts_map[synonym] = concept_info
                concept_forms[label].add(synonym)
        
        # Генерируем все формы слова через pymorphy
        if pymorphy:
            try:
                morph = pymorphy.MorphAnalyzer()
                parse = morph.parse(label)[0]
                
                # Получаем все формы слова (падежи, числа)
                for form in parse.lexeme:
                    form_word = form.word.lower()
                    # Игнорируем слишком короткие формы
                    if len(form_word) > 2:
                        # Проверяем, что это не просто окончание
                        if form_word not in concepts_map:
                            concepts_map[form_word] = concept_info
                            concept_forms[label].add(form_word)
                    
            except Exception as e:
                print(f"  ⚠️ Ошибка морфологии для '{label}': {e}")
        
        # Добавляем английские названия (если есть)
        if 'label_en' in concept and concept['label_en']:
            en_lower = concept['label_en'].lower()
            concepts_map[en_lower] = concept_info
            concept_forms[label].add(en_lower)

    # Статистика
    total_forms = sum(len(forms) for forms in concept_forms.values())
    print(f"📊 Сгенерировано форм слов: {total_forms}")
    print(f"📋 Уникальных ключей для поиска: {len(concepts_map)}")
    
    return concepts_map, concept_forms


def escape_existing_links(text):
    """
    Заменяет существующие Markdown-ссылки на временные маркеры
    """
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = []
    
    def repl(match):
        links.append(match.group(0))
        return f"@@LINK_{len(links)-1}@@"
    
    text = re.sub(link_pattern, repl, text)
    return text, links


def restore_existing_links(text, links):
    """
    Возвращает маркеры обратно в исходные ссылки
    """
    for i, link in enumerate(links):
        text = text.replace(f"@@LINK_{i}@@", link)
    return text


def normalize_paths(text):
    """
    Исправляет ошибки в путях: .// → ./, ././ → ./
    """
    text = re.sub(r'\.//', './', text)
    text = re.sub(r'\./\./', './', text)
    return text


def should_skip_context(text, match_start, match_end):
    """
    Проверяет, нужно ли пропустить это вхождение (заголовки, код и т.д.)
    """
    # Проверяем, не внутри ли это заголовка
    lines_before = text[:match_start].split('\n')
    if lines_before:
        last_line = lines_before[-1]
        if last_line.startswith('#') and len(last_line.strip('# ')) > 0:
            return True
    
    # Проверяем, не внутри ли это Markdown-разметки
    surrounding = text[max(0, match_start-10):min(len(text), match_end+10)]
    if '```' in surrounding or '`' in surrounding:
        return True
    
    return False


def insert_links(text, concepts_map, current_file=None):
    """
    Вставляет ссылки на понятия, избегая конфликтов
    """
    # Шаг 1: экранируем существующие ссылки
    text, original_links = escape_existing_links(text)

    # Шаг 2: сортируем ключи по убыванию длины (сначала длинные фразы)
    sorted_keys = sorted(concepts_map.keys(), key=len, reverse=True)

    # Словарь для временных маркеров
    phrase_markers = {}
    marker_counter = 0

    # Шаг 3: заменяем вхождения ключей на маркеры
    for key in sorted_keys:
        # Пропускаем, если это текущий файл (не ссылаемся на себя)
        if current_file and concepts_map[key]['id'] == current_file:
            continue
            
        escaped_key = re.escape(key)
        # Ищем как отдельное слово (с границами слова)
        pattern = r'(?<![a-zA-Zа-яА-ЯёЁ0-9])' + escaped_key + r'(?![a-zA-Zа-яА-ЯёЁ0-9])'
        
        def create_marker(match):
            nonlocal marker_counter
            matched_text = match.group(0)
            
            # Проверяем контекст
            if should_skip_context(text, match.start(), match.end()):
                return matched_text
            
            marker = f"@@PHRASE_{marker_counter}@@"
            concept_info = concepts_map[key]
            
            # Используем оригинальный регистр в тексте ссылки
            phrase_markers[marker] = f"[{matched_text}]({concept_info['link']})"
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
    
    return text, len(phrase_markers)


def process_all_articles(concepts_map):
    """
    Обрабатывает все статьи в папках разделов
    """
    if not os.path.exists(ARTICLES_BASE_DIR):
        print(f"❌ Папка {ARTICLES_BASE_DIR} не найдена!")
        print("   Сначала запустите article_generator_team17.py")
        return False

    stats = {
        'processed': 0,
        'total_links_added': 0,
        'by_section': defaultdict(lambda: {'files': 0, 'links': 0})
    }

    print("\n🔍 Поиск статей...")

    # Проходим по всем папкам разделов
    for section_folder in sorted(os.listdir(ARTICLES_BASE_DIR)):
        section_path = os.path.join(ARTICLES_BASE_DIR, section_folder)
        
        if not os.path.isdir(section_path):
            continue
            
        print(f"\n📂 Раздел: {section_folder}")
        
        # Обрабатываем каждую статью в разделе
        for filename in sorted(os.listdir(section_path)):
            if not filename.endswith('.md') or filename == 'README.md':
                continue
                
            filepath = os.path.join(section_path, filename)
            
            # Получаем ID статьи из имени файла (без .md)
            file_id = filename[:-3]
            
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Считаем исходные ссылки
            original_links = original_content.count('](')
            
            # Вставляем новые ссылки
            new_content, added_links = insert_links(original_content, concepts_map, file_id)
            
            # Сохраняем, если были изменения
            if added_links > 0:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                stats['by_section'][section_folder]['links'] += added_links
            
            stats['processed'] += 1
            stats['total_links_added'] += added_links
            stats['by_section'][section_folder]['files'] += 1
            
            status = f"+{added_links}" if added_links > 0 else "0"
            print(f"  [{stats['processed']}] {filename}: {status} ссылок")

    return stats


def print_statistics(stats, concept_forms):
    """
    Вывод подробной статистики
    """
    print("\n" + "=" * 70)
    print("📊 СТАТИСТИКА РАССТАНОВКИ ССЫЛОК")
    print("=" * 70)
    
    print(f"\n📁 Всего обработано файлов: {stats['processed']}")
    print(f"🔗 Всего добавлено ссылок: {stats['total_links_added']}")
    
    if stats['processed'] > 0:
        avg_links = stats['total_links_added'] / stats['processed']
        print(f"📈 Среднее число ссылок на статью: {avg_links:.1f}")
    
    print("\n📊 По разделам:")
    for section, section_stats in stats['by_section'].items():
        if section_stats['files'] > 0:
            avg = section_stats['links'] / section_stats['files']
            print(f"  • {section}:")
            print(f"    - Статей: {section_stats['files']}")
            print(f"    - Ссылок: {section_stats['links']}")
            print(f"    - В среднем: {avg:.1f} на статью")
    
    if pymorphy:
        print(f"\n🔤 Морфология: pymorphy{MORPHY_VERSION}")
        print(f"📚 Всего форм слов: {sum(len(forms) for forms in concept_forms.values())}")
        print(f"📋 Уникальных понятий: {len(concept_forms)}")
    
    print("=" * 70)


def main():
    print("=" * 70)
    print("🔗 РАССТАНОВКА ПЕРЕКРЁСТНЫХ ССЫЛОК - Команда 17")
    print("=" * 70)
    print("Проект: Детская энциклопедия компьютерных игр")
    print()

    # Проверяем наличие файла с понятиями
    if not os.path.exists(CONCEPTS_FILE):
        print(f"❌ Файл {CONCEPTS_FILE} не найден!")
        print("   Сначала запустите wikidata_enricher.py")
        return

    # Загружаем понятия и генерируем формы слов
    print("📚 Загрузка понятий...")
    concepts_map, concept_forms = load_concepts(CONCEPTS_FILE)
    
    # Обрабатываем все статьи
    stats = process_all_articles(concepts_map)
    
    if stats:
        print_statistics(stats, concept_forms)
        
        print("\n✅ Готово! Теперь статьи связаны перекрёстными ссылками.")
        print("   При просмотре в браузере можно кликать на выделенные термины.")
    else:
        print("\n❌ Не удалось обработать статьи")


if __name__ == "__main__":
    main()
