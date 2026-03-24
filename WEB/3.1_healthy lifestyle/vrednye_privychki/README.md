# Вредные [привычки](../../1.2_natural_sciences/neurobiology_for_teens/articles/11_reward_system.md)

**Раздел:** 3.1. [Здоровый образ жизни](articles/profilaktika.md) → Вредные привычки  
**[Команда](../../4.1_rules_of_study/how_to_learn_effectively/articles/peer_learning.md):** 777  
**Дата обновления:** 2026-03-19

---

## 📖 Описание направления

Раздел детской энциклопедии, посвящённый вредным привычкам. Основная идея — объяснить ребёнку 10 лет, что такое вредные привычки, как они формируются, почему они опасны и как от них защититься. Тексты написаны простым и доступным языком с использованием примеров из жизни.

## 🧠 Онтология предметной области

```mermaid
graph TD
    VP["🚫 Вредные привычки"]

    VP --> SUBSTANCE["🧪 Вещества"]
    VP --> MECHANISM["🧠 Механизмы зависимости"]
    VP --> DIGITAL["📱 Цифровые зависимости"]
    VP --> LIFESTYLE["🛋️ Образ жизни"]
    VP --> SHIELD["🛡️ Профилактика"]

    %% Вещества
    SUBSTANCE --> SMOKING["Курение"]
    SUBSTANCE --> ALCOHOL["Алкоголь"]
    SUBSTANCE --> ENERGY["Энергетики"]
    SUBSTANCE --> DRUGS_MYTHS["Мифы о наркотиках"]
    SUBSTANCE --> OVERDOSE["Передозировка"]

    %% Механизмы
    MECHANISM --> DOPAMINE["Дофаминовая петля"]
    MECHANISM --> PERSONALITY["Как зависимость<br/>меняет личность"]

    %% Цифровые
    DIGITAL --> SOCIAL["Соцсети и FoMO"]
    DIGITAL --> DOOM["Думскроллинг"]
    DIGITAL --> GAMES["Комп. игры"]
    DIGITAL --> LUDO["Лудомания"]
    DIGITAL --> SHOP["Шопоголизм"]

    %% Образ жизни
    LIFESTYLE --> FASTFOOD["Фастфуд"]
    LIFESTYLE --> SEDENTARY["Малоподвижность"]
    LIFESTYLE --> SLEEP["Недосыпание"]
    LIFESTYLE --> KNUCKLE["Щёлканье суставами"]
    LIFESTYLE --> NAILS["Грызение ногтей"]

    %% Профилактика
    SHIELD --> PREVENT["Профилактика<br/>вредных привычек"]

    %% Горизонтальные связи
    DOPAMINE -.- SOCIAL
    DOPAMINE -.- SHOP
    DOPAMINE -.- FASTFOOD
    PERSONALITY -.- DRUGS_MYTHS
    PERSONALITY -.- OVERDOSE
    DOOM -.- SOCIAL
    ENERGY -.->|связан с| SLEEP
    SEDENTARY -.->|связан с| FASTFOOD
    PREVENT -.->|противодействует| VP

    %% Стили
    classDef substance fill:#ffcdd2,stroke:#c62828
    classDef mechanism fill:#e1bee7,stroke:#6a1b9a
    classDef digital fill:#bbdefb,stroke:#1565c0
    classDef lifestyle fill:#fff9c4,stroke:#f9a825
    classDef shield fill:#c8e6c9,stroke:#2e7d32
    classDef root fill:#e0e0e0,stroke:#424242

    class SUBSTANCE,SMOKING,ALCOHOL,ENERGY,DRUGS_MYTHS,OVERDOSE substance
    class MECHANISM,DOPAMINE,PERSONALITY mechanism
    class DIGITAL,SOCIAL,DOOM,GAMES,LUDO,SHOP digital
    class LIFESTYLE,FASTFOOD,SEDENTARY,SLEEP,KNUCKLE,NAILS lifestyle
    class SHIELD,PREVENT shield
    class VP root
```

## 🔗 Граф перекрёстных ссылок между статьями

> 64 ссылки расставлены автоматически скриптом `crosslink.py` с учётом падежей (pymorphy3)

```mermaid
graph LR
    %% Узлы
    SMOKE["Курение"]
    ALC["Алкоголь"]
    ENERGY["Энергетики"]
    DRUGS["Мифы о наркотиках"]
    OD["Передозировка"]
    DOPA["Дофамин"]
    ADDICT["Зависимость и личность"]
    SM["Соцсети"]
    DOOM["Думскроллинг"]
    GAMES["Комп. игры"]
    LUDO["Лудомания"]
    SHOP["Шопоголизм"]
    FF["Фастфуд"]
    SEDEN["Малоподвижность"]
    SLEEP["Недосыпание"]
    KNUCK["Суставы"]
    NAILS["Онихофагия"]
    PREV["Профилактика"]

    %% Ссылки (64)
    SMOKE --> ADDICT
    ALC --> ADDICT
    ENERGY --> DOPA & ADDICT & SLEEP & ALC & OD
    DRUGS --> FF & ADDICT & DOPA & ALC
    OD --> DRUGS & ENERGY & ALC & ADDICT
    DOPA --> FF & SM & ADDICT
    ADDICT --> GAMES & DRUGS & OD & SLEEP
    SM --> ADDICT & DOOM
    DOOM --> DOPA & SLEEP
    GAMES --> DOOM & DOPA & SEDEN & SLEEP
    LUDO --> ADDICT & PREV & GAMES & SLEEP & ALC & DRUGS
    SHOP --> DOPA & ADDICT & SM & DOOM & OD
    FF --> DRUGS & DOPA & SM & NAILS & ENERGY
    SEDEN --> SMOKE & ALC & DOPA & ENERGY
    SLEEP --> ALC & DOPA & DOOM & ENERGY
    KNUCK --> DOOM & SEDEN
    NAILS --> DOOM
    PREV --> DOPA & DRUGS & FF & SMOKE & ADDICT & DOOM & ALC

    %% Стили
    classDef substance fill:#ffcdd2,stroke:#c62828
    classDef mechanism fill:#e1bee7,stroke:#6a1b9a
    classDef digital fill:#bbdefb,stroke:#1565c0
    classDef lifestyle fill:#fff9c4,stroke:#f9a825
    classDef shield fill:#c8e6c9,stroke:#2e7d32

    class SMOKE,ALC,ENERGY,DRUGS,OD substance
    class DOPA,ADDICT mechanism
    class SM,DOOM,GAMES,LUDO,SHOP digital
    class FF,SEDEN,SLEEP,KNUCK,NAILS lifestyle
    class PREV shield
```

## 📋 Таблица понятий

| # | Понятие | WikiData | Категория | [Автор](../../4.2_thinking_and_working_information/how_to_search_information/articles/copypaste.md) |
|---|---------|----------|-----------|-------|
| 1 | [Курение](../../1.2_natural_sciences/neurobiology_for_teens/articles/13_nicotine.md) | [Q662860](https://www.wikidata.org/wiki/Q662860) | Вещества | Дмитрий Марьин |
| 2 | [Алкоголь](articles/alcohol.md) и [подростки](../../3.1. healthy lifestyle/Sleep, nutrition, and adolescent energy/articles/biology_of_night_owls_teens.md) | [Q154](https://www.wikidata.org/wiki/Q154) | Вещества | Дмитрий Марьин |
| 3 | [Энергетики](../../3.1. healthy lifestyle/Sleep, nutrition, and adolescent energy/articles/the_energy_trap.md) | [Q30574535](https://www.wikidata.org/wiki/Q30574535) | Вещества | Воробьев Глеб |
| 4 | [Мифы](../../1.2_natural_sciences/physics_in_everyday_life/Q140028.md) о «лёгких» наркотиках | [Q12140](https://www.wikidata.org/wiki/Q12140) | Вещества | Аксельрод Анастасия |
| 5 | [Передозировка](articles/overdose.md) | [Q1347065](https://www.wikidata.org/wiki/Q1347065) | Вещества | Аксельрод Анастасия |
| 6 | [Дофаминовая петля](articles/Dopamine.md) | [Q170304](https://www.wikidata.org/wiki/Q170304) | Механизмы | Гуляев Антон |
| 7 | Как [зависимость](../../3.1. healthy lifestyle/Sleep, nutrition, and adolescent energy/articles/the_energy_trap.md) меняет [личность](../../1.2_natural_sciences/neurobiology_for_teens/articles/06_phineas_gage.md) | [Q2739434](https://www.wikidata.org/wiki/Q2739434) | Механизмы | Аксельрод Анастасия |
| 8 | [Соцсети](../../2.1_society/how_and_where_find_friends/articles/tcifrovaya_druzhba.md) и [FoMO](articles/Social_media.md) | [Q202833](https://www.wikidata.org/wiki/Q202833) | Цифровые | Гуляев Антон |
| 9 | [Думскроллинг](articles/Doomscrolling.md) | [Q97210710](https://www.wikidata.org/wiki/Q97210710) | Цифровые | Гуляев Антон |
| 10 | [Компьютерные игры](articles/computer_games.md) | [Q56828378](https://www.wikidata.org/wiki/Q56828378) | Цифровые | Дмитрий Марьин |
| 11 | [Лудомания](articles/ludomania.md) | [Q860861](https://www.wikidata.org/wiki/Q860861) | Цифровые | Мустафаев Алим |
| 12 | [Шопоголизм](articles/shopogolizm.md) | [Q1140705](https://www.wikidata.org/wiki/Q1140705) | Цифровые | Воробьев Глеб |
| 13 | [Фастфуд](articles/fastfud_i_pischevoy_musor.md) и [пищевой мусор](articles/fastfud_i_pischevoy_musor.md) | [Q223557](https://www.wikidata.org/wiki/Q223557) | [Образ](../../7.2 Media, leisure and hobbies/Computer games/articles/game_culture/cosplay.md) жизни | Воробьев Глеб |
| 14 | Малоподвижный образ жизни | [Q1349194](https://www.wikidata.org/wiki/Q1349194) | Образ жизни | Пономарев Артем |
| 15 | [Недосыпание](articles/nedosypanie.md) | [Q15070482](https://www.wikidata.org/wiki/Q15070482) | Образ жизни | Пономарев Артем |
| 16 | [Щёлканье](articles/knuckle.md) суставами | [Q241790](https://www.wikidata.org/wiki/Q241790) | Образ жизни | Мустафаев Алим |
| 17 | [Онихофагия](articles/nailbiting.md) | [Q225378](https://www.wikidata.org/wiki/Q225378) | Образ жизни | Мустафаев Алим |
| 18 | [Профилактика](../../3.1_healthy_lifestyle/pervaya_pomoshch/ushibi_porezy_ozhogi/18_mify_i_7_pravil.md) вредных привычек | — | Профилактика | Пономарев Артем |

## Участники группы (Команда 777)

| # | ФИО | Статьи | [LLM](../../7.1_art/modern_technological_art/README.md) |
|---|-----|--------|-----|
| 1 | Гуляев Антон | Дофаминовая петля, Соцсети и FoMO, Думскроллинг | Gemini 3, Nano Banana 2 |
| 2 | Дмитрий Марьин | Курение, Алкоголь, Компьютерные игры | OpenRouter |
| 3 | Воробьев Глеб | Энергетики, Фастфуд, Шопоголизм | Claude (Anthropic) |
| 4 | Аксельрод Анастасия | Мифы о наркотиках, Передозировка, Зависимость и личность | DeepSeek |
| 5 | Пономарев Артем | [Малоподвижность](articles/malopodvizhnost.md), Недосыпание, Профилактика | Claude (Anthropic) |
| 6 | Мустафаев Алим | Щёлканье суставами, Лудомания, Онихофагия | DeepSeek |
