
import os
import re

import tqdm
import json
import  pymorphy3

from dotenv import load_dotenv
from gigachat import GigaChat
from SPARQLWrapper import SPARQLWrapper, JSON


load_dotenv()


def get_wikidata_entity_id(topic, lang='ru'):
    """Поиск Q-кода сущности в Wikidata по названию."""
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f'''
    SELECT ?entity WHERE {{
      ?entity rdfs:label "{topic}"@{lang}.
    }} LIMIT 1
    '''
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    if results["results"]["bindings"]:
        entity_uri = results["results"]["bindings"][0]["entity"]["value"]
        qid = entity_uri.split('/')[-1]
        return qid
    return None

def get_wikidata_properties(qid, lang='ru'):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f'''
    SELECT ?prop ?propLabel ?value ?valueLabel WHERE {{
      wd:{qid} ?prop ?value.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{lang},en". }}
    }} LIMIT 100
    '''
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    properties = []
    for binding in results["results"]["bindings"]:
        prop_label = binding.get('propLabel', {}).get('value', binding['prop']['value'])
        value_label = binding.get('valueLabel', {}).get('value', binding['value']['value'])
        properties.append({
            'property': prop_label,
            'value': value_label
        })
    return properties

def create_article(promt: str, out_file_name: str):
    with GigaChat(credentials=os.getenv('API_KEY'), verify_ssl_certs=False) as giga:
        response = giga.chat(promt)
        with open(out_file_name, 'w', encoding='utf-8') as f:
            f.write(response.choices[0].message.content)



def create_articles(articles, article_file_names, second_promt_part: str):
    for i, article in enumerate(articles):
        qid = get_wikidata_entity_id(article)
        context = ''
        print(article, qid)
        if qid:
            props = get_wikidata_properties(qid)
            if props:
                facts = "\n".join([f"- {p['property']}: {p['value']}" for p in props[:10]])  # ограничим 10 фактов
                context = f"Вот известные факты об этой теме из базы знаний Wikidata:\n{facts}\n\n"

        full_prompt = (f'Создай статью о теме \"{article}\". {context}Используй приведённые факты для достоверности, '
                       f'но статью напиши развёрнуто и интересно. ' + second_promt_part)

        create_article(full_prompt,
                       article_file_names[i])


def split(text: str):
    out_array = []
    tmp = ''
    for i in text:
        if i.isalpha():
            tmp += i
        elif tmp != '':
            out_array.append(tmp)
            tmp = ''
            out_array.append(i)
        else:
            out_array.append(i)
    return out_array

def add_references(concept_file, path, path_links):
    concepts = []
    with open(concept_file, 'r', encoding='utf-8') as f:
       concepts = json.load(f)
    links = {}
    morph = pymorphy3.MorphAnalyzer()
    files = []
    for concept in concepts['concepts']:
        for lemma in concept['lemmas']:
            links[lemma] = path_links + concept['file']
        files.append([concept['file'], concept['author']])

    for file in files:
        article = path + file[0]
        with open(article, 'r+', encoding='utf-8') as f:
            src_text = f.read()
            dst_text = split(src_text)
            out_text = ''
            for l in dst_text:
                if l.isalpha():
                    src_l = morph.parse(l)[0].normal_form
                    if src_l in links.keys():
                        if file[0] not in links[src_l] and out_text[-1] != '[':
                            out_text += f'[{l}]({links[src_l]})'
                        else:
                            out_text += l
                    else:
                        out_text += l
                else:
                    out_text += l
            f.truncate(0)
            f.seek(0)
            f.write(out_text)
            if f'Авторы:' not in out_text:
                f.write('\n\n---\n\n' + f'Авторы: @{file[1]}\n\nРесурсы LLM - Gigachat')



# create_articles(['спецэффекты', 'монтаж', 'фильм'],
#                 [
#                     '../articles/special_effects.md',
#                     '../articles/montage.md',
#                     '../articles/movie.md'
#                 ],
#                 'Сделай большую статью, кол-во слов от 1000. '
#                 'Убери риторические вопросы и формулировки "я/мы". Только нейтральные формулировки. '
#                 'Пиши для ребенка 10 летнего возраста. '
#                 'Однако должны быть четкие формулировки, чтобы не было двойственности.'
#                 'Оформи ответ в виде .md формата для github.'
#                 'В начале статьи напиши тему как в промте(не жирным текстом). Убери смайлики и сделай строгое оформление'
#                 )
# #


create_articles(['сценарий', 'режиссёр', 'саундтрек'],
                [
                    '../articles/script.md',
                    '../articles/director.md',
                    '../articles/soundtrack.md'
                ],
                'Сделай большую статью, кол-во слов от 1000. '
                'Убери риторические вопросы и формулировки "я/мы". Только нейтральные формулировки. '
                'Пиши для ребенка 10 летнего возраста. '
                'Однако должны быть четкие формулировки, чтобы не было двойственности.'
                'Оформи ответ в виде .md формата для github.'
                'В начале статьи напиши тему как в промте(не жирным текстом). Убери смайлики и сделай строгое оформление'
                )



add_references('../concepts.json', '../articles/', './')
