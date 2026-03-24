# Условные конструкции: как научить компьютер принимать решения

![Робот на перекрестке выбора пути](covers/cover_6_control_flow.png)

Представь, что ты стоишь перед перекрестком. Если горит зеленый [свет](../../1.2_natural_sciences/physics_in_everyday_life/Q1.md) — ты идешь. Если красный — стоишь. А если желтый — готовишься. Ты только что выполнил «[алгоритм](../../2.1_society/cause_and_effect_relationships/articles/ai_causality.md) с условием»! 🚦

Компьютеры на самом деле не очень умные. Они просто очень быстро выполняют команды. Чтобы [программа](../../5.1_technology_and_digital_literacy/operating system/articles/process.md) не просто шла по прямой, а умела выбирать [путь](../../1.2_natural_sciences/physics_in_everyday_life/Q11476.md) (например, пускать игрока на [уровень](../../../8.1_entertainment/articles/gamification.md) или нет), программисты используют **условные конструкции**. 

Давай узнаем, как заставить [C](../../2.1_society/how_and_where_find_friends/articles/sora_drug.md)++ «думать» и выбирать!

---

## Что такое «Если» в коде?

В языке C++ самая главная [команда](../../4.1_rules_of_study/how_to_learn_effectively/articles/peer_learning.md) для принятия решений — это слово `if` (в переводе с английского — «если»). 

Работает это так:
1. Компьютер видит слово `if`.
2. Он проверяет условие в скобках.
3. Если условие — **Правда** (True), он выполняет [код](1_introduction.md).
4. Если условие — **[Ложь](../../2.1_society/cause_and_effect_relationships/articles/false_connections.md)** (False), он просто перепрыгивает этот кусок кода.

### Пример с мороженым 🍦

```c++
#include <iostream>

int main() {
    int money = 100; // У нас есть 100 рублей
    int ice_cream_price = 80; // Мороженое стоит 80

    if (money >= ice_cream_price) {
        std::cout << "Ура! Покупаем мороженое!" << std::endl;
    }

    return 0;
}
```

> [!NOTE]
> Обрати [внимание](../../1.2_natural_sciences/neurobiology_for_teens/articles/16_love_chemistry.md) на фигурные скобки `{ }`. Всё, что находится внутри них, выполнится только тогда, когда условие сработает. Это «домик» для твоего кода.

---

## А что если... (Использование else)

Иногда нам мало просто сказать «если». Нам нужно [решение](../../2.1_society/cause_and_effect_relationships/articles/personal_choice.md) на случай, если условие **не выполнилось**. Для этого есть команда `else` (в переводе — «иначе»).

**[Аналогия](../../1.2_natural_sciences/physics_in_everyday_life/Q46344.md):** Если на улице [дождь](../../3.2 healthy lifestyle/how to act in a dangerous situation/articles/thunderstorm-safety.md) — возьми зонт, иначе — надень кепку.

```c++
if (rain == true) {
    std::cout << "Берем зонт!" << std::endl;
} else {
    std::cout << "Надеваем кепку!" << std::endl;
}
```

---

## Много выборов: else if

А что, если вариантов больше двух? Например, в игре у тебя может быть золотая медаль, серебряная или вообще никакой. Тогда на [помощь](../../3.1_healthy_lifestyle/pervaya_pomoshch/ushibi_porezy_ozhogi/10_krovotechenie_chto_delat.md) приходит `else if` («а если еще»).

```c++
int place = 2; // Твое место в гонке

if (place == 1) {
    std::cout << "Золотая медаль! 🥇" << std::endl;
} else if (place == 2) {
    std::cout << "Серебряная медаль! 🥈" << std::endl;
} else if (place == 3) {
    std::cout << "Бронзовая медаль! 🥉" << std::endl;
} else {
    std::cout << "Главное — участие! 🏃" << std::endl;
}
```

> [!IMPORTANT]
> Компьютер проверяет условия сверху вниз. Как только он найдет первое верное условие, он выполнит его код и проигнорирует всё остальное, что идет ниже.

---

## Знаки сравнения: как мы проверяем условия?

Чтобы сравнивать числа, нам нужны специальные знаки. В C++ они немного отличаются от тех, что ты учишь в школе:

| Знак | Что означает | Пример |
| :--- | :--- | :--- |
| `==` | Равно ([проверка](../../1.2_natural_sciences/why_science_help_understand_world/scientific_method.md)) | `5 == 5` (Правда) |
| `!=` | Не равно | `5 != 3` (Правда) |
| `>` | Больше | `10 > 5` (Правда) |
| `<` | Меньше | `2 < 8` (Правда) |
| `>=` | Больше или равно | `5 >= 5` (Правда) |
| `<=` | Меньше или равно | `4 <= 10` (Правда) |

> [!WARNING]
> Самая частая [ошибка](../../5.1_technology_and_digital_literacy/how_internet_works/articles/http_https/http_https.md) новичка — путать `=` и `==`.  
> Один знак `=` — это **присваивание** (мы кладем [значение](../../7.2 Media, leisure and hobbies /useful_and_interesting_leisure/articles/leisure_and_why_need.md) в коробку).  
> Два знака `==` — это **[сравнение](5_operators.md)** (мы спрашиваем: «А они одинаковые?»).

---

## Сложные условия (Логические операторы)

Иногда нужно проверить сразу две вещи. Например: «Если у меня есть билет **И** мне исполнилось 12 лет, то я могу пойти на [фильм](../../../8.1_entertainment/articles/movie.md)».

1. **И (`&&`)** — условие верно, только если **оба** пункта правда.
2. **ИЛИ (`||`)** — условие верно, если **хотя бы один** пункт правда.
3. **НЕ (`!`)** — делает всё наоборот (правду превращает в ложь).

**Пример:**
```c++
bool has_ticket = true;
int age = 10;

if (has_ticket && age >= 12) {
    std::cout << "Добро пожаловать в кинозал!" << std::endl;
} else {
    std::cout << "Извини, ты не можешь пройти." << std::endl;
}
```
*В этом примере мы не пройдем, потому что [возраст](../../5.1_technology_and_digital_literacy/information and media literacy/карта_компетенций_по_возрастам.md) меньше 12, хотя билет есть.*

---

## [Оператор](../../3.2 healthy lifestyle/how to act in a dangerous situation/articles/emergency-112.md) Switch: Волшебный переключатель

Если у тебя очень много вариантов (например, [выбор](../../2.1_society/cause_and_effect_relationships/articles/personal_choice.md) дня недели или [цвета](../../1.2_natural_sciences/physics_in_everyday_life/Q11652.md)), писать много `if else` становится скучно. Для этого придумали `switch`. Это как пульт от телевизора: нажал кнопку — включился нужный канал.

```c++
int button = 2;

switch (button) {
    case 1:
        std::cout << "Включаем мультики!" << std::endl;
        break;
    case 2:
        std::cout << "Включаем передачу про животных!" << std::endl;
        break;
    case 3:
        std::cout << "Включаем новости." << std::endl;
        break;
    default:
        std::cout << "Такой кнопки нет!" << std::endl;
}
```

> [!TIP]
> Не забывай ставить `break` после каждого варианта! Если его не будет, компьютер «провалится» дальше и выполнит все команды из следующих кнопок подряд.

---

## Маленький секрет: Тернарный оператор

Если твой выбор совсем крошечный, его можно записать в одну строку. Это выглядит немного странно, но профессионалы это любят.

`условие ? значение_если_да : значение_если_нет;`

**Пример:**
```c++
int score = 50;
std::string result = (score >= 40) ? "Сдал!" : "Не сдал...";
std::cout << result;
```

---

## [Типичные ошибки](../../6.1_Independent_living_and_daily_living_skills/Simple_and_safe_cooking/articles/safe_use_of_kitchen_appliances.md), которых стоит избегать 🚫

1. **Забытые скобки.** Условие всегда должно быть в круглых скобках: `if (x > 0)`.
2. **Лишняя точка с запятой.** Никогда не ставь `;` сразу после `if (...)`. Если ты напишешь `if (x > 0);`, то компьютер подумает, что условие закончилось прямо здесь, и выполнит следующий код в любом случае.
3. **Путаница с `else`.** Помни, что `else` не может существовать сам по себе, без `if` сверху.

---

## Задание для самопроверки 🎮

Попробуй представить код для такой [задачи](../../1.2_natural_sciences/why_science_help_understand_world/research_work.md):
Ты создаешь игру-тест. Игрок вводит число от 1 до 10.
- Если число меньше 5 — напиши «Холодно!».
- Если число от 5 до 8 — напиши «[Тепло](../../1.2_natural_sciences/physics_in_everyday_life/Q11382.md)!».
- Если число 9 или 10 — напиши «Горячо!».

Как бы ты это написал, используя `if` и `else if`?

---

## Подведём итоги

Условные конструкции — это «[мозг](../../3.1. healthy lifestyle/Sleep, nutrition, and adolescent energy/articles/breakfast_for_the_brain.md)» твоей программы. Без них программы были бы скучными и линейными. Теперь ты умеешь создавать развилки и заставлять код выбирать правильный путь!

На следующем этапе мы узнаем, как зацикливать эти [действия](../../3.1_healthy_lifestyle/pervaya_pomoshch/ushibi_porezy_ozhogi/03_obschie_pravila_algorithm.md), чтобы не [повторять](../../4.1_rules_of_study/how_to_memorize/articles/povtorenie.md) код по сто раз.

**Удачи в изучении C++!** 🐾

---
[Вернуться к списку статей](./article_index_information_media_literacy.md)

---
[Автор](../../4.2_thinking_and_working_information/how_to_search_information/articles/copypaste.md): Кривошапкин Егор;  
*[Ресурсы](../../2.1_society/cause_and_effect_relationships/articles/ecological_footprint.md): [LLM](../../7.1_art/modern_technological_art/README.md) - Gemini*