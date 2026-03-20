"""
Скрипт для генерации markdown-страничек детской энциклопедии
через GigaChat API (Python SDK).

Для каждого понятия из concepts.json генерирует статью,
используя контекст из WikiData (если доступен).

Использование:
  1. Установите зависимости: pip install -r requirements.txt
  2. Создайте файл .env рядом со скриптом и укажите:
       GIGACHAT_CREDENTIALS=ваш_ключ_авторизации
     (ключ авторизации (Authorization key) из https://developers.sber.ru/studio/)
     Либо задайте переменную окружения GIGACHAT_CREDENTIALS.
  3. Запустите: python generate_pages.py

  Опционально: сначала запустите wikidata_extract.py,
  чтобы обогатить промпты данными из WikiData.
"""

import json
import os
import sys
import time

from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

# Загружаем переменные из .env файла (если есть)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# Пути
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONCEPTS_PATH = os.path.join(SCRIPT_DIR, "concepts.json")
CONTEXTS_PATH = os.path.join(SCRIPT_DIR, "wikidata", "_contexts.json")
OUTPUT_DIR = os.path.join(
    SCRIPT_DIR, "..", "..", "WEB", "8.1_entertainment", "articles"
)

# Параметры генерации
TEMPERATURE = 0.7
MAX_TOKENS = 3000
MODEL = "GigaChat"  # бесплатная модель

# Маппинг name → русское название для заголовка статьи
TITLE_MAP = {
    "history_of_games": "История видеоигр",
    "game_genres": "Жанры видеоигр",
    "board_games": "Настольные игры",
    "esports": "Киберспорт",
    "gambling_and_harm": "Азартные игры и их вред",
    "gamification": "Геймификация",
    "composer": "Композитор",
    "music_genres": "Жанры музыки",
    "musical_instruments": "Музыкальные инструменты",
    "music": "Понятие музыки и её устройство",
    "history_of_music": "История музыки",
    "psychology_of_music": "Влияние музыки на человека",
    "movie": "Фильм",
    "animation": "Мультфильм",
    "documentary": "Документальный фильм",
    "media_literacy": "Медиаграмотность",
    "soundtrack": "Саундтрек",
    "montage": "Монтаж",
    "special_effects": "Спецэффекты",
    "script": "Сценарий",
    "director": "Режиссёр",
}


def get_title(concept: dict) -> str:
    return TITLE_MAP.get(concept["name"], concept["name"].replace("_", " ").title())


SYSTEM_PROMPT = (
    "Ты автор детской энциклопедии для восьмиклассников. Пиши просто, "
    "интересно и понятно для десятилетнего ребёнка. Используй короткие "
    "предложения, яркие примеры и аналогии из повседневной жизни. "
    "Добавляй забавные факты и сравнения. Структурируй текст с помощью "
    "markdown-заголовков второго и третьего уровня (## и ###). "
    "Пиши развёрнуто, подробно раскрывая каждый раздел."
)

USER_PROMPT_TEMPLATE = (
    "Напиши подробную статью для детской энциклопедии о понятии «{title}».\n"
    "Тема раздела: «Игры, фильмы и музыка: баланс пользы и развлечения».\n\n"
    "Описание статьи: {description}\n\n"
    "Требования к содержанию (каждый пункт раскрой подробно, минимум 2-3 абзаца на раздел):\n"
    "1. Введение — объясни простыми словами, что это такое, зачем это существует\n"
    "2. История — расскажи, как и когда это появилось, ключевые этапы развития\n"
    "3. Основные виды или разновидности — перечисли и кратко опиши каждый вид\n"
    "4. Интересные факты — приведи 3-5 удивительных и забавных фактов\n"
    "5. Примеры из жизни — конкретные известные примеры, понятные детям\n"
    "6. Польза — чем это полезно для развития, обучения, творчества\n"
    "7. Возможные риски — что может быть вредно при неправильном использовании\n"
    "8. Баланс пользы и развлечения — практические советы для ребёнка\n"
    "9. Заключение — короткий итог\n"
    "{wikidata_context}"
    "\nОтвет в формате markdown. Начни с заголовка первого уровня: # {title}.\n"
    "Используй таблицы, списки и выделение жирным где уместно."
)


def load_concepts() -> list[dict]:
    with open(CONCEPTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["concepts"]


def load_wikidata_contexts() -> dict[str, str]:
    if os.path.exists(CONTEXTS_PATH):
        with open(CONTEXTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def build_prompt(concept: dict, wikidata_context: str) -> str:
    ctx_block = ""
    if wikidata_context:
        ctx_block = f"\nДополнительная информация из WikiData: {wikidata_context}\n"
    title = get_title(concept)
    return USER_PROMPT_TEMPLATE.format(
        title=title,
        description=concept["description"],
        wikidata_context=ctx_block,
    )


def generate_article(giga: GigaChat, concept: dict, wikidata_context: str) -> str:
    user_prompt = build_prompt(concept, wikidata_context)

    payload = Chat(
        messages=[
            Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
            Messages(role=MessagesRole.USER, content=user_prompt),
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    response = giga.chat(payload)
    return response.choices[0].message.content


def main():
    # Credentials: из .env файла или переменной окружения GIGACHAT_CREDENTIALS
    credentials = os.getenv("GIGACHAT_CREDENTIALS", "")
    if not credentials:
        print("Ошибка: ключ авторизации GigaChat не найден.")
        print()
        print("Способ 1 (рекомендуемый): создайте файл .env рядом со скриптом:")
        print("  GIGACHAT_CREDENTIALS=ваш_authorization_key")
        print()
        print("Способ 2: задайте переменную окружения:")
        print("  Windows PowerShell:  $env:GIGACHAT_CREDENTIALS='ваш_ключ'")
        print("  Linux/macOS:         export GIGACHAT_CREDENTIALS=ваш_ключ")
        print()
        print("Ключ авторизации (Authorization key) берётся на странице:")
        print("  https://developers.sber.ru/studio/")
        sys.exit(1)

    concepts = load_concepts()
    wikidata_contexts = load_wikidata_contexts()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Загружено {len(concepts)} понятий")
    print(
        f"WikiData-контексты: {'найдены' if wikidata_contexts else 'не найдены (запустите wikidata_extract.py)'}"
    )
    print(f"Выходная директория: {OUTPUT_DIR}")
    print(f"Модель: {MODEL}, temperature={TEMPERATURE}\n")

    generated = 0
    errors = 0

    with GigaChat(
        credentials=credentials,
        verify_ssl_certs=False,
        model=MODEL,
        scope="GIGACHAT_API_PERS",
    ) as giga:
        for i, concept in enumerate(concepts, 1):
            title = get_title(concept)
            print(f"[{i}/{len(concepts)}] Генерирую: {title}...", end=" ")

            # file: "entertainment/computer_game.md" → берём только имя файла
            filename = os.path.basename(concept["file"])
            output_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(output_path):
                print("⏭ уже существует, пропускаю")
                generated += 1
                continue

            try:
                ctx = wikidata_contexts.get(concept["name"], "")
                text = generate_article(giga, concept, ctx)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)

                print(f"✓ ({len(text)} символов)")
                generated += 1

            except Exception as e:
                print(f"✗ Ошибка: {e}")
                errors += 1

            # Пауза между запросами (ограничение бесплатного лимита)
            if i < len(concepts):
                time.sleep(2)

    print(f"\nГотово! Сгенерировано: {generated}, ошибок: {errors}")
    print(f"Файлы сохранены в: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
