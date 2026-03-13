import json
import os
import re
from pathlib import Path


def load_concepts(file_path: str) -> list:
    """Загрузка concepts.json"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_topics_dict(concepts_file):
    """Создает словарь тем и их файлов для поиска ссылок"""
    data = load_concepts(concepts_file)
    first_section = data[0]
    concepts = first_section.get("concepts", [])

    topics_dict = {}
    file_to_topic = {}  # для обратного поиска

    for concept in concepts:
        name = concept.get("name", "")
        file_path = concept.get("file", "")
        if file_path:
            # Получаем имя файла для ссылки
            filename = os.path.basename(file_path)
            topics_dict[name.lower()] = filename
            file_to_topic[filename] = name

            # Добавляем ключевые слова из lemmas
            lemmas = concept.get("lemmas", [])
            for lemma in lemmas:
                if lemma and len(lemma) > 2:  # Игнорируем очень короткие слова
                    topics_dict[lemma.lower()] = filename

    return topics_dict, file_to_topic


def add_cross_links(article_text, topics_dict, current_filename):
    """
    Добавляет перекрестные ссылки на связанные статьи

    Args:
        article_text: текст статьи
        topics_dict: словарь тем и их файлов
        current_filename: текущий файл (чтобы не ссылаться на себя)

    Returns:
        str: текст с добавленными ссылками
    """
    # Сортируем темы по длине (от длинных к коротким)
    sorted_topics = sorted(topics_dict.keys(), key=len, reverse=True)

    # Множество для хранения уже добавленных ссылок (чтобы не дублировать)
    added_links = set()

    for topic_word in sorted_topics:
        target_file = topics_dict[topic_word]

        # Не ссылаемся на самих себя
        if target_file == current_filename:
            continue

        # Создаем паттерн для поиска слова с границами слов
        # Используем re.escape для безопасного поиска
        pattern = r'\b' + re.escape(topic_word) + r'\b'

        def replace_match(match):
            word = match.group(0)

            # Проверяем, не создавали ли уже ссылку на этот файл
            link_key = f"{target_file}:{word}"
            if link_key in added_links:
                return word  # Уже есть ссылка на этот файл

            # Проверяем позицию слова
            pos = match.start()

            # Проверяем, не внутри ли уже Markdown ссылки
            text_before = article_text[max(0, pos - 100):pos]
            text_after = article_text[pos:pos + 100]

            # Пропускаем, если слово уже внутри ссылки
            if '](' in text_before or '![' in text_before:
                return word

            # Пропускаем, если после слова уже есть ссылка
            if '](' in text_after[:50]:
                return word

            # Добавляем в множество обработанных
            added_links.add(link_key)

            # Возвращаем слово с ссылкой
            return f"[{word}]({target_file})"

        # Применяем замену
        article_text = re.sub(pattern, replace_match, article_text, flags=re.IGNORECASE)

    return article_text


def process_all_articles(concepts_file):
    """
    Основная функция для обработки всех статей и добавления ссылок
    """
    print("=" * 50)
    print("Добавление перекрестных ссылок в статьи")
    print("=" * 50)

    # Загружаем данные
    data = load_concepts(concepts_file)
    first_section = data[0]
    concepts = first_section.get("concepts", [])

    # Создаем словарь тем
    topics_dict, file_to_topic = create_topics_dict(concepts_file)
    print(f"Найдено ключевых слов для ссылок: {len(topics_dict)}")

    # Статистика
    total_links_added = 0
    articles_processed = 0

    for concept in concepts:
        topic = concept.get("name", "")
        file_path = concept.get("file", "")

        if not topic or not file_path:
            continue

        # Формируем полный путь к файлу
        full_file_path = "../../../" + os.path.join(os.path.dirname(concepts_file), file_path)
        filename = os.path.basename(file_path)

        if not os.path.exists(full_file_path):
            print(f"❌ Файл не найден: {full_file_path}")
            continue

        print(f"\n📄 Обработка: {topic}")
        print(f"   Файл: {filename}")

        try:
            # Читаем статью
            with open(full_file_path, 'r', encoding='utf-8') as f:
                article = f.read()

            # Сохраняем длину для статистики
            original_length = len(article)

            # Добавляем ссылки
            new_article = add_cross_links(article, topics_dict, filename)

            # Считаем количество добавленных ссылок
            links_added = new_article.count('](') - article.count('](')
            total_links_added += links_added

            # Сохраняем обратно
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(new_article)

            print(f"   ✅ Добавлено ссылок: {links_added}")
            print(f"   📊 Размер: {original_length} → {len(new_article)} символов")

            articles_processed += 1

        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

    print("\n" + "=" * 50)
    print("ГОТОВО!")
    print(f"📊 Обработано статей: {articles_processed}")
    print(f"🔗 Всего добавлено ссылок: {total_links_added}")
    print("=" * 50)


def main():
    """Главная функция"""
    CONCEPTS_FILE = "../concepts.json"
    process_all_articles(CONCEPTS_FILE)


if __name__ == "__main__":
    main()