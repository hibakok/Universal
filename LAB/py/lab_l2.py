"""lab_l2.py — оракул WALL v1 (SPEC/11): исходник .wall -> текст BRICK v2.

Вход:  текст программы на языке WALL v1 (str, ASCII).
Выход: compile_wall(text) -> str — текст .b2 (BRICK v2), детерминированный
       (R8): один вход — один выход; канон эмиттера — SPEC/11 + lab_l2_gen.
Ошибки: WallError(сообщение, номер_строки) — номер с 1.
Функция: эталонный компилятор слоя L2 (фронт: лексер + разбор + семантика
         имён); бэкенд — lab_l2_gen.py. Два независимых свидетеля (оракул
         на Python здесь, wall.exe на BRICK v2 в E6.4b) обязаны совпадать.
Состав: lab_l2_err.py (WallError), lab_l2.py (фронт), lab_l2_gen.py (бэк).
"""
import re

from lab_l2_err import WallError          # noqa: F401 — реэкспорт для батареи
import lab_l2_gen
CMP_OPS = ("==", "!=", "<=", ">=", "<", ">")
ADD_OPS = ("+", "-", "|", "^")
MUL_OPS = ("&", "<<", ">>")
MAXNUM = 2147483647
MAXEXT = 8
MAXSTR = 512
MAXNAME = 63
MAXENAME = 31          # имя ext: слот hint = 2 + 31 + 1 (SPEC/11 п.6)
_SYM2 = ("==", "!=", "<=", ">=", "<<", ">>")
_ESC = {"n": 0x0A, "r": 0x0D, "t": 0x09, "0": 0x00, "\\": 0x5C, "'": 0x27}


# ---------------------------------------------------------------- лексер
def _lex(text):
    """текст -> [(номер, [токен...], исходный-текст-без-комментария)].

    Разбиение строк — как у enc (SPEC/09): LF, CRLF и одиночный CR.
    Токен: ('id'|'num'|'sym', значение) или ('str', байты). Комментарий —
    от ';' до конца строки (внутри '...' не считается). Нумерация с 1."""
    out = []
    for no, raw in enumerate(re.split(r"\r\n|\r|\n", text), 1):
        toks, i, n = [], 0, len(raw)
        while i < n:
            c = raw[i]
            if c in " \t\r":
                i += 1
            elif c == ";":
                break
            elif c == "'":
                j, bs = i + 1, bytearray()
                while True:
                    if j >= n:
                        raise WallError("незакрытая строка", no)
                    ch = raw[j]
                    if ch == "'":
                        break
                    if ch == "\\":
                        if j + 1 >= n:
                            raise WallError("незакрытая строка", no)
                        if raw[j + 1] not in _ESC:
                            raise WallError("неизвестный экран \\%s"
                                            % raw[j + 1], no)
                        bs.append(_ESC[raw[j + 1]])
                        j += 2
                        continue
                    if not (0x20 <= ord(ch) <= 0x7E):
                        raise WallError("символ вне ASCII в строке", no)
                    bs.append(ord(ch))
                    j += 1
                if len(bs) > MAXSTR:
                    raise WallError("строка длиннее %d байт" % MAXSTR, no)
                toks.append(("str", bytes(bs)))
                i = j + 1
            elif c.isdigit():
                j = i
                while j < n and raw[j].isdigit():
                    j += 1
                v = int(raw[i:j])
                if v > MAXNUM:
                    raise WallError("число больше %d" % MAXNUM, no)
                toks.append(("num", v))
                i = j
            elif c.isalpha() or c == "_":
                j = i
                while j < n and (raw[j].isalnum() or raw[j] == "_"):
                    j += 1
                toks.append(("id", raw[i:j]))
                i = j
            elif raw[i:i + 2] in _SYM2:
                toks.append(("sym", raw[i:i + 2]))
                i += 2
            elif c in "()=,-+<>|&^!":
                toks.append(("sym", c))
                i += 1
            else:
                raise WallError("недопустимый символ %r" % c, no)
        out.append((no, toks, raw[:i].strip()))
    return out


# ---------------------------------------------------------------- разбор
class P:
    """Разбор выражений/условий из токенов одной строки."""

    def __init__(self, no, toks):
        self.no = no
        self.t = toks
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def pop(self):
        tok = self.peek()
        self.i += 1
        return tok

    def want(self, kind, val=None):
        k, v = self.pop()
        if k != kind or (val is not None and v != val):
            raise WallError("ожидалось %s %r, получено %r"
                            % (kind, val, v), self.no)
        return v

    def at_end(self):
        if self.i < len(self.t):
            raise WallError("лишние символы в конце строки: %r"
                            % self.t[self.i][1], self.no)

    def expr(self):
        e = self.mul()
        while True:
            k, v = self.peek()
            if k == "sym" and v in ADD_OPS:
                self.pop()
                e = ("bin", v, e, self.mul())
            else:
                return e

    def mul(self):
        e = self.unary()
        while True:
            k, v = self.peek()
            if k == "sym" and v in MUL_OPS:
                self.pop()
                e = ("bin", v, e, self.unary())
            else:
                return e

    def unary(self):
        if self.peek() == ("sym", "-"):
            self.pop()
            return ("neg", self.unary())
        return self.prim()

    def prim(self):
        k, v = self.pop()
        if (k, v) == ("sym", "("):
            e = self.expr()
            self.want("sym", ")")
            return e
        if k == "num":
            return ("num", v)
        if k == "id":
            if v == "getb":
                self.want("sym", "(")
                b = self.expr()
                self.want("sym", ",")
                ix = self.expr()
                self.want("sym", ")")
                return ("getb", b, ix, self.no)
            if v == "len":
                self.want("sym", "(")
                name = self.want("id")
                self.want("sym", ")")
                return ("len", name, self.no)
            if self.peek() == ("sym", "("):
                self.pop()
                args = self.args()
                return ("call", v, args, self.no)
            return ("name", v, self.no)
        if (k, v) == ("sym", "&"):
            name = self.want("id")
            return ("addr", name, self.no)
        raise WallError("ожидалось выражение, получено %r" % (v,), self.no)

    def args(self):
        """аргументы вызова: уже после '('; до ')' включительно."""
        out = []
        if self.peek() != ("sym", ")"):
            out.append(self.expr())
            while self.peek() == ("sym", ","):
                self.pop()
                out.append(self.expr())
        self.want("sym", ")")
        return out

    def cond(self):
        l = self.expr()
        k, v = self.pop()
        if k != "sym" or v not in CMP_OPS:
            raise WallError("в условии ожидается сравнение %s"
                            % "/".join(CMP_OPS), self.no)
        return (v, l, self.expr())


def _name_ok(name, no, allow_upper=False):
    if len(name) > MAXNAME:
        raise WallError("имя длиннее %d байт" % MAXNAME, no)
    if not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", name):
        raise WallError("плохое имя %r" % name, no)
    if not allow_upper and name.lower() != name:
        raise WallError("имя %r должно быть строчным (кроме ext)" % name, no)
    if name.startswith("_"):
        raise WallError("имя %r не может начинаться с '_'" % name, no)


def last_line(lines):
    """номер последней непустой строки (для программных ошибок)"""
    for no, _t, txt in reversed(lines):
        if txt:
            return no
    return lines[-1][0] if lines else 0


def parse(text):
    """текст -> (программа-AST, таблица имён, карта строк исходника)."""
    lines = _lex(text)
    if len(text.encode("latin1", "replace")) > 128 * 1024:
        raise WallError("исходник больше 128 КиБ", 0)
    srcmap = {no: txt for no, _t, txt in lines}
    # число строк: разбиение + без пустого хвостового элемента (SPEC/11 п.3)
    nlines = len(lines)
    if text.endswith("\n") or text.endswith("\r"):
        nlines -= 1
    if not text:
        nlines = 0
    prog = {"globals": [], "strs": [], "exts": [], "funcs": [],
            "nlines": nlines}
    names = {}
    cur = None
    stack = []
    seen_func = False

    def body():
        kind, ref = stack[-1]
        if kind == "func":
            return ref
        if kind == "else":
            return ref[3]
        return ref[2]              # if -> then-ветка, while -> тело

    for no, toks, _txt in lines:
        if not toks:
            continue
        k, v = toks[0]
        # ---- режим объявлений (только до первой func) ----
        if cur is None and not stack and not seen_func and \
                not (k == "id" and v == "func"):
            p = P(no, toks)
            kw = p.want("id")
            if kw == "var":
                name = p.want("id")
                _name_ok(name, no)
                p.at_end()
                if name in names:
                    raise WallError("повторное имя %r" % name, no)
                names[name] = "var"
                prog["globals"].append((name, no))
            elif kw == "str":
                name = p.want("id")
                _name_ok(name, no)
                p.want("sym", "=")
                ek, ev = p.pop()
                if ek != "str":
                    raise WallError("после = ожидается 'текст'", no)
                p.at_end()
                if name in names:
                    raise WallError("повторное имя %r" % name, no)
                names[name] = "str"
                prog["strs"].append((name, ev, no))
            elif kw == "ext":
                name = p.want("id")
                _name_ok(name, no, allow_upper=True)
                if len(name) > MAXENAME:
                    raise WallError("имя ext длиннее %d байт" % MAXENAME, no)
                p.at_end()
                if name.lower() in {e.lower() for e in prog["exts"]} or \
                        name.lower() in names:
                    raise WallError("повторное имя %r" % name, no)
                names[name] = "ext"
                prog["exts"].append(name)
                if len(prog["exts"]) > MAXEXT:
                    raise WallError("больше %d ext" % MAXEXT, no)
            else:
                raise WallError("объявление %r после func недопустимо (v1)"
                                % kw, no)
            continue
        # ---- заголовок функции ----
        if cur is None:
            p = P(no, toks)
            p.want("id", "func")
            name = p.want("id")
            _name_ok(name, no)
            params = []
            if p.peek() == ("sym", "("):
                p.pop()
                if p.peek() != ("sym", ")"):
                    params.append(p.want("id"))
                    while p.peek() == ("sym", ","):
                        p.pop()
                        params.append(p.want("id"))
                p.want("sym", ")")
            p.at_end()
            if len(params) > 4:
                raise WallError("больше 4 параметров", no)
            for pn in params:
                _name_ok(pn, no)
                if pn in names:
                    raise WallError("параметр %r конфликтует с глобальным"
                                    % pn, no)
            if len(set(params)) != len(params):
                raise WallError("повторное имя параметра", no)
            if name in names:
                raise WallError("повторное имя %r" % name, no)
            names[name] = "func"
            seen_func = True
            cur = {"name": name, "params": params, "line": no,
                   "locals": [], "body": []}
            stack = [("func", cur["body"])]
            continue
        # ---- утверждения тела ----
        p = P(no, toks)
        kwk, kwv = p.peek()
        if kwk == "id" and kwv == "end":
            p.pop()
            p.at_end()
            if not stack:
                raise WallError("лишний end", no)
            kind, _b = stack.pop()
            if kind == "func":
                prog["funcs"].append(cur)
                cur = None
            continue
        if kwk == "id" and kwv == "else":
            p.pop()
            p.at_end()
            if not stack or stack[-1][0] != "if":
                raise WallError("else вне if", no)
            stack.append(("else", stack.pop()[1]))
            continue
        if kwk == "id" and kwv == "var":
            p.pop()
            name = p.want("id")
            _name_ok(name, no)
            p.at_end()
            if name in cur["locals"] or name in cur["params"]:
                raise WallError("повторное локальное имя %r" % name, no)
            if name in names:
                raise WallError("локаль %r конфликтует с глобальным" % name,
                                no)
            cur["locals"].append(name)
            body().append(("var", name, no))
            continue
        if kwk == "id" and kwv == "return":
            p.pop()
            e = None
            if p.i < len(p.t):
                e = p.expr()
            p.at_end()
            body().append(("return", e, no))
            continue
        if kwk == "id" and kwv == "if":
            p.pop()
            c = p.cond()
            p.at_end()
            node = ["if", c, [], [], no]
            body().append(node)
            stack.append(("if", node))
            continue
        if kwk == "id" and kwv == "while":
            p.pop()
            c = p.cond()
            p.at_end()
            node = ["while", c, [], no]
            body().append(node)
            stack.append(("while", node))
            continue
        if kwk == "id" and kwv == "setb":
            p.pop()
            p.want("sym", "(")
            b = p.expr()
            p.want("sym", ",")
            ix = p.expr()
            p.want("sym", ",")
            val = p.expr()
            p.want("sym", ")")
            p.at_end()
            body().append(("setb", b, ix, val, no))
            continue
        if kwk == "id":
            name = p.pop()[1]
            if p.peek() == ("sym", "("):
                p.pop()
                args = p.args()
                p.at_end()
                body().append(("call", name, args, no))
                continue
            p.want("sym", "=")
            e = p.expr()
            p.at_end()
            body().append(("assign", name, e, no))
            continue
        raise WallError("не разобрано: %r" % (toks[0][1],), no)
    if cur is not None or stack:
        raise WallError("незакрытый блок (не хватает end)", last_line(lines))
    mains = [f for f in prog["funcs"] if f["name"] == "main"]
    if len(mains) != 1:
        raise WallError("нужна ровно одна func main", last_line(lines))
    if mains[0]["params"]:
        raise WallError("main не должна иметь параметров", mains[0]["line"])
    return prog, names, srcmap


def compile_wall(text):
    """текст WALL v1 -> текст .b2 (BRICK v2). Главный вход оракула."""
    prog, names, srcmap = parse(text)
    return lab_l2_gen.Gen(prog, names, srcmap).run()
