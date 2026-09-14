// Приложение курса: карта → урок → задача.
// Hash-роутер, потому что сайт живёт на подпути GitHub Pages и сервера нет.

import { Runtime } from "./runtime.js";
import { store } from "./storage.js";
import { createEditor } from "./editor.js";
import { buildFile, downloadText, basename } from "./download.js";
import { makeZip, downloadBlob } from "./zip.js";
import * as gh from "./github-sync.js";

const $ = (sel, root = document) => root.querySelector(sel);
const esc = (s) => String(s).replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let CONTENT = null;
let runtime = null;
const byLesson = new Map();
const byTheory = new Map();

function theoryLinks(ids, { compact = false } = {}) {
  const items = (ids || []).map((id) => byTheory.get(id)).filter(Boolean);
  if (!items.length) return "";
  const links = items.map((t) =>
    `<a class="theory-link" href="${t.href}" target="_blank" rel="noopener">
       <span class="theory-link__icon">${t.kind === "reference" ? "⌘" : "▤"}</span>
       ${esc(t.title)}</a>`).join("");
  return compact
    ? `<div class="theory-row">${links}</div>`
    : `<div class="theory-row"><span class="theory-row__label">Теория</span>${links}</div>`;
}

// ---------------------------------------------------------------- утилиты

const strip = (s) => (s || "").replace(/\r\n/g, "\n").trim();

/** Код, который реально пойдёт в прогон: правки студента → его прошлое решение → заготовка. */
function effectiveCode(task) {
  if (store.hasCode(task.id)) return store.getCode(task.id);
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
  if (s.state === "attempted") return "attempted";
  if (task.solved_in_repo && !store.hasCode(task.id)) return "solved";
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
}

function setCrumbs(parts) {
  $("#crumbs").innerHTML = parts
    .map((p) => (p.href ? `<a href="${p.href}">${esc(p.text)}</a>` : esc(p.text)))
    .join(" › ");
}

function viewMap() {
  setCrumbs([{ text: "Карта курса" }]);

  const modules = CONTENT.modules.map((m) => {
    const lessons = m.lessons.map((id) => byLesson.get(id)).filter(Boolean);
    const done = lessons.reduce((s, l) => s + lessonProgress(l).done, 0);
    const total = lessons.reduce((s, l) => s + lessonProgress(l).total, 0);
    const pct = total ? Math.round((done / total) * 100) : 0;

    const rows = lessons.map((l) => {
      const p = lessonProgress(l);
      return `<div class="lesson-row" data-href="#/l/${l.id}">
        <span class="lesson-row__title">${esc(l.title)}</span>
        <span class="lesson-row__count">${p.done}/${p.total}</span>
      </div>`;
    }).join("");

    return `<section class="card module">
      <div class="module__head">
        <h2 class="module__title">${esc(m.title)}</h2>
        <span class="module__sub">${esc(m.subtitle)}</span>
      </div>
      <div class="bar"><div class="bar__fill" style="width:${pct}%"></div></div>
      <div class="muted">${done} из ${total} задач</div>
      ${theoryLinks(m.theory)}
      <div class="lessons">${rows}</div>
    </section>`;
  }).join("");

  const totalDone = CONTENT.lessons.reduce((s, l) => s + lessonProgress(l).done, 0);
  const totalAll = CONTENT.lessons.reduce((s, l) => s + lessonProgress(l).total, 0);

  const unsaved = CONTENT.lessons
    .flatMap((l) => l.tasks)
    .filter((t) => store.isUnsaved(t.id)).length;

  render(`<h1>Курс Python</h1>
    <p class="muted">Решено ${totalDone} из ${totalAll} задач. Код исполняется прямо в браузере.</p>
    ${unsaved ? `<div class="banner banner--warn" style="margin-top:14px">
      Решено в браузере, но ещё не выгружено в файлы курса: <b>${unsaved}</b>.
      Прогресс живёт в localStorage — чистка браузера его сотрёт.</div>` : ""}
    <div class="modules" style="margin-top:20px">${modules}</div>
    <div class="task-nav">
      <span></span>
      <button class="btn" id="dl-all">Скачать все файлы курса (.zip)</button>
    </div>`);

  $("#dl-all").onclick = downloadAll;
}

function viewLesson(lesson) {
  const mod = CONTENT.modules.find((m) => m.id === lesson.module);
  setCrumbs([
    { text: "Карта курса", href: "#/" },
    { text: mod ? mod.title : lesson.module },
    { text: lesson.title },
  ]);

  const rows = lesson.tasks.map((t) => {
    const st = taskState(t);
    return `<div class="task-row" data-href="#/l/${lesson.id}/${t.name}">
      <span class="task-row__num">${t.ordinal}</span>
      <span class="task-row__title">${esc(t.title)}</span>
      ${t.kind === "class" ? '<span class="task-row__kind">CLASS</span>' : ""}
      <span class="state state--${st}">${STATE_LABEL[st]}</span>
    </div>`;
  }).join("");

  const p = lessonProgress(lesson);

  render(`<h1>${esc(lesson.title)}</h1>
    <p class="muted">${p.done} из ${p.total} задач · исходник
      <code>${esc(lesson.source_file)}</code></p>
    ${theoryLinks(mod ? mod.theory : [])}
    ${lesson.intro_html ? `<div class="card panel" style="margin:16px 0">
        <div class="panel__title">Про этот блок</div>
        <div class="desc">${lesson.intro_html}</div>
      </div>` : ""}
    <h2>Задачи</h2>
    <div class="tasks">${rows}</div>
    <div class="task-nav">
      <button class="btn" data-href="#/">← К карте курса</button>
      <button class="btn" id="dl-lesson">Скачать ${esc(basename(lesson.source_file))}</button>
    </div>`);

  $("#dl-lesson").onclick = () => downloadLesson(lesson);
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
    <section class="card panel desc">
      <div class="panel__title">Задача ${task.ordinal} из ${lesson.tasks.length}</div>
      <h3>${esc(task.title)}</h3>
      ${task.description_html}
      ${task.has_own_tests ? "" :
        '<div class="note"><span class="note__label">Замечание</span> ' +
        'у этой задачи нет собственных проверок — она проверяется вместе со следующей.</div>'}
      ${theoryLinks(mod ? mod.theory : [])}
    </section>

    <section class="card panel">
      <div class="panel__title">Ваше решение</div>
      <div id="blockers"></div>
      <div class="editor-wrap" id="editor"></div>
      <div class="editor-actions">
        <button class="btn btn--primary" id="run">Проверить</button>
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

  if ("requestIdleCallback" in window) requestIdleCallback(() => runtime.preload());
  else setTimeout(() => runtime.preload(), 500);
}

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
    scheduleSync();
    parts.unshift(`<div class="banner banner--success"><b>Задача решена</b> — ${passed}/${expected} проверок.${
      inFile ? "" : " Не забудьте скачать файл, чтобы решение попало в курс."}</div>`);
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

// ---------------------------------------------------------------- синхронизация

let syncTimer = null;
let syncing = false;

function solvedCount() {
  return CONTENT.lessons.flatMap((l) => l.tasks)
    .filter((t) => ["solved", "unsaved"].includes(taskState(t))).length;
}

function setSyncStatus(text, kind = "") {
  const el = $("#sync-status");
  if (el) {
    el.textContent = text;
    el.dataset.kind = kind;
  }
}

/** Отправить прогресс в репозиторий. Дебаунс, чтобы не коммитить на каждый чих. */
function scheduleSync() {
  if (!gh.tokenStore.has()) return;
  clearTimeout(syncTimer);
  setSyncStatus("изменения не сохранены", "pending");
  syncTimer = setTimeout(() => syncNow(true), 4000);
}

async function syncNow(quiet = false) {
  if (!gh.tokenStore.has()) {
    if (!quiet) toast("Сначала подключите GitHub — кнопка «Синхронизация»");
    return;
  }
  if (syncing) return;
  syncing = true;
  setSyncStatus("сохраняю…", "busy");
  try {
    store.flush();
    const payload = {
      ...store.snapshot(),
      solved: solvedCount(),
      updated: new Date().toISOString(),
    };
    const saved = await gh.saveProgress(payload);
    // saveProgress мог вернуть результат слияния с чужой правкой — принимаем его.
    if (saved !== payload) {
      store.applyMerged(saved);
      route();
    }
    setSyncStatus(`сохранено ${new Date().toLocaleTimeString().slice(0, 5)}`, "ok");
  } catch (e) {
    setSyncStatus("ошибка синхронизации", "error");
    toast(`Синхронизация не удалась: ${e.message}`);
  } finally {
    syncing = false;
  }
}

/** Подтянуть прогресс из репозитория и слить с локальным. */
async function pullProgress({ silent = true } = {}) {
  try {
    const remote = await gh.loadProgress();
    if (!remote) return;
    const merged = gh.mergeProgress(store.snapshot(), remote);
    store.applyMerged(merged);
    if (!silent) toast("Прогресс подтянут из репозитория");
    return true;
  } catch (e) {
    if (!silent) toast(`Не удалось прочитать прогресс: ${e.message}`);
  }
}

/** Записать решения прямо в .py-файлы курса в репозитории. */
async function pushSolutions() {
  if (!gh.tokenStore.has()) {
    toast("Сначала подключите GitHub — кнопка «Синхронизация»");
    return;
  }
  setSyncStatus("пишу файлы курса…", "busy");
  let written = 0, unchanged = 0;
  try {
    for (const lesson of CONTENT.lessons) {
      const codeMap = {};
      let touched = false;
      for (const t of lesson.tasks) {
        if (store.hasCode(t.id)) {
          codeMap[t.id] = store.getCode(t.id);
          touched = true;
        }
      }
      if (!touched) continue;
      const result = await gh.pushCourseFile(lesson.source_file,
                                             buildFile(lesson, codeMap));
      if (result === "written") written++;
      else unchanged++;
      store.markDownloaded(lesson.tasks.map((t) => t.id));
    }
    setSyncStatus("файлы курса обновлены", "ok");
    toast(`Записано файлов: ${written}${unchanged ? `, без изменений: ${unchanged}` : ""}. ` +
          `Не забудьте git pull локально.`);
    route();
  } catch (e) {
    setSyncStatus("ошибка записи", "error");
    toast(`Не удалось записать: ${e.message}`);
  }
}

function openSyncPanel() {
  const wrap = document.createElement("div");
  wrap.className = "modal";
  wrap.innerHTML = `<div class="modal__box">
    <div class="modal__title">Синхронизация с GitHub</div>
    <p class="muted">Прогресс хранится в <code>docs/progress.json</code> репозитория
      <code>${gh.OWNER || "akim-dev3"}/python-course</code> — он доступен с любого
      устройства и не пропадёт при чистке браузера.</p>

    <div class="banner banner--warn">
      Нужен <b>fine-grained</b> токен, выданный на <b>один этот репозиторий</b>
      с правом <b>Contents: read and write</b> и со сроком годности.
      Токен лежит в этом браузере, а страница публичная — классический токен
      с полным доступом сюда вставлять нельзя.
      <div style="margin-top:8px">
        <a href="https://github.com/settings/personal-access-tokens/new"
           target="_blank" rel="noopener">Создать такой токен →</a>
      </div>
    </div>

    <label class="field">
      <span>Токен</span>
      <input type="password" id="gh-token" placeholder="github_pat_…"
             autocomplete="off" spellcheck="false">
    </label>

    <div class="editor-actions">
      <button class="btn btn--primary" id="gh-save">Подключить</button>
      <button class="btn" id="gh-pull">Загрузить прогресс</button>
      <button class="btn" id="gh-push">Записать решения в файлы курса</button>
      <span class="spacer"></span>
      <button class="btn btn--ghost" id="gh-forget">Забыть токен</button>
      <button class="btn btn--ghost" id="gh-close">Закрыть</button>
    </div>
    <div id="gh-result"></div>
  </div>`;

  document.body.appendChild(wrap);
  const close = () => wrap.remove();
  wrap.addEventListener("click", (e) => { if (e.target === wrap) close(); });
  $("#gh-close", wrap).onclick = close;
  $("#gh-token", wrap).value = gh.tokenStore.get();

  const say = (html, kind = "info") => {
    $("#gh-result", wrap).innerHTML = `<div class="banner banner--${kind}">${html}</div>`;
  };

  $("#gh-save", wrap).onclick = async () => {
    gh.tokenStore.set($("#gh-token", wrap).value);
    say("Проверяю доступ…");
    try {
      const info = await gh.checkAccess();
      if (!info.canWrite) {
        say("Токен читает репозиторий, но не может писать. " +
            "Нужно право <b>Contents: read and write</b>.", "error");
        return;
      }
      say(`Подключено к <code>${esc(info.repo)}</code>. Прогресс будет ` +
          `сохраняться автоматически.`, "success");
      setSyncStatus("подключено", "ok");
      await syncNow(true);
    } catch (e) {
      say(esc(e.message), "error");
    }
  };

  $("#gh-pull", wrap).onclick = async () => {
    say("Загружаю…");
    const ok = await pullProgress({ silent: false });
    say(ok ? "Прогресс загружен и слит с локальным." : "Сохранённого прогресса пока нет.",
        ok ? "success" : "warn");
    route();
  };

  $("#gh-push", wrap).onclick = async () => {
    say("Пишу файлы курса… это создаст коммиты.");
    await pushSolutions();
    say("Готово. Не забудьте <code>git pull</code> в локальной папке курса.", "success");
  };

  $("#gh-forget", wrap).onclick = () => {
    gh.tokenStore.set("");
    $("#gh-token", wrap).value = "";
    setSyncStatus("не подключено", "");
    say("Токен удалён из браузера.", "info");
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

  if (parts[0] !== "l") return viewMap();

  const lesson = byLesson.get(parts[1]);
  if (!lesson) return viewMap();
  if (!parts[2]) return viewLesson(lesson);

  const task = lesson.tasks.find((t) => t.name === parts[2]);
  if (!task) return viewLesson(lesson);
  viewTask(lesson, task);
}

// делегирование: любой элемент с data-href работает как ссылка
document.addEventListener("click", (e) => {
  const el = e.target.closest("[data-href]");
  if (el && !el.disabled) location.hash = el.dataset.href;
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

  $("#export").onclick = () =>
    downloadText("pycourse-progress.json", store.exportJSON());

  $("#import").onclick = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/json,.json";
    input.onchange = async () => {
      const file = input.files[0];
      if (!file) return;
      try {
        const n = store.importJSON(await file.text());
        toast(`Импортировано решений: ${n}`);
        route();
      } catch (err) {
        toast(`Импорт не удался: ${err.message}`);
      }
    };
    input.click();
  };

  $("#sync").onclick = openSyncPanel;

  window.addEventListener("hashchange", route);
  route();

  // Прогресс из репозитория подтягиваем после первой отрисовки, чтобы страница
  // не ждала сеть. Если он новее локального — слияние и перерисовка.
  if (gh.tokenStore.has()) setSyncStatus("подключено", "ok");
  pullProgress().then((changed) => {
    if (changed) route();
  });

  // На закрытии вкладки авторизованный запрос уже не успеет — браузер его
  // оборвёт. Поэтому страховкой служит localStorage (он флашится на pagehide),
  // а в репозиторий несохранённое уедет при следующем открытии.
  window.addEventListener("pagehide", () => {
    if (syncTimer) sessionStorage.setItem("pycourse:dirty", "1");
  });
  if (sessionStorage.getItem("pycourse:dirty") && gh.tokenStore.has()) {
    sessionStorage.removeItem("pycourse:dirty");
    syncNow(true);
  }
}

main();
