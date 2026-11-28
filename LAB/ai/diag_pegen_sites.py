#!/usr/bin/env python3
"""diag_pegen_sites.py — диагностика мест пределов pegen.exe (E9.5-1a):
декодирует тело, классифицирует ВСЕ rip-ссылки по символам bss (v1-ячейки,
filebuf, imagebuf, zeropad, ячейки v2, outbuf/spantab/sectab/secdata/rawtab)
и находит инструкции с иммедиатами пределов. Частный инструмент (LAB/ai/)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "LAB", "py"))

import lab_atom                            # noqa: E402
import lab_x86                             # noqa: E402

BODY = 0x1544
DELTA = 0x7CA                     # сдвиг bss после порта v2 (E9.4-4b-4)

# ТЕКУЩИЕ символы (телесные смещения; bss начинается с 0x1544):
SYMS = [                         # (имя, начало, конец) — по возрастанию
    ("v1data", 0x7AD, 0xD7A),        # таблицы/строки/шаблон v1 — файл
    ("v2code", 0xD7A, 0x1512),       # код v2 — файл
    ("v2data", 0x1512, 0x1544),      # v2kwtab+строки — файл
    ("v1bss", 0x1544, 0xF6C + DELTA),            # ячейки v1 + fname_out
    ("filebuf", 0xF6C + DELTA, 0x10F6C + DELTA),
    ("imagebuf", 0x10F6C + DELTA, 0x30F6C + DELTA),
    ("zeropad", 0x30F6C + DELTA, 0x3117C + DELTA),
    ("v2cells", 0x3117C + DELTA, 0x3117C + DELTA + 60),
    ("outbuf", 0x3117C + DELTA + 60, 0x3117C + DELTA + 60 + 0x40000),
    ("spantab", 0x3117C + DELTA + 60 + 0x40000,
     0x3117C + DELTA + 60 + 0x40200),
    ("sectab", 0x3117C + DELTA + 60 + 0x40200,
     0x3117C + DELTA + 60 + 0x40A00),
    ("secdata", 0x3117C + DELTA + 60 + 0x40A00,
     0x3117C + DELTA + 60 + 0x42A00),
    ("rawtab", 0x3117C + DELTA + 60 + 0x42A00, 0x7C382),
]
NO_MOVE = {"v1data", "v2code", "v2data", "v1bss", "filebuf"}


def classify(t):
    for name, lo, hi in SYMS:
        if lo <= t < hi:
            return name
    return None


def main():
    hex_t = open(os.path.join(ROOT, "KERNEL/L0-PEGEN/pegen.hex"),
                 encoding="utf-8").read()
    body = lab_atom.assemble(hex_t)
    assert len(body) == BODY, hex(len(body))
    fetch = lambda a, n: int.from_bytes(body[a:a + n], "little")
    riprefs = []          # (сайт, имя_символа, цель, имя_инстр)
    imms = []             # (сайт, смещение_imm, значение, имя_инстр)
    for lo, hi in ((0, 0x7AD), (0xD7A, 0x1512)):
        i = lo
        while i < hi:
            name, ln, args = lab_x86.decode(fetch, i)
            bs = body[i:i + ln]
            for arg in args:
                if (isinstance(arg, tuple) and len(arg) >= 7 and
                        isinstance(arg[6], tuple) and arg[6][0] == "abs"):
                    t = arg[6][1]
                    if t >= 0x7AD:            # интересует только bss/данные
                        riprefs.append((i, classify(t), t, name))
            # dword-окна внутри инструкции — кандидаты imm32/disp32
            for off in range(1, ln - 2):
                v = int.from_bytes(bs[off:off + 4], "little")
                if v in (0x20001, 0x20000, 0x10001, 0x10000, 0x40000,
                         0x2000, 64, 128, 0x210):
                    imms.append((i, off, v, name, ln))
            i += ln
    print("=== rip-ссылки в bss/данные (сайт, символ, цель) ===")
    for i, sym, t, name in riprefs:
        print("@%04X %-9s -> %06X  %s" % (i, sym or "?", t, name))
    print("\n=== dword-кандидаты иммедиатов ===")
    for i, off, v, name, ln in imms:
        print("@%04X +%-2d = %-8X %-24s (len %d)" % (i, off, v, name, ln))


if __name__ == "__main__":
    main()
