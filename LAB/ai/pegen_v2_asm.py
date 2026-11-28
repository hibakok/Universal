#!/usr/bin/env python3
"""pegen_v2_asm.py — мини-ассемблер «компоновки» для роста pegen.hex (LAB/ai).

Принцип e4_ledger: кодировки назначаются вручную (каждая форма — фиксированные
байты, как в теле pegen), компоновка лишь разрешает rip-смещения и длины
переходов. Каждая эмиссия проверяется ОБРАТНЫМ декодированием lab_x86.decode
(имя + длина совпадают) — ошибка кодировки ловится ДО записи в pegen.hex.

Только формы, уже встречающиеся в теле pegen (подмножество SPEC/05):
без SIB-индексаций, без movsx — заведомо совместимо с эмулятором LAB.
"""
import lab_x86

REGS64 = {"rax": 0, "rcx": 1, "rdx": 2, "rbx": 3, "rsi": 6, "rdi": 7,
          "r8": 8, "r9": 9, "r10": 10, "r11": 11, "r12": 12, "r13": 13,
          "r14": 14, "r15": 15}
REGS32 = {"eax": 0, "ecx": 1, "edx": 2, "ebx": 3, "esi": 6, "edi": 7,
          "r8d": 8, "r9d": 9, "r10d": 10, "r11d": 11, "r12d": 12,
          "r13d": 13, "r14d": 14, "r15d": 15}
REGS8 = {"al": 0, "cl": 1, "dl": 2, "bl": 3, "sil": 6, "dil": 7,
         "r8b": 8, "r9b": 9, "r10b": 10, "r11b": 11, "r12b": 12,
         "r13b": 13, "r14b": 14, "r15b": 15}
CC = {"o": 0, "no": 1, "b": 2, "ae": 3, "e": 4, "ne": 5, "be": 6, "a": 7,
      "s": 8, "ns": 9, "l": 12, "ge": 13, "le": 14, "g": 15}
_ALU = {"add": 0x01, "or": 0x09, "and": 0x21, "sub": 0x29, "xor": 0x31}


def _rex(w=0, r=0, x=0, b=0):
    v = 0x40 | (w << 3) | (r << 2) | (x << 1) | b
    return [] if v == 0x40 else [v]


def _modrm(mod, reg, rm):
    # поля modrm — 3 бита; старшие биты номеров r8-r15 уходит в REX (W/R/X/B
    # ставят вызывающие формы по условию reg >= 8)
    return [(mod << 6) | ((reg & 7) << 3) | (rm & 7)]


def _rm(base, disp):
    assert base not in ("rsp", "rbp"), "без SIB: база %s" % base
    if disp is None:
        return 0, REGS64[base]
    assert -0x80000000 <= disp <= 0x7FFFFFFF
    mod = 1 if -128 <= disp <= 127 else 2
    return mod, REGS64[base]


def _disp(mod, disp):
    if disp is None:
        return []
    if mod == 1:
        return [disp & 0xFF]
    return list((disp & 0xFFFFFFFF).to_bytes(4, "little"))


def _norm(reg, w):
    """Имя регистра -> номер: при w=0 принимает и 64-имена (rax->eax,
    r9->r9d); при w=1 — и 32-имена (eax->rax, r9d->r9)."""
    if w:
        if reg in REGS64:
            return REGS64[reg]
        n = REGS32[reg]
        return n
    if reg in REGS32:
        return REGS32[reg]
    n = REGS64[reg]
    return n


class Asm:
    """Накопитель инструкций с метками и данными-символами (self.syms).

    symbols(): метка | int | self.syms[имя] — заполняется ДО emit().
    """

    def __init__(self):
        self.parts = []      # ("label", имя) | ("ins", имя, emit, пояснение)
        self.labels = {}
        self.syms = {}
        self.out = []        # (адрес, байты, пояснение)
        self.probing = False
        self._probe_addr = 0

    def label(self, name):
        self.parts.append(("label", name))

    def _add(self, name, emit, comment):
        self.parts.append(("ins", name, emit, comment))

    def sym(self, name):
        """Метка | int | self.syms[имя]; probe/без syms — 0 (ширины форм
        фиксированы — длины от значений не зависят)."""
        if not self.probing and name in self.labels:
            return self.labels[name]
        if isinstance(name, int):
            return name
        return self.syms.get(name, 0)

    def lval(self, name):
        """Значение метки ИЛИ символа данных; probe — текущий адрес."""
        if self.probing:
            return self._probe_addr
        if name in self.labels:
            return self.labels[name]
        return self.sym(name)

    def emit(self, origin):
        # проход A (probe): адреса меток; все ширины форм фиксированы,
        # символы/смещения подставляются нулевые — длины не зависят от них
        self.probing = True
        addr = origin
        for p in self.parts:
            if p[0] == "label":
                self.labels[p[1]] = addr
                continue
            self._probe_addr = addr
            addr += len(p[2](addr, self))
        # проход B: реальная эмиссия (метки известны; syms — снаружи)
        self.probing = False
        self.out = []
        addr = origin
        for p in self.parts:
            if p[0] == "label":
                continue
            bs = p[2](addr, self)
            self.out.append((addr, bs, p[3]))
            addr += len(bs)
        for a, bs, _cm in self.out:       # round-trip контроль кодировок
            fetch = lambda _a, _n, _bs=bs, _a0=a: int.from_bytes(
                _bs[_a - _a0:_a - _a0 + _n], "little")
            nm, ln, _args = lab_x86.decode(fetch, a)
            assert ln == len(bs), "@%X: %s длина %d != %d" % (a, nm, ln,
                                                              len(bs))
        return self

    def lines(self):
        return ["@%04X %s ; %s" % (a, " ".join("%02X" % b for b in bs), cm)
                for a, bs, cm in self.out]

    # ------------------------------------------------------- формы (вручную)
    def mov_rr(self, dst, src, cm, w=1):
        d, s = _norm(dst, w), _norm(src, w)
        self._add("mov", lambda a, t: bytes(
            _rex(w, s >= 8, 0, d >= 8) + [0x89] + _modrm(3, s, d)), cm)

    def mov_ri(self, reg, imm, cm, w=1):
        r = _norm(reg, w)
        if w:
            assert -0x80000000 <= imm <= 0x7FFFFFFF
            self._add("mov", lambda a, t: bytes(
                _rex(1, 0, 0, r >= 8) + [0xC7] + _modrm(3, 0, r) +
                list((imm & 0xFFFFFFFF).to_bytes(4, "little"))), cm)
        else:
            self._add("mov", lambda a, t: bytes(
                _rex(0, 0, 0, r >= 8) + [0xB8 + (r & 7)] +
                list((imm & 0xFFFFFFFF).to_bytes(4, "little"))), cm)

    def mov_rip(self, reg, sym, cm, w=1, store=False):
        r = _norm(reg, w)
        op = 0x89 if store else 0x8B

        def emit(a, t):
            pre = bytes(_rex(w, r >= 8, 0, 0) + [op] + _modrm(0, r, 5))
            d = t.sym(sym) - (a + len(pre) + 4)
            return pre + d.to_bytes(4, "little", signed=True)
        self._add("mov", emit, cm)

    def mov_rip_i32(self, sym, imm, cm):
        """mov dword [rip+sym], imm32 (C7 05 disp32 imm32).

        E9.5-1: база rip — КОНЕЦ ИНСТРУКЦИИ (disp32 + imm32 = 10 Б),
        а не конец поля disp (баг сессии 87: запись уходила на +4 мимо
        ячейки — взаимно компенсировалась со чтениями cmp_rip_i8 и не
        проявлялась на корпусе T-M5-18)."""

        def emit(a, t):
            pre = bytes([0xC7] + _modrm(0, 0, 5))
            d = t.sym(sym) - (a + len(pre) + 4 + 4)   # + imm32!
            return pre + d.to_bytes(4, "little", signed=True) + \
                (imm & 0xFFFFFFFF).to_bytes(4, "little")
        self._add("mov", emit, cm)

    def lea_rip(self, reg, sym, cm):
        r = REGS64[reg]

        def emit(a, t):
            pre = bytes(_rex(1, r >= 8, 0, 0) + [0x8D] + _modrm(0, r, 5))
            d = t.sym(sym) - (a + len(pre) + 4)
            return pre + d.to_bytes(4, "little", signed=True)
        self._add("lea", emit, cm)

    def mov_mr(self, dst, base, disp, cm, w=1, byte=False):
        """mov dst, [base+disp] (8B/8A /r)."""
        mod, bm = _rm(base, disp)
        s = REGS8[dst] if byte else _norm(dst, w)
        self._add("mov", lambda a, t: bytes(
            _rex(0 if byte else w, s >= 8, 0, bm >= 8) +
            [0x8A if byte else 0x8B] + _modrm(mod, s, bm) + _disp(mod, disp)),
            cm)

    def mov_rm(self, base, disp, src, cm, w=1, byte=False):
        """mov [base+disp], src (89/88 /r)."""
        mod, bm = _rm(base, disp)
        s = REGS8[src] if byte else _norm(src, w)
        self._add("mov", lambda a, t: bytes(
            _rex(0 if byte else w, s >= 8, 0, bm >= 8) +
            [0x88 if byte else 0x89] + _modrm(mod, s, bm) + _disp(mod, disp)),
            cm)

    def movzx(self, dst, base, disp, cm, word=False):
        d = REGS32[dst]
        mod, bm = _rm(base, disp)
        self._add("movzx", lambda a, t: bytes(
            _rex(0, d >= 8, 0, bm >= 8) + [0x0F, 0xB7 if word else 0xB6] +
            _modrm(mod, d, bm) + _disp(mod, disp)), cm)

    def movb_ri(self, base, disp, imm, cm):
        mod, bm = _rm(base, disp)
        self._add("mov", lambda a, t: bytes(
            _rex(0, 0, 0, bm >= 8) + [0xC6] + _modrm(mod, 0, bm) +
            _disp(mod, disp) + [imm & 0xFF]), cm)

    def alu_rr(self, op, dst, src, cm, w=1):
        """add/or/and/sub/xor r,r (op /r, reg=src, rm=dst); cmp — 3B (reg=dst)."""
        d, s = _norm(dst, w), _norm(src, w)
        if op == "cmp":
            self._add("cmp", lambda a, t: bytes(
                _rex(w, d >= 8, 0, s >= 8) + [0x3B] + _modrm(3, d, s)), cm)
        else:
            self._add(op, lambda a, t: bytes(
                _rex(w, s >= 8, 0, d >= 8) + [_ALU[op]] +
                _modrm(3, s, d)), cm)

    def alu_ri(self, op, reg, imm, cm, w=1):
        r = _norm(reg, w)
        ext = {"add": 0, "or": 1, "and": 4, "sub": 5, "cmp": 7}[op]
        if -128 <= imm <= 127:
            self._add(op, lambda a, t: bytes(
                _rex(w, 0, 0, r >= 8) + [0x83] + _modrm(3, ext, r) +
                [imm & 0xFF]), cm)
        else:
            assert op in ("add", "cmp"), "imm32 только add/cmp"
            self._add(op, lambda a, t: bytes(
                _rex(w, 0, 0, r >= 8) + [0x81] + _modrm(3, ext, r) +
                list((imm & 0xFFFFFFFF).to_bytes(4, "little"))), cm)

    def add_rip(self, reg, sym, cm, w=1):
        r = _norm(reg, w)

        def emit(a, t):
            pre = bytes(_rex(w, r >= 8, 0, 0) + [0x03] + _modrm(0, r, 5))
            d = t.sym(sym) - (a + len(pre) + 4)
            return pre + d.to_bytes(4, "little", signed=True)
        self._add("add", emit, cm)

    def cmp_rip_i8(self, sym, imm, cm):
        """cmp dword [rip+sym], imm8 (83 3D disp32 imm8).

        E9.5-1: база rip — КОНЕЦ ИНСТРУКЦИИ (7 Б), не конец поля disp
        (баг сессии 87: чтение на +1 мимо — dword захватывал соседнюю
        ячейку; на корпусе компенсировался записями mov_rip_i32)."""

        def emit(a, t):
            pre = bytes([0x83] + _modrm(0, 7, 5))
            d = t.sym(sym) - (a + len(pre) + 4 + 1)   # + imm8!
            return pre + d.to_bytes(4, "little", signed=True) + \
                bytes([imm & 0xFF])
        self._add("cmp", emit, cm)

    def cmp_rip_r32(self, reg, sym, cm):
        """cmp [rip+d], r32 (39 /r, reg=r)."""
        r = REGS32[reg]

        def emit(a, t):
            pre = bytes(_rex(0, r >= 8, 0, 0) + [0x39] + _modrm(0, r, 5))
            d = t.sym(sym) - (a + len(pre) + 4)
            return pre + d.to_bytes(4, "little", signed=True)
        self._add("cmp", emit, cm)

    def cmp_r_rip(self, reg, sym, cm, w=1):
        """cmp r64/r32, [rip+d] (3B /r, reg=r)."""
        r = _norm(reg, w)

        def emit(a, t):
            pre = bytes(_rex(w, r >= 8, 0, 0) + [0x3B] + _modrm(0, r, 5))
            d = t.sym(sym) - (a + len(pre) + 4)
            return pre + d.to_bytes(4, "little", signed=True)
        self._add("cmp", emit, cm)

    def cmp_b_ri(self, base, disp, imm, cm):
        """cmp byte [base+disp], imm8 (80 /7 ib)."""
        mod, bm = _rm(base, disp)
        self._add("cmp", lambda a, t: bytes(
            _rex(0, 0, 0, bm >= 8) + [0x80] + _modrm(mod, 7, bm) +
            _disp(mod, disp) + [imm & 0xFF]), cm)

    def alu_rm(self, op, reg, base, disp, cm, w=1):
        """add reg, [base+disp] (03 /r)."""
        r = _norm(reg, w)
        mod, bm = _rm(base, disp)
        self._add(op, lambda a, t: bytes(
            _rex(w, r >= 8, 0, bm >= 8) + [0x03] + _modrm(mod, r, bm) +
            _disp(mod, disp)), cm)

    def cmp_ri8(self, reg, imm, cm):
        r = REGS8[reg]
        if r == 0:
            self._add("cmp", lambda a, t: bytes([0x3C, imm & 0xFF]), cm)
        else:
            self._add("cmp", lambda a, t: bytes(
                _rex(0, 0, 0, r >= 8) + [0x80] + _modrm(3, 7, r) +
                [imm & 0xFF]), cm)

    def test_rr(self, dst, src, cm, w=0):
        d, s = _norm(dst, w), _norm(src, w)
        self._add("test", lambda a, t: bytes(
            _rex(w, s >= 8, 0, d >= 8) + [0x85] + _modrm(3, s, d)), cm)

    def inc(self, reg, cm, w=0):
        r = _norm(reg, w)
        self._add("inc", lambda a, t: bytes(
            _rex(w, 0, 0, r >= 8) + [0xFF] + _modrm(3, 0, r)), cm)

    def shl_ri(self, reg, n, cm):
        r = REGS32[reg]
        self._add("shl", lambda a, t: bytes(
            _rex(0, 0, 0, r >= 8) + [0xC1] + _modrm(3, 4, r) + [n]), cm)

    def jcc(self, cc, target, cm):
        def emit(a, t):
            d = t.lval(target) - (a + 2)
            assert -128 <= d <= 127, "jcc %s -> %s: %d" % (cc, target, d)
            return bytes([0x70 | CC[cc], d & 0xFF])
        self._add("jcc", emit, cm)

    def jcc_near(self, cc, target, cm):
        """jcc rel32 (0F 8x cd) — для дальних переходов внутри кирпича."""
        def emit(a, t):
            d = t.lval(target) - (a + 6)
            return bytes([0x0F, 0x80 | CC[cc]] + list(d.to_bytes(
                4, "little", signed=True)))
        self._add("jcc", emit, cm)

    def jmp(self, target, cm, short=True):
        def emit(a, t):
            if short:
                d = t.lval(target) - (a + 2)
                assert -128 <= d <= 127, "jmp %s: %d" % (target, d)
                return bytes([0xEB, d & 0xFF])
            d = t.lval(target) - (a + 5)
            return bytes([0xE9] + list(d.to_bytes(4, "little", signed=True)))
        self._add("jmp", emit, cm)

    def call(self, target, cm):
        def emit(a, t):
            d = t.lval(target) - (a + 5)
            return bytes([0xE8] + list(d.to_bytes(4, "little", signed=True)))
        self._add("call", emit, cm)

    def call_rip(self, sym, cm):
        def emit(a, t):
            d = t.sym(sym) - (a + 6)
            return bytes([0xFF, 0x15] + list(d.to_bytes(4, "little",
                                                        signed=True)))
        self._add("call", emit, cm)

    def ret(self, cm):
        self._add("ret", lambda a, t: b"\xC3", cm)

    def int3(self, cm):
        self._add("int3", lambda a, t: b"\xCC", cm)

    def cdqe(self, cm):
        self._add("cdqe", lambda a, t: b"\x48\x98", cm)
