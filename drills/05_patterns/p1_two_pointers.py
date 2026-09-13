# ============================================================
# МОДУЛЬ 5 — P1: TWO POINTERS (два указателя)
#
# ТЕОРИЯ (прочитай перед задачами):
#   Два индекса идут по списку вместо вложенных циклов.
#   Работает там, где вложенный O(n²) можно свести к одному
#   проходу O(n) — обычно на отсортированных данных или когда
#   нужно сравнивать элементы с двух концов.
#
#   ШАБЛОН 1 — навстречу друг другу:
#   left, right = 0, len(lst) - 1
#   while left < right:
#       if <условие>:
#           left += 1
#       else:
#           right -= 1
#
#   ШАБЛОН 2 — в одну сторону (slow/fast):
#   slow = 0
#   for fast in range(len(lst)):
#       if <условие>:
#           lst[slow] = lst[fast]
#           slow += 1
#
# Правило перед задачей:
#   # Вход: ... Выход: ... Паттерн: какой шаблон ... Сложность: ...
# ============================================================


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


sorted_nums = [1, 3, 5, 7, 9, 12, 15, 18, 21, 24, 27, 30]

lst_a = [1, 2, 2, 3, 3, 3, 4, 5, 5]


# ------------------------------------------------------------
# 1. is_palindrome(s) → bool
#
# Проверяет, читается ли строка одинаково с обоих концов.
# is_palindrome("racecar") → True
# is_palindrome("hello")   → False
# is_palindrome("a")       → True
# is_palindrome("")        → True
#
# ЗАДАЧА: без s[::-1] и reversed() — сравнивай символы с двух
# концов двумя указателями, сдвигая их навстречу друг другу.
# ------------------------------------------------------------
def is_palindrome(s):
    left, right = 0, len(s) - 1

    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True


check(is_palindrome("racecar"), True, "is_palindrome")
check(is_palindrome("hello"), False, "is_palindrome")
check(is_palindrome("a"), True, "is_palindrome")
check(is_palindrome(""), True, "is_palindrome")


# ------------------------------------------------------------
# 2. reverse_in_place(lst) → None (меняет lst на месте)
#
# Переворачивает список БЕЗ создания нового списка и без [::-1].
# lst = [1, 2, 3, 4, 5]
# reverse_in_place(lst) → lst теперь [5, 4, 3, 2, 1]
#
# Паттерн: два указателя с концов, меняй местами, сдвигай навстречу
# ------------------------------------------------------------
def reverse_in_place(lst):
    left, right = 0, len(lst) - 1

    while left < right:
        lst[left], lst[right] = lst[right], lst[left]
        left += 1
        right -= 1
    return lst


test_lst = [1, 2, 3, 4, 5]
reverse_in_place(test_lst)
check(test_lst, [5, 4, 3, 2, 1], "проверка")

test_lst2 = [1, 2]
reverse_in_place(test_lst2)
check(test_lst2, [2, 1], "проверка")


# ------------------------------------------------------------
# 3. two_sum_sorted(sorted_lst, target) → tuple[int, int] | None
#
# То же самое, что find_pair_sum из Модуля 4, но список уже
# ОТСОРТИРОВАН — здесь используй два указателя, а не set.
# Возвращай ЗНАЧЕНИЯ (не индексы). При нескольких валидных парах
# алгоритм с двух указателей всегда находит одну конкретную —
# ту, что получится по шаблону ниже (сужение с концов).
#
# two_sum_sorted(sorted_nums, 16) → (1, 15)   (есть и (7,9)=16, но
#                                    указатели найдут (1,15) раньше)
# two_sum_sorted(sorted_nums, 100) → None
#
# Паттерн: left=0, right=len-1. Если сумма < target — left+=1
#          (нужно число побольше). Если сумма > target — right-=1.
#          Если равна — нашёл.
# ------------------------------------------------------------
def two_sum_sorted(sorted_lst, target):
    left, right = 0, len(sorted_lst) - 1

    while left < right:
        if sorted_lst[left] + sorted_lst[right] < target:
            left += 1
        elif sorted_lst[left] + sorted_lst[right] > target:
            right -= 1
        else:
            return sorted_lst[left], sorted_lst[right]


check(two_sum_sorted(sorted_nums, 16), (1, 15), "two_sum_sorted")
check(two_sum_sorted(sorted_nums, 100), None, "two_sum_sorted")
check(two_sum_sorted(sorted_nums, 4), (1, 3), "two_sum_sorted")


# ------------------------------------------------------------
# 4. remove_duplicates_sorted(sorted_lst) → list
#
# Удаляет повторы из ОТСОРТИРОВАННОГО списка, сохраняя порядок.
# remove_duplicates_sorted(lst_a) → [1, 2, 3, 4, 5]
# remove_duplicates_sorted([1, 1, 1]) → [1]
# remove_duplicates_sorted([]) → []
#
# Паттерн: slow/fast — slow указывает куда писать следующий
# уникальный элемент, fast бежит по всему списку.
# Сложность: O(n)
# ------------------------------------------------------------
def remove_duplicates_sorted(sorted_lst):
    if not sorted_lst:
        return sorted_lst

    slow = 0
    for fast in range(1, len(sorted_lst)):
        if sorted_lst[fast] != sorted_lst[slow]:
            slow += 1
            sorted_lst[slow] = sorted_lst[fast]

    del sorted_lst[slow + 1 :]
    return sorted_lst


check(remove_duplicates_sorted(lst_a), [1, 2, 3, 4, 5], "remove_duplicates_sorted")
check(remove_duplicates_sorted([1, 1, 1]), [1], "remove_duplicates_sorted")
check(remove_duplicates_sorted([]), [], "remove_duplicates_sorted")


# ------------------------------------------------------------
# 5. merge_sorted(lst1, lst2) → list
#
# Сливает два ОТСОРТИРОВАННЫХ списка в один отсортированный.
# БЕЗ sorted(lst1 + lst2) — это было бы O(n log n), а два
# указателя дают O(n).
#
# merge_sorted([1, 3, 5], [2, 4, 6]) → [1, 2, 3, 4, 5, 6]
# merge_sorted([1, 2], [3, 4, 5])    → [1, 2, 3, 4, 5]
# merge_sorted([], [1, 2])           → [1, 2]
#
# Паттерн: i=0 (указатель в lst1), j=0 (указатель в lst2).
# Сравнивай lst1[i] и lst2[j], меньший добавляй в результат
# и сдвигай его указатель. В конце — доклей остаток.
# ------------------------------------------------------------
def merge_sorted(lst1, lst2):
    result = []
    i, j = 0, 0

    while i < len(lst1) and j < len(lst2):
        if lst1[i] < lst2[j]:
            result.append(lst1[i])
            i += 1
        else:
            result.append(lst2[j])
            j += 1

    result.extend(lst1[i:])
    result.extend(lst2[j:])

    return result


check(merge_sorted([1, 3, 5], [2, 4, 6]), [1, 2, 3, 4, 5, 6], "merge_sorted")
check(merge_sorted([1, 2], [3, 4, 5]), [1, 2, 3, 4, 5], "merge_sorted")
check(merge_sorted([], [1, 2]), [1, 2], "merge_sorted")


# ------------------------------------------------------------
# 6. closest_pair_sum(sorted_lst, target) → tuple[int, int]
#
# Пара чисел, сумма которых БЛИЖЕ ВСЕГО к target (не обязательно
# равна). Всегда есть ответ (список из 2+ элементов).
#
# closest_pair_sum(sorted_nums, 20) → (5, 15) — сумма ровно 20, ближе не бывает
# closest_pair_sum(sorted_nums, 2)  → (1, 3)  — сумма 4, ближе всех к 2
#
# Паттерн: как two_sum_sorted, но вместо остановки на точном
# совпадении — на каждом шаге сравнивай, не ближе ли текущая
# пара к target, чем лучшая найденная раньше (используй abs()).
# Условие сдвига указателей то же самое (сумма < target → left+=1,
# иначе right-=1). Если сумма == target — это уже идеальный
# ответ (diff=0), можно сразу возвращать.
# ------------------------------------------------------------
def closest_pair_sum(sorted_lst, target):
    left = 0
    right = len(sorted_lst) - 1

    best_pair = (sorted_lst[left], sorted_lst[right])
    min_diff = abs((sorted_lst[left] + sorted_lst[right]) - target)

    while left < right:
        current_sum = sorted_lst[left] + sorted_lst[right]
        current_diff = abs(current_sum - target)

        if current_diff < min_diff:
            min_diff = current_diff
            best_pair = (sorted_lst[left], sorted_lst[right])

        if current_sum == target:
            return (sorted_lst[left], sorted_lst[right])
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return best_pair


check(closest_pair_sum(sorted_nums, 20), (5, 15), "closest_pair_sum")
check(closest_pair_sum(sorted_nums, 2), (1, 3), "closest_pair_sum")
