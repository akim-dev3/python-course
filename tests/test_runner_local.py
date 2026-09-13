#!/usr/bin/env python3
"""
Прогон docs/runner.py локальным CPython — той же минорной версии, что внутри
Pyodide 314. Смысл: отладить механику проверок до появления браузера и WASM.

    python tests/test_runner_local.py
"""

import importlib.util
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "docs" / "content.json"

spec = importlib.util.spec_from_file_location("runner", ROOT / "docs" / "runner.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

failures = []


def expect(cond, msg):
    if not cond:
        failures.append(msg)
    return cond


def run_lesson(lesson, code_overrides=None):
    """Прогнать урок целиком, как это сделает сайт."""
    overrides = code_overrides or {}
    units = [
        {"id": t["id"],
         "code": overrides.get(t["id"],
                               t["reference_solution"] or t["starter_code"])}
        for t in lesson["tasks"]
    ]
    blocks = [{"task": t["id"], "code": t["test_source"]}
              for t in lesson["tasks"] if t["has_own_tests"]]
    payload = json.dumps({"prelude": lesson["prelude"],
                          "units": units, "blocks": blocks})
    return json.loads(runner.run_json(payload))


def main():
    if not CONTENT.exists():
        raise SystemExit("нет docs/content.json — сначала python build_content.py")
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    lessons = {l["id"]: l for l in data["lessons"]}

    print("Прогон уроков как есть (решённые задачи + заготовки):\n")
    for lesson in data["lessons"]:
        rep = run_lesson(lesson)

        expect(rep["prelude_error"] is None,
               f"{lesson['id']}: prelude упал: {rep['prelude_error']}")
        expect(not rep["units"],
               f"{lesson['id']}: заготовка не компилируется: {rep['units']}")

        total = sum(len(b["checks"]) for b in rep["blocks"])
        passed = sum(c["ok"] for b in rep["blocks"] for c in b["checks"])
        crashed = [b["task"] for b in rep["blocks"] if b["error"]]

        expect(not crashed,
               f"{lesson['id']}: тест-блок упал с исключением: {crashed}")

        # Задача считается решённой, только если отработали ВСЕ ожидаемые
        # проверки и все зелёные: иначе «первый check прошёл, на втором вылетело»
        # засчиталось бы как успех.
        by_task = {b["task"]: b for b in rep["blocks"]}
        solved_now = []
        for t in lesson["tasks"]:
            b = by_task.get(t["id"])
            if (b and not b["error"] and len(b["checks"]) == t["expected_checks"]
                    and all(c["ok"] for c in b["checks"])):
                solved_now.append(t["name"])

        in_repo = [t["name"] for t in lesson["tasks"] if t["solved_in_repo"]]
        print(f"  {lesson['id']:<8} checks {passed}/{total:<3} "
              f"решено по тестам: {len(solved_now)}  в файле: {len(in_repo)}")

        # Всё, что уже решено в файле и имеет свои тесты, обязано быть зелёным.
        for t in lesson["tasks"]:
            if t["solved_in_repo"] and t["has_own_tests"]:
                expect(t["name"] in solved_now,
                       f"{lesson['id']}/{t['name']}: решение из файла НЕ проходит "
                       f"свои же тесты")

    # ---- отдельные проверки поведения раннера ----
    print("\nПоведение раннера:")

    def one(code, test, prelude=""):
        return json.loads(runner.run_json(json.dumps({
            "prelude": prelude,
            "units": [{"id": "t", "code": code}],
            "blocks": [{"task": "t", "code": test}],
        })))

    r = one("def f(x):\n    return x * 2\n", 'check(f(2), 4, "f")')
    expect(r["blocks"][0]["checks"][0]["ok"], "простой зелёный check не сработал")
    print("  OK   зелёный check")

    r = one("def f(x)\n    return x\n", 'check(f(1), 1, "f")')
    err = r["units"][0]["error"]
    expect(err["kind"] == "syntax" and err["lineno"] == 1,
           f"SyntaxError не пойман или строка неверна: {err}")
    print(f"  OK   SyntaxError → строка {err['lineno']}, ничего не исполнялось")

    r = one("def f():\n    return 1 // 0\n", 'check(f(), 1, "f")')
    err = r["blocks"][0]["error"]
    expect(err and err["type"] == "ZeroDivisionError", f"runtime-ошибка не поймана: {err}")
    expect(err["at"] and err["at"]["lineno"] == 2,
           f"строка ошибки в коде студента определена неверно: {err['at']}")
    print(f"  OK   runtime-ошибка → {err['type']} в строке {err['at']['lineno']}")

    r = one("def f():\n    return f()\n", 'check(f(), 1, "f")')
    err = r["blocks"][0]["error"]
    expect(err and err["type"] == "RecursionError",
           f"бесконечная рекурсия не поймана: {err}")
    print("  OK   бесконечная рекурсия → RecursionError, процесс жив")

    r = one("def f():\n    while True:\n        print('x')\n", 'check(f(), 1, "f")')
    err = r["blocks"][0]["error"]
    expect(err and "бесконечный цикл" in err["msg"],
           f"лимит stdout не сработал: {err}")
    print("  OK   бесконечный print → обрыв по лимиту вывода")

    # Циклический связный список + собственный __repr__ — классическая ловушка:
    # обычный repr ушёл бы в бесконечную рекурсию ВНУТРИ проверки.
    cyc = (
        "class N:\n"
        "    def __init__(self):\n"
        "        self.next = self\n"
        "    def __repr__(self):\n"
        "        return f'N({self.next!r})'\n"
        "def f():\n"
        "    return N()\n"
    )
    r = one(cyc, 'check(f(), None, "cycle")')
    c = r["blocks"][0]["checks"][0]
    expect(not c["ok"] and isinstance(c["actual"], str),
           f"циклический repr не обезврежен: {r['blocks'][0]}")
    print("  OK   циклический __repr__ не вешает проверку")

    r = one("def f():\n    return 1\n", 'check(f(), 1, "a")\ncheck(f(), 2, "b")')
    checks = r["blocks"][0]["checks"]
    expect(len(checks) == 2 and checks[0]["ok"] and not checks[1]["ok"],
           f"падение одной проверки не должно ронять остальные: {checks}")
    print("  OK   красный check не обрывает остальные")

    print()
    if failures:
        print(f"ПРОВАЛЕНО ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print("Все проверки пройдены.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
