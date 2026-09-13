# ============================================================
# МОДУЛЬ 4 — P1: СЛОЖНОСТЬ АЛГОРИТМОВ (Big O)
#
# Цель: понять разницу между O(n) и O(n²),
#       научиться выбирать эффективный паттерн.
#
# КЛЮЧЕВЫЕ ФАКТЫ (перед задачами):
#   "x" in list  → O(n)   — перебор каждого элемента
#   "x" in set   → O(1)   — мгновенная проверка
#   dict["key"]  → O(1)   — доступ по ключу
#   два вложенных цикла → O(n²)
#
# Правило перед каждой задачей:
#   # Вход: ... Выход: ... Паттерн: ... Сложность: ...
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

sentence = ["the", "cat", "sat", "on", "the", "mat", "the", "cat"]

lst_a = ["apple", "banana", "cherry", "date"]
lst_b = ["banana", "elderberry", "apple", "fig", "cherry"]


# ------------------------------------------------------------
# 1. has_target_slow(lst, target) → bool   [O(n) — цикл]
#    has_target_fast(lst, target) → bool   [O(1) — set]
#
# Есть ли target в списке?
# Ожидается: True для "cherry", False для "mango"
#
# ЗАДАЧА: напиши ОБА варианта.
# slow — обычный цикл for
# fast — сначала конвертируй lst в set, затем проверяй in
# ------------------------------------------------------------
def has_target_slow(lst, target):
    for item in lst:
        if item == target:
            return True
    return False


def has_target_fast(lst, target):
    s = set(lst)
    return target in s


print(has_target_slow(words, "cherry"))  # True
print(has_target_slow(words, "mango"))  # False
print(has_target_fast(words, "cherry"))  # True
print(has_target_fast(words, "mango"))  # False


# ------------------------------------------------------------
# 2. has_duplicate_slow(lst) → bool   [O(n²)]
#    has_duplicate_fast(lst) → bool   [O(n)]
#
# Есть ли хотя бы один повторяющийся элемент?
# Ожидается: True для words и numbers
# Ожидается: False для ["a", "b", "c"]
#
# slow — два вложенных цикла (i, j где j > i)
# fast — один проход через seen: set
# ------------------------------------------------------------
def has_duplicate_slow(lst):
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] == lst[j]:
                return True
    return False


def has_duplicate_fast(lst):
    seen = set()
    for x in lst:
        if x in seen:
            return True
        seen.add(x)
    return False


print(has_duplicate_slow(words))  # True
print(has_duplicate_fast(words))  # True
print(has_duplicate_fast(numbers))  # True
print(has_duplicate_fast(["a", "b", "c"]))  # False


# ------------------------------------------------------------
# 3. first_duplicate(lst) → any | None
#
# Первый элемент, встретившийся второй раз (в порядке обхода).
# Ожидается: "apple" для words (apple появляется на позиции 3)
# Ожидается: 2 для numbers (первое повторение — цифра 2)
# Ожидается: None для ["x", "y", "z"]
#
# Паттерн: seen: set — добавляй элемент, проверяй перед добавлением
# Сложность: O(n)
# ------------------------------------------------------------
def first_duplicate(lst):
    seen = set()
    for i in lst:
        if i in seen:
            return i
        seen.add(i)
    return None


print(first_duplicate(words))  # "apple"
print(first_duplicate(numbers))  # 2
print(first_duplicate(["x", "y", "z"]))  # None


# ------------------------------------------------------------
# 4. count_frequencies(lst) → dict[str, int]
#
# Сколько раз каждое слово встречается в списке. O(n).
# Ожидается для sentence:
#   {"the": 3, "cat": 2, "sat": 1, "on": 1, "mat": 1}
#
# Паттерн: COUNT GROUP BY — уже знакомый dict-паттерн,
#          теперь понимаем почему он O(n)
# ------------------------------------------------------------
def count_frequencies(lst):
    counts = {}
    for i in lst:
        counts[i] = counts.get(i, 0) + 1
    return counts


print(count_frequencies(sentence))
# {"the": 3, "cat": 2, "sat": 1, "on": 1, "mat": 1}


# ------------------------------------------------------------
# 5. common_elements_slow(lst1, lst2) → list   [O(n²)]
#    common_elements_fast(lst1, lst2) → list   [O(n)]
#
# Элементы, присутствующие в обоих списках (без дубликатов).
# Ожидается: ["apple", "banana", "cherry"] (порядок не важен)
#
# slow — вложенный цикл: для каждого из lst1 проверяй в lst2
# fast — set intersection: set(lst1) & set(lst2)
# ------------------------------------------------------------
def common_elements_slow(lst1, lst2):
    list_all = []
    for el1 in lst1:
        for el2 in lst2:
            if el1 == el2:
                list_all.append(el1)
    return list_all


def common_elements_fast(lst1, lst2):
    common = set(lst1) & set(lst2)
    return common


print(sorted(common_elements_slow(lst_a, lst_b)))  # ["apple", "banana", "cherry"]
print(sorted(common_elements_fast(lst_a, lst_b)))  # ["apple", "banana", "cherry"]


# ------------------------------------------------------------
# 6. find_pair_sum(lst, target) → tuple[int, int] | None
#
# Два числа из списка, сумма которых равна target.
# Возвращает пару в любом порядке. O(n).
# Ожидается: find_pair_sum(numbers, 11) → кортеж двух чисел (≠)
# Ожидается: find_pair_sum(numbers, 100) → None
#
# Паттерн: для каждого x проверяй (target - x) in seen: set
# ------------------------------------------------------------
def find_pair_sum(lst, target):
    seen = set()
    for i in lst:
        if (target - i) in seen:
            return i, target - i
        seen.add(i)
    return None


print(find_pair_sum(numbers, 11))  # например (7, 4) или (4, 7)
print(find_pair_sum(numbers, 100))  # None
print(find_pair_sum(numbers, 3))  # например (2, 1) или (1, 2)


# ------------------------------------------------------------
# 7. unique_count(lst) → int
#
# Количество уникальных элементов. O(n).
# Ожидается: unique_count(words) = 7
# Ожидается: unique_count(numbers) = 10
#             (12 чисел, 2 и 7 повторяются — значит 10 уникальных)
# ------------------------------------------------------------
def unique_count(lst):
    return len(set(lst))


print(unique_count(words))  # 7
print(unique_count(numbers))  # 10
