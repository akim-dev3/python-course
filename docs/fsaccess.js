// Прямая запись решений в файлы курса на диске (File System Access API).
//
// Смысл: источник правды у курса — .py-файлы, и сайт пишет ровно в них.
// Тогда «сохранить прогресс» перестаёт быть отдельной задачей: решения
// оказываются там же, где их ждёт python и git. Шаг «скачать и переложить»
// исчезает, а чистка браузера ничего не уносит.
//
// Разрешение на папку браузер запоминает: handle кладётся в IndexedDB, при
// следующем открытии достаточно одного клика (а часто и его не нужно).
// Работает в Chrome и Edge на десктопе, по https или на localhost.

const DB_NAME = "pycourse-fs";
const STORE = "handles";
const KEY = "course-dir";

export const supported = () => typeof window.showDirectoryPicker === "function";

// ---------------------------------------------------------------- IndexedDB

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function idbGet(key) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readonly").objectStore(STORE).get(key);
    tx.onsuccess = () => resolve(tx.result);
    tx.onerror = () => reject(tx.error);
  });
}

async function idbSet(key, value) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readwrite").objectStore(STORE).put(value, key);
    tx.onsuccess = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function idbDel(key) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readwrite").objectStore(STORE).delete(key);
    tx.onsuccess = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

// ---------------------------------------------------------------- папка

let dirHandle = null;

/** Восстановить папку из прошлого сеанса. Возвращает "ready" | "prompt" | null. */
export async function restore() {
  if (!supported()) return null;
  const handle = await idbGet(KEY).catch(() => null);
  if (!handle) return null;
  dirHandle = handle;
  const state = await handle.queryPermission({ mode: "readwrite" });
  return state === "granted" ? "ready" : "prompt";
}

/** Спросить разрешение заново — требует клика пользователя. */
export async function regrant() {
  if (!dirHandle) return false;
  const state = await dirHandle.requestPermission({ mode: "readwrite" });
  return state === "granted";
}

/** Выбрать папку курса. Требует клика пользователя. */
export async function connect() {
  const handle = await window.showDirectoryPicker({
    id: "python-course",
    mode: "readwrite",
  });
  dirHandle = handle;
  await idbSet(KEY, handle);
  return handle.name;
}

export async function forget() {
  dirHandle = null;
  await idbDel(KEY).catch(() => {});
}

export const isConnected = () => Boolean(dirHandle);
export const folderName = () => (dirHandle ? dirHandle.name : "");

async function resolvePath(relPath, { create = false } = {}) {
  if (!dirHandle) throw new Error("папка курса не подключена");
  const parts = relPath.split("/");
  const filename = parts.pop();
  let dir = dirHandle;
  for (const part of parts) {
    dir = await dir.getDirectoryHandle(part, { create });
  }
  return dir.getFileHandle(filename, { create });
}

/** Прочитать файл курса. null, если его нет. */
export async function readFile(relPath) {
  try {
    const fh = await resolvePath(relPath);
    return await (await fh.getFile()).text();
  } catch (e) {
    if (e.name === "NotFoundError") return null;
    throw e;
  }
}

export async function writeFile(relPath, text) {
  const fh = await resolvePath(relPath, { create: true });
  const w = await fh.createWritable();
  await w.write(text);
  await w.close();
}

/**
 * Проверить, что выбрана именно папка курса, а не что-то соседнее.
 * Иначе сайт молча создаст пустое дерево drills/… в случайном месте.
 */
export async function looksLikeCourse(sampleRelPath) {
  return (await readFile(sampleRelPath)) !== null;
}
