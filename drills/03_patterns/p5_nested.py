# ============================================================
# ПАТТЕРН: ВЛОЖЕННЫЕ СТРУКТУРЫ
# Основной паттерн:
#   for student in students:
#       for course in student.get("courses", []):
#           # course — внутренний объект
#           # student.get("grade") — фильтр по внешнему
# Правило перед задачей:
#   # Вход: ... Выход: ... Паттерн: ...
# ============================================================


def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")


students = [
    {
        "name": "Ivan",
        "grade": "A",
        "courses": [
            {"name": "math", "score": 90, "passed": True},
            {"name": "physics", "score": 85, "passed": True},
            {"name": "history", "score": 78, "passed": True},
        ],
    },
    {
        "name": "Anna",
        "grade": "B",
        "courses": [
            {"name": "math", "score": 72, "passed": True},
            {"name": "biology", "score": 58, "passed": False},
            {"name": "history", "score": 80, "passed": True},
        ],
    },
    {
        "name": "Oleg",
        "grade": "C",
        "courses": [
            {"name": "math", "score": 45, "passed": False},
            {"name": "physics", "score": 60, "passed": False},
        ],
    },
    {
        "name": "Mila",
        "grade": "A",
        "courses": [
            {"name": "biology", "score": 95, "passed": True},
            {"name": "history", "score": 88, "passed": True},
            {"name": "math", "score": 82, "passed": True},
        ],
    },
    {
        "name": "Petr",
        "grade": "B",
        "courses": [
            {"name": "physics", "score": 70, "passed": True},
            {"name": "math", "score": 55, "passed": False},
        ],
    },
]


# ------------------------------------------------------------
# 1. total_courses_taken(students) → int
# Суммарное количество курсов по всем студентам
# Ожидается: 13
# ------------------------------------------------------------
def total_courses_taken(students):
    return sum(len(s.get("courses", [])) for s in students)


check(total_courses_taken(students), 13, "total_courses_taken")


# ------------------------------------------------------------
# 2. total_passed(students) → int
# Суммарное количество пройденных курсов (passed == True)
# Ожидается: 9
# ------------------------------------------------------------
def total_passed(students):
    return sum(
        1 for s in students for course in s.get("courses", []) if course.get("passed")
    )


check(total_passed(students), 9, "total_passed")


# ------------------------------------------------------------
# 3. avg_score_by_student(students) → dict
# Средний балл каждого студента по его курсам (округли до 2 знаков)
# Ожидается: {"Ivan": 84.33, "Anna": 70.0, "Oleg": 52.5, "Mila": 88.33, "Petr": 62.5}
# ------------------------------------------------------------
def avg_score_by_student(students):
    totals = {}
    counts = {}
    for s in students:
        for course in s.get("courses", []):
            name = s.get("name")
            score = course.get("score", 0)
            totals[name] = totals.get(name, 0) + score
            counts[name] = counts.get(name, 0) + 1
    return {name: round(totals[name] / counts[name], 2) for name in totals}


check(avg_score_by_student(students), {"Ivan": 84.33, "Anna": 70.0, "Oleg": 52.5, "Mila": 88.33, "Petr": 62.5}, "avg_score_by_student")


# ------------------------------------------------------------
# 4. total_score_by_course(students) → dict
# Суммарный score по каждому курсу (по всем студентам)
# Ожидается: {"math": 344, "physics": 215, "history": 246, "biology": 153}
# ------------------------------------------------------------
def total_score_by_course(students):
    score_courses = {}
    for s in students:
        for course in s.get("courses", []):
            name = course.get("name")
            score = course.get("score", 0)
            score_courses[name] = score_courses.get(name, 0) + score
    return score_courses


check(total_score_by_course(students), {"math": 344, "physics": 215, "history": 246, "biology": 153}, "total_score_by_course")


# ------------------------------------------------------------
# 5. failing_students(students) → list[str]
# Имена студентов у которых есть хотя бы один непройденный курс
# Ожидается: ["Anna", "Oleg", "Petr"]
# ------------------------------------------------------------
def failing_students(students):
    fail_stud = []
    for s in students:
        for course in s.get("courses", []):
            if not course.get("passed"):
                name = s.get("name")

                if name not in fail_stud:
                    fail_stud.append(name)
    return fail_stud


check(failing_students(students), ["Anna", "Oleg", "Petr"], "failing_students")


# ------------------------------------------------------------
# 6. top_course(students) → str
# Курс с максимальным суммарным score
# Ожидается: "math"
# ------------------------------------------------------------
def top_course(students):
    score_courses = {}
    for s in students:
        for course in s.get("courses", []):
            name = course.get("name")
            score = course.get("score", 0)
            score_courses[name] = score_courses.get(name, 0) + score
    return max(score_courses, key=score_courses.get)


check(top_course(students), "math", "top_course")


# ------------------------------------------------------------
# 7. best_student(students) → str
# Студент с наивысшим средним баллом
# Ожидается: "Mila"
# ------------------------------------------------------------
def best_student(students):
    avg_score_stud = avg_score_by_student(students)
    return max(avg_score_stud, key=avg_score_stud.get)


check(best_student(students), "Mila", "best_student")
