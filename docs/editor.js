// Фасад над редактором кода.
//
// Внутри CodeMirror 5 — единственный вариант, который работает обычными
// <script> с CDN, без бандлера (CM6 это ESM-граф из ~8 пакетов). Репозиторий
// CM5 заархивирован, поэтому весь контакт с ним заперт в этом файле: если
// однажды понадобится Ace, меняется только он.

const CM = () => window.CodeMirror;

export function createEditor(host, { value = "", onChange = null } = {}) {
  if (!CM()) {
    // Мягкая деградация: без CDN редактор превращается в textarea,
    // но решать задачи всё ещё можно.
    const ta = document.createElement("textarea");
    ta.className = "editor-fallback";
    ta.value = value;
    ta.spellcheck = false;
    host.appendChild(ta);
    ta.addEventListener("input", () => onChange?.(ta.value));
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
    },
  });

  if (onChange) cm.on("change", () => onChange(cm.getValue()));

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
