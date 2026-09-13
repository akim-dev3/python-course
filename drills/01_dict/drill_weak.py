# ============================================================
# ЗАКРЕПЛЕНИЕ СЛАБЫХ ТОЧЕК
# Перед каждой задачей пиши:
#   # Вход: ...
#   # Выход: ...
#   # Паттерн: ...
#   # dict нужен / не нужен — потому что ...
# ============================================================

products = [
    {"name": "apple", "category": "fruit", "price": 30, "in_stock": True},
    {"name": "banana", "category": "fruit", "price": 15, "in_stock": True},
    {"name": "milk", "category": "dairy", "price": 80, "in_stock": False},
    {"name": "cheese", "category": "dairy", "price": 250, "in_stock": True},
    {"name": "bread", "category": "bakery", "price": 45, "in_stock": True},
    {"name": "butter", "category": "dairy", "price": 120, "in_stock": False},
    {"name": "mango", "category": "fruit", "price": 200, "in_stock": True},
]


# ------------------------------------------------------------
# Задача A — FILTER + SORTED
# cheap_in_stock(products) → list[str]
# Имена товаров в наличии, отсортированные по цене возрастанию
# Ожидается: ["banana", "apple", "bread", "cheese", "mango"]
# ------------------------------------------------------------
def cheap_in_stock(products):
    # list[dict], list[str], filter + sorted
    in_stock = [p for p in products if p.get("in_stock")]
    return [p["name"] for p in sorted(in_stock, key=lambda x: x.get("price", 0))]


# ------------------------------------------------------------
# Задача B — GROUP BY + AVG
# avg_price_by_category(products) → dict
# Средняя цена по каждой категории (все товары, не только in_stock)
# Ожидается: {"fruit": 81.67, "dairy": 150.0, "bakery": 45.0}
# ------------------------------------------------------------
def avg_price_by_category(products):
    # list[dict], dict, group by + avg
    totals = {}
    counts = {}
    for p in products:
        category = p.get("category")
        totals[category] = totals.get(category, 0) + p.get("price", 0)
        counts[category] = counts.get(category, 0) + 1
    return {
        category: round(totals[category] / counts[category], 2) for category in totals
    }


# ------------------------------------------------------------
# Задача C — GROUP BY (реальная группировка)
# stock_value_by_category(products) → dict
# Суммарная стоимость товаров в наличии по категориям
# Ожидается: {"fruit": 245, "dairy": 250, "bakery": 45}
# ------------------------------------------------------------
def stock_value_by_category(products):
    # list[dict], dict, group by
    totals = {}
    for p in products:
        category = p.get("category")
        if p.get("in_stock"):
            totals[category] = totals.get(category, 0) + p.get("price", 0)
    return totals


# ------------------------------------------------------------
# Задача D — FILTER + SORTED (снова, без dict)
# top_expensive(products) → list[str]
# Имена ТОП-3 самых дорогих товаров в наличии
# Ожидается: ["mango", "cheese", "bread"]
# ------------------------------------------------------------
def top_expensive(products):
    in_stock_product = [p for p in products if p.get("in_stock")]
    return [
        p.get("name")
        for p in sorted(
            in_stock_product, key=lambda x: x.get("price", 0), reverse=True
        )[:3]
    ]


# ------------------------------------------------------------
# Задача E — КОМБО с защитой
# cheapest_in_category(products, category) → str | None
# Самый дешёвый товар в наличии в указанной категории.
# Если таких нет — вернуть None.
# Примеры:
#   cheapest_in_category(products, "fruit")  → "banana"
#   cheapest_in_category(products, "dairy")  → "cheese"
#   cheapest_in_category(products, "frozen") → None
# ------------------------------------------------------------
def cheapest_in_category(products, category):
    candidates = [
        p for p in products if p.get("category") == category and p.get("in_stock")
    ]
    if not candidates:
        return None

    return min(candidates, key=lambda x: x.get("price", 0))["name"]
