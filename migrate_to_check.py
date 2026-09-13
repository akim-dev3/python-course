#!/usr/bin/env python3
"""
Разовая миграция старых drill-файлов с `print(...)` на `check(...)`.

Зачем: только у check() ожидание записано машиночитаемо, поэтому сайт может
показать «ожидалось X, получилось Y». Заодно локальный запуск начинает
печатать OK/FAIL во всех модулях, а не только в новых.

ГЕЙТ КОРРЕКТНОСТИ. Ожидание берётся из комментария (это ЗАМЫСЕЛ), затем файл
исполняется и фактический результат сверяется с этим ожиданием. Переписывается
только то, где они совпали. Где разошлись — задача помечается на ручной разбор
и остаётся как была: иначе мы забетонировали бы в тесте существующую ошибку.

    python migrate_to_check.py            показать, что будет сделано
    python migrate_to_check.py --apply    переписать файлы
"""

import argparse
import ast
import io
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent

TARGETS = [
    "drills/03_patterns/p1_count_sum.py",
    "drills/03_patterns/p2_filter_sorted.py",
    "drills/03_patterns/p3_groupby.py",
    "drills/03_patterns/p4_avg_topn.py",
    "drills/03_patterns/p5_nested.py",
    "drills/04_algo/p1_complexity.py",
    "drills/04_algo/p2_recursion.py",
    "drills/04_algo/p3_search.py",
    "drills/05_patterns/p1_two_pointers.py",
    "drills/05_patterns/p1b_two_pointers_reinforce.py",
]

CHECK_DEF = '''

def check(actual, expected, label=""):
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")

'''

# Имена, которые не считаем «задачей» при выборе метки для check().
WRAPPERS = {
    "sorted", "len", "sum", "max", "min", "list", "set", "dict", "tuple",
    "str", "int", "float", "bool", "abs", "round", "repr", "type", "any", "all",
}


def label_for(arg_node):
    """Имя проверяемой функции: пропускаем обёртки вроде sorted(...)."""
    for node in ast.walk(arg_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id not in WRAPPERS:
                return node.func.id
    for node in ast.walk(arg_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            return node.func.attr
    return "проверка"


def inline_comment(line):
    """Текст комментария справа от кода — с учётом # внутри строковых литералов."""
    in_str, quote, esc = False, "", False
    for i, ch in enumerate(line):
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if in_str:
            if ch == quote:
                in_str = False
        elif ch in "\"'":
            in_str, quote = True, ch
        elif ch == "#":
            return line[i + 1:].strip()
    return None


def block_expectation(lines, print_lineno):
    """Для формата 03_patterns: `# Ожидается: X` в комментарном блоке выше.

    Между print(...) и блоком лежит тело функции, поэтому на код НЕ
    останавливаемся — границей служит предыдущий print/check, то есть конец
    предыдущей задачи.
    """
    i = print_lineno - 2
    while i >= 0:
        s = lines[i].strip()
        if s.startswith("print(") or s.startswith("check("):
            return None                      # ушли в предыдущую задачу
        m = re.match(r"^#\s*Ожидается:\s*(.+)$", s)
        if m:
            return m.group(1).strip()
        i -= 1
    return None


def next_line_expectation(lines, print_lineno):
    """Ожидание строкой НИЖЕ print(...) — так оформлены длинные словари."""
    i = print_lineno            # 0-based индекс следующей строки
    if i < len(lines):
        s = lines[i].strip()
        if s.startswith("#"):
            return s[1:].strip()
    return None


def block_says_unordered(lines, print_lineno):
    """Задача сама объявила, что порядок результата не важен."""
    i = print_lineno - 2
    while i >= 0:
        s = lines[i].strip()
        if s.startswith("print(") or s.startswith("check("):
            return False
        low = s.lower()
        if "порядок не важен" in low or "в любом порядке" in low \
                or "порядок не имеет значения" in low:
            return True
        i -= 1
    return False


def parse_expected(text):
    """Комментарий → литерал Python. Возвращает (ok, значение, исходный текст)."""
    if not text:
        return False, None, None
    # «255  (85 + 92 + 78)» — берём часть до пояснения в скобках
    candidates = [text]
    # «255  (85 + 92 + 78)», «12 (все)», «5 (между 9 и 12)» — отрезаем пояснение
    m = re.match(r"^(.*?)\s+\([^()]*\)$", text)
    if m and m.group(1).strip():
        candidates.append(m.group(1).strip())
    for cand in candidates:
        try:
            return True, ast.literal_eval(cand), cand
        except Exception:
            continue
    return False, None, None


def collect_prints(src):
    """Top-level `print(один_аргумент)` в порядке появления."""
    tree = ast.parse(src)
    out = []
    for node in tree.body:
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "print"
                and len(node.value.args) == 1 and not node.value.keywords):
            out.append(node.value)
    return tree, out


def actual_values(path, src, expected_count):
    """Исполнить файл, подменив print, и собрать фактические значения по порядку."""
    recorded = []

    def fake_print(*args, **kwargs):
        recorded.append(args[0] if len(args) == 1 else args)

    g = {"__name__": "__migrate__", "print": fake_print}
    try:
        with redirect_stdout(io.StringIO()):
            exec(compile(src, str(path), "exec"), g)
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    if len(recorded) != expected_count:
        return None, (f"печатей {len(recorded)}, а top-level print(...) "
                      f"{expected_count} — соответствие неоднозначно")
    return recorded, None


def migrate(path, apply):
    src = path.read_text(encoding="utf-8", newline="")
    if "def check(" in src:
        return {"file": str(path), "skipped": "уже мигрирован"}

    lines = src.splitlines(keepends=True)
    tree, prints = collect_prints(src)
    if not prints:
        return {"file": str(path), "skipped": "нет top-level print()"}

    recorded, err = actual_values(path, src, len(prints))
    if err:
        return {"file": str(path), "error": err}

    plan, manual = [], []
    for idx, call in enumerate(prints):
        line0 = call.lineno - 1
        raw_line = lines[line0]
        text = (inline_comment(raw_line)
                or next_line_expectation(lines, call.lineno)
                or block_expectation(lines, call.lineno))
        ok, value, literal = parse_expected(text)

        if not ok:
            manual.append((call.lineno, (text or "нет ожидания")[:60]))
            continue

        actual = recorded[idx]
        # Если задача сама объявила «порядок не важен», сравниваем как множества:
        # иначе честное решение через sorted() выглядело бы провалом.
        unordered = (block_says_unordered(lines, call.lineno)
                     and isinstance(actual, (list, tuple))
                     and isinstance(value, (list, tuple)))
        same = (sorted(actual) == sorted(value)) if unordered else (actual == value)

        if not same:
            manual.append((call.lineno,
                           f"расхождение: факт {actual!r} vs комментарий {value!r}"))
            continue

        expr = ast.get_source_segment(src, call.args[0])
        if unordered:
            expr, literal = f"sorted({expr})", f"sorted({literal})"
        indent = raw_line[:len(raw_line) - len(raw_line.lstrip())]
        eol = "\r\n" if raw_line.endswith("\r\n") else "\n"
        plan.append((line0, f'{indent}check({expr}, {literal}, "{label_for(call.args[0])}"){eol}'))

    if apply and plan:
        for line0, new in plan:
            lines[line0] = new
        out = "".join(lines)
        # def check вставляем сразу после шапки — перед первым кодом
        insert_at = 0
        for i, ln in enumerate(out.splitlines(keepends=True)):
            if ln.strip() and not ln.lstrip().startswith("#"):
                insert_at = i
                break
        parts = out.splitlines(keepends=True)
        parts.insert(insert_at, CHECK_DEF.lstrip("\n"))
        path.write_text("".join(parts), encoding="utf-8", newline="")

    return {"file": str(path), "converted": len(plan), "manual": manual,
            "total": len(prints)}


def verify(path):
    """После миграции: запустить файл и убедиться, что все check зелёные."""
    src = path.read_text(encoding="utf-8", newline="")
    buf = io.StringIO()
    g = {"__name__": "__verify__"}
    try:
        with redirect_stdout(buf):
            exec(compile(src, str(path), "exec"), g)
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    out = buf.getvalue()
    ok = len(re.findall(r"^OK  ", out, re.M))
    fail = len(re.findall(r"^FAIL", out, re.M))
    return (ok, fail), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="переписать файлы")
    args = ap.parse_args()

    print("Миграция print() → check()" + ("" if args.apply else "  [ПРОГОН БЕЗ ЗАПИСИ]"))
    print()
    total_conv = total_manual = 0
    manual_all = []

    for rel in TARGETS:
        path = ROOT / rel
        res = migrate(path, args.apply)
        if "skipped" in res:
            print(f"  --   {rel:<48} {res['skipped']}")
            continue
        if "error" in res:
            print(f"  ERR  {rel:<48} {res['error']}")
            continue
        total_conv += res["converted"]
        total_manual += len(res["manual"])
        mark = "OK  " if not res["manual"] else "WARN"
        print(f"  {mark} {rel:<48} {res['converted']}/{res['total']} переведено")
        for lineno, why in res["manual"]:
            manual_all.append(f"{rel}:{lineno} — {why}")

    print(f"\n  переведено: {total_conv}, на ручной разбор: {total_manual}")
    if manual_all:
        print("\nТребует ручного разбора:")
        for m in manual_all:
            print("  -", m)

    if args.apply:
        print("\nПроверка после миграции (все check должны быть зелёными):")
        bad = False
        for rel in TARGETS:
            counts, err = verify(ROOT / rel)
            if err:
                print(f"  ERR  {rel:<48} {err}")
                bad = True
                continue
            ok, fail = counts
            print(f"  {'OK  ' if not fail else 'FAIL'} {rel:<48} OK={ok} FAIL={fail}")
            bad |= fail > 0
        if bad:
            print("\nЕСТЬ КРАСНЫЕ — разберись до коммита.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
