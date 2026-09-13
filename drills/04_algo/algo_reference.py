# ============================================================
# МОДУЛЬ 4 — ТЕОРИЯ С ПРОГОНАМИ
#
# Этот файл ЗАПУСКАЕТСЯ — смотри вывод и читай комментарии.
# Порядок работы с модулем:
#   1. Запусти этот файл, прочитай вывод снизу вверх по разделам
#   2. p2_recursion_guided.py  — заполни пропуски
#   3. p1_complexity_guided.py — заполни пропуски
#   4. p3_search_guided.py     — заполни пропуски
#   5. p2_recursion.py / p1_complexity.py / p3_search.py — с нуля
# ============================================================


# ════════════════════════════════════════════════════════════
# РАЗДЕЛ 1: BIG O — зачем и что это такое
# ════════════════════════════════════════════════════════════

# Big O — это не точное число операций.
# Это ответ на вопрос: "как изменится время работы, если данных станет в 10 раз больше?"
#
#   O(1)    → останется тем же           dict["key"], lst[0], x in set
#   O(n)    → вырастет в 10 раз          один цикл
#   O(n²)   → вырастет в 100 раз         два вложенных цикла
#   O(log n)→ вырастет примерно на 3     бинарный поиск
#
# Пример: список из 1000 элементов vs список из 10 000 элементов
#   O(n)  : 1000 → 10 000 операций   (в 10 раз больше)
#   O(n²) : 1000² → 10 000² = 1 000 000 → 100 000 000 операций (в 100 раз!)

print("=" * 50)
print("РАЗДЕЛ 1: Big O — сравнение на числах")
print("=" * 50)

import time

data_small = list(range(5000))
data_large = list(range(10000))  # вдвое больше


# O(n²) — медленно
def has_dup_slow(lst):
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] == lst[j]:
                return True
    return False


# O(n) — быстро
def has_dup_fast(lst):
    seen = set()
    for x in lst:
        if x in seen:
            return True
        seen.add(x)
    return False


t = time.time()
has_dup_slow(data_small)
slow_small = time.time() - t
t = time.time()
has_dup_slow(data_large)
slow_large = time.time() - t
t = time.time()
has_dup_fast(data_large)
fast_large = time.time() - t

print(f"O(n²) на 5000:  {slow_small:.4f} сек")
print(
    f"O(n²) на 10000: {slow_large:.4f} сек  ← в ~4 раза дольше (данных вдвое больше → 2² = 4)"
)
print(f"O(n)  на 10000: {fast_large:.6f} сек  ← почти мгновенно")
print()

# Правила чтения Big O в коде:
print("Правила чтения:")
print("  один цикл по n          → O(n)")
print("  цикл ВНУТРИ цикла       → O(n²)")
print("  два цикла ПОДРЯД        → O(n) (не O(n²)!)")
print("  dict[key], lst[i]       → O(1)")
print("  'x' in list             → O(n)  ← медленно")
print("  'x' in set              → O(1)  ← мгновенно")
print()


# ════════════════════════════════════════════════════════════
# РАЗДЕЛ 2: РЕКУРСИЯ — как это работает изнутри
# ════════════════════════════════════════════════════════════

# Рекурсия — функция вызывает сама себя.
# Два обязательных элемента:
#   БАЗА  — условие остановки. return без рекурсивного вызова.
#   ШАГ   — вызов с меньшими данными. Без этого не дойдём до базы.
#
# Без базы → RecursionError (Python обрывает на ~1000 уровне).

print("=" * 50)
print("РАЗДЕЛ 2: Рекурсия — прогон с выводом")
print("=" * 50)


# Пример 1: обратный отсчёт — видим порядок вызовов
def countdown_debug(n, depth=0):
    indent = "  " * depth  # отступ показывает уровень вложенности
    print(f"{indent}countdown({n}) вызвана")
    if n < 0:  # БАЗА
        print(f"{indent}→ база: return []")
        return []
    result = [n] + countdown_debug(n - 1, depth + 1)
    print(f"{indent}countdown({n}) вернула {result}")
    return result


print("countdown(3) с отладкой:")
print(countdown_debug(3))
print()


# Пример 2: factorial — видим как раскручивается
def factorial_debug(n, depth=0):
    indent = "  " * depth
    print(f"{indent}factorial({n})")
    if n <= 1:
        print(f"{indent}→ база: return 1")
        return 1
    result = n * factorial_debug(n - 1, depth + 1)
    print(f"{indent}→ {n} × ... = {result}")
    return result


print("factorial(4) с отладкой:")
factorial_debug(4)
print()


# Пример 3: sum_digits
def sum_digits(n):
    if n == 0:  # БАЗА
        return 0
    return n % 10 + sum_digits(n // 10)  # последняя цифра + сумма остальных


print("sum_digits:")
print(f"  sum_digits(123) = {sum_digits(123)}")  # 6
print(f"  sum_digits(9)   = {sum_digits(9)}")  # 9
print(f"  sum_digits(0)   = {sum_digits(0)}")  # 0
print()


# Пример 4: flatten — рекурсия нужна потому что вложенность неизвестна
def flatten(nested):
    result = []
    for item in nested:
        if isinstance(item, list):  # если элемент — список, разворачиваем рекурсивно
            result.extend(flatten(item))
        else:
            result.append(item)  # если число/строка — просто добавляем
    return result


print("flatten:")
print(f"  [1,[2,3],[4,[5,6]]] → {flatten([1, [2, 3], [4, [5, 6]]])}")
print(f"  [1,[2,[3,[4]]]]     → {flatten([1, [2, [3, [4]]]])}")
print()

# Когда рекурсия, когда цикл?
print("Когда что:")
print("  Плоский список / числа        → цикл (проще и без риска RecursionError)")
print("  Вложенные структуры (JSON, дерево, файловая система) → рекурсия")
print()


# ════════════════════════════════════════════════════════════
# РАЗДЕЛ 3: БИНАРНЫЙ ПОИСК — пошагово
# ════════════════════════════════════════════════════════════

# Работает ТОЛЬКО на отсортированном списке.
# Идея: каждый раз отбрасываем половину оставшегося диапазона.
# Скорость: O(log n) — на 1 000 000 элементов ~20 шагов.

print("=" * 50)
print("РАЗДЕЛ 3: Бинарный поиск — прогон с выводом")
print("=" * 50)

lst = [1, 3, 5, 7, 9, 12, 15, 18, 21, 24, 27, 30]


def binary_search_debug(lst, target):
    left, right = 0, len(lst) - 1
    step = 1
    print(f"  Ищем {target} в {lst}")

    while left <= right:
        mid = (left + right) // 2
        print(
            f"  Шаг {step}: left={left}, right={right}, mid={mid}, lst[mid]={lst[mid]}",
            end="  →  ",
        )

        if lst[mid] == target:
            print(f"НАШЛИ! Индекс {mid}")
            return mid
        elif lst[mid] < target:
            print(f"{lst[mid]} < {target}, ищем правее → left = {mid + 1}")
            left = mid + 1
        else:
            print(f"{lst[mid]} > {target}, ищем левее → right = {mid - 1}")
            right = mid - 1
        step += 1

    print(f"  Не нашли → return -1")
    return -1


print("Поиск 21:")
binary_search_debug(lst, 21)
print()
print("Поиск 6 (нет в списке):")
binary_search_debug(lst, 6)
print()

# Чистая версия — без отладки — именно её нужно знать наизусть:
print("Чистый алгоритм (выучи этот блок):")
print("""
def binary_search(lst, target):
    left, right = 0, len(lst) - 1
    while left <= right:
        mid = (left + right) // 2
        if lst[mid] == target:   return mid
        elif lst[mid] < target:  left = mid + 1    # target правее
        else:                    right = mid - 1   # target левее
    return -1
""")


def binary_search(lst, target):
    left, right = 0, len(lst) - 1
    while left <= right:
        mid = (left + right) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


print(f"binary_search(lst, 12)  = {binary_search(lst, 12)}")  # 5
print(f"binary_search(lst, 1)   = {binary_search(lst, 1)}")  # 0
print(f"binary_search(lst, 99)  = {binary_search(lst, 99)}")  # -1
print()


# ════════════════════════════════════════════════════════════
# ИТОГОВАЯ ШПАРГАЛКА
# ════════════════════════════════════════════════════════════

print("=" * 50)
print("ИТОГ — что запомнить")
print("=" * 50)
print("""
Big O:
  O(1)    → dict["k"], lst[i], x in set  — мгновенно
  O(n)    → один цикл, один проход
  O(n²)   → цикл ВНУТРИ цикла — избегать на больших данных
  O(log n)→ делим пополам (бинарный поиск)

Рекурсия:
  Всегда нужны БАЗА (условие остановки) + ШАГ (меньшие данные).
  Без базы → RecursionError.
  Применять для вложенных структур неизвестной глубины.

Бинарный поиск:
  Только на ОТСОРТИРОВАННОМ списке.
  left / right / mid — три переменные, одно условие while left <= right.
  1 000 000 элементов → ~20 шагов.
""")
