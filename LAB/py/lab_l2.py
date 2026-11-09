"""lab_l2.py — оракул WALL v1/v2 (SPEC/11): исходник .wall -> текст BRICK v2.

Вход:  текст программы на языке WALL (str, ASCII).
Выход: compile_wall(text) -> str — текст .b2 (BRICK v2), детерминированный
       (R8): один вход — один выход; канон эмиттера — SPEC/11 + lab_l2_gen.
Ошибки: WallError(сообщение, номер_строки) — номер с 1.
Функция: эталонный компилятор слоя L2 (фронт: разбор строк/утверждений +
         семантика имён); два независимых свидетеля (оракул на Python
         здесь, wall.exe на BRICK v2) обязаны совпадать.
WALL v2 (E6.4c): массивы var a[n] (значение имени — адрес нулевого
         элемента), индексация qword e[i] (чтение/запись, цепочки),
         умножение/деление/остаток (* / %), break/continue, цепочки
         условий && и || (short-circuit). Программа без v2-конструкций
         компилируется байт-в-байт как v1 (заголовок «WALL v1»).
Состав: lab_l2_err.py (WallError), lab_l2_lex.py (лексер+выражения),
       lab_l2.py (этот файл: parse), lab_l2_gen.py (бэк-эмиттер),
       lab_l2_lay.py (раскладка кадров).
"""
import re

from lab_l2_err import WallError          # noqa: F401 — реэкспорт для батареи
import lab_l2_gen
from lab_l2_lex import MAXNUM, MUL_OPS, P, _array_size, _lex, _name_ok, \
    last_line

MAXEXT = 8
MAXENAME = 31          # имя ext: слот hint = 2 + 31 + 1 (SPEC/11 п.6)


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
            "nlines": nlines, "v2": False}

    def v2on(*_a):
        prog["v2"] = True

    names = {}
    cur = None
    stack = []
    seen_func = False
    wdepth = [0]                               # v2: глубина вложенности while

    def body():
        kind, ref = stack[-1]
        if kind == "func":
            return ref
        if kind == "else":
            return ref[3]
        return ref[2]              # if -> then-ветка, while -> тело

    def locnames():
        return [n for n, _s in cur["locals"]]

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
                size = _array_size(p, no)
                p.at_end()
                if name in names:
                    raise WallError("повторное имя %r" % name, no)
                if size is None:
                    names[name] = "var"
                    prog["globals"].append((name, 1, no))
                else:
                    names[name] = "arr"
                    v2on()
                    prog["globals"].append((name, size, no))
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
                   "locals": [], "body": []}    # locals: [(имя, размер)]
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
            if kind == "while":
                wdepth[0] -= 1
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
            size = _array_size(p, no)
            p.at_end()
            if name in locnames() or name in cur["params"]:
                raise WallError("повторное локальное имя %r" % name, no)
            if name in names:
                raise WallError("локаль %r конфликтует с глобальным" % name,
                                no)
            if size is None:
                cur["locals"].append((name, 1))
            else:
                v2on()
                cur["locals"].append((name, size))
            body().append(("lvar", name, size or 1, no))
            continue
        if kwk == "id" and kwv == "break":
            p.pop()
            p.at_end()
            if wdepth[0] == 0:
                raise WallError("break вне цикла while", no)
            v2on()
            body().append(("break", no))
            continue
        if kwk == "id" and kwv == "continue":
            p.pop()
            p.at_end()
            if wdepth[0] == 0:
                raise WallError("continue вне цикла while", no)
            v2on()
            body().append(("continue", no))
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
            if len(c) > 1 or len(c[0]) > 1:
                v2on()
            node = ["if", c, [], [], no]
            body().append(node)
            stack.append(("if", node))
            continue
        if kwk == "id" and kwv == "while":
            p.pop()
            c = p.cond()
            p.at_end()
            if len(c) > 1 or len(c[0]) > 1:
                v2on()
            node = ["while", c, [], no]
            body().append(node)
            stack.append(("while", node))
            wdepth[0] += 1
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
            if p.peek() == ("sym", "["):       # v2: a[i]... = значение
                e = ("name", name, no)
                while p.peek() == ("sym", "["):
                    p.pop()
                    ix = p.expr()
                    p.want("sym", "]")
                    e = ("index", e, ix, no)
                p.want("sym", "=")
                val = p.expr()
                p.at_end()
                kind = names.get(name)
                if kind == "str":
                    raise WallError("строка %r неизменяема (только setb)"
                                    % name, no)
                if kind in ("func", "ext"):
                    raise WallError("%r — не переменная" % name, no)
                if kind is None and name not in locnames() and \
                        name not in cur["params"]:
                    raise WallError("неизвестное имя %r" % name, no)
                body().append(("astore", e, val, no))
                continue
            p.want("sym", "=")
            e = p.expr()
            p.at_end()
            body().append(("assign", name, e, no))
            continue
        raise WallError("не разобрано: %r" % (toks[0][1],), no)

    def _v2_expr(e):
        t = e[0]
        if t == "bin":
            if e[1] in MUL_OPS:
                v2on()
            _v2_expr(e[2])
            _v2_expr(e[3])
        elif t == "neg":
            _v2_expr(e[1])
        elif t == "getb":
            _v2_expr(e[1])
            _v2_expr(e[2])
        elif t == "index":
            v2on()
            _v2_expr(e[1])
            _v2_expr(e[2])
        elif t == "call":
            for a in e[2]:
                _v2_expr(a)

    def _v2_cond(c):
        for disj in c:
            for cmp in disj:
                _v2_expr(cmp[1])
                _v2_expr(cmp[2])

    for fn in prog["funcs"]:
        for st in _walk(fn["body"]):
            if st[0] == "assign":
                _v2_expr(st[2])
            elif st[0] == "return" and st[1] is not None:
                _v2_expr(st[1])
            elif st[0] == "astore":
                _v2_expr(st[1])
                _v2_expr(st[2])
            elif st[0] == "call":
                for a in st[2]:
                    _v2_expr(a)
            elif st[0] == "setb":
                for e in st[1:4]:
                    _v2_expr(e)
            elif st[0] in ("if", "while"):
                _v2_cond(st[1])
    if cur is not None or stack:
        raise WallError("незакрытый блок (не хватает end)", last_line(lines))
    mains = [f for f in prog["funcs"] if f["name"] == "main"]
    if len(mains) != 1:
        raise WallError("нужна ровно одна func main", last_line(lines))
    if mains[0]["params"]:
        raise WallError("main не должна иметь параметров", mains[0]["line"])
    return prog, names, srcmap


def _walk(body):
    """обход утверждений (в т.ч. вложенных if/while) — для флага v2."""
    for st in body:
        yield st
        if st[0] == "if":
            yield from _walk(st[2])
            yield from _walk(st[3])
        elif st[0] == "while":
            yield from _walk(st[2])


def compile_wall(text):
    """текст WALL v1/v2 -> текст .b2 (BRICK v2). Главный вход оракула."""
    prog, names, srcmap = parse(text)
    return lab_l2_gen.Gen(prog, names, srcmap).run()
