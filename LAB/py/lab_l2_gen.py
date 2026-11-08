"""lab_l2_gen.py — бэкенд оракула WALL v1 (SPEC/11): AST -> текст BRICK v2.

Вход:  программа (AST из lab_l2.parse), таблица имён, карта строк исходника.
Выход: текст .b2 (BRICK v2) — детерминированный; правила раскладки слотов,
       кадров и эмиттеров — SPEC/11 (это канон: wall.exe обязан повторять
       этот выход байт-в-байт).
Ошибки: WallError(сообщение, номер_строки) — номер с 1.
Функция: кирпич кодогенерации слоя L2; вызывается lab_l2.compile_wall().
"""
from lab_l2_err import WallError            # noqa: F401  (реэкспорт)

ARGREG = ("rcx", "rdx", "r8", "r9")
JINV = {"==": "jne", "!=": "je", "<": "jge", "<=": "jg",
        ">": "jle", ">=": "jl"}
ALU = {"+": "add", "-": "sub", "&": "and", "|": "or", "^": "xor"}
# фиксированная раскладка области импортов (SPEC/11 п.6)
IMP_IDT = 0x28          # описатель + терминатор
IMP_IAT = 0x48          # 9 слотов QWORD
IMP_ALL = 0xB8
HINT_SLOT = 34          # 2 (hint) + 31 (имя) + 1 (NUL), выравнивание чётно
HINT_SLOTS = 8
ENTRY_RVA_OFF = 0x200   # смещение :_entry в теле (RVA 0x1200)
MAXLABELS = 500


def _hex(v):
    return "%X" % v


def _align16(v):
    return (v + 15) & ~15


def need(e):
    """Число T-слотов выражения при генерации с текущей глубины."""
    t = e[0]
    if t == "neg":
        return need(e[1])
    if t == "bin":
        return 1 + max(need(e[2]), need(e[3]))
    if t == "getb":
        return 1 + max(need(e[1]), need(e[2]))
    if t == "call":
        return max([need(a) for a in e[2]] + [0])
    return 0                      # num, name, addr, len


class Layout:
    """Раскладка кадровых слотов функции (SPEC/11 п.7)."""

    def __init__(self, fn, names, funcparams):
        self.fn = fn
        self.names = names
        self.fp = funcparams
        base = list(fn["params"]) + list(fn["locals"])
        self.base = {n: i for i, n in enumerate(base)}
        self.nbase = len(base)
        self.maxd = self.maxc = 0
        self.setb = self.ext5 = False
        self._scan(fn["body"])
        self.nslots = (self.nbase + self.maxd + self.maxc +
                       (3 if self.setb else 0) + (1 if self.ext5 else 0))
        self.framesize = _align16(8 * self.nslots) + 0x30

    def _upd(self, d):
        self.maxd = max(self.maxd, d)

    def _call(self, name, args):
        kind = self.names.get(name)
        n = len(args)
        self.maxc = max(self.maxc, min(n, 4) if kind == "ext" else n)
        if kind == "ext" and n == 5:
            self.ext5 = True
        for a in args:
            self._scan_expr(a)

    def _scan_expr(self, e):
        """обход выражения: вызовы (в т.ч. вложенные) дают C-слоты"""
        t = e[0]
        if t == "call":
            self._call(e[1], e[2])
        elif t == "bin":
            self._scan_expr(e[2])
            self._scan_expr(e[3])
        elif t == "neg":
            self._scan_expr(e[1])
        elif t == "getb":
            self._scan_expr(e[1])
            self._scan_expr(e[2])

    def _scan(self, body):
        for st in body:
            t = st[0]
            if t == "assign":
                self._scan_expr(st[2])
                self._upd(need(st[2]))
            elif t == "return":
                if st[1] is not None:
                    self._scan_expr(st[1])
                    self._upd(need(st[1]))
            elif t == "call":
                self._call(st[1], st[2])
            elif t == "setb":
                self.setb = True
                for e in (st[1], st[2], st[3]):
                    self._scan_expr(e)
                    self._upd(need(e))
            elif t == "if":
                c = st[1]
                self._scan_expr(c[1])
                self._scan_expr(c[2])
                self._upd(1 + max(need(c[1]), need(c[2])))
                self._scan(st[2])
                self._scan(st[3])
            elif t == "while":
                c = st[1]
                self._scan_expr(c[1])
                self._scan_expr(c[2])
                self._upd(1 + max(need(c[1]), need(c[2])))
                self._scan(st[2])

    # смещения слотов (rbp-относительные, 0-базовый индекс)
    def _off(self, idx):
        return 8 * (idx + 1)

    def local(self, name):
        return self._off(self.base[name])

    def t(self, d):
        return self._off(self.nbase + d - 1)

    def c(self, i):
        return self._off(self.nbase + self.maxd + i - 1)

    def s(self, i):
        return self._off(self.nbase + self.maxd + self.maxc + i)


class Gen:
    """Эмиттер: программа -> список строк .b2 (SPEC/11 п.8 — канон)."""

    def __init__(self, prog, names, srcmap):
        self.prog, self.names, self.src = prog, names, srcmap
        self.fp = {f["name"]: len(f["params"]) for f in prog["funcs"]}
        self.out = []
        self.k = 0            # счётчик меток _if/_w
        self.nlab = 0         # контроль лимита меток brick

    def m(self, cmt, text):
        self.out.append("M %s ; %s" % (text, cmt))

    def lbl(self, name):
        self.out.append(":" + name)
        self.nlab += 1

    def raw(self, line):
        self.out.append(line)

    # ------------------------------------------------------------- запуск
    def run(self):
        p = self.prog
        nl = p["nlines"]
        self.raw("; UNIVERSAL / WALL v1 / сгенерировано компилятором WALL"
                 " (SPEC/11)")
        self.raw("; исходник: %d строк; функций: %d; ext: %d; str: %d; "
                 "глобальных var: %d"
                 % (nl, len(p["funcs"]), len(p["exts"]),
                    len(p["strs"]), len(p["globals"])))
        self._imports()
        self.raw("; --- код ---")
        self.lbl("_entry")
        self.m("вход: выравнивание стека для вызова main", "sub rsp, 8")
        self.m("вход: вызов main", "call $main")
        self.m("вход: возврат из main без ExitProcess — ловушка", "int3")
        for fn in p["funcs"]:
            self._func(fn)
        if p["strs"]:
            self.raw("; --- данные: строки ---")
            for name, bs, no in p["strs"]:
                self.lbl(name)
                src = self.src[no]
                if not bs:
                    self.raw("DZ 0 ; %s" % src)
                for i in range(0, len(bs), 16):
                    self.raw("DB %s ; %s" % (" ".join(
                        "%02X" % b for b in bs[i:i + 16]), src))
        if p["globals"]:
            self.raw("; --- данные: глобальные переменные (нулевые ячейки) ---")
            for name, no in p["globals"]:
                self.lbl(name)
                self.raw("DZ 8 ; %s" % self.src[no])
        if self.nlab > MAXLABELS:
            raise WallError("больше %d меток" % MAXLABELS, 0)
        return "\n".join(self.out) + "\n"

    # ------------------------------------------------------------- импорты
    def _imports(self):
        exts = self.prog["exts"]
        self.raw("; --- импорты: фиксированная область 0x200 байт (SPEC/11) ---")
        self.lbl("_idt")
        if exts:
            self.raw("DD $_intt 0 0 $_dll $_iat ; описатель импорта"
                     " kernel32")
        else:
            self.raw("DD 0 0 0 0 0 ; без импортов")
        self.raw("DZ 14 ; терминатор IDT")
        self.lbl("_iat")
        for i, e in enumerate(exts):
            self.lbl("_iat_" + e.lower())
            self.raw("DQ $_hint_%s" % e.lower())
        self.raw("DQ " + " ".join(["0"] * (HINT_SLOTS + 1 - len(exts))))
        self.lbl("_intt")
        vals = ["$_hint_" + e.lower() for e in exts]
        self.raw("DQ " + " ".join(vals + ["0"] * (HINT_SLOTS + 1 - len(exts))))
        if exts:
            self.lbl("_dll")
            self.raw("DB 6B 65 72 6E 65 6C 33 32 2E 64 6C 6C 00"
                     ' ; "kernel32.dll\\0"')
            self.raw("DZ 1 ; выравнивание")
            for i in range(HINT_SLOTS):
                if i < len(exts):
                    nm = exts[i]
                    row = [0, 0] + list(nm.encode("ascii")) + [0]
                    row += [0] * (HINT_SLOT - len(row))
                    self.lbl("_hint_" + nm.lower())
                    self.raw('DB %s ; "%s"' % (" ".join(
                        "%02X" % b for b in row), nm))
                else:
                    self.raw("DZ 22 ; свободный слот импорта")
            self.raw("DZ 2A ; выравнивание области до 0x200")
        else:
            self.raw("DZ 148 ; без импортов: выравнивание области до 0x200")

    # ------------------------------------------------------------ функция
    def _func(self, fn):
        lay = Layout(fn, self.names, self.fp)
        self.lbl(fn["name"])
        c = "кадр %s" % fn["name"]
        self.m(c, "push rbp")
        self.m(c, "mov rbp, rsp")
        self.m(c, "sub rsp, %s" % _hex(lay.framesize))
        for i, pn in enumerate(fn["params"]):
            self.m(c, "mov [rbp-%s], %s" % (_hex(lay.local(pn)), ARGREG[i]))
        self._body(fn["body"], lay, fn)
        # эпилог не нужен, если последнее утверждение — return (SPEC/11)
        if not (fn["body"] and fn["body"][-1][0] == "return"):
            self._epilogue(fn)

    def _epilogue(self, fn):
        c = "выход %s" % fn["name"]
        self.m(c, "mov rsp, rbp")
        self.m(c, "pop rbp")
        self.m(c, "ret")

    def _body(self, body, lay, fn):
        for st in body:
            t = st[0]
            if t == "var":
                continue
            if t == "assign":
                src = self.src[st[3]]
                self.expr(st[2], 1, lay, src)
                name = st[1]
                if name in lay.base:
                    self.m(src, "mov [rbp-%s], r10" % _hex(lay.local(name)))
                elif self.names.get(name) == "var":
                    self.m(src, "mov [rip+$%s], r10" % name)
                elif self.names.get(name) == "str":
                    raise WallError("строка %r неизменяема (только setb)"
                                    % name, st[3])
                elif name in self.names:
                    raise WallError("%r — не переменная" % name, st[3])
                else:
                    raise WallError("неизвестное имя %r" % name, st[3])
            elif t == "return":
                src = self.src[st[2]]
                if st[1] is not None:
                    self.expr(st[1], 1, lay, src)
                    self.m(src, "mov rax, r10")
                self._epilogue(fn)
            elif t == "call":
                self.call(st[1], st[2], st[3], 1, lay, False,
                          self.src[st[3]])
            elif t == "setb":
                src = self.src[st[4]]
                self.expr(st[1], 1, lay, src)
                self.m(src, "mov [rbp-%s], r10" % _hex(lay.s(0)))
                self.expr(st[2], 1, lay, src)
                self.m(src, "mov [rbp-%s], r10" % _hex(lay.s(1)))
                self.expr(st[3], 1, lay, src)
                self.m(src, "mov [rbp-%s], r10" % _hex(lay.s(2)))
                self.m(src, "mov r10, [rbp-%s]" % _hex(lay.s(0)))
                self.m(src, "mov r11, [rbp-%s]" % _hex(lay.s(1)))
                self.m(src, "mov al, [rbp-%s]" % _hex(lay.s(2)))
                self.m(src, "mov [r10+r11], al")
            elif t == "if":
                self._if(st, lay, fn)
            elif t == "while":
                self._while(st, lay, fn)

    def _cond(self, c, lay, src):
        self.expr(c[1], 2, lay, src)
        self.m(src, "mov [rbp-%s], r10" % _hex(lay.t(1)))
        self.expr(c[2], 2, lay, src)
        self.m(src, "mov r11, r10")
        self.m(src, "mov r10, [rbp-%s]" % _hex(lay.t(1)))
        self.m(src, "cmp r10, r11")

    def _if(self, st, lay, fn):
        cond, then, els, no = st[1], st[2], st[3], st[4]
        src = self.src[no]
        self.k += 1
        k = self.k
        self._cond(cond, lay, src)
        if els:
            self.m(src, "%s $_if%d" % (JINV[cond[0]], k))
            self._body(then, lay, fn)
            self.m(src, "jmp $_if%de" % k)
            self.lbl("_if%d" % k)
            self._body(els, lay, fn)
            self.lbl("_if%de" % k)
        else:
            self.m(src, "%s $_if%de" % (JINV[cond[0]], k))
            self._body(then, lay, fn)
            self.lbl("_if%de" % k)

    def _while(self, st, lay, fn):
        cond, body, no = st[1], st[2], st[3]
        src = self.src[no]
        self.k += 1
        k = self.k
        self.lbl("_w%d" % k)
        self._cond(cond, lay, src)
        self.m(src, "%s $_w%de" % (JINV[cond[0]], k))
        self._body(body, lay, fn)
        self.m(src, "jmp $_w%d" % k)
        self.lbl("_w%de" % k)

    # --------------------------------------------------------- выражения
    def expr(self, e, d, lay, src):
        t = e[0]
        if t == "num":
            self.m(src, "mov r10, %s" % _hex(e[1]))
        elif t == "neg":
            self.expr(e[1], d, lay, src)
            self.m(src, "neg r10")
        elif t == "name":
            self._load_name(e[1], e[2], lay, src)
        elif t == "addr":
            name, no = e[1], e[2]
            if name in lay.base:
                self.m(src, "lea r10, [rbp-%s]" % _hex(lay.local(name)))
            elif self.names.get(name) in ("var", "str"):
                self.m(src, "lea r10, [rip+$%s]" % name)
            elif name in self.names:
                raise WallError("& не применимо к %r" % name, no)
            else:
                raise WallError("неизвестное имя %r" % name, no)
        elif t == "len":
            if self.names.get(e[1]) != "str":
                raise WallError("len применим только к str", e[2])
            n = len(dict((n, b) for n, b, _ in self.prog["strs"])[e[1]])
            self.m(src, "mov r10, %s" % _hex(n))
        elif t == "bin":
            self.expr(e[2], d + 1, lay, src)
            self.m(src, "mov [rbp-%s], r10" % _hex(lay.t(d)))
            self.expr(e[3], d + 1, lay, src)
            self.m(src, "mov r11, r10")
            self.m(src, "mov r10, [rbp-%s]" % _hex(lay.t(d)))
            if e[1] in ALU:
                self.m(src, "%s r10, r11" % ALU[e[1]])
            else:
                self.m(src, "mov rcx, r11")
                self.m(src, "%s r10, cl" % ("shl" if e[1] == "<<" else "shr"))
        elif t == "getb":
            self.expr(e[1], d + 1, lay, src)
            self.m(src, "mov [rbp-%s], r10" % _hex(lay.t(d)))
            self.expr(e[2], d + 1, lay, src)
            self.m(src, "mov r11, r10")
            self.m(src, "mov r10, [rbp-%s]" % _hex(lay.t(d)))
            self.m(src, "movzx r10d, byte [r10+r11]")
        elif t == "call":
            self.call(e[1], e[2], e[3], d, lay, True, src)

    def _load_name(self, name, no, lay, src):
        if name in lay.base:
            self.m(src, "mov r10, [rbp-%s]" % _hex(lay.local(name)))
            return
        kind = self.names.get(name)
        if kind == "var":
            self.m(src, "mov r10, [rip+$%s]" % name)
        elif kind == "str":
            self.m(src, "lea r10, [rip+$%s]" % name)
        elif kind is None:
            raise WallError("неизвестное имя %r" % name, no)
        else:
            raise WallError("%r — функция, не значение" % name, no)

    def call(self, name, args, no, d, lay, want, src):
        kind = self.names.get(name)
        if kind == "func":
            if len(args) != self.fp[name]:
                raise WallError("функция %s ожидает %d аргументов, получено %d"
                                % (name, self.fp[name], len(args)), no)
            for i, a in enumerate(args, 1):
                self.expr(a, d, lay, src)
                self.m(src, "mov [rbp-%s], r10" % _hex(lay.c(i)))
            for i in range(len(args)):
                self.m(src, "mov %s, [rbp-%s]"
                       % (ARGREG[i], _hex(lay.c(i + 1))))
            self.m(src, "call $%s" % name)
            if want:
                self.m(src, "mov r10, rax")
        elif kind == "ext":
            if len(args) > 5:
                raise WallError("ext-вызов %s: больше 5 аргументов" % name, no)
            for i, a in enumerate(args, 1):
                self.expr(a, d, lay, src)
                if i <= 4:
                    self.m(src, "mov [rbp-%s], r10" % _hex(lay.c(i)))
                else:
                    self.m(src, "mov [rbp-%s], r10" % _hex(lay.s(3)))
            for i in range(min(len(args), 4)):
                self.m(src, "mov %s, [rbp-%s]"
                       % (ARGREG[i], _hex(lay.c(i + 1))))
            if len(args) == 5:
                self.m(src, "mov r10, [rbp-%s]" % _hex(lay.s(3)))
                self.m(src, "mov [rsp+20], r10")
            self.m(src, "call [rip+$_iat_%s]" % name.lower())
            if want:
                self.m(src, "mov r10, rax")
        elif kind is None:
            raise WallError("неизвестное имя %r" % name, no)
        else:
            raise WallError("%r — не функция" % name, no)
