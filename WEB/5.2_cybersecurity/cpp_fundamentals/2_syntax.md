# [Структура](../../4.1_rules_of_study/how_to_learn_effectively/articles/note_taking.md) программы и базовый синтаксис

![Картинка структура программы](covers/cover_2_syntax.png)

## Что это и зачем

Когда вы смотрите на программу на [C](../../2.1_society/how_and_where_find_friends/articles/sora_drug.md)++ в первый раз, она может казаться набором малопонятных символов. Знак `#`, угловые скобки, двойное двоеточие `::`, точки с запятой в конце каждой строки — всё это не случайные украшения, а строгие [правила](../../2.1_society/cause_and_effect_relationships/articles/why_rules_work.md) языка. [Понимание](../../2.1_society/cause_and_effect_relationships/articles/empathy_causality.md) структуры программы — это фундамент, без которого невозможно двигаться дальше.

Каждая [программа](../../5.1_technology_and_digital_literacy/operating system/articles/process.md) на C++, какой бы сложной она ни была, строится из одних и тех же блоков: директив препроцессора, заголовочных файлов, функций и операторов. Даже программа из миллиона строк следует тем же правилам, что и «Hello, World!». Разобравшись со структурой один раз, вы будете читать [чужой](../../3.2 healthy lifestyle/how to act in a dangerous situation/articles/stranger-safety.md) [код](1_introduction.md) и писать свой осознанно, а не методом копирования примеров.

---

## Синтаксис / Как работает

Рассмотрим расширенную программу, которая демонстрирует все ключевые структурные элементы:

```cpp
#include <iostream>
#include <string>

int main() {
    std::string name = "C++";
    int year = 1983;

    std::cout << "Язык " << name << " появился в " << year << " году." << std::endl;

    return 0;
}
```

### Директивы препроцессора (`#include`)

Строки, начинающиеся с символа `#`, обрабатываются **препроцессором** — специальной программой, которая запускается до компилятора. Директива `#include` буквально вставляет содержимое указанного файла в текущий код.

```cpp
#include <iostream>   // заголовочный файл из стандартной библиотеки
#include <string>     // ещё один заголовочный файл
#include "myfile.h"   // заголовочный файл из текущего проекта
```

Разница между угловыми скобками `< >` и кавычками `" "` принципиальная:
- `< >` — [компилятор](1_introduction.md) ищет [файл](../../5.1_technology_and_digital_literacy/operating system/articles/file_system.md) в системных директориях стандартной библиотеки.
- `" "` — компилятор сначала ищет файл рядом с текущим исходным файлом, потом в системных директориях.

Директивы препроцессора **не заканчиваются точкой с запятой** — это одно из немногих исключений в синтаксисе C++.

### Функция `main`

Каждая исполняемая программа на C++ обязана содержать функцию `main`. Именно с неё [операционная система](../../5.1_technology_and_digital_literacy/operating system/articles/kernel.md) начинает выполнение программы.

```cpp
int main() {
    // тело функции
    return 0;
}
```

- `int` перед `main` — [тип](13_struct.md) возвращаемого значения. Функция `main` возвращает целое число операционной системе.
- `return 0;` — [сигнал](../../5.1_technology_and_digital_literacy/how_internet_works/articles/wifi/router.md) ОС о [том](../../7.1_art/musical_instruments/articles/drums.md), что программа завершилась успешно. Любое ненулевое [значение](../../7.2 Media, leisure and hobbies /useful_and_interesting_leisure/articles/leisure_and_why_need.md) означает ошибку.
- Фигурные скобки `{ }` обозначают **блок кода** — начало и конец тела функции.

### [Пространство](../../1.2_natural_sciences/physics_in_everyday_life/Q36253.md) имён `std::`

Стандартная библиотека C++ помещает все свои компоненты в пространство имён `std` (от *standard*). Именно поэтому перед `cout`, `cin`, `string` и другими стандартными объектами стоит `std::`.

Можно сократить запись с помощью директивы `using namespace std;`, тогда `std::` писать не нужно:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Привет!" << endl;
    return 0;
}
```

Однако в больших проектах `using namespace std;` считается плохой практикой — имена из разных библиотек могут совпадать и конфликтовать. Для учебных программ это допустимо, но лучше привыкать к явному `std::`.

### Точки с запятой и фигурные скобки

В C++ **каждый [оператор](../../3.2 healthy lifestyle/how to act in a dangerous situation/articles/emergency-112.md) заканчивается точкой с запятой** `;`. Оператор — это одна инструкция: объявление переменной, вызов функции, возврат значения. Компилятор не обращает [внимания](../../4.1_rules_of_study/how_to_memorize/articles/vnimanie.md) на переносы строк и отступы — он ориентируется только на `;` как на разделитель.

**Фигурные скобки** `{ }` группируют несколько операторов в один блок. [Блоки](../../1.2_natural_sciences/physics_in_everyday_life/Q169019.md) используются для тела функций, условий, циклов.

---

## Примеры использования

### Программа с несколькими переменными и выводом

```cpp
#include <iostream>
#include <string>

int main() {
    std::string language = "C++";
    int version = 17;
    bool isPopular = true;

    std::cout << "Язык: " << language << std::endl;
    std::cout << "Стандарт: C++" << version << std::endl;
    std::cout << "Популярен: " << isPopular << std::endl;

    return 0;
}
```

[Вывод](../../1.2_natural_sciences/why_science_help_understand_world/scientific_method.md) программы:
```
Язык: C++
Стандарт: C++17
Популярен: 1
```

Обратите [внимание](../../1.2_natural_sciences/neurobiology_for_teens/articles/16_love_chemistry.md): `bool` при выводе через `std::cout` отображается как `1` (true) или `0` (false), а не как слова.

### Несколько функций в одном файле

Программа может содержать несколько функций. Функция `main` вызывает другие:

```cpp
#include <iostream>

void greet() {
    std::cout << "Добро пожаловать в C++!" << std::endl;
}

int main() {
    greet();
    return 0;
}
```

- `void` означает, что функция ничего не возвращает.
- Функция `greet` объявлена **до** `main`, поэтому компилятор знает о ней в момент вызова. Если расположить `greet` после `main`, потребуется предварительное объявление ([прототип](../../1.2_natural_sciences/physics_in_everyday_life/Q11023.md)) — подробнее в статье о функциях.

---

## [Типичные ошибки](../../6.1_Independent_living_and_daily_living_skills/Simple_and_safe_cooking/articles/safe_use_of_kitchen_appliances.md)

**Точка с запятой после фигурной скобки функции.** [Тело](../../1.2_natural_sciences/why_science_help_understand_world/organism.md) функции заканчивается на `}` без `;`. Точка с запятой после закрывающей скобки — признак структуры или класса, но не функции:

```cpp
// Неправильно
int main() {
    return 0;
};   // лишняя точка с запятой — компилятор может принять, но это ошибка стиля

// Правильно
int main() {
    return 0;
}
```

**Пропущен `#include` для используемого типа.** Если вы используете `std::string`, но не подключили `<string>`, компилятор выдаст ошибку:

```cpp
// Неправильно — нет #include <string>
int main() {
    std::string s = "привет";  // ошибка: 'string' is not a member of 'std'
    return 0;
}
```

```cpp
// Правильно
#include <string>

int main() {
    std::string s = "привет";
    return 0;
}
```

**Несбалансированные фигурные скобки.** Каждой открывающей `{` должна соответствовать закрывающая `}`. Пропущенная скобка приводит к каскаду ошибок компиляции, которые на первый взгляд непонятны:

```cpp
// Неправильно — нет закрывающей скобки функции main
int main() {
    std::cout << "Hello" << std::endl;
    return 0;
// компилятор: ошибка в конце файла
```

Хороший редактор (VS Code, CLion) подсвечивает скобки попарно — пользуйтесь этим.

---

## Итог

- Директивы `#include` подключают заголовочные файлы и обрабатываются до компиляции; они не заканчиваются `;`.
- Угловые скобки `< >` используются для системных файлов, [кавычки](../../../4.2/how_to_search_information/articles/search_operations.md) `" "` — для файлов проекта.
- Функция `main` — обязательная точка входа; возвращает `0` при успешном завершении.
- Все стандартные объекты ([cout](4_io.md), [cin](4_io.md), [string](12_strings.md)) находятся в пространстве имён `std::`.
- Каждый оператор заканчивается `;`, блоки кода обозначаются фигурными скобками `{ }`.

---
[Вернуться к списку статей](./article_index_information_media_literacy.md)

---
[Автор](../../4.2_thinking_and_working_information/how_to_search_information/articles/copypaste.md): Руслан Юнусов  
*[Ресурсы](../../2.1_society/cause_and_effect_relationships/articles/ecological_footprint.md): [LLM](../../7.1_art/modern_technological_art/README.md) - Clause Sonnet 4.6*
