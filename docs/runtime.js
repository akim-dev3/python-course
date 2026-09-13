// Клиент воркера с Pyodide: загрузка, прогресс, таймаут и перезапуск.

const WORKER_URL = "./runner.worker.js";

export const RuntimeState = {
  IDLE: "idle",          // воркера нет, ничего не качали
  LOADING: "loading",    // тянем ~6 МБ Pyodide
  READY: "ready",
  RUNNING: "running",
  FAILED: "failed",
};

export class Runtime extends EventTarget {
  constructor({ timeoutMs = 5000 } = {}) {
    super();
    this.timeoutMs = timeoutMs;
    this.state = RuntimeState.IDLE;
    this.progress = 0;
    this.bootMs = null;
    this.worker = null;
    this.seq = 0;
    this.pending = null;
  }

  #emit(type, detail = {}) {
    this.dispatchEvent(new CustomEvent(type, { detail }));
  }

  #setState(state, detail = {}) {
    this.state = state;
    this.#emit("state", { state, ...detail });
  }

  #spawn() {
    const worker = new Worker(WORKER_URL, { type: "module" });
    worker.onmessage = (e) => this.#onMessage(e.data);
    worker.onerror = (e) => {
      this.#setState(RuntimeState.FAILED, { error: e.message || "worker error" });
      this.pending?.reject(new Error(e.message || "worker error"));
      this.pending = null;
    };
    this.worker = worker;
    return worker;
  }

  #onMessage(msg) {
    if (msg.t === "dl") {
      this.progress = msg.total ? msg.loaded / msg.total : 0;
      this.#setState(RuntimeState.LOADING, { progress: this.progress });
      return;
    }
    if (msg.t === "boot") {
      this.progress = 1;
      this.#setState(RuntimeState.LOADING, { progress: 1, phase: msg.phase });
      return;
    }
    if (msg.t === "ready") {
      this.bootMs = msg.ms;
      if (this.state !== RuntimeState.RUNNING) {
        this.#setState(RuntimeState.READY, { bootMs: msg.ms });
      }
      return;
    }
    if (msg.t === "result") {
      if (!this.pending || this.pending.runId !== msg.runId) return;
      clearTimeout(this.pending.timer);
      const { resolve } = this.pending;
      this.pending = null;
      this.#setState(RuntimeState.READY, { bootMs: this.bootMs });
      resolve(msg.report);
      return;
    }
    if (msg.t === "fatal") {
      clearTimeout(this.pending?.timer);
      const reject = this.pending?.reject;
      this.pending = null;
      this.#setState(RuntimeState.FAILED, { error: msg.msg });
      reject?.(new Error(msg.msg));
    }
  }

  /** Начать грузить Pyodide заранее, не дожидаясь нажатия «Проверить». */
  preload() {
    if (this.worker) return;
    this.#setState(RuntimeState.LOADING, { progress: 0 });
    this.#spawn().postMessage({ t: "boot" });
  }

  /**
   * Прогнать урок. payload — {prelude, units, blocks}.
   * По таймауту воркер убивается: это единственный способ прервать
   * бесконечный цикл, потому что SharedArrayBuffer на GitHub Pages недоступен.
   */
  run(payload) {
    if (this.pending) return Promise.reject(new Error("уже идёт прогон"));
    if (!this.worker) {
      this.#setState(RuntimeState.LOADING, { progress: 0 });
      this.#spawn();
    }

    const runId = ++this.seq;
    this.#setState(RuntimeState.RUNNING);

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending = null;
        this.worker?.terminate();
        this.worker = null;
        // Ассеты остались в HTTP-кэше на год, так что перезапуск быстрый.
        this.#setState(RuntimeState.IDLE);
        this.#emit("timeout", { runId });
        reject(new TimeoutError(this.timeoutMs));
      }, this.timeoutMs);

      this.pending = { runId, resolve, reject, timer };
      this.worker.postMessage({ t: "run", runId, payload: JSON.stringify(payload) });
    });
  }
}

export class TimeoutError extends Error {
  constructor(ms) {
    super(
      `Прервано по таймауту ${ms / 1000} с — скорее всего бесконечный цикл. ` +
      `Частая причина: while без изменения указателя или без break.`
    );
    this.name = "TimeoutError";
  }
}
