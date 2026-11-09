"""lab_l2_lex.py — лексер и разбор выражений WALL v1/v2 (SPEC/11).

Вход:  текст программы (str) / токены одной строки.
Выход: _lex(text) -> [(номер, [токен...], исходный-текст-без-комментария)];
       класс P — разбор выражений/условий из токенов строки (приоритеты
       v2: аддитив > конъюнкция(&,<<,>>) > мультипликатив(*,/,%) > унарный;
       постфиксная qword-индексация e[i]; условия — цепочки || из &&).
Ошибки: WallError(сообщение, номер_строки) — номер с 1.
Функция: фронтальная половина оракула WALL; вызывается lab_l2.parse.
Состав оракула: lab_l2_err.py, lab_l2_lex.py, lab_l2.py, lab_l2_gen.py,
       lab_l2_lay.py (E6.4c — разрез по лимиту 500 строк).
"""
import re

from lab_l2_err import WallError

MAXNUM = 2147483647
MAXSTR = 512
MAXNAME = 63
MAXARR = 4096          # v2: элементов массива (локального и глобального)
CMP_OPS = ("==", "!=", "<=", ">=", "<", ">")
ADD_OPS = ("+", "-", "|", "^")
BAND_OPS = ("&", "<<", ">>")              # конъюнкция уровня (v1: мультипликатив)
MUL_OPS = ("*", "/", "%")                 # v2: верхний бинарный уровень
_SYM2 = ("==", "!=", "<=", ">=", "<<", ">>", "&&", "||")
_ESC = {"n": 0x0A, "r": 0x0D, "t": 0x09, "0": 0x00, "\\": 0x5C, "'": 0x27}


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
            elif c in "()=,-+<>|&^![]*/%":
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

    # v2: приоритеты аддитив > конъюнкция > мультипликатив > унарное
    def expr(self):
        e = self.band()
        while True:
            k, v = self.peek()
            if k == "sym" and v in ADD_OPS:
                self.pop()
                e = ("bin", v, e, self.band())
            else:
                return e

    def band(self):
        e = self.mul()
        while True:
            k, v = self.peek()
            if k == "sym" and v in BAND_OPS:
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
        return self.postfix()

    def postfix(self):
        e = self.prim()
        while self.peek() == ("sym", "["):        # v2: qword-индексация
            self.pop()
            ix = self.expr()
            self.want("sym", "]")
            e = ("index", e, ix, self.no)
        return e

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

    # v2: условие — цепочки || из цепочек && сравнений (short-circuit)
    def cond(self):
        disj = [self.conj()]
        while self.peek() == ("sym", "||"):
            self.pop()
            disj.append(self.conj())
        return disj

    def conj(self):
        out = [self.cmp()]
        while self.peek() == ("sym", "&&"):
            self.pop()
            out.append(self.cmp())
        return out

    def cmp(self):
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


def _array_size(p, no):
    """v2: [n] после имени var — размер массива (1..MAXARR).
    None — скобок нет (скаляр)."""
    if p.peek() != ("sym", "["):
        return None
    p.pop()
    k, v = p.pop()
    if k != "num":
        raise WallError("размер массива — десятичное число", no)
    p.want("sym", "]")
    if not 1 <= v <= MAXARR:
        raise WallError("размер массива 1..%d" % MAXARR, no)
    return v


def last_line(lines):
    """номер последней непустой строки (для программных ошибок)"""
    for no, _t, txt in reversed(lines):
        if txt:
            return no
    return lines[-1][0] if lines else 0


