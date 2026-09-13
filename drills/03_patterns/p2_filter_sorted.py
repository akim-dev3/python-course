# ============================================================
# ПАТТЕРН: FILTER + FILTER+SORTED
# Ключевое правило: dict не нужен — каждый элемент идёт в результат сам по себе
# Правило перед задачей:
#   # Вход: ... Выход: ... Паттерн: ...
# ============================================================


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


movies = [
    {
        "title": "Inception",
        "genre": "sci-fi",
        "year": 2010,
        "rating": 8.8,
        "watched": True,
    },
    {
        "title": "Interstellar",
        "genre": "sci-fi",
        "year": 2014,
        "rating": 8.5,
        "watched": True,
    },
    {
        "title": "The Room",
        "genre": "drama",
        "year": 2003,
        "rating": 3.7,
        "watched": False,
    },
    {
        "title": "Parasite",
        "genre": "drama",
        "year": 2019,
        "rating": 8.6,
        "watched": True,
    },
    {"title": "Dune", "genre": "sci-fi", "year": 2021, "rating": 8.0, "watched": False},
    {"title": "Joker", "genre": "drama", "year": 2019, "rating": 8.4, "watched": True},
    {
        "title": "Morbius",
        "genre": "action",
        "year": 2022,
        "rating": 5.2,
        "watched": False,
    },
    {
        "title": "Oppenheimer",
        "genre": "drama",
        "year": 2023,
        "rating": 8.9,
        "watched": True,
    },
]


# ------------------------------------------------------------
# 1. watched_titles(movies) → list[str]
# Названия просмотренных фильмов (порядок не важен)
# Ожидается: ["Inception", "Interstellar", "Parasite", "Joker", "Oppenheimer"]
# ------------------------------------------------------------
def watched_titles(movies):
    return sorted(movie.get("title") for movie in movies if movie.get("watched"))


check(sorted(watched_titles(movies)), sorted(["Inception", "Interstellar", "Parasite", "Joker", "Oppenheimer"]), "watched_titles")


# ------------------------------------------------------------
# 2. top_rated_watched(movies) → list[str]
# Названия просмотренных фильмов по rating убыванию
# Ожидается: ["Oppenheimer", "Inception", "Parasite", "Interstellar", "Joker"]
# ------------------------------------------------------------
def top_rated_watched(movies):
    watched_movies = [movie for movie in movies if movie.get("watched")]
    return [
        movie.get("title")
        for movie in sorted(
            watched_movies, key=lambda x: x.get("rating", 0), reverse=True
        )
    ]


check(top_rated_watched(movies), ["Oppenheimer", "Inception", "Parasite", "Interstellar", "Joker"], "top_rated_watched")


# ------------------------------------------------------------
# 3. watchlist(movies) → list[str]
# Непросмотренные фильмы с rating >= 7.5, по rating убыванию
# Ожидается: ["Dune"]
# ------------------------------------------------------------
def watchlist(movies):
    unwatched_movies = [
        movie
        for movie in movies
        if movie.get("watched") == False and movie.get("rating", 0) >= 7.5
    ]
    return [
        movie.get("title")
        for movie in sorted(
            unwatched_movies, key=lambda x: x.get("rating", 0), reverse=True
        )
    ]


check(watchlist(movies), ["Dune"], "watchlist")


# ------------------------------------------------------------
# 4. good_recent(movies) → list[str]
# Фильмы с rating >= 8.5 И year >= 2019, по year убыванию
# Ожидается: ["Oppenheimer", "Parasite"]
# ------------------------------------------------------------
def good_recent(movies):
    filtered_movies = [
        m for m in movies if m.get("rating", 0) >= 8.5 and m.get("year", 0) >= 2019
    ]

    sorted_movies = sorted(
        filtered_movies, key=lambda m: m.get("year", 0), reverse=True
    )

    return [m.get("title") for m in sorted_movies]


check(good_recent(movies), ["Oppenheimer", "Parasite"], "good_recent")


# ------------------------------------------------------------
# 5. sci_fi_titles(movies) → list[str]
# Sci-fi фильмы по rating убыванию (все, независимо от watched)
# Ожидается: ["Inception", "Interstellar", "Dune"]
# ------------------------------------------------------------
def sci_fi_titles(movies):
    sciFi_movies = [movie for movie in movies if movie.get("genre") == "sci-fi"]
    return [
        movie.get("title")
        for movie in sorted(
            sciFi_movies, key=lambda x: x.get("rating", 0), reverse=True
        )
    ]


check(sci_fi_titles(movies), ["Inception", "Interstellar", "Dune"], "sci_fi_titles")


# ------------------------------------------------------------
# 6. top3_overall(movies) → list[str]
# ТОП-3 фильма по rating (все жанры)
# Ожидается: ["Oppenheimer", "Inception", "Parasite"]
# ------------------------------------------------------------
def top3_overall(movies):
    sort_rait_movies = sorted(movies, key=lambda x: x.get("rating", 0), reverse=True)[
        :3
    ]

    return [movie.get("title") for movie in sort_rait_movies]


check(top3_overall(movies), ["Oppenheimer", "Inception", "Parasite"], "top3_overall")


# ------------------------------------------------------------
# 7. new_releases(movies) → list[str]
# Все фильмы с year >= 2019, по year убыванию
# Ожидается: ["Oppenheimer", "Morbius", "Dune", "Parasite", "Joker"]
# ------------------------------------------------------------
def new_releases(movies):
    year_movies = [movie for movie in movies if movie.get("year", 0) >= 2019]
    return [
        movie.get("title")
        for movie in sorted(year_movies, key=lambda x: x.get("year", 0), reverse=True)
    ]


check(new_releases(movies), ["Oppenheimer", "Morbius", "Dune", "Parasite", "Joker"], "new_releases")
