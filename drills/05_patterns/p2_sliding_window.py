# ============================================================
# МОДУЛЬ 5 — P2: SLIDING WINDOW (скользящее окно)
#
# ТЕОРИЯ (прочитай перед задачами):
#   "Окно" — это непрерывный кусок списка/строки между двумя
#   указателями left и right. Вместо пересчёта суммы/условия
#   заново для каждого окна (O(n·k) или O(n²)) — двигаем окно
#   на один шаг и обновляем результат за O(1). Итого O(n).
#
#   ШАБЛОН — окно ФИКСИРОВАННОГО размера k:
#   window_sum = sum(lst[:k])
#   best = window_sum
#   for right in range(k, len(lst)):
#       window_sum += lst[right] - lst[right - k]   # +новый -старый
#       best = max(best, window_sum)
#
#   ШАБЛОН — окно ПЕРЕМЕННОГО размера (растёт/сжимается):
#   left = 0
#   window_state = ...   # сумма, set символов, счётчик и т.п.
#   for right in range(len(lst)):
#       # добавить lst[right] в window_state
#       while <окно нарушает условие>:
#           # убрать lst[left] из window_state
#           left += 1
#       # тут окно [left, right] валидно — обнови ответ
#
# Правило перед задачей:
#   # Вход: ... Выход: ... Окно: фиксированное | переменное ... Сложность: ...
#
# check(actual, expected) печатает OK/FAIL и не роняет файл на
# первой ошибке — видно все результаты разом.
# ============================================================


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


nums = [2, 1, 5, 1, 3, 2, 7, 4, 1, 8]


# ------------------------------------------------------------
# 1. max_sum_subarray(lst, k) → int
#
# Максимальная сумма подряд идущих k элементов.
# max_sum_subarray(nums, 3) → 13   (окно 2+7+4 или 4+1+8, оба дают 13)
# max_sum_subarray([1, 2, 3], 5) → None   (k больше длины списка)
#
# Паттерн: окно фиксированного размера k — используй шаблон
# "+новый -старый" из шапки файла, не пересчитывай сумму заново
# на каждом шаге.
# Сложность: O(n), не O(n·k)
# ------------------------------------------------------------
def max_sum_subarray(lst, k):
    pass


check(max_sum_subarray(nums, 3), 13, "max_sum_subarray")
check(max_sum_subarray([1, 2, 3], 5), None, "max_sum_subarray")


# ------------------------------------------------------------
# 2. average_of_windows(lst, k) → list[float]
#
# Список средних значений для каждого окна размера k.
# average_of_windows([1, 2, 3, 4, 5], 2) → [1.5, 2.5, 3.5, 4.5]
# average_of_windows([1, 2, 3], 3) → [2.0]
#
# Паттерн: тот же "+новый -старый", но сохраняй среднее
# на каждом шаге в список результатов.
# ------------------------------------------------------------
def average_of_windows(lst, k):
    pass


check(average_of_windows([1, 2, 3, 4, 5], 2), [1.5, 2.5, 3.5, 4.5], "average_of_windows")
check(average_of_windows([1, 2, 3], 3), [2.0], "average_of_windows")


# ------------------------------------------------------------
# 3. longest_unique_substring(s) → str
#
# Самая длинная подстрока БЕЗ повторяющихся символов.
# longest_unique_substring("abcabcbb") → "abc"
# longest_unique_substring("bbbbb")    → "b"
# longest_unique_substring("pwwkew")   → "wke"
# longest_unique_substring("")         → ""
#
# Паттерн: окно ПЕРЕМЕННОГО размера + set с символами в окне.
# Расширяй right, добавляя символ в set. Если символ уже в
# set (значит повтор) — сжимай left, убирая символы из set,
# пока повтора не станет. На каждом шаге сравнивай длину окна
# с лучшей найденной.
# Сложность: O(n)
# ------------------------------------------------------------
def longest_unique_substring(s):
    pass


check(longest_unique_substring("abcabcbb"), "abc", "longest_unique_substring")
check(longest_unique_substring("bbbbb"), "b", "longest_unique_substring")
check(longest_unique_substring("pwwkew"), "wke", "longest_unique_substring")
check(longest_unique_substring(""), "", "longest_unique_substring")


# ------------------------------------------------------------
# 4. min_len_subarray_sum(lst, target) → int
#
# Длина САМОГО КОРОТКОГО непрерывного куска, сумма которого
# >= target. Если такого нет — 0.
#
# min_len_subarray_sum([2, 3, 1, 2, 4, 3], 7) → 2   (кусок [4, 3], сумма 7)
# min_len_subarray_sum([1, 1, 1, 1], 100) → 0   (сумма всего списка < 100)
# min_len_subarray_sum([4, 3, 5], 4) → 1   (сам 4 уже >= 4)
#
# Паттерн: окно переменного размера + текущая сумма окна.
# Расширяй right, прибавляя к сумме. Пока сумма окна >= target —
# сравнивай длину окна с минимумом и СЖИМАЙ left (окно должно
# оставаться минимальным, но валидным).
# Сложность: O(n)
# ------------------------------------------------------------
def min_len_subarray_sum(lst, target):
    pass


check(min_len_subarray_sum([2, 3, 1, 2, 4, 3], 7), 2, "min_len_subarray_sum")
check(min_len_subarray_sum([1, 1, 1, 1], 100), 0, "min_len_subarray_sum")
check(min_len_subarray_sum([4, 3, 5], 4), 1, "min_len_subarray_sum")


# ------------------------------------------------------------
# 5. contains_nearby_duplicate(lst, k) → bool
#
# Есть ли два одинаковых элемента на расстоянии <= k друг от друга
# (по индексам).
#
# contains_nearby_duplicate([1, 2, 3, 1], 3) → True   (индексы 0 и 3, разница 3)
# contains_nearby_duplicate([1, 2, 3, 1], 2) → False  (разница 3 > 2)
# contains_nearby_duplicate([1, 2, 3, 4], 2) → False
#
# Паттерн: окно ФИКСИРОВАННОГО размера k+1 через set — держи в
# set только последние k+1 элементов. Если новый элемент уже
# в set — нашёл. Если размер set превышает k+1 — убирай самый
# старый (тот, что вышел из окна).
# ------------------------------------------------------------
def contains_nearby_duplicate(lst, k):
    pass


check(contains_nearby_duplicate([1, 2, 3, 1], 3), True, "contains_nearby_duplicate")
check(contains_nearby_duplicate([1, 2, 3, 1], 2), False, "contains_nearby_duplicate")
check(contains_nearby_duplicate([1, 2, 3, 4], 2), False, "contains_nearby_duplicate")
