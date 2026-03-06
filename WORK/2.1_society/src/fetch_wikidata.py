import requests
import json
import os
from datetime import datetime


HEADERS = {
    'User-Agent': 'KidBook-Lab-Work/1.0 (https://github.com/cppdevelope/2026_kidbook; mailto:cppdevelope@example.com)',
    'Accept': 'application/json'
}


def get_wikidata_description(q_id):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{q_id}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return {'error': f'HTTP {response.status_code}'}
        data = response.json()
        entity = data['entities'][q_id]
        
        result = {}
        # Берём русское описание, если есть
        if 'descriptions' in entity and 'ru' in entity['descriptions']:
            result['description_ru'] = entity['descriptions']['ru']['value']
        else:
            result['description_ru'] = ''  # пустая строка, если нет описания
        
        # Берём русское название (label)
        if 'labels' in entity and 'ru' in entity['labels']:
            result['label_ru'] = entity['labels']['ru']['value']
        if 'labels' in entity and 'en' in entity['labels']:
            result['label_en'] = entity['labels']['en']['value']
        
        return result
    except Exception as e:
        return {'error': str(e), 'description_ru': ''}


def main():
    concepts_file = '../concepts.json'  # путь к вашему файлу
    
    if not os.path.exists(concepts_file):
        print(f"❌ Файл {concepts_file} не найден!")
        return
    
    with open(concepts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = []
    
    print("=" * 60)
    print("🔍 Получение данных из WikiData")
    print("=" * 60)
    print(f"Раздел: {data.get('section', 'N/A')}")
    print(f"Всего понятий: {len(data.get('concepts', []))}")
    print()
    
    success_count = 0
    error_count = 0
    
    for concept in data['concepts']:
        wid = concept.get('wikidata_id')
        label = concept.get('label', 'Unknown')
        local_desc = concept.get('description', '')
        
        if wid:
            print(f"  Запрос: {label} ({wid})")
            
            desc_data = get_wikidata_description(wid)
            
            # Для вывода в консоль используем локальное описание
            if local_desc:
                preview = local_desc[:50] + ('...' if len(local_desc) > 50 else '')
                print(f"    ✓ Локальное описание: {preview}")
            else:
                print(f"    ⚠️ Локальное описание отсутствует")
            
            # Если хотите видеть ещё и Wikidata описание (для справки), можно добавить:
            # if desc_data.get('description_ru'):
            #     print(f"      (WikiData: {desc_data['description_ru'][:50]}...)")
            
            result = {
                'concept_id': concept['id'],
                'label': label,
                'wikidata_id': wid,
                'local_description': local_desc,
                'wikidata_label_ru': desc_data.get('label_ru', ''),
                'wikidata_description_ru': desc_data.get('description_ru', ''),
                'wikidata_label_en': desc_data.get('label_en', '')
            }
            results.append(result)
            
            if 'error' in desc_data:
                error_count += 1
            else:
                success_count += 1
        else:
            print(f"  ⚠️ Пропущено: {label} (нет WikiData ID)")
    
    os.makedirs('../raw_data', exist_ok=True)
    output_file = '../raw_data/wikidata_export.json'
    
    export_data = {
        'export_date': datetime.now().isoformat(),
        'section': data.get('section', ''),
        'topic': data.get('topic', ''),
        'author_group': data.get('author_group', ''),
        'total_concepts': len(results),
        'success_count': success_count,
        'error_count': error_count,
        'concepts': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print(f"✅ Данные сохранены в {output_file}")
    print(f"📊 Успешно: {success_count} | Ошибок: {error_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()