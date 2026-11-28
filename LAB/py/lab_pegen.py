"""lab_pegen.py — оракул PEG v1/v2 (SPEC/07): тело + PEG -> готовый EXE.

Вход:  тело секции (bytes), текст PEG (str).
Выход: bytes готового PE32+; ValueError при плохом PEG.
Функция: независимая от pegen.exe сборка EXE. v1 (образы семейства):
         константный каркас заголовков SPEC/04 + патчи полей по
         директивам. v2 (E9.4-3c, чужие образы PE32+): нули + патчи
         !hdr/!sec + тело секции кода !body — диспетчер wrap() по
         первой директиве (v2 начинается с !pev2; v1-тексты ведут
         себя как раньше — нейтральность T-E9-30).

Каркас SKELETON — побайтовый снимок константной части заголовков,
одинаковой у всех шести артефактов E0–E5 (проверено lab_pe.py:
Machine/Magic/alignment/Subsystem/секция — инварианты SPEC/04;
артефакты исполняются реальным Windows). Патчуемые поля обнулены.
"""
import struct

SKELETON = bytes.fromhex(
    "4d5a90000300000004000000ffff0000b800000000000000400000000000000000000000"
    "000000000000000000000000000000000000000000000000800000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000050450000648601000000000000000000"
    "00000000f00022000b020100000000000000000000000000000000000010000000000040"
    "010000000010000000020000060000000000010006000000000000000000000000020000"
    "000000000300000000001000000000000000000000000000000010000000000000000000"
    "000000000000000010000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000"
    "00000000000000000000000000000000000000000000000000000000000000002e746578"
    "7400000000000000001000000000000000000000000000000000000000000000200000e0"
    "000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000"
    "0000000000000000"
)

assert len(SKELETON) == 0x200, len(SKELETON)


def parse_peg(text):
    """PEG v1 -> dict параметров. Строго по SPEC/07."""
    params = {"module": None, "entry": None, "idata": None, "iat": None,
              "bss": 0, "stackcom": 0x1000, "heapcom": 0x1000}
    for lineno, raw in enumerate(text.split("\n"), 1):
        line = raw.rstrip("\r").strip()
        if not line or line.startswith(";"):
            continue
        if not line.startswith("!"):
            raise ValueError("строка %d: нет '!'" % lineno)
        parts = line[1:].split()
        key, vals = parts[0], parts[1:]
        if key == "module":
            if not vals or not (1 <= len(vals[0]) <= 31):
                raise ValueError("строка %d: плохое имя модуля" % lineno)
            params["module"] = vals[0]
            continue
        if key not in ("entry", "idata", "iat", "bss", "stackcom", "heapcom"):
            raise ValueError("строка %d: неизвестная директива %r" %
                             (lineno, key))
        nums = []
        for v in vals:
            if not v or len(v) > 8 or any(c not in "0123456789ABCDEF"
                                          for c in v):
                raise ValueError("строка %d: плохое значение %r" %
                                 (lineno, v))
            nums.append(int(v, 16))
        if key in ("idata", "iat"):
            if len(nums) != 2:
                raise ValueError("строка %d: %s требует 2 значения" %
                                 (lineno, key))
            params[key] = nums
        else:
            if len(nums) != 1:
                raise ValueError("строка %d: %s требует 1 значение" %
                                 (lineno, key))
            params[key] = nums[0]
    for must in ("module", "entry", "idata", "iat"):
        if params[must] is None:
            raise ValueError("нет обязательной директивы !%s" % must)
    return params


def wrap(body, peg_text):
    """Тело + PEG -> EXE (bytes). Диспетчер версий: v2 — если первая
    директива !pev2 (чужие образы, E9.4-3c), иначе v1 (семья,
    формулы SPEC/07)."""
    d = _first_directive(peg_text)
    if d is not None and d[0] == "pev2":
        return wrap2(body, peg_text)
    p = parse_peg(peg_text)
    imgsize = len(body)
    if imgsize > 0x100000:
        raise ValueError("образ больше 1 МиБ (E9.5-1: тело brick — план"
                         " E9.5-2; было 128 КиБ — E6.4g-3, до этого"
                         " 64 КиБ)")
    vsize = imgsize + p["bss"]
    raw_size = _align(imgsize, 0x200)
    hdr = bytearray(SKELETON)
    stub = b"Universal L0 " + p["module"].encode("latin1") + \
        b". No DOS support.\r\n$"
    if 0x40 + len(stub) > 0x80:
        raise ValueError("имя модуля длиннее заглушки DOS")
    hdr[0x40:0x40 + len(stub)] = stub
    _u32(hdr, 0x9C, raw_size)                        # SizeOfCode
    _u32(hdr, 0xA8, p["entry"])                      # точка входа
    _u32(hdr, 0xD0, _align(vsize, 0x1000) + 0x1000)  # SizeOfImage
    _u32(hdr, 0xE8, p["stackcom"])                   # фиксация стека
    _u32(hdr, 0xF8, p["heapcom"])                    # фиксация кучи
    _u32(hdr, 0x110, p["idata"][0])                  # DD[1] RVA
    _u32(hdr, 0x114, p["idata"][1])                  # DD[1] размер
    _u32(hdr, 0x168, p["iat"][0])                    # DD[12] RVA
    _u32(hdr, 0x16C, p["iat"][1])                    # DD[12] размер
    _u32(hdr, 0x190, vsize)                          # VirtualSize
    _u32(hdr, 0x198, raw_size)                       # SizeOfRawData
    _u32(hdr, 0x19C, 0x200)                          # PointerToRawData
    return bytes(hdr) + body + b"\x00" * (raw_size - imgsize)


def _align(x, a):
    return (x + a - 1) & ~(a - 1)


def _u32(buf, off, val):
    buf[off:off + 4] = struct.pack("<I", val)


# ------------------------------------------------------------ PEG v2
def _first_directive(text):
    """Первая директива файла (пустые/';'строки пропускаются) ->
    (имя, [значения]) | ("", []) | None. Граница версий: v2
    начинается с !pev2 (SPEC/07 «Рост v2»)."""
    for raw in text.split("\n"):
        line = raw.rstrip("\r").strip()
        if not line or line.startswith(";"):
            continue
        if not line.startswith("!"):
            return ("", [])
        parts = line[1:].split()
        return (parts[0], parts[1:])
    return None


def _hex_val(v, lineno, what):
    """Значение в стиле v1: 1..8 ЗАГЛАВНЫХ hex-цифр -> int."""
    if not v or len(v) > 8 or any(c not in "0123456789ABCDEF" for c in v):
        raise ValueError("строка %d: плохое %s %r" % (lineno, what, v))
    return int(v, 16)


def _hex_blob(v, lineno):
    """Блоб v2: чётное число ЗАГЛАВНЫХ hex-цифр, 1..64 байта."""
    if not v or len(v) > 128 or len(v) % 2 or \
            any(c not in "0123456789ABCDEF" for c in v):
        raise ValueError("строка %d: плохой блоб HEX %r" % (lineno, v[:16]))
    return bytes.fromhex(v)


def parse_peg_v2(text):
    """PEG v2 -> dict: H (область заголовков), hdr/сек-патчи, !body.
    Первая директива — ОБЯЗАНА быть !pev2 (SPEC/07 «Рост v2»);
    дальнейший порядок свободный; повторы pev2/body — ошибка."""
    p = {"H": None, "hdr": [], "body": None, "sec": []}
    seen_body = False
    for lineno, raw in enumerate(text.split("\n"), 1):
        line = raw.rstrip("\r").strip()
        if not line or line.startswith(";"):
            continue
        if not line.startswith("!"):
            raise ValueError("строка %d: нет '!'" % lineno)
        parts = line[1:].split()
        key, vals = parts[0], parts[1:]
        if p["H"] is None:
            if key != "pev2" or len(vals) != 1:
                raise ValueError("строка %d: v2 начинается с !pev2 <H>"
                                 % lineno)
            p["H"] = _hex_val(vals[0], lineno, "H")
        elif key == "pev2":
            raise ValueError("строка %d: повтор !pev2" % lineno)
        elif key == "hdr":
            if len(vals) != 2:
                raise ValueError("строка %d: !hdr <off> <HEX>" % lineno)
            p["hdr"].append((_hex_val(vals[0], lineno, "off"),
                             _hex_blob(vals[1], lineno)))
        elif key == "body":
            if len(vals) != 1:
                raise ValueError("строка %d: !body <n>" % lineno)
            if seen_body:
                raise ValueError("строка %d: повтор !body" % lineno)
            seen_body = True
            p["body"] = _hex_val(vals[0], lineno, "n")
        elif key == "sec":
            if len(vals) != 3:
                raise ValueError("строка %d: !sec <n> <off> <HEX>" % lineno)
            p["sec"].append((_hex_val(vals[0], lineno, "n"),
                             _hex_val(vals[1], lineno, "off"),
                             _hex_blob(vals[2], lineno)))
        else:
            raise ValueError("строка %d: неизвестная директива %r"
                             % (lineno, key))
    if p["H"] is None:
        raise ValueError("нет директив (v2 начинается с !pev2 <H>)")
    if not seen_body:
        raise ValueError("нет обязательной директивы !body")
    return p


def _u16b(b, o):
    return struct.unpack("<H", b[o:o + 2])[0]


def _u32b(b, o):
    return struct.unpack("<I", b[o:o + 4])[0]


def wrap2(body, peg_text):
    """Тело секции кода + PEG v2 -> чужой EXE (bytes). Сборка —
    SPEC/07 «Рост v2»: область заголовков (нули + патчи !hdr)
    самоописывает образ (MZ/e_lfanew/PE/таблица секций), тело
    пишется в raw секции !body, патчи !sec — в сырые области
    прочих секций; всё непокрытое — нули."""
    p = parse_peg_v2(peg_text)
    if p["H"] < 0x40:
        raise ValueError("v2: H %X меньше DOS-заголовка" % p["H"])
    hdr = bytearray(p["H"])
    spans = []
    for off, blob in p["hdr"]:
        if off + len(blob) > p["H"]:
            raise ValueError("!hdr @%X: патч за границами области"
                             " заголовков" % off)
        for s, e in spans:
            if off < e and s < off + len(blob):
                raise ValueError("!hdr @%X: наложение патчей" % off)
        spans.append((off, off + len(blob)))
        hdr[off:off + len(blob)] = blob
    hdr = bytes(hdr)
    # самОописание собранной области (только структура, не семантика)
    if hdr[0:2] != b"MZ":
        raise ValueError("v2: нет MZ")
    lfa = _u32b(hdr, 0x3C)
    if lfa + 4 > p["H"] or hdr[lfa:lfa + 4] != b"PE\x00\x00":
        raise ValueError("v2: нет PE-сигнатуры в области заголовков")
    nsec = _u16b(hdr, lfa + 6)
    opt = _u16b(hdr, lfa + 0x14)
    tbl = lfa + 4 + 0x14 + opt
    if nsec == 0 or tbl + 40 * nsec > p["H"]:
        raise ValueError("v2: таблица секций вне области заголовков")
    secs = [(_u32b(hdr, tbl + 40 * i + 20), _u32b(hdr, tbl + 40 * i + 16))
            for i in range(nsec)]     # (raw_ptr @+0x14, raw_size @+0x10)
    # сырые области: после заголовков, без взаимных наложений
    ranges = []
    for rp, rs in secs:
        if rs == 0:
            continue
        if rp < p["H"]:
            raise ValueError("v2: raw секции @%X залезает в заголовки" % rp)
        for s, e in ranges:
            if rp < e and s < rp + rs:
                raise ValueError("v2: наложение raw областей секций")
        ranges.append((rp, rp + rs))
    n = p["body"]
    if n >= nsec:
        raise ValueError("v2: !body %X за пределами таблицы секций" % n)
    brp, brs = secs[n]
    if brs < len(body):
        raise ValueError("v2: тело %d больше raw секции !body (%X)"
                         % (len(body), brs))
    out = bytearray(max([p["H"]] + [e for _s, e in ranges]))
    out[0:p["H"]] = hdr
    out[brp:brp + len(body)] = body
    per = {}
    for i, off, blob in p["sec"]:
        if i >= nsec:
            raise ValueError("v2: !sec %X за пределами таблицы секций" % i)
        if i == n:
            raise ValueError("v2: !sec на секции !body")
        rp, rs = secs[i]
        if rs == 0 or off + len(blob) > rs:
            raise ValueError("v2: !sec за границами raw секции %X" % i)
        per.setdefault(i, []).append((off, off + len(blob)))
        out[rp + off:rp + off + len(blob)] = blob
    for i, rr in per.items():               # наложения внутри секции
        rr.sort()
        for a, b in zip(rr, rr[1:]):
            if b[0] < a[1]:
                raise ValueError("v2: наложение !sec в секции %X" % i)
    return bytes(out)


def load_peg(path):
    with open(path, "rb") as f:
        return f.read().decode("latin1")


if __name__ == "__main__":
    import sys
    exe = wrap(open(sys.argv[1], "rb").read(), load_peg(sys.argv[2]))
    open(sys.argv[3], "wb").write(exe)
    print("OK %d байт" % len(exe))
