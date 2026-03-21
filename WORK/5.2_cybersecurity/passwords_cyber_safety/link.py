import json
import re
from pathlib import Path

def create_concept_map(json_path: Path):
    """Читает JSON и генерирует словарь лемм для поиска (строго по списку из файла)."""
    with open(json_path, 'r', encoding='utf-8') as file:
        raw_data = json.load(file)

    concept_map = {}

    for item in raw_data:
        target_link = f"./{item['name']}.md"
        
        # Берем ТОЛЬКО те леммы, которые явно указаны в concepts.json
        for lemma in item.get('lemmas', []):
            lemma_lower = lemma.lower()
            if len(lemma_lower) > 2: # Игнорируем слишком короткие слова (на всякий случай)
                concept_map[lemma_lower] = {'link': target_link, 'title': item['name']}
                
    return concept_map

def process_text_links(content: str, concept_map: dict, current_file_name: str):
    """Находит термины в тексте и оборачивает их в Markdown-ссылки."""
    
    # Разделяем текст на строки, чтобы не трогать заголовки и метаданные
    lines = content.split('\n')
    processed_lines = []
    
    # 1. Сортируем термины по убыванию длины
    sorted_terms = sorted(concept_map.keys(), key=len, reverse=True)

    for line in lines:
        # Пропускаем заголовки, метаданные, списки и блок "Коротко"
        if line.startswith('#') or line.startswith('**') or line.startswith('💡') or line.startswith('![') or line.startswith('>'):
            processed_lines.append(line)
            continue
            
        # Прячем уже существующие ссылки в текущей строке
        existing_links = []
        def hide_link(m):
            existing_links.append(m.group(0))
            return f"__HIDDEN_LINK_{len(existing_links)-1}__"
        
        line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', hide_link, line)

        # Ищем совпадения
        for term in sorted_terms:
            concept_info = concept_map[term]
            concept_id = concept_info['title']
            
            # Не ссылаемся на саму себя
            if concept_id == current_file_name:
                continue
                
            pattern = r'\b' + re.escape(term) + r'\b'
            
            # Заменяем все вхождения термина в строке
            if re.search(pattern, line, flags=re.IGNORECASE):
                def mark_term(m):
                    matched = m.group(0)
                    return f"[{matched}]({concept_info['link']})"
                
                line = re.sub(pattern, mark_term, line, flags=re.IGNORECASE)

        # Возвращаем спрятанные ссылки на место
        for idx, link in enumerate(existing_links):
            line = line.replace(f"__HIDDEN_LINK_{idx}__", link)
            
        processed_lines.append(line)

    return '\n'.join(processed_lines)

def main():
    # Используем pathlib для более современного и чистого кода
    root_dir = Path(__file__).resolve().parent.parent.parent
    concepts_file = Path(__file__).resolve().parent / 'concepts.json'
    articles_dir = root_dir / 'WEB' / '5.2_cybersecurity' / 'passwords_cyber_safety' / 'articles'

    print("Старт процесса линковки терминов...")
    
    if not concepts_file.exists():
        print(f"Файл {concepts_file} не найден!")
        return

    c_map = create_concept_map(concepts_file)
    print(f"Сгенерировано {len(c_map)} словоформ для поиска.")

    for md_file in articles_dir.glob('*.md'):
        text = md_file.read_text(encoding='utf-8')
        
        # Передаем имя текущего файла (без .md), чтобы не ссылаться на саму себя
        current_name = md_file.stem 
        updated_text = process_text_links(text, c_map, current_name)

        if text != updated_text:
            md_file.write_text(updated_text, encoding='utf-8')
            print(f"  [+] Обновлен файл: {md_file.name}")
        else:
            print(f"  [-] Без изменений: {md_file.name}")

    print("Линковка успешно завершена!")

if __name__ == "__main__":
    main()