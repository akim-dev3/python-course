# ============================================================
# ФИНАЛЬНЫЙ ПРОЕКТ — с нуля
# Новые данные, новая предметная область
# Пишешь build_report без черновиков и без подглядывания
# ============================================================

data = {
    "sessions": [
        {
            "id": 1,
            "trainer": "Alex",
            "type": "cardio",
            "duration": 45,
            "completed": True,
            "members": [
                {"name": "Ivan", "calories": 420, "hr_avg": 145},
                {"name": "Anna", "calories": 380, "hr_avg": 138},
            ],
        },
        {
            "id": 2,
            "trainer": "Mila",
            "type": "strength",
            "duration": 60,
            "completed": True,
            "members": [
                {"name": "Oleg", "calories": 310, "hr_avg": 122},
                {"name": "Petr", "calories": 290, "hr_avg": 118},
                {"name": "Anna", "calories": 330, "hr_avg": 125},
            ],
        },
        {
            "id": 3,
            "trainer": "Alex",
            "type": "yoga",
            "duration": 30,
            "completed": False,
            "members": [
                {"name": "Ivan", "calories": 150, "hr_avg": 95},
            ],
        },
        {
            "id": 4,
            "trainer": "Mila",
            "type": "cardio",
            "duration": 50,
            "completed": True,
            "members": [
                {"name": "Dina", "calories": 460, "hr_avg": 152},
                {"name": "Ivan", "calories": 440, "hr_avg": 148},
            ],
        },
        {
            "id": 5,
            "trainer": "Roma",
            "type": "strength",
            "duration": 55,
            "completed": True,
            "members": [
                {"name": "Petr", "calories": 320, "hr_avg": 130},
                {"name": "Oleg", "calories": 280, "hr_avg": 115},
            ],
        },
        {
            "id": 6,
            "trainer": "Alex",
            "type": "cardio",
            "duration": 40,
            "completed": False,
            "members": [],
        },
        {
            "id": 7,
            "trainer": "Roma",
            "type": "yoga",
            "duration": 60,
            "completed": True,
            "members": [
                {"name": "Dina", "calories": 180, "hr_avg": 98},
                {"name": "Anna", "calories": 160, "hr_avg": 92},
            ],
        },
        {
            "id": 8,
            "trainer": "Mila",
            "type": "strength",
            "duration": 45,
            "completed": True,
            "members": [
                {"name": "Ivan", "calories": 350, "hr_avg": 128},
                {"name": "Dina", "calories": 370, "hr_avg": 132},
                {"name": "Petr", "calories": 300, "hr_avg": 120},
            ],
        },
    ]
}

# ------------------------------------------------------------
# build_report(data) → dict
#
# total_sessions      int   — всего тренировок
# completed_sessions  int   — завершённых тренировок
# total_members_visits int  — суммарное количество посещений (все сессии)
# top_member          str   — участник с наибольшим суммарным calories (только completed)
# calories_by_type    dict  — {type: total_calories} только completed
# avg_duration_by_trainer dict — {trainer: avg_duration} все сессии (округли до 2)
# high_intensity      list  — имена участников у которых хотя бы одна сессия с hr_avg > 140
#                             (только completed, без дублей, sorted)
# best_trainer        str   — тренер с наибольшим количеством завершённых сессий
# ------------------------------------------------------------


#! 1
def total_sessions(data):
    return len(data)


#! 2
def completed_sessions(data):
    return len([1 for session in data if session.get("completed")])


#! 3
def total_members_visits(data):
    return len([member for session in data for member in session.get("members", [])])


#! 4
def top_member(data):
    member_dict = {}
    for session in data:
        if session.get("completed"):
            for member in session.get("members", []):
                name = member.get("name")
                calories = member.get("calories", 0)
                member_dict[name] = member_dict.get(name, 0) + calories
    if not member_dict:
        return None
    best_member = max(member_dict, key=member_dict.get)
    return best_member


#! 5
def calories_by_type(data):
    calories_dict = {}
    for session in data:
        if session.get("completed"):
            for member in session.get("members", []):
                type = session.get("type")
                calories = member.get("calories", 0)
                calories_dict[type] = calories_dict.get(type, 0) + calories
    if not calories_dict:
        return None
    return calories_dict


#! 6
def avg_duration_by_trainer(data):
    if not data:
        return {}

    trainer_durations = {}

    for session in data:
        trainer = session.get("trainer")
        duration = session.get("duration", 0)

        if trainer:
            if trainer not in trainer_durations:
                trainer_durations[trainer] = []
            trainer_durations[trainer].append(duration)

    return {
        trainer: round(sum(durations) / len(durations), 2)
        for trainer, durations in trainer_durations.items()
    }


#! 7
def high_intensity(data):
    return sorted(
        {
            member.get("name")
            for session in data
            if session.get("completed")
            for member in session.get("members", [])
            if member.get("hr_avg", 0) > 140
        }
    )


#! 8
def best_trainer(data):
    count_completed = {}
    for session in data:
        trainer = session.get("trainer")
        if session.get("completed"):
            count_completed[trainer] = count_completed.get(trainer, 0) + 1
    best_tr = max(count_completed, key=count_completed.get)
    return best_tr


def build_report(data):
    data = data.get("sessions", [])

    return {
        "total_sessions": total_sessions(data),
        "completed_sessions": completed_sessions(data),
        "total_members_visits": total_members_visits(data),
        "top_member": top_member(data),
        "calories_by_type": calories_by_type(data),
        "avg_duration_by_trainer": avg_duration_by_trainer(data),
        "high_intensity": high_intensity(data),
        "best_trainer": best_trainer(data),
    }


print(build_report(data))
