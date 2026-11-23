"""lab_bridge_text.py — рендер-ветвь оракула моста BRIDGE v1 (SPEC/15).

Вход:  факты моста (словарь parse_family из lab_bridge.py: body/ins/
       labels/target/bss/module/pe/stackcom/heapcom), операнды декодера
       lab_x86, таблица меток.
Выход: ТЕКСТ: операнды в каноне enc (_mtext — мнемоника+операнды,
       иначе H-фолбэк), примечания H-строк (_note), шапки b2 (_b2_text)
       и PEG (_peg_text v1; _peg2_text — E9.4-3c-2: канон патчей PEG v2
       из фактов parse_foreign — сворачивание _fold/_chunks64) — чистые
       функции рендера, детерминированные.
Функция: ветвь РЕНДЕР оракула — выделена из lab_bridge.py по лимиту
       500 строк (срез E9.4-2, гигиена; прецедент front/back —
       lab_l2.py + lab_l2_gen.py). Спуск/факты/метки/семантика —
       во фронте (lab_bridge.py): изменение СЕМАНТИКИ — туда,
       изменение ВИДА текста — сюда. Канон SPEC/15: инструменты
       обязаны повторять этот текст байт-в-байт (T-E9-22/24).
"""
import lab_enc
import lab_x86

SECT = 0x1000                    # RVA секции .text (SPEC/04)
BASE_OFF = -SECT                 # «base» — тело-смещение RVA 0
KW = {8: "byte ", 16: "word ", 32: "dword ", 64: "qword "}


def _hx(v):
    """Число -> ЗАГЛАВНЫЙ hex, знак «-» при отрицательном."""
    return ("-%X" % -v) if v < 0 else "%X" % v


# ------------------------------------------------------------ рендер строк
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
        if t[0] != "t":   # косвенный jmp (FF /4, E9.4-1) — всегда
            return None   # H-строка: вне канона enc (круг байто-точен)
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


# ------------------------------------------------------------ тексты выходов
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


# ------------------------------------------------------------ PEG v2 (3c-2)
def _fold(data, lo, hi):
    """Канон сворачивания (SPEC/07 «Канон патчей»): ненулевые пробеги
    области [lo, hi); дырка < 4 нулей сливается в пробег -> [(off,
    bytes)]. Хвостовые нули и дырки >= 4 — вне патчей (нули сборки)."""
    out = []
    i = lo
    while i < hi:
        if data[i] == 0:
            i += 1
            continue
        j = i + 1
        while j < hi:
            if data[j] != 0:
                j += 1
                continue
            z = j
            while z < hi and data[z] == 0:
                z += 1
            if z - j >= 4 or z == hi:      # дырка >= 4 / конец области
                break
            j = z
        out.append((i, bytes(data[i:j])))
        i = j
    return out


def _chunks64(runs):
    """Патч длиннее 64 байт режется кусками по 64 -> [(off, bytes)]."""
    for off, blob in runs:
        for k in range(0, len(blob), 64):
            yield off + k, blob[k:k + 64]


def _peg2_text(f, data, H):
    """Факты parse_foreign + образ + H -> текст PEG v2 (E9.4-3c-2).
    Чистый рендер канона SPEC/07: шапка + `!pev2 H` + патчи `!hdr`
    области заголовков [0, H) + `!body <слот секции кода>` + патчи
    `!sec` прочих raw-областей (порядок: !hdr по off, !sec по n,
    затем off). Файл сворачивается ЦЕЛИКОМ: всё непокрытое — нули."""
    pe = f["pe"]
    secs = pe["sections"]
    slot = next(i for i, s in enumerate(secs) if s is f["code"])
    out = ["; UNIVERSAL / PEG v2 / мост BRIDGE v1 (SPEC/15)",
            "; Исходник: чужой PE32+ (секций %d, DLL %d)"
            % (len(secs), len(pe["imports"])),
            "!pev2 %X" % H]
    out.extend("!hdr %X %s" % (off, blob.hex().upper())
               for off, blob in _chunks64(_fold(data, 0, H)))
    out.append("!body %X" % slot)
    for i, s in enumerate(secs):
        if s is f["code"] or not s["raw_size"]:
            continue
        rp = s["raw_ptr"]
        out.extend("!sec %X %X %s" % (i, off - rp, blob.hex().upper())
                   for off, blob in _chunks64(_fold(data, rp,
                                                    rp + s["raw_size"])))
    return "\n".join(out) + "\n"
