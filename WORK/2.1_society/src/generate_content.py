#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_SITE_URL = os.getenv('OPENROUTER_SITE_URL', '')
GENERATE_IMAGES = os.getenv('GENERATE_IMAGES', 'False').lower() == 'true'


def generate_text_qwen(concept_label, concept_desc):
    prompt = f"""Ты пишешь детскую энциклопедию для детей 10-12 лет.

ТЕМА: {concept_label}
ОПРЕДЕЛЕНИЕ: {concept_desc}

Напиши статью 400-600 слов со структурой:
1. Введение — что это такое простыми словами
2. Основная часть — как это работает в реальном мире
3. Примеры из жизни школьника (минимум 3 примера)
4. Интересные факты (2-3 факта)
5. Заключение — краткий вывод

Тон: дружелюбный, обращайся на "ты"
Используй Markdown: заголовки ##, списки -, жирный **текст**
Добавь эмодзи для живости 📚

Начни с заголовка: # {concept_label}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": "KidBook Lab Work 2.1"
    }

    models_to_try = [
        "qwen/qwen-2.5-72b-instruct",
        "qwen/qwen-2-7b-instruct"
    ]

    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Пиши 400-600 слов для детей 10-12 лет. Завершай статью полностью."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }

        try:
            print(f"  🔄 {model}...", end=" ")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=90
            )

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                word_count = len(content.split())
                print(f"{word_count} слов ✅")
                if word_count >= 300:
                    return content
            else:
                print(f"❌ {response.status_code}")
        except Exception:
            print(f"❌ Ошибка")

    return "⚠️ Не удалось сгенерировать текст."


def generate_image_pollinations(prompt_text):
    try:
        full_prompt = f"children book illustration, {prompt_text}, flat vector style, bright colors, educational"
        encoded_prompt = urllib.parse.quote(full_prompt)
        seed = int(time.time() * 1000) % 100000
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
        response = requests.head(image_url, timeout=15)
        return image_url if response.status_code == 200 else None
    except:
        return None


def generate_image_lorem_picsum():
    try:
        seed = int(time.time())
        image_url = f"https://picsum.photos/seed/{seed}/1024/1024"
        response = requests.head(image_url, timeout=10)
        return image_url if response.status_code == 200 else None
    except:
        return None


def generate_image_placeholder(concept_label):
    try:
        encoded_label = urllib.parse.quote(concept_label)
        colors = ['667eea', 'f093fb', '4facfe', '43e97b', 'fa709a']
        color = colors[hash(concept_label) % len(colors)]
        image_url = f"https://placehold.co/1024x1024/{color}/FFFFFF.png?text={encoded_label}&font=roboto"
        response = requests.head(image_url, timeout=10)
        return image_url if response.status_code == 200 else None
    except:
        return None


def generate_image_fallback(prompt_text, concept_label):
    services = [
        ("Pollinations.ai", lambda: generate_image_pollinations(prompt_text)),
        ("Lorem Picsum", lambda: generate_image_lorem_picsum()),
        ("Placehold.co", lambda: generate_image_placeholder(concept_label))
    ]
    for service_name, service_func in services:
        print(f"  🎨 {service_name}...", end=" ")
        img_url = service_func()
        if img_url:
            print(f"✅")
            return img_url
        else:
            print(f"⚠️")
    return None


def download_image(url, filename):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        img_data = requests.get(url, headers=headers, timeout=30).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        return True
    except Exception as e:
        print(f"  ⚠️ Ошибка скачивания: {e}")
        return False


def main():
    if not OPENROUTER_API_KEY:
        print("❌ Ошибка: Не найден ключ OPENROUTER_API_KEY в файле .env")
        return

    concepts_file = '../concepts.json'
    if not os.path.exists(concepts_file):
        print(f"❌ Файл {concepts_file} не найден!")
        return

    with open(concepts_file, 'r', encoding='utf-8') as f:
        concepts_data = json.load(f)

    articles_dir = '../../../WEB/14_team/rights_and_responsibilities/articles'
    images_dir = '../../../WEB/14_team/rights_and_responsibilities/images'

    os.makedirs(articles_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    print("=" * 60)
    print("🤖 Генерация контента: OpenRouter")
    print("=" * 60)
    print(f"Раздел: {concepts_data.get('section', 'N/A')}")
    print(f"Группа: {concepts_data.get('author_group', 'N/A')}")
    print(f"Картинки: {'Включены' if GENERATE_IMAGES else 'Выключены'}")
    print(f"Понятий всего: {len(concepts_data.get('concepts', []))}")
    print()

    generated_count = 0
    image_count = 0
    total_words = 0
    incomplete_count = 0

    for i, concept in enumerate(concepts_data['concepts'], 1):
        print(f"[{i}/{len(concepts_data['concepts'])}] Обработка: {concept['label']}...")

        local_description = concept['description']
        author_name = concept.get('author', 'Неизвестный автор')

        text_content = generate_text_qwen(concept['label'], local_description)
        word_count = len(text_content.split())
        total_words += word_count

        if word_count < 300:
            incomplete_count += 1
            print(f"  ⚠️ Статья короткая ({word_count} слов)")
        else:
            print(f"  ✅ Объём нормальный ({word_count} слов)")

        image_rel_path = ""

        if GENERATE_IMAGES:
            print(f"  🎨 Генерация иллюстрации...")
            img_prompt = f"{concept['label']}: {local_description}"
            img_url = generate_image_fallback(img_prompt, concept['label'])

            if img_url:
                image_filename = f"{concept['id']}.png"
                image_full_path = os.path.join(images_dir, image_filename)

                if download_image(img_url, image_full_path):
                    image_rel_path = f"../images/{image_filename}"
                    print(f"  ✅ Картинка сохранена")
                    image_count += 1
                else:
                    print(f"  ⚠️ Не удалось скачать картинку")
            else:
                print(f"  ⚠️ Все сервисы изображений недоступны")

        filename = f"{concept['id']}.md"
        filepath = os.path.join(articles_dir, filename)

        md_content = f"# {concept['label']}\n\n"
        md_content += f"**ID:** `{concept['id']}`  \n"
        md_content += f"**WikiData:** [{concept['wikidata_id']}]"
        md_content += f"(https://www.wikidata.org/wiki/{concept['wikidata_id']})  \n"
        md_content += f"**Раздел:** {concepts_data['section']}\n\n"

        md_content += f"> 💡 **Коротко:** {local_description}\n\n"

        if image_rel_path:
            md_content += f"![{concept['label']}]({image_rel_path})\n\n"
        else:
            md_content += f"> ⚠️ Изображение временно недоступно\n\n"

        md_content += "---\n\n"
        md_content += f"{text_content}\n\n"
        md_content += "---\n\n"

        md_content += f"*Автор: {author_name} • Сгенерировано с помощью OpenRouter • "
        md_content += f"Слов: {word_count} • {datetime.now().strftime('%Y-%m-%d')}*\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        generated_count += 1
        print(f"  ✅ Статья сохранена")

        time.sleep(1)

    avg_words = total_words // generated_count if generated_count > 0 else 0

    print()
    print("=" * 60)
    print(f"✅ Готово!")
    print(f"📝 Статей сгенерировано: {generated_count}")
    print(f"📊 Средний объём статьи: {avg_words} слов")
    print(f"📈 Всего слов: {total_words}")
    print(f"⚠️ Коротких статей: {incomplete_count}")
    print(f"🎨 Картинок создано: {image_count}")
    print(f"📁 Папка статей: {articles_dir}")
    print(f"📁 Папка картинок: {images_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()