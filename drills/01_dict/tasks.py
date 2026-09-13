# ============================================================
# DICT DRILLS — тренировка паттернов до автоматизма
# ============================================================
# Перед каждой задачей:
#   1. Что на входе, что на выходе (тип)
#   2. Назови паттерн
#   3. Пиши код
# ============================================================

users = [
    {"name": "Ivan", "age": 25, "city": "Moscow", "active": True, "score": 85},
    {"name": "Anna", "age": 17, "city": "Moscow", "active": True, "score": 92},
    {"name": "Oleg", "age": 30, "city": "Kazan", "active": False, "score": 60},
    {"name": "Mila", "age": 15, "city": "Kazan", "active": True, "score": 78},
    {"name": "Petr", "age": 22, "city": "Moscow", "active": False, "score": 55},
]


# ------------------------------------------------------------
# Задача 1 — COUNT ✅
# count_active_adults(users) → int
# Количество активных пользователей старше 18
# ------------------------------------------------------------
def count_active_adults(users):
    return sum(1 for u in users if u.get("age") > 18 and u.get("active"))


# ------------------------------------------------------------
# Задача 2 — SUM ✅
# total_score(users) → int
# Сумма score только активных пользователей
# Ожидается: 255  (85 + 92 + 78)
# ------------------------------------------------------------
def total_score(users):
    # list[dict], int, sum
    return sum(u.get("score", 0) for u in users if u.get("active"))


# ------------------------------------------------------------
# Задача 3 — FILTER ✅
# get_high_scorers(users) → list[dict]
# Список активных пользователей со score > 80
# Ожидается: [{"name": "Ivan"...}, {"name": "Anna"...}]
# ------------------------------------------------------------
def get_high_scorers(users):
    # list[dict], list[dict], filter
    return [u for u in users if u.get("score", 0) > 80 and u.get("active")]


# ------------------------------------------------------------
# Задача 4 — GROUP BY ✅
# count_by_city(users) → dict
# Количество пользователей в каждом городе (все, не только active)
# Ожидается: {"Moscow": 3, "Kazan": 2}
# ------------------------------------------------------------
def count_by_city(users):
    # list[dict], dict, group by
    count_users = {}
    for u in users:
        city = u.get("city")
        count_users[city] = count_users.get(city, 0) + 1
    return count_users


# ------------------------------------------------------------
# Задача 5 — GROUP BY с суммой ✅
# score_by_city(users) → dict
# Сумма score по городам только для активных
# Ожидается: {"Moscow": 177, "Kazan": 78}
# ------------------------------------------------------------
def score_by_city(users):
    # list[dict], dict, group by
    count_score = {}
    for u in users:
        city = u.get("city")
        score = u.get("score", 0)
        if u.get("active"):
            count_score[city] = count_score.get(city, 0) + score
    return count_score


# ------------------------------------------------------------
# Задача 6 — TOP N ✅
# top_cities(users) → list[str]
# ТОП-2 города по количеству пользователей (все)
# Ожидается: ["Moscow", "Kazan"]
# ------------------------------------------------------------
def top_cities(users):
    # dict, list, top N
    dict_users = count_by_city(users)
    top_two = sorted(dict_users.items(), key=lambda x: x[1], reverse=True)[:2]
    top_two_keys = [k for k, v in top_two]
    return top_two_keys


# ------------------------------------------------------------
# Задача 7 — MAX В DICT ✅
# best_city(users) → str
# Город с максимальной суммой score (только active)
# Ожидается: "Moscow"
# ------------------------------------------------------------
def best_city(users):
    # dict, key(str), max в dict
    dict_score = score_by_city(users)
    return max(dict_score, key=dict_score.get)


# ------------------------------------------------------------
# Задача 8 — КОМБО (FILTER + SORTED) ✅
# top_active_users(users) → list[str]
# Имена активных пользователей, отсортированные по score убыванию
# Ожидается: ["Anna", "Ivan", "Mila"]
# ------------------------------------------------------------
def top_active_users(users):
    # dict, list, GROUP BY + FILTER + SORTED
    active = [u for u in users if u.get("active")]
    return [
        u["name"] for u in sorted(active, key=lambda x: x.get("score", 0), reverse=True)
    ]


# ============================================================
# РАУНД 2 — новые данные
# ============================================================

orders = [
    {"id": 1, "user": "Ivan", "category": "food", "amount": 1500, "paid": True},
    {"id": 2, "user": "Anna", "category": "electronics", "amount": 8000, "paid": True},
    {"id": 3, "user": "Ivan", "category": "electronics", "amount": 3000, "paid": False},
    {"id": 4, "user": "Mila", "category": "food", "amount": 500, "paid": True},
    {"id": 5, "user": "Anna", "category": "food", "amount": 700, "paid": True},
    {"id": 6, "user": "Oleg", "category": "electronics", "amount": 5000, "paid": False},
    {"id": 7, "user": "Mila", "category": "electronics", "amount": 2000, "paid": True},
]


# ------------------------------------------------------------
# Задача 9 — COUNT ✅
# count_paid(orders) → int
# Количество оплаченных заказов
# Ожидается: 5
# ------------------------------------------------------------
def count_paid(orders):
    return sum(1 for o in orders if o.get("paid"))


# ------------------------------------------------------------
# Задача 10 — SUM ✅
# total_revenue(orders) → int
# Сумма amount только по оплаченным заказам
# Ожидается: 12700
# ------------------------------------------------------------
def total_revenue(orders):
    return sum(o.get("amount", 0) for o in orders if o.get("paid"))


# ------------------------------------------------------------
# Задача 11 — FILTER ✅
# big_paid_orders(orders) → list[dict]
# Оплаченные заказы с amount > 1000
# Ожидается: [заказ Ivan 1500, Anna 8000, Mila 2000]
# ------------------------------------------------------------
def big_paid_orders(orders):
    return [o for o in orders if o.get("amount", 0) > 1000 and o.get("paid")]


# ------------------------------------------------------------
# Задача 12 — GROUP BY ✅
# revenue_by_category(orders) → dict
# Сумма amount по категориям — только оплаченные
# Ожидается: {"food": 2700, "electronics": 10000}
# ------------------------------------------------------------
def revenue_by_category(orders):
    category_dict = {}
    for o in orders:
        category = o.get("category")
        amount = o.get("amount", 0)
        if o.get("paid"):
            category_dict[category] = category_dict.get(category, 0) + amount
    return category_dict


# ------------------------------------------------------------
# Задача 13 — TOP N ✅
# top_categories(orders) → list[str]
# ТОП-1 категория по выручке (оплаченные)
# Ожидается: ["electronics"]
# ------------------------------------------------------------
def top_categories(orders):
    paid_categories = revenue_by_category(orders)
    sorted_categories = sorted(
        paid_categories.items(), key=lambda x: x[1], reverse=True
    )[:1]
    return [k for k, v in sorted_categories]


# ------------------------------------------------------------
# Задача 14 — GROUP BY + MAX ✅
# best_user(orders) → str
# Пользователь с наибольшей суммой оплаченных заказов
# Ожидается: "Anna"  (8000 + 700 = 8700)
# ------------------------------------------------------------
def best_user(orders):
    user_dict = {}
    for o in orders:
        user = o.get("user")
        amount = o.get("amount", 0)
        if o.get("paid"):
            user_dict[user] = user_dict.get(user, 0) + amount
    return max(user_dict, key=user_dict.get)


# ------------------------------------------------------------
# Задача 15 — КОМБО ✅
# user_order_counts(orders) → list[tuple]
# Список (user, кол-во_заказов) всех пользователей,
# отсортированный по убыванию количества. Все заказы (не только paid).
# Ожидается: [("Ivan", 2), ("Anna", 2), ("Mila", 2), ("Oleg", 1)]
# Примечание: при равенстве порядок между Ivan/Anna/Mila не важен
# ------------------------------------------------------------
def user_order_counts(orders):
    sorted_users = {}
    for o in orders:
        user = o.get("user")
        sorted_users[user] = sorted_users.get(user, 0) + 1
    return sorted(sorted_users.items(), key=lambda x: x[1], reverse=True)


# ============================================================
# РАУНД 3 — комбо, стресс-тест
# ============================================================

employees = [
    {"name": "Ivan", "dept": "dev", "salary": 120000, "senior": True},
    {"name": "Anna", "dept": "dev", "salary": 95000, "senior": False},
    {"name": "Oleg", "dept": "hr", "salary": 70000, "senior": False},
    {"name": "Mila", "dept": "dev", "salary": 140000, "senior": True},
    {"name": "Petr", "dept": "hr", "salary": 85000, "senior": True},
    {"name": "Dima", "dept": "dev", "salary": 60000, "senior": False},
    {"name": "Olga", "dept": "hr", "salary": 90000, "senior": True},
]


# ------------------------------------------------------------
# Задача 16 — FILTER + COUNT ✅
# dept_headcount(employees) → dict
# Количество сотрудников в каждом отделе — только senior
# Ожидается: {"dev": 2, "hr": 2}
# ------------------------------------------------------------
def dept_headcount(employees):
    count_dept = {}
    for e in employees:
        dept = e.get("dept")
        if e.get("senior"):
            count_dept[dept] = count_dept.get(dept, 0) + 1
    return count_dept


# ------------------------------------------------------------
# Задача 17 — GROUP BY + AVG ✅
# avg_salary_by_dept(employees) → dict
# Средняя зарплата по каждому отделу (все сотрудники)
# Ожидается: {"dev": 103750.0, "hr": 81666.67}  (округли до 2 знаков)
# ------------------------------------------------------------
def avg_salary_by_dept(employees):
    totals = {}
    counts = {}
    for e in employees:
        dept = e.get("dept")
        totals[dept] = totals.get(dept, 0) + e.get("salary", 0)
        counts[dept] = counts.get(dept, 0) + 1
    return {dept: round(totals[dept] / counts[dept], 2) for dept in totals}


# ------------------------------------------------------------
# Задача 18 — FILTER + SORTED → list[str] ✅
# top_earners(employees) → list[str]
# Имена senior-сотрудников, отсортированные по зарплате убыванию
# Ожидается: ["Mila", "Ivan", "Petr", "Olga"]
# ------------------------------------------------------------
def top_earners(employees):
    seniors = [e for e in employees if e.get("senior")]
    return [
        e["name"]
        for e in sorted(seniors, key=lambda x: x.get("salary", 0), reverse=True)
    ]


# ------------------------------------------------------------
# Задача 19 — GROUP BY + TOP N → list[str] ✅
# richest_depts(employees) → list[str]
# ТОП-1 отдел по суммарной зарплате (все сотрудники)
# Ожидается: ["dev"]
# ------------------------------------------------------------
def richest_depts(employees):
    dept_totals = {}
    for e in employees:
        dept = e.get("dept")
        salary = e.get("salary", 0)
        dept_totals[dept] = dept_totals.get(dept, 0) + salary
    return [max(dept_totals, key=dept_totals.get)]


# ------------------------------------------------------------
# Задача 20 — КОМБО с защитой ✅
# best_senior(employees, dept) → str | None
# Имя senior-сотрудника с максимальной зарплатой в указанном отделе.
# Если таких нет — вернуть None.
# Примеры:
#   best_senior(employees, "dev")  → "Mila"
#   best_senior(employees, "hr")   → "Petr"
#   best_senior(employees, "qa")   → None
# ------------------------------------------------------------
def best_senior(employees, dept):
    candidates = [e for e in employees if e.get("dept") == dept and e.get("senior")]
    if not candidates:
        return None
    return max(candidates, key=lambda x: x.get("salary", 0))["name"]
