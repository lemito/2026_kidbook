import json
import os
import re
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter

# --- Настройки путей ---
WORK_DIR = "./LABS/AI/lab1/2026_kidbook_153/WORK/2.1_society/how_and_where_find_friends"
WEB_BASE_DIR = "./LABS/AI/lab1/2026_kidbook_153/WEB"
CONCEPTS_FILE = os.path.join(WORK_DIR, "concepts.json")
REPORT_FILE = os.path.join(WORK_DIR, "linking_suggestions_hybrid.md")

# Параметры поиска
SIMILARITY_THRESHOLD = 0.12
MAX_LINKS = 20
LEMMA_WEIGHT = 0.35     # Вес для подхода "леммы vs статья"
ARTICLE_WEIGHT = 0.65   # Вес для подхода "статья vs статья"

def get_all_md_files(base_directory):
    """Рекурсивно находит все .md файлы."""
    documents = []
    md_files = glob.glob(os.path.join(base_directory, "**/*.md"), recursive=True)
    
    print(f"Найдено .md файлов: {len(md_files)}")
    
    for full_path in md_files:
        try:
            rel_path = os.path.relpath(full_path, base_directory)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Извлекаем заголовок
                title = extract_title_from_md(content)
                if not title:
                    title = os.path.basename(full_path).replace(".md", "").replace("_", " ").title()
                
                # Очищаем контент для анализа
                clean_content = clean_text(content)
                
                documents.append({
                    "full_path": full_path,
                    "rel_path": rel_path,
                    "web_path": os.path.join("WEB", rel_path).replace("\\", "/"),
                    "title": title,
                    "content": content,
                    "clean_content": clean_content,
                    "filename": os.path.basename(full_path)
                })
        except Exception as e:
            print(f"Ошибка при чтении {full_path}: {e}")
    
    return documents

def extract_title_from_md(content):
    """Извлекает первый заголовок h1."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def clean_text(text):
    """Очищает текст от Markdown разметки."""
    # Убираем ссылки
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Убираем изображения
    text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
    # Убираем форматирование
    text = re.sub(r'[*_`#]', '', text)
    # Приводим к нижнему регистру
    text = text.lower()
    # Убираем лишние пробелы
    text = ' '.join(text.split())
    return text

def load_concepts(concepts_file, all_articles):
    """
    Загружает концепты и связывает их с соответствующими статьями.
    """
    with open(concepts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Создаем словарь для быстрого поиска статьи по пути
    article_by_path = {}
    for article in all_articles:
        article_by_path[article['web_path']] = article
        article_by_path[article['web_path'].replace('WEB/', '')] = article
        article_by_path[os.path.basename(article['full_path'])] = article
    
    concepts_with_articles = []
    
    for section in data:
        section_name = section.get("section", "Без раздела")
        for concept in section.get("concepts", []):
            # Ищем соответствующую статью
            concept_file = concept.get("file", "")
            source_article = None
            
            for key in [concept_file, os.path.basename(concept_file)]:
                if key in article_by_path:
                    source_article = article_by_path[key]
                    break
            
            if source_article:
                # Собираем текст для анализа (название + леммы + описание)
                analysis_text = f"{concept.get('name', '')} {' '.join(concept.get('lemmas', []))} {concept.get('description', '')}"
                analysis_text = clean_text(analysis_text)
                
                concepts_with_articles.append({
                    "id": concept["id"],
                    "name": concept["name"],
                    "file": concept["file"],
                    "lemmas": concept.get("lemmas", []),
                    "description": concept.get("description", ""),
                    "analysis_text": analysis_text,
                    "section": section_name,
                    "author": concept.get("author", "Неизвестен"),
                    "source_article": source_article
                })
            else:
                print(f"⚠️ Не найдена статья для концепта: {concept['name']} ({concept['file']})")
    
    return concepts_with_articles

def find_related_by_lemmas(concept, all_articles, vectorizer, article_vectors, top_n=MAX_LINKS):
    """
    Подход 1: Поиск по леммам (концепт -> статьи)
    """
    if not concept['analysis_text'].strip():
        return []
    
    # Векторизуем текст концепта
    concept_vector = vectorizer.transform([concept['analysis_text']])
    
    # Вычисляем схожесть со всеми статьями
    similarities = cosine_similarity(concept_vector, article_vectors).flatten()
    
    # Получаем индексы статей с схожестью выше порога
    similar_indices = np.where(similarities >= SIMILARITY_THRESHOLD)[0]
    similar_indices = similar_indices[np.argsort(similarities[similar_indices])[::-1]]
    
    # Формируем результаты
    results = []
    for idx in similar_indices[:top_n]:
        # Проверяем, что это не исходная статья
        if all_articles[idx]['full_path'] != concept['source_article']['full_path']:
            results.append({
                "article": all_articles[idx],
                "similarity": float(similarities[idx]),
                "method": "lemmas"
            })
    
    return results

def find_related_by_article(concept, all_articles, vectorizer, article_vectors, top_n=MAX_LINKS):
    """
    Подход 2: Поиск по полному тексту статьи (статья -> статья)
    """
    source_article = concept['source_article']
    
    # Находим индекс исходной статьи
    source_idx = None
    for i, article in enumerate(all_articles):
        if article['full_path'] == source_article['full_path']:
            source_idx = i
            break
    
    if source_idx is None:
        return []
    
    # Получаем вектор исходной статьи
    source_vector = article_vectors[source_idx]
    
    # Вычисляем схожесть со всеми статьями
    similarities = cosine_similarity(source_vector, article_vectors).flatten()
    
    # Получаем индексы статей с схожестью выше порога (исключая саму статью)
    similar_indices = []
    for i, sim in enumerate(similarities):
        if i != source_idx and sim >= SIMILARITY_THRESHOLD:
            similar_indices.append((i, sim))
    
    # Сортируем
    similar_indices.sort(key=lambda x: x[1], reverse=True)
    
    # Формируем результаты
    results = []
    for idx, sim in similar_indices[:top_n]:
        results.append({
            "article": all_articles[idx],
            "similarity": float(sim),
            "method": "article"
        })
    
    return results

def combine_recommendations(lemma_results, article_results, all_articles):
    """
    Комбинирует результаты двух подходов с весами.
    """
    combined = {}
    
    # Добавляем результаты по леммам
    for res in lemma_results:
        article_path = res['article']['full_path']
        combined[article_path] = {
            "article": res['article'],
            "lemma_score": res['similarity'],
            "article_score": 0,
            "methods": ["lemmas"]
        }
    
    # Добавляем/обновляем результаты по статьям
    for res in article_results:
        article_path = res['article']['full_path']
        if article_path in combined:
            combined[article_path]['article_score'] = res['similarity']
            combined[article_path]['methods'].append("article")
        else:
            combined[article_path] = {
                "article": res['article'],
                "lemma_score": 0,
                "article_score": res['similarity'],
                "methods": ["article"]
            }
    
    # Вычисляем комбинированный score
    for path, data in combined.items():
        data['combined_score'] = (
            LEMMA_WEIGHT * data['lemma_score'] + 
            ARTICLE_WEIGHT * data['article_score']
        )
        
        # Бонус за совпадение по обоим методам
        if len(data['methods']) > 1:
            data['combined_score'] *= 1.2  # 20% бонус
            data['consensus'] = True
        else:
            data['consensus'] = False
    
    # Сортируем по комбинированному score
    sorted_results = sorted(
        combined.values(), 
        key=lambda x: x['combined_score'], 
        reverse=True
    )
    
    return sorted_results

def main():
    print("=" * 70)
    print("🔗 ГИБРИДНЫЙ АНАЛИЗ ПЕРЕЛИНКОВКИ")
    print("=" * 70)
    print(f"⚖️  Веса: Леммы={LEMMA_WEIGHT}, Статьи={ARTICLE_WEIGHT}")
    print(f"🎯 Порог схожести: {SIMILARITY_THRESHOLD}")
    
    # 1. Загружаем все статьи
    print("\n📂 Загрузка всех статей из WEB...")
    all_articles = get_all_md_files(WEB_BASE_DIR)
    print(f"✅ Загружено статей: {len(all_articles)}")
    
    if not all_articles:
        print("❌ Статьи не найдены")
        return
    
    # 2. Загружаем концепты и связываем со статьями
    print("\n📂 Загрузка концептов...")
    if not os.path.exists(CONCEPTS_FILE):
        print(f"❌ Файл {CONCEPTS_FILE} не найден")
        return
    
    concepts = load_concepts(CONCEPTS_FILE, all_articles)
    print(f"✅ Загружено концептов со статьями: {len(concepts)}")
    
    if not concepts:
        print("❌ Нет концептов с привязанными статьями")
        return
    
    # 3. Векторизация всех статей
    print("\n🔄 Вычисление TF-IDF векторов...")
    
    # Подготавливаем тексты
    article_texts = []
    for article in all_articles:
        # Удваиваем название для повышения его важности
        text = f"{article['title']} {article['title']} {article['clean_content']}"
        article_texts.append(text)
    
    vectorizer = TfidfVectorizer(
        max_features=5000,
        min_df=2,
        max_df=0.8,
        ngram_range=(1, 2),
        stop_words=['это', 'как', 'что', 'для', 'в', 'на', 'с', 'по', 'и', 'не', 'весь', 'мочь', 'быть']
    )
    
    article_vectors = vectorizer.fit_transform(article_texts)
    print(f"   Размерность матрицы: {article_vectors.shape}")
    
    # 4. Гибридный поиск связей
    print("\n🔗 Гибридный поиск связей...")
    
    all_suggestions = []
    method_stats = {"lemmas": 0, "article": 0, "both": 0}
    
    for i, concept in enumerate(concepts):
        if i % 5 == 0:
            print(f"   Обработано {i}/{len(concepts)} концептов")
        
        # Поиск обоими методами
        lemma_results = find_related_by_lemmas(concept, all_articles, vectorizer, article_vectors, top_n=MAX_LINKS)
        article_results = find_related_by_article(concept, all_articles, vectorizer, article_vectors, top_n=MAX_LINKS)
        
        # Комбинируем результаты
        combined = combine_recommendations(lemma_results, article_results, all_articles)
        
        # Статистика по методам
        for res in combined[:MAX_LINKS]:
            if len(res['methods']) > 1:
                method_stats["both"] += 1
            else:
                method_stats[res['methods'][0]] += 1
        
        if combined:
            all_suggestions.append({
                "concept": concept,
                "recommendations": combined[:MAX_LINKS]
            })
    
    print(f"✅ Найдено связей для {len(all_suggestions)} концептов")
    
    # 5. Генерация отчета
    print("\n📝 Генерация гибридного отчета...")
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as md:
        md.write("# 🔗 ГИБРИДНЫЙ ОТЧЕТ ПО ПЕРЕЛИНКОВКЕ\n\n")
        md.write(f"*Дата генерации: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
        
        # Методология
        md.write("## 🎯 Методология\n\n")
        md.write("Комбинируются два подхода:\n\n")
        md.write("1. **Леммы → Статьи** (30% веса): Поиск по ключевым словам из концепта\n")
        md.write("2. **Статья → Статья** (70% веса): Полнотекстовый поиск похожих статей\n")
        md.write("3. **Бонус +20%** за совпадение по обоим методам\n\n")
        
        # Статистика
        md.write("## 📊 Статистика\n\n")
        md.write(f"- **Всего статей в WEB:** {len(all_articles)}\n")
        md.write(f"- **Всего концептов со статьями:** {len(concepts)}\n")
        md.write(f"- **Концептов с рекомендациями:** {len(all_suggestions)} ({len(all_suggestions)/len(concepts)*100:.1f}%)\n")
        md.write(f"- **Порог схожести:** {SIMILARITY_THRESHOLD}\n\n")
        
        md.write("### Распределение рекомендаций по методам:\n\n")
        md.write(f"- 🎯 Только по леммам: {method_stats['lemmas']}\n")
        md.write(f"- 📄 Только по статье: {method_stats['article']}\n")
        md.write(f"- ⭐ Совпадение (оба метода): {method_stats['both']}\n\n")
        
        # Детальные рекомендации
        md.write("## 🔗 Рекомендуемые связи\n\n")
        
        for item in all_suggestions:
            concept = item["concept"]
            source = concept["source_article"]
            
            md.write(f"### 📄 {concept['name']}\n\n")
            md.write(f"- **ID:** `{concept['id']}`\n")
            md.write(f"- **Файл:** `../../../{concept['file']}`\n")
            md.write(f"- **Раздел:** {concept['section']}\n")
            md.write(f"- **Автор:** {concept['author']}\n\n")
            
            if concept['lemmas']:
                md.write(f"**Леммы:** {', '.join(concept['lemmas'][:10])}\n\n")
            
            md.write(f"**Исходная статья:** [{source['title']}](../../../{source['web_path']})\n\n")
            
            md.write("#### 📚 Рекомендуемые связанные статьи:\n\n")
            
            for rank, rec in enumerate(item["recommendations"], 1):
                article = rec["article"]
                
                # Индикатор метода
                if len(rec['methods']) > 1:
                    method_badge = "⭐ КОНСЕНСУС"
                    color = "🟣"
                elif rec['methods'][0] == "lemmas":
                    method_badge = "🎯 По леммам"
                    color = "🔵"
                else:
                    method_badge = "📄 По статье"
                    color = "🟢"
                
                # Оценка силы связи
                if rec['combined_score'] > 0.3:
                    strength = "🔴 Сильная"
                elif rec['combined_score'] > 0.2:
                    strength = "🟡 Средняя"
                else:
                    strength = "🟢 Слабая"
                
                md.write(f"{rank}. **[{article['title']}](../../../{article['web_path']})**\n")
                md.write(f"   - Путь: `../../../{article['web_path']}`\n")
                md.write(f"   - Комбинированная схожесть: `{rec['combined_score']:.3f}` ({strength})\n")
                md.write(f"   - Леммы: `{rec['lemma_score']:.3f}` | Статья: `{rec['article_score']:.3f}`\n")
                md.write(f"   - Метод: {color} {method_badge}\n\n")
            
            # HTML для вставки
            md.write("#### 📋 HTML для вставки:\n\n")
            md.write("```html\n")
            md.write('<div class="related-articles">\n')
            md.write('  <h3>Читайте также</h3>\n')
            md.write('  <ul>\n')
            
            for rec in item["recommendations"][:5]:  # Топ-5 для вставки
                article = rec["article"]
                md.write(f'    <li><a href="../../../{article["web_path"]}">{article["title"]}</a></li>\n')
            
            md.write('  </ul>\n')
            md.write('</div>\n')
            md.write("```\n\n")
            
            md.write("---\n\n")
    
    print(f"✅ Гибридный отчет сохранен: {REPORT_FILE}")
    
    # Финальная статистика
    total_recs = sum(len(item['recommendations']) for item in all_suggestions)
    print("\n" + "=" * 70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)
    print(f"Всего проанализировано статей: {len(all_articles)}")
    print(f"Концептов с рекомендациями: {len(all_suggestions)}")
    print(f"Всего рекомендаций: {total_recs}")
    print(f"Среднее рекомендаций на концепт: {total_recs/len(concepts):.2f}")
    print(f"\nРаспределение по методам:")
    print(f"  🎯 Только леммы: {method_stats['lemmas']}")
    print(f"  📄 Только статья: {method_stats['article']}")
    print(f"  ⭐ Консенсус: {method_stats['both']}")

if __name__ == "__main__":
    main()