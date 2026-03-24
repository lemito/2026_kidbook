# Как узнать свой [IP](ip_and_mac.md) и [MAC-адрес](ip_and_mac.md)

Каждое [устройство](../../../../1.2_natural_sciences/physics_in_everyday_life/Q178032.md) в сети имеет адреса — IP и [MAC](ip_and_mac.md). Иногда их нужно знать: при настройке сети, при решении проблем с интернетом или просто из любопытства. Подробнее о [том](../../../../7.1_art/musical_instruments/articles/drums.md), что это такое — в статье [IP и MAC-адреса](ip_and_mac.md).

---

## Публичный [IP-адрес](ip_and_mac.md)

Это [адрес](ip_and_mac.md), который видит весь [интернет](../../../../1.2_natural_sciences/physics_in_everyday_life/Q26540.md) — адрес твоего роутера. Самый простой способ узнать его — зайти на любой из этих сайтов:

- [whatismyip.com](https://whatismyip.com)
- [2ip.ru](https://2ip.ru)

Ты увидишь что-то вроде `85.249.112.47`. Это и есть твой публичный IP.

> Если ты подключён через [мобильный интернет](../wifi/wifi_vs_mobile_net.md) — это адрес твоего оператора. Если через домашний [Wi-Fi](../history/internet_at_home.md) — адрес роутера.

---

## Локальный IP-адрес

Это [приватный адрес](nat.md) внутри твоей домашней сети — тот, который выдал [роутер](../wifi/router.md) именно твоему устройству. Обычно начинается с `192.168.` или `10.`.

### [Windows](../../../operating system/articles/operating_system.md)

Открой командную строку (Win + R → `cmd` → Enter) и введи:

```
ipconfig
```

Ищи строку **IPv4-адрес** — например:

```
IPv4-адрес. . . . . . . . . : 192.168.1.42
```

### [macOS](../../../operating system/articles/operating_system.md)

Открой Терминал и введи:

```
ifconfig | grep "inet "
```

Или через графический интерфейс: Системные настройки → [Сеть](../history/internet_history.md) → выбери своё [подключение](../../../../1.2_natural_sciences/physics_in_everyday_life/Q25250.md).

### [Linux](../../../operating system/articles/operating_system.md)

```
ip addr show
```

или

```
ifconfig
```

Ищи строку `inet` рядом с названием интерфейса (`eth0`, `wlan0` и т.п.).

---

## MAC-адрес

### Windows

В той же командной строке:

```
ipconfig /all
```

Ищи строку **[Физический адрес](ip_and_mac.md)** (Physical Address):

```
Физический адрес. . . . . . : A4-C3-F0-85-AC-2D
```

### macOS / Linux

```
ifconfig
```

Ищи строку **ether**:

```
ether a4:c3:f0:85:ac:2d
```

---

## [ARP-кэш](ip_and_mac.md): кто ещё есть в сети

Чтобы увидеть все [устройства](../../../operating system/articles/HAL.md), с которыми твой компьютер недавно общался в локальной сети (с их IP и MAC-адресами):

```
arp -a
```

Работает на Windows, macOS и Linux одинаково. Пример вывода:

```
192.168.1.1     d4-6e-0e-11-22-33   (роутер)
192.168.1.10    b8-27-eb-44-55-66
192.168.1.15    3c-22-fb-aa-bb-cc
```

---

## Шпаргалка

| Что узнать | Windows | macOS / Linux |
|---|---|---|
| Публичный IP | [whatismyip.com](https://whatismyip.com) | [whatismyip.com](https://whatismyip.com) |
| Локальный IP | `ipconfig` | `ifconfig` или `ip addr` |
| MAC-адрес | `ipconfig /all` | `ifconfig` (строка `ether`) |
| Устройства в сети | `arp -a` | `arp -a` |

---

*← [IP и MAC-адреса](ip_and_mac.md)*

---

*[Автор](../../../../4.2_thinking_and_working_information/how_to_search_information/articles/copypaste.md): Денис Коваленко*
*[LLM](../../../../7.1_art/modern_technological_art/README.md): Claude Sonnet*
