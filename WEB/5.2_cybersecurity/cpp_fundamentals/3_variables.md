# Переменные и типы данных

![Картинка переменные и типы данных](covers/cover_3_variables.png)

## Что это и зачем

Любая [программа](../../5.1_technology_and_digital_literacy/operating system/articles/process.md) работает с данными: числами, текстом, флагами «да/нет». Чтобы хранить эти [данные](../../2.1_society/cause_and_effect_relationships/articles/ai_causality.md) во [время](../../1.2_natural_sciences/physics_in_everyday_life/Q20702.md) [работы](../../8.2_future/choosing_a_career_path/articles/interview.md) программы, используются **переменные** — именованные ячейки в оперативной [памяти](../../4.1_rules_of_study/how_to_memorize/articles/pamyat.md). Когда вы объявляете переменную, [компилятор](1_introduction.md) резервирует под неё определённое количество [байт](../../7.2 Media, leisure and hobbies/Computer games/articles/technologies_inside/smart_processor.md) и запоминает её имя, чтобы вы могли обращаться к этой ячейке по имени, а не по адресу.

В отличие от Python или JavaScript, [C](../../2.1_society/how_and_where_find_friends/articles/sora_drug.md)++ — **статически типизированный** [язык](1_introduction.md). Это означает, что [тип](13_struct.md) каждой переменной задаётся один раз при объявлении и не может измениться в ходе выполнения программы. Компилятор знает тип заранее и за счёт этого генерирует более эффективный [код](1_introduction.md). Это же помогает находить [ошибки](../../3.1_healthy_lifestyle/pervaya_pomoshch/ushibi_porezy_ozhogi/07_ushib_chego_nelzya.md) ещё до запуска программы: если вы попытаетесь сложить число со строкой, компилятор скажет об этом немедленно.

[Понимание](../../2.1_society/cause_and_effect_relationships/articles/empathy_causality.md) типов данных — это не просто формальность. [Выбор](../../2.1_society/cause_and_effect_relationships/articles/personal_choice.md) неправильного типа может привести к потере точности вычислений, переполнению переменной или лишнему расходу памяти.

---

## [Синтаксис](2_syntax.md) / Как работает

### Объявление и инициализация переменной

```cpp
тип имя;              // объявление без начального значения
тип имя = значение;   // объявление с инициализацией
```

Конкретные примеры:

```cpp
int age = 25;
double price = 99.99;
char grade = 'A';
bool isActive = true;
```

### Основные типы данных

| Тип | Размер | [Диапазон](../../5.1_technology_and_digital_literacy/how_internet_works/articles/wifi/radio.md) / Описание | Пример |
|---|---|---|---|
| `int` | 4 байта | от −2 147 483 648 до 2 147 483 647 | `int x = 42;` |
| `long long` | 8 байт | очень большие целые числа | `long long big = 9000000000LL;` |
| `double` | 8 байт | дробные числа (~15 знаков точности) | `double pi = 3.14159;` |
| `float` | 4 байта | дробные числа (~7 знаков точности) | `float temp = 36.6f;` |
| `char` | 1 байт | один символ (в одинарных кавычках) | `char c = 'Z';` |
| `bool` | 1 байт | `true` или `false` | `bool flag = false;` |

**Когда что использовать:**
- `int` — счётчики, индексы, целые [результаты](../../1.2_natural_sciences/why_science_help_understand_world/research_work.md).
- `double` — [деньги](../../2.1_society/cause_and_effect_relationships/articles/economic_chains.md), [физические величины](../../1.2_natural_sciences/physics_in_everyday_life/Q12453.md), всё, где нужна [точность](../../1.2_natural_sciences/physics_in_everyday_life/Q36253.md) дробной части.
- `float` — графика и игры, где важна [скорость](../../1.2_natural_sciences/physics_in_everyday_life/Q11402.md), а не максимальная точность.
- `char` — отдельные символы, коды клавиш.
- `bool` — логические флаги, результаты проверок.

### Ключевое слово `auto`

Начиная со стандарта C++11, компилятор может определить тип переменной сам, если вы используете `auto`:

```cpp
auto x = 10;       // компилятор выведет int
auto y = 3.14;     // компилятор выведет double
auto z = 'A';      // компилятор выведет char
```

`auto` удобен, когда тип очевиден из правой части. Однако злоупотреблять им не стоит: явное указание типа делает код понятнее для читателя.

### [Правила](../../2.1_society/cause_and_effect_relationships/articles/why_rules_work.md) именования переменных

Имя переменной в C++ должно:
- Начинаться с буквы или символа подчёркивания `_`.
- Содержать только буквы, цифры и `_`.
- Не совпадать с ключевыми словами языка (`int`, `return`, `if` и т.д.).

```cpp
int age = 25;        // хорошо
int _count = 0;      // допустимо
int myValue123 = 5;  // хорошо

int 2fast = 10;      // ошибка: начинается с цифры
int my-var = 5;      // ошибка: дефис недопустим
int return = 1;      // ошибка: return — ключевое слово
```

C++ чувствителен к регистру: `Age`, `age` и `AGE` — три разные переменные.

Принятый [стиль](../../7.1_art/modern_technological_art/articles/5.5_yandex_neural.md) именования: **camelCase** (`firstName`, `totalPrice`) или **snake_case** (`first_name`, `total_price`). Главное — придерживаться одного стиля в рамках проекта.

---

## Примеры использования

### Вычисление площади прямоугольника

```cpp
#include <iostream>

int main() {
    double width = 5.5;
    double height = 3.0;
    double area = width * height;

    std::cout << "Площадь: " << area << " кв. м" << std::endl;

    return 0;
}
```

[Вывод](../../1.2_natural_sciences/why_science_help_understand_world/scientific_method.md):
```
Площадь: 16.5 кв. м
```

### [Работа](../../1.2_natural_sciences/physics_in_everyday_life/Q11382.md) с символами и флагами

```cpp
#include <iostream>

int main() {
    char initial = 'R';
    int score = 95;
    bool passed = true;

    std::cout << "Инициал: " << initial << std::endl;
    std::cout << "Оценка: " << score << std::endl;
    std::cout << "Сдал экзамен: " << passed << std::endl;

    return 0;
}
```

Вывод:
```
Инициал: R
Оценка: 95
Сдал экзамен: 1
```

---

## [Типичные ошибки](../../6.1_Independent_living_and_daily_living_skills/Simple_and_safe_cooking/articles/safe_use_of_kitchen_appliances.md)

**Использование неинициализированной переменной.** Если объявить переменную без начального значения и сразу использовать её, [результат](../../1.2_natural_sciences/why_science_help_understand_world/experimental_science.md) непредсказуем — в ней будет «мусор» из памяти:

```cpp
// Опасно
int x;
std::cout << x;  // выведет случайное число, не 0
```

```cpp
// Правильно — всегда инициализируйте переменные
int x = 0;
std::cout << x;  // выведет 0
```

**Переполнение типа `int`.** Если результат [вычисления](../../7.2 Media, leisure and hobbies/Computer games/articles/technologies_inside/smart_processor.md) выходит за границы диапазона типа, происходит переполнение — число «перескакивает» на противоположный конец диапазона:

```cpp
int big = 2147483647;  // максимальное значение int
big = big + 1;
std::cout << big;      // выведет -2147483648, а не 2147483648!
```

Если нужны большие числа, используйте `long long`.

**[Потеря](../../1.2_natural_sciences/neurobiology_for_teens/articles/20_sadness.md) точности при делении целых чисел.** При делении двух `int` результат тоже `int` — дробная часть отбрасывается:

```cpp
int a = 7;
int b = 2;
double result = a / b;
std::cout << result;  // выведет 3, а не 3.5!
```

Чтобы получить дробный результат, хотя бы один операнд должен быть `double`:

```cpp
double result = 7.0 / 2;  // или (double)a / b
std::cout << result;      // выведет 3.5
```

---

## Итог

- Переменная — именованная ячейка памяти; тип задаётся один раз при объявлении.
- Основные типы: `int` (целые), `double` (дробные), `char` (символ), `bool` (истина/[ложь](../../2.1_society/cause_and_effect_relationships/articles/false_connections.md)).
- Всегда инициализируйте переменные при объявлении — неинициализированная переменная содержит «мусор».
- Деление двух `int` даёт `int`; чтобы получить дробный результат, используйте `double`.
- `auto` позволяет не писать тип явно, но злоупотреблять им не стоит.

---
[Вернуться к списку статей](./article_index_information_media_literacy.md)

---
[Автор](../../4.2_thinking_and_working_information/how_to_search_information/articles/copypaste.md): Руслан Юнусов  
*[Ресурсы](../../2.1_society/cause_and_effect_relationships/articles/ecological_footprint.md): [LLM](../../7.1_art/modern_technological_art/README.md) - Clause Sonnet 4.6*
