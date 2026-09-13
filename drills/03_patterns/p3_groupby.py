# ============================================================
# ПАТТЕРН: GROUP BY
# Ключевое правило: один ключ встречается НЕСКОЛЬКО РАЗ → нужен dict
# Правило перед задачей:
#   # Вход: ... Выход: ... Паттерн: ...
# ============================================================

sales = [
    {
        "id": 1,
        "region": "north",
        "category": "food",
        "amount": 1200,
        "manager": "Alice",
    },
    {"id": 2, "region": "south", "category": "tech", "amount": 8500, "manager": "Bob"},
    {
        "id": 3,
        "region": "north",
        "category": "tech",
        "amount": 3200,
        "manager": "Alice",
    },
    {"id": 4, "region": "west", "category": "food", "amount": 700, "manager": "Carol"},
    {"id": 5, "region": "south", "category": "food", "amount": 950, "manager": "Bob"},
    {
        "id": 6,
        "region": "north",
        "category": "clothes",
        "amount": 2100,
        "manager": "Alice",
    },
    {"id": 7, "region": "west", "category": "tech", "amount": 5600, "manager": "Carol"},
    {
        "id": 8,
        "region": "south",
        "category": "clothes",
        "amount": 1800,
        "manager": "Bob",
    },
    {"id": 9, "region": "west", "category": "food", "amount": 430, "manager": "Carol"},
    {"id": 10, "region": "north", "category": "food", "amount": 880, "manager": "Dave"},
]


# ------------------------------------------------------------
# 1. count_by_region(sales) → dict
# Количество сделок по регионам
# Ожидается: {"north": 4, "south": 3, "west": 3}
# ------------------------------------------------------------
def count_by_region(sales):
    regions_count = {}
    for s in sales:
        region = s.get("region")
        regions_count[region] = regions_count.get(region, 0) + 1
    return regions_count


print(count_by_region(sales))


# ------------------------------------------------------------
# 2. revenue_by_category(sales) → dict
# Сумма amount по категориям
# Ожидается: {"food": 4160, "tech": 17300, "clothes": 3900}
# ------------------------------------------------------------
def revenue_by_category(sales):
    categories = {}
    for s in sales:
        category = s.get("category")
        amount = s.get("amount", 0)
        categories[category] = categories.get(category, 0) + amount
    return categories


print(revenue_by_category(sales))


# ------------------------------------------------------------
# 3. revenue_by_region(sales) → dict
# Сумма amount по регионам
# Ожидается: {"north": 7380, "south": 11250, "west": 6730}
# ------------------------------------------------------------
def revenue_by_region(sales):
    amount_regions = {}
    for s in sales:
        region = s.get("region")
        amount = s.get("amount", 0)
        amount_regions[region] = amount_regions.get(region, 0) + amount
    return amount_regions


print(revenue_by_region(sales))


# ------------------------------------------------------------
# 4. count_by_manager(sales) → dict
# Количество сделок на каждого менеджера
# Ожидается: {"Alice": 3, "Bob": 3, "Carol": 3, "Dave": 1}
# ------------------------------------------------------------
def count_by_manager(sales):
    managers_count = {}
    for s in sales:
        manager = s.get("manager")
        managers_count[manager] = managers_count.get(manager, 0) + 1
    return managers_count


print(count_by_manager(sales))


# ------------------------------------------------------------
# 5. revenue_by_manager(sales) → dict
# Сумма amount по менеджерам
# Ожидается: {"Alice": 6500, "Bob": 11250, "Carol": 6730, "Dave": 880}
# ------------------------------------------------------------
def revenue_by_manager(sales):
    amount_managers = {}
    for s in sales:
        manager = s.get("manager")
        amount = s.get("amount", 0)
        amount_managers[manager] = amount_managers.get(manager, 0) + amount
    return amount_managers


print(revenue_by_manager(sales))


# ------------------------------------------------------------
# 6. big_deals_by_region(sales) → dict
# Количество сделок с amount > 1000 по регионам
# Ожидается: {"north": 3, "south": 2, "west": 1}
# ------------------------------------------------------------
def big_deals_by_region(sales):
    big_deals = {}
    for s in sales:
        region = s.get("region")
        amount = s.get("amount", 0)
        if amount > 1000:
            big_deals[region] = big_deals.get(region, 0) + 1
    return big_deals


print(big_deals_by_region(sales))


# ------------------------------------------------------------
# 7. food_revenue_by_region(sales) → dict
# Сумма amount только для category == "food" по регионам
# Ожидается: {"north": 2080, "south": 950, "west": 1130}
# ------------------------------------------------------------
def food_revenue_by_region(sales):
    food_amount = {}
    for s in sales:
        region = s.get("region")
        amount = s.get("amount", 0)
        category = s.get("category")
        if category == "food":
            food_amount[region] = food_amount.get(region, 0) + amount
    return food_amount


print(food_revenue_by_region(sales))
