# ============================================================
# МИНИ-ПРОЕКТ 2: Аналитика студентов
# build_report(data) → dict с 8 полями
# Пишешь сам, без черновика
# ============================================================

data = {
    "students": [
        {
            "id": 1,
            "name": "Ivan",
            "grade": "senior",
            "courses": [
                {"name": "math", "score": 90, "passed": True},
                {"name": "physics", "score": 85, "passed": True},
                {"name": "history", "score": 78, "passed": True},
            ],
        },
        {
            "id": 2,
            "name": "Anna",
            "grade": "junior",
            "courses": [
                {"name": "math", "score": 72, "passed": True},
                {"name": "biology", "score": 58, "passed": False},
                {"name": "history", "score": 80, "passed": True},
            ],
        },
        {
            "id": 3,
            "name": "Oleg",
            "grade": "junior",
            "courses": [
                {"name": "math", "score": 45, "passed": False},
                {"name": "physics", "score": 60, "passed": False},
            ],
        },
        {
            "id": 4,
            "name": "Mila",
            "grade": "senior",
            "courses": [
                {"name": "biology", "score": 95, "passed": True},
                {"name": "history", "score": 88, "passed": True},
                {"name": "math", "score": 82, "passed": True},
            ],
        },
        {
            "id": 5,
            "name": "Petr",
            "grade": "junior",
            "courses": [
                {"name": "physics", "score": 70, "passed": True},
                {"name": "math", "score": 55, "passed": False},
            ],
        },
        {
            "id": 6,
            "name": "Dina",
            "grade": "senior",
            "courses": [
                {"name": "history", "score": 91, "passed": True},
                {"name": "biology", "score": 87, "passed": True},
            ],
        },
        {"id": 7, "name": "Mark", "grade": "junior", "courses": []},
        {
            "id": 8,
            "name": "Olga",
            "grade": "senior",
            "courses": [
                {"name": "math", "score": 88, "passed": True},
                {"name": "physics", "score": 76, "passed": True},
                {"name": "biology", "score": 62, "passed": False},
            ],
        },
    ]
}

# ------------------------------------------------------------
# build_report(data) → dict
#
# total_students   int    — всего студентов
# total_courses    int    — суммарное количество курсов
# pass_rate        float  — доля пройденных курсов (0.0–1.0, округли до 2)
# top_student      str    — студент с наивысшим средним баллом
# failing          list   — имена студентов с хотя бы одним failed курсом
# avg_by_course    dict   — {course: avg_score} по всем студентам (округли до 2)
# honor_roll       list   — имена студентов у которых ВСЕ курсы passed,
#                           отсортированные по имени (студентов без курсов не включать)
# grade_counts     dict   — {grade: количество студентов}
#
# Ожидаемый вывод:
# total_students  → 8
# total_courses   → 18
# pass_rate       → 0.72  (13 passed из 18)
# top_student     → "Dina"  (avg: 89.0)
# failing         → ["Anna", "Oleg", "Petr", "Olga"]
# avg_by_course   → {"math": 72.0, "physics": 72.75, "history": 84.25, "biology": 75.5}
# honor_roll      → ["Dina", "Ivan", "Mila"]
# grade_counts    → {"senior": 4, "junior": 4}
# ------------------------------------------------------------


#! 1
def total_students(data):
    return len(data)


#! 2
def total_courses(data):
    return sum(len(student.get("courses", [])) for student in data)


#! 3
def pass_rate(data):
    total_passed = 0
    all_courses = 0
    for student in data:
        for course in student.get("courses", []):
            all_courses += 1
            if course.get("passed"):
                total_passed += 1
    if all_courses == 0:
        return 0.0

    return round(total_passed / all_courses, 2)


#! 4
def top_student(data):
    best_avg = 0.0
    best_student_name = None

    for student in data:
        courses = student.get("courses", [])
        if not courses:
            continue

        scores = [course.get("score", 0) for course in courses]
        avg_student = sum(scores) / len(scores)

        if avg_student > best_avg:
            best_avg = avg_student
            best_student_name = student.get("name")

    return best_student_name


#! 5
def failing(data):
    return [
        student.get("name")
        for student in data
        if any(course.get("passed") is False for course in student.get("courses", []))
    ]


#! 6
def avg_by_course(data):
    course_scores = {}

    for student in data:
        for course in student.get("courses", []):
            name = course.get("name")
            score = course.get("score", 0)

            if name not in course_scores:
                course_scores[name] = []
            course_scores[name].append(score)

    avg_courses = {}
    for name, scores in course_scores.items():
        avg_courses[name] = round(sum(scores) / len(scores), 2)

    return avg_courses


#! 7
def honor_roll(data):
    result = []
    for student in data:
        courses = student.get("courses", [])

        if not courses:
            continue

        if all(course.get("passed") for course in courses):
            result.append(student.get("name"))

    return sorted(result)


#! 8
def grade_counts(data):
    students_res = {}
    for student in data:
        grade = student.get("grade")
        students_res[grade] = students_res.get(grade, 0) + 1
    return students_res


def build_report(data):
    data = data.get("students", [])

    return {
        "total_students": total_students(data),
        "total_courses": total_courses(data),
        "pass_rate": pass_rate(data),
        "top_student": top_student(data),
        "failing": failing(data),
        "avg_by_course": avg_by_course(data),
        "honor_roll": honor_roll(data),
        "grade_counts": grade_counts(data),
    }


print(build_report(data))
