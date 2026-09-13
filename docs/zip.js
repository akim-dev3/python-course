// Минимальный ZIP без сжатия (метод "store").
//
// Своя реализация вместо библиотеки по двум причинам: не тянуть ещё один CDN
// и не зависеть от того, загружен ли Pyodide — «скачать всё» должно работать
// даже до того, как поднялся Python.
//
// Формат: локальный заголовок на каждый файл, потом центральный каталог,
// потом End of Central Directory. Store-режим означает, что данные пишутся
// как есть, поэтому CRC32 — единственная нетривиальная часть.

const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(bytes) {
  let c = 0xffffffff;
  for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function dosTime(d) {
  const time = (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1);
  const date = ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
  return { time, date };
}

class Buf {
  constructor() { this.parts = []; this.len = 0; }
  u16(v) { const b = new Uint8Array(2); new DataView(b.buffer).setUint16(0, v, true); this.raw(b); }
  u32(v) { const b = new Uint8Array(4); new DataView(b.buffer).setUint32(0, v >>> 0, true); this.raw(b); }
  raw(bytes) { this.parts.push(bytes); this.len += bytes.length; }
  blob() { return new Blob(this.parts, { type: "application/zip" }); }
}

/**
 * files: [{ name: "drills/06_data_structures/p1_stack.py", text: "..." }]
 * Пути внутри архива сохраняются, чтобы распаковать поверх python_course/
 * одним движением.
 */
export function makeZip(files) {
  const enc = new TextEncoder();
  const { time, date } = dosTime(new Date());
  const out = new Buf();
  const entries = [];

  for (const f of files) {
    const nameBytes = enc.encode(f.name);
    const data = enc.encode(f.text);
    const crc = crc32(data);
    const offset = out.len;

    out.u32(0x04034b50);
    out.u16(20);            // версия
    out.u16(0x0800);        // флаг: имена файлов в UTF-8
    out.u16(0);             // метод: store
    out.u16(time); out.u16(date);
    out.u32(crc);
    out.u32(data.length); out.u32(data.length);
    out.u16(nameBytes.length); out.u16(0);
    out.raw(nameBytes);
    out.raw(data);

    entries.push({ nameBytes, crc, size: data.length, offset });
  }

  const cdStart = out.len;
  for (const e of entries) {
    out.u32(0x02014b50);
    out.u16(20); out.u16(20);
    out.u16(0x0800); out.u16(0);
    out.u16(time); out.u16(date);
    out.u32(e.crc);
    out.u32(e.size); out.u32(e.size);
    out.u16(e.nameBytes.length);
    out.u16(0); out.u16(0);   // extra, comment
    out.u16(0); out.u16(0);   // disk, internal attrs
    out.u32(0);               // external attrs
    out.u32(e.offset);
    out.raw(e.nameBytes);
  }
  const cdSize = out.len - cdStart;

  out.u32(0x06054b50);
  out.u16(0); out.u16(0);
  out.u16(entries.length); out.u16(entries.length);
  out.u32(cdSize); out.u32(cdStart);
  out.u16(0);

  return out.blob();
}

export function downloadBlob(filename, blob) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
