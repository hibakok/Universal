"""trace_m.py — транслитерация ветви M (M-строки канона, E9.2-3c) на
Python 1:1 с планом WALL (bridge_self_m*.wall) + сверка с оракулом.

Вход:  12 артефактов семейства + синтетика (synthm/hint-ins/imp0 —
       как T-E9-22). Декод — оракул lab_bridge.parse_family; состояние
       декодера инструмента (глобали dname/da1k/... om*) строится
       картой oracle-кортежей -> представление ветвей D/D2 (1:1).
Выход: отчёт: для КАЖДОЙ выжившей инструкции решение транслитерации
       (M + текст строки) обязано совпасть с оракулом _emit_lines(
       mode=None): M ⟺ M и тексты строк байт-в-байт; H ⟺ H.
       Итог: N/N — план ветви M подтверждён (можно писать WALL).
Функция: локализация логика/механика (прецедент trace_wall.py,
       сессия 71): ошибки ЗДЕСЬ — логика плана; ошибки после WALL —
       механика транскрипции.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "py"))

import lab_bridge                             # noqa: E402
import lab_pe                                 # noqa: E402
import lab_pegen                              # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..")

ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva", "L5-BRIDGE/bridge"]

# индексы мнемоник s_mn (блоб с ведущим NUL: 0 = jcc-псевдоимя)
MN = {"jcc": 0, "add": 1, "or": 2, "and": 3, "sub": 4, "xor": 5, "cmp": 6,
      "test": 7, "mov": 8, "lea": 9, "push": 10, "pop": 11, "cdqe": 12,
      "cqo": 13, "cdq": 14, "ret": 15, "int3": 16, "jmp": 17, "call": 18,
      "movzx": 19, "imul": 20, "rol": 21, "shl": 22, "shr": 23,
      "sar": 24, "neg": 25, "idiv": 26, "inc": 27, "dec": 28}

SECT = lab_bridge.SECT
BASE_OFF = lab_bridge.BASE_OFF


def hexs(v):
    """_hx оракула: ЗАГЛАВНЫЙ hex, знак «-»."""
    return ("-%X" % -v) if v < 0 else "%X" % v


class St(object):
    """Состояние декодера инструмента (глобали ветвей D/D2) + лабмапа."""

    def __init__(self, fam, labels, lo):
        name, ln, args = fam["ins"][lo]
        body = fam["body"]
        self.lo = lo
        self.body = body
        self.dname = MN[name]
        self.dlen = ln
        self.dargc = len([a for a in args]) if args else 0
        self.dcc = 0
        self.da1k = 0
        self.da2k = 0
        self.da1r = 0
        self.da2r = 0
        self.da1s = 0
        self.da2s = 0
        self.da1v = 0
        self.da2v = 0
        self.damem = 0
        self.ombase = -1
        self.omidx = -1
        self.omscale = 1
        self.omdisp = 0
        self.omsize = 0
        self.omrip = 0
        self.mripon = 0
        if name == "jcc":
            self.dcc = lab_x86_cc(args[0])
            # инструмент: set_tgt -> слот 1 (cc-строка — не операнд)
            a1 = args[1]
            self.da1k = 4
            self.da1v = a1[1]
        else:
            for i, a in enumerate(args):
                slot = i + 1
                if isinstance(a, str):                # cl
                    self._set(slot, "k", 5)
                elif isinstance(a, int):              # счётчик
                    self._set(slot, "k", 6)
                    self._set(slot, "v", a)
                elif a[0] == "r":
                    self._set(slot, "k", 1)
                    self._set(slot, "r", a[1])
                    self._set(slot, "s", a[2])
                elif a[0] == "i":
                    k = 3
                    if self._is_b8w():
                        k = 7
                    self._set(slot, "k", k)
                    self._set(slot, "v", a[1])
                    self._set(slot, "s", a[2])
                elif a[0] == "t":
                    self._set(slot, "k", 4)
                    self._set(slot, "v", a[1])
                elif a[0] == "m":
                    self._set(slot, "k", 2)
                    self._set(slot, "s", a[5])   # set_rm: daXs = opsize
                    self.damem = slot
                    self.ombase = -1 if a[1] is None else a[1]
                    self.omidx = -1 if a[2] is None else a[2]
                    self.omscale = a[3]
                    self.omdisp = a[4]
                    self.omsize = a[5]
                    if a[6] is not None:
                        self.mripon = 1
                        self.omrip = a[6][1]
        self.labels = labels

    def _is_b8w(self):
        """Вид 7 (imm-u64): ТОЛЬКО B8..BF с REX.W (48/49 B8) — без
        REX.W это imm32 (вид 3)."""
        j = self.lo
        if 0x40 <= self.body[j] <= 0x4F:
            if not self.body[j] & 8:
                return False
            j += 1
            return 0xB8 <= self.body[j] <= 0xBF
        return False

    def _set(self, slot, f, v):
        setattr(self, "da%d%s" % (slot, f), v)

    def lab(self, off):
        return off in self.labels

    def labname(self, off):
        return self.labels[off]


def lab_x86_cc(s):
    return ["o", "no", "b", "ae", "z", "nz", "be", "a", "s", "ns", "p",
            "np", "l", "ge", "le", "g"].index(s)


REG64 = ["rax", "rcx", "rdx", "rbx", "rsp", "rbp", "rsi", "rdi"] + \
        ["r%d" % i for i in range(8, 16)]
REG8 = ["al", "cl", "dl", "bl", "spl", "bpl", "sil", "dil"] + \
       ["r%db" % i for i in range(8, 16)]
REG32 = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"] + \
        ["r%dd" % i for i in range(8, 16)]
KW = {8: "byte ", 16: "word ", 32: "dword ", 64: "qword "}


# ------------------------------------------------------------ план WALL
class M(object):
    """Транслитерация кирпичей K5-M001..M023 (порядок = план WALL)."""

    def __init__(self, st):
        self.st = st
        self.mb = []                 # mbuf
        self.mlen = 0
        self.mslot = -1
        self.mslotz = 0
        self.mslof = 0
        self.memx = 0
        self.memb = 0
        self.out = []

    # K5-M001 m_put
    def put(self, b):
        self.mb.append(b & 0xFF)
        self.mlen += 1

    # K5-M002 m_put4
    def put4(self, v):
        self.put(v & 0xFF)
        self.put((v >> 8) & 0xFF)
        self.put((v >> 16) & 0xFF)
        self.put((v >> 24) & 0xFF)

    # K5-M003 m_rex
    def rex(self, w, r, x, b):
        v = w * 8 + r * 4 + x * 2 + b
        if v != 0:
            self.put(0x40 | v)

    # K5-M004 m_memxb (глобали memx/memb)
    def memxb(self):
        self.memx = 0
        self.memb = 0
        if self.st.mripon == 1:
            return
        if self.st.omidx >= 8:
            self.memx = 1
        if self.st.ombase >= 8:
            self.memb = 1

    # K5-M005 m_enc_mem
    def enc_mem(self, regv):
        st = self.st
        self.mslot = -1
        self.mslotz = 0
        if st.mripon == 1:
            self.put(5 + regv * 8)
            self.mslot = self.mlen
            self.mslotz = 4
            self.mslof = st.omrip
            return 0
        d = st.omdisp
        usesib = 0
        sib = 0
        rm = 0
        if st.omidx >= 0 or (st.ombase & 7) == 4:
            usesib = 1
            sib = 4
            if st.omidx >= 0:
                sib = st.omidx & 7
            sib = sib * 8 + (st.ombase & 7)
            rm = 4
        else:
            rm = st.ombase & 7
        mod = 0
        if d == 0:
            if rm == 4:
                if usesib == 1 and (st.ombase & 7) == 5:
                    mod = 1
            else:
                if rm == 5:
                    mod = 1
        else:
            if -128 <= d <= 127:
                mod = 1
            else:
                mod = 2
        self.put(mod * 64 + regv * 8 + rm)
        if usesib == 1:
            self.put(sib)
        if mod == 1:
            if d == 0:
                self.put(0)
            else:
                self.put(d & 0xFF)
        if mod == 2:
            self.put4(d)
        return 0

    # K5-M006 m_cmp: слот НЕ входит в mlen (фиксированные байты)
    def cmp(self):
        st = self.st
        body = st.body
        lo = st.lo
        if self.mslot < 0:
            if self.mlen != st.dlen:
                return 1
            j = 0
            while j < self.mlen:
                if body[lo + j] != self.mb[j]:
                    return 1
                j = j + 1
            return 0
        if self.mlen != self.mslot:
            return 1                # слот обязан идти сразу за фиксированными
        if self.mslot + self.mslotz != st.dlen:
            return 1                # слот — последний токен (pos == ln)
        j = 0
        while j < self.mslot:
            if body[lo + j] != self.mb[j]:
                return 1
            j = j + 1
        if self.mslotz == 1:
            want = body[lo + self.mslot]
            if want >= 128:
                want = want - 256
        else:
            v = body[lo + self.mslot] \
                + 256 * body[lo + self.mslot + 1] \
                + 65536 * body[lo + self.mslot + 2] \
                + 16777216 * body[lo + self.mslot + 3]
            want = v
            if v > 2147483647:
                want = v - 4294967296
        loff = self.mslof
        if want != loff - (lo + self.mslot + self.mslotz):
            return 1
        return 0

    # ---- рендер операндов (в self.out — «outbuf»)

    # K5-M007 m_opmem: kw + "[...]" | "[rip+$...]"
    def opmem(self, slot, kw):
        st = self.st
        if kw:
            size = self._gets(slot)
            if size not in KW:
                return 1
            self.out.append(KW[size])
        if st.mripon == 1:
            off = st.omrip
            if off != BASE_OFF and not st.lab(off):
                return 1
            self.out.append("[rip+$")
            self.out.append("base" if off == BASE_OFF else
                            st.labname(off))
            self.out.append("]")
            return 0
        if st.omscale != 1:
            return 1
        if st.ombase < 0:
            return 1
        self.out.append("[" + REG64[st.ombase])
        if st.omidx >= 0:
            self.out.append("+" + REG64[st.omidx])
        d = st.omdisp
        if d < 0:
            self.out.append("-" + hexs(-d))
        elif d > 0:
            self.out.append("+" + hexs(d))
        self.out.append("]")
        return 0

    # K5-M008 m_opr: reg / imm / cnt / cl / mem(+kw)
    def opr(self, slot, kw):
        st = self.st
        k = self._getk(slot)
        if k == 1:
            size = self._gets(slot)
            idx = self._getr(slot)
            if size == 8:
                self.out.append(REG8[idx])
            elif size == 32:
                self.out.append(REG32[idx])
            elif size == 64:
                self.out.append(REG64[idx])
            else:
                return 1                # 16-бит регистры — вне канона
            return 0
        if k == 3:
            self.out.append(hexs(self._getv(slot)))
            return 0
        if k == 6:
            self.out.append(hexs(self._getv(slot)))
            return 0
        if k == 5:
            self.out.append("cl")
            return 0
        if k == 2:
            return self.opmem(slot, kw)
        return 1                        # 4 (цель) / 7 (imm64) / 0

    def _getk(self, slot):
        return getattr(self.st, "da%dk" % slot)

    def _getr(self, slot):
        return getattr(self.st, "da%dr" % slot)

    def _gets(self, slot):
        return getattr(self.st, "da%ds" % slot)

    def _getv(self, slot):
        return getattr(self.st, "da%dv" % slot)

    # K5-M009..M023 — кодировщики по мнемотаблице (1:1 с планом WALL)

    def alu_base(self):
        n = self.st.dname
        if n == 1:
            return 0
        if n == 2:
            return 8
        if n == 3:
            return 32
        if n == 4:
            return 40
        if n == 5:
            return 48
        return 56

    def alu_ext(self):
        n = self.st.dname
        if n == 1:
            return 0
        if n == 2:
            return 1
        if n == 3:
            return 4
        if n == 4:
            return 5
        if n == 5:
            return 6
        return 7

    # K5-M010 m_bsimple: cdqe/cqo/ret/int3 (cdq — отказ)
    def bsimple(self):
        n = self.st.dname
        if n == 12:
            self.put(0x48)
            self.put(0x98)
        elif n == 13:
            self.put(0x48)
            self.put(0x99)
        elif n == 15:
            self.put(0xC3)
        elif n == 16:
            self.put(0xCC)
        else:
            return 1
        return 0

    # K5-M011 m_bjmp
    def bjmp(self):
        st = self.st
        if st.da1v != BASE_OFF and not st.lab(st.da1v):
            return 1
        self.out.append("$")
        self.out.append("base" if st.da1v == BASE_OFF else
                        st.labname(st.da1v))
        if st.dlen == 2:
            self.out.append(":1")
            self.put(0xEB)
            self.mslot = self.mlen
            self.mslotz = 1
            self.mslof = st.da1v
        else:
            self.put(0xE9)
            self.mslot = self.mlen
            self.mslotz = 4
            self.mslof = st.da1v
        return 0

    # K5-M012 m_bjcc
    def bjcc(self):
        st = self.st
        if st.da1v != BASE_OFF and not st.lab(st.da1v):
            return 1
        self.out.append("$")
        self.out.append("base" if st.da1v == BASE_OFF else
                        st.labname(st.da1v))
        if st.dlen == 2:
            self.out.append(":1")
            self.put(0x70 | st.dcc)
            self.mslot = self.mlen
            self.mslotz = 1
            self.mslof = st.da1v
        else:
            self.put(0x0F)
            self.put(0x80 | st.dcc)
            self.mslot = self.mlen
            self.mslotz = 4
            self.mslof = st.da1v
        return 0

    # K5-M013 m_bcall
    def bcall(self):
        st = self.st
        if st.da1k == 4:
            if st.da1v == BASE_OFF:
                return 1                # call $base — нет (оракула)
            if not st.lab(st.da1v):
                return 1
            self.out.append("$" + st.labname(st.da1v))
            self.put(0xE8)
            self.mslot = self.mlen
            self.mslotz = 4
            self.mslof = st.da1v
            return 0
        if st.da1k == 2 and st.mripon == 1:
            if st.omrip != BASE_OFF and not st.lab(st.omrip):
                return 1
            self.out.append("[rip+$")
            self.out.append("base" if st.omrip == BASE_OFF else
                            st.labname(st.omrip))
            self.out.append("]")
            self.put(0xFF)
            self.put(0x15)
            self.mslot = self.mlen
            self.mslotz = 4
            self.mslof = st.omrip
            return 0
        return 1

    # K5-M014 m_bmovzx
    def bmovzx(self):
        st = self.st
        if st.da1k != 1 or st.da1s not in (32, 64):
            return 1
        if st.da2k == 1:
            if st.da2s != 8:
                return 1
            self.out.append(self._regname(1))
            self.out.append(", ")
            self.out.append(self._regname(2))
            self.rex(0, 1 if st.da1r >= 8 else 0, 0,
                     1 if st.da2r >= 8 else 0)
            self.put(0x0F)
            self.put(0xB6)
            self.put(0xC0 + (st.da1r & 7) * 8 + (st.da2r & 7))
            return 0
        if st.da2k == 2 and st.da2s in (8, 16):
            self.out.append(self._regname(1))
            self.out.append(", ")
            if self.opmem(2, True) != 0:
                return 1
            self.memxb()
            self.rex(0, 1 if st.da1r >= 8 else 0, self.memx, self.memb)
            self.put(0x0F)
            self.put(0xB6 if st.da2s == 8 else 0xB7)
            self.enc_mem(st.da1r & 7)
            return 0
        return 1

    def _regname(self, slot):
        size = self._gets(slot)
        idx = self._getr(slot)
        if size == 8:
            return REG8[idx]
        if size == 32:
            return REG32[idx]
        return REG64[idx]

    # K5-M015 m_bstack: push/pop (reg 64)
    def bstack(self):
        st = self.st
        if st.da1k != 1 or st.da1s != 64:
            return 1
        self.out.append(self._regname(1))
        self.rex(0, 0, 0, 1 if st.da1r >= 8 else 0)
        if st.dname == 10:
            self.put(0x50 | (st.da1r & 7))
        else:
            self.put(0x58 | (st.da1r & 7))
        return 0

    # K5-M016 m_btest
    def btest(self):
        st = self.st
        if st.da1k != 1 or st.da2k != 1:
            return 1
        if st.da1s != st.da2s or st.da1s == 16:
            return 1
        self.out.append(self._regname(1))
        self.out.append(", ")
        self.out.append(self._regname(2))
        op = 0x84 if st.da1s == 8 else 0x85
        self.rex(1 if st.da1s == 64 else 0, 1 if st.da2r >= 8 else 0, 0,
                 1 if st.da1r >= 8 else 0)
        self.put(op)
        self.put(0xC0 + (st.da2r & 7) * 8 + (st.da1r & 7))
        return 0

    # K5-M017 m_blea
    def blea(self):
        st = self.st
        if st.da1k != 1 or st.da1s not in (32, 64):
            return 1
        if st.da2k != 2:
            return 1
        self.out.append(self._regname(1))
        self.out.append(", ")
        if self.opmem(2, False) != 0:
            return 1
        self.memxb()
        self.rex(1 if st.da1s == 64 else 0, 1 if st.da1r >= 8 else 0,
                 self.memx, self.memb)
        self.put(0x8D)
        self.enc_mem(st.da1r & 7)
        return 0

    # K5-M018 m_bimul
    def bimul(self):
        st = self.st
        if st.da1k != 1 or st.da2k != 1:
            return 1
        if st.da1s != 64 or st.da2s != 64:
            return 1
        self.out.append(self._regname(1))
        self.out.append(", ")
        self.out.append(self._regname(2))
        self.rex(1, 1 if st.da1r >= 8 else 0, 0,
                 1 if st.da2r >= 8 else 0)
        self.put(0x0F)
        self.put(0xAF)
        self.put(0xC0 + (st.da1r & 7) * 8 + (st.da2r & 7))
        return 0

    # K5-M019 m_bshift: rol/shl/shr/sar
    def bshift(self):
        st = self.st
        ext = {21: 0, 22: 4, 23: 5, 24: 7}[st.dname]
        if st.da1k != 1 or st.da1s == 16:
            return 1
        if st.da2k == 6:
            v = st.da2v
            if v < 0 or v > 255:
                return 1
            self.out.append(self._regname(1))
            self.out.append(", ")
            self.out.append(hexs(v))
            op = 0xC0 if st.da1s == 8 else 0xC1
            self.rex(1 if st.da1s == 64 else 0, 0, 0,
                     1 if st.da1r >= 8 else 0)
            self.put(op)
            self.put(0xC0 + ext * 8 + (st.da1r & 7))
            self.put(v & 0xFF)
            return 0
        if st.da2k == 5:
            self.out.append(self._regname(1))
            self.out.append(", ")
            self.out.append("cl")
            op = 0xD2 if st.da1s == 8 else 0xD3
            self.rex(1 if st.da1s == 64 else 0, 0, 0,
                     1 if st.da1r >= 8 else 0)
            self.put(op)
            self.put(0xC0 + ext * 8 + (st.da1r & 7))
            return 0
        return 1

    # K5-M020 m_bf7: neg/idiv
    def bf7(self):
        st = self.st
        if st.da1k != 1 or st.da1s not in (32, 64):
            return 1
        ext = 3 if st.dname == 25 else 7
        self.out.append(self._regname(1))
        self.rex(1 if st.da1s == 64 else 0, 0, 0,
                 1 if st.da1r >= 8 else 0)
        self.put(0xF7)
        self.put(0xC0 + ext * 8 + (st.da1r & 7))
        return 0

    # K5-M021 m_bff: inc/dec
    def bff(self):
        st = self.st
        if st.da1k != 1 or st.da1s not in (32, 64):
            return 1
        ext = 0 if st.dname == 27 else 1
        self.out.append(self._regname(1))
        self.rex(1 if st.da1s == 64 else 0, 0, 0,
                 1 if st.da1r >= 8 else 0)
        self.put(0xFF)
        self.put(0xC0 + ext * 8 + (st.da1r & 7))
        return 0

    # K5-M022 m_balu: add/or/and/sub/xor/cmp
    def balu(self):
        st = self.st
        k1 = st.da1k
        k2 = st.da2k
        base = self.alu_base()
        ext = self.alu_ext()
        if k1 == 1 and k2 == 1:
            if st.da1s != st.da2s:
                return 1
            self.out.append(self._regname(1))
            self.out.append(", ")
            self.out.append(self._regname(2))
            op = base if st.da1s == 8 else base + 1
            self.rex(1 if st.da1s == 64 else 0, 1 if st.da2r >= 8 else 0,
                     0, 1 if st.da1r >= 8 else 0)
            self.put(op)
            self.put(0xC0 + (st.da2r & 7) * 8 + (st.da1r & 7))
            return 0
        if k1 == 1 and k2 == 3:
            v = st.da2v
            self.out.append(self._regname(1))
            self.out.append(", ")
            self.out.append(hexs(v))
            if st.da1s == 8:
                if v < -128 or v > 255:
                    return 1
                self.rex(0, 0, 0, 1 if st.da1r >= 8 else 0)
                self.put(0x80)
                self.put(0xC0 + ext * 8 + (st.da1r & 7))
                self.put(v & 0xFF)
                return 0
            if -128 <= v <= 127:
                self.rex(1 if st.da1s == 64 else 0, 0, 0,
                         1 if st.da1r >= 8 else 0)
                self.put(0x83)
                self.put(0xC0 + ext * 8 + (st.da1r & 7))
                self.put(v & 0xFF)
                return 0
            if st.da1s == 64 and (v < -2147483648 or v > 2147483647):
                return 1
            self.rex(1 if st.da1s == 64 else 0, 0, 0,
                     1 if st.da1r >= 8 else 0)
            self.put(0x81)
            self.put(0xC0 + ext * 8 + (st.da1r & 7))
            self.put4(v)
            return 0
        if k1 == 1 and k2 == 2:
            self.out.append(self._regname(1))
            self.out.append(", ")
            if self.opmem(2, False) != 0:
                return 1
            op = base + 2 if st.da1s == 8 else base + 3
            self.memxb()
            self.rex(1 if st.da1s == 64 else 0, 1 if st.da1r >= 8 else 0,
                     self.memx, self.memb)
            self.put(op)
            self.enc_mem(st.da1r & 7)
            return 0
        if k1 == 2 and k2 == 1:
            if self.opmem(1, False) != 0:
                return 1
            self.out.append(", ")
            self.out.append(self._regname(2))
            op = base if st.da2s == 8 else base + 1
            self.memxb()
            self.rex(1 if st.da2s == 64 else 0, 1 if st.da2r >= 8 else 0,
                     self.memx, self.memb)
            self.put(op)
            self.enc_mem(st.da2r & 7)
            return 0
        if k1 == 2 and k2 == 3:
            if st.da1s not in (8, 32, 64):
                return 1
            if st.mripon == 1:
                return 1                # rip + imm — вне канона
            v = st.da2v
            if self.opmem(1, True) != 0:
                return 1
            self.out.append(", ")
            self.out.append(hexs(v))
            if st.da1s == 8:
                if v < -128 or v > 255:
                    return 1
                opc = 0x80
            else:
                if -128 <= v <= 127:
                    opc = 0x83
                else:
                    if st.da1s == 64 and (v < -2147483648
                                         or v > 2147483647):
                        return 1
                    opc = 0x81
            self.memxb()
            self.rex(1 if st.da1s == 64 else 0, 0, self.memx, self.memb)
            self.put(opc)
            self.enc_mem(ext)
            if opc == 0x83 or (opc == 0x80 and st.da1s == 8) \
                    or opc == 0x80:
                if st.da1s == 8 or opc == 0x83:
                    self.put(v & 0xFF)
                else:
                    self.put(v & 0xFF)
            if opc == 0x81:
                self.put4(v)
            return 0
        return 1

    # K5-M023 m_bmov
    def bmov(self):
        st = self.st
        k1 = st.da1k
        k2 = st.da2k
        if k1 == 1 and k2 == 1:
            if st.da1s != st.da2s:
                return 1
            if st.da1s == 16:
                return 1
            self.out.append(self._regname(1))
            self.out.append(", ")
            self.out.append(self._regname(2))
            op = 0x88 if st.da1s == 8 else 0x89
            self.rex(1 if st.da1s == 64 else 0, 1 if st.da2r >= 8 else 0,
                     0, 1 if st.da1r >= 8 else 0)
            self.put(op)
            self.put(0xC0 + (st.da2r & 7) * 8 + (st.da1r & 7))
            return 0
        if k1 == 1 and k2 == 3:
            v = st.da2v
            if st.da1s == 8:
                if v < -128 or v > 255:
                    return 1
                self.out.append(self._regname(1))
                self.out.append(", ")
                self.out.append(hexs(v))
                self.rex(0, 0, 0, 1 if st.da1r >= 8 else 0)
                self.put(0xB0 | (st.da1r & 7))
                self.put(v & 0xFF)
                return 0
            if st.da1s == 32:
                self.out.append(self._regname(1))
                self.out.append(", ")
                self.out.append(hexs(v))
                self.rex(0, 0, 0, 1 if st.da1r >= 8 else 0)
                self.put(0xB8 | (st.da1r & 7))
                self.put4(v)
                return 0
            if v < -2147483648 or v > 2147483647:
                return 1
            self.out.append(self._regname(1))
            self.out.append(", ")
            self.out.append(hexs(v))
            self.put(0x48 | (1 if st.da1r >= 8 else 0))
            self.put(0xC7)
            self.put(0xC0 | (st.da1r & 7))
            self.put4(v)
            return 0
        if k1 == 1 and k2 == 2:
            self.out.append(self._regname(1))
            self.out.append(", ")
            if self.opmem(2, False) != 0:
                return 1
            op = 0x8A if st.da1s == 8 else 0x8B
            self.memxb()
            self.rex(1 if st.da1s == 64 else 0, 1 if st.da1r >= 8 else 0,
                     self.memx, self.memb)
            self.put(op)
            self.enc_mem(st.da1r & 7)
            return 0
        if k1 == 2 and k2 == 1:
            if self.opmem(1, False) != 0:
                return 1
            self.out.append(", ")
            self.out.append(self._regname(2))
            op = 0x88 if st.da2s == 8 else 0x89
            self.memxb()
            self.rex(1 if st.da2s == 64 else 0, 1 if st.da2r >= 8 else 0,
                     self.memx, self.memb)
            self.put(op)
            self.enc_mem(st.da2r & 7)
            return 0
        if k1 == 2 and k2 == 3:
            if st.da1s not in (8, 32, 64):
                return 1
            if st.mripon == 1:
                return 1
            v = st.da2v
            if self.opmem(1, True) != 0:
                return 1
            self.out.append(", ")
            self.out.append(hexs(v))
            if st.da1s == 8:
                if v < 0 or v > 255:
                    return 1
                self.memxb()
                self.rex(0, 0, self.memx, self.memb)
                self.put(0xC6)
                self.enc_mem(0)
                self.put(v & 0xFF)
                return 0
            if st.da1s == 64:
                if v < -2147483648 or v > 2147483647:
                    return 1
                self.memxb()
                self.rex(1, 0, self.memx, self.memb)
                self.put(0xC7)
                self.enc_mem(0)
                self.put4(v)
                return 0
            self.memxb()
            self.rex(0, 0, self.memx, self.memb)
            self.put(0xC7)
            self.enc_mem(0)
            self.put4(v)
            return 0
        return 1


def m_line_trace(st):
    """K5-M009 драйвер: → текст M-строки | None (H-фолбэк)."""
    m = M(st)
    n = st.dname
    # имя мнемоники (jcc: j + cc)
    if n == 0:
        name = "j" + ["o", "no", "b", "ae", "z", "nz", "be", "a", "s",
                      "ns", "p", "np", "l", "ge", "le", "g"][st.dcc]
        rc = m.bjcc()
    elif n == 17:
        name = "jmp"
        rc = m.bjmp()
    elif n == 18:
        name = "call"
        rc = m.bcall()
    elif n in (12, 13, 15, 16):
        name = {12: "cdqe", 13: "cqo", 15: "ret", 16: "int3"}[n]
        rc = m.bsimple()
    elif n == 14:
        return None                     # cdq — нет в SIMPLE enc
    elif n == 19:
        name = "movzx"
        rc = m.bmovzx()
    elif n in (10, 11):
        name = {10: "push", 11: "pop"}[n]
        rc = m.bstack()
    elif n == 7:
        name = "test"
        rc = m.btest()
    elif n == 9:
        name = "lea"
        rc = m.blea()
    elif n == 20:
        name = "imul"
        rc = m.bimul()
    elif n in (21, 22, 23, 24):
        name = {21: "rol", 22: "shl", 23: "shr", 24: "sar"}[n]
        rc = m.bshift()
    elif n == 25:
        name = "neg"
        rc = m.bf7()
    elif n == 26:
        name = "idiv"
        rc = m.bf7()
    elif n == 27:
        name = "inc"
        rc = m.bff()
    elif n == 28:
        name = "dec"
        rc = m.bff()
    elif n in (1, 2, 3, 4, 5, 6):
        name = {1: "add", 2: "or", 3: "and", 4: "sub", 5: "xor",
                6: "cmp"}[n]
        rc = m.balu()
    elif n == 8:
        name = "mov"
        rc = m.bmov()
    else:
        return None
    if rc != 0:
        return None
    if m.cmp() != 0:
        return None
    txt = name
    if m.out:
        txt += " " + "".join(m.out)
    return "M %s ; @%04X" % (txt, st.lo)


def labels_of(fam):
    """Точная копия вычисления меток _emit_lines (как probe_e92_3c)."""
    import bisect
    import lab_bridge as lb
    ins = fam["ins"]
    limit = fam["target"]
    labels, semantic, _known = lb._import_map(fam)
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
            sem[o] = v
    starts_sorted = sorted(ins)
    sem_ranges = [(o, o + (4 if v[0] == "DD" else 8) * len(v[1]))
                  for o, v in sem.items()]

    def inside_ins(o):
        i = bisect.bisect_right(starts_sorted, o) - 1
        return i >= 0 and starts_sorted[i] < o < \
            starts_sorted[i] + ins[starts_sorted[i]][1]

    def inside_sem(o):
        return any(s < o < e for s, e in sem_ranges)

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
                if off == lb.BASE_OFF or off in labels:
                    continue
                if off in ins or off in sem:
                    labels[off] = "l%x" % (off + lb.SECT)
                elif 0 <= off < limit and not inside_ins(off) \
                        and not inside_sem(off):
                    labels[off] = "d%x" % (off + lb.SECT)
    return labels


def check_one(data, tag, rep):
    fam = lab_bridge.parse_family(data)
    labels = labels_of(fam)
    # строки оракула по смещениям
    lines, st = lab_bridge._emit_lines(fam, None)
    oline = {}
    for s in lines:
        p = s.rsplit("@", 1)
        if len(p) == 2 and p[1][:1].upper() == "X" or \
                (len(p) == 2 and p[1][:4].isdigit() is False):
            pass
    # проще: индекс по хвосту «@%04X»
    for s in lines:
        if s.startswith(":") or s.startswith("D") or s.startswith("M ") \
                or s.startswith("H "):
            j = s.rfind("@")
            if j >= 0:
                try:
                    off = int(s[j + 1:], 16)
                    oline[off] = s
                except ValueError:
                    pass
    bad = 0
    for a in sorted(fam["ins"]):
        want = oline.get(a)
        mine = m_line_trace(St(fam, labels, a))
        if want is not None and want.startswith("M "):
            if mine != want:
                bad += 1
                if rep[0] < 10:
                    rep.append("%s @%04X: оракул «%s» != наш «%s»"
                               % (tag, a, want, mine))
        else:
            if mine is not None:
                bad += 1
                if rep[0] < 10:
                    rep.append("%s @%04X: оракул H, наш «%s»"
                               % (tag, a, mine))
    rep[0] += len(fam["ins"])
    return bad


def synth_cases(kfile):
    """Синтетика T-E9-22: synthm (тень), hint-ins, imp0.

    synthm — тело uva[:0x200] (импорт-область канона WALL у RVA 0x1000)
    + крафт (как T-E9-21: 0x200 jz +2, 0x202 mov eax,imm32, 0x204
    add — ТЕНЬ, 0x207 ret, 0x208 нули); peg — поля образа uva."""
    uva = kfile("L3-UVA/uva.exe")
    ufam = lab_bridge.parse_family(uva)
    pe = ufam["pe"]
    craft = bytes([0x74, 0x02, 0xB8, 0x05, 0x05, 0x05, 0x05,
                   0xC3, 0x00, 0x00])
    peg = "; synth\n!module synthm\n!entry 1200\n!idata %X %X\n" \
          "!iat %X %X\n" % (pe["dd1_import_rva"], pe["dd1_import_size"],
                            pe["dd12_iat_rva"], pe["dd12_iat_size"])
    synth = lab_pegen.wrap(bytes(ufam["body"])[:0x200] + craft, peg)
    _fam = lab_bridge.parse_family(kfile("L0-SEED/seed.exe"))
    _imp = _fam["pe"]["imports"][0]
    _intf = _imp["oft_rva"] - 0x1000 + _fam["pe"]["sec_raw_ptr"]
    _seed = kfile("L0-SEED/seed.exe")
    mut_hint = bytearray(_seed)
    mut_hint[_intf:_intf + 8] = (0x102C).to_bytes(8, "little")
    mut_imp0 = bytearray(_seed)
    mut_imp0[_intf:_intf + 8] = (0).to_bytes(8, "little")
    return [(synth, "synthm"), (bytes(mut_hint), "hint-ins"),
            (bytes(mut_imp0), "imp0")]


def main():
    def kfile(rel):
        return open(os.path.join(ROOT, "KERNEL", rel), "rb").read()

    rep = [0]
    total_bad = 0
    total_ins = 0
    for m in ARTIFACTS:
        data = kfile("%s.exe" % m)
        n0 = rep[0]
        bad = check_one(data, m.split("/")[-1], rep)
        total_bad += bad
        print("%-10s инструкций %5d  расхождений %d"
              % (m.split("/")[-1], rep[0] - n0, bad))
    for data, tag in synth_cases(kfile):
        n0 = rep[0]
        bad = check_one(data, tag, rep)
        total_bad += bad
        print("%-10s инструкций %5d  расхождений %d" % (tag, rep[0] - n0,
                                                        bad))
    print()
    if total_bad == 0:
        print("ИТОГ: %d/%d — план ветви M совпадает с оракулом на"
              " каждом решении и каждом тексте строки" % (rep[0], rep[0]))
    else:
        print("ИТОГ: расхождений %d из %d:" % (total_bad, rep[0]))
        for s in rep[1:12]:
            print("  " + s)


if __name__ == "__main__":
    main()
