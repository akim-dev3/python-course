# ============================================================
# МОДУЛЬ 4 — P3 GUIDED: ПОИСК
#
# Формат: код частично написан — заполни пропуски.
# Пропуск обозначен: None  (замени на настоящий код)
#
# ГЛАВНОЕ:
#   Линейный поиск — идём по каждому элементу. O(n).
#   Бинарный поиск — делим пополам. O(log n). Только на отсортированном!
#
# БИНАРНЫЙ ПОИСК — алгоритм, который нужно понять наизусть:
#
#   left = 0              ← левая граница поиска
#   right = len(lst) - 1  ← правая граница
#
#   while left <= right:
#       mid = (left + right) // 2   ← середина
#       if lst[mid] == target:      ← нашли
#           return mid
#       elif lst[mid] < target:     ← target ПРАВЕЕ середины
#           left = mid + 1          ← сдвигаем левую границу
#       else:                       ← target ЛЕВЕЕ середины
#           right = mid - 1         ← сдвигаем правую границу
#
#   return -1  ← не нашли
# ============================================================

sorted_nums = [1, 3, 5, 7, 9, 12, 15, 18, 21, 24, 27, 30]

products = [
    {"id": 101, "name": "Laptop", "price": 1200, "in_stock": True},
    {"id": 102, "name": "Mouse", "price": 25, "in_stock": True},
    {"id": 103, "name": "Monitor", "price": 450, "in_stock": False},
    {"id": 104, "name": "Keyboard", "price": 80, "in_stock": True},
    {"id": 105, "name": "Headset", "price": 150, "in_stock": False},
]

products_by_id = sorted(products, key=lambda p: p["id"])


# ------------------------------------------------------------
# 1. linear_search — найти индекс элемента, перебором
#
# linear_search(sorted_nums, 12) → 5
# linear_search(sorted_nums, 99) → -1
#
# Паттерн: enumerate(lst) — даёт (индекс, значение) на каждом шаге
#   for i, val in enumerate(lst):
#       if val == target: return i
# ------------------------------------------------------------


def linear_search(lst, target):
    for i, val in enumerate(lst):
        if val == target:
            return i  # ← ПРОПУСК: вернуть индекс i
    return -1


print("=== Задача 1: linear_search ===")
print(linear_search(sorted_nums, 12))  # 5
print(linear_search(sorted_nums, 1))  # 0
print(linear_search(sorted_nums, 30))  # 11
print(linear_search(sorted_nums, 99))  # -1


# ------------------------------------------------------------
# 2. binary_search — найти индекс через деление пополам
#
# Скопируй алгоритм из шапки файла — буквально перенеси его
# внутрь функции, заменяя None на реальный код.
#
# ПРОГОН ВРУЧНУЮ (sorted_nums, target=21):
#   [1, 3, 5, 7, 9, 12, 15, 18, 21, 24, 27, 30]
#    0  1  2  3  4   5   6   7   8   9  10  11
#
#   left=0, right=11 → mid=5 → lst[5]=12
#   12 < 21 → target правее → left = 6
#
#   left=6, right=11 → mid=8 → lst[8]=21
#   21 == 21 → нашли! → return 8
# ------------------------------------------------------------


def binary_search(lst, target):
    left = 0
    right = len(lst) - 1

    while left <= right:
        mid = (left + right) // 2

        if lst[mid] == target:
            return mid  # ← ПРОПУСК: вернуть mid

        elif lst[mid] < target:
            left = mid + 1  # ← ПРОПУСК: сдвинуть left (mid + 1)

        else:
            right = mid - 1  # ← ПРОПУСК: сдвинуть right (mid - 1)

    return -1


print("\n=== Задача 2: binary_search ===")
print(binary_search(sorted_nums, 12))  # 5
print(binary_search(sorted_nums, 1))  # 0
print(binary_search(sorted_nums, 30))  # 11
print(binary_search(sorted_nums, 99))  # -1


# ------------------------------------------------------------
# 3. count_in_range — сколько элементов в диапазоне [low, high]?
#
# count_in_range(sorted_nums, 7, 21) → 6  (7,9,12,15,18,21)
#
# Простой вариант: один цикл, считаем подходящие. O(n).
# ------------------------------------------------------------


def count_in_range(sorted_lst, low, high):
    count = 0
    for x in sorted_lst:
        if low <= x <= high:  # ← ПРОПУСК: x в диапазоне [low, high]
            count += 1
    return count


print("\n=== Задача 3: count_in_range ===")
print(count_in_range(sorted_nums, 7, 21))  # 6
print(count_in_range(sorted_nums, 1, 1))  # 1
print(count_in_range(sorted_nums, 100, 200))  # 0
print(count_in_range(sorted_nums, 1, 30))  # 12


# ------------------------------------------------------------
# 4. find_insert_position — куда вставить value?
#
# find_insert_position([1,3,5,7], 4) → 2  (между 3 и 5)
# find_insert_position([1,3,5,7], 0) → 0  (перед всеми)
# find_insert_position([1,3,5,7], 8) → 4  (после всех)
#
# Адаптируем бинарный поиск: вместо поиска точного совпадения
# ищем место, где элемент должен стоять.
#
# ОТЛИЧИЕ от обычного бинарного:
#   - нет return mid при совпадении
#   - left сдвигается если lst[mid] < value  (а не <=)
#   - right идёт только вниз до left
#   - в конце: left — это и есть позиция вставки
#
# ПРОГОН: [1,3,5,7], value=4
#   left=0, right=3 → mid=1 → lst[1]=3
#   3 < 4 → left = 2
#   left=2, right=3 → mid=2 → lst[2]=5
#   5 >= 4 → right = 1
#   left=2 > right=1 → выходим
#   return left = 2 ✓
# ------------------------------------------------------------


def find_insert_position(sorted_lst, value):
    left = 0
    right = len(sorted_lst)  # обрати внимание: right = len, а не len-1
    # потому что можем вставить и после последнего

    while left < right:  # left < right (не <=, как в обычном)
        mid = (left + right) // 2

        if sorted_lst[mid] < value:
            left = mid + 1  # ← ПРОПУСК: left = mid + 1
        else:
            right = mid  # ← ПРОПУСК: right = mid

    return left  # left — позиция вставки


print("\n=== Задача 4: find_insert_position ===")
print(find_insert_position([1, 3, 5, 7], 4))  # 2
print(find_insert_position([1, 3, 5, 7], 0))  # 0
print(find_insert_position([1, 3, 5, 7], 8))  # 4
print(find_insert_position(sorted_nums, 10))  # 5


# ------------------------------------------------------------
# 5. first_exceeding — первый элемент СТРОГО больше threshold
#
# first_exceeding(sorted_nums, 5)  → 7
# first_exceeding(sorted_nums, 30) → None
# first_exceeding(sorted_nums, 0)  → 1
#
# Простой вариант: идём по порядку, первый подходящий — возвращаем. O(n).
# ------------------------------------------------------------


def first_exceeding(sorted_lst, threshold):
    for x in sorted_lst:
        if x > threshold:
            return x  # ← ПРОПУСК: вернуть x
    return None  # ← ничего не нашли — правильно, оставь None


print("\n=== Задача 5: first_exceeding ===")
print(first_exceeding(sorted_nums, 5))  # 7
print(first_exceeding(sorted_nums, 30))  # None
print(first_exceeding(sorted_nums, 0))  # 1
print(first_exceeding(sorted_nums, 29))  # 30


# ------------------------------------------------------------
# 6. search_by_field — линейный поиск в списке словарей
#
# Возвращает первый словарь, где data[field] == target.
# search_by_field(products, "name", "Monitor") → {"id": 103, ...}
# search_by_field(products, "id", 999)         → None
#
# Паттерн: for item in data: if item.get(field) == target: return item
# ------------------------------------------------------------


def search_by_field(data, field, target):
    for item in data:
        if item.get(field) == target:  # ← ПРОПУСК: с чем сравниваем?
            return item
    return None


print("\n=== Задача 6: search_by_field ===")
print(search_by_field(products, "name", "Monitor"))  # {"id": 103, ...}
print(search_by_field(products, "id", 999))  # None
print(search_by_field(products, "in_stock", False))  # {"id": 103, ...}
print(search_by_field(products, "price", 80))  # {"id": 104, ...}


# ------------------------------------------------------------
# 7. binary_search_by_field — бинарный поиск в списке словарей
#
# Список отсортирован по sort_field. Ищем объект где sort_field == target.
# Возвращает весь словарь или None.
#
# Это обычный бинарный поиск, но вместо lst[mid]
# используем data[mid].get(sort_field)
#
# ПРОГОН (products_by_id, sort_field="id", target=103):
#   ids: [101, 102, 103, 104, 105]  — индексы 0-4
#   left=0, right=4 → mid=2 → data[2]["id"]=103 → нашли! return data[2]
# ------------------------------------------------------------


def binary_search_by_field(data, sort_field, target):
    left = 0
    right = len(data) - 1

    while left <= right:
        mid = (left + right) // 2
        mid_val = data[mid].get(sort_field)  # значение поля в середине

        if mid_val == target:
            return data[mid]  # ← ПРОПУСК: вернуть data[mid] (весь словарь)

        elif mid_val < target:
            left = mid + 1  # ← ПРОПУСК: left = mid + 1

        else:
            right = mid - 1  # ← ПРОПУСК: right = mid - 1

    return None


print("\n=== Задача 7: binary_search_by_field ===")
print(binary_search_by_field(products_by_id, "id", 103))  # {"id": 103, ...}
print(binary_search_by_field(products_by_id, "id", 999))  # None
print(binary_search_by_field(products_by_id, "id", 101))  # {"id": 101, ...}
print(binary_search_by_field(products_by_id, "id", 105))  # {"id": 105, ...}
