// Сборка .py-файла из решений студента.
//
// Вся сложность решена на этапе сборки: content.json хранит файл как
// последовательность сегментов raw/slot, и склейка сегментов побайтово равна
// оригиналу (это assert в build_content.py --verify). Значит достаточно
// подставить код в слоты — и получится файл ровно того формата, что в курсе:
// его можно положить обратно в python_course/ и запустить локально,
// оригинальный def check живёт в raw-сегменте и никуда не делся.

function normalize(code) {
  // Ровно один \n в конце слота: две пустые строки перед следующим блоком
  // лежат в соседнем raw-сегменте, иначе отступы PEP8 поедут.
  return code.replace(/\r\n/g, "\n").replace(/\s+$/, "") + "\n";
}

export function buildFile(lesson, codeMap) {
  return lesson.segments
    .map((s) => (s.t === "raw" ? s.text : normalize(codeMap[s.task] ?? s.text)))
    .join("");
}

/**
 * Обратная операция к buildFile: вынуть решения из .py-файла на диске.
 *
 * Слоты не ищутся по признакам кода — они вычисляются как ПРОМЕЖУТКИ между
 * неизменяемыми raw-кусками. Если хоть один raw не найден по порядку или
 * в конце остался лишний текст, разбор считается несостоявшимся и функция
 * возвращает null: лучше ничего не подставить, чем подставить не то.
 */
export function extractSolutions(lesson, fileText) {
  const text = fileText.replace(/\r\n/g, "\n");
  const out = {};
  let pos = 0;
  let pendingSlot = null;

  for (const seg of lesson.segments) {
    if (seg.t === "slot") {
      pendingSlot = seg;
      continue;
    }
    const raw = seg.text.replace(/\r\n/g, "\n");
    const idx = raw === "" ? pos : text.indexOf(raw, pos);
    if (idx === -1) return null;

    if (pendingSlot) {
      out[pendingSlot.task] = normalize(text.slice(pos, idx));
      pendingSlot = null;
    } else if (idx !== pos) {
      return null;                 // между raw-кусками оказался чужой текст
    }
    pos = idx + raw.length;
  }

  if (pendingSlot) {
    out[pendingSlot.task] = normalize(text.slice(pos));
    pos = text.length;
  }
  return pos === text.length ? out : null;
}

export function downloadText(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function basename(path) {
  return path.split("/").pop();
}
