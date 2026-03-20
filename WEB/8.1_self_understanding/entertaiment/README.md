# Развлечения: игры, фильмы и [музыка](articles/music.md) — [баланс](../7.2_leisure/useful_and_interesting_leisure/articles/balance_study_rest_hobby.md) пользы и развлечения

## Описание направления

Раздел детской энциклопедии, посвящённый играм, фильмам и музыке. Основная идея — объяснить ребёнку 10 лет, что развлечения могут быть не только весёлыми, но и полезными, а также научить находить баланс между удовольствием и пользой.

## Онтология предметной области

### [Визуализация](../how_to_memorize/articles/vizualizaciya.md) (Mermaid)

```mermaid
graph TD
    ENT["🎭 Развлечения"]

    ENT --> GAMES["🎮 Видеоигры"]
    ENT --> FILMS["🎬 Кино"]
    ENT --> MUSIC["🎵 Музыка"]

    %% Игры
    GAMES --> HOG["История видеоигр<br/>(Q941220)"]
    GAMES --> GGEN["Жанры видеоигр<br/>(Q659563)"]
    GAMES --> BG["Настольные игры<br/>(Q131436)"]
    GAMES --> ES["Киберспорт<br/>(Q300920)"]
    GAMES --> GAMB["Азартные игры и вред<br/>(Q133323)"]
    GAMES --> GM["Геймификация<br/>(Q1145661)"]

    %% Музыка
    MUSIC --> MUS["Понятие музыки<br/>(Q638)"]
    MUSIC --> HM["История музыки<br/>(Q188451)"]
    MUSIC --> PM["Влияние музыки<br/>(Q886424)"]
    MUSIC --> COMP["Композитор<br/>(Q36834)"]
    MUSIC --> MGEN["Жанры музыки<br/>(Q188451)"]
    MUSIC --> MINST["Музыкальные инструменты<br/>(Q34379)"]

    %% Кино
    FILMS --> MOV["Фильм<br/>(Q11424)"]
    FILMS --> DIR["Режиссёр<br/>(P57)"]
    FILMS --> SCR["Сценарий<br/>(Q103076)"]
    FILMS --> ST["Саундтрек<br/>(Q217199)"]
    FILMS --> MONT["Монтаж<br/>(Q237893)"]
    FILMS --> SFX["Спецэффекты<br/>(Q8317)"]
    FILMS --> AN["Мультфильм<br/>(Q202866)"]
    FILMS --> DOC["Документальный фильм<br/>(Q93204)"]

    %% Медиаграмотность
    ML["📚 Медиаграмотность<br/>(Q1004817)"]
    DOC -.->|развивает| ML
    AN -.->|развивает| ML

    %% Горизонтальные связи
    ST -.->|звучит в| MOV
    ST -.->|звучит в| GAMES
    DIR -.->|снимает| MOV
    SCR -.->|основа для| MOV
    MONT -.->|часть производства| MOV
    SFX -.->|используется в| MOV
    PM -.->|влияние на| GAMES
    PM -.->|влияние на| FILMS
    GM -.->|применяется в| EDUC["Обучение"]

    %% Стили
    classDef games fill:#e8f5e9,stroke:#388e3c
    classDef films fill:#e3f2fd,stroke:#1976d2
    classDef music fill:#fce4ec,stroke:#c62828
    classDef general fill:#fff9c4,stroke:#f9a825

    class GAMES,HOG,GGEN,BG,ES,GAMB,GM games
    class FILMS,MOV,AN,DOC,DIR,SCR,ST,MONT,SFX films
    class MUSIC,MUS,HM,PM,COMP,MGEN,MINST music
    class ENT,ML,EDUC general
```

### Описание связей

| Тип связи | Обозначение | Примеры |
|-----------|-------------|---------|
| **Иерархическая** (подвид / включает) | Сплошная линия → | Развлечение → [Фильм](articles/movie.md); Фильм → [Мультфильм](articles/animation.md) |
| **Горизонтальная** (влияет / использует) | Пунктирная линия -.-> | Фильмы ↔ Игры (экранизации); Песня → Фильм ([саундтрек](articles/soundtrack.md)) |
| **Функциональная** (требует / развивает) | Пунктирная линия -.-> | Развлечение → [Медиаграмотность](../5.1_technology_and_digital_literacy/information and media literacy/что_такое_информационная_и_медиаграмотность.md) |

### Список понятий

| # | Понятие | WikiData | Категория | Файл |
|---|---------|----------|-----------|------|
| 1 | [История видеоигр](articles/history-of-games.md) | [Q941220](https://www.wikidata.org/wiki/Q941220) | Игры | `articles/history-of-games.md` |
| 2 | Жанры видеоигр | [Q659563](https://www.wikidata.org/wiki/Q659563) | Игры | `articles/game-genres.md` |
| 3 | [Настольные игры](../7.2_leisure/useful_and_interesting_leisure/articles/board_and_intellectual_games.md) | [Q131436](https://www.wikidata.org/wiki/Q131436) | Игры | `articles/board-games.md` |
| 4 | [Киберспорт](../7.2_leisure/useful_and_interesting_leisure/articles/computer_games_with_benefit.md) | [Q300920](https://www.wikidata.org/wiki/Q300920) | Игры | `articles/esports.md` |
| 5 | Азартные игры и их [вред](../3.1. healthy lifestyle/Sleep, nutrition, and adolescent energy/articles/the_energy_trap.md) | [Q133323](https://www.wikidata.org/wiki/Q133323) | Игры | `articles/gambling-and-harm.md` |
| 6 | [Геймификация](articles/gamification.md) | [Q1145661](https://www.wikidata.org/wiki/Q1145661) | Игры | `articles/gamification.md` |
| 7 | [Композитор](articles/composer.md) | [Q36834](https://www.wikidata.org/wiki/Q36834) | Музыка | `articles/composer.md` |
| 8 | Жанры музыки | [Q188451](https://www.wikidata.org/wiki/Q188451) | Музыка | `articles/music_genres.md` |
| 9 | Музыкальные инструменты | [Q34379](https://www.wikidata.org/wiki/Q34379) | Музыка | `articles/musical_instruments.md` |
| 10 | Понятие музыки и её устройство | [Q638](https://www.wikidata.org/wiki/Q638) | Музыка | `articles/music.md` |
| 11 | [История музыки](articles/history_of_music.md) | [Q188451](https://www.wikidata.org/wiki/Q188451) | Музыка | `articles/history_of_music.md` |
| 12 | [Влияние музыки](articles/psychology_of_music.md) на человека | [Q886424](https://www.wikidata.org/wiki/Q886424) | Музыка | `articles/psychology_of_music.md` |
| 13 | [Режиссёр](articles/director.md) | [P57](https://www.wikidata.org/wiki/Property:P57) | Фильмы | `articles/director.md` |
| 14 | [Сценарий](articles/script.md) | [Q103076](https://www.wikidata.org/wiki/Q103076) | Фильмы | `articles/script.md` |
| 15 | Саундтрек | [Q217199](https://www.wikidata.org/wiki/Q217199) | Фильмы | `articles/soundtrack.md` |
| 16 | Фильм | [Q11424](https://www.wikidata.org/wiki/Q11424) | Фильмы | `articles/movie.md` |
| 17 | [Спецэффекты](articles/special_effects.md) | [Q8317](https://www.wikidata.org/wiki/Q8317) | Фильмы | `articles/special_effects.md` |
| 18 | [Монтаж](../5.1_technology_and_digital_literacy/information and media literacy/оценка_качества_изображений_и_видео.md) | [Q237893](https://www.wikidata.org/wiki/Q237893) | Фильмы | `articles/montage.md` |
| 19 | Мультфильм | [Q202866](https://www.wikidata.org/wiki/Q202866) | Фильмы | `articles/animation.md` |
| 20 | [Документальный фильм](articles/documentary.md) | [Q93204](https://www.wikidata.org/wiki/Q93204) | Фильмы | `articles/documentary.md` |
| 21 | Медиаграмотность | [Q1004817](https://www.wikidata.org/wiki/Q1004817) | Общее | `articles/media_literacy.md` |

## Источники знаний

### WikiData / SPARQL

Для каждого понятия из таблицы выше были извлечены [данные](../2.1_society/cause_and_effect_relationships/articles/ai_causality.md) из WikiData с помощью SPARQL-запросов:
- Метки и описания на русском/английском языках
- Иерархические связи (P279 — subclass of, P31 — instance of)
- Связанные сущности (P136 — [жанр](articles/movie.md), P737 — influenced by и др.)

Скрипт: [`wikidata_extract.py`](wikidata_extract.py)

[Результаты](../1.2_natural_sciences/why_science_help_understand_world/research_work.md): директория [`wikidata/`](wikidata/)

### Генерация текстов

Тексты энциклопедических статей сгенерированы с помощью **GigaChat API** (модель GigaChat, бесплатный лимит GIGACHAT_API_PERS).

Промпт-шаблон:
> **Системный**: "Ты [автор](../5.1_technology_and_digital_literacy/information and media literacy/авторское_право_и_честное_использование.md) детской энциклопедии для восьмиклассников. Пиши просто, интересно и понятно для десятилетнего ребёнка. Пиши развёрнуто, подробно раскрывая каждый раздел."
>
> **Пользователь**: "Напиши подробную статью для детской энциклопедии о понятии «{понятие}». Тема раздела: «Игры, фильмы и музыка: баланс пользы и развлечения». Описание: {description}. Содержание: введение, [история](../2.1_society/cause_and_effect_relationships/articles/lessons_of_history.md), [виды](../3.1_healthy_lifestyle/pervaya_pomoshch/ushibi_porezy_ozhogi/08_porezy_sadiny_vidy.md), интересные факты (3-5), примеры из жизни, [польза](../7.2_leisure/useful_and_interesting_leisure/articles/computer_games_with_benefit.md), [риски](../7.2_leisure/useful_and_interesting_leisure/articles/safety_during_recreation.md), баланс, заключение. Используй WikiData: {wikidata_context}. Ответ в формате markdown."

Параметры: `temperature=0.7`, `max_tokens=3000`

Скрипт: [`generate_pages.py`](generate_pages.py)

### Перекрёстные ссылки

Ссылки между понятиями расставлены автоматически скриптом [`crosslink.py`](crosslink.py), который:
1. Загружает `concepts.json` со всеми падежными формами понятий
2. В каждом markdown-файле находит вхождения форм других понятий
3. Заменяет первое вхождение каждого понятия на markdown-ссылку `[форма](файл.md)`
4. Не заменяет понятие внутри собственной статьи и в заголовках

Для работы с падежами используется библиотека `pymorphy3`.


## Участники группы

| # | ФИО | Понятия |
|---|-----|---------|
| 1 | Долбус Дмитрий | История видеоигр, Жанры видеоигр, Настольные игры, Киберспорт, Азартные игры и их вред, Геймификация |
| 2 | Хабирова Амина | Композитор, Жанры музыки, Музыкальные инструменты |
| 3 | Канева Юлия | Понятие музыки и её устройство, История музыки, Влияние музыки на человека |
| 4 | Хереш Артемий | Режиссёр, Сценарий, Саундтрек |
| 5 | Фролов Матвей | Фильм, Спецэффекты, Монтаж |
| 6 | Глушко Игорь | Мультфильм, Документальный фильм, Медиаграмотность |
