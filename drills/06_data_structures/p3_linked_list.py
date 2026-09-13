# ============================================================
# МОДУЛЬ 6 — P3: LINKED LIST (связный список)
#
# Смотри класс Node/LinkedList в ds_reference.py — используй такой
# же Node (с полями value и next). Решения не даны — пишешь сам.
# Правило перед каждой задачей:
#   # Вход: ... Выход: ... Паттерн: ...
#
# check(actual, expected) печатает OK/FAIL и не роняет файл на
# первой ошибке — видно все результаты разом.
# ============================================================


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


# ------------------------------------------------------------
# 1. build_list(values) → Node | None
#
# Вспомогательная: построить связный список из обычного list и
# вернуть head. Нужна для проверки остальных функций (не задача
# на "подумать", просто утилита — но написать самому, чтобы руки
# привыкли к Node).
#
# to_list(build_list([1, 2, 3])) → [1, 2, 3]   # где to_list ниже
# ------------------------------------------------------------
def build_list(values):
    pass


# ------------------------------------------------------------
# 2. to_list(head) → list
#
# Обратная операция: пройти по связному списку и собрать обычный list.
# Используй для проверки результатов функций ниже.
# ------------------------------------------------------------
def to_list(head):
    pass


check(to_list(build_list([1, 2, 3])), [1, 2, 3], "build_list + to_list")


# ------------------------------------------------------------
# 3. reverse_list(head) → Node | None
#
# Развернуть связный список (изменить направление ссылок), вернуть
# новый head.
#
# to_list(reverse_list(build_list([1, 2, 3]))) → [3, 2, 1]
#
# Паттерн: три указателя (prev, current, next_node), на каждом шаге
# разворачиваем current.next на prev, потом двигаем все три вперёд.
# Без создания новых Node — только перелинковка.
# ------------------------------------------------------------
def reverse_list(head):
    pass


check(to_list(reverse_list(build_list([1, 2, 3]))), [3, 2, 1], "reverse_list")


# ------------------------------------------------------------
# 4. find_middle(head) → Node | None
#
# Найти средний узел списка (при чётной длине — второй из двух средних).
#
# find_middle(build_list([1, 2, 3, 4, 5])).value → 3
# find_middle(build_list([1, 2, 3, 4])).value    → 3
#
# Паттерн: slow/fast pointers — slow двигается на 1 шаг, fast на 2;
# когда fast дойдёт до конца, slow будет посередине (уже видел этот
# паттерн в Модуле 5 на массивах — здесь то же самое, но на ссылках).
# ------------------------------------------------------------
def find_middle(head):
    pass


middle1 = find_middle(build_list([1, 2, 3, 4, 5]))
check(middle1.value if middle1 else None, 3, "find_middle")
middle2 = find_middle(build_list([1, 2, 3, 4]))
check(middle2.value if middle2 else None, 3, "find_middle")


# ------------------------------------------------------------
# 5. has_cycle(head) → bool
#
# Определить, есть ли цикл в связном списке (последний узел
# ссылается не на None, а обратно на один из предыдущих).
#
# Паттерн: тот же slow/fast — если есть цикл, fast рано или поздно
# "догонит" slow внутри цикла. Если fast дошёл до None — цикла нет.
#
# Замечание: чтобы протестировать вручную, придётся построить список
# и вручную приделать node.next = какой-то более ранний узел —
# build_list() для этого не подходит, тестируй отдельным кодом.
# ------------------------------------------------------------
def has_cycle(head):
    pass


no_cycle = build_list([1, 2, 3])
check(has_cycle(no_cycle), False, "has_cycle (без цикла)")

a = Node(1)
b = Node(2)
c = Node(3)
a.next = b
b.next = c
c.next = a  # цикл вручную
check(has_cycle(a), True, "has_cycle (с циклом)")


# ------------------------------------------------------------
# 6. remove_duplicates_sorted(head) → Node | None
#
# Список уже отсортирован. Удалить узлы-дубликаты значений так,
# чтобы каждое значение осталось только один раз.
#
# to_list(remove_duplicates_sorted(build_list([1, 1, 2, 3, 3, 3])))
# → [1, 2, 3]
#
# Паттерн: один проход, сравниваем current.value с current.next.value;
# если равны — "перепрыгиваем" через дубликат
# (current.next = current.next.next), иначе двигаем current дальше.
# ------------------------------------------------------------
def remove_duplicates_sorted(head):
    pass


check(
    to_list(remove_duplicates_sorted(build_list([1, 1, 2, 3, 3, 3]))),
    [1, 2, 3],
    "remove_duplicates_sorted",
)
