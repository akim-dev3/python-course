# ============================================================
# NESTED DRILLS — вложенные структуры
# Открывается после закрытия 01_dict
# ============================================================
# Основной паттерн:
#
#   for order in orders:
#       for item in order.get("items", []):
#           # item — внутренний объект
#           # order.get("status") — фильтр по внешнему
#
# ============================================================

data = {
    "orders": [
        {
            "id": 1,
            "user": "Ivan",
            "status": "paid",
            "items": [
                {"product": "apple", "price": 10, "qty": 3},
                {"product": "banana", "price": 5, "qty": 5},
            ],
        },
        {
            "id": 2,
            "user": "Anna",
            "status": "pending",
            "items": [
                {"product": "apple", "price": 10, "qty": 2},
            ],
        },
        {
            "id": 3,
            "user": "Ivan",
            "status": "paid",
            "items": [
                {"product": "orange", "price": 20, "qty": 1},
                {"product": "banana", "price": 5, "qty": 10},
            ],
        },
        {"id": 4, "user": "Oleg", "status": "cancelled", "items": []},
    ]
}


# ------------------------------------------------------------
# Мини-проект: build_report(data) → dict
#
# total_orders     int    — всего заказов
# total_items_sold int    — сумма qty по всем items
# total_revenue    int    — price*qty только для paid
# top_product      str    — самый продаваемый товар по qty
# user_spent       dict   — {user: сумма} только paid
# big_orders       list   — id заказов где item с qty >= 5
# avg_order_value  float  — средний чек по paid
# top_user         str    — пользователь с max тратами
# ------------------------------------------------------------
#! 1
def total_orders(data):
    return len(data)


#! 2
def total_items_sold(data):
    return sum(
        [item.get("qty", 0) for order in data for item in order.get("items", [])]
    )


#! 3
def total_revenue(data):
    total = 0
    for order in data:
        if order.get("status") == "paid":
            for item in order.get("items", []):
                paid_revenue = item.get("price", 0) * item.get("qty", 0)
                total += paid_revenue
    return total


#! 4
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


#! 5
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


#! 6
def big_orders(data):
    return [
        order["id"]
        for order in data
        for item in order.get("items", [])
        if item.get("qty", 0) >= 5
    ]


#! 7
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


#! 8
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
