import os
import sys
import argparse
from google import genai

def generate_article(theme: str) -> str:
    client = genai.Client()
    system_instruction = f"""
Ты - автор википедии для подростков. твоя задача — написать статью в стиле Википедии для на русском языке простым и понятным языком.
Статья должна включать:
- Введение с определением темы
- Основные характеристики и факты
- Интересные детали
- Разделы с подзаголовками (используй ## для основных разделов)
- если возможно включай таблицы и списки 
- не включай раздел смотри также

Объем: примерно 500-1000 слов.
Используй формат Markdown для оформления
"""
    prompt = f"""напиши статью на тему {theme}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction
        ),
        contents=prompt
    )
    
    if response.text:
        return response.text
    else:
        print("Error: Model returned an empty response.")
        return None

def format_article(article: str) -> str:
    return article + """

---
Авторы: Гига Максим, Изиланов Илья\\
Ресурсы: LLM - Google Gemini 
"""


def describe_article(file: str) -> str:
    client = genai.Client()
    system_instruction = f"""
Тебе дается статья википедии в формате markdown. Ты должен из нее извлечь краткое описание - 1 краткое предложение о чем статья, а также список ключевых терминов которые можно узнать прочитав статью - около 5 штук
Результат необходимо вывести в формате JSON. Описание - строка "description", термины - массив строк "lemmas"
"""
    prompt = f"""{file}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction
        ),
        contents=prompt
    )
    
    if response.text:
        return response.text
    else:
        print("Error: Model returned an empty response.")
        return None


def main():
    if len(sys.argv) == 2:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            text = f.read()
            print("generating description and lemmas based on file")
            output = describe_article(text)
            print(output)
            return

    if len(sys.argv) < 3:
        print("theme and output filename must be provided")
        return
    theme = sys.argv[1]
    output = sys.argv[2]
    print(f"generating article with theme {theme}")

    article = generate_article(theme)
    article = format_article(article)

    with open(output, "w", encoding="utf-8") as f:
        f.write(article)
    print(f"saved to {output}")


if __name__ == "__main__":
    main()
