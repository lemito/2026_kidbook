import os

# Настройка путей
# Скрипт запускается из: ~/2026_kidbook/WORK/src
# Цель: ~/2026_kidbook/WEB/3.1_healthe_lifestyle/hygiene_and_personal_care

# Вычисляем путь относительно расположения этого скрипта
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Поднимаемся на 2 уровня вверх (из src -> WORK -> root), затем заходим в WEB...
TARGET_REL_PATH = "../../WEB/3.1_healthe_lifestyle/hygiene_and_personal_care"
TARGET_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, TARGET_REL_PATH))

# Список статей
articles = {
    # Уровень 1
    "handwashing": "Мытье рук",
    "shower": "Душ и ванна",
    "toothbrush": "Чистка зубов",
    "water": "Водный баланс",
    "sleep": "Сон",
    "sanitizer": "Антисептик для рук",

    # Уровень 2
    "facewash": "Умывание лица",
    "deodorant": "Дезодорант и запах",
    "haircare": "Уход за волосами",
    "shaving": "Бритье",
    "nails": "Стрижка ногтей",
    "lip_care": "Уход за губами",

    # Уровень 3
    "floss": "Зубная нить",
    "acne": "Прыщи и акне",
    "sunscreen": "Защита от солнца",
    "comb": "Личная расческа",
    "dentist": "Стоматолог",
    "dermatologist": "Дерматолог",

    # Уровень 4
    "clean_clothes": "Чистая одежда",
    "underwear": "Нижнее белье",
    "socks": "Носки и запах ног",
    "shoes": "Уход за обувью",
    "towel": "Личное полотенце",
    "bedding": "Постельное белье"
}

def create_files():
    print(f"[INFO] Target directory resolved to: {TARGET_DIR}")

    # Проверка наличия целевой папки
    if not os.path.exists(TARGET_DIR):
        print(f"[WARN] Directory not found. Attempting to create: {TARGET_DIR}")
        try:
            os.makedirs(TARGET_DIR)
        except OSError as e:
            print(f"[ERROR] Could not create directory: {e}")
            return

    # Генерация файлов
    count = 0
    for filename, title in articles.items():
        file_path = os.path.join(TARGET_DIR, f"{filename}.md")
        content = f"# {title}\n\nTODO"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[OK] Created: {filename}.md")
            count += 1
        except IOError as e:
            print(f"[ERROR] Failed to write {filename}.md: {e}")

    print(f"[INFO] Operation complete. {count} files processed.")

if __name__ == "__main__":
    create_files()