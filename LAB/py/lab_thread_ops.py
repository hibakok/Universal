"""lab_thread_ops.py — построители тел инструкций (lab_thread, часть 2).

Вход:  CPU, args инструкции (семантический кортеж lab_x86.decode).
Выход: каждый построитель -> (pre, body) — строки исходника замыкания
       fn(nrip) ПОД КОНКРЕТНУЮ форму операндов (см. lab_thread._gen),
       либо None — форма не специализируется (универсальный путь).
Функция: тела ПОБАЙТОВО повторяют lab_cpu_ops._op_* (референсную
       семантику): те же выражения над теми же сырыми значениями,
       маски стоят ровно там же. Выделен из lab_thread.py по лимиту
       500 строк (E6.4d-5/0); хелперы операндов — в lab_thread.
"""
from lab_thread import (_SZ, _CCE, _bits, _rreg, _wreg, _addrp, _read,
                        _write, _scan_read, _scan_write)

# --- построители тел инструкций (выражения == lab_cpu._op_*) ---

def _alu(cpu, args, sym, wr):
    """add/sub/cmp и and/or/xor/test: (a sym b) с флагами; wr — запись."""
    if len(args) != 2 or args[0][0] == "i":
        return None
    if args[0][0] == "m" and args[1][0] == "m":
        return None    # двух mem-операндов не бывает (инвариант x86);
                       # иначе чтения делят имя buf — НЕ поддерживается
    m, s, _n, _c = _SZ[_bits(args[0])]
    pre, la, ea = _read(cpu, args[0], "a")
    p2, lb, eb = _read(cpu, args[1], "b")
    body = la + lb
    if ea != "a":
        body.append("a = %s" % ea)
    if eb != "b":
        body.append("b = %s" % eb)
    if sym == "+":
        body.append("s = a + b")           # сумма — один раз
        body.append("res = s & %s" % m)
    else:
        body.append("res = (a %s b) & %s" % (sym, m))
    body.append("fl[0] = 1 if res == 0 else 0")
    body.append("fl[2] = (res >> %d) & 1" % s)
    if sym in "&|^":
        body.append("fl[1] = 0")
        body.append("fl[3] = 0")
    else:
        if sym == "+":
            body.append("fl[1] = 1 if s > %s else 0" % m)
            ofc = "sa == sb and fl[2] != sa"
        else:
            body.append("fl[1] = 1 if a < b else 0")
            ofc = "sa != sb and fl[2] != sa"
        body.append("sa = (a >> %d) & 1" % s)
        body.append("sb = (b >> %d) & 1" % s)
        body.append("fl[3] = 1 if (%s) else 0" % ofc)
    if wr:
        p3, lw = _write(cpu, args[0], "res")
        return pre + p2 + p3, body + lw + ["return nrip"]
    return pre + p2, body + ["return nrip"]


def _b_mov(cpu, args):
    """mov/movzx: put(dst, get(src)) — флаги не трогаются."""
    if len(args) != 2 or args[0][0] == "i":
        return None
    if args[0][0] == "m" and args[1][0] == "m":
        return None                      # в подмножестве не бывает
    pre, lr, er = _read(cpu, args[1], "v")
    p2, lw = _write(cpu, args[0], er)
    return pre + p2, lr + lw + ["return nrip"]


def _b_lea(cpu, args):
    """lea: put(reg, _opaddr(mem)) — адрес, без обращения к памяти."""
    if len(args) != 2 or args[0][0] != "r" or args[1][0] != "m":
        return None
    kind, v = _addrp(args[1])
    val = repr(v) if kind == "const" else v
    return [], [_wreg(args[0], val), "return nrip"]


def _b_neg(cpu, args):
    if len(args) != 1 or args[0][0] == "i":
        return None
    m, s, _n, _c = _SZ[_bits(args[0])]
    pre, lr, er = _read(cpu, args[0], "a")
    p2, lw = _write(cpu, args[0], "res")
    body = lr + ([] if er == "a" else ["a = %s" % er]) + [
        "fl[1] = 1 if a != 0 else 0",
        "res = (-a) & %s" % m,
        "fl[0] = 1 if res == 0 else 0",
        "fl[2] = (res >> %d) & 1" % s,
        "fl[3] = 1 if a == (1 << %d) else 0" % s]
    return pre + p2, body + lw + ["return nrip"]


def _incdec(cpu, args, sym):
    """inc/dec: флаги как add/sub с 1, НО cf сохраняется."""
    if len(args) != 1 or args[0][0] == "i":
        return None
    m, s, _n, _c = _SZ[_bits(args[0])]
    pre, lr, er = _read(cpu, args[0], "a")
    p2, lw = _write(cpu, args[0], "res")
    body = lr + ([] if er == "a" else ["a = %s" % er]) + [
        "cf0 = fl[1]",
        "res = (a %s 1) & %s" % (sym, m),
        "fl[0] = 1 if res == 0 else 0",
        "fl[2] = (res >> %d) & 1" % s]
    if sym == "+":
        body.append("fl[1] = 1 if (a + 1) > %s else 0" % m)
        ofc = "sa == sb and fl[2] != sa"
    else:
        body.append("fl[1] = 1 if a < 1 else 0")
        ofc = "sa != sb and fl[2] != sa"
    body += ["sa = (a >> %d) & 1" % s,
             "sb = (1 >> %d) & 1" % s,
             "fl[3] = 1 if (%s) else 0" % ofc,
             "fl[1] = cf0"]
    return pre + p2, body + lw + ["return nrip"]


def _b_shift(cpu, args, kind):
    """shl/shr/sar/rol: imm (маскировано декодером) или 'cl'."""
    if len(args) != 2 or args[0][0] == "i":
        return None
    op, cnt = args
    size = _bits(op)
    m, s, _n, _c = _SZ[size]
    pre, lr, er = _read(cpu, op, "a")
    rd = lr + ([] if er == "a" else ["a = %s" % er])
    p2, lw = _write(cpu, op, "val" if kind == "sar" else "res")
    if cnt == "cl":
        head = ["cnt = regs[1] & %s" % ("0x3F" if size == 64 else
                                        "0x1F"), "if cnt:"]
        cvar = "cnt"
    elif isinstance(cnt, int):
        if cnt == 0:
            return [], ["return nrip"]   # флаги/операнд не трогаются
        head = []
        cvar = str(cnt)
    else:
        return None
    if kind == "shl":
        core = ["full = a << %s" % cvar,
                "res = full & %s" % m,
                "fl[1] = (full >> %d) & 1" % size,   # cf — бит ВЫШЕ size
                "fl[0] = 1 if res == 0 else 0",
                "fl[2] = (res >> %d) & 1" % s]
    elif kind == "shr":
        core = ["fl[1] = (a >> (%s - 1)) & 1" % cvar,
                "res = a >> %s" % cvar,
                "fl[0] = 1 if res == 0 else 0",
                "fl[2] = (res >> %d) & 1" % s]
    elif kind == "sar":
        core = ["sa = a >> %d" % s,
                "val = a",
                "for _ in range(%s):" % cvar,
                "    val = (val >> 1) | (sa << %d)" % s,
                "fl[1] = a & 1",
                "fl[0] = 1 if val == 0 else 0",
                "fl[2] = (val >> %d) & 1" % s]
    else:                                # rol: ZF/SF не трогает
        core = ["c = %s %% %d" % (cvar, size),
                "res = ((a << c) | (a >> (%d - c))) & %s if c else a"
                % (size, m),
                "fl[1] = res & 1"]
    if head:                             # cl: чтение ПОСЛЕ проверки cnt
        body = head + ["    " + l for l in rd + core + lw]
    else:
        body = rd + core + lw
    return pre + p2, body + ["return nrip"]


def _b_imul(cpu, args):
    """imul reg, r/m: знаковое произведение, CF=OF=1 при переполнении."""
    if len(args) != 2 or args[0][0] != "r":
        return None
    m, s, _n, cfull = _SZ[_bits(args[0])]
    pre, la, ea = _read(cpu, args[0], "a")
    p2, lb, eb = _read(cpu, args[1], "b")
    p3, lw = _write(cpu, args[0], "res")
    body = la + lb
    if ea != "a":
        body.append("a = %s" % ea)
    if eb != "b":
        body.append("b = %s" % eb)
    body += [
        "fa = a - %s if (a >> %d) & 1 else a" % (cfull, s),
        "fb = b - %s if (b >> %d) & 1 else b" % (cfull, s),
        "full = fa * fb",
        "res = full & %s" % m,
        "fl[1] = fl[3] = 0 if (res - %s if (res >> %d) & 1 else res)"
        " == full else 1" % (cfull, s),
        "fl[0] = 1 if res == 0 else 0",
        "fl[2] = (res >> %d) & 1" % s]
    return pre + p2 + p3, body + lw + ["return nrip"]


def _b_push(cpu, args):
    if len(args) != 1 or args[0][0] != "r" or args[0][2] != 64:
        return None
    memo = cpu.memo is not None
    pre = ["p8 = _S8.pack_into"] + (["m = memo"] if memo else [])
    # значение читается ДО декремента rsp (push rsp кладёт СТАРОЕ
    # значение — как self.get(reg) до push64 в эталоне)
    return pre, ["v = %s" % _rreg(args[0]),
                 "rsp = (regs[4] - 8) & 0xFFFFFFFFFFFFFFFF",
                 "regs[4] = rsp"] + \
        _scan_write("rsp", "v", 8, "0xFFFFFFFFFFFFFFFF", memo) + \
        ["return nrip"]


def _b_pop(cpu, args):
    if len(args) != 1 or args[0][0] != "r" or args[0][2] != 64:
        return None
    memo = cpu.memo is not None
    pre = ["u8 = _S8.unpack_from"] + (["m = memo"] if memo else [])
    return pre, _scan_read("v", "regs[4]", 8, memo) + [
        "regs[4] = (regs[4] + 8) & 0xFFFFFFFFFFFFFFFF",
        _wreg(args[0], "v"),
        "return nrip"]


def _b_jmp(cpu, args):
    if len(args) != 1 or args[0][0] != "t":
        return None
    return [], ["return %d" % args[0][1]]


def _b_jcc(cpu, args):
    if len(args) != 2 or args[1][0] != "t" or args[0] not in _CCE:
        return None
    return [], ["return %d if %s else nrip"
                % (args[1][1], _CCE[args[0]])]


def _b_call(cpu, args):
    """call: прямой ('t') или косвенный (память FF /2; чтение 8 байт
    независимо от размера операнда — IAT PE32+, как _op_call)."""
    if len(args) != 1:
        return None
    a = args[0]
    if a[0] == "t":
        pre, lr, dest = [], [], "%d" % a[1]
    elif a[0] == "m":
        pre, lr, dest = _read(cpu, a, "dest", force8=True)
    else:
        return None
    memo = cpu.memo is not None
    pre = pre + ["p8 = _S8.pack_into"] + (["m = memo"] if memo else [])
    body = lr + ["stub = stubs.get(%s)" % dest,
                 "if stub is not None:",
                 "    stub(cpu)",
                 "    return nrip",
                 "if %s == cpu.retguard:" % dest,
                 '    raise RuntimeError("call на ловушку возврата @ %X"'
                 " % nrip)",
                 "rsp = (regs[4] - 8) & 0xFFFFFFFFFFFFFFFF",
                 "regs[4] = rsp"]
    body.extend(_scan_write("rsp", "nrip", 8,
                            "0xFFFFFFFFFFFFFFFF", memo))
    body.append("return %s" % dest)
    return pre, body


def _b_ret(cpu, args):
    if args:
        return None
    memo = cpu.memo is not None
    pre = ["u8 = _S8.unpack_from"] + (["m = memo"] if memo else [])
    return pre, _scan_read("dest", "regs[4]", 8, memo) + [
        "regs[4] = (regs[4] + 8) & 0xFFFFFFFFFFFFFFFF",
        "if dest == cpu.retguard:",
        '    raise RuntimeError("возврат из точки входа (нет'
        ' ExitProcess)")',
        "return dest"]


def _b_cdqe(cpu, args):
    return [], ["eax = regs[0] & 0xFFFFFFFF",
                "regs[0] = eax - 0x100000000 if eax & 0x80000000"
                " else eax",
                "return nrip"]


def _b_cqo(cpu, args):
    return [], ["regs[2] = 0xFFFFFFFFFFFFFFFF if regs[0] >> 63 else 0",
                "return nrip"]


def _b_cdq(cpu, args):
    return [], ["regs[2] = 0xFFFFFFFF if regs[0] & 0x80000000 else 0",
                "return nrip"]


def _b_int3(cpu, args):
    return [], ['raise RuntimeError("int3 (страховка) @ rip=%X — поток'
                ' дошёл до ловушки" % (nrip - 1))']


_BUILDERS = {
    "mov": _b_mov, "movzx": _b_mov, "lea": _b_lea,
    "add": lambda c, a: _alu(c, a, "+", True),
    "sub": lambda c, a: _alu(c, a, "-", True),
    "cmp": lambda c, a: _alu(c, a, "-", False),
    "and": lambda c, a: _alu(c, a, "&", True),
    "test": lambda c, a: _alu(c, a, "&", False),
    "or": lambda c, a: _alu(c, a, "|", True),
    "xor": lambda c, a: _alu(c, a, "^", True),
    "neg": _b_neg,
    "inc": lambda c, a: _incdec(c, a, "+"),
    "dec": lambda c, a: _incdec(c, a, "-"),
    "shl": lambda c, a: _b_shift(c, a, "shl"),
    "shr": lambda c, a: _b_shift(c, a, "shr"),
    "sar": lambda c, a: _b_shift(c, a, "sar"),
    "rol": lambda c, a: _b_shift(c, a, "rol"),
    "imul": _b_imul,
    "push": _b_push, "pop": _b_pop,
    "jmp": _b_jmp, "jcc": _b_jcc,
    "call": _b_call, "ret": _b_ret,
    "cdqe": _b_cdqe, "cqo": _b_cqo, "cdq": _b_cdq,
    "int3": _b_int3,
}                       # idiv не специализируется — универсальный путь
