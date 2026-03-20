# SPARQL-запросы к DBpedia

Endpoint: https://dbpedia.org/sparql

## 1) Иерархия категорий про финансовую грамотность
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?cat ?catLabel ?broader ?broaderLabel WHERE {
  ?cat skos:broader ?broader ;
       rdfs:label ?catLabel .
  ?broader rdfs:label ?broaderLabel .

  FILTER(lang(?catLabel) = "en" && lang(?broaderLabel) = "en")

  FILTER(
    ?cat = <http://dbpedia.org/resource/Category:Personal_finance> ||
    ?broader = <http://dbpedia.org/resource/Category:Personal_finance>
  )

  FILTER(!REGEX(LCASE(STR(?catLabel)), "minister|country|journal|history|continent|asia"))
  FILTER(!REGEX(LCASE(STR(?broaderLabel)), "minister|country|journal|history|continent|asia"))
}
LIMIT 100
```
