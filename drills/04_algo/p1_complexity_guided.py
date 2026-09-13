# ============================================================
# МОДУЛЬ 4 — P1 GUIDED: СЛОЖНОСТЬ (Big O)
#
# Формат: код частично написан — заполни пропуски.
# Пропуск обозначен: None  (замени на настоящий код)
#
# После того как все задачи работают — переходи к p1_complexity.py
# и пиши всё с нуля.
# ============================================================

words = [
    "apple",
    "banana",
    "cherry",
    "apple",
    "date",
    "banana",
    "elderberry",
    "fig",
    "cherry",
    "grape",
]
numbers = [4, 2, 7, 1, 9, 3, 5, 8, 6, 10, 2, 7]
lst_a = ["apple", "banana", "cherry", "date"]
lst_b = ["banana", "elderberry", "apple", "fig", "cherry"]


# ------------------------------------------------------------
# 1. has_target — есть ли элемент в списке?
#
# SLOW: идём по каждому элементу через for. O(n).
# FAST: конвертируем список в set, потом проверяем in. O(1).
#
# Почему set быстрее: list ищет перебором, set — по хэшу (мгновенно).
# ------------------------------------------------------------


def has_target_slow(lst, target):
    for item in lst:
        if item == target:
            return True  # нашли — возвращаем сразу
    return False  # ← ПРОПУСК: что вернуть если не нашли?


def has_target_fast(lst, target):
    s = set(lst)  # конвертируем список в set — O(n) один раз
    return target in s  # ← ПРОПУСК: проверь, есть ли target в s (одна строка)


print("=== Задача 1 ===")
print(has_target_slow(words, "cherry"))  # True
print(has_target_slow(words, "mango"))  # False
print(has_target_fast(words, "cherry"))  # True
print(has_target_fast(words, "mango"))  # False


# ------------------------------------------------------------
# 2. has_duplicate — есть ли хоть один повтор?
#
# SLOW: два вложенных цикла — для каждого i проверяем все j после него.
#       Это O(n²) — очень медленно на большом списке.
#
# FAST: идём один раз, запоминаем виденные в set.
#       Если элемент уже в seen — нашли дубликат. O(n).
# ------------------------------------------------------------


def has_duplicate_slow(lst):
    for i in range(len(lst)):
        for j in range(
            i + 1, len(lst)
        ):  # j всегда > i, чтобы не сравнивать элемент с собой
            if lst[i] == lst[j]:  # ← ПРОПУСК: с чем сравниваем lst[i]?
                return True
    return False


def has_duplicate_fast(lst):
    seen = set()
    for x in lst:
        if x in seen:  # x уже встречался раньше — это дубликат
            return True  # ← ПРОПУСК: что вернуть?
        seen.add(x)  # запомнили x
    return False


print("\n=== Задача 2 ===")
print(has_duplicate_slow(words))  # True
print(has_duplicate_fast(words))  # True
print(has_duplicate_fast(numbers))  # True
print(has_duplicate_fast(["a", "b", "c"]))  # False


# ------------------------------------------------------------
# 3. first_duplicate — первый элемент, встреченный второй раз
#
# Та же идея: идём один раз + seen: set.
# Разница: не просто return True, а return сам элемент.
# ------------------------------------------------------------


def first_duplicate(lst):
    seen = set()
    for x in lst:
        if x in seen:
            return x  # ← ПРОПУСК: что именно вернуть? (не True, а сам элемент)
        seen.add(x)  # ← ПРОПУСК: добавь x в seen (одна строка)
    return None  # ← ничего не нашли — это правильно, оставь None


print("\n=== Задача 3 ===")
print(first_duplicate(words))  # "apple"
print(first_duplicate(numbers))  # 2
print(first_duplicate(["x", "y", "z"]))  # None


# ------------------------------------------------------------
# 4. count_frequencies — сколько раз каждое слово встречается
#
# Это GROUP BY из Модуля 3 — теперь понимаем почему он O(n).
# Один проход по списку, в dict накапливаем счётчик.
# ------------------------------------------------------------

sentence = ["the", "cat", "sat", "on", "the", "mat", "the", "cat"]


def count_frequencies(lst):
    result = {}
    for word in lst:
        result[word] = result.get(word, 0) + 1
    return result


print("\n=== Задача 4 ===")
print(count_frequencies(sentence))
# {"the": 3, "cat": 2, "sat": 1, "on": 1, "mat": 1}


# ------------------------------------------------------------
# 5. common_elements — элементы, которые есть в обоих списках
#
# SLOW: для каждого из lst1 проходим по всему lst2. O(n²).
# FAST: set intersection — set(lst1) & set(lst2). O(n).
# ------------------------------------------------------------


def common_elements_slow(lst1, lst2):
    result = []
    for item in lst1:
        if item in lst2:  # in list — это O(n)! вот откуда O(n²)
            if item not in result:  # чтобы не добавлять дубликаты
                result.append(item)
    return result


def common_elements_fast(lst1, lst2):
    # & — это пересечение множеств: элементы, которые есть в обоих
    common = set(lst1) & set(lst2)  # ← ПРОПУСК: set(lst1) & set(???)
    return list(common)


print("\n=== Задача 5 ===")
print(sorted(common_elements_slow(lst_a, lst_b)))  # ["apple", "banana", "cherry"]
print(sorted(common_elements_fast(lst_a, lst_b)))  # ["apple", "banana", "cherry"]


# ------------------------------------------------------------
# 6. find_pair_sum — два числа с суммой target
#
# Задача: найти два разных числа x и y такие, что x + y == target.
#
# МЕДЛЕННЫЙ способ: два вложенных цикла — O(n²).
# БЫСТРЫЙ способ: O(n) через seen: set.
#
# Логика быстрого:
#   Идём по числам. Для каждого x проверяем: есть ли (target - x) в seen?
#   Если есть — нашли пару! (target - x) + x == target.
#   Если нет — добавляем x в seen и идём дальше.
#
# Пример: lst = [4, 2, 7], target = 11
#   x=4: ищем 7 в seen={} → нет. seen={4}
#   x=2: ищем 9 в seen={4} → нет. seen={4,2}
#   x=7: ищем 4 в seen={4,2} → ЕСТЬ! Возвращаем (4, 7).
# ------------------------------------------------------------


def find_pair_sum(lst, target):
    seen = set()
    for x in lst:
        complement = target - x  # вот это нам нужно найти в seen
        if complement in seen:
            return (
                complement,
                x,
            )  # ← ПРОПУСК: верни кортеж из двух чисел (complement, x)
        seen.add(x)
    return None


print("\n=== Задача 6 ===")
print(
    find_pair_sum(numbers, 11)
)  # (2, 9) или (1, 10) или другая пара — главное сумма 11
print(find_pair_sum(numbers, 100))  # None
print(find_pair_sum(numbers, 3))  # пара с суммой 3


# ------------------------------------------------------------
# 7. unique_count — количество уникальных элементов
#
# Самая короткая задача модуля.
# set автоматически убирает дубликаты — остаются только уникальные.
# ------------------------------------------------------------


def unique_count(lst):
    return len(set(lst))  # ← ПРОПУСК: одна строка — конвертируй в set, возьми len


print("\n=== Задача 7 ===")
print(unique_count(words))  # 7
print(unique_count(numbers))  # 10
