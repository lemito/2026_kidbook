import os
import json
from datetime import datetime


def create_web_structure():
    concepts_file = '../concepts.json'
    
    with open(concepts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    web_base = '../../../WEB/14_team/rights_and_responsibilities'
    articles_dir = os.path.join(web_base, 'articles')
    images_dir = os.path.join(web_base, 'images')
    
    os.makedirs(articles_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    print("✅ Создана структура папок:")
    print(f"   {web_base}/")
    print(f"   ├── articles/")
    print(f"   └── images/")
    
    return data


def create_index_md(data):
    web_base = '../../../WEB/14_team/rights_and_responsibilities'
    
    table_rows = []
    for i, concept in enumerate(data['concepts'], 1):
        row = f"| {i} | [{concept['label']}](./articles/{concept['id']}.md) | {concept['description']} |"
        table_rows.append(row)
    
    content = f"""# {data['topic']}

**Раздел:** {data['section']}  
**Группа:** {data['author_group']}  
**Дата обновления:** {datetime.now().strftime('%Y-%m-%d')}

---

## 📖 О разделе

В этом разделе ты узнаешь о своих правах и обязанностях как гражданина. 
Мы расскажем простыми словами о важных вещах: что такое закон, почему нужно 
учиться в школе, и кто защищает твои права.

## 📚 Содержание

| № | Понятие | Краткое описание |
|---|---------|------------------|
{chr(10).join(table_rows)}

## 🔗 Полезные ссылки

- [Словарь терминов](./glossary.md) — все понятия в одном месте
- [WikiData](https://www.wikidata.org/) — база знаний, которую мы использовали
- [Вернуться к оглавлению](../../README.md)

---

*Сгенерировано с помощью ИИ • Раздел 2.1 • 2026*
"""
    
    filepath = os.path.join(web_base, 'index.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Создан файл: {filepath}")


def create_glossary_md(data):
    web_base = '../../../WEB/14_team/rights_and_responsibilities'
    
    table_rows = []
    for concept in sorted(data['concepts'], key=lambda x: x['label']):
        row = f"| **{concept['label']}** | {concept['description']} | [Читать](./articles/{concept['id']}.md) |"
        table_rows.append(row)
    
    content = f"""# Словарь терминов раздела 2.1

**Раздел:** {data['topic']}  
**Всего понятий:** {len(data['concepts'])}

---

## А-Я

| Понятие | Определение | Ссылка |
|---------|-------------|--------|
{chr(10).join(table_rows)}

---

## 📊 Статистика

| Метрика | Значение |
|---------|----------|
| Всего понятий | {len(data['concepts'])} |
| Источник данных | WikiData |
| Генерация текста | Qwen (OpenRouter) |
| Генерация изображений | Pollinations.ai |

---

*Словарь создан автоматически • 2026*
"""
    
    filepath = os.path.join(web_base, 'glossary.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Создан файл: {filepath}")


def main():
    print("=" * 60)
    print("🌐 Инициализация структуры WEB")
    print("=" * 60)
    
    data = create_web_structure()
    create_index_md(data)
    create_glossary_md(data)
    
    print()
    print("=" * 60)
    print("✅ Готово! Структура WEB создана.")
    print("   Теперь можно запускать generate_content.py")
    print("=" * 60)


if __name__ == "__main__":
    main()