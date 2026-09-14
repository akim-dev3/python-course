#!/usr/bin/env python3
"""
Дописать check(...) в файлы, где задачи есть, а вызовов нет вовсе (01_dict).

Вызов не выдумывается: он записан в самом комментарии задачи строкой вида
`count_active_adults(users) → int`. Отсюда берётся и выражение, и имя функции.

Ожидание берётся из `# Ожидается: X`, если оно разбирается как литерал, и
сверяется с фактом — это тот же гейт, что в migrate_to_check.py. Там, где
ожидание записано с обрывом (`[{"name": "Ivan"...}]`) и литералом не является,
значение выводится из фактического поведения уже проверенного решения; такие
места печатаются отдельным списком, чтобы это было видно, а не молчаливо.

    python add_checks.py            показать, что будет сделано
    python add_checks.py --apply    записать
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
SEP = "# " + "-" * 60

TARGETS = ["drills/01_dict/tasks.py", "drills/01_dict/drill_weak.py"]

CHECK_DEF = ('def check(actual, expected, label=""):\n'
             '    status = "OK  " if actual == expected else "FAIL"\n'
             '    print(f"{status} {label}: {actual!r} (ожидалось {expected!r})")\n')

SIG_RE = re.compile(r"^([A-Za-z_]\w*)\s*(\([^)]*\))\s*→")
EXP_RE = re.compile(r"^Ожидается:\s*(.+)$")


def blocks_of(lines):
    out, i = [], 0
    while i < len(lines):
        if lines[i].rstrip() == SEP:
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith("#") \
                    and lines[j].rstrip() != SEP:
                j += 1
            if j < len(lines) and lines[j].rstrip() == SEP:
                out.append((i, j))
                i = j + 1
                continue
        i += 1
    return out


def parse_expected(text):
    for cand in (text, re.sub(r"\s+\([^()]*\)$", "", text).strip()):
        try:
            return True, ast.literal_eval(cand), cand
        except Exception:
            continue
    return False, None, None


def process(rel, apply):
    path = ROOT / rel
    src = path.read_text(encoding="utf-8", newline="")
    if "def check(" in src:
        return {"file": rel, "skipped": "уже есть check"}

    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    defs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    # Исполняем файл один раз: нужны и датасеты, и сами решения.
    env = {"__name__": "__addchecks__"}
    with redirect_stdout(io.StringIO()):
        exec(compile(src, str(path), "exec"), env)

    plan, derived, problems = [], [], []
    for open_i, close_i in blocks_of(lines):
        body = [l.strip().lstrip("#").strip() for l in lines[open_i + 1: close_i]]

        sig = next((SIG_RE.match(b) for b in body if SIG_RE.match(b)), None)
        if not sig:
            continue
        name, args = sig.group(1), sig.group(2)
        if name not in defs:
            problems.append(f"{rel}: в блоке сигнатура {name}{args}, но такой функции нет")
            continue

        # Если блок содержит явные примеры `fn(...) → значение`, они и есть
        # контракт задачи: там записаны настоящие аргументы (а в сигнатуре
        # стоит просто имя параметра вроде dept, которого в данных нет).
        # Только после явного «Примеры:» — иначе под этот шаблон попадёт
        # строка сигнатуры `fn(users) → int`, где справа тип, а не значение.
        examples, in_examples = [], False
        for b in body:
            if re.match(r"^Примеры?:", b):
                in_examples = True
                continue
            if not in_examples:
                continue
            m = re.match(rf"^({re.escape(name)}\s*\(.*\))\s*→\s*(.+)$", b)
            if m:
                examples.append((m.group(1).strip(), m.group(2).strip()))

        cases = examples or [(f"{name}{args}", None)]
        emitted = []

        for call, exp_text in cases:
            try:
                actual = eval(call, env)
            except Exception as e:
                problems.append(f"{rel}:{open_i + 1} {call} → {type(e).__name__}: {e}")
                emitted = None
                break

            if exp_text is None:
                exp_text = next((EXP_RE.match(b).group(1) for b in body if EXP_RE.match(b)), None)
            ok, value, literal = parse_expected(exp_text) if exp_text else (False, None, None)

            if ok and actual != value:
                problems.append(f"{rel}:{open_i + 1} {name}: факт {actual!r} "
                                f"vs комментарий {value!r}")
                emitted = None
                break
            if not ok:
                derived.append(
                    f"{rel}: {name} — ожидание выведено из поведения "
                    f"(в комментарии {'обрыв: ' + exp_text if exp_text else 'нет ожидания'})")
                literal = repr(actual)

            emitted.append(f'check({call}, {literal}, "{name}")\n')

        if emitted:
            plan.append((defs[name].end_lineno, "".join(emitted)))

    if apply and plan:
        # Вставляем снизу вверх, чтобы не съезжали номера строк.
        for end_lineno, text in sorted(plan, reverse=True):
            lines.insert(end_lineno, "\n\n" + text)
        out = "".join(lines)
        first_code = next(i for i, l in enumerate(out.splitlines(keepends=True))
                          if l.strip() and not l.lstrip().startswith("#"))
        parts = out.splitlines(keepends=True)
        parts.insert(first_code, CHECK_DEF + "\n\n")
        path.write_text("".join(parts), encoding="utf-8", newline="")

    return {"file": rel, "added": len(plan), "derived": derived, "problems": problems}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    print("Дописывание check() в файлы без вызовов"
          + ("" if args.apply else "  [ПРОГОН БЕЗ ЗАПИСИ]") + "\n")
    all_derived, all_problems = [], []
    for rel in TARGETS:
        res = process(rel, args.apply)
        if "skipped" in res:
            print(f"  --   {rel:<34} {res['skipped']}")
            continue
        print(f"  OK   {rel:<34} добавлено проверок: {res['added']}")
        all_derived += res["derived"]
        all_problems += res["problems"]

    if all_derived:
        print(f"\nОжидание выведено из поведения решения ({len(all_derived)}):")
        for d in all_derived:
            print("  -", d)
    if all_problems:
        print(f"\nПРОБЛЕМЫ ({len(all_problems)}):")
        for p in all_problems:
            print("  -", p)

    if args.apply:
        print("\nПроверка после записи:")
        bad = False
        for rel in TARGETS:
            buf = io.StringIO()
            with redirect_stdout(buf):
                exec(compile((ROOT / rel).read_text(encoding="utf-8"), rel, "exec"),
                     {"__name__": "__verify__"})
            out = buf.getvalue()
            ok = len(re.findall(r"^OK  ", out, re.M))
            fail = len(re.findall(r"^FAIL", out, re.M))
            print(f"  {'OK  ' if not fail else 'FAIL'} {rel:<34} OK={ok} FAIL={fail}")
            bad |= fail > 0
        if bad:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
