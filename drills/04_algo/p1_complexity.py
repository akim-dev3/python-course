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


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


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


check(has_target_slow(words, "cherry"), True, "has_target_slow")
check(has_target_slow(words, "mango"), False, "has_target_slow")
check(has_target_fast(words, "cherry"), True, "has_target_fast")
check(has_target_fast(words, "mango"), False, "has_target_fast")


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


check(has_duplicate_slow(words), True, "has_duplicate_slow")
check(has_duplicate_fast(words), True, "has_duplicate_fast")
check(has_duplicate_fast(numbers), True, "has_duplicate_fast")
check(has_duplicate_fast(["a", "b", "c"]), False, "has_duplicate_fast")


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


check(first_duplicate(words), "apple", "first_duplicate")
check(first_duplicate(numbers), 2, "first_duplicate")
check(first_duplicate(["x", "y", "z"]), None, "first_duplicate")


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


check(count_frequencies(sentence), {"the": 3, "cat": 2, "sat": 1, "on": 1, "mat": 1}, "count_frequencies")


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


check(sorted(common_elements_slow(lst_a, lst_b)), ["apple", "banana", "cherry"], "common_elements_slow")
check(sorted(common_elements_fast(lst_a, lst_b)), ["apple", "banana", "cherry"], "common_elements_fast")


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


check(sorted(find_pair_sum(numbers, 11)), [4, 7], "find_pair_sum")  # пара в любом порядке
check(find_pair_sum(numbers, 100), None, "find_pair_sum")
check(sorted(find_pair_sum(numbers, 3)), [1, 2], "find_pair_sum")  # пара в любом порядке


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


check(unique_count(words), 7, "unique_count")
check(unique_count(numbers), 10, "unique_count")
