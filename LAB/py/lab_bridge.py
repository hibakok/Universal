"""lab_bridge.py — оракул моста BRIDGE v1 (SPEC/15): EXE -> BRICK v2 + PEG v1.

Вход:  байты EXE семейства UNIVERSAL (PE32+ SPEC/04; один kernel32.dll;
       вход в секции). Выход: bridge(data) -> (текст BRICK v2, текст
       PEG v1); BridgeError — образ вне семейства.
Функция: эталонная семантика моста L5 (E9.1 «сначала истина семантики»,
       прецедент E7.1/E8.1): чужой машинный код входит в наш мир как
       ИСХОДНИК. Композиция lab_pe + lab_x86; спуск от входа
       (терминалы; нули/сбой — данные; тень — младший адрес побеждает);
       метки l/d/iat_ (iat_ > l > d; $base — RVA 0; правило
       представимости E9.2-3b); M-строка при точном воспроизведении
       enc (иначе H-строка); данные DD/DQ с $ссылками, DB <= 16,
       DZ >= 3; тело = max(ненулевой хвост, концы команд), вилка
       SizeOfRawData, хвост -> !bss. Круг enc -> brick -> pegen(+peg)
       == EXE байт-в-байт — секция 18 (T-E9-01..16). Правила — SPEC/15.
"""
import bisect

import lab_enc
import lab_pe
import lab_x86

SECT = 0x1000                    # RVA секции .text (SPEC/04)
BASE_OFF = -SECT                 # «base» — тело-смещение RVA 0
DB_MAX = 16                      # байт в одной DB-строке
DZ_MIN = 3                       # минимальный пробег нулей для DZ
KW = {8: "byte ", 16: "word ", 32: "dword ", 64: "qword "}

class BridgeError(ValueError):
    pass

def _u32(b, o):
    return int.from_bytes(b[o:o + 4], "little")

def _u64(b, o):
    return int.from_bytes(b[o:o + 8], "little")

def _hx(v):
    """Число -> ЗАГЛАВНЫЙ hex, знак «-» при отрицательном."""
    return ("-%X" % -v) if v < 0 else "%X" % v

def _san(name):
    """Имя импорта -> суффикс [a-z0-9_]{1,59}. E9.2-3b: только ASCII
    (латиница-1 alnum «ÿ» отвергается enc; зонд probe_e92_3b2)."""
    s = "".join(c if "0" <= c <= "9" or "a" <= c <= "z" else "_"
                for c in name.lower())
    return s[:59] or "f"

# ------------------------------------------------------------ проход кода
def _walk(body, entry, limit):
    """Спуск от entry: offset -> (имя, длина, аргументы). Путь
    обрывается: терминал (jmp/ret/int3), сбой декодирования, выход
    за limit, ВСЕ-НУЛЕВЫЕ байты (нули — данные, не код)."""
    def fetch(a, n):
        if a < 0 or a + n > len(body):
            raise IndexError
        return int.from_bytes(body[a:a + n], "little")

    ins = {}
    pending = [entry]
    while pending:
        a = pending.pop()
        while 0 <= a < limit:
            if a in ins:
                break
            try:
                name, ln, args = lab_x86.decode(fetch, a)
            except (lab_x86.UnknownOpcode, IndexError):
                break                       # данные — путь закончен
            if not any(body[a:a + ln]):
                break                       # нули — данные, не код
            ins[a] = (name, ln, args)
            nxt = a + ln
            if name in ("ret", "int3"):
                break
            if name == "jmp":
                pending.append(args[0][1])
                break
            if name == "jcc":
                pending.append(args[1][1])
            elif name == "call" and args[0][0] == "t":
                pending.append(args[0][1])
            a = nxt
    return ins

def _sweep(ins):
    """Пересечения: младший адрес побеждает -> dict выживших."""
    out = {}
    cursor = 0
    for a in sorted(ins):
        if a < cursor:
            continue                        # затенена
        out[a] = ins[a]
        cursor = a + ins[a][1]
    return out

# ------------------------------------------------------------ разбор семьи
def parse_family(data):
    """EXE семейства -> словарь фактов моста (код, длина, импорты).
    Полный анализ; отказ — BridgeError (SPEC/15 п. 2)."""
    try:
        pe = lab_pe.parse(data)
    except Exception as e:                     # noqa: BLE001 — любой крах
        raise BridgeError("не семейство: не разбирается (%s)" % e)
    bad = [b for b in lab_pe.check_spec04(pe)
           if b != "точка входа != 0x1000"]      # вход 0x1200 — легален
    if bad:
        raise BridgeError("не семейство: " + "; ".join(bad))
    body = pe["body"]
    if not body or not any(body):
        raise BridgeError("пустая/нулевая секция")
    vsize, raw = pe["sec_vsize"], pe["sec_raw_size"]
    # имя модуля из DOS-заглушки (шаблон pegen, SPEC/07)
    stub = data[0x40:0x80]
    if not stub.startswith(b"Universal L0 "):
        raise BridgeError("чужая DOS-заглушка")
    end = stub.find(b". No DOS support.")
    module = stub[13:end].decode("latin1") if end > 13 else ""
    if not (1 <= len(module) <= 31) or any(c.isspace() for c in module):
        raise BridgeError("нет имени модуля в заглушке")
    # код: спуск от входа; границы инструкций — в пределах VirtualSize
    entry = pe["addr_entry_point"] - SECT
    ins = _sweep(_walk(body, entry, vsize))
    for a, (_nm, ln, _ar) in ins.items():
        if a + ln > vsize:
            raise BridgeError("инструкция @%X за VirtualSize" % a)
    # целевая длина тела: последний ненулевой байт и концы инструкций;
    # при необходимости — минимальная длина выравнивающей вилки raw
    nz = max(i for i, b in enumerate(body) if b)
    target = max([nz + 1, 1] + [a + ins[a][1] for a in ins])
    if (target + 0x1FF) & ~0x1FF != raw:
        target = raw - 0x1FF        # минимальная длина той же вилки
    if target > vsize:
        raise BridgeError("длина тела больше VirtualSize")
    return {
        "pe": pe, "body": body, "vsize": vsize, "raw": raw,
        "target": target, "bss": vsize - target, "module": module,
        "entry_off": entry, "ins": ins,
        "stackcom": _u32(data, 0xE8), "heapcom": _u32(data, 0xF8),
    }

# --------------------------------------------------- метки/импорты
def _import_map(fam):
    """Структуры импорта -> (labels, semantic, known_rva): offset ->
    имя метки (iat_*, d*) / ("DD"|"DQ", [значения]) с $ссылками /
    RVA -> имя. Представимость (E9.2-3b, SPEC/15 п. 4/6): метка НЕ
    создаётся строго внутри выжившей инструкции (наложение разрезов
    — невалидный b2); DQ с не-созданной меткой — сырыми байтами.
    """
    body, pe = fam["body"], fam["pe"]
    labels, semantic, known = {}, {}, {}
    imp = pe["imports"][0]
    iat_off = imp["iat_rva"] - SECT
    int_off = (imp["oft_rva"] or imp["iat_rva"]) - SECT
    name_off = imp["name_rva"] - SECT
    hints = [(fn, hr - SECT) for fn, hr in imp["funcs"]]
    n = len(hints)
    limit = fam["target"]
    if not (0 <= iat_off and iat_off + 8 * (n + 1) <= limit
            and 0 <= name_off < limit
            and all(0 <= h < limit for _fn, h in hints)):
        return labels, semantic, known        # сырые байты (байто-точно)
    starts = sorted(fam["ins"])

    def inside_ins(o):                         # строго внутри выжившей
        i = bisect.bisect_right(starts, o) - 1
        return i >= 0 and starts[i] < o < \
            starts[i] + fam["ins"][starts[i]][1]

    for k, (fn, h) in enumerate(hints):
        if not inside_ins(iat_off + 8 * k):
            labels[iat_off + 8 * k] = "iat_" + _san(fn)
        if not inside_ins(h):
            labels.setdefault(h, "d%x" % (h + SECT))
            known[h + SECT] = labels[h]
    if not inside_ins(name_off):
        labels.setdefault(name_off, "d%x" % (name_off + SECT))
        known[name_off + SECT] = labels[name_off]
    if int_off != iat_off and not inside_ins(int_off):
        labels.setdefault(int_off, "d%x" % (int_off + SECT))
    if int_off in labels:
        known[int_off + SECT] = labels[int_off]
    if iat_off in labels:
        known[iat_off + SECT] = labels[iat_off]
    idt_off = pe["dd1_import_rva"] - SECT
    if 0 <= idt_off and idt_off + 20 <= limit:
        semantic[idt_off] = ("DD", [_dollar(_u32(body, idt_off + 4 * k),
                                            known) for k in range(5)])
    for base in {iat_off, int_off}:
        rows = []
        for k in range(n + 1):
            v = _u64(body, base + 8 * k)
            if v == 0 and k == n:
                t = "0"
            elif k < n and v == hints[k][1] + SECT \
                    and hints[k][1] in labels:
                t = "$" + labels[hints[k][1]]
            else:
                rows = None
                break
            rows.append((base + 8 * k, t))
        if rows is not None:               # по записи на строку:
            for off, t in rows:            # метки слотов — между строк
                semantic[off] = ("DQ", [t])
    return labels, semantic, known

def _dollar(v, known):
    """dword -> $имя (если RVA известна) | hex."""
    s = known.get(v)
    return "$" + s if s else _hx(v)

# ------------------------------------------------ рендер строк
def _reg(op):
    _, idx, size = op
    if size == 8:
        return lab_x86.REG8[idx]
    if size == 16:
        return lab_x86.REG16[idx]
    if size == 64:
        return lab_x86.REG64[idx]
    return "r%dd" % idx if idx >= 8 else \
        lab_x86.REG64[idx].replace("r", "e", 1)

def _mem(op, labels):
    """('m', b, i, scale, disp, size, ripabs) -> текст | None."""
    _, b, i, scale, disp, _size, ripabs = op
    if ripabs is not None:
        off = ripabs[1]
        if off == BASE_OFF:
            return "[rip+$base]"
        name = labels.get(off)
        return "[rip+$%s]" % name if name else None
    if scale != 1:
        return None
    s = lab_x86.REG64[b]
    if i is not None:
        s += "+" + lab_x86.REG64[i]
    if disp:
        s += _hx(disp) if disp < 0 else "+" + _hx(disp)
    return "[%s]" % s

def _plain(op):
    """Операнд reg/imm/cl -> текст | None (mem — _mem)."""
    if isinstance(op, str):
        return op if op == "cl" else None
    if isinstance(op, int):                 # счётчик сдвига (lab_x86)
        return _hx(op)
    if op[0] == "r":
        return _reg(op)
    if op[0] == "i":
        return _hx(op[1])
    return None

def _mtext(name, args, ln, labels):
    """Инструкция -> (мнемоника, [операнды]) | None. Слот :1 (rel8) —
    по длине исходной инструкции (2 байта)."""
    if name in ("cdqe", "cqo", "cdq", "ret", "int3"):
        return name, []                     # аргументы декодера — шум
    rel8 = ln == 2 and name in ("jmp", "jcc")
    if name in ("jmp", "jcc"):
        t = args[1] if name == "jcc" else args[0]
        nm = "jmp" if name == "jmp" else "j%s" % args[0]
        if t[1] == BASE_OFF:
            return nm, ["$base" + (":1" if rel8 else "")]
        if t[1] not in labels:
            return None
        return nm, ["$" + labels[t[1]] + (":1" if rel8 else "")]
    if name == "call":
        a = args[0]
        if a[0] == "t":
            return None if a[1] not in labels else \
                ("call", ["$" + labels[a[1]]])
        t = _mem(a, labels)
        return ("call", [t]) if t else None
    ops = []
    for a in args:
        if isinstance(a, tuple) and a[0] == "m":
            other = [x for x in args if x is not a and
                     isinstance(x, tuple)]
            kw = KW[a[5]] if (other and other[0][0] == "i" or
                              name == "movzx") else ""
            t = _mem(a, labels)
            if t is None:
                return None
            ops.append(kw + t)
        else:
            t = _plain(a)
            if t is None:
                return None
            ops.append(t)
    return name, ops

def _template(mnem, ops, body, off, ln, rlabels):
    """Кодировка enc == байты инструкции (слоты включительно)?"""
    try:
        toks = lab_enc.encode_m(mnem, list(ops), 1)
    except lab_enc.EncError:
        return False
    pos = 0
    for t in toks:
        if isinstance(t, int):
            if body[off + pos] != t:
                return False
            pos += 1
            continue
        _, lname, size = t
        p = pos
        pos += size
        if pos != ln:
            return False                # слот обязан быть последним
        want = int.from_bytes(body[off + p:off + pos], "little",
                              signed=True)
        loff = BASE_OFF if lname == "base" else rlabels.get(lname)
        if loff is None or want != loff - (off + pos):
            return False
    return pos == ln

def _note(name, args):
    """Комментарий H-строки: мнемоника с «сырыми» адресами."""
    try:
        if name == "jcc":
            return "j%s %X" % (args[0], args[1][1])
        if name in ("ret", "int3", "cdqe", "cqo", "cdq"):
            return name
        parts = []
        for a in args:
            if isinstance(a, str):
                parts.append(a)
            elif isinstance(a, int):
                parts.append(_hx(a))
            elif a[0] == "r":
                parts.append(_reg(a))
            elif a[0] == "i":
                parts.append(_hx(a[1]))
            elif a[0] == "t":
                parts.append("%X" % a[1])
            elif a[0] == "m" and a[6] is not None:
                d = a[6][1] + SECT
                parts.append("[rip%+d]" % d if d else "[rip]")
            elif a[0] == "m":
                parts.append("[mem]")
        return "%s %s" % (name, ", ".join(parts))
    except Exception:
        return name

# ------------------------------------------------------------ эмиссия b2
def _emit_lines(fam, mode=None):
    """Факты моста -> (строки BRICK v2, статистика). Чистый рендер.

    mode (срезы E9.2-3, SPEC/15 п. 10): None — канон (M-строки при
    точном воспроизведении enc + метки + семантика); "H" — H-строки
    с метками/семантикой (E9.2-3b); "RAW" — без них (E9.2-3a).
    Байто-точность круга — во всех режимах (H-строка — те же байты)."""
    body, ins = fam["body"], fam["ins"]
    limit = fam["target"]
    if mode == "RAW":
        labels, semantic = {}, {}
    else:
        labels, semantic, _known = _import_map(fam)
    # семантика не пересекает инструкции/друг друга/метки (E9.2-3b)
    ins_ranges = [(a, a + ins[a][1]) for a in ins]
    sem = {}
    for o in sorted(semantic):
        v = semantic[o]
        size = 4 * len(v[1]) if v[0] == "DD" else 8 * len(v[1])
        clash = any(o < e and s < o + size for s, e in ins_ranges)
        if not clash:
            clash = any(o < e and s < o + size for s, e in
                        ((q, q + (4 if w[0] == "DD" else 8) * len(w[1]))
                         for q, w in sem.items()))
        if not clash:
            clash = any(o < q < o + size for q in labels)
        if not clash:
            sem[o] = v                    # конфликт — сырыми байтами
    starts_sorted = sorted(ins)
    sem_ranges = [(o, o + (4 if v[0] == "DD" else 8) * len(v[1]))
                  for o, v in sem.items()]

    def inside_ins(o):
        i = bisect.bisect_right(starts_sorted, o) - 1
        return i >= 0 and starts_sorted[i] < o < \
            starts_sorted[i] + ins[starts_sorted[i]][1]

    def inside_sem(o):
        return any(s < o < e for s, e in sem_ranges)

    # метки l*/d*: цели переходов и rip-ссылок (приоритет iat_ > l > d)
    if mode != "RAW":
        for a in starts_sorted:
            for op in ins[a][2]:
                if not isinstance(op, tuple):
                    continue
                if op[0] == "t":
                    offs = [op[1]]
                elif op[0] == "m" and op[6] is not None:
                    offs = [op[6][1]]
                else:
                    continue
                for off in offs:
                    if off == BASE_OFF or off in labels:
                        continue
                    if off in ins or off in sem:
                        labels[off] = "l%x" % (off + SECT)
                    elif 0 <= off < limit and not inside_ins(off) \
                            and not inside_sem(off):
                        labels[off] = "d%x" % (off + SECT)
                    # иначе метка невозможна — инструкция возьмёт H-форму
    rlabels = {v: k for k, v in labels.items()}
    # линейная эмиссия: разрезы по стартам строк
    out, stats = [], {"m": 0, "h": 0, "dz": 0, "db": 0, "sem": 0,
                      "lab": len(labels), "ins": len(ins)}
    cuts = sorted(set(labels) | set(sem) | set(ins) | {0, limit})
    for lo, hi in zip(cuts, cuts[1:]):
        if lo in labels:
            out.append(":%s ; @%04X" % (labels[lo], lo))
        o = lo
        if lo in ins:
            name, ln, args = ins[lo]
            mt = None if mode else _mtext(name, args, ln, labels)
            if mt and _template(mt[0], mt[1], body, lo, ln, rlabels):
                txt = mt[0] if not mt[1] else \
                    "%s %s" % (mt[0], ", ".join(mt[1]))
                out.append("M %s ; @%04X" % (txt, lo))
                stats["m"] += 1
            else:
                bs = " ".join("%02X" % b for b in body[lo:lo + ln])
                out.append("H %s ; @%04X %s" % (bs, lo,
                                                _note(name, args)))
                stats["h"] += 1
            o = lo + ln                        # хвост сегмента — данными
        elif lo in sem:
            kind, vals = sem[lo]
            out.append("%s %s ; @%04X" % (kind, " ".join(vals), lo))
            stats["sem"] += 1
            o = lo + (4 if kind == "DD" else 8) * len(vals)
        while o < hi:                           # данные сегмента
            z = 0
            while o + z < hi and body[o + z] == 0:
                z += 1
            if z >= DZ_MIN:
                out.append("DZ %X ; @%04X" % (z, o))
                stats["dz"] += 1
                o += z
                continue
            first = o
            chunk = []
            while o < hi and len(chunk) < DB_MAX:
                if body[o] == 0:
                    zz = 0
                    while o + zz < hi and body[o + zz] == 0:
                        zz += 1
                    if zz >= DZ_MIN:
                        break
                chunk.append("%02X" % body[o])
                o += 1
            out.append("DB %s ; @%04X" % (" ".join(chunk), first))
            stats["db"] += 1
    return out, stats

def _b2_text(fam, lines):
    head = [
        "; UNIVERSAL / BRICK v2 / мост BRIDGE v1 (SPEC/15)",
        "; Исходник: %s.exe (тело секции RVA %X, %X Б; !bss %X)"
        % (fam["module"], SECT, fam["target"], fam["bss"]),
        "; Круг: enc -> brick -> pegen(+peg моста) == исходный EXE",
    ]
    return "\n".join(head + lines) + "\n"

def _peg_text(fam):
    pe = fam["pe"]
    out = ["; UNIVERSAL / PEG v1 / мост BRIDGE v1 (SPEC/15) / исходник:"
           " %s.exe" % fam["module"],
           "!module %s" % fam["module"],
           "!entry %X" % pe["addr_entry_point"],
           "!idata %X %X" % (pe["dd1_import_rva"], pe["dd1_import_size"]),
           "!iat %X %X" % (pe["dd12_iat_rva"], pe["dd12_iat_size"])]
    if fam["bss"]:
        out.append("!bss %X" % fam["bss"])
    if fam["stackcom"] != 0x1000:
        out.append("!stackcom %X" % fam["stackcom"])
    if fam["heapcom"] != 0x1000:
        out.append("!heapcom %X" % fam["heapcom"])
    return "\n".join(out) + "\n"

def emit_b2(data, mode=None):
    """EXE -> (текст BRICK v2, статистика); mode — срезы E9.2-3."""
    fam = parse_family(data)
    lines, stats = _emit_lines(fam, mode)
    return _b2_text(fam, lines), stats

def emit_peg(data):
    """EXE -> текст PEG v1 (регенерация обёртки, SPEC/07)."""
    return _peg_text(parse_family(data))

def bridge(data):
    """EXE -> (текст BRICK v2, текст PEG v1). Полный мост."""
    fam = parse_family(data)
    lines, _stats = _emit_lines(fam)
    return _b2_text(fam, lines), _peg_text(fam)
