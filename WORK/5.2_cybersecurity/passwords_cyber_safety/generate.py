import os
import json
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')

SYSTEM_PROMPT = """Ты пишешь детскую энциклопедию для детей 10-12 лет.
Твоя задача — сгенерировать статью в строгом Markdown-формате.

Структура статьи ДОЛЖНА быть следующей:
# [Название статьи на русском]

**ID:** [id статьи]  
**WikiData:** [Оставь пустым, если не знаешь]  
**Раздел:** 5.2. Кибербезопасность и поведение в сети  

💡 **Коротко:** [Краткое описание]

## Введение
[Что это такое простыми словами]

## [Основная тема] (можно несколько)
[Как это работает в реальном мире]

## Примеры из жизни
[Минимум 3 примера]

## Заключение
[Краткий вывод]

Тон: дружелюбный, обращайся на "ты".
Используй Markdown: заголовки ##, списки -, жирный **текст**."""

def generate_text(concept_id, concept_name, concept_desc):
    if not API_KEY:
        print("Нет API_KEY в .env, пропускаем генерацию текста.")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    user_prompt = f"Напиши статью про '{concept_name}'.\nID: {concept_id}\nОписание: {concept_desc}"
    
    payload = {
        "model": "gemini-3.1-pro",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    print(f"[TEXT] Отправка запроса...")
    try:
        response = requests.post(f"{API_URL}/v1/chat/completions", json=payload, headers=headers)
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            print(f"Текст успешно сгенерирован ({len(content)} символов).")
            return content
        else:
            print(f"Ошибка API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Ошибка сети: {e}")
        return None

def generate_image(concept_name, concept_desc, output_path):
    if not API_KEY:
        print("Нет API_KEY в .env, пропускаем генерацию картинки.")
        return False

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Формируем промпт для получения картинок в едином стиле
    full_prompt = f"Иллюстрация для детской книги про кибербезопасность. Тема: {concept_name}. {concept_desc}. Яркие цвета, плоский векторный стиль, дружелюбно, без текста."
    
    payload = {
        "prompt": full_prompt,
        "model": "nano-banana-2"
    }
    
    print(f"[IMAGE] Генерация картинки для: {concept_name}...")
    try:
        response = requests.post(f"{API_URL}/v1/images/generate", json=payload, headers=headers)
        
        if response.status_code == 200:
            # API возвращает сырые байты PNG
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Картинка сохранена: {output_path}")
            return True
        else:
            print(f"Ошибка API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Ошибка сети: {e}")
        return False

def update_markdown_with_image(md_path, image_name, concept_name):
    """
    Вставляет ссылку на картинку в markdown файл после блока 'Коротко:'.
    """
    if not os.path.exists(md_path):
        print(f"Файл {md_path} не найден, пропускаем вставку картинки.")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Проверяем, есть ли уже картинка
    image_link = f"![{concept_name}](../images/{image_name}.png)\n"
    if any(image_link.strip() in line for line in lines):
        print(f"Картинка уже вставлена в {os.path.basename(md_path)}")
        return

    # Ищем блок "Коротко:" и вставляем после него пустую строку и картинку
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if line.startswith("💡 **Коротко:**") and not inserted:
            new_lines.append("\n")
            new_lines.append(image_link)
            inserted = True

    if inserted:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Картинка добавлена в {os.path.basename(md_path)}")
    else:
        print(f"Не удалось найти место для вставки картинки в {os.path.basename(md_path)}")

def main():
    concepts_path = os.path.join(os.path.dirname(__file__), 'concepts.json')
    images_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'WEB', '5.2_cybersecurity', 'passwords_cyber_safety', 'images')
    articles_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'WEB', '5.2_cybersecurity', 'passwords_cyber_safety', 'articles')
    
    os.makedirs(images_dir, exist_ok=True)
    
    with open(concepts_path, 'r', encoding='utf-8') as f:
        concepts = json.load(f)
        
    for concept in concepts:
        name = concept['name']
        desc = concept['description']
        
        print(f"\n--- Обработка концепта: {name} ---")
        
        # 1. Генерируем текст и записываем в файл
        if not os.path.exists(os.path.join(articles_dir, f"{name}.md")):
            generated_text = generate_text(name, name, desc)
            md_path = os.path.join(articles_dir, f"{name}.md")
            
            if generated_text:
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(generated_text)
                print(f"Текст сохранен в {name}.md")
        
        # 2. Генерируем картинку
        img_path = os.path.join(images_dir, f"{name}.png")
        if not os.path.exists(img_path):
            if generate_image(name, desc, img_path):
                # 3. Вставляем картинку в MD файл
                update_markdown_with_image(md_path, name, name)
        else:
            print(f"Картинка {name}.png уже существует, пропускаем.")
            # Все равно пытаемся вставить в MD, если картинка уже есть, но в MD ее нет
            update_markdown_with_image(md_path, name, name)

if __name__ == "__main__":
    main()