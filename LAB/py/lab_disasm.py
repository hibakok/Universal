"""lab_disasm.py — дизассемблер подмножества x86-64 (по декодеру lab_x86).

Вход:  диапазон адресов образа + fetch, либо трасса rip-ов из CPU.
Выход: строки «адрес  мнемоника  операнды» (list[str]).
Функция: человеко-читаемая печать инструкций для VERIFY-журналов;
         проверка покрытия (ни одной UnknownOpcode на исполненном пути).
"""
import lab_x86

R64, R8, R16 = lab_x86.REG64, lab_x86.REG8, lab_x86.REG16


def render(fetch, rip, name, args):
    """Одна инструкция -> строка мнемоники."""
    if name == "jcc":
        return "j%s %X" % (args[0], args[1][1])
    if name in ("jmp",):
        return "jmp %X" % args[0][1]
    if name == "call" and args[0][0] == "t":
        return "call %X" % args[0][1]
    if name == "call":
        return "call [%s]" % _mem(args[0])
    if name in ("ret", "int3"):
        return name
    if name == "push" or name == "pop":
        return "%s %s" % (name, _reg(args[0]))
    if name == "movzx":
        return "movzx %s, %s" % (_reg(args[0]), _src(args[1]))
    if name == "lea":
        return "lea %s, [%s]" % (_reg(args[0]), _memtext(args[1]))
    if name == "cdqe":
        return "cdqe"
    if name in ("shl", "shr", "rol", "sar"):
        cnt = "cl" if args[1] == "cl" else hex(args[1])
        return "%s %s, %s" % (name, _dst(args[0]), cnt)
    if name in ("inc", "dec", "neg"):
        return "%s %s" % (name, _dst(args[0]))
    # двухоперандные: mov/add/sub/and/or/xor/cmp/test
    return "%s %s, %s" % (name, _dst(args[0]), _src(args[1]))


def _reg(op):
    _, idx, size = op
    if size == 8:
        return R8[idx]
    if size == 16:
        return R16[idx]
    if size == 32:
        return R64[idx].replace("r", "e", 1) if idx >= 8 else \
            ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"][idx]
    return R64[idx]


def _dst(op):
    return _reg(op) if op[0] == "r" else "[%s]" % _memtext(op)


def _src(op):
    if op[0] == "i":
        return hex(op[1])
    return _dst(op)


def _mem(op):
    """Краткая форма rip-относительной памяти (для call [rip+X])."""
    _, b, i, sc, disp, _sz, rip = op
    if rip is not None:
        return "rip+%X -> %X" % (rip[1] & 0xFFFFFFFF, rip[1])
    return _memtext(op)


def _memtext(op):
    _, b, i, sc, disp, _sz, rip = op
    if rip is not None:
        return "rip->%X" % rip[1]
    parts = []
    if b is not None:
        parts.append(R64[b])
    if i is not None:
        parts.append("%s*%d" % (R64[i], sc) if sc > 1 else R64[i])
    if disp or not parts:
        parts.append(hex(disp))
    return "+".join(parts)


def disassemble_range(fetch, start, end):
    """Линейный дизассемблинг диапазона; останавливается на первой
    неизвестной инструкции (возвращает список строк + адрес сбоя)."""
    out, rip = [], start
    while rip < end:
        try:
            name, length, args = lab_x86.decode(fetch, rip)
        except lab_x86.UnknownOpcode as e:
            return out, rip
        out.append("%08X  %s" % (rip, render(fetch, rip, name, args)))
        rip += length
    return out, None


def disassemble_trace(fetch, trace, cache):
    """Дизассемблинг исполненной трассы (rip -> строка)."""
    seen, out = set(), []
    for rip in trace:
        if rip in seen:
            continue
        seen.add(rip)
        name, length, args = cache[rip]
        out.append("%08X  %s" % (rip, render(fetch, rip, name, args)))
    return out


if __name__ == "__main__":
    import sys
    import lab_pe
    pe = lab_pe.load(sys.argv[1])
    img = bytearray((pe["size_of_image"] + 0xFFF) & ~0xFFF)
    raw = open(sys.argv[1], "rb").read()
    img[0:pe["size_of_headers"]] = raw[:pe["size_of_headers"]]
    va, ptr = pe["sec_vaddr"], pe["sec_raw_ptr"]
    img[va:va + pe["sec_raw_size"]] = raw[ptr:ptr + pe["sec_raw_size"]]
    base = pe["image_base"]
    fetch = lambda a, n: int.from_bytes(
        img[a - base:a - base + n], "little")
    lines, fail = disassemble_range(fetch, base + pe["addr_entry_point"],
                                    base + va + int(sys.argv[2], 0)
                                    if len(sys.argv) > 2 else
                                    base + va + 0x200)
    for l in lines:
        print(l)
    if fail:
        print("! сбой на %X" % fail, file=sys.stderr)
