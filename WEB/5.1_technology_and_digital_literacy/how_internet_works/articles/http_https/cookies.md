# Что такое cookies и зачем они нужны

Ты заходишь на сайт, вводишь [логин](../../../../5.2_cybersecurity/passwords_cyber_safety/articles/login.md) и [пароль](../../../../3.2 healthy lifestyle/how to act in a dangerous situation/articles/internet-safety.md). Перезагружаешь страницу — и ты всё ещё залогинен. Добавляешь товар в корзину, переходишь на другую вкладку — товар никуда не делся. Как сайт «помнит» тебя?

[Ответ](http_https.md) — **cookies** (куки). Это небольшие текстовые файлы, которые [браузер](http_https.md) сохраняет на твоём компьютере и автоматически отправляет серверу при каждом запросе.

---

## Проблема, которую решают cookies

[HTTP](http_https.md) — **[протокол](http_https.md) без состояния** (stateless). Это значит, что для сервера каждый [запрос](http_https.md) — как первая встреча. [Сервер](http_https.md) не помнит, что ты уже делал секунду назад.

**[Аналогия](../../../../1.2_natural_sciences/physics_in_everyday_life/Q46344.md):** представь продавца в магазине, у которого после каждого покупателя полностью стирается [память](../../../../3.1. healthy lifestyle/Sleep, nutrition, and adolescent energy/articles/sleep_and_memory_grades.md). Ты говоришь: «Дайте мне продолжение моего заказа», — а он смотрит на тебя как на незнакомца.

Cookies — это как бейдж, который магазин вешает тебе на грудь при входе. Продавец видит бейдж и сразу «вспоминает», кто ты.

---

## Как работают cookies

1. Ты заходишь на сайт в первый раз
2. Сервер отвечает и добавляет в [заголовок](http_https.md) ответа специальную строку: `Set-Cookie: session_id=abc123`
3. Браузер сохраняет cookie на [диск](../../../operating system/articles/file_system.md)
4. При каждом следующем запросе браузер **автоматически** добавляет: `Cookie: session_id=abc123`
5. Сервер видит cookie и «вспоминает» тебя

```
Первый запрос:
  Браузер → Сервер:  GET /page
  Сервер → Браузер:  200 OK
                     Set-Cookie: session_id=abc123

Следующий запрос:
  Браузер → Сервер:  GET /profile
                     Cookie: session_id=abc123
  Сервер → Браузер:  200 OK  (знает, кто ты)
```

---

## Что хранится в cookies

Cookie — это пара «имя=[значение](../../../../7.2 Media, leisure and hobbies /useful_and_interesting_leisure/articles/leisure_and_why_need.md)». Примеры:

| Cookie | Что означает |
|--------|-------------|
| `session_id=abc123` | Идентификатор сессии — чтобы ты оставался залогиненным |
| `theme=dark` | Выбранная тема оформления |
| `lang=ru` | Выбранный [язык](../../../../5.2_cybersecurity/cpp_fundamentals/1_introduction.md) |
| `cart=item1,item2` | Содержимое корзины |

Каждый cookie также имеет параметры:

| Параметр | Что означает |
|----------|-------------|
| `Expires` | Дата истечения. Если нет — удаляется при закрытии браузера |
| `HttpOnly` | Недоступен для JavaScript ([защита](../dns/cdn.md) от кражи) |
| `Secure` | Передаётся только по [HTTPS](http_https.md) |
| `SameSite` | Защита от межсайтовых атак |

---

## [Виды](../../../../3.1_healthy_lifestyle/pervaya_pomoshch/ushibi_porezy_ozhogi/08_porezy_sadiny_vidy.md) cookies

### Сессионные cookies
Хранятся только пока открыт браузер. Как только закрываешь браузер — исчезают.

*Пример: временная корзина покупок, [форма](../../../../7.1_art/modern_technological_art/articles/4.5_algorithmic_craft.md) входа на одну сессию.*

### Постоянные cookies
Хранятся на диске до указанной даты — дни, месяцы, годы.

*Пример: «[Запомнить](../../../../4.1_rules_of_study/how_to_memorize/articles/zapominanie.md) меня» при входе в почту — остаёшься залогиненным неделями.*

### Сторонние cookies (third-party)
Устанавливаются не тем сайтом, который ты посещаешь, а встроенными элементами других компаний — рекламой, кнопками «Поделиться», виджетами.

*Пример: ты смотришь кроссовки на одном сайте → рекламная [сеть](../history/internet_history.md) устанавливает свой cookie → теперь реклама этих кроссовок «преследует» тебя на всех сайтах, где есть реклама той же сети.*

> **Знаешь ли ты?** Именно из-за сторонних cookies появились баннеры «Принять cookies» на всех сайтах. Европейский [закон](../../../../1.2_natural_sciences/physics_in_everyday_life/Q41719.md) (GDPR, 2018) обязал сайты спрашивать [разрешение](../../../../7.2 Media, leisure and hobbies/Computer games/articles/technologies_inside/screen_magic.md) на отслеживание. [Firefox](../web_basics/browser.md) и [Safari](../web_basics/browser.md) блокируют сторонние cookies по умолчанию.

---

## [Безопасность](../../../../1.2_natural_sciences/neurobiology_for_teens/articles/17_hugs_oxytocin.md) cookies

**Cookies — не вирусы.** Это просто текстовые файлы, они не могут запускать [код](../../../../5.2_cybersecurity/cpp_fundamentals/1_introduction.md) или причинить [вред](../../../../3.1. healthy lifestyle/Sleep, nutrition, and adolescent energy/articles/the_energy_trap.md) сами по себе.

Но у них есть [риски](../../../../7.2 Media, leisure and hobbies /useful_and_interesting_leisure/articles/safety_during_recreation.md):

- **Кража сессионного cookie** — если злоумышленник получит твой `session_id`, он сможет войти в твой [аккаунт](../../../information and media literacy/информационная_безопасность_для_детей.md) без пароля. Именно поэтому важен параметр `HttpOnly` (JavaScript не может прочитать такой cookie) и `Secure` (cookie передаётся только по HTTPS).
- **Слежка через сторонние cookies** — [сбор данных](../../../../1.2_natural_sciences/why_science_help_understand_world/research.md) о твоих интересах рекламными сетями.

### Как защищают современные cookies

Хорошо настроенный cookie выглядит так:
```
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict; Expires=...
```
Все четыре параметра вместе закрывают основные уязвимости.

---

## Как управлять cookies в браузере

Ты можешь в любой момент:
- **Посмотреть** все cookies: DevTools (F12) → вкладка Application → Cookies
- **Удалить** cookies для конкретного сайта или все сразу — в настройках браузера
- **Запретить** сторонние cookies в настройках приватности

> **Осторожно:** если удалишь все cookies, браузер «забудет» все сайты — придётся заходить в аккаунты заново.

---

## Интересные [факты](../../../../1.2_natural_sciences/physics_in_everyday_life/Q17737.md)

- **Название «cookie»** взято из программирования — «magic cookie» означал маленький [пакет](../tcp_udp/tcp_udp.md) данных, который передаётся туда-обратно без изменений. Первые HTTP-cookies придумал Лу Монтулли в 1994 году.
- **Первый cookie** был создан специально для интернет-магазина — чтобы корзина покупок не сбрасывалась при переходе между страницами.
- **Размер cookies** ограничен — [максимум](../../../../1.2_natural_sciences/physics_in_everyday_life/Q136980.md) около 4 КБ на cookie. Много данных в них не сохранить, поэтому обычно хранят только идентификатор, а остальное — на сервере.
- **LocalStorage и SessionStorage** — современные альтернативы cookies для хранения данных в браузере. Они вмещают до 5–10 МБ, но не отправляются серверу автоматически.

---

Авторы: Коростин Никита

*[Данные](../../../../2.1_society/cause_and_effect_relationships/articles/ai_causality.md): WikiData ([Q483326](https://www.wikidata.org/wiki/Q483326))*

*[Ресурсы](../../../../2.1_society/cause_and_effect_relationships/articles/ecological_footprint.md): [LLM](../../../../7.1_art/modern_technological_art/README.md) — Claude Sonnet 4.6*
