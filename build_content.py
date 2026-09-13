#!/usr/bin/env python3
"""
Генератор content.json для веб-платформы курса.

Читает drill-файлы, вытаскивает из них задачи и тесты, кладёт результат
в docs/content.json. Файлы курса — источник правды; этот скрипт их только
ЧИТАЕТ и никогда не исполняет (в курсе есть бенчмарки на секунды).

Ключевая идея — посегментная нарезка. Файл режется на чередующиеся куски:
  raw  — неизменяемый текст (шапка, комментарные блоки, тесты)
  slot — тело задачи, которое студент заменяет своим кодом
Склейка всех сегментов обязана побайтово совпасть с оригиналом (--verify).
Отсюда бесплатно получается корректная выгрузка «скачать решения»: подставил
в слоты свой код, склеил — и файл в точности того же формата, что в курсе.

Запуск:
    python build_content.py            собрать
    python build_content.py --verify   + проверить побайтовую реконструкцию
    python build_content.py --lint     + проверить, что не утекает личное
"""

import argparse
import ast
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):          # иначе кириллица падает в cp1251-консоли
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

SEP = "# " + "-" * 60          # разделитель блока задачи, ровно 62 символа

# Версия Pyodide запиннена: обновление — сознательное действие, не «latest».
RUNTIME = {
    "pyodide_version": "314.0.6",
    "index_url": "https://cdn.jsdelivr.net/pyodide/v314.0.6/full/",
    # Размеры измерены range-запросами — нужны для честного прогресс-бара,
    # потому что jsDelivr отдаёт stdlib chunked, без Content-Length.
    "prefetch": [
        {"file": "pyodide.asm.wasm", "bytes": 3438246},
        {"file": "python_stdlib.zip", "bytes": 2505338},
    ],
    "timeout_ms": 5000,
    "stdout_limit": 200000,
}

# Реестр: какие файлы публикуем и куда они ложатся в структуре курса.
# parser="check" — файлы с машиночитаемым check(actual, expected, label).
# Остальные форматы (print + ожидание в комментарии) добавятся после миграции.
LESSONS = [
    dict(id="diag",   module="diag", parser="check",
         src="diagnostic_check.py",
         title="Диагностика после паузы"),
    dict(id="m05-p2", module="m05", parser="check",
         src="drills/05_patterns/p2_sliding_window.py",
         title="P2: Sliding Window (скользящее окно)"),
    dict(id="m05-p3", module="m05", parser="check",
         src="drills/05_patterns/p3_mastery_check.py",
         title="P3: Итоговая проверка"),
    dict(id="m06-p1", module="m06", parser="check",
         src="drills/06_data_structures/p1_stack.py",
         title="P1: Stack (стек)"),
    dict(id="m06-p2", module="m06", parser="check",
         src="drills/06_data_structures/p2_queue.py",
         title="P2: Queue (очередь)"),
    dict(id="m06-p3", module="m06", parser="check",
         src="drills/06_data_structures/p3_linked_list.py",
         title="P3: Linked List (связный список)"),
    dict(id="m06-p4", module="m06", parser="check",
         src="drills/06_data_structures/p4_hashing.py",
         title="P4: Hashing (хэш-таблицы)"),
]

MODULES = [
    dict(id="diag", title="Диагностика",
         subtitle="Что осталось после паузы — Модули 1-4"),
    dict(id="m05", title="Модуль 5 — Two Pointers и Sliding Window",
         subtitle="Два указателя и скользящее окно"),
    dict(id="m06", title="Модуль 6 — Структуры данных",
         subtitle="Stack, Queue, Linked List, Hashing"),
]

# Помеченные секции внутри комментарного блока задачи.
NOTE_PREFIXES = (
    "Паттерн", "Сложность", "Окно", "ЛОВУШКА", "Замечание",
    "Подсказка", "База", "Шаг", "ВАЖНО",
)


# ---------------------------------------------------------------------------
# Разбор комментарных блоков
# ---------------------------------------------------------------------------

def comment_block_bounds(lines, def_lineno):
    """Границы блока `# ---…---` прямо над def. Идём ВВЕРХ от def, чтобы блок
    физически не мог «перепрыгнуть» на чужую задачу.

    Возвращает (i_open, i_close) — индексы строк-разделителей, 0-based,
    или (None, None), если блока нет (так отсекаются def check и class Node).
    """
    i = def_lineno - 2                          # строка прямо над def
    while i >= 0 and not lines[i].strip():      # пропускаем пустые
        i -= 1
    if i < 0 or lines[i].rstrip() != SEP:
        return None, None
    close, j = i, i - 1
    while j >= 0 and lines[j].rstrip() != SEP:
        if not lines[j].lstrip().startswith("#"):   # наткнулись на код — блок битый
            return None, None
        j -= 1
    return (j, close) if j >= 0 else (None, None)


def strip_hashes(lines):
    """`# текст` → `текст`, `#` → ``."""
    out = []
    for ln in lines:
        s = ln.rstrip("\n").rstrip()
        s = s.lstrip()
        if s.startswith("#"):
            s = s[1:]
            if s.startswith(" "):
                s = s[1:]
        out.append(s)
    return out


def parse_block(body_lines):
    """Комментарный блок задачи → (title, chunks).

    chunks — список {"kind": "para"|"example"|"note", ...} в порядке появления.
    """
    text = strip_hashes(body_lines)
    while text and not text[0].strip():
        text.pop(0)
    while text and not text[-1].strip():
        text.pop()
    if not text:
        return "", []

    # Заголовок: первая строка, плюс продолжение до первой пустой строки
    # (случай «4. MinStack — стек, у которого get_min() всегда возвращает /
    # минимум за O(1)»).
    title_parts, idx = [text[0].strip()], 1
    while idx < len(text) and text[idx].strip():
        title_parts.append(text[idx].strip())
        idx += 1
    title = " ".join(title_parts)

    chunks, para = [], []

    def flush_para():
        if para:
            chunks.append({"kind": "para", "text": " ".join(para)})
            para.clear()

    i = idx
    while i < len(text):
        line = text[i].strip()
        if not line:
            flush_para()
            i += 1
            continue

        prefix = next((p for p in NOTE_PREFIXES
                       if line.startswith(p + ":") or line.startswith(p + " —")), None)
        if prefix:
            flush_para()
            note = [line.split(":", 1)[1].strip() if ":" in line else line]
            i += 1
            while i < len(text) and text[i].strip():
                nxt = text[i].strip()
                if any(nxt.startswith(p + ":") for p in NOTE_PREFIXES):
                    break
                note.append(nxt)
                i += 1
            chunks.append({"kind": "note", "label": prefix,
                           "text": " ".join(note).strip()})
            continue

        # Строка-пример: содержит стрелку и выглядит как вызов
        if "→" in line and re.match(r"^[A-Za-z_]\w*\s*\(", line):
            flush_para()
            examples = []
            while i < len(text) and text[i].strip():
                cur = text[i].strip()
                if "→" not in cur:
                    break
                examples.append(cur)
                i += 1
            chunks.append({"kind": "example", "lines": examples})
            continue

        para.append(line)
        i += 1

    flush_para()
    return title, chunks


def inline_html(s):
    """Экранирование + `код` → <code>."""
    out, parts = [], s.split("`")
    for n, part in enumerate(parts):
        esc = html.escape(part)
        out.append(f"<code>{esc}</code>" if n % 2 else esc)
    return "".join(out)


def chunks_to_html(chunks):
    out = []
    for c in chunks:
        if c["kind"] == "para":
            out.append(f"<p>{inline_html(c['text'])}</p>")
        elif c["kind"] == "example":
            body = "\n".join(html.escape(x) for x in c["lines"])
            out.append(f'<pre class="example">{body}</pre>')
        elif c["kind"] == "note":
            out.append(
                f'<div class="note note--{html.escape(c["label"].lower())}">'
                f'<span class="note__label">{html.escape(c["label"])}</span> '
                f'{inline_html(c["text"])}</div>'
            )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Разбор кода
# ---------------------------------------------------------------------------

def is_stub(node):
    """Тело — ровно `pass`? Для класса: все методы `pass`."""
    if isinstance(node, ast.ClassDef):
        methods = [m for m in node.body if isinstance(m, ast.FunctionDef)]
        return bool(methods) and all(
            len(m.body) == 1 and isinstance(m.body[0], ast.Pass) for m in methods
        )
    return len(node.body) == 1 and isinstance(node.body[0], ast.Pass)


def signature_lines(lines, node):
    """Текст сигнатуры: от `def`/`class` до строки перед первым телом."""
    first_body = node.body[0].lineno
    return lines[node.lineno - 1: first_body - 1]


def make_stub(lines, node):
    """Заготовка с оригинальной сигнатурой и `pass` вместо тела."""
    if isinstance(node, ast.ClassDef):
        out = list(signature_lines(lines, node))
        for k, m in enumerate(m for m in node.body if isinstance(m, ast.FunctionDef)):
            if k:                                # пустая строка только МЕЖДУ методами
                out.append("\n")
            out.extend(signature_lines(lines, m))
            out.append("        pass\n")
        return "".join(out)
    return "".join(signature_lines(lines, node)) + "    pass\n"


class _Refs(ast.NodeVisitor):
    """Какие имена задач упоминаются в куске кода и сколько там check()."""

    def __init__(self, task_names):
        self.task_names = task_names
        self.used = set()
        self.checks = 0

    def visit_Call(self, node):
        f = node.func
        if isinstance(f, ast.Name) and f.id == "check":
            self.checks += 1
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in self.task_names:
            self.used.add(node.id)
        self.generic_visit(node)


def parse_check_file(path, lesson):
    """Один drill-файл в check-формате → (lesson_dict, список задач)."""
    # encoding явный — иначе Windows возьмёт cp1251 и упадёт на кириллице.
    # newline="" отключает трансляцию \r\n → \n: src должен содержать РОВНО то,
    # что лежит в файле, иначе «побайтовая» реконструкция врёт на CRLF-файлах.
    src = path.read_text(encoding="utf-8", newline="")
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src, filename=str(path))

    top = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]

    # Задача — это def/class, над которым есть комментарный блок.
    # Так автоматически отсеиваются служебные def check и class Node,
    # без хрупкого чёрного списка по именам.
    task_nodes = []
    for n in top:
        open_i, close_i = comment_block_bounds(lines, n.lineno)
        if open_i is not None:
            task_nodes.append((n, open_i, close_i))

    if not task_nodes:
        raise SystemExit(f"{path}: не найдено ни одной задачи")

    task_names = {n.name for n, _, _ in task_nodes}
    first_task_line = task_nodes[0][1]          # строка первого разделителя

    # --- prelude: исполняемый код до первой задачи, без оригинального check ---
    prelude_nodes = [
        n for n in tree.body
        if n.end_lineno <= first_task_line
        and not (isinstance(n, ast.FunctionDef) and n.name == "check")
    ]
    prelude = "\n".join(ast.get_source_segment(src, n) for n in prelude_nodes)

    # --- шапка файла для показа в уроке ---
    intro_lines = []
    for ln in lines:
        if ln.lstrip().startswith("#"):
            intro_lines.append(ln)
        elif ln.strip():
            break
    intro_text = [x for x in strip_hashes(intro_lines) if not set(x.strip()) <= {"=", ""}]
    intro_html = "\n".join(
        f"<p>{inline_html(p)}</p>"
        for p in re.split(r"\n\s*\n", "\n".join(intro_text).strip())
        if p.strip()
    )

    # --- сегменты и задачи ---
    segments, tasks, cursor = [], [], 0
    for idx, (node, open_i, close_i) in enumerate(task_nodes):
        a, b = node.lineno - 1, node.end_lineno

        segments.append({"t": "raw", "text": "".join(lines[cursor:a])})
        task_id = f"{lesson['id']}/{node.name}"
        segments.append({"t": "slot", "task": task_id, "text": "".join(lines[a:b])})
        cursor = b

        # Тест-блок: узлы между этой задачей и следующей.
        # Комментарный блок следующей задачи сюда не попадает — берём узлы AST,
        # а не текст.
        next_start = (task_nodes[idx + 1][0].lineno
                      if idx + 1 < len(task_nodes) else len(lines) + 1)
        test_nodes = [
            n for n in tree.body
            if n.lineno > node.end_lineno and n.end_lineno < next_start
        ]
        test_source = "\n".join(ast.get_source_segment(src, n) for n in test_nodes)

        refs = _Refs(task_names)
        for n in test_nodes:
            refs.visit(n)

        title, chunks = parse_block(lines[open_i + 1: close_i])
        m = re.match(r"^\s*(\d+)[.)]\s*(.*)$", title)
        ordinal, title_text = (int(m.group(1)), m.group(2).strip()) if m else (idx + 1, title)

        stub = is_stub(node)
        current = "".join(lines[a:b])

        tasks.append({
            "id": task_id,
            "ordinal": ordinal,
            "name": node.name,
            "kind": "class" if isinstance(node, ast.ClassDef) else "function",
            "title": title_text,
            "description_html": chunks_to_html(chunks),
            "starter_code": make_stub(lines, node),
            "reference_solution": None if stub else current,
            "solved_in_repo": not stub,
            "test_source": test_source,
            "has_own_tests": refs.checks > 0,
            "expected_checks": refs.checks,
            "needs": sorted(refs.used | {node.name}),
            "slot_index": len(segments) - 1,
        })

    segments.append({"t": "raw", "text": "".join(lines[cursor:])})

    lesson_out = {
        "id": lesson["id"],
        "module": lesson["module"],
        "title": lesson["title"],
        "source_file": lesson["src"],
        "intro_html": intro_html,
        "prelude": prelude,
        "segments": segments,
        "tasks": tasks,
    }
    return lesson_out, src


# ---------------------------------------------------------------------------
# Линтер приватности
# ---------------------------------------------------------------------------

LINT_PATTERNS = {
    "путь в личное хранилище": r"Brain[_/]|Второй мозг|Ежедневн|Синтез —|Проекты/|Области/",
    "личные маркеры": r"выгоран|дневник|\bELO\b|тревог|прокраст|слаб(ая|ые|ых) точ",
    "контакты": r"akimowilj|@outlook|@gmail",
    "дата-провала": r"\b[0-3][0-9]\.[01][0-9]\.20[0-9]{2}\b",
}


def lint(payload):
    blob = json.dumps(payload, ensure_ascii=False)
    hits = []
    for label, pat in LINT_PATTERNS.items():
        for m in re.finditer(pat, blob, re.IGNORECASE):
            ctx = blob[max(0, m.start() - 60): m.end() + 60].replace("\\n", " ")
            hits.append(f"  [{label}] …{ctx}…")
    return hits


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="проверить побайтовую реконструкцию файлов из сегментов")
    ap.add_argument("--lint", action="store_true",
                    help="проверить, что в content.json не утекло личное")
    args = ap.parse_args()

    lessons, sources, total, solved = [], {}, 0, 0
    for spec in LESSONS:
        path = ROOT / spec["src"]
        if not path.exists():
            raise SystemExit(f"нет файла: {path}")
        lesson, src = parse_check_file(path, spec)
        lessons.append(lesson)
        sources[spec["id"]] = src
        total += len(lesson["tasks"])
        solved += sum(t["solved_in_repo"] for t in lesson["tasks"])

    modules = []
    for m in MODULES:
        ids = [l["id"] for l in lessons if l["module"] == m["id"]]
        modules.append({**m, "lessons": ids, "theory": []})

    payload = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runtime": RUNTIME,
        "modules": modules,
        "theory": [],
        "lessons": lessons,
    }

    ok = True

    if args.verify:
        print("Реконструкция:")
        good = 0
        for lesson in lessons:
            rebuilt = "".join(s["text"] for s in lesson["segments"])
            if rebuilt == sources[lesson["id"]]:
                good += 1
                mark = "OK  "
            else:
                mark, ok = "FAIL", False
            n = len(lesson["tasks"])
            s = sum(t["solved_in_repo"] for t in lesson["tasks"])
            print(f"  {mark} {lesson['source_file']:<48} задач: {n:>2}  решено: {s}")
        print(f"\n  {good}/{len(lessons)} файлов реконструированы побайтово, "
              f"{total} задач, {solved} решено")

    if args.lint:
        hits = lint(payload)
        print("\nЛинтер приватности:", "чисто" if not hits else f"{len(hits)} срабатываний")
        for h in hits[:20]:
            print(h)
        if hits:
            ok = False

    if not ok:
        print("\nСБОРКА НЕ ЗАПИСАНА — сначала почини то, что выше.")
        return 1

    DOCS.mkdir(exist_ok=True)
    out = DOCS / "content.json"
    # newline="" — иначе Windows подставит CRLF и файл будет расходиться с репо
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                   encoding="utf-8", newline="")
    print(f"\nЗаписано: {out.relative_to(ROOT)} "
          f"({out.stat().st_size // 1024} КБ, {total} задач)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
