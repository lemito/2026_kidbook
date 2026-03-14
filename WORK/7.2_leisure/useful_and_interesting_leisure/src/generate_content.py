from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import configparser
import json
import os
from pathlib import Path
import time
import requests
import uuid
import re
import shutil


articles_dir = '../../../../WEB/7.2_leisure/useful_and_interesting_leisure/articles'
images_dir = '../../../../WEB/7.2_leisure/useful_and_interesting_leisure/images'


def get_access_token(auth_key):
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        'Authorization': f'Basic {auth_key}',
        'RqUID': str(uuid.uuid4()),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'scope': 'GIGACHAT_API_PERS'}

    response = requests.post(url, headers=headers, data=data, verify=False)
    return response.json()['access_token']


def generate_image(access_token, prompt):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "system",
                "content": "Ты — художник, который создает визуальные изображения"
            },
            {
                "role": "user",
                "content": prompt + " Без текста и надписей. Чистое изображение без надписей и тому подобное"
            }
        ],
        "function_call": "auto",
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload, verify=False)
    return response.json()


def extract_image_id(response_text):
    # ID приходит в теге <img src="uuid">
    match = re.search(r'<img src="([a-f0-9-]+)"', response_text)
    return match.group(1) if match else None


def download_image(access_token, file_id, output_filename):
    url = f"https://gigachat.devices.sberbank.ru/api/v1/files/{file_id}/content"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/jpg'
    }

    response = requests.get(url, headers=headers, stream=True, verify=False)

    if response.status_code == 200:
        with open(output_filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        print(f"✅ Изображение сохранено: {output_filename}")
    else:
        print(f"❌ Ошибка: {response.status_code}")


def get_auth() -> str:
    """Получение авторизационных данных из config.ini"""
    config = configparser.ConfigParser()
    config.read('../config.ini')
    return config["GIGACHAT"]["auth"]


def load_concepts(file_path: str) -> list:
    """Загрузка concepts.json"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_directory(file_path: str):
    """Создание директории для файла, если её нет"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        Path(directory).mkdir(parents=True, exist_ok=True)


def generate_article(topic: str, author: str, image_path: str = "IMAGE_PLACEHOLDER", max_retries: int = 3) -> str:
    """
    Генерация статьи через GigaChat API с повторными попытками

    Args:
        topic: название темы
        author: автор темы
        max_retries: максимальное количество попыток
    """
    auth_token = get_auth()

    prompt = f"""
Ты пишешь статьи для энциклопедии для школьников 8-го класса. Твоя задача — объяснить тему просто, интересно и с пользой. Используй дружеский, уважительный стиль общения, обращайся к читателю на «ты».
Это educational content для школьного проекта.
Не надо здороваться с читателем.
Можешь в некоторых местах использовать эмодзи, но не слишком много
Тема статьи: {topic}
Объем: 400-600 слов.
Используй Markdown для форматирования текста (заголовки, списки, выделение курсивом или жирным).
при написании можешь придерживаться любой структуры главное, чтобы было интересно и полезно + нужное кол-во слов + чтобы были определение, заголовок, введение, заключение
в тексте в каком нибудь месте должна быть использована эта строка в таком виде как она есть 
!ВАЖНО: В тексте статьи добавь строку для изображения: 
![Иллюстрация: описание темы]({image_path})
Просто вставь эту строку без изменений
    """

    refusal_phrases = [
        "не обладает собственным мнением",
        "временно ограничены",
        "не может ответить на этот вопрос",
        "не могу предоставить информацию",
        "не могу ответить"
    ]

    for attempt in range(max_retries):
        try:
            with GigaChat(credentials=auth_token, verify_ssl_certs=False) as giga:
                response = giga.chat(
                    Chat(
                        messages=[
                            Messages(
                                role=MessagesRole.USER,
                                content=prompt
                            )
                        ]
                    )
                )

                if response and response.choices and len(response.choices) > 0:
                    article_text = response.choices[0].message.content

                    # Проверяем, не является ли ответ отказом
                    is_refusal = any(phrase in article_text.lower() for phrase in refusal_phrases)

                    if is_refusal and attempt < max_retries - 1:
                        print(f"  ⚠️ Получен отказ, пробуем снова ({attempt + 2}/{max_retries})...")
                        time.sleep(2)
                        continue
                    elif is_refusal:
                        print(f"  ⚠️ Получен отказ после {max_retries} попыток")
                        article_text = f"# {topic}\n\nК сожалению, не удалось сгенерировать статью по данной теме."

                    signature = f"\n\n---\n\n*Автор: {author} • Сгенерировано с помощью GigaChat*"
                    article_text += signature

                    return article_text
                else:
                    raise Exception("Пустой ответ от API")

        except Exception as e:
            print(f"  ⚠️ Ошибка при обращении к GigaChat (попытка {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                stub = f"# {topic}\n\nК сожалению, произошла техническая ошибка при генерации статьи.\n\n---\n\n*Автор: {author} • Сгенерировано с помощью GigaChat*"
                return stub


def process_concepts(concepts_file: str, overwrite: bool = True):
    """
    Основная функция обработки всех концептов

    Args:
        concepts_file: путь к файлу concepts.json
        overwrite: перезаписывать существующие файлы
    """
    data = load_concepts(concepts_file)

    if not isinstance(data, list) or len(data) == 0:
        print("Ошибка: файл concepts.json должен содержать непустой список")
        return

    first_section = data[0]
    concepts = first_section.get("concepts", [])

    print(f"Найдено концептов для обработки: {len(concepts)}")

    for i, concept in enumerate(concepts, 1):
        topic = concept.get("name", "")
        surname = concept.get("author", "")
        file_path = concept.get("file", "")
        id = concept.get("id", "")
        image_name = id.split('/')[-1]

        if not topic or not file_path:
            print(f"Пропуск {i}-го элемента: нет name или file")
            continue

        full_file_path = "../../../" + os.path.join(os.path.dirname(concepts_file), file_path)

        if os.path.exists(full_file_path) and not overwrite:
            print(f"Файл уже существует, пропускаем: {full_file_path}")
            continue

        try:
            ensure_directory(full_file_path)

            auth_key = get_auth()
            token = get_access_token(auth_key)

            print("Генерация изображения...")
            result = generate_image(token, f"Красочная иллюстрация для статьи на тему: {topic}. Подходит для школьников 8 класса. Современный стиль, яркие цвета.")
            print("Конец генерации...")
            #print(result)
            content = result['choices'][0]['message']['content']
            file_id = extract_image_id(content)
            image_path = f"{images_dir}/{image_name}.jpg"
            print(image_path)
            if file_id:
                download_image(token, file_id, image_path)

            # Генерируем статью
            print(f"\n[{i}/{len(concepts)}] Генерация статьи для {topic}")
            print(f"Путь: {full_file_path}")
            article = generate_article(topic, surname, image_path)
            article = article.replace("ВОТ_ЗДЕСЬ_БУДЕТ_ИЗОБРАЖЕНИЕ", f"![Иллюстрация: {topic}]({image_path})")

            # Сохраняем файл
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(article)

            print(f"✓ Статья сохранена: {full_file_path}")

            time.sleep(1)

        except Exception as e:
            print(f"✗ Ошибка при обработке '{topic}': {str(e)}")


def main():
    """Главная функция"""
    # Путь к файлу concepts.json
    CONCEPTS_FILE = "../concepts.json"

    process_concepts(
        concepts_file=CONCEPTS_FILE,
        overwrite=True  # True - перезаписывать, False - пропускать существующие
    )


if __name__ == "__main__":
    main()
