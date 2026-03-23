```mermaid
graph TD
    %% Главный узел
    CAREER["💼 Выбор профессии"]

    %% Категории
    CAREER --> SPEC["🛠️ Специальности"]
    CAREER --> EDU["🎓 Образование и Мечта"]
    CAREER --> JOB["🚀 Работа и Офис"]

    %% Специальности (по concepts.json)
    SPEC --> PROG["Программист<br/>(Q5482740)"]
    SPEC --> DOC["Врач<br/>(Q39631)"]
    SPEC --> DES["Дизайнер<br/>(Q190539)"]
    SPEC --> PROF["Понятие профессии<br/>(Q28640)"]

    %% Образование и старт (по concepts.json)
    EDU --> UNIV["Университет<br/>(Q3918)"]
    EDU --> SKILL["Навыки<br/>(Q1058914)"]
    EDU --> HOBBY["Хобби<br/>(Q11707)"]
    EDU --> DREAM["Мечта<br/>(Q1158639)"]

    %% Процесс и место (по concepts.json)
    JOB --> RES["Резюме<br/>(Q186649)"]
    JOB --> INT["Собеседование<br/>(Q178685)"]
    JOB --> STAGE["Стажировка<br/>(Q1313364)"]
    JOB --> SAL["Зарплата<br/>(Q178631)"]
    JOB --> TEAM["Команда<br/>(Q171138)"]
    JOB --> OFF["Офис<br/>(Q149460)"]
    JOB --> PATH["Карьерный путь<br/>(Q652431)"]

    %% Горизонтальные связи (Перекрестные ссылки)
    HOBBY -.->|превращается в| PROF
    SKILL -.->|нужны для| PROG
    UNIV -.->|готовит к| DOC
    RES -.->|ведет на| INT
    INT -.->|определяет| SAL
    STAGE -.->|часть| PATH
    OFF -.->|место для| TEAM

    %% Стилизация
    classDef spec fill:#e3f2fd,stroke:#1976d2
    classDef edu fill:#e8f5e9,stroke:#388e3c
    classDef job fill:#fff9c4,stroke:#f9a825
    classDef main fill:#fce4ec,stroke:#c62828

    class PROG,DOC,DES,PROF spec
    class UNIV,SKILL,HOBBY,DREAM edu
    class RES,INT,STAGE,SAL,TEAM,OFF,PATH job
    class CAREER main
```    