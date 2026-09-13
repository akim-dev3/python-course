# Данные
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
data = data.get("orders", [])


# ТЕСТ — сделай без копирования:
# Вернуть ТОП-3 пользователей по количеству заказов
def get_best_three_us(data):
    dict_users = {}
    for order in data:
        user = order.get("user")
        dict_users[user] = dict_users.get(user, 0) + 1

    return [
        k for k, v in sorted(dict_users.items(), key=lambda x: x[1], reverse=True)[:3]
    ]


print(get_best_three_us(data))
