# ============================================================
# МОДУЛЬ 4 — P2: РЕКУРСИЯ
#
# ТЕОРИЯ (прочитай перед задачами):
#   Рекурсия = функция вызывает сама себя.
#   БЕЗ базового случая → RecursionError.
#
#   ШАБЛОН:
#   def func(n):
#       if <базовый случай>:        ← СТОП
#           return <значение>
#       return func(<меньший n>)    ← шаг ближе к базе
#
#   ОТЛАДКА: добавь print(f"func({n}) вызвана") в начало,
#            чтобы увидеть порядок вызовов.
#
# Правило перед задачей:
#   # Вход: ... Выход: ... База: ... Рекурсивный шаг: ...
# ============================================================


# ------------------------------------------------------------
# 1. countdown(n) → list[int]
#
# Список чисел от n до 0 включительно.
# countdown(5) → [5, 4, 3, 2, 1, 0]
# countdown(0) → [0]
#
# База: n < 0 → []  (или n == 0 → [0])
# Шаг: [n] + countdown(n - 1)
# ------------------------------------------------------------


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


def countdown(n):
    if n < 0:
        return []
    return [n] + countdown(n - 1)


check(countdown(5), [5, 4, 3, 2, 1, 0], "countdown")
check(countdown(0), [0], "countdown")
check(countdown(3), [3, 2, 1, 0], "countdown")


# ------------------------------------------------------------
# 2. factorial(n) → int
#
# Произведение чисел от 1 до n.
# factorial(5) = 5 × 4 × 3 × 2 × 1 = 120
# factorial(0) = 1  (по определению)
# factorial(1) = 1
#
# База: n <= 1 → 1
# Шаг: n * factorial(n - 1)
# ------------------------------------------------------------
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)


check(factorial(5), 120, "factorial")
check(factorial(0), 1, "factorial")
check(factorial(10), 3628800, "factorial")


# ------------------------------------------------------------
# 3. power(base, exp) → int | float
#
# Возведение в степень БЕЗ оператора **.
# power(2, 10) = 1024
# power(3, 0)  = 1    (любое число в степени 0 = 1)
# power(5, 1)  = 5
# power(2, 8)  = 256
#
# База: exp == 0 → 1
# Шаг: base * power(base, exp - 1)
# ------------------------------------------------------------
def power(base, exp):
    if exp == 0:
        return 1
    return base * power(base, exp - 1)


check(power(2, 10), 1024, "power")
check(power(3, 0), 1, "power")
check(power(5, 3), 125, "power")
check(power(2, 8), 256, "power")


# ------------------------------------------------------------
# 4. sum_digits(n) → int
#
# Сумма цифр неотрицательного числа.
# sum_digits(123)  → 6   (1 + 2 + 3)
# sum_digits(9999) → 36
# sum_digits(0)    → 0
#
# Подсказка:
#   последняя цифра = n % 10
#   остаток числа   = n // 10
# База: n == 0 → 0
# Шаг: (n % 10) + sum_digits(n // 10)
# ------------------------------------------------------------
def sum_digits(n):
    if n == 0:
        return 0
    last = n % 10
    rest = n // 10
    return last + sum_digits(rest)


check(sum_digits(123), 6, "sum_digits")
check(sum_digits(9999), 36, "sum_digits")
check(sum_digits(0), 0, "sum_digits")
check(sum_digits(1), 1, "sum_digits")


# ------------------------------------------------------------
# 5. reverse_string(s) → str
#
# Переворот строки рекурсивно (без s[::-1] и reversed()).
# reverse_string("hello")  → "olleh"
# reverse_string("python") → "nohtyp"
# reverse_string("a")      → "a"
# reverse_string("")        → ""
#
# Подсказка:
#   первый символ = s[0]
#   остаток       = s[1:]
# База: len(s) <= 1 → s
# Шаг: reverse_string(s[1:]) + s[0]
# ------------------------------------------------------------
def reverse_string(s):
    if len(s) <= 1:
        return s
    return reverse_string(s[1:]) + s[0]


check(reverse_string("hello"), "olleh", "reverse_string")
check(reverse_string("python"), "nohtyp", "reverse_string")
check(reverse_string("a"), "a", "reverse_string")
check(reverse_string(""), "", "reverse_string")


# ------------------------------------------------------------
# 6. flatten(nested) → list
#
# Разворачивает список произвольной глубины в плоский.
# flatten([1, [2, 3], [4, [5, 6]]]) → [1, 2, 3, 4, 5, 6]
# flatten([1, [2, [3, [4, [5]]]]]) → [1, 2, 3, 4, 5]
# flatten([1, 2, 3]) → [1, 2, 3]
# flatten([]) → []
#
# Подсказка: isinstance(item, list) — проверяет, является ли
#            item списком (True/False)
# Паттерн:
#   result = []
#   for item in nested:
#       if isinstance(item, list): result.extend(flatten(item))
#       else: result.append(item)
# ------------------------------------------------------------
def flatten(nested):
    result = []

    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


check(flatten([1, [2, 3], [4, [5, 6]]]), [1, 2, 3, 4, 5, 6], "flatten")
check(flatten([1, [2, [3, [4, [5]]]]]), [1, 2, 3, 4, 5], "flatten")
check(flatten([1, 2, 3]), [1, 2, 3], "flatten")
check(flatten([]), [], "flatten")


# ------------------------------------------------------------
# 7. count_nested(data, key, value) → int
#
# Считает, сколько объектов на ЛЮБОМ уровне вложенности
# содержат key == value.
#
# Каждый объект может иметь поле "children" — список таких же
# объектов. Рекурсия идёт по children.
#
# count_nested(employees, "dept", "IT") → 3
# count_nested(employees, "dept", "HR") → 2
#
# Паттерн:
#   для каждого emp в data:
#     если emp[key] == value: count += 1
#     count += count_nested(emp.get("children", []), key, value)
# ------------------------------------------------------------
employees = [
    {
        "name": "Alice",
        "dept": "IT",
        "children": [
            {"name": "Bob", "dept": "IT", "children": []},
            {
                "name": "Carol",
                "dept": "HR",
                "children": [{"name": "Dan", "dept": "IT", "children": []}],
            },
        ],
    },
    {
        "name": "Eve",
        "dept": "HR",
        "children": [{"name": "Frank", "dept": "Finance", "children": []}],
    },
]


def count_nested(data, key, value):
    count = 0
    for emp in data:
        if emp.get(key) == value:
            count += 1
        children = emp.get("children", [])
        count += count_nested(children, key, value)
    return count


check(count_nested(employees, "dept", "IT"), 3, "count_nested")
check(count_nested(employees, "dept", "HR"), 2, "count_nested")
check(count_nested(employees, "dept", "Finance"), 1, "count_nested")
