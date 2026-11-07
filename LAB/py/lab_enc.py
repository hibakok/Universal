"""lab_enc.py — оракул кодировщика ENC v1 (SPEC/09): M-строка -> H-строка.

Вход:  текст BRICK v2 (str/bytes): v1 + M-строки.
Выход: normalize(text) -> текст BRICK v1 (M-строки заменены на H-строки);
       encode_m(мнемоника, [операнды]) -> список токенов (int-байты либо
       ("slot", имя, размер)); ValueError EncError("FORMAT AT=XXXX").
Функция: независимая реализация канонических кодировок SPEC/09 —
         эталон для будущего enc.exe (M1-ENC, этап E6.2) и кодогенератор
         транслятора L2. Адресов НЕ считает: ссылки $имя/$имя:1 проходят
         в слоты нетронутыми (их разрешает brick.exe, SPEC/08).
"""
import re

REGS = {}
for _i, (_n, _n32) in enumerate(zip(
        "rax rcx rdx rbx rsp rbp rsi rdi".split(),
        "eax ecx edx ebx esp ebp esi edi".split())):
    REGS[_n] = (_i, 64)
    REGS[_n32] = (_i, 32)
for _i in range(8, 16):
    REGS["r%d" % _i] = (_i, 64)
    REGS["r%dd" % _i] = (_i, 32)
for _n, _i in zip("al cl dl bl".split(), range(4)):
    REGS[_n] = (_i, 8)
for _n, _i in zip("sil dil spl bpl".split(), (6, 7, 4, 5)):
    REGS[_n] = (_i, 8)
for _i in range(8, 16):
    REGS["r%db" % _i] = (_i, 8)

ALU = {"add": (0x00, 0), "or": (0x08, 1), "and": (0x20, 4),
       "sub": (0x28, 5), "xor": (0x30, 6), "cmp": (0x38, 7)}
SHIFT = {"rol": 0, "ror": 1, "shl": 4, "shr": 5, "sar": 7}
JCC = {"jo": 0, "jno": 1, "jb": 2, "jae": 3, "jz": 4, "jnz": 5,
       "jbe": 6, "ja": 7, "js": 8, "jns": 9, "jl": 0xC, "jge": 0xD,
       "jle": 0xE, "jg": 0xF}
JCC["je"], JCC["jne"] = JCC["jz"], JCC["jnz"]      # синонимы
SIZEKW = {"byte": 8, "word": 16, "dword": 32, "qword": 64}
NUM_RE = re.compile(r"^-?[0-9A-F]{1,8}$")
REF_RE = re.compile(r"^\$([a-z0-9_]{1,63})(:1)?$")

class EncError(ValueError):
    pass

def _err(ln):
    raise EncError("FORMAT AT=%04X" % ln)

# ---------------------------------------------------------------- разбор
class _Op:
    """Разобранный операнд: reg/imm/ref/mem (поля None вне типа)."""

    def __init__(self, kind, **kw):
        self.kind = kind
        self.code = kw.get("code")          # reg: номер 0..15
        self.size = kw.get("size")          # reg/mem: 8/16/32/64
        self.val = kw.get("val")            # imm: значение
        self.name = kw.get("name")          # ref: имя метки
        self.slot = kw.get("slot")          # ref: 4 или 1
        self.base = kw.get("base")          # mem: код базы (int)
        self.idx = kw.get("idx")            # mem: код индекса | None
        self.disp = kw.get("disp")          # mem: смещение | None
        self.rip = kw.get("rip")            # mem: имя $ссылки

def _num(s):
    if not NUM_RE.match(s):
        return None
    return -int(s[1:], 16) if s[0] == "-" else int(s, 16)

def _mem(inner, ln):
    """Разбор содержимого скобок '[...]' -> _Op|None."""
    parts = [p for p in inner.replace("-", "+-").split("+") if p]
    kw = {}
    if parts and parts[0] == "rip":
        if len(parts) != 2 or not parts[1].startswith("$"):
            return None
        m = REF_RE.match(parts[1])
        if not m or m.group(2):             # [rip+$имя], всегда 4 байта
            return None
        return _Op("mem", rip=m.group(1), size=None, base=None, idx=None,
                   disp=None)
    if not 1 <= len(parts) <= 3:
        return None
    b = REGS.get(parts[0])
    if b is None or b[1] != 64:
        return None
    kw["base"] = b[0]
    kw["idx"] = kw["disp"] = None
    rest = parts[1:]
    if rest:
        i = REGS.get(rest[0])
        if i is not None and i[1] == 64:     # [база+индекс(±число)]
            if i[0] == 4:                    # rsp/r12 — «нет индекса»
                return None
            kw["idx"] = i[0]
            if len(rest) == 2:
                d = _num(rest[1])
                if d is None:
                    return None
                kw["disp"] = d
            elif len(rest) != 1:
                return None
        else:                                # [база ±число]
            if len(rest) != 1:
                return None
            d = _num(rest[0])
            if d is None:
                return None
            kw["disp"] = d
    return _Op("mem", size=None, **kw)

def _operand(s, ln):
    s = s.strip()
    if not s:
        _err(ln)
    if s in REGS:
        c, z = REGS[s]
        return _Op("reg", code=c, size=z)
    if s.startswith("$"):
        m = REF_RE.match(s)
        if not m:
            _err(ln)
        return _Op("ref", name=m.group(1), slot=1 if m.group(2) else 4)
    for kw, sz in SIZEKW.items():
        if s.startswith(kw + " ") and s.endswith("]"):
            inner = s[len(kw):].strip()      # "[...]"
            if not (inner.startswith("[") and inner.endswith("]")):
                _err(ln)
            o = _mem(inner[1:-1], ln)
            if o is None:
                _err(ln)
            o.size = sz
            return o
    if s.startswith("[") and s.endswith("]"):
        o = _mem(s[1:-1], ln)
        if o is None:
            _err(ln)
        return o
    v = _num(s)
    if v is not None:
        return _Op("imm", val=v)
    _err(ln)

def _split_ops(ops, ln):
    """['rsp', ' 38'] -> [_Op, _Op]; запятые уже разделены (normalize)."""
    return [_operand(p, ln) for p in ops]

# ------------------------------------------------------------- кодирование
def _rex(w, r, x, b):
    v = (w << 3) | (r << 2) | (x << 1) | b
    return 0x40 | v if v else None

def _i32(v, ln):
    if not -0x80000000 <= v <= 0xFFFFFFFF:
        _err(ln)
    return [v >> i & 0xFF for i in (0, 8, 16, 24)]

def _imm8s(v, ln):
    """Знаковый байт (83/80-формы): -0x80..0x7F."""
    if not -0x80 <= v <= 0x7F:
        return None
    return [v & 0xFF]

def _enc_mem(m, regv, ln):
    """Память -> (rex_x, rex_b, modrm, sib|None, tail-байты, слот)."""
    if m.rip is not None:
        return 0, 0, 0x05 | regv << 3, None, [], ("slot", m.rip, 4)
    d = m.disp if m.disp is not None else 0
    if not -0x80000000 <= d <= 0x7FFFFFFF:
        _err(ln)
    if m.idx is not None or m.base == 4:
        sib = ((m.idx & 7) if m.idx is not None else 4) << 3 | m.base & 7
        rm = 4
    else:
        sib, rm = None, m.base & 7
    if d == 0:
        mod, tail = 0, []
        if rm == 4:                          # SIB-база 5 (rbp/r13)
            if sib is not None and m.base & 7 == 5:
                mod, tail = 1, [0]
        elif rm == 5:                        # rbp/r13 без disp = rip!
            mod, tail = 1, [0]
    elif -0x80 <= d <= 0x7F:
        mod, tail = 1, [d & 0xFF]
    else:
        mod, tail = 2, _i32(d, ln)
    x = 1 if m.idx is not None and m.idx >= 8 else 0
    b = 1 if m.base >= 8 else 0
    return x, b, mod << 6 | regv << 3 | rm, sib, tail, None

def _rr(op, dst, src, ln, w_from_size=True):
    """reg,reg -> байты (REX+opcode+modrm)."""
    if dst.size != src.size:
        _err(ln)
    rex = _rex(dst.size == 64 and w_from_size, src.code >= 8, 0,
               dst.code >= 8)
    modrm = 0xC0 | (src.code & 7) << 3 | dst.code & 7
    return ([rex] if rex else []) + [op, modrm]

def _rm(op, reg, m, ln, w64):
    """reg,mem или mem,reg (reg в поле reg) -> байты + слот."""
    x, b, modrm, sib, tail, slot = _enc_mem(m, reg.code & 7, ln)
    rex = _rex(w64, reg.code >= 8, x, b)
    out = ([rex] if rex else []) + [op, modrm]
    if sib is not None:
        out.append(sib)
    out += tail
    if slot:
        out.append(slot)
    return out

def _alu_imm(opc, ext, dst, v, ln):
    """ALU reg,imm / mem,imm: 80/83/81 по размеру и значению."""
    if dst.size == 8:
        if not -0x80 <= v <= 0xFF:
            _err(ln)
        imm = [v & 0xFF]
        opc8 = 0x80
        return opc8, imm
    imm = _imm8s(v, ln)
    if imm is not None:
        return 0x83, imm
    if dst.size == 64 and not -0x80000000 <= v <= 0x7FFFFFFF:
        _err(ln)
    return 0x81, _i32(v, ln)

def _enc_alu(mn, ops, ln):
    base, ext = ALU[mn]
    dst, src = ops
    if dst.kind == "reg" and src.kind == "reg":
        op = base if dst.size == 8 else base + 1
        return _rr(op, dst, src, ln)
    if dst.kind == "reg" and src.kind == "imm":
        opc, imm = _alu_imm(0, ext, dst, src.val, ln)
        rex = _rex(dst.size == 64, 0, 0, dst.code >= 8)
        modrm = 0xC0 | ext << 3 | dst.code & 7
        return ([rex] if rex else []) + [opc, modrm] + imm
    if dst.kind == "reg" and src.kind == "mem":
        if src.size is not None and src.size != dst.size:
            _err(ln)
        op = base + 2 if dst.size == 8 else base + 3
        return _rm(op, dst, src, ln, dst.size == 64)
    if dst.kind == "mem" and src.kind == "reg":
        if dst.size is not None and dst.size != src.size:
            _err(ln)
        op = base if src.size == 8 else base + 1
        return _rm(op, src, dst, ln, src.size == 64)
    if dst.kind == "mem" and src.kind == "imm":
        if dst.size not in (8, 32, 64) or dst.rip is not None:
            _err(ln)                          # слот не в конце / нет word
        opc, imm = _alu_imm(0, ext, dst, src.val, ln)
        x, b, modrm, sib, tail, slot = _enc_mem(dst, ext, ln)
        if slot:
            _err(ln)
        rex = _rex(dst.size == 64, 0, x, b)
        out = ([rex] if rex else []) + [opc, modrm]
        if sib is not None:
            out.append(sib)
        return out + tail + imm
    _err(ln)

def _enc_mov(ops, ln):
    dst, src = ops
    if dst.kind == "reg" and src.kind == "reg":
        op = {8: 0x88, 32: 0x89, 64: 0x89}[dst.size] \
            if dst.size == src.size else None
        if op is None:
            _err(ln)
        return _rr(op, dst, src, ln)
    if dst.kind == "reg" and src.kind == "imm":
        v = src.val
        if dst.size == 8:
            if not -0x80 <= v <= 0xFF:
                _err(ln)
            rex = _rex(0, 0, 0, dst.code >= 8)
            return ([rex] if rex else []) + [0xB0 | dst.code & 7,
                                             v & 0xFF]
        if dst.size == 32:
            rex = _rex(0, 0, 0, dst.code >= 8)
            return ([rex] if rex else []) + [0xB8 | dst.code & 7] + \
                _i32(v, ln)
        if not -0x80000000 <= v <= 0x7FFFFFFF:      # r64: imm32 sext
            _err(ln)
        return [0x48 | (dst.code >= 8), 0xC7, 0xC0 | dst.code & 7] + \
            _i32(v, ln)
    if dst.kind == "reg" and src.kind == "mem":
        if src.size is not None and src.size != dst.size:
            _err(ln)
        op = {8: 0x8A, 32: 0x8B, 64: 0x8B}[dst.size]
        return _rm(op, dst, src, ln, dst.size == 64)
    if dst.kind == "mem" and src.kind == "reg":
        if dst.size is not None and dst.size != src.size:
            _err(ln)
        op = {8: 0x88, 32: 0x89, 64: 0x89}[src.size]
        return _rm(op, src, dst, ln, src.size == 64)
    if dst.kind == "mem" and src.kind == "imm":
        if dst.size not in (8, 32, 64) or dst.rip is not None:
            _err(ln)
        v = src.val
        if dst.size == 8:
            if not 0 <= v <= 0xFF:
                _err(ln)
            imm = [v]
        else:
            if dst.size == 64 and not -0x80000000 <= v <= 0x7FFFFFFF:
                _err(ln)
            imm = _i32(v, ln)
        x, b, modrm, sib, tail, slot = _enc_mem(dst, 0, ln)
        if slot:
            _err(ln)
        rex = _rex(dst.size == 64, 0, x, b)
        out = ([rex] if rex else []) + [0xC6 if dst.size == 8 else 0xC7,
                                        modrm]
        if sib is not None:
            out.append(sib)
        return out + tail + imm
    _err(ln)                                   # ref и пр. — ошибка

def _enc_movzx(ops, ln):
    dst, src = ops
    if dst.kind != "reg" or dst.size not in (32, 64):
        _err(ln)
    if src.kind == "reg":
        if src.size != 8:
            _err(ln)                           # word-регистров в v1 нет
        rex = _rex(0, dst.code >= 8, 0, src.code >= 8)
        modrm = 0xC0 | dst.code & 7 << 3 | src.code & 7
        return ([rex] if rex else []) + [0x0F, 0xB6, modrm]
    if src.kind != "mem" or src.size not in (8, 16):
        _err(ln)
    return _rm2_0f(0xB6 if src.size == 8 else 0xB7, dst, src, ln)

def _rm2_0f(sub, reg, m, ln):
    """0F xx /r c памятью, БЕЗ REX.W (movzx)."""
    x, b, modrm, sib, tail, slot = _enc_mem(m, reg.code & 7, ln)
    rex = _rex(0, reg.code >= 8, x, b)
    out = ([rex] if rex else []) + [0x0F, sub, modrm]
    if sib is not None:
        out.append(sib)
    out += tail
    if slot:
        out.append(slot)
    return out

def _enc_shift(mn, ops, ln):
    dst, src = ops
    if dst.kind != "reg" or dst.size == 16:
        _err(ln)
    ext = SHIFT[mn]
    if src.kind == "reg":
        if not (src.size == 8 and src.code == 1):    # только cl
            _err(ln)
        op = {8: 0xD2, 32: 0xD3, 64: 0xD3}[dst.size]
        rex = _rex(dst.size == 64, 0, 0, dst.code >= 8)
        return ([rex] if rex else []) + [op, 0xC0 | ext << 3 |
                                         dst.code & 7]
    if src.kind != "imm" or not 0 <= src.val <= 0xFF:
        _err(ln)
    op = {8: 0xC0, 32: 0xC1, 64: 0xC1}[dst.size]
    rex = _rex(dst.size == 64, 0, 0, dst.code >= 8)
    return ([rex] if rex else []) + [op, 0xC0 | ext << 3 | dst.code & 7,
                                     src.val]

def _enc_f7(mn, ops, ln):
    """neg(/3): reg 32/64."""
    ext = 3
    (o,) = ops
    if o.kind != "reg" or o.size not in (32, 64):
        _err(ln)
    rex = _rex(o.size == 64, 0, 0, o.code >= 8)
    return ([rex] if rex else []) + [0xF7, 0xC0 | ext << 3 | o.code & 7]

def _enc_ff(mn, ops, ln):
    """inc(/0) и dec(/1): reg 32/64."""
    ext = 0 if mn == "inc" else 1
    (o,) = ops
    if o.kind != "reg" or o.size not in (32, 64):
        _err(ln)
    rex = _rex(o.size == 64, 0, 0, o.code >= 8)
    return ([rex] if rex else []) + [0xFF, 0xC0 | ext << 3 | o.code & 7]

def _enc_test(ops, ln):
    dst, src = ops
    if dst.kind != "reg" or src.kind != "reg" or dst.size != src.size \
            or dst.size == 16:
        _err(ln)
    op = {8: 0x84, 32: 0x85, 64: 0x85}[dst.size]
    return _rr(op, dst, src, ln)

def _enc_lea(ops, ln):
    dst, src = ops
    if dst.kind != "reg" or dst.size not in (32, 64) or src.kind != \
            "mem" or src.size is not None:
        _err(ln)
    return _rm(0x8D, dst, src, ln, dst.size == 64)

def _enc_stack(mn, ops, ln):
    (o,) = ops
    if o.kind != "reg" or o.size != 64:
        _err(ln)
    base = 0x50 if mn == "push" else 0x58
    rex = _rex(0, 0, 0, o.code >= 8)
    return ([rex] if rex else []) + [base | o.code & 7]

def _enc_jmp(mn, ops, ln):
    (o,) = ops
    if o.kind != "ref":
        _err(ln)
    if o.slot == 1:
        return [0xEB, ("slot", o.name, 1)]
    return [0xE9, ("slot", o.name, 4)]

def _enc_jcc(mn, ops, ln):
    (o,) = ops
    if o.kind != "ref":
        _err(ln)
    cc = JCC[mn]
    if o.slot == 1:
        return [0x70 | cc, ("slot", o.name, 1)]
    return [0x0F, 0x80 | cc, ("slot", o.name, 4)]

def _enc_call(ops, ln):
    (o,) = ops
    if o.kind == "ref" and o.slot == 4:
        return [0xE8, ("slot", o.name, 4)]
    if o.kind == "mem" and o.rip is not None and o.size is None:
        return [0xFF, 0x15, ("slot", o.rip, 4)]
    _err(ln)

def _enc_movr(ops, ln):
    """'mov' с проверкой ссылок: $имя допустим только у переходов/в [rip+]."""
    if ops[0].kind == "ref" or (len(ops) > 1 and ops[1].kind == "ref"):
        _err(ln)
    return _enc_mov(ops, ln)

SIMPLE = {"cdqe": [0x48, 0x98], "ret": [0xC3], "int3": [0xCC]}
ENCODERS = {"mov": lambda mn, o, ln: _enc_movr(o, ln),
            "movzx": lambda mn, o, ln: _enc_movzx(o, ln),
            "lea": lambda mn, o, ln: _enc_lea(o, ln),
            "test": lambda mn, o, ln: _enc_test(o, ln),
            "call": lambda mn, o, ln: _enc_call(o, ln),
            "neg": _enc_f7, "inc": _enc_ff,
            "dec": _enc_ff, "push": _enc_stack, "pop": _enc_stack,
            "jmp": _enc_jmp}
for _m in ALU:
    ENCODERS[_m] = _enc_alu
for _m in SHIFT:
    ENCODERS[_m] = _enc_shift
for _m in JCC:
    ENCODERS[_m] = _enc_jcc

def encode_m(mnem, ops, ln):
    """Мнемоника + операнды-строки -> список токенов (int | слот)."""
    if mnem in SIMPLE:
        if ops:
            _err(ln)
        return list(SIMPLE[mnem])
    if mnem not in ENCODERS:
        _err(ln)
    parsed = _split_ops(ops, ln) if ops else []
    need2 = mnem in ("mov", "movzx", "lea", "test") or mnem in ALU \
        or mnem in SHIFT
    if need2 and len(parsed) != 2 or not need2 and len(parsed) != 1:
        _err(ln)
    return ENCODERS[mnem](mnem, parsed, ln)

def _fmt(tokens):
    parts = []
    for t in tokens:
        if isinstance(t, int):
            parts.append("%02X" % t)
        else:
            parts.append("$%s" % t[1] + (":1" if t[2] == 1 else ""))
    return " ".join(parts)

def normalize(text):
    """Текст BRICK v2 -> текст BRICK v1 (байты как str, LF)."""
    if isinstance(text, bytes):
        text = text.decode("latin1")
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        st = line.strip()
        if st.startswith("M ") or st == "M":
            body = st[1:].strip()
            comment = ""
            if ";" in body:
                body, comment = body.split(";", 1)
                comment = ";" + comment
            parts = body.split(None, 1)
            mnem = parts[0] if parts else ""
            rest = parts[1].strip() if len(parts) > 1 else ""
            ops = [p.strip() for p in rest.split(",")] if rest else []
            h = _fmt(encode_m(mnem, ops, i))
            out.append("H " + h + ((" " + comment.strip()) if comment
                                   else ""))
        else:
            out.append(line)
    return "\n".join(out) + "\n"
