# ============================================================
# МОДУЛЬ 5 — P1b: ЗАКРЕПЛЕНИЕ (два указателя с концов)
#
# Не повтор p1 — три новые задачи на тот же паттерн, чтобы
# рука привыкла узнавать его без подсказок. Уровень сложности
# как в p1_two_pointers.py, не как в p3 (там сложнее).
#
# Смотри заметку в Obsidian ("Python — Модуль 5 Two Pointers
# и Sliding Window (на пальцах)"), если завис — без интернета.
#
# Правило перед задачей:
#   # Вход: ... Выход: ... Паттерн: ... Сложность: ...
# ============================================================


# ------------------------------------------------------------
# 1. count_pairs_with_sum(sorted_lst, target) → int
#
# Сколько РАЗНЫХ пар (по позиции) дают в сумме target.
# Список отсортирован и содержит ТОЛЬКО РАЗНЫЕ числа (без
# повторов) — это важно, без этого условия задача сложнее.
#
# count_pairs_with_sum([1, 2, 3, 4, 5, 6], 7) → 3
#   (1,6), (2,5), (3,4)
# count_pairs_with_sum([1, 2, 3, 4, 5], 6)    → 2
#   (1,5), (2,4)
# count_pairs_with_sum([1, 2, 3], 10)         → 0
#
# Паттерн: как two_sum_sorted, но при точном совпадении —
# НЕ возвращай сразу. Посчитай пару и подумай, что сделать
# с обоими указателями, чтобы не зациклиться и не пропустить
# следующую пару.
# Сложность: O(n)
# ------------------------------------------------------------
def count_pairs_with_sum(sorted_lst, target):
    counter = 0
    left, right = 0, len(sorted_lst) - 1

    while left < right:
        sum_lst = sorted_lst[left] + sorted_lst[right]
        if sum_lst == target:
            counter += 1
        if sum_lst < target:
            left += 1
        else:
            right -= 1
    return counter


print(count_pairs_with_sum([1, 2, 3, 4, 5, 6], 7))  # 3
print(count_pairs_with_sum([1, 2, 3, 4, 5], 6))  # 2
print(count_pairs_with_sum([1, 2, 3], 10))  # 0


# ------------------------------------------------------------
# 2. intersection_sorted(lst1, lst2) → list
#
# Общие элементы двух ОТСОРТИРОВАННЫХ списков (без повторов
# в ответе). Оба списка могут быть разной длины.
#
# intersection_sorted([1,3,4,6,8,10], [2,3,4,7,8]) → [3, 4, 8]
# intersection_sorted([1,2,3], [4,5,6])             → []
#
# ЛОВУШКА: это НЕ two_sum_sorted. Тут два указателя идут не
# с концов ОДНОГО списка навстречу друг другу, а каждый по
# СВОЕМУ списку, независимо. i — указатель в lst1, j — в lst2.
#
# Паттерн: сравни lst1[i] и lst2[j].
#   меньше -> двигай i (в том списке, где значение меньше)
#   больше -> двигай j
#   равны  -> нашёл общий элемент, добавь и двигай ОБА
# Сложность: O(n + m)
# ------------------------------------------------------------
def intersection_sorted(lst1, lst2):
    i, j = 0, 0
    result = []

    while i < len(lst1) and j < len(lst2):
        if lst1[i] < lst2[j]:
            # result.append(lst1[i])
            i += 1
        elif lst1[i] > lst2[j]:
            # result.append(lst2[j])
            j += 1

        elif lst1[i] == lst2[j]:
            result.append(lst1[i])
            i += 1
            j += 1

    return result


print(intersection_sorted([1, 3, 4, 6, 8, 10], [2, 3, 4, 7, 8]))  # [3, 4, 8]
print(intersection_sorted([1, 2, 3], [4, 5, 6]))  # []


# ------------------------------------------------------------
# 3. count_pairs_sum_less_than(sorted_lst, target) → int
#
# Сколько пар (по позиции, left < right) дают сумму СТРОГО
# МЕНЬШЕ target. Список отсортирован.
#
# count_pairs_sum_less_than([1, 2, 3, 4, 5], 6) → 4
#   (1,2)=3, (1,3)=4, (1,4)=5, (2,3)=5 -- все < 6
# count_pairs_sum_less_than([1, 1, 1, 1], 2)    → 0
#   все суммы ровно 2, ни одна не меньше
#
# ЛОВУШКА: наивный способ — перебрать все пары, O(n²). Два
# указателя дают O(n), но не за счёт пропуска проверок по
# одной, а за счёт того, что ОДНА проверка сразу отвечает
# сразу за НЕСКОЛЬКО пар.
#
# Подумай: если lst[left] + lst[right] < target — то что
# можно сказать про lst[left] + lst[k] для ЛЮБОГО k между
# left+1 и right (список отсортирован, k <= right)? Сколько
# таких k?
# Сложность: O(n)
# ------------------------------------------------------------
def count_pairs_sum_less_than(sorted_lst, target):
    left, right = 0, len(sorted_lst) - 1
    count = 0
    
    while left < right:
        if sorted_lst[left] + sorted_lst[right] < target:
            count += (right - left)
            left += 1
        elif sorted_lst[left] + sorted_lst[right] >= target:
            right -= 1
        
    return count

print(count_pairs_sum_less_than([1, 2, 3, 4, 5], 6))  # 4
print(count_pairs_sum_less_than([1, 1, 1, 1], 2))  # 0
