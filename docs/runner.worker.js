// Воркер с Pyodide. Живёт отдельно от главного потока по одной причине:
// бесконечный цикл в коде студента иначе вешает вкладку намертво.
//
// Штатный способ прерывания (pyodide.setInterruptBuffer) требует
// SharedArrayBuffer, а тот — заголовков COOP/COEP, которые GitHub Pages
// выставить не даёт. Поэтому единственный надёжный способ прервать цикл —
// worker.terminate() с главного потока, и значит Python обязан быть здесь.

import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.6/full/pyodide.mjs";

const INDEX_URL = "https://cdn.jsdelivr.net/pyodide/v314.0.6/full/";

// Размеры измерены заранее: jsDelivr отдаёт stdlib chunked, без Content-Length,
// поэтому без зашитых чисел прогресс-бар был бы фальшивым.
const BIG = [
  { file: "pyodide.asm.wasm", bytes: 3438246 },
  { file: "python_stdlib.zip", bytes: 2505338 },
];
const TOTAL = BIG.reduce((s, a) => s + a.bytes, 0);

let pyodide = null;
let runJson = null;
let booting = null;

// loadPyodide не даёт колбэка прогресса. Приём: сами тянем тяжёлые файлы
// со стримом, показывая проценты, и тем самым прогреваем HTTP-кэш —
// loadPyodide потом читает их из кэша мгновенно.
async function warmCache() {
  let done = 0;
  for (const asset of BIG) {
    try {
      const res = await fetch(INDEX_URL + asset.file, { cache: "force-cache" });
      if (!res.ok || !res.body) {
        done += asset.bytes;
        postMessage({ t: "dl", loaded: done, total: TOTAL });
        continue;
      }
      const reader = res.body.getReader();
      for (;;) {
        const { done: fin, value } = await reader.read();
        if (fin) break;
        done += value.length;
        postMessage({ t: "dl", loaded: Math.min(done, TOTAL), total: TOTAL });
      }
    } catch {
      // Прогрев — только ради прогресс-бара. Не удался — не беда,
      // loadPyodide скачает сам, просто без процентов.
      done += asset.bytes;
      postMessage({ t: "dl", loaded: Math.min(done, TOTAL), total: TOTAL });
    }
  }
}

async function boot() {
  const t0 = performance.now();
  await warmCache();
  postMessage({ t: "boot", phase: "init" });
  pyodide = await loadPyodide({ indexURL: INDEX_URL });

  postMessage({ t: "boot", phase: "runner" });
  // runner.py лежит рядом с воркером — отдельный настоящий .py, а не строка
  // внутри JS: его можно линтовать и прогонять локальным CPython.
  const src = await (await fetch("./runner.py")).text();
  pyodide.runPython(src);
  runJson = pyodide.globals.get("run_json");

  postMessage({ t: "ready", ms: Math.round(performance.now() - t0) });
}

self.onmessage = async (e) => {
  const msg = e.data;

  if (msg.t === "boot") {
    if (!booting) booting = boot().catch((err) => {
      booting = null;
      postMessage({ t: "fatal", msg: String(err) });
    });
    return;
  }

  if (msg.t === "run") {
    try {
      if (!booting) booting = boot();
      await booting;
      // Строка внутрь, строка наружу: никаких PyProxy на вложенных данных,
      // а значит нечему течь при сотнях прогонов.
      const report = JSON.parse(runJson(msg.payload));
      postMessage({ t: "result", runId: msg.runId, report });
    } catch (err) {
      postMessage({ t: "fatal", runId: msg.runId, msg: String(err) });
    }
  }
};
