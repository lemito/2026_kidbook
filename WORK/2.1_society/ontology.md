# 🕸 3. Визуализация Онтологии

```mermaid
graph TD
    %% Основные сущности
    Person[Человек] -->|имеет статус| Citizen[Гражданин]
    Person -->|живет в| Family[Семья]
    Person -->|учится в| School[Школа]

    %% Права и Законы
    Constitution[Конституция] -->|гарантирует| Right[Право]
    Right -->|включает| Education[Право на образование]
    Right -->|включает| Name[Право на имя]
    Right -->|включает| Privacy[Неприкосновенность частной жизни]
    Right -->|включает| Safety[Безопасность]

    %% Обязанности
    Law[Закон] -->|требует| Duty[Обязанность]
    Duty -->|включает| Study[Обязанность учиться]
    Duty -->|включает| Nature[Обязанность беречь природу]

    %% Связи гражданина
    Citizen -->|обладает| Right
    Citizen -->|исполняет| Duty

    %% Защитники
    Police[Полиция] -->|защищает| Safety
    Police -->|следит за| Law

    %% Стили
    style Person fill:#f9f,stroke:#333
    style Right fill:#bbf,stroke:#333
    style Duty fill:#fbb,stroke:#333
    style Citizen fill:#cfc,stroke:#333
    style Constitution fill:#ffd700,stroke:#333
    style Law fill:#ffa07a,stroke:#333