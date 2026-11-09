"""lab_l2_gen.py — бэкенд оракула WALL v1/v2 (SPEC/11): AST -> текст BRICK v2.

Вход:  программа (AST из lab_l2.parse), таблица имён, карта строк исходника.
Выход: текст .b2 (BRICK v2) — детерминированный; правила раскладки слотов,
       кадров и эмиттеров — SPEC/11 (это канон: wall.exe обязан повторять
       этот выход байт-в-байт).
Ошибки: WallError(сообщение, номер_строки) — номер с 1.
WALL v2 (E6.4c): массивы (имя — адрес a[0]), qword-индексация e[i]/
       e[i] = v, * / %, len(массив), break/continue, guard-цепочки
       && / ||. Программы без v2-конструкций дают байт-в-байт выход v1
       (заголовок «WALL v1»).
Функция: кирпич кодогенерации слоя L2; вызывается lab_l2.compile_wall().
         Раскладка кадров — lab_l2_lay.py (разрез E6.4c).
"""
from lab_l2_err import WallError            # noqa: F401  (реэкспорт)
from lab_l2_lay import Layout, _align16, _hex

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


class Gen:
    """Эмиттер: программа -> список строк .b2 (SPEC/11 п.8 — канон)."""

    def __init__(self, prog, names, srcmap):
        self.prog, self.names, self.src = prog, names, srcmap
        self.fp = {f["name"]: len(f["params"]) for f in prog["funcs"]}
        self.gs = {n: s for n, s, _no in prog["globals"]}
        self.out = []
        self.k = 0            # счётчик меток _if/_w
        self.wstack = []      # v2: стек k объемлющих while (break/continue)
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
        ver = "v2" if p["v2"] else "v1"
        self.raw("; UNIVERSAL / WALL %s / сгенерировано компилятором WALL"
                 " (SPEC/11)" % ver)
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
            for name, size, no in p["globals"]:
                self.lbl(name)
                self.raw("DZ %s ; %s" % (_hex(8 * size), self.src[no]))
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
        lay = Layout(fn, self.names, self.fp, self.gs)
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
            if t == "lvar":
                continue
            if t == "assign":
                src = self.src[st[3]]
                self.expr(st[2], 1, lay, src)
                name = st[1]
                if name in lay.base:
                    if lay.sizes[name] > 1:
                        raise WallError("массив %r нельзя присвоить целиком"
                                        % name, st[3])
                    self.m(src, "mov [rbp-%s], r10" % _hex(lay.local(name)))
                elif self.names.get(name) == "var":
                    self.m(src, "mov [rip+$%s], r10" % name)
                elif self.names.get(name) == "arr":
                    raise WallError("массив %r нельзя присвоить целиком"
                                    % name, st[3])
                elif self.names.get(name) == "str":
                    raise WallError("строка %r неизменяема (только setb)"
                                    % name, st[3])
                elif name in self.names:
                    raise WallError("%r — не переменная" % name, st[3])
                else:
                    raise WallError("неизвестное имя %r" % name, st[3])
            elif t == "astore":            # v2: e[i] = v (S-стейдинг)
                src = self.src[st[3]]
                self._astore(st, lay, src)
            elif t == "break":             # v2
                self.m(self.src[st[1]], "jmp $_w%de" % self.wstack[-1])
            elif t == "continue":          # v2
                self.m(self.src[st[1]], "jmp $_w%d" % self.wstack[-1])
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

    def _astore(self, st, lay, src):
        """v2: e[i] = v — адрес базы в S0, индекс в S1, значение в S2.
        st = ("astore", ("index", база, индекс), значение, строка)."""
        self.expr(st[1][1], 1, lay, src)          # база (адрес)
        self.m(src, "mov [rbp-%s], r10" % _hex(lay.s(0)))
        self.expr(st[1][2], 1, lay, src)          # индекс
        self.m(src, "mov [rbp-%s], r10" % _hex(lay.s(1)))
        self.expr(st[2], 1, lay, src)             # значение
        self.m(src, "mov [rbp-%s], r10" % _hex(lay.s(2)))
        self.m(src, "mov r10, [rbp-%s]" % _hex(lay.s(0)))
        self.m(src, "mov r11, [rbp-%s]" % _hex(lay.s(1)))
        self.m(src, "shl r11, 3")
        self.m(src, "add r10, r11")
        self.m(src, "mov r11, [rbp-%s]" % _hex(lay.s(2)))
        self.m(src, "mov [r10], r11")

    def _cond_one(self, c, lay, src):
        self.expr(c[1], 2, lay, src)
        self.m(src, "mov [rbp-%s], r10" % _hex(lay.t(1)))
        self.expr(c[2], 2, lay, src)
        self.m(src, "mov r11, r10")
        self.m(src, "mov r10, [rbp-%s]" % _hex(lay.t(1)))
        self.m(src, "cmp r10, r11")

    def _guard(self, cond, lay, src, lfalse, pfx, k):
        """v2: guard-эми��сия условия — переход на lfalse при лжи.

        cond = [дизъюнкт...] (||), дизъюнкт = [сравнение...] (&&).
        Провал конъюнкта = провал дизъюнкта -> следующий дизъюнкт
        (метка _<pfx><k>d<i>) или lfalse; успех дизъюнкта -> тело
        (jmp _<pfx><k>t / fall-through последнего)."""
        m = len(cond)
        for i, disj in enumerate(cond, 1):
            lfail = "%s%dd%d" % (pfx, k, i + 1) if i < m else lfalse
            for c in disj:
                self._cond_one(c, lay, src)
                self.m(src, "%s $%s" % (JINV[c[0]], lfail))
            if i < m:
                self.m(src, "jmp $%s%dt" % (pfx, k))
                self.lbl("%s%dd%d" % (pfx, k, i + 1))
        if m > 1:
            self.lbl("%s%dt" % (pfx, k))

    def _if(self, st, lay, fn):
        cond, then, els, no = st[1], st[2], st[3], st[4]
        src = self.src[no]
        self.k += 1
        k = self.k
        if els:
            self._guard(cond, lay, src, "_if%d" % k, "_if", k)
            self._body(then, lay, fn)
            self.m(src, "jmp $_if%de" % k)
            self.lbl("_if%d" % k)
            self._body(els, lay, fn)
            self.lbl("_if%de" % k)
        else:
            self._guard(cond, lay, src, "_if%de" % k, "_if", k)
            self._body(then, lay, fn)
            self.lbl("_if%de" % k)

    def _while(self, st, lay, fn):
        cond, body, no = st[1], st[2], st[3]
        src = self.src[no]
        self.k += 1
        k = self.k
        self.lbl("_w%d" % k)
        self.wstack.append(k)
        self._guard(cond, lay, src, "_w%de" % k, "_w", k)
        self._body(body, lay, fn)
        self.m(src, "jmp $_w%d" % k)
        self.lbl("_w%de" % k)
        self.wstack.pop()

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
                off = lay.arrbase(name) if lay.sizes[name] > 1 \
                    else lay.local(name)
                self.m(src, "lea r10, [rbp-%s]" % _hex(off))
            elif self.names.get(name) in ("var", "str", "arr"):
                self.m(src, "lea r10, [rip+$%s]" % name)
            elif name in self.names:
                raise WallError("& не применимо к %r" % name, no)
            else:
                raise WallError("неизвестное имя %r" % name, no)
        elif t == "len":
            kind = self.names.get(e[1])
            if kind == "str":
                n = len(dict((n, b) for n, b, _ in self.prog["strs"])[e[1]])
            elif kind == "arr":            # v2: размер массива (компиляция)
                n = self.gs[e[1]]
            elif e[1] in lay.base and lay.sizes[e[1]] > 1:
                n = lay.sizes[e[1]]
            else:
                raise WallError("len применим только к str или массиву",
                                e[2])
            self.m(src, "mov r10, %s" % _hex(n))
        elif t == "bin":
            self.expr(e[2], d + 1, lay, src)
            self.m(src, "mov [rbp-%s], r10" % _hex(lay.t(d)))
            self.expr(e[3], d + 1, lay, src)
            self.m(src, "mov r11, r10")
            self.m(src, "mov r10, [rbp-%s]" % _hex(lay.t(d)))
            if e[1] in ALU:
                self.m(src, "%s r10, r11" % ALU[e[1]])
            elif e[1] == "*":              # v2
                self.m(src, "imul r10, r11")
            elif e[1] in ("/", "%"):       # v2: rax/rdx, cqo, idiv
                self.m(src, "mov rax, r10")
                self.m(src, "cqo")
                self.m(src, "idiv r11")
                self.m(src, "mov r10, r%s" % ("ax" if e[1] == "/"
                                              else "dx"))
            else:
                self.m(src, "mov rcx, r11")
                self.m(src, "%s r10, cl" % ("shl" if e[1] == "<<" else "shr"))
        elif t == "index":                 # v2: qword-загрузка e[i]
            if e[1][0] == "name" and self.names.get(e[1][1]) == "str":
                raise WallError("индексирование строки %r запрещено (getb)"
                                % e[1][1], e[1][2])
            self.expr(e[1], d + 1, lay, src)
            self.m(src, "mov [rbp-%s], r10" % _hex(lay.t(d)))
            self.expr(e[2], d + 1, lay, src)
            self.m(src, "shl r10, 3")
            self.m(src, "mov r11, r10")
            self.m(src, "mov r10, [rbp-%s]" % _hex(lay.t(d)))
            self.m(src, "add r10, r11")
            self.m(src, "mov r10, [r10]")
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
            if lay.sizes[name] > 1:        # v2: имя массива = адрес a[0]
                self.m(src, "lea r10, [rbp-%s]" % _hex(lay.arrbase(name)))
            else:
                self.m(src, "mov r10, [rbp-%s]" % _hex(lay.local(name)))
            return
        kind = self.names.get(name)
        if kind == "var":
            self.m(src, "mov r10, [rip+$%s]" % name)
        elif kind in ("str", "arr"):       # v2: глобальный массив — адрес
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
