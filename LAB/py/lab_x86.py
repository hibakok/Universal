"""lab_x86.py — декодер используемого подмножества x86-64 (SPEC/05).

Вход:  fetch(addr, n) -> int (little-endian), rip инструкции.
Выход: (имя, длина, аргументы) — semantic-кортеж для исполнителя
       (lab_cpu) и дизассемблера (lab_disasm).
Функция: декодировать одну инструкцию нашего подмножества;
         неизвестный опкод -> UnknownOpcode с адресом и байтами.

Операнды-дескрипторы:
  ('r', индекс_регистра, размер)  — регистр (индекс 0..15)
  ('m', base, index, scale, disp, размер, riprel) — память;
       base/index = None или индекс регистра; riprel = None или
       ('riprel', disp32) — цель = конец инструкции + disp32
       (вычисляется в конце декодирования)
  ('i', значение, размер)  — непосредственный
  ('t', абсолютный_адрес)  — цель перехода/вызова
Размеры: 8/16/32/64 бита.
"""
BYTE, WORD, DWORD, QWORD = 8, 16, 32, 64

REG64 = ["rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi", "rdi",
         "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
REG8 = ["al", "cl", "dl", "bl", "spl", "bpl", "sil", "dil",
        "r8b", "r9b", "r10b", "r11b", "r12b", "r13b", "r14b", "r15b"]
REG16 = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di",
         "r8w", "r9w", "r10w", "r11w", "r12w", "r13w", "r14w", "r15w"]

CC = ["o", "no", "b", "ae", "z", "nz", "be", "a",
      "s", "ns", "p", "np", "l", "ge", "le", "g"]

ALU = {0x00: "add", 0x08: "or", 0x20: "and", 0x28: "sub",
       0x30: "xor", 0x38: "cmp"}


class UnknownOpcode(ValueError):
    pass


def _s8(v):
    return v - 0x100 if v & 0x80 else v


def _s32(v):
    return v - 0x100000000 if v & 0x80000000 else v


def decode(fetch, rip):
    """Декодировать инструкцию по адресу rip. -> (имя, длина, args)."""
    pos = rip
    b = fetch(pos, 1)
    pos += 1
    rex = 0
    if 0x40 <= b <= 0x4F:
        rex = b
        b = fetch(pos, 1)
        pos += 1
    w = 8 if rex & 8 else 0
    rbit = (rex & 4) << 1   # REX.R -> +8 к полю reg
    xbit = (rex & 2) << 2   # REX.X -> +8 к индексу SIB
    bbit = (rex & 1) << 3   # REX.B -> +8 к rm/базе
    size = QWORD if w else DWORD
    riprel = None           # ('riprel', disp) если операнд rip-относителен

    if b == 0x0F:
        return _decode_0f(fetch, rip, pos, w, rbit, xbit, bbit)

    # --- ALU reg/mem формы (00..3B) ---
    base = b & 0xF8
    if base in ALU and (b & 7) < 4:
        name = ALU[base]
        opsize = BYTE if (b & 1) == 0 else size
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, opsize)
        pos = mem["pos"]
        riprel = mem["riprel"]
        args = (mem["op"], ("r", reg, opsize))
        if b & 2:  # бит направления d=1: reg <- rm
            args = (("r", reg, opsize), mem["op"])
        return _finish(name, rip, pos, args, riprel, fetch)
    # --- ALU AL/eAX + imm ---
    if b in (0x04, 0x0C, 0x24, 0x2C, 0x3C):  # AL, imm8
        name = ALU[b & 0xF8]
        imm = fetch(pos, 1)
        pos += 1
        return (name, pos - rip,
                (("r", 0, BYTE), ("i", imm, BYTE)))
    if b in (0x05, 0x0D, 0x25, 0x2D, 0x35, 0x3D):  # eAX, imm32
        name = ALU[b & 0xF8]
        imm = fetch(pos, 4)
        pos += 4
        val = _s32(imm) if w else imm
        return (name, pos - rip, (("r", 0, size), ("i", val, size)))
    # --- группы с modrm ---
    if b in (0x80, 0x81, 0x83):
        opsize = BYTE if b == 0x80 else size
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, opsize)
        pos = mem["pos"]
        riprel = mem["riprel"]
        name = {0: "add", 1: "or", 4: "and", 5: "sub", 6: "xor",
                7: "cmp"}.get(reg)
        if name is None:
            raise UnknownOpcode("группа %02X /%d @ %X" % (b, reg, rip))
        if b == 0x81:
            imm = fetch(pos, 4)
            pos += 4
            val = _s32(imm) if w else imm
        else:
            raw = fetch(pos, 1)
            pos += 1
            val = raw & 0xFF if b == 0x80 else _s8(raw)
        return _finish(name, rip, pos, (mem["op"], ("i", val, opsize)),
                       riprel, fetch)
    if b in (0x84, 0x85):  # test
        opsize = BYTE if b == 0x84 else size
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, opsize)
        pos = mem["pos"]
        riprel = mem["riprel"]
        return _finish("test", rip, pos, (mem["op"], ("r", reg, opsize)),
                       riprel, fetch)
    if b in (0x88, 0x89, 0x8A, 0x8B):  # mov
        opsize = BYTE if b in (0x88, 0x8A) else size
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, opsize)
        pos = mem["pos"]
        riprel = mem["riprel"]
        if b in (0x88, 0x89):
            args = (mem["op"], ("r", reg, opsize))
        else:
            args = (("r", reg, opsize), mem["op"])
        return _finish("mov", rip, pos, args, riprel, fetch)
    if b == 0x8D:  # lea
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, QWORD)
        pos = mem["pos"]
        riprel = mem["riprel"]
        return _finish("lea", rip, pos, (("r", reg, size), mem["op"]),
                       riprel, fetch)
    if b == 0x98:  # cdqe (REX.W) / cwde
        return "cdqe", pos - rip, (("r", 0, size),)
    if b == 0x99:  # cqo (REX.W) / cdq — знак rax -> rdx:rax
        return ("cqo" if w else "cdq"), pos - rip, ()
    if 0xB0 <= b <= 0xB7:  # mov r8, imm8
        reg = (b & 7) | bbit
        imm = fetch(pos, 1)
        pos += 1
        return "mov", pos - rip, (("r", reg, BYTE), ("i", imm, BYTE))
    if 0xB8 <= b <= 0xBF:  # mov r32,imm32 / r64,imm64 (REX.W)
        reg = (b & 7) | bbit
        if w:
            imm = fetch(pos, 8)
            pos += 8
            return "mov", pos - rip, (("r", reg, QWORD), ("i", imm, QWORD))
        imm = fetch(pos, 4)
        pos += 4
        return "mov", pos - rip, (("r", reg, DWORD), ("i", imm, DWORD))
    if b in (0xC0, 0xC1):  # сдвиг с imm8
        opsize = BYTE if b == 0xC0 else size
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, opsize)
        pos = mem["pos"]
        riprel = mem["riprel"]
        name = {0: "rol", 4: "shl", 5: "shr", 7: "sar"}.get(reg)
        if name is None:
            raise UnknownOpcode("сдвиг /%d @ %X" % (reg, rip))
        imm = fetch(pos, 1)
        pos += 1
        # счётчик сдвига: 64-бит маскируется 6 битами (REX.W),
        # прочие — 5 (правило Intel; найдено E6.2: shr rax,32)
        imm &= 0x3F if opsize == QWORD else 0x1F
        return _finish(name, rip, pos, (mem["op"], imm),
                       riprel, fetch)
    if b == 0xC3:
        return "ret", pos - rip, ()
    if b == 0xC6:  # mov rm8, imm8
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, BYTE)
        pos = mem["pos"]
        riprel = mem["riprel"]
        imm = fetch(pos, 1)
        pos += 1
        return _finish("mov", rip, pos, (mem["op"], ("i", imm, BYTE)),
                       riprel, fetch)
    if b == 0xC7:  # mov rm, imm32 (при W — знакорасширение)
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, size)
        pos = mem["pos"]
        riprel = mem["riprel"]
        imm = fetch(pos, 4)
        pos += 4
        val = _s32(imm) if w else imm
        return _finish("mov", rip, pos, (mem["op"], ("i", val, size)),
                       riprel, fetch)
    if b == 0xCC:
        return "int3", pos - rip, ()
    if b == 0xD3:  # сдвиг по CL
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, size)
        pos = mem["pos"]
        riprel = mem["riprel"]
        name = {0: "rol", 4: "shl", 5: "shr", 7: "sar"}.get(reg)
        if name is None:
            raise UnknownOpcode("сдвиг CL /%d @ %X" % (reg, rip))
        return _finish(name, rip, pos, (mem["op"], "cl"), riprel, fetch)
    if b == 0xE8:  # call rel32
        rel = _s32(fetch(pos, 4))
        pos += 4
        return "call", pos - rip, (("t", pos + rel),)
    if b == 0xE9:  # jmp rel32
        rel = _s32(fetch(pos, 4))
        pos += 4
        return "jmp", pos - rip, (("t", pos + rel),)
    if b == 0xEB:  # jmp rel8
        rel = _s8(fetch(pos, 1))
        pos += 1
        return "jmp", pos - rip, (("t", pos + rel),)
    if 0x50 <= b <= 0x57:  # push r64
        return "push", pos - rip, (("r", (b & 7) | bbit, QWORD),)
    if 0x58 <= b <= 0x5F:  # pop r64
        return "pop", pos - rip, (("r", (b & 7) | bbit, QWORD),)
    if 0x70 <= b <= 0x7F:  # jcc rel8
        rel = _s8(fetch(pos, 1))
        pos += 1
        return ("jcc", pos - rip, (CC[b & 0xF], ("t", pos + rel)))
    if b in (0xF6, 0xF7):  # группа F6/F7
        opsize = BYTE if b == 0xF6 else size
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, opsize)
        pos = mem["pos"]
        riprel = mem["riprel"]
        if reg == 3:
            return _finish("neg", rip, pos, (mem["op"],), riprel, fetch)
        if reg == 7 and b == 0xF7:  # idiv r/m (32/64; E6.4c)
            return _finish("idiv", rip, pos, (mem["op"],), riprel, fetch)
        raise UnknownOpcode("F6/F7 /%d @ %X" % (reg, rip))
    if b == 0xFF:  # группа FF
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, size)
        pos = mem["pos"]
        riprel = mem["riprel"]
        if reg == 0:
            return _finish("inc", rip, pos, (mem["op"],), riprel, fetch)
        if reg == 1:
            return _finish("dec", rip, pos, (mem["op"],), riprel, fetch)
        if reg == 2:
            return _finish("call", rip, pos, (mem["op"],), riprel, fetch)
        raise UnknownOpcode("FF /%d @ %X" % (reg, rip))
    raise UnknownOpcode("опкод %02X @ %X" % (b, rip))


def _decode_0f(fetch, rip, pos, w, rbit, xbit, bbit):
    b = fetch(pos, 1)
    pos += 1
    if 0x80 <= b <= 0x8F:  # jcc rel32 (все 16 условий)
        rel = _s32(fetch(pos, 4))
        pos += 4
        return "jcc", pos - rip, (CC[b & 0xF], ("t", pos + rel))
    if b in (0xB6, 0xB7):  # movzx
        srcsize = BYTE if b == 0xB6 else WORD
        size = QWORD if w else DWORD
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, srcsize)
        pos = mem["pos"]
        if mem["riprel"] is not None:
            mem = dict(mem)
            mem["op"] = _apply_riprel(mem["op"], pos, mem["riprel"], rip)
        return "movzx", pos - rip, (("r", reg, size), mem["op"])
    if b == 0xAF:  # imul r, r/m (двухоперандная; E6.4c): reg — приёмник
        size = QWORD if w else DWORD
        mod, reg, mem = _modrm(fetch, pos, rbit, xbit, bbit, size)
        pos = mem["pos"]
        riprel = mem["riprel"]
        return _finish("imul", rip, pos,
                       (("r", reg, size), mem["op"]), riprel, fetch)
    raise UnknownOpcode("0F %02X @ %X" % (b, rip))


def _apply_riprel(op, end_pos, riprel, rip):
    """Прописать абсолютную цель rip-относительной адресации."""
    if op[0] != "m":
        return op
    return ("m", op[1], op[2], op[3], op[4], op[5], ("abs", end_pos +
                                                     riprel[1]))


def _finish(name, rip, pos, args, riprel, fetch):
    """Завершить декодирование: если есть rip-относительный операнд —
    вычислить его абсолютную цель от КОНЦА инструкции."""
    if riprel is None:
        return name, pos - rip, args
    newargs = tuple(_apply_riprel(a, pos, riprel, rip) for a in args)
    return name, pos - rip, newargs


def _modrm(fetch, pos, rbit, xbit, bbit, opsize):
    """Разбор modrm (+SIB, +disp). -> (mod, reg, описание)."""
    m = fetch(pos, 1)
    pos += 1
    mod = m >> 6
    reg = ((m >> 3) & 7) | rbit
    rm = m & 7
    if mod == 3:
        return mod, reg, {"op": ("r", rm | bbit, opsize), "pos": pos,
                          "riprel": None}
    base = None
    index = None
    scale = 1
    disp = 0
    riprel = None
    if rm == 4:  # SIB
        s = fetch(pos, 1)
        pos += 1
        scale = 1 << (s >> 6)
        idx = (s >> 3) & 7
        index = (idx | xbit) if (idx != 4 or xbit) else None
        bas = s & 7
        if mod == 0 and bas == 5:
            disp = fetch(pos, 4)  # беззнаковое disp32, без базы
            pos += 4
        else:
            base = bas | bbit
            if mod == 1:
                disp = _s8(fetch(pos, 1))
                pos += 1
            elif mod == 2:
                disp = _s32(fetch(pos, 4))
                pos += 4
    elif rm == 5 and mod == 0:  # rip-относительно
        disp = _s32(fetch(pos, 4))
        pos += 4
        riprel = ("riprel", disp)
    else:
        base = rm | bbit
        if mod == 1:
            disp = _s8(fetch(pos, 1))
            pos += 1
        elif mod == 2:
            disp = _s32(fetch(pos, 4))
            pos += 4
    op = ("m", base, index, scale, disp, opsize, None)
    return mod, reg, {"op": op, "pos": pos, "riprel": riprel}
