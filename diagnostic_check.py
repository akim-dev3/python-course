# ============================================================
# ДИАГНОСТИКА — что осталось после паузы (Модули 1-4)
#
# Без новой теории, без докстрок — тот же формат, что и в
# обычных drills. Решения не даны, пишешь сам.
# Правило перед каждой задачей:
#   # Вход: ... Выход: ... Паттерн: ...
#
# Если где-то ступор дольше 5-10 минут — не гугли, просто отметь
# и присылай как есть. Разберём по твоей реальной ошибке
# (диагностика → объяснение → код), не заранее.
#
# Модуль 5 (two pointers / sliding window) тут не дублируется —
# для него drills/05_patterns/p2_sliding_window.py и
# p3_mastery_check.py, они и так не были дорешаны.
#
# check(actual, expected) печатает OK/FAIL и НЕ останавливает
# файл на первой ошибке — так видно все 8 результатов разом.
# ============================================================


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


# ============================================================
# МОДУЛЬ 1 — база (переменные, циклы, строки, функции)
# ============================================================

# ------------------------------------------------------------
# 1. count_vowels(s) → int
#
# Сколько гласных букв (a, e, i, o, u) в строке. Регистр не важен.
# count_vowels("Hello World") → 3
# count_vowels("sky") → 0
#
# Паттерн: цикл for по строке + счётчик
# ------------------------------------------------------------
def count_vowels(s):
    counter = 0
    vowels = 'aeiou'
    for i in s:
        if i.lower() in vowels:
            counter += 1
    return counter


check(count_vowels("Hello World"), 3, "count_vowels")
check(count_vowels("sky"), 0, "count_vowels")


# ------------------------------------------------------------
# 2. is_palindrome(s) → bool
#
# Читается ли строка одинаково в обе стороны. Регистр не важен.
# is_palindrome("Level") → True
# is_palindrome("hello") → False
#
# Паттерн: сравни строку с её разворотом (s[::-1])
# ------------------------------------------------------------
def is_palindrome(s):
    lower_s = s.lower()
    return lower_s == lower_s[::-1]


check(is_palindrome("Level"), True, "is_palindrome")
check(is_palindrome("hello"), False, "is_palindrome")


# ============================================================
# МОДУЛЬ 2 — коллекции (list, set)
# ============================================================

# ------------------------------------------------------------
# 3. dedupe_preserve_order(lst) → list
#
# Убрать повторы, оставив только первое появление каждого
# элемента. Порядок остальных элементов не менять.
# dedupe_preserve_order([1, 2, 2, 3, 1, 4]) → [1, 2, 3, 4]
# dedupe_preserve_order(["a", "b", "a"]) → ["a", "b"]
#
# Паттерн: seen: set — добавляй элемент в результат, только если
# его ещё не было в seen (как first_duplicate из Модуля 4)
# ------------------------------------------------------------
def dedupe_preserve_order(lst):
    seen = set()
    result = []
    for i in lst:
        if i not in seen:
            seen.add(i)
            result.append(i)
    return result


check(dedupe_preserve_order([1, 2, 2, 3, 1, 4]), [1, 2, 3, 4], "dedupe_preserve_order")
check(dedupe_preserve_order(["a", "b", "a"]), ["a", "b"], "dedupe_preserve_order")


# ------------------------------------------------------------
# 4. flatten_once(nested) → list
#
# Развернуть список списков в один плоский список (на один
# уровень вложенности).
# flatten_once([[1, 2], [3], [4, 5, 6]]) → [1, 2, 3, 4, 5, 6]
# flatten_once([[], [1], []]) → [1]
#
# Паттерн: цикл по внешнему списку, внутри — цикл по вложенному
# ------------------------------------------------------------
def flatten_once(nested):
    general_lst = []
    for lst in nested:
        for i in lst:
            general_lst.append(i)
    return general_lst


check(flatten_once([[1, 2], [3], [4, 5, 6]]), [1, 2, 3, 4, 5, 6], "flatten_once")
check(flatten_once([[], [1], []]), [1], "flatten_once")


# ============================================================
# МОДУЛЬ 3 — dict (COUNT / GROUP BY)
# ============================================================

# ------------------------------------------------------------
# 5. most_common_word(text) → str
#
# Самое частое слово в строке (слова разделены пробелами).
# При равенстве — подойдёт любое из самых частых.
# most_common_word("the cat sat on the mat the cat ran") → "the"
#
# Паттерн: text.split() → COUNT через dict
# (counts[word] = counts.get(word, 0) + 1) → max(dict, key=dict.get)
# ------------------------------------------------------------
def most_common_word(text):
    words = text.split()
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return max(counts, key=counts.get)


check(most_common_word("the cat sat on the mat the cat ran"), "the", "most_common_word")


# ------------------------------------------------------------
# 6. group_by_length(words) → dict
#
# Сгруппировать слова по длине: ключ — длина, значение — список
# слов этой длины.
# group_by_length(["a", "bb", "cc", "ddd", "e"])
# → {1: ["a", "e"], 2: ["bb", "cc"], 3: ["ddd"]}
#
# Паттерн: GROUP BY — d.setdefault(key, []).append(word)
# ------------------------------------------------------------
def group_by_length(words):
    pass


check(
    group_by_length(["a", "bb", "cc", "ddd", "e"]),
    {1: ["a", "e"], 2: ["bb", "cc"], 3: ["ddd"]},
    "group_by_length",
)


# ============================================================
# МОДУЛЬ 4 — алгоритмическое мышление (рекурсия, бинарный поиск)
# ============================================================

# ------------------------------------------------------------
# 7. factorial_recursive(n) → int
#
# Факториал ЧЕРЕЗ РЕКУРСИЮ (функция вызывает сама себя, не цикл).
# factorial_recursive(5) → 120   (5*4*3*2*1)
# factorial_recursive(0) → 1
#
# Паттерн: база рекурсии (n == 0 → return 1) + шаг
# (return n * factorial_recursive(n - 1))
# ------------------------------------------------------------
def factorial_recursive(n):
    pass


check(factorial_recursive(5), 120, "factorial_recursive")
check(factorial_recursive(0), 1, "factorial_recursive")


# ------------------------------------------------------------
# 8. binary_search(sorted_lst, target) → int
#
# Индекс target в ОТСОРТИРОВАННОМ списке, или -1 если элемента
# нет. Обязательно бинарный поиск (O(log n)) — в этом весь смысл
# задачи, обычный перебор не считается.
# binary_search([1, 3, 5, 7, 9, 11], 7) → 3
# binary_search([1, 3, 5, 7, 9, 11], 4) → -1
#
# Паттерн: left=0, right=len(lst)-1, пока left<=right — считай
# mid, сравнивай sorted_lst[mid] с target, сужай границы
# ------------------------------------------------------------
def binary_search(sorted_lst, target):
    pass


check(binary_search([1, 3, 5, 7, 9, 11], 7), 3, "binary_search")
check(binary_search([1, 3, 5, 7, 9, 11], 4), -1, "binary_search")
