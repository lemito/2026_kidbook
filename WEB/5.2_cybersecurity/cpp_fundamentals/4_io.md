# Ввод и [вывод](../../1.2_natural_sciences/why_science_help_understand_world/scientific_method.md) данных

![Картинка ввод и вывод программы](covers/cover_4_io.png)

## Что это и зачем

[Программа](../../5.1_technology_and_digital_literacy/operating system/articles/process.md), которая не может общаться с пользователем, практически бесполезна. Именно для этого в [C](../../2.1_society/how_and_where_find_friends/articles/sora_drug.md)++ существует библиотека `iostream` — она обеспечивает два потока данных: [поток](../../5.1_technology_and_digital_literacy/operating system/articles/thread.md) вывода на [экран](../../3.1. healthy lifestyle/Sleep, nutrition, and adolescent energy/articles/gadgets_blue_light_sleep.md) и поток ввода с клавиатуры. Слово «поток» здесь не случайно: [данные](../../2.1_society/cause_and_effect_relationships/articles/ai_causality.md) текут в одном направлении, как [вода](../../3.1. healthy lifestyle/Sleep, nutrition, and adolescent energy/articles/drinking_regime.md) по трубе. Вы отправляете данные в поток вывода — они появляются на экране. Вы читаете из потока ввода — программа получает то, что напечатал пользователь.

[Понимание](../../2.1_society/cause_and_effect_relationships/articles/empathy_causality.md) `std::cout` и `std::cin` — это [первый шаг](../../1.2_natural_sciences/physics_in_everyday_life/Q26540.md) к созданию интерактивных программ. Без этого любая программа остаётся «чёрным ящиком», [результат](../../1.2_natural_sciences/why_science_help_understand_world/experimental_science.md) [работы](../../8.2_future/choosing_a_career_path/articles/interview.md) которого [нельзя](../../3.1_healthy_lifestyle/pervaya_pomoshch/ushibi_porezy_ozhogi/07_ushib_chego_nelzya.md) ни увидеть, ни повлиять на него.

---

## [Синтаксис](2_syntax.md) / Как работает

### Вывод: `std::cout`

`std::cout` (от *character output*) — [объект](../../1.2_natural_sciences/physics_in_everyday_life/Q634.md) для вывода данных в [консоль](../../../8.1_entertainment/articles/history-of-games.md). [Оператор](../../3.2 healthy lifestyle/how to act in a dangerous situation/articles/emergency-112.md) `<<` передаёт данные в поток.

```cpp
#include <iostream>

int main() {
    std::cout << "Привет, мир!" << std::endl;
    return 0;
}
```

- `<<` — оператор вставки, его можно «цеплять» несколько раз в одну строку.
- `std::endl` — вставляет символ новой строки и **сбрасывает буфер** вывода (гарантирует, что [текст](../../4.1_rules_of_study/how_to_learn_effectively/articles/reading_skills.md) появится на экране немедленно). Альтернатива — символ `'\n'`, который быстрее, потому что не сбрасывает буфер.

```cpp
// Вывод нескольких значений в одну строку
int age = 20;
std::cout << "Возраст: " << age << " лет" << std::endl;

// '\n' вместо std::endl — предпочтительно для производительности
std::cout << "Строка 1\n";
std::cout << "Строка 2\n";
```

### Ввод: `std::cin`

`std::cin` (от *character input*) — объект для чтения данных с клавиатуры. Оператор `>>` извлекает данные из потока и записывает их в переменную.

```cpp
#include <iostream>

int main() {
    int number;
    std::cout << "Введите число: ";
    std::cin >> number;
    std::cout << "Вы ввели: " << number << std::endl;
    return 0;
}
```

`std::cin >>` читает данные до первого пробела или переноса строки. Это важно: если пользователь введёт `42 100`, то первый `>>` прочитает `42`, второй — `100`.

### [Чтение](../../4.1_rules_of_study/how_to_learn_effectively/articles/reading_skills.md) нескольких значений

Операторы ввода тоже можно цеплять:

```cpp
int a, b;
std::cout << "Введите два числа: ";
std::cin >> a >> b;
std::cout << "Сумма: " << a + b << std::endl;
```

---

## Примеры использования

### Простой калькулятор суммы

```cpp
#include <iostream>

int main() {
    double x, y;

    std::cout << "Введите первое число: ";
    std::cin >> x;

    std::cout << "Введите второе число: ";
    std::cin >> y;

    std::cout << "Результат: " << x + y << std::endl;

    return 0;
}
```

Пример работы программы:
```
Введите первое число: 3.5
Введите второе число: 1.5
Результат: 5
```

### Форматированный вывод

Чтобы управлять точностью вывода дробных чисел, подключают заголовочный [файл](../../5.1_technology_and_digital_literacy/operating system/articles/file_system.md) `<iomanip>`:

```cpp
#include <iostream>
#include <iomanip>

int main() {
    double price = 199.9;
    std::cout << "Цена: " << std::fixed << std::setprecision(2) << price << " руб." << std::endl;
    return 0;
}
```

Вывод:
```
Цена: 199.90 руб.
```

- `std::fixed` — выводить число в фиксированном формате (без экспоненты).
- `std::setprecision(2)` — два знака после запятой.

---

## [Типичные ошибки](../../6.1_Independent_living_and_daily_living_skills/Simple_and_safe_cooking/articles/safe_use_of_kitchen_appliances.md)

**Использование `std::cin` для строк с пробелами.** Оператор `>>` читает только до первого пробела. Если нужно прочитать целую строку, используйте `std::getline`:

```cpp
#include <iostream>
#include <string>

int main() {
    std::string name;

    // Неправильно для имён с пробелом — прочитает только первое слово
    // std::cin >> name;

    // Правильно
    std::cout << "Введите полное имя: ";
    std::getline(std::cin, name);
    std::cout << "Привет, " << name << "!" << std::endl;

    return 0;
}
```

**Смешивание `>>` и `getline`.** После чтения числа через `>>` в буфере остаётся символ новой строки `'\n'`. Следующий `getline` прочитает именно его и вернёт пустую строку. [Решение](../../2.1_society/cause_and_effect_relationships/articles/personal_choice.md) — очистить буфер перед `getline`:

```cpp
int age;
std::cin >> age;
std::cin.ignore();          // убрать '\n' из буфера
std::getline(std::cin, name);
```

---

## Итог

- `std::cout <<` выводит данные в консоль; `<<` можно цеплять в одну цепочку.
- `std::cin >>` читает данные с клавиатуры до первого пробела или переноса строки.
- `std::endl` делает новую строку и сбрасывает буфер; `'\n'` — только новую строку (быстрее).
- Для чтения строк с пробелами используйте `std::getline`, а не `>>`.
- После `std::cin >>` перед `std::getline` вызывайте `std::cin.ignore()`.

---
[Вернуться к списку статей](./article_index_information_media_literacy.md)

---
[Автор](../../4.2_thinking_and_working_information/how_to_search_information/articles/copypaste.md): Велиев Рауф  
*[Ресурсы](../../2.1_society/cause_and_effect_relationships/articles/ecological_footprint.md): [LLM](../../7.1_art/modern_technological_art/README.md) - Clause Sonnet 4.6*
