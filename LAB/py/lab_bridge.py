"""lab_bridge.py — ФРОНТ оракула моста BRIDGE v1 (SPEC/15): EXE -> факты.

Вход:  байты EXE семейства UNIVERSAL (PE32+ SPEC/04, один kernel32.dll)
       ИЛИ произвольного PE32+ (parse_foreign — E9.4-3b).
       Выход: bridge(data) -> (текст BRICK v2, PEG v1); BridgeError — чужое.
Функция: эталонная семантика моста L5 (E9.1 «сначала истина семантики»,
       прецедент E7.1/E8.1): чужой машинный код входит в наш мир как
       ИСХОДНИК. Композиция lab_pe + lab_x86; спуск от входа (терминалы:
       прямой jmp/ret/int3 и косвенный FF /4 — E9.4-1, НО jmp qword
       [rip+X] даёт цели-кандидаты из таблицы переходов — E9.4-2;
       нули/сбой — данные; тень — младший адрес побеждает); метки
       l/d/iat_ (iat_ > l > d; $base — RVA 0; представимость E9.2-3b);
       эмиссия — режимы _emit_lines(None/H/RAW). parse_foreign
       (E9.4-3b) — чужой путь: исполняемая секция по точке входа +
       спуск в её теле + факты для PEG v2; эмиссия чужой обёртки —
       emit_peg_v2 (E9.4-3c-2: канон патчей SPEC/07); эмиссия b2
       чужого тела — emit_b2_foreign (E9.4-3c-3: канон п. 4-6,
       base = vaddr секции кода).
       РЕНДЕР текста — lab_bridge_text.py (M/H-строки, шапки b2/PEG;
       ветвь выделена по лимиту 500 строк — прецедент lab_l2/lab_l2_gen,
       E9.4-2). Правила — SPEC/15.
"""
import bisect

import lab_pe
import lab_x86
from lab_bridge_text import (BASE_OFF, SECT, _b2_foreign_text,
                             _b2_text, _hx, _mtext, _note,
                             _peg2_text, _peg_text, _template)

DB_MAX = 16                      # байт в одной DB-строке
DZ_MIN = 3                       # минимальный пробег нулей для DZ

class BridgeError(ValueError):
    pass

def _u32(b, o):
    return int.from_bytes(b[o:o + 4], "little")

def _u64(b, o):
    return int.from_bytes(b[o:o + 8], "little")

def _san(name):
    """Имя импорта -> суффикс [a-z0-9_]{1,59}. E9.2-3b: только ASCII
    (латиница-1 alnum «ÿ» отвергается enc; зонд probe_e92_3b2)."""
    s = "".join(c if "0" <= c <= "9" or "a" <= c <= "z" else "_"
                for c in name.lower())
    return s[:59] or "f"

# ------------------------------------------------------------ проход кода
def _walk(body, entry, limit):
    """Спуск от entry: offset -> (имя, длина, аргументы). Путь
    обрывается: терминал (прямой jmp/ret/int3; косвенный FF /4 —
    терминал, его кандидаты — ТОЛЬКО таблица переходов E9.4-2),
    сбой декодирования, выход за limit, ВСЕ-НУЛЕВЫЕ байты
    (нули — данные, не код)."""
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
            if name == "jmp":   # прямой — кандидат; FF /4 — терминал
                if args[0][0] == "t":
                    pending.append(args[0][1])
                else:           # E9.4-2: таблица переходов из данных
                    pending.extend(_jtab(body, limit, args[0]))
                break
            if name == "jcc":
                pending.append(args[1][1])
            elif name == "call" and args[0][0] == "t":
                pending.append(args[0][1])
            a = nxt
    return ins

def _jtab(body, limit, op):
    """Таблица переходов (E9.4-2, SPEC/15 п. 3): косвенный jmp qword
    [rip+X] (X — в данных) даёт цели-кандидаты из данных. Читаются
    qword от X ПОДРЯД, пока значение — адрес кода (0 < v < limit);
    терминатор — первый non-code qword (0 или вне тела) либо конец
    тела (за target — виртуальные нули: вилка raw/bss). Регистровая/
    индексная форма (jmp r64, [base+idx]) — БЕЗ кандидатов (E9.4-1):
    цель = значение операнда, вычислить без исполнения нельзя."""
    if op[0] != "m" or op[6] is None or op[5] != 64 \
            or op[1] is not None or op[2] is not None:
        return []
    out = []
    off = op[6][1]
    while 0 <= off and off + 8 <= limit:
        v = _u64(body, off)
        if not 0 < v < limit:
            break
        out.append(v)
        off += 8
    return out

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

# ------------------------------------------------------------ разбор чужих
def parse_foreign(data):
    """Чужой EXE PE32+ -> словарь фактов моста (E9.4-3b, SPEC/15
    п. 10): исполняемая секция — по точке входа (первая секция
    виртуального диапазона входа; обязана иметь EXECUTE), спуск —
    в её теле от входа (семантика п. 3 та же: терминалы/тени/нули/
    таблицы переходов; граница — VirtualSize секции). Факты — для
    PEG v2: pe (все секции/импорты), code (слот секции кода),
    body/vsize/raw/entry_off/ins, target/bss (п. 7; вилка
    обобщена на FileAlignment образа — у семейства 0x200, значения
    те же). Семейных полей (module/stackcom/heapcom) НЕТ: у чужих
    образов нет шаблона pegen (заглушка/поля — дело PEG v2).
    Отказ — BridgeError. Порядок проверок: сигнатуры MZ/PE ->
    Machine/Magic x86-64 -> FileAlignment (степень 2) -> секция
    по входу -> EXECUTE -> длина raw в файле -> тело не пусто ->
    вход в raw-части -> спуск -> за VirtualSize -> target/bss."""
    try:
        pe = lab_pe.parse(data)
    except Exception as e:                     # noqa: BLE001 — любой крах
        raise BridgeError("не PE32+: не разбирается (%s)" % e)
    if not pe["mz"] or not pe["pe_sig_ok"]:
        raise BridgeError("не PE32+: нет сигнатур MZ/PE")
    if pe["machine"] != 0x8664 or pe["magic"] != 0x020B:
        raise BridgeError("не PE32+: Machine/Magic не x86-64")
    fa = pe["file_align"]
    if fa < 1 or fa & (fa - 1):
        raise BridgeError("FileAlignment %X не степень 2" % fa)
    entry = pe["addr_entry_point"]
    code = next((s for s in pe["sections"]
                 if s["vaddr"] <= entry < s["vaddr"] + s["vsize"]), None)
    if code is None:
        raise BridgeError("вход вне секций")
    if not (code["chars"] & 0x20000000):
        raise BridgeError("в секции входа нет EXECUTE")
    body = data[code["raw_ptr"]:code["raw_ptr"] + code["raw_size"]]
    if len(body) != code["raw_size"]:
        raise BridgeError("файл короче raw секции кода")
    if not any(body):
        raise BridgeError("пустая/нулевая секция кода")
    entry_off = entry - code["vaddr"]
    if entry_off >= len(body):
        raise BridgeError("вход в bss (вне raw-части)")
    vsize, raw = code["vsize"], code["raw_size"]
    ins = _sweep(_walk(body, entry_off, vsize))
    for a, (_nm, ln, _ar) in ins.items():
        if a + ln > vsize:
            raise BridgeError("инструкция @%X за VirtualSize" % a)
    nz = max(i for i, b in enumerate(body) if b)
    target = max([nz + 1, 1] + [a + ins[a][1] for a in ins])
    if (target + fa - 1) & ~(fa - 1) != raw:
        target = raw - (fa - 1)     # минимальная длина той же вилки (п. 7)
    if target > vsize:
        raise BridgeError("длина тела больше VirtualSize")
    return {
        "pe": pe, "code": code, "body": body, "vsize": vsize,
        "raw": raw, "target": target, "bss": vsize - target,
        "entry_off": entry_off, "ins": ins,
    }

# --------------------------------------------------- метки/импорты
def _import_map(fam, base=SECT):
    """Структуры импорта -> (labels, semantic, known_rva): offset ->
    имя метки (iat_*, d*) / ("DD"|"DQ", [значения]) с $ссылками /
    RVA -> имя. base — RVA секции кода (E9.4-3c-3: семья — SECT;
    чужой путь — vaddr секции кода; структуры вне тела — сырыми
    байтами). Представимость (E9.2-3b, SPEC/15 п. 4/6): метка НЕ
    создаётся строго внутри выжившей инструкции (наложение разрезов
    — невалидный b2); DQ с не-созданной меткой — сырыми байтами.
    """
    body, pe = fam["body"], fam["pe"]
    labels, semantic, known = {}, {}, {}
    imp = pe["imports"][0]
    iat_off = imp["iat_rva"] - base
    int_off = (imp["oft_rva"] or imp["iat_rva"]) - base
    name_off = imp["name_rva"] - base
    hints = [(fn, hr - base) for fn, hr in imp["funcs"]]
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
            labels.setdefault(h, "d%x" % (h + base))
            known[h + base] = labels[h]
    if not inside_ins(name_off):
        labels.setdefault(name_off, "d%x" % (name_off + base))
        known[name_off + base] = labels[name_off]
    if int_off != iat_off and not inside_ins(int_off):
        labels.setdefault(int_off, "d%x" % (int_off + base))
    if int_off in labels:
        known[int_off + base] = labels[int_off]
    if iat_off in labels:
        known[iat_off + base] = labels[iat_off]
    idt_off = pe["dd1_import_rva"] - base
    if 0 <= idt_off and idt_off + 20 <= limit:
        semantic[idt_off] = ("DD", [_dollar(_u32(body, idt_off + 4 * k),
                                            known) for k in range(5)])
    for itab in {iat_off, int_off}:
        rows = []
        for k in range(n + 1):
            v = _u64(body, itab + 8 * k)
            if v == 0 and k == n:
                t = "0"
            elif k < n and v == hints[k][1] + base \
                    and hints[k][1] in labels:
                t = "$" + labels[hints[k][1]]
            else:
                rows = None
                break
            rows.append((itab + 8 * k, t))
        if rows is not None:               # по записи на строку:
            for off, t in rows:            # метки слотов — между строк
                semantic[off] = ("DQ", [t])
    return labels, semantic, known

def _dollar(v, known):
    """dword -> $имя (если RVA известна) | hex."""
    s = known.get(v)
    return "$" + s if s else _hx(v)

# ------------------------------------------------------------ эмиссия b2
def _emit_lines(fam, mode=None, base=SECT):
    """Факты моста -> (строки BRICK v2, статистика). Чистый рендер.

    mode (срезы E9.2-3, SPEC/15 п. 10): None — канон (M-строки при
    точном воспроизведении enc + метки + семантика); "H" — H-строки
    с метками/семантикой (E9.2-3b); "RAW" — без них (E9.2-3a).
    base — RVA секции кода (E9.4-3c-3): имена меток l/d — RVA
    (семья и чужой путь с vaddr 0x1000 — одни и те же имена);
    $base — ТЕЛЕСНОЕ смещение -0x1000 (ABI brick SPEC/08: при
    vaddr != 0x1000 имя обозначает RVA vaddr-0x1000 — байты
    точны контролем повторного кодирования, пересмотр — при
    порте). Байто-точность круга — во всех режимах (H-строка —
    те же байты)."""
    body, ins = fam["body"], fam["ins"]
    limit = fam["target"]
    if mode == "RAW":
        labels, semantic = {}, {}
    else:
        labels, semantic, _known = _import_map(fam, base)
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
                        labels[off] = "l%x" % (off + base)
                    elif 0 <= off < limit and not inside_ins(off) \
                            and not inside_sem(off):
                        labels[off] = "d%x" % (off + base)
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

def emit_b2(data, mode=None):
    """EXE -> (текст BRICK v2, статистика); mode — срезы E9.2-3."""
    fam = parse_family(data)
    lines, stats = _emit_lines(fam, mode)
    return _b2_text(fam, lines), stats

def emit_peg(data):
    """EXE -> текст PEG v1 (регенерация обёртки, SPEC/07)."""
    return _peg_text(parse_family(data))

def emit_peg_v2(data):
    """Чужой EXE -> текст PEG v2 (E9.4-3c-2, SPEC/07 «Рост v2»):
    факты parse_foreign -> канон патчей (!pev2/!hdr/!body/!sec —
    рендер lab_bridge_text._peg2_text; H = min raw_ptr секций с raw).
    Отказы после проверок parse_foreign: нет секций с raw (защитная
    ветвь — пустой код отвергается раньше) / файл короче raw прочих
    секций (код цел, но сворачивать больше нечего — байто-точность
    круга невозможна)."""
    f = parse_foreign(data)
    pe = f["pe"]
    raws = [s for s in pe["sections"] if s["raw_size"] > 0]
    if not raws:
        raise BridgeError("нет секций с raw")
    H = min(s["raw_ptr"] for s in raws)
    for s in raws:
        if s["raw_ptr"] + s["raw_size"] > len(data):
            raise BridgeError("файл короче raw секции")
    return _peg2_text(f, data, H)

def emit_b2_foreign(data):
    """Чужой EXE -> (текст b2 тела секции кода, статистика) — E9.4-3c-3
    (SPEC/15 п. 10): parse_foreign -> канон п. 4-6 (M-строки при точном
    воспроизведении enc / H-фолбэк, метки l/d/iat_, семантика DD/DQ —
    только импорты ВНУТРИ тела; base = vaddr секции кода). Шапка —
    lab_bridge_text._b2_foreign_text (выводимые факты; БЕЗ module/
    stackcom/heapcom — их у чужих образов нет). Отказы — наследованные
    parse_foreign: эмиссия — чистый рендер над проверенными фактами."""
    f = parse_foreign(data)
    lines, stats = _emit_lines(f, None, f["code"]["vaddr"])
    return _b2_foreign_text(f, lines), stats

def bridge(data):
    """EXE -> (текст BRICK v2, текст PEG v1). Полный мост."""
    fam = parse_family(data)
    lines, _stats = _emit_lines(fam)
    return _b2_text(fam, lines), _peg_text(fam)
