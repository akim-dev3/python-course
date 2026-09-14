# ============================================================
# DICT PATTERNS — шпаргалка (читать перед задачей, не во время)
# ============================================================

data = [
    {"name": "Ivan", "city": "Moscow", "score": 85, "active": True},
    {"name": "Anna", "city": "Moscow", "score": 92, "active": True},
    {"name": "Oleg", "city": "Kazan", "score": 60, "active": False},
    {"name": "Mila", "city": "Kazan", "score": 78, "active": True},
    {"name": "Petr", "city": "Moscow", "score": 55, "active": False},
]

# ----------------------------------------------------------
# 1. COUNT — сколько элементов по условию
# ----------------------------------------------------------
# Вход: list[dict]   Выход: int
count = sum(1 for x in data if x.get("active"))
# → 3

# ----------------------------------------------------------
# 2. SUM — сумма поля по условию
# ----------------------------------------------------------
# Вход: list[dict]   Выход: int | float
total = sum(x.get("score", 0) for x in data if x.get("active"))
# → 255

# ----------------------------------------------------------
# 3. FILTER — список объектов по условию
# ----------------------------------------------------------
# Вход: list[dict]   Выход: list[dict]
result = [x for x in data if x.get("active") and x.get("score", 0) > 80]
# → [{"name": "Ivan"...}, {"name": "Anna"...}]

# ----------------------------------------------------------
# 4. GROUP BY — {ключ: агрегат}
# ----------------------------------------------------------
# Вход: list[dict]   Выход: dict
by_city = {}
for x in data:
    key = x.get("city")
    by_city[key] = by_city.get(key, 0) + 1
# → {"Moscow": 3, "Kazan": 2}

# GROUP BY с суммой:
score_by_city = {}
for x in data:
    key = x.get("city")
    score_by_city[key] = score_by_city.get(key, 0) + x.get("score", 0)

# ----------------------------------------------------------
# 5. TOP N — отсортированный топ из dict
# ----------------------------------------------------------
# Вход: dict         Выход: list[tuple] или list[str]
top2 = sorted(by_city.items(), key=lambda x: x[1], reverse=True)[:2]
# → [("Moscow", 3), ("Kazan", 2)]

top2_keys = [k for k, v in top2]
# → ["Moscow", "Kazan"]

# ----------------------------------------------------------
# 6. MAX В DICT — ключ с максимальным значением
# ----------------------------------------------------------
# Вход: dict         Выход: key (str | int | ...)
best_city = max(by_city, key=by_city.get)
# → "Moscow"


# ----------------------------------------------------------
# ЗАЩИТА ОТ ПУСТЫХ ДАННЫХ (всегда)
# ----------------------------------------------------------
def safe_avg(data):
    if not data:
        return 0
    return sum(x.get("score", 0) for x in data) / len(data)


# ----------------------------------------------------------
# СЛОВАРЬ → СПИСОК СЛОВАРЕЙ
# ----------------------------------------------------------
# Вход: dict         Выход: list[dict]
as_list = [{"city": k, "count": v} for k, v in by_city.items()]
# → [{"city": "Moscow", "count": 3}, ...]


# ----------------------------------------------------------
# 8. AVG — среднее по группам (всегда два dict)
# ----------------------------------------------------------
# Вход: list[dict]   Выход: dict
totals = {}
counts = {}
for x in data:
    key = x.get("city")
    totals[key] = totals.get(key, 0) + x.get("score", 0)
    counts[key] = counts.get(key, 0) + 1
avg_by_city = {k: round(totals[k] / counts[k], 2) for k in totals}
# → {"Moscow": 77.33, "Kazan": 69.0}


# ----------------------------------------------------------
# 9. NESTED — вложенные структуры
# ----------------------------------------------------------
# Вход: list[dict] где у каждого есть список items
# Выход: зависит от задачи

nested_data = [
    {"user": "Ivan", "status": "paid", "items": [
        {"product": "apple", "price": 10, "qty": 3},
    ]},
]

# Паттерн двойного цикла:
for order in nested_data:
    for item in order.get("items", []):
        # item — внутренний объект
        # order.get("status") — фильтр по внешнему
        pass

# SUM по вложенным (только paid):
total = 0
for order in nested_data:
    if order.get("status") == "paid":
        for item in order.get("items", []):
            total += item.get("price", 0) * item.get("qty", 0)

# GROUP BY по вложенным:
product_qty = {}
for order in nested_data:
    for item in order.get("items", []):
        p = item.get("product")
        product_qty[p] = product_qty.get(p, 0) + item.get("qty", 0)
