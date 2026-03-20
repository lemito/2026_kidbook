# SPARQL-запросы к Wikidata

Endpoint: https://query.wikidata.org/

## 1) Поиск кандидатов по понятиям нашей темы (EntitySearch + фильтрация шума)
Запрос ищет кандидатов по терминам и отсекает типичные омонимы (фильмы, география, дизамбиги).

```sparql
SELECT DISTINCT ?term ?item ?itemLabel ?itemDescription ?rank WHERE {
  VALUES ?term {
    "бюджет"
    "доход"
    "расход"
    "потребность"
    "желание"
    "накопления"
    "финансовая цель"
    "цена"
    "скидка"
    "сравнение"
    "качество"
    "чек"
    "карманные деньги"
    "наличные"
    "банковская карта"
    "импульсивная покупка"
  }

  SERVICE wikibase:mwapi {
    bd:serviceParam wikibase:api "EntitySearch";
                    wikibase:endpoint "www.wikidata.org";
                    mwapi:search ?term;
                    mwapi:language "ru";
                    mwapi:limit "25".
    ?item wikibase:apiOutputItem mwapi:item.
    ?rank wikibase:apiOrdinal true.
  }

  OPTIONAL {
    ?item schema:description ?itemDescription.
    FILTER(LANG(?itemDescription) = "ru")
  }

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru".
  }

  FILTER(?rank <= 10)

  FILTER(
    !BOUND(?itemDescription) ||
    REGEX(LCASE(?itemDescription), "финанс|деньг|расход|доход|бюджет|цена|скидк|сбереж|накоп|плат|покуп|карта|чек")
  )

  FILTER(!REGEX(LCASE(STR(COALESCE(?itemLabel, ""))),
    "фильм|film|album|альбом|поэма|poem|river|река|станци|municipality|фамили|manga|disambiguation|страница значений|доходный дом|доходное|комитет"))

  FILTER(!REGEX(LCASE(STR(COALESCE(?itemDescription, ""))),
    "film|фильм|альбом|поэма|poem|municipality|river|станц|населенный пункт|disambiguation|страница значений|manga|webcomic|essay"))
}
ORDER BY ?term ?rank
```

## 2) Проверка карточек финальных сущностей (стабильный запрос)
Запрос возвращает только выбранные сущности темы и их базовые признаки: класс, родительский класс, описание.

```sparql
SELECT ?item ?itemLabel
       (GROUP_CONCAT(DISTINCT ?instanceOfLabel; separator=", ") AS ?instanceOfList)
       (GROUP_CONCAT(DISTINCT ?subclassOfLabel; separator=", ") AS ?subclassOfList)
       (SAMPLE(?itemDescription) AS ?itemDescription) WHERE {
  VALUES ?item {
    wd:Q41263    # budget
    wd:Q1527264  # income
    wd:Q28754054 # consumption/expense (use as expense proxy)
    wd:Q160151   # price
    wd:Q291046   # discount
    wd:Q693464   # cash
    wd:Q806806   # bank card
    wd:Q80042    # cheque
    wd:Q1629885  # store of value / savings proxy
    wd:Q190258   # need
    wd:Q241625   # desire
    wd:Q185957   # quality
    wd:Q1720648  # comparison
  }

  OPTIONAL { ?item wdt:P31 ?instanceOf. }
  OPTIONAL { ?item wdt:P279 ?subclassOf. }
  OPTIONAL {
    ?item schema:description ?itemDescription.
    FILTER(LANG(?itemDescription) = "ru")
  }

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en".
  }
}
GROUP BY ?item ?itemLabel
ORDER BY ?itemLabel
```

## 3) Связи выбранных сущностей с близкими понятиями
Запрос показывает осмысленные связи выбранных сущностей с их классами и смежными понятиями.

```sparql
SELECT DISTINCT ?source ?sourceLabel ?propLabel ?target ?targetLabel WHERE {
  VALUES ?source {
    wd:Q41263    # budget
    wd:Q1527264  # income
    wd:Q28754054 # expense proxy
    wd:Q160151   # price
    wd:Q291046   # discount
    wd:Q693464   # cash
    wd:Q806806   # bank card
    wd:Q80042    # cheque
    wd:Q1629885  # savings proxy
    wd:Q190258   # need
    wd:Q241625   # desire
    wd:Q185957   # quality
    wd:Q1720648  # comparison
  }

  VALUES ?p {
    wdt:P31      # instance of
    wdt:P279     # subclass of
    wdt:P361     # part of
    wdt:P527     # has part(s)
    wdt:P1889    # different from
    wdt:P1269    # facet of
  }

  ?source ?p ?target .
  FILTER(isIRI(?target))
  ?prop wikibase:directClaim ?p .

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en".
  }

  FILTER(!REGEX(LCASE(STR(COALESCE(?targetLabel, ""))),
    "фильм|album|manga|поэма|река|город|муниципал|станци|комитет|webcomic"))
}
ORDER BY ?sourceLabel ?propLabel ?targetLabel
LIMIT 200
```