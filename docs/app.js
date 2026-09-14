// Приложение курса: карта → урок → задача.
// Hash-роутер, потому что сайт живёт на подпути GitHub Pages и сервера нет.

import { Runtime } from "./runtime.js?v=fecb6288";
import { store } from "./storage.js?v=fecb6288";
import { createEditor } from "./editor.js?v=fecb6288";
import { buildFile, extractSolutions, downloadText, basename } from "./download.js?v=fecb6288";
import { makeZip, downloadBlob } from "./zip.js?v=fecb6288";
import * as fs from "./fsaccess.js?v=fecb6288";

const $ = (sel, root = document) => root.querySelector(sel);
const esc = (s) => String(s).replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let CONTENT = null;
let runtime = null;
const byLesson = new Map();
const byTheory = new Map();

const theoryOf = (ids) => (ids || []).map((id) => byTheory.get(id)).filter(Boolean);

/** Мелкие чипы — для карты курса, где важна компактность. */
function theoryLinks(ids) {
  const items = theoryOf(ids);
  if (!items.length) return "";
  const links = items.map((t) =>
    `<button class="theory-link" data-theory="${t.id}">
       <span class="theory-link__icon">${t.kind === "reference" ? "⌘" : "▤"}</span>
       ${esc(t.title)}</button>`).join("");
  return `<div class="theory-row"><span class="theory-row__label">Теория</span>${links}</div>`;
}

/** Крупные карточки — на странице урока теория идёт ПЕРЕД задачами. */
function theoryCards(ids) {
  const items = theoryOf(ids);
  if (!items.length) return "";
  // Разбор «на пальцах» — первым и крупно, остальное складываем под спойлер:
  // иначе четыре карточки подряд выглядят как «читать всё это».
  const plain = items.filter((t) => t.kind === "plain");
  const rest = items.filter((t) => t.kind !== "plain");

  const KIND = {
    plain: "объяснение с примерами",
    note: "подробный конспект",
    reference: "шпаргалка с кодом",
  };

  const card = (t, main = false) => `<button class="theory-card${main ? " is-main" : ""}"
      data-theory="${t.id}">
      <span class="theory-card__icon">${t.kind === "reference" ? "⌘" : "▤"}</span>
      <span class="theory-card__body">
        <span class="theory-card__title">${esc(t.title)}</span>
        <span class="theory-card__kind">${KIND[t.kind] || "конспект"}${
          t.images ? ` · ${t.images} схем` : ""}</span>
      </span>
      <span class="theory-card__go">Читать →</span>
    </button>`;

  const head = plain.length ? plain : rest.slice(0, 1);
  const tail = plain.length ? rest : rest.slice(1);

  return `<section class="step">
      <div class="step__title">Теория</div>
      <div class="step__hint">Разбор с примерами — читать до задач.</div>
      <div class="theory-cards">${head.map((t) => card(t, true)).join("")}</div>
      ${tail.length ? `<details class="theory-more">
        <summary>ещё материалы по теме: ${tail.length}</summary>
        <div class="theory-cards">${tail.map((t) => card(t)).join("")}</div>
      </details>` : ""}
    </section>`;
}

/** Кнопка «Теория» прямо в шапке задачи — читать, не уходя со страницы. */
function theoryButton(ids) {
  const items = theoryOf(ids);
  if (!items.length) return "";
  const main = items.find((t) => t.kind === "plain")
            || items.find((t) => t.kind !== "reference")
            || items[0];
  return `<button class="btn btn--theory" data-theory="${main.id}"
     title="${esc(main.title)}">▤ Теория</button>`;
}

/**
 * Конспект открывается панелью поверх задачи, а не в новой вкладке:
 * так не теряется место, где ты остановился, и можно читать вперемешку
 * с решением. Статическая страница загружается и встраивается как есть.
 */
async function openTheory(id) {
  const meta = byTheory.get(id);
  if (!meta) return;
  if ($(".reader")) $(".reader").remove();

  const panel = document.createElement("div");
  panel.className = "reader";
  panel.innerHTML = `<div class="reader__bar">
      <span class="reader__title">${esc(meta.title)}</span>
      <a class="btn btn--ghost" href="${meta.href}" target="_blank" rel="noopener"
         title="Открыть отдельной страницей">В новой вкладке</a>
      <button class="btn btn--ghost" id="reader-close">Закрыть <kbd>Esc</kbd></button>
    </div>
    <div class="reader__body theory"><div class="empty">Загружаю конспект…</div></div>`;
  document.body.appendChild(panel);
  document.body.classList.add("has-reader");

  const close = () => {
    panel.remove();
    document.body.classList.remove("has-reader");
  };
  $("#reader-close", panel).onclick = close;

  try {
    const html = await (await fetch(meta.href, { cache: "no-cache" })).text();
    const doc = new DOMParser().parseFromString(html, "text/html");
    const content = doc.querySelector("main.theory");
    $(".reader__body", panel).innerHTML = content
      ? content.innerHTML
      : '<div class="banner banner--error">Не удалось разобрать страницу конспекта.</div>';

    // Картинки в конспекте лежат рядом с ним, а мы встроили его на другую
    // страницу — пути надо переписать, иначе будут битые.
    const base = meta.href.slice(0, meta.href.lastIndexOf("/") + 1);
    for (const img of panel.querySelectorAll("img[src]")) {
      const src = img.getAttribute("src");
      if (!/^(https?:|\/)/.test(src)) img.setAttribute("src", base + src);
    }

    if (panel.querySelector(".mermaid")) {
      const m = (await import("https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs")).default;
      m.initialize({ startOnLoad: false, theme: "dark" });
      await m.run({ nodes: panel.querySelectorAll(".mermaid") });
    }
  } catch (e) {
    $(".reader__body", panel).innerHTML =
      `<div class="banner banner--error">Конспект не загрузился: ${esc(e.message)}</div>`;
  }
}

// ---------------------------------------------------------------- утилиты

const strip = (s) => (s || "").replace(/\r\n/g, "\n").trim();

/**
 * Режим «решаю заново». Включается сбросом прогресса.
 *
 * Без него сброс отменял бы сам себя: решения лежат в файлах курса, и сайт
 * подтянул бы их обратно при следующей загрузке. Поэтому сброс не стирает
 * файлы (это была бы потеря работы), а переводит сайт на заготовки и
 * перестаёт автоматически читать решения с диска, пока режим включён.
 */
const fromScratch = () => store.getUI("fromScratch", false);

/** Код, который реально пойдёт в прогон: правки студента → прошлое решение → заготовка. */
function effectiveCode(task) {
  if (store.hasCode(task.id)) return store.getCode(task.id);
  if (fromScratch()) return task.starter_code;
  return task.reference_solution || task.starter_code;
}

/** Задача всё ещё нетронутая заготовка? */
function isStub(task) {
  return strip(effectiveCode(task)) === strip(task.starter_code);
}

/** Блоки, которые проверяют эту задачу. У build_list своих тестов нет —
 *  его проверяет блок to_list, поэтому гоняем блоки зависимых задач. */
function verifyingBlocks(lesson, task) {
  if (task.has_own_tests) return [task];
  return lesson.tasks.filter(
    (t) => t.has_own_tests && t.needs.includes(task.name)
  );
}

/** Нерешённые задачи, от которых зависит эта. */
function blockers(lesson, task) {
  const names = new Set();
  for (const b of verifyingBlocks(lesson, task)) {
    for (const n of b.needs) names.add(n);
  }
  names.delete(task.name);
  return lesson.tasks.filter((t) => names.has(t.name) && isStub(t));
}

function taskState(task) {
  const s = store.getStatus(task.id);
  if (s.state === "solved") return store.isUnsaved(task.id) ? "unsaved" : "solved";

  // Код совпал с проверенным решением из репозитория — задача решена,
  // откуда бы этот код ни взялся. Прежнее правило («решено в репозитории И
  // в браузере кода нет») ломалось, как только решения подтягивались с диска:
  // код появлялся, и весь прогресс переставал считаться.
  if (!fromScratch() && task.reference_solution &&
      strip(effectiveCode(task)) === strip(task.reference_solution)) {
    return "solved";
  }
  if (s.state === "attempted") return "attempted";
  return "fresh";
}

const STATE_LABEL = {
  fresh: "не начата",
  attempted: "в работе",
  solved: "решена",
  unsaved: "не выгружена",
};

function lessonProgress(lesson) {
  const done = lesson.tasks.filter((t) => ["solved", "unsaved"].includes(taskState(t))).length;
  return { done, total: lesson.tasks.length };
}

const isDone = (task) => ["solved", "unsaved"].includes(taskState(task));

/** Все задачи курса подряд, в порядке модулей и уроков. */
function allTasks() {
  const out = [];
  for (const mod of CONTENT.modules) {
    for (const lid of mod.lessons) {
      const lesson = byLesson.get(lid);
      if (lesson) for (const t of lesson.tasks) out.push({ lesson, task: t });
    }
  }
  return out;
}

/**
 * Следующая нерешённая задача — то, ради чего сюда заходят.
 * Ищем начиная с текущей позиции и с заворотом, чтобы кнопка «дальше»
 * не упиралась в конец урока, когда впереди ещё есть незакрытое.
 */
function nextUnsolved(after = null) {
  const list = allTasks();
  const from = after
    ? list.findIndex((x) => x.task.id === after.id) + 1
    : 0;
  for (let i = 0; i < list.length; i++) {
    const item = list[(from + i) % list.length];
    if (!isDone(item.task)) return item;
  }
  return null;
}

const taskHref = ({ lesson, task }) => `#/l/${lesson.id}/${task.name}`;

// ---------------------------------------------------------------- рантайм

function initRuntime() {
  runtime = new Runtime({ timeoutMs: CONTENT.runtime.timeout_ms });
  const chip = $("#chip");
  const label = $("#chip-label");

  runtime.addEventListener("state", (e) => {
    const d = e.detail;
    chip.dataset.state = d.state;
    if (d.state === "loading") {
      label.textContent = d.phase
        ? "Python: запуск"
        : `Python: ${Math.round((d.progress || 0) * 100)}%`;
    } else if (d.state === "ready") {
      label.textContent = runtime.bootMs
        ? `Python готов (${(runtime.bootMs / 1000).toFixed(1)} с)`
        : "Python готов";
    } else if (d.state === "running") {
      label.textContent = "Выполняется…";
    } else if (d.state === "failed") {
      label.textContent = "Python: ошибка";
    } else {
      label.textContent = "Python: не загружен";
    }
  });
}

// ---------------------------------------------------------------- рендер

function render(html) {
  $("#view").innerHTML = html;
  renderRail();
}

function setCrumbs(parts) {
  // На верхнем уровне крошки повторяли бы активную вкладку — прячем их.
  $("#crumbs").innerHTML = parts.length < 2 ? "" : parts
    .map((p) => (p.href ? `<a href="${p.href}">${esc(p.text)}</a>` : esc(p.text)))
    .join(" / ");
}

/** Теория — самостоятельный раздел, а не приложение к задаче. */
function viewTheoryIndex() {
  setActiveTab("theory");
  setCrumbs([{ text: "Теория" }]);

  const KIND = {
    plain: "объяснение с примерами",
    note: "подробный конспект",
    reference: "шпаргалка с кодом",
  };

  const blocks = CONTENT.modules.map((m) => {
    const items = theoryOf(m.theory);
    if (!items.length) return "";
    const lessonsCount = m.lessons.length;

    const cards = items.map((t) => `
      <a class="theory-card${t.kind === "plain" ? " is-main" : ""}" href="${t.href}">
        <span class="theory-card__icon">${t.kind === "reference" ? "⌘" : "▤"}</span>
        <span class="theory-card__body">
          <span class="theory-card__title">${esc(t.title)}</span>
          <span class="theory-card__kind">${KIND[t.kind] || "конспект"}${
            t.images ? ` · ${t.images} схем` : ""}</span>
        </span>
        <span class="theory-card__go">Читать →</span>
      </a>`).join("");

    return `<section class="module">
      <div class="module__head" style="cursor:default">
        <h2 class="module__title">${esc(m.title)}</h2>
        <span class="module__sub">${esc(m.subtitle)}</span>
      </div>
      <div class="theory-cards" style="margin-top:14px">${cards}</div>
      <div class="theory-topractice">
        <button class="btn btn--ghost" data-href="#/">
          Перейти к задачам этого модуля (${lessonsCount}) →</button>
      </div>
    </section>`;
  }).join("");

  render(`<div class="page-head">
      <div>
        <h1>Теория</h1>
        <p class="muted">Конспекты по модулям. «На пальцах» — с примерами и схемами,
          остальные — как справочник.</p>
      </div>
      <div class="stats">
        <div class="stat"><b>${CONTENT.theory.length}</b><span>материалов</span></div>
      </div>
    </div>
    <div class="modules">${blocks}</div>`);
}

/**
 * Боковая колонка — дерево курса. Она повторяет реальную структуру папок,
 * потому что курс это и есть файлы: drills/06_data_structures/p1_stack.py.
 */
function renderRail() {
  const rail = $("#rail");
  if (!rail) return;

  const hash = location.hash.replace(/^#/, "");
  const open = new Set(store.getUI("railOpen", CONTENT.modules.map((m) => m.id)));

  let html = `<div class="rail__label">курс</div>`;
  for (const m of CONTENT.modules) {
    const lessons = m.lessons.map((id) => byLesson.get(id)).filter(Boolean);
    const done = lessons.reduce((s, l) => s + lessonProgress(l).done, 0);
    const total = lessons.reduce((s, l) => s + lessonProgress(l).total, 0);
    const isOpen = open.has(m.id);
    const full = total && done === total;

    html += `<div class="rail__mod${full ? " is-full" : ""}" data-rail-toggle="${m.id}">
      <span class="rail__caret">${isOpen ? "▾" : "▸"}</span>
      <span class="rail__name">${esc(m.title.replace(/^Модуль\s+/i, "м"))}</span>
      <span class="rail__count">${done}/${total}</span>
    </div>`;

    if (!isOpen) continue;
    for (const l of lessons) {
      const active = hash.startsWith(`/l/${l.id}`);
      html += `<a class="rail__item${active ? " is-active" : ""}"
         data-href="#/l/${l.id}">${esc(l.title)}</a>`;
    }
  }

  html += `<div class="rail__sep"></div>
    <div class="rail__label">теория</div>`;
  for (const t of CONTENT.theory.filter((x) => x.kind === "plain")) {
    html += `<a class="rail__item" data-theory="${t.id}">${esc(t.title)}</a>`;
  }
  html += `<a class="rail__item" data-href="#/theory">все материалы →</a>`;

  rail.innerHTML = html;

  for (const el of rail.querySelectorAll("[data-rail-toggle]")) {
    el.onclick = () => {
      const id = el.dataset.railToggle;
      const set = new Set(store.getUI("railOpen", CONTENT.modules.map((m) => m.id)));
      set.has(id) ? set.delete(id) : set.add(id);
      store.setUI("railOpen", [...set]);
      renderRail();
    };
  }
}

function setActiveTab(which) {
  $("#tab-theory")?.classList.toggle("is-active", which === "theory");
  $("#tab-practice")?.classList.toggle("is-active", which === "practice");
}

function viewMap() {
  setActiveTab("practice");
  setCrumbs([{ text: "Практика" }]);

  const collapsed = new Set(store.getUI("collapsed", []));

  const modules = CONTENT.modules.map((m) => {
    const lessons = m.lessons.map((id) => byLesson.get(id)).filter(Boolean);
    const done = lessons.reduce((s, l) => s + lessonProgress(l).done, 0);
    const total = lessons.reduce((s, l) => s + lessonProgress(l).total, 0);
    const pct = total ? Math.round((done / total) * 100) : 0;
    const isCollapsed = collapsed.has(m.id);

    const rows = lessons.map((l) => {
      const p = lessonProgress(l);
      const full = p.done === p.total;
      return `<div class="lesson-row${full ? " is-done" : ""}" data-href="#/l/${l.id}">
        <span class="lesson-row__title">${esc(l.title)}</span>
        <span class="lesson-row__count">${p.done}/${p.total}</span>
      </div>`;
    }).join("");

    return `<section class="module${isCollapsed ? " is-collapsed" : ""}${
      total && done === total ? " is-full" : ""}">
      <div class="module__head" data-toggle="${m.id}">
        <span class="module__caret">${isCollapsed ? "▸" : "▾"}</span>
        <h2 class="module__title">${esc(m.title)}</h2>
        <span class="module__sub">${esc(m.subtitle)}</span>
        <span class="module__count">${done}/${total}</span>
      </div>
      <div class="bar"><div class="bar__fill" style="width:${pct}%"></div></div>
      <div class="module__body">
        <div class="lessons">${rows}</div>
      </div>
    </section>`;
  }).join("");

  const tasks = CONTENT.lessons.flatMap((l) => l.tasks);
  const totalAll = tasks.length;
  const totalDone = tasks.filter(isDone).length;
  const inProgress = tasks.filter((t) => taskState(t) === "attempted").length;
  const next = nextUnsolved();

  render(`<div class="page-head">
      <div>
        <h1>Практика</h1>
        <p class="muted">Код исполняется прямо в браузере, ничего ставить не нужно.
          Теория — в <a href="#/theory">соседнем разделе</a>.</p>
      </div>
      <div class="stats">
        <div class="stat"><b>${totalDone}</b><span>решено</span></div>
        <div class="stat"><b>${totalAll - totalDone}</b><span>осталось</span></div>
        <div class="stat"><b>${inProgress}</b><span>в работе</span></div>
      </div>
    </div>

    ${next ? `<div class="continue" data-href="${taskHref(next)}">
      <div>
        <div class="continue__label">Продолжить с этого места</div>
        <div class="continue__task">${esc(next.task.title)}</div>
        <div class="continue__where">${esc(next.lesson.title)}</div>
      </div>
      <span class="continue__go">Открыть →</span>
    </div>` : `<div class="banner banner--success">Все задачи курса решены.</div>`}

    <div class="modules">${modules}</div>
    <div class="task-nav">
      <span></span>
      <button class="btn" id="dl-all">Скачать все файлы курса (.zip)</button>
    </div>`);

  $("#dl-all").onclick = downloadAll;

  for (const head of document.querySelectorAll("[data-toggle]")) {
    head.onclick = () => {
      const id = head.dataset.toggle;
      const set = new Set(store.getUI("collapsed", []));
      set.has(id) ? set.delete(id) : set.add(id);
      store.setUI("collapsed", [...set]);
      viewMap();
    };
  }
}

function viewLesson(lesson) {
  const mod = CONTENT.modules.find((m) => m.id === lesson.module);
  setCrumbs([
    { text: "Карта курса", href: "#/" },
    { text: mod ? mod.title : lesson.module },
    { text: lesson.title },
  ]);

  const onlyOpen = store.getUI("onlyOpen", false);
  const shown = onlyOpen ? lesson.tasks.filter((t) => !isDone(t)) : lesson.tasks;

  const rows = shown.map((t) => {
    const st = taskState(t);
    return `<div class="task-row task-row--${st}" data-href="#/l/${lesson.id}/${t.name}">
      <span class="task-row__num">${t.ordinal}</span>
      <span class="task-row__title">${esc(t.title)}</span>
      ${t.kind === "class" ? '<span class="task-row__kind">CLASS</span>' : ""}
      <span class="state state--${st}">${STATE_LABEL[st]}</span>
    </div>`;
  }).join("") || '<div class="empty">В этом блоке всё решено.</div>';

  const p = lessonProgress(lesson);

  render(`<h1>${esc(lesson.title)}</h1>
    <p class="muted">${p.done} из ${p.total} задач · исходник
      <code>${esc(lesson.source_file)}</code></p>

    ${theoryCards(mod ? mod.theory : [])}

    <section class="step">
      <div class="tasks-head">
        <div>
          <div class="step__title">Задачи</div>
          <div class="step__hint">${p.done} из ${p.total} решено</div>
        </div>
        <label class="switch">
          <input type="checkbox" id="only-open" ${onlyOpen ? "checked" : ""}>
          <span>только нерешённые</span>
        </label>
      </div>
      ${lesson.intro_html ? `<div class="lesson-intro desc">${lesson.intro_html}</div>` : ""}
      <div class="tasks">${rows}</div>
    </section>
    <div class="task-nav">
      <button class="btn" data-href="#/">← К карте курса</button>
      <button class="btn" id="dl-lesson">Скачать ${esc(basename(lesson.source_file))}</button>
    </div>`);

  $("#dl-lesson").onclick = () => downloadLesson(lesson);
  $("#only-open").onchange = (e) => {
    store.setUI("onlyOpen", e.target.checked);
    viewLesson(lesson);
  };
}

function viewTask(lesson, task) {
  const mod = CONTENT.modules.find((m) => m.id === lesson.module);
  setCrumbs([
    { text: "Карта курса", href: "#/" },
    { text: mod ? mod.title : lesson.module, href: "#/" },
    { text: lesson.title, href: `#/l/${lesson.id}` },
    { text: task.name },
  ]);

  const idx = lesson.tasks.indexOf(task);
  const prev = lesson.tasks[idx - 1];
  const next = lesson.tasks[idx + 1];

  render(`<div class="task-layout">
    <section class="panel desc">
      <div class="desc__head">
        <span class="panel__title" style="margin:0">Задача ${task.ordinal} из ${lesson.tasks.length}</span>
        ${theoryButton(mod ? mod.theory : [])}
      </div>
      <h3>${esc(task.title)}</h3>
      ${task.description_html}
      ${task.has_own_tests ? "" :
        '<div class="note"><span class="note__label">Замечание</span> ' +
        'у этой задачи нет собственных проверок — она проверяется вместе со следующей.</div>'}
    </section>

    <section class="panel">
      <div class="panel__title">Ваше решение</div>
      <div id="blockers"></div>
      <div class="editor-wrap" id="editor"></div>
      <div class="editor-actions">
        <button class="btn btn--primary" id="run">Проверить <kbd>Ctrl+↵</kbd></button>
        <button class="btn btn--ghost" id="reset">Сбросить к заготовке</button>
        ${task.reference_solution ?
          '<button class="btn btn--ghost" id="show-ref">Моё прежнее решение</button>' : ""}
        <span class="spacer"></span>
        <button class="btn btn--ghost" id="dl">Скачать файл</button>
      </div>
      <div class="results" id="results"></div>
    </section>
  </div>

  <div class="task-nav">
    <button class="btn" ${prev ? `data-href="#/l/${lesson.id}/${prev.name}"` : "disabled"}>← Предыдущая</button>
    <button class="btn" data-href="#/l/${lesson.id}">К списку задач</button>
    <button class="btn" ${next ? `data-href="#/l/${lesson.id}/${next.name}"` : "disabled"}>Следующая →</button>
  </div>`);

  const editor = createEditor($("#editor"), {
    value: effectiveCode(task),
    onChange: (code) => {
      store.setCode(task.id, code);
      if (store.getStatus(task.id).state === "fresh") {
        store.setStatus(task.id, { state: "attempted" });
      }
    },
  });
  editor.refresh();

  // Предупреждаем ДО запуска: иначе студент увидит невнятный TypeError
  // из-за чужой нерешённой задачи, а не из-за своей ошибки.
  const blocked = blockers(lesson, task);
  if (blocked.length) {
    $("#blockers").innerHTML = `<div class="banner banner--warn">
      Эта задача проверяется вместе с
      ${blocked.map((b) => `<code>${esc(b.name)}</code>`).join(", ")} —
      пока они не решены, проверка будет падать не по вашей вине.</div>`;
  }

  $("#run").onclick = () => runTask(lesson, task, editor);
  $("#reset").onclick = () => {
    store.resetCode(task.id);
    editor.setValue(task.reference_solution || task.starter_code);
    editor.clearErrors();
    $("#results").innerHTML = "";
  };
  const refBtn = $("#show-ref");
  if (refBtn) refBtn.onclick = () => editor.setValue(task.reference_solution);
  $("#dl").onclick = () => downloadLesson(lesson);

  // Ctrl+Enter — как в любом редакторе кода: запуск, не отрывая рук.
  currentRun = () => runTask(lesson, task, editor);
  editor.focus();

  if ("requestIdleCallback" in window) requestIdleCallback(() => runtime.preload());
  else setTimeout(() => runtime.preload(), 500);
}

// Что запускает Ctrl+Enter на текущей странице. null — если не на задаче.
let currentRun = null;

// ---------------------------------------------------------------- прогон

async function runTask(lesson, task, editor) {
  const btn = $("#run");
  const out = $("#results");
  btn.disabled = true;
  editor.clearErrors();
  out.innerHTML = '<div class="banner banner--info">Выполняется…</div>';

  const myCode = editor.getValue();
  store.setCode(task.id, myCode);

  const units = lesson.tasks.map((t) => ({
    id: t.id,
    code: t.id === task.id ? myCode : effectiveCode(t),
  }));
  const blocks = verifyingBlocks(lesson, task).map((t) => ({
    task: t.id, code: t.test_source,
  }));

  let report;
  try {
    report = await runtime.run({ prelude: lesson.prelude, units, blocks });
  } catch (err) {
    out.innerHTML = `<div class="banner banner--warn">${esc(err.message)}</div>`;
    btn.disabled = false;
    return;
  }
  btn.disabled = false;

  renderReport(out, report, lesson, task, editor, blocks);
}

function renderReport(out, report, lesson, task, editor, blocks) {
  const parts = [];

  if (report.prelude_error) {
    parts.push(`<div class="banner banner--error">Не удалось подготовить урок:
      ${esc(report.prelude_error.msg || "")}</div>`);
  }

  // Ошибка компиляции/исполнения в самом коде студента — показываем первой
  // и подсвечиваем строку прямо в редакторе.
  const myUnit = report.units.find((u) => u.task === task.id);
  if (myUnit) {
    const e = myUnit.error;
    if (e.kind === "syntax") {
      parts.push(`<div class="banner banner--error">
        <b>Синтаксическая ошибка</b>, строка ${e.lineno}: ${esc(e.msg)}
        ${e.text ? `<br><code>${esc(e.text)}</code>` : ""}</div>`);
      editor.markError(e.lineno, e.msg);
    } else {
      parts.push(`<div class="banner banner--error">
        <b>${esc(e.type)}</b>: ${esc(e.msg)}</div>`);
      if (e.at) editor.markError(e.at.lineno, e.msg);
    }
  }

  const otherUnits = report.units.filter((u) => u.task !== task.id);
  if (otherUnits.length) {
    parts.push(`<div class="banner banner--warn">Не запускается код соседних задач:
      ${otherUnits.map((u) => `<code>${esc(u.task.split("/").pop())}</code>`).join(", ")}</div>`);
  }

  let allChecks = 0, passed = 0, crashed = false;
  for (const b of report.blocks) {
    for (const c of b.checks) {
      allChecks++;
      if (c.ok) passed++;
      parts.push(`<div class="result result--${c.ok ? "ok" : "fail"}">
        <span class="result__mark">${c.ok ? "OK" : "FAIL"}</span>
        <span class="result__body">
          <span class="result__label">${esc(c.label || "проверка")}</span>
          <span class="result__detail"> → ${esc(c.actual)}${
            c.ok ? "" : ` (ожидалось ${esc(c.expected)})`}</span>
        </span></div>`);
    }
    if (b.error) {
      crashed = true;
      const e = b.error;
      const where = e.at ? ` (строка ${e.at.lineno} вашего кода)` : "";
      parts.push(`<div class="banner banner--error">
        Проверка оборвалась: <b>${esc(e.type || e.kind)}</b> ${esc(e.msg || "")}${where}</div>`);
      if (e.at) editor.markError(e.at.lineno, e.msg);
    }
  }

  // Решено — только если отработали ВСЕ ожидаемые проверки и все зелёные.
  // Иначе «первый check прошёл, на втором вылетело» засчиталось бы как успех.
  const expected = blocks.reduce((s, b) => {
    const t = lesson.tasks.find((x) => x.id === b.task);
    return s + (t ? t.expected_checks : 0);
  }, 0);
  const solved = !crashed && !myUnit && allChecks === expected && passed === expected && expected > 0;

  if (solved) {
    const inFile = strip(effectiveCode(task)) === strip(task.reference_solution || "");
    store.setStatus(task.id, { state: "solved", pass: passed, fail: 0, downloaded: inFile });
    scheduleWrite(lesson.id);
    const next = nextUnsolved(task);
    // Про запись в файл ничего не утверждаем: она идёт следом и может не
    // пройти (например, браузер ждёт подтверждения доступа к папке).
    // Настоящий результат показывает индикатор в шапке.
    const hint = fs.isConnected()
      ? ""
      : (inFile ? "" : " Чтобы решение попало в файлы курса, подключите папку или скачайте файл.");
    parts.unshift(`<div class="banner banner--success solved-banner">
      <div><b>Задача решена</b> — ${passed}/${expected} проверок.${hint}</div>
      ${next ? `<button class="btn btn--primary" data-href="${taskHref(next)}">
        Дальше: ${esc(next.task.name)} →</button>` : ""}
    </div>`);
  } else if (allChecks) {
    store.setStatus(task.id, { state: "attempted", pass: passed, fail: allChecks - passed });
  }

  if (report.stdout && report.stdout.trim()) {
    parts.push(`<div class="panel__title" style="margin-top:14px">Вывод print()</div>
      <div class="stdout">${esc(report.stdout)}</div>`);
  }

  out.innerHTML = parts.join("") || '<div class="banner banner--warn">Проверок не выполнилось.</div>';
}

// ---------------------------------------------------------------- выгрузка

function downloadLesson(lesson) {
  const codeMap = {};
  const ids = [];
  for (const t of lesson.tasks) {
    if (store.hasCode(t.id)) {
      codeMap[t.id] = store.getCode(t.id);
      ids.push(t.id);
    }
  }
  downloadText(basename(lesson.source_file), buildFile(lesson, codeMap));
  store.markDownloaded(ids);
  toast(`Скачан ${basename(lesson.source_file)} — положите его в python_course/${
    lesson.source_file.includes("/") ? lesson.source_file.split("/").slice(0, -1).join("/") + "/" : ""}`);
}

// ------------------------------------------------- папка курса на диске

let writeTimer = null;
const pendingWrites = new Set();

function setFsStatus(text, kind = "") {
  const el = $("#fs-status");
  if (el) {
    el.textContent = text;
    el.dataset.kind = kind;
  }
}

/** Записать файлы уроков, которых коснулись правки. */
async function flushWrites() {
  if (!fs.isConnected() || !pendingWrites.size) return;
  const ids = [...pendingWrites];
  pendingWrites.clear();
  setFsStatus("записываю…", "busy");
  try {
    for (const lessonId of ids) {
      const lesson = byLesson.get(lessonId);
      const codeMap = {};
      for (const t of lesson.tasks) {
        if (store.hasCode(t.id)) codeMap[t.id] = store.getCode(t.id);
      }
      await fs.writeFile(lesson.source_file, buildFile(lesson, codeMap));
      store.markDownloaded(lesson.tasks.map((t) => t.id));
    }
    setFsStatus(`записано в файлы ${new Date().toLocaleTimeString().slice(0, 5)}`, "ok");
  } catch (e) {
    ids.forEach((id) => pendingWrites.add(id));
    // Разрешение на папку браузер отзывает между сеансами — это не ошибка,
    // а ожидаемое состояние, и чинится одним кликом.
    if (e.name === "NotAllowedError" || e.name === "SecurityError") {
      needsGrant();
    } else {
      setFsStatus("не записалось", "error");
      toast(`Не удалось записать в файлы: ${e.message}`);
    }
  }
}

/** Показать, что нужен клик для подтверждения доступа, и дать его сделать. */
function needsGrant() {
  const el = $("#fs-status");
  if (!el) return;
  setFsStatus("подтвердить доступ к папке →", "pending");
  el.classList.add("is-action");
  el.onclick = async () => {
    if (await fs.regrant()) {
      el.classList.remove("is-action");
      el.onclick = null;
      setFsStatus(`папка: ${fs.folderName()}`, "ok");
      await importFromDisk({ silent: true });
      await flushWrites();
      route();
    } else {
      setFsStatus("доступ не дан", "error");
    }
  };
}

function scheduleWrite(lessonId) {
  if (!fs.isConnected()) return;
  pendingWrites.add(lessonId);
  setFsStatus("есть незаписанное", "pending");
  clearTimeout(writeTimer);
  writeTimer = setTimeout(flushWrites, 1200);
}

/**
 * Прочитать решения из файлов на диске и влить в хранилище.
 * Файл главнее там, где в нём есть настоящее решение; там, где на диске
 * всё ещё заготовка, сохраняется несохранённая работа из браузера.
 */
async function importFromDisk({ silent = false, force = false } = {}) {
  // В режиме «решаю заново» автоматический импорт отменил бы сброс.
  // По явной кнопке (force) — импортируем и выходим из режима.
  if (fromScratch() && !force) return 0;
  if (force) store.setUI("fromScratch", false);

  let imported = 0, unreadable = [];
  for (const lesson of CONTENT.lessons) {
    let text;
    try {
      text = await fs.readFile(lesson.source_file);
    } catch {
      continue;
    }
    if (text === null) continue;

    const found = extractSolutions(lesson, text);
    if (!found) {
      unreadable.push(lesson.source_file);
      continue;
    }
    for (const task of lesson.tasks) {
      const onDisk = found[task.id];
      if (onDisk === undefined) continue;
      if (strip(onDisk) === strip(task.starter_code)) continue;  // на диске заготовка
      if (strip(onDisk) === strip(store.getCode(task.id, ""))) continue;
      store.setCode(task.id, onDisk);
      store.setStatus(task.id, { downloaded: true });
      imported++;
    }
  }
  store.flush();
  if (!silent) {
    const extra = unreadable.length
      ? ` Не удалось разобрать: ${unreadable.join(", ")} — формат файла изменён вручную.`
      : "";
    toast(`Подтянуто решений из файлов: ${imported}.${extra}`);
  }
  return imported;
}

async function openFolderPanel() {
  const wrap = document.createElement("div");
  wrap.className = "modal";
  const state = fs.isConnected() ? "подключена" : "не подключена";

  wrap.innerHTML = `<div class="modal__box">
    <div class="modal__title">Настройки</div>
    <div class="panel__title" style="margin-bottom:10px">Папка курса</div>
    <p class="muted">Сайт может писать решения прямо в <code>.py</code>-файлы курса
      на диске. Тогда прогресс не зависит от браузера, а шаг «скачать и
      переложить» не нужен: решения сразу там, где их ждут <code>python</code> и
      <code>git</code>.</p>

    ${fs.supported() ? "" : `<div class="banner banner--error">
      Этот браузер не умеет записывать в файлы (нужен Chrome или Edge на компьютере).
      Остаются «скачать» и «экспорт прогресса».</div>`}

    <div class="banner banner--info">
      Состояние: <b>${state}</b>${fs.folderName() ? ` — <code>${esc(fs.folderName())}</code>` : ""}.
      Выбирать нужно папку <code>python_course</code> — ту, где лежат
      <code>drills/</code> и <code>docs/</code>.
    </div>

    <div class="editor-actions">
      <button class="btn btn--primary" id="fs-pick"
        ${fs.supported() ? "" : "disabled"}>Выбрать папку</button>
      <button class="btn" id="fs-import">Подтянуть решения из файлов</button>
      <button class="btn" id="fs-write">Записать всё сейчас</button>
      <button class="btn btn--ghost" id="fs-forget">Отключить папку</button>
    </div>

    <div class="panel__title" style="margin:22px 0 10px">Прогресс</div>
    <div class="editor-actions">
      <button class="btn" id="pr-export">Сохранить в файл</button>
      <button class="btn" id="pr-import">Восстановить из файла</button>
      <span class="spacer"></span>
      <button class="btn" id="pr-reset">Сбросить прогресс…</button>
      <button class="btn btn--ghost" id="fs-close">Закрыть</button>
    </div>
    <div id="fs-result"></div>
  </div>`;

  document.body.appendChild(wrap);
  const close = () => wrap.remove();
  wrap.addEventListener("click", (e) => { if (e.target === wrap) close(); });
  $("#fs-close", wrap).onclick = close;

  const say = (html, kind = "info") => {
    $("#fs-result", wrap).innerHTML = `<div class="banner banner--${kind}">${html}</div>`;
  };

  $("#fs-pick", wrap).onclick = async () => {
    try {
      const name = await fs.connect();
      // Проверяем, что это действительно курс, иначе сайт молча создаст
      // пустое дерево drills/… в случайной папке.
      const sample = CONTENT.lessons[0].source_file;
      if (!(await fs.looksLikeCourse(sample))) {
        await fs.forget();
        say(`В папке <code>${esc(name)}</code> нет <code>${esc(sample)}</code> — ` +
            `похоже, выбрана не та папка. Нужна <code>python_course</code>.`, "error");
        return;
      }
      setFsStatus(`папка: ${name}`, "ok");
      const n = await importFromDisk({ silent: true });
      say(`Подключена <code>${esc(name)}</code>. Подтянуто решений из файлов: ${n}. ` +
          `Дальше запись идёт сама после каждой решённой задачи.`, "success");
      route();
    } catch (e) {
      if (e.name === "AbortError") return;     // просто закрыл диалог выбора
      say(esc(e.message), "error");
    }
  };

  $("#fs-import", wrap).onclick = async () => {
    if (!fs.isConnected()) return say("Сначала выберите папку.", "warn");
    const n = await importFromDisk({ silent: true, force: true });
    say(`Подтянуто решений: ${n}.`, "success");
    route();
  };

  $("#fs-write", wrap).onclick = async () => {
    if (!fs.isConnected()) return say("Сначала выберите папку.", "warn");
    CONTENT.lessons.forEach((l) => pendingWrites.add(l.id));
    await flushWrites();
    say("Все файлы курса перезаписаны текущими решениями.", "success");
    route();
  };

  $("#fs-forget", wrap).onclick = async () => {
    await fs.forget();
    setFsStatus("папка не подключена", "");
    say("Папка отключена. Решения остаются в браузере и в уже записанных файлах.", "info");
  };

  $("#pr-export", wrap).onclick = () =>
    downloadText("pycourse-progress.json", store.exportJSON());

  $("#pr-import", wrap).onclick = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/json,.json";
    input.onchange = async () => {
      const file = input.files[0];
      if (!file) return;
      try {
        const n = store.importJSON(await file.text());
        say(`Восстановлено решений: ${n}.`, "success");
        route();
      } catch (err) {
        say(`Не удалось прочитать файл: ${esc(err.message)}`, "error");
      }
    };
    input.click();
  };

  $("#pr-reset", wrap).onclick = () => confirmReset(say);
}

/**
 * Сброс прогресса. Два шага намеренно: действие необратимое, а решения
 * могли не уехать в файлы. Поэтому сначала показываем, что именно пропадёт,
 * и предлагаем сохранить.
 */
function confirmReset(say) {
  const tasks = allTasks();
  const inBrowser = tasks.filter(({ task }) => store.hasCode(task.id)).length;
  const unsaved = tasks.filter(({ task }) => store.isUnsaved(task.id)).length;

  say(`<b>Сбросить прогресс?</b> Из браузера будут стёрты решения
    <b>${inBrowser}</b> задач и все отметки.
    ${unsaved ? `Из них <b>${unsaved}</b> ещё не выгружены в файлы курса —
      после сброса их будет не вернуть.` : ""}
    Файлы <code>.py</code> на диске <b>не трогаются</b>: если папка подключена,
    решения подтянутся из них обратно.
    <div class="editor-actions" style="margin-top:10px">
      <button class="btn" id="reset-save">Сначала сохранить в файл</button>
      <button class="btn btn--primary" id="reset-yes">Да, сбросить</button>
    </div>`, "warn");

  $("#reset-save").onclick = () =>
    downloadText("pycourse-progress.json", store.exportJSON());

  $("#reset-yes").onclick = () => {
    store.reset();
    store.setUI("fromScratch", true);
    say(`Прогресс сброшен, задачи открыты с заготовок.
      Файлы курса не тронуты — чтобы вернуть прежние решения, нажмите
      «Подтянуть решения из файлов».`, "success");
    route();
  };
}

/** Весь курс одним архивом — пути сохранены, распаковывается поверх python_course/. */
function downloadAll() {
  const files = [];
  const ids = [];
  for (const lesson of CONTENT.lessons) {
    const codeMap = {};
    for (const t of lesson.tasks) {
      if (store.hasCode(t.id)) {
        codeMap[t.id] = store.getCode(t.id);
        ids.push(t.id);
      }
    }
    files.push({ name: lesson.source_file, text: buildFile(lesson, codeMap) });
  }
  downloadBlob("python_course-solutions.zip", makeZip(files));
  store.markDownloaded(ids);
  toast(`Архив собран: ${files.length} файлов. Распакуйте поверх папки python_course/.`);
}

// ---------------------------------------------------------------- поиск

/** Ctrl+K — прыжок к любой из 129 задач без кликанья по урокам. */
function openSearch() {
  if ($(".search")) return;
  const items = allTasks();

  const wrap = document.createElement("div");
  wrap.className = "modal search";
  wrap.innerHTML = `<div class="modal__box search__box">
    <input id="q" class="search__input" placeholder="Название задачи или урока…"
           autocomplete="off" spellcheck="false">
    <div class="search__list" id="hits"></div>
    <div class="search__hint">↑↓ — выбор · ↵ — открыть · Esc — закрыть</div>
  </div>`;
  document.body.appendChild(wrap);

  const input = $("#q", wrap);
  const list = $("#hits", wrap);
  let filtered = [];
  let active = 0;

  function draw() {
    const q = input.value.trim().toLowerCase();
    filtered = (q
      ? items.filter(({ lesson, task }) =>
          task.name.toLowerCase().includes(q) ||
          task.title.toLowerCase().includes(q) ||
          lesson.title.toLowerCase().includes(q))
      : items.filter(({ task }) => !isDone(task))
    ).slice(0, 40);

    if (active >= filtered.length) active = Math.max(0, filtered.length - 1);

    list.innerHTML = filtered.length
      ? filtered.map(({ lesson, task }, i) => {
          const st = taskState(task);
          return `<div class="search__hit${i === active ? " is-active" : ""}" data-i="${i}">
            <span class="state state--${st}"></span>
            <span class="search__name">${esc(task.name)}</span>
            <span class="search__where">${esc(lesson.title)}</span>
          </div>`;
        }).join("")
      : `<div class="empty">Ничего не нашлось</div>`;

    for (const el of list.querySelectorAll(".search__hit")) {
      el.onclick = () => go(Number(el.dataset.i));
    }
  }

  function go(i) {
    const item = filtered[i];
    if (!item) return;
    wrap.remove();
    location.hash = taskHref(item);
  }

  input.oninput = () => { active = 0; draw(); };
  input.onkeydown = (e) => {
    if (e.key === "ArrowDown") { active = Math.min(active + 1, filtered.length - 1); draw(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { active = Math.max(active - 1, 0); draw(); e.preventDefault(); }
    else if (e.key === "Enter") { go(active); e.preventDefault(); }
  };
  wrap.addEventListener("click", (e) => { if (e.target === wrap) wrap.remove(); });

  draw();
  input.focus();
}

let toastTimer = null;
function toast(text) {
  let el = $("#toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "toast";
    el.className = "toast";
    document.body.appendChild(el);
  }
  el.textContent = text;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.remove(), 5000);
}

// ---------------------------------------------------------------- роутер

function route() {
  const hash = location.hash.replace(/^#/, "") || "/";
  const parts = hash.split("/").filter(Boolean);
  currentRun = null;           // Ctrl+Enter действует только на странице задачи
  window.scrollTo(0, 0);

  if (parts[0] === "theory") return viewTheoryIndex();
  if (parts[0] !== "l") return viewMap();
  setActiveTab("practice");

  const lesson = byLesson.get(parts[1]);
  if (!lesson) return viewMap();
  if (!parts[2]) return viewLesson(lesson);

  const task = lesson.tasks.find((t) => t.name === parts[2]);
  if (!task) return viewLesson(lesson);
  viewTask(lesson, task);
}

// делегирование: любой элемент с data-href работает как ссылка
document.addEventListener("click", (e) => {
  const theory = e.target.closest("[data-theory]");
  if (theory) {
    e.stopPropagation();
    openTheory(theory.dataset.theory);
    return;
  }
  const el = e.target.closest("[data-href]");
  if (el && !el.disabled) location.hash = el.dataset.href;
});

document.addEventListener("keydown", (e) => {
  // Ctrl/Cmd+Enter — проверить. Работает и из редактора, поэтому вешаем
  // на документ, а не на кнопку.
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && currentRun) {
    e.preventDefault();
    currentRun();
    return;
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    openSearch();
    return;
  }
  if (e.key === "Escape") {
    const reader = $(".reader");
    if (reader) {
      reader.remove();
      document.body.classList.remove("has-reader");
      return;
    }
    const modal = $(".modal");
    if (modal) modal.remove();
  }
});

document.addEventListener("storage-full", () => {
  toast("В браузере кончилось место — скачайте решения, чтобы не потерять их.");
});

// ---------------------------------------------------------------- старт

async function main() {
  try {
    // no-cache, а не default: content.json меняется на каждой пересборке,
    // и без ревалидации браузер показывал бы прошлую версию курса.
    CONTENT = await (await fetch("./content.json", { cache: "no-cache" })).json();
  } catch (e) {
    render(`<div class="banner banner--error">Не удалось загрузить content.json: ${esc(e.message)}</div>`);
    return;
  }
  for (const l of CONTENT.lessons) byLesson.set(l.id, l);
  for (const t of CONTENT.theory || []) byTheory.set(t.id, t);

  initRuntime();

  $("#settings").onclick = openFolderPanel;
  $("#search").onclick = openSearch;

  window.addEventListener("hashchange", route);
  route();

  // Папку из прошлого сеанса восстанавливаем после первой отрисовки.
  if (!fs.supported()) {
    setFsStatus("запись в файлы недоступна", "");
  } else {
    fs.restore().then(async (state) => {
      if (state === "ready") {
        setFsStatus(`папка: ${fs.folderName()}`, "ok");
        await importFromDisk({ silent: true });
        route();
      } else if (state === "prompt") {
        // Разрешение даётся только по клику пользователя — сами не можем.
        needsGrant();
      } else {
        setFsStatus("папка не подключена", "");
      }
    });
  }

  // Незаписанное не должно потеряться при закрытии вкладки.
  window.addEventListener("pagehide", () => {
    if (pendingWrites.size) sessionStorage.setItem("pycourse:dirty", "1");
  });
}

main();
