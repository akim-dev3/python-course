// Синхронизация прогресса через GitHub Contents API.
//
// Прогресс лежит в самом репозитории (docs/progress.json), поэтому доступен
// с любого устройства и переживает чистку браузера. Читать его можно без
// токена — файл отдаётся Pages как обычная статика; токен нужен только
// для записи.
//
// БЕЗОПАСНОСТЬ. Токен хранится в localStorage на публичной странице. Поэтому
// в интерфейсе прямо требуется fine-grained токен, выданный на ОДИН этот
// репозиторий с правом Contents: read and write и со сроком годности.
// Тогда худшее, что даёт утечка токена, — правки в публичном репозитории
// с учебными задачами. Классический токен с полным доступом сюда вставлять
// нельзя, и об этом сказано в панели настроек.

export const OWNER = "akim-dev3";
export const REPO = "python-course";
const BRANCH = "main";
const PROGRESS_PATH = "docs/progress.json";

const K_TOKEN = "pycourse:v1:gh-token";

const api = (path) => `https://api.github.com/repos/${OWNER}/${REPO}/${path}`;

// btoa не умеет не-ASCII, а в решениях и комментариях кириллица.
function toBase64(text) {
  const bytes = new TextEncoder().encode(text);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

function fromBase64(b64) {
  const bin = atob(b64.replace(/\n/g, ""));
  const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

export const tokenStore = {
  get: () => localStorage.getItem(K_TOKEN) || "",
  set(value) {
    if (value) localStorage.setItem(K_TOKEN, value.trim());
    else localStorage.removeItem(K_TOKEN);
  },
  has: () => Boolean(localStorage.getItem(K_TOKEN)),
};

class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function request(url, options = {}) {
  const token = tokenStore.get();
  const headers = {
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    ...(options.headers || {}),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers, cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) {
    let detail = "";
    try {
      detail = (await res.json()).message || "";
    } catch {}
    throw new HttpError(res.status, describe(res.status, detail));
  }
  return res.json();
}

function describe(status, detail) {
  if (status === 401) return "Токен не принят — проверьте, что он скопирован целиком и не истёк";
  if (status === 403) return "Доступ запрещён — у токена нет права Contents: read and write на этот репозиторий";
  if (status === 409) return "Конфликт версий";
  if (status === 422) return `GitHub отклонил запрос: ${detail}`;
  return `GitHub вернул ${status}${detail ? ": " + detail : ""}`;
}

/** Прочитать файл. Возвращает {text, sha} или null, если файла ещё нет. */
export async function readFile(path) {
  const data = await request(api(`contents/${path}?ref=${BRANCH}`));
  if (!data) return null;
  return { text: fromBase64(data.content), sha: data.sha };
}

/** Записать файл. sha обязателен при перезаписи существующего. */
export async function writeFile(path, text, sha, message) {
  const body = {
    message,
    content: toBase64(text),
    branch: BRANCH,
    ...(sha ? { sha } : {}),
  };
  const data = await request(api(`contents/${path}`), {
    method: "PUT",
    body: JSON.stringify(body),
  });
  return data.content.sha;
}

/** Проверить токен и права. Возвращает описание для интерфейса. */
export async function checkAccess() {
  const repo = await request(api(""));
  if (!repo) throw new Error("Репозиторий не найден");
  return {
    repo: repo.full_name,
    canWrite: Boolean(repo.permissions && repo.permissions.push),
    private: repo.private,
  };
}

// ---------------------------------------------------------------- прогресс

let progressSha = null;

/** Прочитать прогресс. Без токена — через Pages, он публичный. */
export async function loadProgress() {
  try {
    const file = await readFile(PROGRESS_PATH);
    if (file) {
      progressSha = file.sha;
      return JSON.parse(file.text);
    }
  } catch (e) {
    if (e.status !== 401 && e.status !== 403) throw e;
    // Токен кривой — пробуем публичной копией, чтение всё равно возможно.
  }
  try {
    const res = await fetch("./progress.json", { cache: "no-cache" });
    if (res.ok) return await res.json();
  } catch {}
  return null;
}

/**
 * Слияние по полю ts: побеждает более поздняя правка каждой ОТДЕЛЬНОЙ задачи.
 * Так работа с двух устройств не затирается целиком, а сливается позадачно.
 */
export function mergeProgress(local, remote) {
  const out = { code: {}, status: {} };
  for (const section of ["code", "status"]) {
    const a = (local && local[section]) || {};
    const b = (remote && remote[section]) || {};
    for (const key of new Set([...Object.keys(a), ...Object.keys(b)])) {
      const mine = a[key];
      const theirs = b[key];
      if (!mine) out[section][key] = theirs;
      else if (!theirs) out[section][key] = mine;
      else out[section][key] = (theirs.ts || 0) > (mine.ts || 0) ? theirs : mine;
    }
  }
  return out;
}

export async function saveProgress(payload) {
  const text = JSON.stringify(payload, null, 1);
  const message = `progress: ${payload.solved ?? "?"} решено (${new Date()
    .toISOString().slice(0, 16).replace("T", " ")})`;
  try {
    progressSha = await writeFile(PROGRESS_PATH, text, progressSha, message);
  } catch (e) {
    if (e.status !== 409 && e.status !== 422) throw e;
    // Кто-то записал раньше нас: перечитываем, сливаем, пробуем ещё раз.
    const remote = await readFile(PROGRESS_PATH);
    progressSha = remote ? remote.sha : null;
    const merged = mergeProgress(payload, remote ? JSON.parse(remote.text) : null);
    merged.solved = payload.solved;
    merged.updated = new Date().toISOString();
    progressSha = await writeFile(
      PROGRESS_PATH, JSON.stringify(merged, null, 1), progressSha, message);
    return merged;
  }
  return payload;
}

/** Записать собранный .py прямо в файл курса в репозитории. */
export async function pushCourseFile(path, text) {
  const existing = await readFile(path);
  if (existing && existing.text === text) return "unchanged";
  await writeFile(path, text, existing ? existing.sha : null,
                  `solutions: ${path.split("/").pop()}`);
  return "written";
}
