// Прогресс и код студента в localStorage.
//
// Ключи раздельные намеренно: если сломается status, код не должен уехать
// вместе с ним. Источник правды по задачам — файлы в python_course/;
// localStorage это рабочая копия браузера, поэтому есть экспорт/импорт.

const PREFIX = "pycourse:v1:";
const K_CODE = PREFIX + "code";
const K_STATUS = PREFIX + "status";
const K_UI = PREFIX + "ui";

const HISTORY_LIMIT = 3;

function load(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

let quotaWarned = false;

function save(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (e) {
    if (!quotaWarned) {
      quotaWarned = true;
      document.dispatchEvent(new CustomEvent("storage-full", { detail: { error: e } }));
    }
    return false;
  }
}

class Store {
  constructor() {
    this.code = load(K_CODE, {});
    this.status = load(K_STATUS, {});
    this.ui = load(K_UI, {});
    this._timer = null;

    // Флаш при уходе со страницы: дебаунс не должен съесть последние правки.
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") this.flush();
    });
    window.addEventListener("pagehide", () => this.flush());
  }

  getCode(taskId, fallback = "") {
    const rec = this.code[taskId];
    return rec ? rec.code : fallback;
  }

  hasCode(taskId) {
    return Boolean(this.code[taskId]);
  }

  setCode(taskId, code) {
    const prev = this.code[taskId];
    const history = prev ? [prev.code, ...(prev.history || [])] : [];
    this.code[taskId] = {
      code,
      ts: Date.now(),
      // Кольцо на 3 версии — дешёвая страховка от случайного «сбросить».
      history: history.filter((h) => h !== code).slice(0, HISTORY_LIMIT),
    };
    this.#schedule();
  }

  resetCode(taskId) {
    delete this.code[taskId];
    this.#schedule();
  }

  getStatus(taskId) {
    return this.status[taskId] || { state: "fresh", pass: 0, fail: 0 };
  }

  setStatus(taskId, patch) {
    this.status[taskId] = { ...this.getStatus(taskId), ...patch, ts: Date.now() };
    this.#schedule();
  }

  /** Решена в браузере, но ещё не выгружена в файл курса. */
  isUnsaved(taskId) {
    const s = this.status[taskId];
    return Boolean(s && s.state === "solved" && !s.downloaded);
  }

  markDownloaded(taskIds) {
    for (const id of taskIds) {
      if (this.status[id]) this.status[id].downloaded = true;
    }
    this.#schedule();
  }

  getUI(key, fallback) {
    return key in this.ui ? this.ui[key] : fallback;
  }

  setUI(key, value) {
    this.ui[key] = value;
    this.#schedule();
  }

  #schedule() {
    clearTimeout(this._timer);
    this._timer = setTimeout(() => this.flush(), 400);
  }

  flush() {
    clearTimeout(this._timer);
    save(K_CODE, this.code);
    save(K_STATUS, this.status);
    save(K_UI, this.ui);
  }

  exportJSON() {
    return JSON.stringify(
      { version: 1, exported: new Date().toISOString(), code: this.code, status: this.status },
      null, 1
    );
  }

  importJSON(text) {
    const data = JSON.parse(text);
    if (!data || typeof data !== "object" || !data.code) {
      throw new Error("не похоже на экспорт прогресса");
    }
    this.code = { ...this.code, ...data.code };
    this.status = { ...this.status, ...(data.status || {}) };
    this.flush();
    return Object.keys(data.code).length;
  }
}

export const store = new Store();
