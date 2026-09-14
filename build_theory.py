#!/usr/bin/env python3
"""
Сборка страниц теории: Markdown-конспекты и файлы-справочники → статический HTML.

Страницы теории намеренно НЕ часть SPA: так картинки, Mermaid и печать просто
работают, а конспект можно открыть во второй вкладке рядом с задачей.

Конвертация делается здесь, на этапе сборки, а не в браузере — клиентского
Markdown-парсера на сайте нет вообще.
"""

import html
import re
import shutil
import sys
from pathlib import Path

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

ROOT = Path(__file__).resolve().parent
VAULT = ROOT.parent / "Brain" / "Области" / "Программирование"
ATTACH = VAULT / "attachments"

# Что публикуем. Навигатор НЕ публикуется: он состоит из вики-ссылок на личные
# заметки и структуру хранилища.
NOTES = [
    ("Python — Модуль 1 База Python.md", "m1-basics",
     "Модуль 1 — База Python", ["diag"]),
    ("Python — Модуль 2 Коллекции.md", "m2-collections",
     "Модуль 2 — Коллекции", ["diag"]),
    ("Python — Модуль 3 Dict и агрегации.md", "m3-dict",
     "Модуль 3 — Dict и агрегации", ["m03"]),
    ("Python — слабые точки dict и агрегация.md", "m3-pitfalls",
     "Частые ошибки в dict-паттернах", ["m03"]),
    ("Python — Модуль 4 Алгоритмическое мышление.md", "m4-algo",
     "Модуль 4 — Алгоритмическое мышление", ["m04"]),
    ("Python — Модуль 4 Алгоритмы (на пальцах).md", "m4-algo-plain",
     "Модуль 4 — Алгоритмы на пальцах", ["m04"]),
    ("Python — Модуль 5 Two Pointers и Sliding Window (на пальцах).md",
     "m5-two-pointers", "Модуль 5 — Two Pointers и Sliding Window на пальцах", ["m05"]),
    ("Python — Модуль 6 Структуры данных (на пальцах).md", "m6-data-structures",
     "Модуль 6 — Структуры данных на пальцах", ["m06"]),
]

# Файлы-шпаргалки из самого курса — тоже теория.
REFERENCES = [
    ("patterns/dict_patterns.py", "ref-dict",
     "Шпаргалка — dict-паттерны", ["m03"]),
    ("drills/04_algo/algo_reference.py", "ref-algo",
     "Шпаргалка — Big O, рекурсия, бинарный поиск", ["m04"]),
    ("drills/06_data_structures/ds_reference.py", "ref-ds",
     "Шпаргалка — структуры данных", ["m06"]),
]

SLUGS = {slug: title for _, slug, title, _ in NOTES}
TITLE_TO_SLUG = {}   # заполняется ниже: имя заметки Obsidian → slug

PAGE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Python-курс</title>
<link rel="stylesheet" href="../styles.css">
<link rel="stylesheet" href="../pygments.css">
<link rel="stylesheet" href="../theory.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="../index.html#/">Python-курс</a>
  <span class="crumbs">Теория › {title}</span>
  <a class="btn btn--ghost" href="../index.html#/">К задачам</a>
</header>
<main class="wrap theory">
<h1>{title}</h1>
{meta}
{body}
{footer}
</main>
{mermaid}
</body>
</html>
"""

MERMAID_SCRIPT = """<script type="module">
  import m from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  m.initialize({ startOnLoad: true, theme: "dark",
                 themeVariables: { fontFamily: "ui-monospace, monospace" } });
</script>"""


def strip_frontmatter(text):
    """Срезать YAML-шапку. Оттуда берём только дату обновления."""
    updated = None
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end]
            m = re.search(r"^обновлена:\s*(.+)$", fm, re.M)
            if m:
                updated = m.group(1).strip()
            text = text[end + 4:]
    return text.lstrip("\n"), updated


def strip_tail_sections(text):
    """Убрать хвостовые разделы со ссылками на личные заметки."""
    for header in ("## Связи", "## Связанные заметки", "## Навигатор"):
        i = text.find("\n" + header)
        if i != -1:
            text = text[:i]
    return text.rstrip() + "\n"


def sanitize_paths(text):
    """Убрать пути в личное хранилище.

    Заодно чинит устаревшее: `Brain_Resources/python/python_course/` указывает
    туда, где курс лежал раньше, — сейчас это просто `python_course/`.
    Остальные `Brain_Resources/python/...` — архивные папки, на сайте им
    не место, поэтому упоминание сворачивается в нейтральное «архив курса».
    """
    text = text.replace("Brain_Resources/python/python_course/", "python_course/")
    text = re.sub(r"`?Brain_Resources/python/[A-Za-z0-9_\-/]*`?", "архив курса", text)
    text = re.sub(r"`?Brain/[A-Za-z0-9_\-/]*`?", "хранилище заметок", text)
    return text


def convert_links(text, images_used):
    """Вики-синтаксис Obsidian → HTML."""

    def img(m):
        name = m.group(1).split("|")[0].strip()
        images_used.add(name)
        # Без loading="lazy": у ненагруженной картинки нет собственных размеров,
        # блок схлопывается почти в ноль, и браузер так и не начинает загрузку.
        # На странице их единицы — экономить нечего.
        return f'<figure><img src="img/{name}" alt="{html.escape(name)}"></figure>'

    text = re.sub(r"!\[\[([^\]]+)\]\]", img, text)

    def link(m):
        raw = m.group(1)
        target, _, alias = raw.partition("|")
        target = target.split("#")[0].strip()
        label = (alias or target).strip()
        slug = TITLE_TO_SLUG.get(target)
        if slug:
            return f'<a href="{slug}.html">{html.escape(label)}</a>'
        # Цель не публикуется — оставляем текстом, чтобы не светить
        # структуру личного хранилища.
        return html.escape(label)

    return re.sub(r"\[\[([^\]]+)\]\]", link, text)


def extract_mermaid(text):
    blocks = []

    def take(m):
        blocks.append(m.group(1))
        return f"\n@@MERMAID{len(blocks) - 1}@@\n"

    text = re.sub(r"```mermaid\n(.*?)```", take, text, flags=re.S)
    return text, blocks


def restore_mermaid(html_text, blocks):
    for i, code in enumerate(blocks):
        html_text = html_text.replace(
            f"<p>@@MERMAID{i}@@</p>",
            f'<pre class="mermaid">{html.escape(code.strip())}</pre>')
    return html_text


def render_note(path, slug, title, modules, out_dir, lessons_by_module):
    text = path.read_text(encoding="utf-8")
    text, updated = strip_frontmatter(text)
    text = strip_tail_sections(text)
    text = sanitize_paths(text)

    images = set()
    text, mermaid_blocks = extract_mermaid(text)
    text = convert_links(text, images)

    body = markdown.markdown(text, extensions=[
        "fenced_code", "tables", "sane_lists", "attr_list", "toc", "codehilite",
    ], extension_configs={
        "codehilite": {"guess_lang": False, "pygments_style": "monokai"},
    })
    body = restore_mermaid(body, mermaid_blocks)

    for name in images:
        src = ATTACH / name
        if src.exists():
            shutil.copy2(src, out_dir / "img" / name)
        else:
            print(f"    ВНИМАНИЕ: нет картинки {name}")

    meta = f'<p class="muted">Конспект обновлён {html.escape(updated)}</p>' if updated else ""
    write_page(out_dir / f"{slug}.html", title, meta, body,
               modules, lessons_by_module, bool(mermaid_blocks))
    return {"id": slug, "title": title, "href": f"theory/{slug}.html",
            "kind": "note", "modules": modules, "images": len(images),
            "has_mermaid": bool(mermaid_blocks)}


def render_reference(rel, slug, title, modules, out_dir, lessons_by_module):
    src = (ROOT / rel).read_text(encoding="utf-8")
    body = ('<p class="muted">Файл курса <code>' + html.escape(rel) +
            '</code> — открывается и запускается локально.</p>' +
            highlight(src, PythonLexer(), HtmlFormatter(cssclass="codehilite")))
    write_page(out_dir / f"{slug}.html", title, "", body,
               modules, lessons_by_module, False)
    return {"id": slug, "title": title, "href": f"theory/{slug}.html",
            "kind": "reference", "modules": modules, "images": 0,
            "has_mermaid": False}


def write_page(dest, title, meta, body, modules, lessons_by_module, has_mermaid):
    links = []
    for mid in modules:
        for lesson in lessons_by_module.get(mid, []):
            links.append(f'<a href="../index.html#/l/{lesson["id"]}">'
                         f'{html.escape(lesson["title"])}</a>')
    footer = ('<div class="theory-footer"><div class="panel__title">Задачи по этой теме</div>'
              + " · ".join(links) + "</div>") if links else ""

    dest.write_text(PAGE.format(
        title=html.escape(title), meta=meta, body=body, footer=footer,
        mermaid=MERMAID_SCRIPT if has_mermaid else "",
    ), encoding="utf-8", newline="")


def build(docs_dir, lessons):
    """Собрать все страницы теории, вернуть индекс для content.json."""
    out_dir = docs_dir / "theory"
    (out_dir / "img").mkdir(parents=True, exist_ok=True)

    lessons_by_module = {}
    for l in lessons:
        lessons_by_module.setdefault(l["module"], []).append(l)

    for filename, slug, title, _ in NOTES:
        TITLE_TO_SLUG[Path(filename).stem] = slug

    (docs_dir / "pygments.css").write_text(
        HtmlFormatter(style="monokai").get_style_defs(".codehilite"),
        encoding="utf-8", newline="")

    index = []
    for filename, slug, title, modules in NOTES:
        path = VAULT / filename
        if not path.exists():
            print(f"    ПРОПУЩЕН (нет файла): {filename}")
            continue
        index.append(render_note(path, slug, title, modules, out_dir, lessons_by_module))

    for rel, slug, title, modules in REFERENCES:
        if not (ROOT / rel).exists():
            print(f"    ПРОПУЩЕН (нет файла): {rel}")
            continue
        index.append(render_reference(rel, slug, title, modules, out_dir, lessons_by_module))

    return index


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    import json
    content = json.loads((ROOT / "docs" / "content.json").read_text(encoding="utf-8"))
    idx = build(ROOT / "docs", content["lessons"])
    for t in idx:
        print(f"  {t['kind']:<9} {t['href']:<34} картинок={t['images']} "
              f"mermaid={t['has_mermaid']}")
