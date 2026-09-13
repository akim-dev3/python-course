# ============================================================
# МИНИ-ПРОЕКТ: Аналитика заказов
# Открывается после 02_nested
# ============================================================
# ТЗ — финальная версия build_report из drills/02_nested/tasks.py
# Здесь пишешь чистый итоговый код без черновиков
# ============================================================


data = {
    "orders": [
        {
            "id": 1,
            "user": "Ivan",
            "status": "paid",
            "items": [
                {"product": "apple", "price": 10, "qty": 4},
                {"product": "milk", "price": 60, "qty": 2},
            ],
        },
        {
            "id": 2,
            "user": "Anna",
            "status": "paid",
            "items": [
                {"product": "banana", "price": 15, "qty": 6},
                {"product": "apple", "price": 10, "qty": 2},
            ],
        },
        {
            "id": 3,
            "user": "Mila",
            "status": "pending",
            "items": [
                {"product": "milk", "price": 60, "qty": 3},
            ],
        },
        {
            "id": 4,
            "user": "Ivan",
            "status": "paid",
            "items": [
                {"product": "banana", "price": 15, "qty": 10},
                {"product": "cheese", "price": 200, "qty": 1},
            ],
        },
        {
            "id": 5,
            "user": "Oleg",
            "status": "cancelled",
            "items": [
                {"product": "apple", "price": 10, "qty": 1},
            ],
        },
        {
            "id": 6,
            "user": "Anna",
            "status": "paid",
            "items": [
                {"product": "cheese", "price": 200, "qty": 2},
                {"product": "milk", "price": 60, "qty": 1},
            ],
        },
        {"id": 7, "user": "Petr", "status": "pending", "items": []},
        {
            "id": 8,
            "user": "Mila",
            "status": "paid",
            "items": [
                {"product": "apple", "price": 10, "qty": 5},
                {"product": "banana", "price": 15, "qty": 3},
            ],
        },
        {
            "id": 9,
            "user": "Oleg",
            "status": "paid",
            "items": [
                {"product": "milk", "price": 60, "qty": 2},
            ],
        },
        {
            "id": 10,
            "user": "Petr",
            "status": "paid",
            "items": [
                {"product": "cheese", "price": 200, "qty": 1},
                {"product": "banana", "price": 15, "qty": 7},
            ],
        },
    ]
}

# ------------------------------------------------------------
# Ожидаемый вывод build_report:
#
# total_orders     → 10
# total_items_sold → 50
# total_revenue    → 1600
# top_product      → "banana"
# user_spent       → {"Ivan": 510, "Anna": 570, "Mila": 95, "Oleg": 120, "Petr": 305}
# big_orders       → [2, 4, 8, 10]
# avg_order_value  → 228.57
# top_user         → "Anna"
# ------------------------------------------------------------


def total_orders(data):
    return len(data)


def total_items_sold(data):
    return sum(
        [item.get("qty", 0) for order in data for item in order.get("items", [])]
    )


def total_revenue(data):
    total = 0
    for order in data:
        if order.get("status") == "paid":
            for item in order.get("items", []):
                paid_revenue = item.get("price", 0) * item.get("qty", 0)
                total += paid_revenue
    return total


def top_product(data):
    total_products = {}
    for order in data:
        for item in order.get("items", []):
            product = item.get("product")
            qty = item.get("qty", 0)

            total_products[product] = total_products.get(product, 0) + qty

    if not total_products:
        return None

    return max(total_products, key=total_products.get)


def user_spent(data):
    spent_users = {}
    for order in data:
        user = order.get("user")
        if not user:
            continue

        if order.get("status") == "paid":
            for item in order.get("items", []):

                paid_total = item.get("price", 0) * item.get("qty", 0)
                spent_users[user] = spent_users.get(user, 0) + paid_total

    if not spent_users:
        return None

    return spent_users


def big_orders(data):
    return [
        order["id"]
        for order in data
        if any(item.get("qty", 0) >= 5 for item in order.get("items", []))
    ]


def avg_order_value(data):
    paid = [o for o in data if o.get("status") == "paid"]
    if not paid:
        return 0
    total = sum(
        item.get("price", 0) * item.get("qty", 0)
        for o in paid
        for item in o.get("items", [])
    )
    return round(total / len(paid), 2)


def top_user(data):
    dict_user = {}
    for order in data:
        user = order.get("user")
        if not user:
            continue
        if order.get("status") == "paid":
            for item in order.get("items", []):

                paid_total = item.get("price", 0) * item.get("qty", 0)
                dict_user[user] = dict_user.get(user, 0) + paid_total

    if not dict_user:
        return None

    return max(dict_user, key=dict_user.get)


def build_report(data):
    data = data.get("orders", [])

    return {
        "total_orders": total_orders(data),
        "total_items_sold": total_items_sold(data),
        "total_revenue": total_revenue(data),
        "top_product": top_product(data),
        "user_spent": user_spent(data),
        "big_orders": big_orders(data),
        "avg_order_value": avg_order_value(data),
        "top_user": top_user(data),
    }


print(build_report(data))
