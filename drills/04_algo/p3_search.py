# ============================================================
# МОДУЛЬ 4 — P3: ПОИСК (ЛИНЕЙНЫЙ И БИНАРНЫЙ)
#
# ТЕОРИЯ (прочитай перед задачами):
#   Линейный поиск — перебираем каждый элемент. O(n).
#   Бинарный поиск — делим отсортированный список пополам. O(log n).
#
#   БИНАРНЫЙ ПОИСК — АЛГОРИТМ (выучи наизусть):
#
#   left, right = 0, len(lst) - 1
#   while left <= right:
#       mid = (left + right) // 2
#       if lst[mid] == target:  return mid
#       if lst[mid] < target:   left = mid + 1    # target ПРАВЕЕ
#       else:                   right = mid - 1   # target ЛЕВЕЕ
#   return -1
#
#   ВАЖНО: бинарный поиск работает ТОЛЬКО на отсортированном списке.
#
# Правило перед задачей:
#   # Вход: ... Выход: ... Поиск: линейный | бинарный
# ============================================================


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


sorted_nums = [1, 3, 5, 7, 9, 12, 15, 18, 21, 24, 27, 30]

products = [
    {"id": 101, "name": "Laptop", "price": 1200, "in_stock": True},
    {"id": 102, "name": "Mouse", "price": 25, "in_stock": True},
    {"id": 103, "name": "Monitor", "price": 450, "in_stock": False},
    {"id": 104, "name": "Keyboard", "price": 80, "in_stock": True},
    {"id": 105, "name": "Headset", "price": 150, "in_stock": False},
]

products_by_id = sorted(products, key=lambda p: p["id"])  # уже отсортирован по id


# ------------------------------------------------------------
# 1. linear_search(lst, target) → int
#
# Возвращает ИНДЕКС первого вхождения target или -1.
# linear_search(sorted_nums, 12)  → 5
# linear_search(sorted_nums, 1)   → 0
# linear_search(sorted_nums, 99)  → -1
#
# Паттерн: enumerate(lst) — даёт (индекс, значение)
# ------------------------------------------------------------
def linear_search(lst, target):
    for i, val in enumerate(lst):
        if val == target:
            return i
    return -1


check(linear_search(sorted_nums, 12), 5, "linear_search")
check(linear_search(sorted_nums, 1), 0, "linear_search")
check(linear_search(sorted_nums, 30), 11, "linear_search")
check(linear_search(sorted_nums, 99), -1, "linear_search")


# ------------------------------------------------------------
# 2. binary_search(lst, target) → int
#
# Бинарный поиск на отсортированном списке.
# Возвращает ИНДЕКС или -1.
# Используй алгоритм из шапки файла.
# binary_search(sorted_nums, 12)  → 5
# binary_search(sorted_nums, 99)  → -1
# ------------------------------------------------------------
def binary_search(lst, target):
    left, right = 0, len(lst) - 1

    while left <= right:
        mid = (left + right) // 2

        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


check(binary_search(sorted_nums, 12), 5, "binary_search")
check(binary_search(sorted_nums, 1), 0, "binary_search")
check(binary_search(sorted_nums, 30), 11, "binary_search")
check(binary_search(sorted_nums, 99), -1, "binary_search")


# ------------------------------------------------------------
# 3. count_in_range(sorted_lst, low, high) → int
#
# Количество элементов в диапазоне [low, high] включительно.
# count_in_range(sorted_nums, 7, 21)    → 6  (7,9,12,15,18,21)
# count_in_range(sorted_nums, 1, 1)     → 1
# count_in_range(sorted_nums, 100, 200) → 0
#
# Подсказка: можно через простой цикл (O(n)) — бинарный не обязателен
# ------------------------------------------------------------
def count_in_range(sorted_lst, low, high):
    count = 0
    for x in sorted_lst:
        if low <= x <= high:
            count += 1
    return count


check(count_in_range(sorted_nums, 7, 21), 6, "count_in_range")
check(count_in_range(sorted_nums, 1, 1), 1, "count_in_range")
check(count_in_range(sorted_nums, 100, 200), 0, "count_in_range")
check(count_in_range(sorted_nums, 1, 30), 12, "count_in_range")


# ------------------------------------------------------------
# 4. find_insert_position(sorted_lst, value) → int
#
# Куда вставить value, чтобы список остался отсортированным.
# Возвращает индекс (0-based).
#
# find_insert_position([1,3,5,7], 4) → 2  (между 3 и 5)
# find_insert_position([1,3,5,7], 0) → 0  (перед всеми)
# find_insert_position([1,3,5,7], 8) → 4  (после всех)
# find_insert_position(sorted_nums, 10) → 5 (между 9 и 12)
#
# Подсказка: адаптируй бинарный поиск:
#   не ищи точное совпадение, сдвигай left пока lst[mid] < value,
#   в итоге left будет позицией вставки
# ------------------------------------------------------------
def find_insert_position(sorted_lst, value):
    left, right = 0, len(sorted_lst)

    while left < right:
        mid = (left + right) // 2

        if sorted_lst[mid] < value:
            left = mid + 1
        else:
            right = mid
    return left


check(find_insert_position([1, 3, 5, 7], 4), 2, "find_insert_position")
check(find_insert_position([1, 3, 5, 7], 0), 0, "find_insert_position")
check(find_insert_position([1, 3, 5, 7], 8), 4, "find_insert_position")
check(find_insert_position(sorted_nums, 10), 5, "find_insert_position")
check(find_insert_position(sorted_nums, 0), 0, "find_insert_position")


# ------------------------------------------------------------
# 5. first_exceeding(sorted_lst, threshold) → int | None
#
# Первый элемент строго больше threshold. O(n) или O(log n).
# first_exceeding(sorted_nums, 5)  → 7   (5 не считается)
# first_exceeding(sorted_nums, 30) → None (нет элементов > 30)
# first_exceeding(sorted_nums, 0)  → 1
# ------------------------------------------------------------
def first_exceeding(sorted_lst, threshold):
    for x in sorted_lst:
        if x > threshold:
            return x
    return None


check(first_exceeding(sorted_nums, 5), 7, "first_exceeding")
check(first_exceeding(sorted_nums, 30), None, "first_exceeding")
check(first_exceeding(sorted_nums, 0), 1, "first_exceeding")
check(first_exceeding(sorted_nums, 29), 30, "first_exceeding")


# ------------------------------------------------------------
# 6. search_by_field(data, field, target) → dict | None
#
# Линейный поиск: возвращает ПЕРВЫЙ dict, где data[field] == target.
# Возвращает весь объект или None.
# search_by_field(products, "name", "Monitor") → {"id": 103, ...}
# search_by_field(products, "id", 999)         → None
# search_by_field(products, "in_stock", False) → {"id": 103, ...}
# ------------------------------------------------------------
def search_by_field(data, field, target):
    for item in data:
        if item.get(field) == target:
            return item
    return None


check(search_by_field(products, "name", "Monitor"), {"id": 103, "name": "Monitor", "price": 450, "in_stock": False}, "search_by_field")
check(search_by_field(products, "id", 999), None, "search_by_field")
check(search_by_field(products, "in_stock", False), {"id": 103, "name": "Monitor", "price": 450, "in_stock": False}, "search_by_field")
check(search_by_field(products, "price", 80), {"id": 104, "name": "Keyboard", "price": 80, "in_stock": True}, "search_by_field")


# ------------------------------------------------------------
# 7. binary_search_by_field(data, sort_field, target) → dict | None
#
# Бинарный поиск в списке словарей, отсортированном по sort_field.
# Возвращает весь объект или None.
# data = products_by_id (отсортирован по "id": 101, 102, 103, 104, 105)
#
# Адаптируй стандартный binary_search:
#   вместо lst[mid] используй data[mid].get(sort_field)
# ------------------------------------------------------------
def binary_search_by_field(data, sort_field, target):
    left, right = 0, len(data) - 1

    while left <= right:
        mid = (left + right) // 2
        mid_val = data[mid].get(sort_field)

        if mid_val == target:
            return data[mid]
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1
    return None


check(binary_search_by_field(products_by_id, "id", 103), {"id": 103, "name": "Monitor", "price": 450, "in_stock": False}, "binary_search_by_field")
check(binary_search_by_field(products_by_id, "id", 999), None, "binary_search_by_field")
check(binary_search_by_field(products_by_id, "id", 101), {"id": 101, "name": "Laptop", "price": 1200, "in_stock": True}, "binary_search_by_field")
check(binary_search_by_field(products_by_id, "id", 105), {"id": 105, "name": "Headset", "price": 150, "in_stock": False}, "binary_search_by_field")
