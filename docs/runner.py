"""
Раннер задач курса. Исполняется внутри Pyodide в браузере, но специально
написан так, чтобы его можно было прогнать и обычным CPython — см.
tests/test_runner_local.py. Отладка механики проверок без WASM экономит часы.

Вход и выход — JSON-строки. Никаких словарей через границу JS↔Python:
так не остаётся PyProxy-объектов, которые надо вручную уничтожать.

Главная идея: в файлах курса уже есть check(actual, expected, label).
На сборке оригинальный def check вырезается, а сюда подставляется версия,
которая КОПИТ структурированный результат вместо печати. Поэтому UI
показывает по-задачно OK/FAIL с actual/expected, не разбирая stdout.
"""

import io
import json
import reprlib
import sys
import traceback

# В WASM стек меньше, чем в CPython: без явного лимита кривая рекурсия роняет
# не RecursionError, а весь интерпретатор.
sys.setrecursionlimit(1500)

STDOUT_LIMIT = 200_000

_R = reprlib.Repr()
_R.maxstring = _R.maxother = 240
_R.maxlist = _R.maxtuple = 24
_R.maxdict = 16
_R.maxlevel = 4          # has_cycle строит ЦИКЛИЧЕСКИЙ список: обычный repr
                         # ушёл бы в бесконечную рекурсию прямо внутри проверки


def _srepr(x):
    try:
        return _R.repr(x)
    except Exception as e:                       # сломанный __repr__ у студента
        return f"<repr упал: {type(e).__name__}>"


class _CappedIO(io.StringIO):
    """Бесконечный цикл с print() превращается из зависания во внятную ошибку."""

    def write(self, s):
        if self.tell() > STDOUT_LIMIT:
            raise RuntimeError(
                "Слишком много вывода — похоже на бесконечный цикл с print()"
            )
        return super().write(s)


class Runner:
    def __init__(self):
        self.results = []

    def check(self, actual, expected, label=""):
        try:
            ok = bool(actual == expected)
        except Exception as e:                   # сломанный __eq__ у студента
            ok = False
            label = f"{label} [сравнение упало: {type(e).__name__}]"
        self.results.append({
            "label": label,
            "ok": ok,
            "actual": _srepr(actual),
            "expected": _srepr(expected),
        })
        return ok


def _clean_tb(exc, user_files):
    """Трейсбек только по кадрам студента — служебные рамки раннера скрыты."""
    out = []
    tb = exc.__traceback__
    while tb is not None:
        code = tb.tb_frame.f_code
        if code.co_filename in user_files:
            out.append({
                "file": code.co_filename,
                "lineno": tb.tb_lineno,
                "func": code.co_name,
            })
        tb = tb.tb_next
    return out


def _locate(exc, user_files):
    """Самый ГЛУБОКИЙ кадр, принадлежащий коду студента."""
    frames = _clean_tb(exc, user_files)
    return frames[-1] if frames else None


def _exec(filename, code, g, user_files):
    """Скомпилировать и исполнить кусок. Возвращает описание ошибки или None."""
    if not code.strip():
        return None
    try:
        obj = compile(code, filename, "exec")
    except SyntaxError as e:
        return {
            "kind": "syntax",
            "file": filename,
            "msg": e.msg,
            "lineno": e.lineno,
            "offset": e.offset,
            "text": (e.text or "").rstrip(),
        }
    try:
        # ТОЛЬКО globals, без отдельного locals. Иначе factorial_recursive
        # не найдёт сам себя при рекурсивном вызове, а to_list(build_list(...))
        # не увидит соседнюю функцию. Ломается тихо и выглядит как ошибка студента.
        exec(obj, g)
    except BaseException as e:
        return {
            "kind": "runtime",
            "file": filename,
            "type": type(e).__name__,
            "msg": str(e),
            "at": _locate(e, user_files),
            "frames": _clean_tb(e, user_files),
        }
    return None


def _run(prelude, units, blocks):
    r = Runner()
    g = {"__name__": "__drill__", "check": r.check}
    out = _CappedIO()
    real_stdout = sys.stdout
    sys.stdout = out

    report = {"prelude_error": None, "units": [], "blocks": [], "stdout": ""}
    user_files = set()

    try:
        report["prelude_error"] = _exec("<prelude>", prelude, g, user_files)

        # Сначала ВСЕ реализации файла, потом тесты. Иначе reverse_list не сможет
        # вызвать build_list, а check(st.get_min(), …) не найдёт MinStack.
        # Даже когда проверяем одну задачу — грузим весь урок, подставляя
        # заготовки там, где решения ещё нет.
        for u in units:
            fname = f"<task:{u['id']}>"
            user_files.add(fname)
            err = _exec(fname, u["code"], g, user_files)
            if err:
                report["units"].append({"task": u["id"], "error": err})

        # Тест-блоки идут последовательно в общем неймспейсе — ровно как при
        # локальном `python file.py`. Разница только в том, что падение блока N
        # не убивает блок N+1.
        for b in blocks:
            start = len(r.results)
            fname = f"<test:{b['task']}>"
            err = _exec(fname, b["code"], g, user_files)
            report["blocks"].append({
                "task": b["task"],
                "checks": r.results[start:],
                "error": err,
            })
    finally:
        sys.stdout = real_stdout

    report["stdout"] = out.getvalue()
    return report


def run_json(payload_json):
    """Единственная точка входа. JSON-строка внутрь, JSON-строка наружу."""
    p = json.loads(payload_json)
    report = _run(p.get("prelude", ""), p.get("units", []), p.get("blocks", []))
    return json.dumps(report, ensure_ascii=False)
