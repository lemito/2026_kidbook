#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
setup_web_structure_team17.py

Скрипт для создания веб-структуры детской энциклопедии компьютерных игр.
Создаёт папки для статей и изображений, генерирует index.md и glossary.md.

Проект: Команда 17 - Детская энциклопедия компьютерных игр
Автор: [Ваше имя]
Дата: 2024

Использование:
    python setup_web_structure_team17.py

Выходные данные:
    ../../WEB/7.2_media/Computer_games/
    ├── articles/
    │   ├── technologies_inside/
    │   ├── how_it_all_started/
    │   └── ... (папки по разделам)
    ├── images/
    │   ├── technologies_inside/
    │   ├── how_it_all_started/
    │   └── ...
    ├── index.md
    └── glossary.md
"""

import os
import json
from datetime import datetime


# Конфигурация путей
WEB_BASE = '../../../../WEB/7.2_media/Computer_games'
CONCEPTS_FILE = '../concepts.json'

# Соответствие разделов и папок (для транслитерации)
SECTION_FOLDERS = {
    'Технологии внутри': 'technologies_inside',
    'История игр': 'how_it_all_started',
    'Жанры и миры': 'genres_and_worlds',
    'Герои и злодеи': 'heroes_and_villains',
    'Создание игр': 'dream_team',
    'Игровая культура': 'game_culture',
    'Здоровье и этикет': 'useful_tips'
}

# Цвета для разных разделов (для визуального оформления)
SECTION_COLORS = {
    'Технологии внутри': '#3498db',  # Синий
    'История игр': '#e74c3c',        # Красный
    'Жанры и миры': '#2ecc71',        # Зелёный
    'Герои и злодеи': '#f39c12',      # Оранжевый
    'Создание игр': '#9b59b6',        # Фиолетовый
    'Игровая культура': '#e91e63',     # Розовый
    'Здоровье и этикет': '#1abc9c'     # Бирюзовый
}


def create_web_structure():
    """
    Создание папок для статей и изображений по разделам
    """
    with open(CONCEPTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Создаём базовые папки
    articles_base = os.path.join(WEB_BASE, 'articles')
    images_base = os.path.join(WEB_BASE, 'images')
    
    os.makedirs(articles_base, exist_ok=True)
    os.makedirs(images_base, exist_ok=True)
    
    # Создаём папки для каждого раздела
    sections_created = set()
    for concept in data['concepts']:
        section = concept.get('section', 'Общее')
        if section not in sections_created:
            folder_name = SECTION_FOLDERS.get(section, section.lower().replace(' ', '_'))
            
            articles_dir = os.path.join(articles_base, folder_name)
            images_dir = os.path.join(images_base, folder_name)
            
            os.makedirs(articles_dir, exist_ok=True)
            os.makedirs(images_dir, exist_ok=True)
            
            sections_created.add(section)
    
    print("✅ Создана структура папок:")
    print(f"   {WEB_BASE}/")
    print(f"   ├── articles/")
    for section in sorted(sections_created):
        folder = SECTION_FOLDERS.get(section, section.lower().replace(' ', '_'))
        print(f"   │   ├── {folder}/")
    print(f"   └── images/")
    for section in sorted(sections_created):
        folder = SECTION_FOLDERS.get(section, section.lower().replace(' ', '_'))
        print(f"       └── {folder}/")
    
    return data


def generate_section_summary(data):
    """
    Генерация сводки по разделам для index.md
    """
    sections = {}
    for concept in data['concepts']:
        section = concept.get('section', 'Общее')
        if section not in sections:
            sections[section] = {
                'count': 0,
                'concepts': [],
                'authors': set()
            }
        sections[section]['count'] += 1
        sections[section]['concepts'].append(concept['label'])
        sections[section]['authors'].add(concept.get('author', 'Команда 17'))
    
    # Генерируем HTML-блоки для каждого раздела
    section_blocks = []
    for section, info in sections.items():
        folder = SECTION_FOLDERS.get(section, section.lower().replace(' ', '_'))
        color = SECTION_COLORS.get(section, '#95a5a6')
        authors = ', '.join(info['authors'])
        
        block = f"""
<div class="section-card" style="border-left: 5px solid {color}; padding-left: 15px; margin: 20px 0;">
    <h3 style="color: {color};">🎮 {section}</h3>
    <p><strong>Понятий:</strong> {info['count']} | <strong>Авторы:</strong> {authors}</p>
    <p><strong>Темы:</strong> {', '.join(info['concepts'][:5])}{'...' if info['count'] > 5 else ''}</p>
    <p><a href="./articles/{folder}/">📁 Перейти к разделу</a></p>
</div>
"""
        section_blocks.append(block)
    
    return '\n'.join(section_blocks)


def create_index_md(data):
    """
    Создание главной страницы index.md
    """
    section_summary = generate_section_summary(data)
    
    # Подсчёт статистики
    total_concepts = len(data['concepts'])
    total_sections = len(set(c.get('section', 'Общее') for c in data['concepts']))
    total_authors = len(set(c.get('author', '') for c in data['concepts'] if c.get('author')))
    
    content = f"""# Детская энциклопедия компьютерных игр 🎮

**Раздел:** {data.get('section', '7.2 Media, leisure and hobbies')}  
**Команда:** {data.get('author_group', 'Команда 17')}  
**Дата обновления:** {datetime.now().strftime('%d.%m.%Y')}

---

## 🌟 О проекте

Добро пожаловать в детскую энциклопедию компьютерных игр! Здесь ты найдёшь простые и понятные объяснения разных игровых терминов, узнаешь историю игр, познакомишься с героями и даже узнаешь, как создаются игры.

Энциклопедия создана специально для детей 10 лет — всё написано простым языком, с примерами из любимых игр и яркими картинками!

---

## 📚 Разделы энциклопедии

{section_summary}

---

## 📊 Статистика проекта

| Метрика | Значение |
|---------|----------|
| 📝 Всего статей | {total_concepts} |
| 📂 Разделов | {total_sections} |
| 👥 Авторов | {total_authors} |
| 🎨 Иллюстраций | {total_concepts} (по одной на статью) |
| 🔗 Источник данных | WikiData |
| 🤖 Генерация текста | Qwen (OpenRouter) |

---

## 🗺️ Как пользоваться

1. Выбери интересующий раздел выше
2. Найди нужное понятие в списке
3. Читай статью и рассматривай иллюстрации
4. Переходи по ссылкам на связанные темы

---

## 🔗 Полезные ссылки

- [📖 Словарь терминов](./glossary.md) — все понятия в алфавитном порядке
- [📁 Все статьи](./articles/) — общая папка со статьями
- [🌐 WikiData](https://www.wikidata.org/) — база знаний, которую мы использовали
- [🏠 Вернуться к предмету](../../README.md)

---

<div class="footer" style="text-align: center; color: #666; margin-top: 50px;">
    <p><em>Сгенерировано с помощью ИИ • Команда 17 • {datetime.now().year}</em></p>
</div>
"""
    
    filepath = os.path.join(WEB_BASE, 'index.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Создан файл: {filepath}")


def create_glossary_md(data):
    """
    Создание словаря терминов glossary.md
    """
    # Группируем понятия по первой букве
    glossary_by_letter = {}
    for concept in sorted(data['concepts'], key=lambda x: x['label'].lower()):
        first_letter = concept['label'][0].upper()
        if first_letter not in glossary_by_letter:
            glossary_by_letter[first_letter] = []
        
        section = concept.get('section', 'Общее')
        folder = SECTION_FOLDERS.get(section, section.lower().replace(' ', '_'))
        
        glossary_by_letter[first_letter].append({
            'label': concept['label'],
            'description': concept.get('wikidata_description_ru', concept.get('local_description', '')),
            'id': concept['concept_id'],
            'section': section,
            'folder': folder
        })
    
    # Генерируем алфавитный указатель
    alphabet_nav = ' | '.join([f"[{letter}](#{letter})" for letter in sorted(glossary_by_letter.keys())])
    
    # Генерируем содержимое по буквам
    letter_blocks = []
    for letter in sorted(glossary_by_letter.keys()):
        items = []
        for concept in glossary_by_letter[letter]:
            items.append(
                f"### **{concept['label']}**  \n"
                f"*Раздел: {concept['section']}*  \n"
                f"{concept['description']}  \n"
                f"[📖 Читать статью](./articles/{concept['folder']}/{concept['id']}.md)  \n"
            )
        
        block = f"""
## {letter}

{chr(10).join(items)}

---
"""
        letter_blocks.append(block)
    
    content = f"""# Словарь терминов 📚

**Проект:** Детская энциклопедия компьютерных игр  
**Всего понятий:** {len(data['concepts'])}  
**Дата:** {datetime.now().strftime('%d.%m.%Y')}

---

## 🔍 Алфавитный указатель

{alphabet_nav}

---

## 📖 Значения терминов

{chr(10).join(letter_blocks)}

---

## 📊 Дополнительная информация

| Раздел | Количество понятий | Авторы |
|--------|-------------------|--------|
"""

    # Добавляем статистику по разделам
    sections_stats = {}
    for concept in data['concepts']:
        section = concept.get('section', 'Общее')
        if section not in sections_stats:
            sections_stats[section] = {'count': 0, 'authors': set()}
        sections_stats[section]['count'] += 1
        sections_stats[section]['authors'].add(concept.get('author', 'Команда 17'))
    
    for section, stats in sorted(sections_stats.items()):
        authors = ', '.join(stats['authors'])
        content += f"| {section} | {stats['count']} | {authors} |\n"
    
    content += """
---

## 🔗 Ссылки

- [🏠 На главную](./index.md)
- [📁 Все статьи](./articles/)
- [🌐 WikiData](https://www.wikidata.org)

---

<div class="footer" style="text-align: center; color: #666; margin-top: 50px;">
    <p><em>Словарь создан автоматически • Команда 17 • {datetime.now().year}</em></p>
</div>
"""
    
    filepath = os.path.join(WEB_BASE, 'glossary.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Создан файл: {filepath}")


def create_readme_for_sections(data):
    """
    Создание README.md в каждой папке раздела
    """
    articles_base = os.path.join(WEB_BASE, 'articles')
    
    # Группируем понятия по разделам
    sections = {}
    for concept in data['concepts']:
        section = concept.get('section', 'Общее')
        if section not in sections:
            sections[section] = []
        sections[section].append(concept)
    
    for section, concepts in sections.items():
        folder = SECTION_FOLDERS.get(section, section.lower().replace(' ', '_'))
        readme_path = os.path.join(articles_base, folder, 'README.md')
        
        # Сортируем понятия по ID
        concepts.sort(key=lambda x: x['concept_id'])
        
        table_rows = []
        for concept in concepts:
            row = f"| {concept['concept_id']} | **{concept['label']}** | {concept.get('wikidata_description_ru', concept.get('local_description', ''))[:100]}... | [Читать](./{concept['concept_id']}.md) |"
            table_rows.append(row)
        
        color = SECTION_COLORS.get(section, '#95a5a6')
        
        content = f"""# Раздел: {section} 🎮

<div style="border-left: 5px solid {color}; padding-left: 15px;">
    <p><strong>Цвет раздела:</strong> <span style="color: {color};">{color}</span></p>
    <p><strong>Всего статей:</strong> {len(concepts)}</p>
</div>

---

## 📚 Статьи раздела

| ID | Понятие | Краткое описание | Ссылка |
|----|---------|------------------|--------|
{chr(10).join(table_rows)}

---

## 🔗 Навигация

- [🏠 На главную](../../index.md)
- [📖 Словарь](../../glossary.md)
- [🎨 Изображения раздела](../../images/{folder}/)

---

<div class="footer">
    <p><em>Раздел создан {datetime.now().strftime('%d.%m.%Y')} • Команда 17</em></p>
</div>
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Создан README для раздела: {section}")


def main():
    print("=" * 70)
    print("🌐 НАСТРОЙКА ВЕБ-СТРУКТУРЫ - Команда 17")
    print("=" * 70)
    print("Проект: Детская энциклопедия компьютерных игр")
    print()
    
    # Проверяем наличие файла concepts.json
    if not os.path.exists(CONCEPTS_FILE):
        print(f"❌ Файл {CONCEPTS_FILE} не найден!")
        print("   Сначала запустите wikidata_enricher.py")
        return
    
    # Создаём структуру папок
    print("📁 Создание структуры папок...")
    data = create_web_structure()
    
    print("\n📄 Генерация навигационных файлов...")
    create_index_md(data)
    create_glossary_md(data)
    create_readme_for_sections(data)
    
    print()
    print("=" * 70)
    print("✅ ВЕБ-СТРУКТУРА УСПЕШНО СОЗДАНА!")
    print("=" * 70)
    print("📂 Все файлы находятся в:")
    print(f"   {WEB_BASE}/")
    print()
    print("📋 Что дальше:")
    print("   1. Запустите article_generator_team17.py для генерации статей")
    print("   2. Проверьте сгенерированные файлы в articles/ и images/")
    print("   3. Откройте index.md в браузере для навигации")
    print("=" * 70)


if __name__ == "__main__":
    main()
