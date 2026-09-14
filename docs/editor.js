// Фасад над редактором кода.
//
// Внутри CodeMirror 5 — единственный вариант, который работает обычными
// <script> с CDN, без бандлера (CM6 это ESM-граф из ~8 пакетов). Репозиторий
// CM5 заархивирован, поэтому весь контакт с ним заперт в этом файле: если
// однажды понадобится Ace, меняется только он.

const CM = () => window.CodeMirror;

// Слова для автодополнения: ключевые слова и встроенные функции, которых
// реально не хватает при печати на курсе (см. паттерны в CLAUDE.md).
// Это не языковой сервер — только список слов, объединённый с тем, что уже
// есть в буфере (свои переменные и функции студент тоже видит в подсказках).
const PY_WORDS = [
  "def", "return", "for", "in", "if", "elif", "else", "while", "break",
  "continue", "pass", "class", "import", "from", "as", "try", "except",
  "finally", "raise", "yield", "with", "lambda", "and", "or", "not", "is",
  "True", "False", "None", "self",
  "len", "range", "sum", "max", "min", "sorted", "reversed", "enumerate",
  "zip", "map", "filter", "isinstance", "print", "round", "abs", "any", "all",
  "dict", "list", "set", "tuple", "str", "int", "float", "bool",
  "append", "extend", "pop", "insert", "remove", "get", "items", "keys",
  "values", "setdefault", "update", "sort", "join", "split", "strip",
  "replace", "format", "startswith", "endswith", "lower", "upper", "count",
];

function pythonHint(cm) {
  const cur = cm.getCursor();
  const token = cm.getTokenAt(cur);
  const start = token.start;
  const word = token.string.slice(0, cur.ch - start);
  if (word && !/^\w+$/.test(word)) return null;

  const wordLower = word.toLowerCase();
  const seen = new Set();
  const list = [];
  const consider = (w) => {
    if (w.length <= word.length) return;
    if (!w.toLowerCase().startsWith(wordLower)) return;
    if (seen.has(w)) return;
    seen.add(w);
    list.push(w);
  };
  PY_WORDS.forEach(consider);
  const re = /[A-Za-z_]\w*/g;
  const text = cm.getValue();
  let m;
  while ((m = re.exec(text))) consider(m[0]);
  if (!list.length) return null;

  list.sort((a, b) => a.length - b.length || a.localeCompare(b));
  return { list, from: CM().Pos(cur.line, start), to: cur };
}

export function createEditor(host, { value = "", onChange = null, onBlur = null } = {}) {
  if (!CM()) {
    // Мягкая деградация: без CDN редактор превращается в textarea,
    // но решать задачи всё ещё можно.
    const ta = document.createElement("textarea");
    ta.className = "editor-fallback";
    ta.value = value;
    ta.spellcheck = false;
    host.appendChild(ta);
    ta.addEventListener("input", () => onChange?.(ta.value));
    if (onBlur) ta.addEventListener("blur", onBlur);
    return {
      getValue: () => ta.value,
      setValue: (v) => { ta.value = v; },
      markError: () => {},
      clearErrors: () => {},
      focus: () => ta.focus(),
      refresh: () => {},
    };
  }

  const cm = CM()(host, {
    value,
    mode: "python",
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    smartIndent: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    styleActiveLine: true,
    gutters: ["CodeMirror-linenumbers", "err-gutter"],
    extraKeys: {
      // В Python отступ пробелами — Tab не должен вставлять \t.
      Tab: (editor) => {
        if (editor.somethingSelected()) editor.indentSelection("add");
        else editor.replaceSelection("    ", "end");
      },
      "Shift-Tab": (editor) => editor.indentSelection("subtract"),
      "Ctrl-Space": (editor) => CM().showHint(editor, pythonHint, { completeSingle: false }),
    },
  });

  if (onChange) cm.on("change", () => onChange(cm.getValue()));
  if (onBlur) cm.on("blur", () => onBlur());

  // Подсказки по ходу набора — как в VSCode: не нужно жать Ctrl+Space
  // самому. Показываются только при вводе буквы/цифры/_, и не мешают,
  // если список подсказок уже открыт или курсор что-то удаляет.
  cm.on("inputRead", (instance, change) => {
    if (instance.state.completionActive) return;
    if (change.origin !== "+input") return;
    const ch = change.text[change.text.length - 1];
    if (!ch || !/\w/.test(ch)) return;
    CM().showHint(instance, pythonHint, { completeSingle: false });
  });

  let marks = [];

  return {
    getValue: () => cm.getValue(),
    setValue: (v) => {
      const cursor = cm.getCursor();
      cm.setValue(v);
      cm.setCursor(cursor);
    },
    /** Подсветить строку с ошибкой (1-based, как отдаёт Python). */
    markError(lineno, message = "") {
      const i = lineno - 1;
      if (i < 0 || i >= cm.lineCount()) return;
      cm.addLineClass(i, "background", "cm-line-error");
      const dot = document.createElement("span");
      dot.className = "err-dot";
      dot.title = message;
      dot.textContent = "●";
      cm.setGutterMarker(i, "err-gutter", dot);
      marks.push(i);
    },
    clearErrors() {
      for (const i of marks) {
        cm.removeLineClass(i, "background", "cm-line-error");
        cm.setGutterMarker(i, "err-gutter", null);
      }
      marks = [];
    },
    focus: () => cm.focus(),
    refresh: () => cm.refresh(),
  };
}
