# ============================================================
# ПАТТЕРН: COUNT + SUM
# Правило перед задачей:
#   # Вход: ... Выход: ... Паттерн: ...
# ============================================================

players = [
    {"name": "Alex", "level": 15, "premium": True, "coins": 4500, "wins": 120},
    {"name": "Bob", "level": 8, "premium": False, "coins": 900, "wins": 34},
    {"name": "Cara", "level": 22, "premium": True, "coins": 8100, "wins": 250},
    {"name": "Dan", "level": 5, "premium": False, "coins": 300, "wins": 10},
    {"name": "Eva", "level": 18, "premium": True, "coins": 6200, "wins": 175},
    {"name": "Frank", "level": 11, "premium": False, "coins": 1500, "wins": 67},
    {"name": "Grace", "level": 30, "premium": True, "coins": 12000, "wins": 400},
    {"name": "Henry", "level": 3, "premium": False, "coins": 150, "wins": 5},
]


# ------------------------------------------------------------
# 1. count_premium(players) → int
# Количество premium-игроков
# Ожидается: 4
# ------------------------------------------------------------
def count_premium(players):
    return sum(1 for player in players if player.get("premium"))


print(count_premium(players))


# ------------------------------------------------------------
# 2. count_high_level(players) → int
# Количество игроков с level >= 10
# Ожидается: 5
# ------------------------------------------------------------
def count_high_level(players):
    return sum(1 for player in players if player.get("level", 0) >= 10)


print(count_high_level(players))


# ------------------------------------------------------------
# 3. count_winning_free(players) → int
# Количество non-premium игроков с wins > 30
# Ожидается: 2
# ------------------------------------------------------------
def count_winning_free(players):
    return sum(
        1
        for player in players
        if player.get("premium") == False and player.get("wins", 0) > 30
    )


print(count_winning_free(players))


# ------------------------------------------------------------
# 4. total_coins(players) → int
# Сумма всех coins
# Ожидается: 33650
# ------------------------------------------------------------
def total_coins(players):
    return sum(player.get("coins", 0) for player in players)


print(total_coins(players))


# ------------------------------------------------------------
# 5. premium_wins(players) → int
# Сумма wins только у premium-игроков
# Ожидается: 945
# ------------------------------------------------------------
def premium_wins(players):
    return sum(player.get("wins", 0) for player in players if player.get("premium"))


print(premium_wins(players))


# ------------------------------------------------------------
# 6. coins_high_level(players) → int
# Сумма coins у игроков с level >= 10
# Ожидается: 32300
# ------------------------------------------------------------
def coins_high_level(players):
    return sum(
        player.get("coins", 0) for player in players if player.get("level", 0) >= 10
    )


print(coins_high_level(players))


# ------------------------------------------------------------
# 7. count_elite(players) → int
# Количество premium-игроков с wins > 200
# Ожидается: 2
# ------------------------------------------------------------
def count_elite(players):
    return sum(
        1 for player in players if player.get("premium") and player.get("wins", 0) > 200
    )


print(count_elite(players))
