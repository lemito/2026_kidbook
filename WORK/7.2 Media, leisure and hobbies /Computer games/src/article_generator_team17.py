#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
article_generator_team17.py

Скрипт для генерации статей детской энциклопедии компьютерных игр
с помощью OpenRouter (Qwen) и создания иллюстраций.

Проект: Команда 17 - Детская энциклопедия компьютерных игр
Автор: [Ваше имя]
Дата: 2024

Использование:
    python article_generator_team17.py

Выходные данные:
    ../articles/[раздел]/[id].md - сгенерированные статьи
    ../images/[раздел]/[id].png - иллюстрации (если GENERATE_IMAGES=True)
"""

import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import urllib.parse

# Загружаем переменные окружения
load_dotenv()

# Конфигурация OpenRouter
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_SITE_URL = os.getenv('OPENROUTER_SITE_URL', 'https://github.com/lizabeth2616/2026_kidbook')
GENERATE_IMAGES = os.getenv('GENERATE_IMAGES', 'False').lower() == 'true'

# Пути к файлам (адаптируйте под структуру проекта)
CONCEPTS_FILE = '../concepts.json'  # Файл с понятиями из wikidata_enricher.py
ARTICLES_BASE_DIR = '../articles'    # Базовая папка для статей
IMAGES_BASE_DIR = '../images'        # Базовая папка для изображений


def generate_text_qwen(concept_label, concept_desc, section):
    """
    Генерация текста статьи через OpenRouter (модель Qwen)
    """
    prompt = f"""Ты пишешь детскую энциклопедию о компьютерных играх для детей 10 лет.

РАЗДЕЛ ЭНЦИКЛОПЕДИИ: {section}
ТЕРМИН: {concept_label}
КРАТКОЕ ОПИСАНИЕ: {concept_desc}

Напиши увлекательную статью объёмом 400-600 слов со структурой:

## Что это такое?
Простое объяснение термина для ребёнка 10 лет. Используй аналогии из реальной жизни.

## Где это встречается в играх?
Приведи 2-3 конкретных примера из популярных игр (Minecraft, Super Mario, GTA, The Legend of Zelda, Roblox, Among Us и др.). Объясни, как этот термин проявляется в этих играх.

## Почему это важно?
Объясни значение этого понятия в игровой индустрии или для игроков.

## Интересные факты
2-3 коротких, но удивительных факта по теме.

Требования к стилю:
- Дружелюбный тон, обращение на "ты"
- Без сложных технических терминов (или сразу объяснять их)
- Добавляй эмодзи для живости 🎮 👾 ⭐
- Используй примеры из игр, которые знают современные дети

Начни с заголовка: # {concept_label}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": "KidBook Computer Games Encyclopedia"
    }

    # Пробуем разные модели Qwen (от большей к меньшей)
    models_to_try = [
        "qwen/qwen-2.5-72b-instruct",  # Основная модель
        "qwen/qwen-2.5-32b-instruct",  # Запасная
        "qwen/qwen-2-7b-instruct"      # Если первые не работают
    ]

    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Ты автор детской энциклопедии о компьютерных играх. Пиши 400-600 слов простым языком для детей 10 лет. Всегда завершай статью полностью."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,  # Немного творчества
            "max_tokens": 3500    # Чтобы хватило на 600 слов
        }

        try:
            print(f"  🔄 Пробуем {model}...", end=" ")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=120  # Увеличим таймаут для больших моделей
            )

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Очищаем от возможных артефактов
                if content.startswith('#'):
                    content = content  # Уже есть заголовок
                else:
                    content = f"# {concept_label}\n\n{content}"
                
                word_count = len(content.split())
                print(f"{word_count} слов ✅")
                
                # Даже если меньше 300 слов, берём что есть (но помечаем)
                return content, word_count
            else:
                print(f"❌ {response.status_code}")
                if response.status_code == 429:  # Too Many Requests
                    time.sleep(5)  # Подождём перед следующей попыткой
        except Exception as e:
            print(f"❌ Ошибка: {type(e).__name__}")
            continue

    return "⚠️ Не удалось сгенерировать текст.", 0


def generate_image_pollinations(prompt_text, concept_label):
    """
    Генерация изображения через Pollinations.ai
    """
    try:
        # Специальный промпт для детских иллюстраций
        full_prompt = f"children book illustration, computer games, {prompt_text}, {concept_label}, flat vector style, bright colors, educational, cute characters, game art style"
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        # Разные сервисы Pollinations
        services = [
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={int(time.time())}",
            f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={int(time.time())}"
        ]
        
        for service_url in services:
            try:
                response = requests.head(service_url, timeout=10)
                if response.status_code == 200:
                    return service_url
            except:
                continue
        return None
    except:
        return None


def generate_image_placeholder(concept_label):
    """
    Заглушка-изображение с текстом (всегда работает)
    """
    try:
        encoded_label = urllib.parse.quote(concept_label)
        # Цвета под разделы (можно расширить)
        colors = {
            'Технологии внутри': '3498db',  # Синий
            'История игр': 'e74c3c',         # Красный
            'Жанры и миры': '2ecc71',         # Зелёный
            'Герои и злодеи': 'f39c12',       # Оранжевый
            'Создание игр': '9b59b6',         # Фиолетовый
            'Игровая культура': 'e91e63',      # Розовый
            'Здоровье и этикет': '1abc9c'      # Бирюзовый
        }
        
        # Определяем цвет по разделу (пока дефолтный)
        color = colors.get('Технологии внутри', '3498db')
        
        image_url = f"https://placehold.co/1024x1024/{color}/FFFFFF/png?text={encoded_label}&font=roboto"
        response = requests.head(image_url, timeout=5)
        return image_url if response.status_code == 200 else None
    except:
        return None


def generate_image_fallback(prompt_text, concept_label):
    """
    Пробуем разные сервисы для генерации изображения
    """
    services = [
        ("Pollinations.ai", lambda: generate_image_pollinations(prompt_text, concept_label)),
        ("Placehold.co", lambda: generate_image_placeholder(concept_label))
    ]
    
    for service_name, service_func in services:
        print(f"  🎨 Пробуем {service_name}...", end=" ")
        img_url = service_func()
        if img_url:
            print(f"✅")
            return img_url
        else:
            print(f"⚠️")
    
    return None


def download_image(url, filename):
    """
    Скачивание изображения по URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        print(f"  ⚠️ Ошибка скачивания: {e}")
        return False


def ensure_directories(section):
    """
    Создание папок для раздела, если их нет
    """
    # Транслитерация раздела для имени папки
    section_folder = section.replace(' ', '_').replace('ё', 'e').lower()
    
    articles_dir = os.path.join(ARTICLES_BASE_DIR, section_folder)
    images_dir = os.path.join(IMAGES_BASE_DIR, section_folder)
    
    os.makedirs(articles_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    return articles_dir, images_dir


def main():
    # Проверяем наличие API ключа
    if not OPENROUTER_API_KEY:
        print("❌ Ошибка: Не найден ключ OPENROUTER_API_KEY в файле .env")
        print("   Получите ключ на https://openrouter.ai/keys")
        return

    # Проверяем наличие файла с понятиями
    if not os.path.exists(CONCEPTS_FILE):
        print(f"❌ Файл {CONCEPTS_FILE} не найден!")
        print("   Сначала запустите wikidata_enricher.py для создания concepts.json")
        return

    # Загружаем понятия
    with open(CONCEPTS_FILE, 'r', encoding='utf-8') as f:
        concepts_data = json.load(f)

    print("=" * 70)
    print("🤖 ГЕНЕРАТОР СТАТЕЙ - Команда 17")
    print("=" * 70)
    print(f"Проект: Детская энциклопедия компьютерных игр")
    print(f"Всего понятий: {len(concepts_data.get('concepts', []))}")
    print(f"Генерация картинок: {'ВКЛ' if GENERATE_IMAGES else 'ВЫКЛ'}")
    print("=" * 70)
    print()

    # Статистика
    stats = {
        'total': 0,
        'success': 0,
        'short_articles': 0,
        'total_words': 0,
        'images_generated': 0,
        'by_section': {}
    }

    # Обрабатываем каждое понятие
    for i, concept in enumerate(concepts_data['concepts'], 1):
        section = concept.get('section', 'Общее')
        concept_id = concept['concept_id']
        label = concept['label']
        description = concept.get('wikidata_description_ru', concept.get('local_description', ''))
        author = concept.get('author', 'Команда 17')
        
        # Инициализируем статистику по разделу
        if section not in stats['by_section']:
            stats['by_section'][section] = {
                'total': 0,
                'success': 0,
                'short': 0,
                'words': 0
            }
        stats['by_section'][section]['total'] += 1
        stats['total'] += 1

        print(f"\n[{i}/{len(concepts_data['concepts'])]}")
        print(f"📌 Раздел: {section}")
        print(f"📝 Понятие: {label}")
        print(f"📋 ID: {concept_id}")

        # Создаём папки для раздела
        articles_dir, images_dir = ensure_directories(section)

        # Генерируем текст
        print(f"  🤖 Генерация статьи...")
        text_content, word_count = generate_text_qwen(label, description, section)
        
        stats['total_words'] += word_count
        stats['by_section'][section]['words'] += word_count

        if word_count >= 300:
            print(f"  ✅ Объём: {word_count} слов (норма)")
            stats['success'] += 1
            stats['by_section'][section]['success'] += 1
        else:
            print(f"  ⚠️ Объём: {word_count} слов (маловато)")
            stats['short_articles'] += 1
            stats['by_section'][section]['short'] += 1

        # Генерируем картинку
        image_rel_path = ""
        if GENERATE_IMAGES:
            print(f"  🎨 Генерация иллюстрации...")
            img_prompt = f"{label}, {description[:100]}"
            img_url = generate_image_fallback(img_prompt, label)

            if img_url:
                image_filename = f"{concept_id}.png"
                image_full_path = os.path.join(images_dir, image_filename)
                
                if download_image(img_url, image_full_path):
                    # Относительный путь для Markdown
                    image_rel_path = f"../../images/{section_folder}/{image_filename}"
                    print(f"  ✅ Картинка сохранена")
                    stats['images_generated'] += 1
                else:
                    print(f"  ⚠️ Не удалось скачать картинку")
            else:
                print(f"  ⚠️ Не удалось создать картинку")

        # Сохраняем статью в Markdown
        filename = f"{concept_id}.md"
        filepath = os.path.join(articles_dir, filename)

        md_content = f"""# {label}

<div class="article-meta">
  <p><strong>ID:</strong> {concept_id} | <strong>Раздел:</strong> {section} | <strong>Автор:</strong> {author}</p>
</div>

<div class="wikidata-ref">
  <p>📚 Данные из <a href="https://www.wikidata.org/wiki/{concept.get('wikidata_id', '')}">WikiData</a></p>
</div>

---

{text_content}

---

<div class="article-footer">
  <p><em>Сгенерировано с помощью OpenRouter • {datetime.now().strftime('%d.%m.%Y')} • Слов: {word_count}</em></p>
</div>
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"  ✅ Статья сохранена: {filepath}")
        
        # Небольшая задержка между запросами
        time.sleep(2)

    # Выводим итоговую статистику
    print()
    print("=" * 70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)
    print(f"📝 Всего статей: {stats['total']}")
    print(f"✅ Успешно сгенерировано: {stats['success']}")
    print(f"⚠️ Коротких статей (<300 слов): {stats['short_articles']}")
    print(f"📈 Всего слов: {stats['total_words']}")
    print(f"📊 Средний объём: {stats['total_words'] // stats['total'] if stats['total'] > 0 else 0} слов")
    print(f"🎨 Картинок создано: {stats['images_generated']}")
    print()
    print("📚 По разделам:")
    for section, section_stats in stats['by_section'].items():
        print(f"  • {section}:")
        print(f"    - Понятий: {section_stats['total']}")
        print(f"    - Успешно: {section_stats['success']}")
        print(f"    - Коротких: {section_stats['short']}")
        print(f"    - Всего слов: {section_stats['words']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
