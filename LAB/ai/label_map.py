"""label_map.py — карта меток wall.brick (RVA) для BYTECODE.md (LAB/ai).

Вход:  KERNEL/L2-WALL/wall.brick (запуск из корня репозитория).
Выход:  метка -> RVA (клон логики пасса 1 lab_brick.assemble — только
       длины строк, без правки оракула) + список всех меток по
       возрастанию для карты ветвей BYTECODE.md.
Функция: диагностический инструмент обновления BYTECODE.md при
         пересборке wall.exe (E6.4c-3/2: прецедент — карта ветвей
         с точными RVA по трассировке меток).
"""
import sys

sys.path.insert(0, "LAB/py")
import lab_brick
from lab_brick import _Parser, _line_h, _line_d, _err, _expect_eol, BASE_LABEL


def labels_of(text):
    buf = text + b"\x00"
    labels = {"base": BASE_LABEL}
    cursor, p, lineno = 0, 0, 1
    while True:
        c = buf[p]
        if c == 0:
            break
        if c == 0x0A:
            p += 1
            lineno += 1
            continue
        if c == 0x0D:
            p += 1
            continue
        if c == 0x3B:
            while buf[p] not in (0, 0x0A):
                p += 1
            continue
        if c == 0x3A:
            p += 1
            ps = _Parser(buf, p)
            addr, n = ps.name()
            p = ps.p
            _expect_eol(buf, p, lineno)
            name = buf[addr:addr + n].decode()
            labels[name] = cursor
            while buf[p] not in (0, 0x0A):
                p += 1
            continue
        if c == 0x48:
            p += 1
            out = bytearray(0x20010)
            cursor = _line_h(buf, p, 1, cursor, labels, out, lineno)
            while buf[p] not in (0, 0x0A):
                p += 1
            continue
        if c == 0x44:
            p += 1
            kind, cursor, filelen = _line_d(buf, p, 1, cursor, 0, labels,
                                            bytearray(0x20010), lineno)
            while buf[p] not in (0, 0x0A):
                p += 1
            continue
        _err(lineno)
    return labels


text = open("KERNEL/L2-WALL/wall.brick", "rb").read()
labs = labels_of(text)
want = ["entry", "pass0", "pass1", "pass2", "p1_line", "p2_line",
        "p1s_brk", "p2s_break", "p2s_continue", "p2s_end", "p2s_while",
        "kw_lookup", "p_mdm", "emit_imul", "emit_divmod", "digits",
        "kwtab", "strblob", "idt", "scalars", "hint_gsh", "dll_name",
        "emit_jmp_line", "fail_format"]
for w in want:
    if w in labs:
        print("%-14s %X" % (w, 0x1000 + labs[w]))
    else:
        print("%-14s ?" % w)
print("всего меток (без base):", len(labs) - 1)
