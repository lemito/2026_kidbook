import requests
import json

def search_wikidata(query):
    """Поиск WikiData ID по названию"""
    url = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'ru',
        'type': 'item',
        'search': query
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'search' in data and data['search']:
        print(f"\nРезультаты для '{query}':")
        for item in data['search'][:3]:
            print(f"  • {item['label']} (ID: {item['id']})")
            if 'description' in item:
                print(f"    {item['description']}")
        return data['search'][0]['id'] if data['search'] else None
    return None

# Пример использования
if __name__ == "__main__":
    concepts = ["пиксель", "геймпад", "косплей"]
    for concept in concepts:
        search_wikidata(concept)
