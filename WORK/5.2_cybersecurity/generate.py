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

def main():
    concepts_path = os.path.join(os.path.dirname(__file__), 'concepts.json')
    articles_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'WEB', '5.2_cybersecurity', 'articles')
    
    with open(concepts_path, 'r', encoding='utf-8') as f:
        concepts = json.load(f)
        
    for concept in concepts:
        name = concept['name']
        desc = concept['description']
        
        print(f"\n--- Обработка концепта: {name} ---")
        
        # Генерируем текст и записываем в файл
        generated_text = generate_text(name, name, desc)
        md_path = os.path.join(articles_dir, f"{name}.md")
        
        if generated_text:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(generated_text)
            print(f"Текст сохранен в {name}.md")

if __name__ == "__main__":
    main()