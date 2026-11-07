"""lab_pegen.py — оракул PEG v1 (SPEC/07): тело + PEG -> готовый EXE.

Вход:  тело секции (bytes), текст PEG (str).
Выход: bytes готового PE32+; ValueError при плохом PEG.
Функция: независимая от pegen.exe сборка EXE: константный каркас
         заголовков SPEC/04 + патчи полей по директивам SPEC/07.

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
    """Тело секции + PEG -> EXE (bytes). Формулы — SPEC/07."""
    p = parse_peg(peg_text)
    imgsize = len(body)
    if imgsize > 0x10000:
        raise ValueError("образ больше 64 КиБ")
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


def load_peg(path):
    with open(path, "rb") as f:
        return f.read().decode("latin1")


if __name__ == "__main__":
    import sys
    exe = wrap(open(sys.argv[1], "rb").read(), load_peg(sys.argv[2]))
    open(sys.argv[3], "wb").write(exe)
    print("OK %d байт" % len(exe))
