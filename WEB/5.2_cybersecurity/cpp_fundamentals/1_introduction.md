# Введение в [C](../../2.1_society/how_and_where_find_friends/articles/sora_drug.md)++

![Эмблема С++](covers/cover_1_introduction.png)

## Что это и зачем

C++ — один из старейших и при этом до сих пор востребованных языков программирования. Он был создан датским учёным Бьёрном Страуструпом в начале 1980-х годов в компании Bell Labs. Страуструп работал с языком C и хотел добавить в него поддержку объектно-ориентированного программирования, сохранив при этом [скорость](../../1.2_natural_sciences/physics_in_everyday_life/Q11402.md) и низкоуровневый контроль над [памятью](../../4.1_rules_of_study/how_to_memorize/articles/pamyat.md). Первоначально язык назывался «C with Classes» («C с классами»), а в 1983 году получил имя C++. Знак `++` — это [оператор](../../3.2 healthy lifestyle/how to act in a dangerous situation/articles/emergency-112.md) инкремента из самого C, намёк на то, что новый язык является «следующим шагом» после C.

Сегодня C++ применяется в областях, где критична производительность и точный контроль над ресурсами:

- **Системное программирование** — операционные системы, [драйверы](../../5.1_technology_and_digital_literacy/operating system/articles/HAL.md) устройств.
- **[Игровая индустрия](../../../8.1_entertainment/articles/history-of-games.md)** — движки Unreal Engine, Unity (частично), большинство AAA-игр.
- **Встроенные системы** — программирование микроконтроллеров, автомобильная [электроника](../../1.2_natural_sciences/physics_in_everyday_life/Q11023.md).
- **Высоконагруженные [сервисы](../../4.1_rules_of_study/how_to_learn_effectively/articles/digital_tools.md)** — торговые системы, [базы данных](../../7.1_art/modern_technological_art/articles/2.2_heath_bunting.md) (MySQL, PostgreSQL написаны на C/C++).
- **Компиляторы и интерпретаторы** — сам компилятор GCC написан на C++.

Почему C++ стоит изучать, если есть более простые языки? Потому что он учит понимать, как [программа](../../5.1_technology_and_digital_literacy/operating system/articles/process.md) работает на уровне [памяти](../../4.1_rules_of_study/how_to_memorize/articles/pamyat.md) и процессора. Освоив C++, вы гораздо лучше будете понимать любой другой язык — Python, Java, Rust.

---

## Настройка компилятора

Чтобы запускать программы на C++, нужен **компилятор** — программа, которая переводит ваш текстовый код в исполняемый [файл](../../5.1_technology_and_digital_literacy/operating system/articles/file_system.md). Самые популярные [варианты](../../6.1_Independent_living_and_daily_living_skills/reasonable_spending/articles/comparison.md):

| Компилятор | [Платформа](../../5.1_technology_and_digital_literacy/information and media literacy/как_работают_новостные_ленты.md) | Как установить |
|---|---|---|
| **GCC (g++)** | [Linux](../../5.1_technology_and_digital_literacy/operating system/articles/operating_system.md), [macOS](../../5.1_technology_and_digital_literacy/operating system/articles/operating_system.md) | `sudo apt install g++` / через Homebrew |
| **Clang** | macOS, Linux | `xcode-select --install` (macOS) |
| **MSVC** | [Windows](../../5.1_technology_and_digital_literacy/operating system/articles/operating_system.md) | Visual Studio Community (бесплатно) |
| **MinGW (g++)** | Windows | Через установщик MinGW или MSYS2 |

Проще всего для начала установить **Visual Studio Code** + расширение **C/C++** от Microsoft, либо воспользоваться **CLion** (бесплатно для студентов). Если не хочется ничего устанавливать — можно писать и запускать код прямо в браузере на [Compiler Explorer](https://godbolt.org/) или [OnlineGDB](https://www.onlinegdb.com/).

Чтобы проверить, что компилятор установлен, откройте терминал и выполните:

```bash
g++ --version
```

Если в [ответ](../../5.1_technology_and_digital_literacy/how_internet_works/articles/http_https/http_https.md) появилась строка с номером версии — всё готово.

---

## Первая программа: Hello World

Традиционно [знакомство](../../2.1_society/how_and_where_find_friends/articles/mozno_li_naiti_druzei_sluchaino.md) с любым языком начинается с программы, выводящей фразу «Hello, World!». Вот она на C++:

```cpp
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
```

Разберём каждую строку:

- `#include <iostream>` — подключает стандартную библиотеку ввода-вывода. Без неё `std::cout` будет неизвестен компилятору.
- `int main()` — точка входа в программу. Каждая программа на C++ начинает выполнение именно отсюда. `int` означает, что функция вернёт целое число.
- `std::cout << "Hello, World!" << std::endl;` — выводит [текст](../../4.1_rules_of_study/how_to_learn_effectively/articles/reading_skills.md) в [консоль](../../../8.1_entertainment/articles/history-of-games.md). `std::cout` — это [поток](../../5.1_technology_and_digital_literacy/operating system/articles/thread.md) вывода, `<<` — оператор вставки данных в поток, `std::endl` — переход на новую строку.
- `return 0;` — возвращает операционной системе код завершения. `0` означает «программа завершилась без ошибок».

### Как скомпилировать и запустить

Сохраните файл с именем `hello.cpp` и выполните в терминале:

```bash
g++ hello.cpp -o hello
./hello
```

Первая [команда](../../4.1_rules_of_study/how_to_learn_effectively/articles/peer_learning.md) компилирует файл `hello.cpp` и создаёт исполняемый файл `hello`. Вторая — запускает его. [Результат](../../1.2_natural_sciences/why_science_help_understand_world/experimental_science.md):

```
Hello, World!
```

---

## [Типичные ошибки](../../6.1_Independent_living_and_daily_living_skills/Simple_and_safe_cooking/articles/safe_use_of_kitchen_appliances.md)

**Забытая точка с запятой.** В C++ каждый оператор заканчивается `;`. Это самая частая [ошибка](../../5.1_technology_and_digital_literacy/how_internet_works/articles/http_https/http_https.md) новичков:

```cpp
// Неправильно — компилятор выдаст ошибку
std::cout << "Hello, World!" << std::endl
return 0;
```

```cpp
// Правильно
std::cout << "Hello, World!" << std::endl;
return 0;
```

**Неправильный регистр.** C++ чувствителен к регистру. `Main`, `MAIN` и `main` — это три разные вещи. Точка входа называется строго `main` в нижнем регистре.

**Отсутствие `#include <iostream>`.** Если убрать эту строку, компилятор скажет, что не знает, что такое `std::cout`. Каждый раз, когда используете функцию или [объект](../../1.2_natural_sciences/physics_in_everyday_life/Q634.md) из стандартной библиотеки, соответствующий заголовочный файл должен быть подключён.

---

## Итог

- C++ создан Бьёрном Страуструпом в 1983 году на основе языка C.
- Язык используется там, где важна производительность: игры, системы, встроенные [устройства](../../5.1_technology_and_digital_literacy/operating system/articles/HAL.md).
- Для [работы](../../8.2_future/choosing_a_career_path/articles/interview.md) нужен компилятор: на Linux/macOS — GCC или Clang, на Windows — MSVC или MinGW.
- Программа на C++ начинается с функции `main()`, [вывод](../../1.2_natural_sciences/why_science_help_understand_world/scientific_method.md) в консоль делается через `std::cout`.
- Каждый оператор завершается точкой с запятой `;`.

---
[Вернуться к списку статей](./article_index_information_media_literacy.md)

---
[Автор](../../4.2_thinking_and_working_information/how_to_search_information/articles/copypaste.md): Руслан Юнусов  
*[Ресурсы](../../2.1_society/cause_and_effect_relationships/articles/ecological_footprint.md): [LLM](../../7.1_art/modern_technological_art/README.md) - Clause Sonnet 4.6*
