# ============================================================
# ПАТТЕРН: AVG + TOP N + MAX В DICT
# AVG — всегда два dict: totals + counts
# TOP N → list[str], MAX → str
# Правило перед задачей:
#   # Вход: ... Выход: ... Паттерн: ...
# ============================================================


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


athletes = [
    {
        "name": "Ivan",
        "sport": "swimming",
        "country": "RUS",
        "gold": 3,
        "silver": 2,
        "score": 92,
    },
    {
        "name": "Anna",
        "sport": "running",
        "country": "USA",
        "gold": 1,
        "silver": 4,
        "score": 78,
    },
    {
        "name": "Oleg",
        "sport": "swimming",
        "country": "RUS",
        "gold": 0,
        "silver": 1,
        "score": 65,
    },
    {
        "name": "Mila",
        "sport": "gymnastics",
        "country": "RUS",
        "gold": 5,
        "silver": 1,
        "score": 97,
    },
    {
        "name": "Tom",
        "sport": "running",
        "country": "USA",
        "gold": 2,
        "silver": 3,
        "score": 84,
    },
    {
        "name": "Sara",
        "sport": "gymnastics",
        "country": "GBR",
        "gold": 4,
        "silver": 2,
        "score": 95,
    },
    {
        "name": "Kai",
        "sport": "swimming",
        "country": "JPN",
        "gold": 2,
        "silver": 0,
        "score": 88,
    },
    {
        "name": "Lena",
        "sport": "running",
        "country": "GBR",
        "gold": 0,
        "silver": 2,
        "score": 71,
    },
]


# ------------------------------------------------------------
# 1. avg_score_by_sport(athletes) → dict
# Средний score по видам спорта (округли до 2 знаков)
# Ожидается: {"swimming": 81.67, "running": 77.67, "gymnastics": 96.0}
# ------------------------------------------------------------
def avg_score_by_sport(athletes):
    totals = {}
    counts = {}

    for a in athletes:
        sport = a.get("sport")
        score = a.get("score", 0)
        totals[sport] = totals.get(sport, 0) + score
        counts[sport] = counts.get(sport, 0) + 1

    return {sport: round(totals[sport] / counts[sport], 2) for sport in totals}


check(avg_score_by_sport(athletes), {"swimming": 81.67, "running": 77.67, "gymnastics": 96.0}, "avg_score_by_sport")


# ------------------------------------------------------------
# 2. avg_gold_by_country(athletes) → dict
# Среднее количество gold по странам (округли до 2 знаков)
# Ожидается: {"RUS": 2.67, "USA": 1.5, "GBR": 2.0, "JPN": 2.0}
# ------------------------------------------------------------
def avg_gold_by_country(athletes):
    groups = {}
    for a in athletes:
        country = a.get("country")
        gold = a.get("gold", 0)

        if country not in groups:
            groups[country] = []

        groups[country].append(gold)

    return {
        country: round(sum(medals) / len(medals), 2)
        for country, medals in groups.items()
    }


check(avg_gold_by_country(athletes), {"RUS": 2.67, "USA": 1.5, "GBR": 2.0, "JPN": 2.0}, "avg_gold_by_country")


# ------------------------------------------------------------
# 3. top3_athletes(athletes) → list[str]
# ТОП-3 спортсмена по gold
# Ожидается: ["Mila", "Sara", "Ivan"]
# ------------------------------------------------------------
def top3_athletes(athletes):
    return [
        a.get("name")
        for a in sorted(athletes, key=lambda x: x.get("gold", 0), reverse=True)[:3]
    ]


check(top3_athletes(athletes), ["Mila", "Sara", "Ivan"], "top3_athletes")


# ------------------------------------------------------------
# 4. top2_sports_by_score(athletes) → list[str]
# ТОП-2 вида спорта по среднему score
# Ожидается: ["gymnastics", "swimming"]
# ------------------------------------------------------------
def top2_sports_by_score(athletes):
    avg_sports = avg_score_by_sport(athletes)
    return sorted(avg_sports, key=avg_sports.get, reverse=True)[:2]


check(top2_sports_by_score(athletes), ["gymnastics", "swimming"], "top2_sports_by_score")


# ------------------------------------------------------------
# 5. best_country_by_gold(athletes) → str
# Страна с максимальной суммой gold
# Ожидается: "RUS"
# ------------------------------------------------------------
def best_country_by_gold(athletes):
    country_dict = {}
    for a in athletes:
        country = a.get("country")
        gold = a.get("gold", 0)
        country_dict[country] = country_dict.get(country, 0) + gold
    return max(country_dict, key=country_dict.get)


check(best_country_by_gold(athletes), "RUS", "best_country_by_gold")


# ------------------------------------------------------------
# 6. top2_runners(athletes) → list[str]
# ТОП-2 бегуна (sport == "running") по score
# Ожидается: ["Tom", "Anna"]
# ------------------------------------------------------------
def top2_runners(athletes):
    runners = [a for a in athletes if a.get("sport") == "running"]
    return [
        a.get("name")
        for a in sorted(runners, key=lambda x: x.get("score", 0), reverse=True)[:2]
    ]


check(top2_runners(athletes), ["Tom", "Anna"], "top2_runners")


# ------------------------------------------------------------
# 7. medals_by_country(athletes) → dict
# Суммарное количество медалей (gold + silver) по странам
# Ожидается: {"RUS": 12, "USA": 10, "GBR": 8, "JPN": 2}
# ------------------------------------------------------------
def medals_by_country(athletes):
    country_medals = {}
    for a in athletes:
        country = a.get("country")
        gold = a.get("gold", 0)
        silver = a.get("silver", 0)
        sum_medals = gold + silver
        country_medals[country] = country_medals.get(country, 0) + sum_medals
    return country_medals


check(medals_by_country(athletes), {"RUS": 12, "USA": 10, "GBR": 8, "JPN": 2}, "medals_by_country")
