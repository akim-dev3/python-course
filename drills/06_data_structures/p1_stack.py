# ============================================================
# МОДУЛЬ 6 — P1: STACK (стек)
#
# Смотри ds_reference.py перед началом. Решения не даны — пишешь сам.
# Правило перед каждой задачей:
#   # Вход: ... Выход: ... Паттерн: ...
#
# check(actual, expected) печатает OK/FAIL и не роняет файл на
# первой ошибке — видно все результаты разом.
# ============================================================


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


# ------------------------------------------------------------
# 1. is_balanced(s) → bool
#
# Дана строка из скобок трёх видов: (), [], {}.
# Вернуть True, если все скобки закрыты правильно и в правильном порядке.
#
# is_balanced("([{}])") → True
# is_balanced("([)]")   → False
# is_balanced("(")      → False
#
# Паттерн: стек — при открывающей push, при закрывающей pop и
# сравни с ожидаемой парой (см. pairs в ds_reference.py)
# ------------------------------------------------------------
def is_balanced(s):
    pass


check(is_balanced("([{}])"), True, "is_balanced")
check(is_balanced("([)]"), False, "is_balanced")
check(is_balanced("("), False, "is_balanced")


# ------------------------------------------------------------
# 2. min_remove_to_make_valid(s) → str
#
# Дана строка, содержащая буквы и круглые скобки '(' ')'.
# Удалить минимум скобок так, чтобы оставшаяся строка стала валидной
# (каждая открывающая закрыта, каждая закрывающая имеет пару).
# Буквы не трогать.
#
# min_remove_to_make_valid("a)b(c)d") → "ab(c)d"
# min_remove_to_make_valid("))((")    → ""
#
# Паттерн: стек с ИНДЕКСАМИ открывающих скобок. Лишнюю закрывающую
# (стек пуст) сразу помечай на удаление. В конце всё, что осталось
# в стеке — тоже лишние открывающие, тоже на удаление.
# ------------------------------------------------------------
def min_remove_to_make_valid(s):
    pass


check(min_remove_to_make_valid("a)b(c)d"), "ab(c)d", "min_remove_to_make_valid")
check(min_remove_to_make_valid("))(("), "", "min_remove_to_make_valid")


# ------------------------------------------------------------
# 3. evaluate_postfix(tokens) → int
#
# Вычислить выражение в постфиксной (обратной польской) записи.
# tokens — список чисел и операторов (+, -, *, /), деление — целочисленное.
#
# evaluate_postfix(["2", "1", "+", "3", "*"]) → 9   # (2+1)*3
# evaluate_postfix(["4", "13", "5", "/", "+"]) → 6  # 4 + (13//5)
#
# Паттерн: стек с числами. На операторе — pop два числа (второй pop —
# левый операнд), применить операцию, push результат обратно.
# ------------------------------------------------------------
def evaluate_postfix(tokens):
    pass


check(evaluate_postfix(["2", "1", "+", "3", "*"]), 9, "evaluate_postfix")
check(evaluate_postfix(["4", "13", "5", "/", "+"]), 6, "evaluate_postfix")


# ------------------------------------------------------------
# 4. MinStack — стек, у которого get_min() всегда возвращает
# минимум за O(1)
#
# st = MinStack()
# st.push(3); st.push(1); st.push(2)
# st.get_min() → 1
# st.pop()               # снял 2
# st.get_min() → 1
# st.pop()               # снял 1
# st.get_min() → 3
#
# Паттерн: держать ВТОРОЙ стек с текущим минимумом на каждый момент,
# а не искать min() по всему стеку каждый раз (это было бы O(n)).
# ------------------------------------------------------------
class MinStack:
    def __init__(self):
        pass

    def push(self, value):
        pass

    def pop(self):
        pass

    def get_min(self):
        pass


st = MinStack()
st.push(3)
st.push(1)
st.push(2)
check(st.get_min(), 1, "MinStack.get_min")
st.pop()
check(st.get_min(), 1, "MinStack.get_min")
st.pop()
check(st.get_min(), 3, "MinStack.get_min")


# ------------------------------------------------------------
# 5. daily_temperatures(temps) → list[int]
#
# Для каждого дня — через сколько дней температура станет выше.
# Если такого дня нет — 0.
#
# daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])
# → [1, 1, 4, 2, 1, 1, 0, 0]
#
# Паттерн: monotonic stack — храним ИНДЕКСЫ дней, для которых ещё
# не нашли "теплее". Проходя новый день, снимаем со стека все дни,
# которые холоднее текущего.
# ------------------------------------------------------------
def daily_temperatures(temps):
    pass


check(
    daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]),
    [1, 1, 4, 2, 1, 1, 0, 0],
    "daily_temperatures",
)


# ------------------------------------------------------------
# 6. simplify_path(path) → str
#
# Дан абсолютный путь в Unix-стиле (как из os.path, но строкой).
# Упростить: убрать лишние '/', обработать '.' (текущая папка)
# и '..' (подняться на уровень выше).
#
# simplify_path("/a/./b/../../c/") → "/c"
# simplify_path("/../")            → "/"
# simplify_path("/home//foo/")     → "/home/foo"
#
# Паттерн: стек папок. path.split("/") даёт части, пропускай "" и ".",
# на ".." — pop из стека (если есть что снимать), иначе push part.
# ------------------------------------------------------------
def simplify_path(path):
    pass


check(simplify_path("/a/./b/../../c/"), "/c", "simplify_path")
check(simplify_path("/../"), "/", "simplify_path")
check(simplify_path("/home//foo/"), "/home/foo", "simplify_path")
