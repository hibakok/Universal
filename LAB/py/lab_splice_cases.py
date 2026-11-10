"""lab_splice_cases.py — эталоны SPLICE v1 (SPEC/10).

CASES: (имя, корень, host, want) — нормальные склейки; want выписан
ВРУЧНУЮ (независимо от оракула — якорь, как lab_enc_cases.CASES).
ERRORS: (имя, корень, host, код, msg) — msg = хвост строки
«U-L1-SPLICE ERR=...» (без CRLF).
"""
import lab_splice


def _chain(depth):
    """Цепочка depth файлов f0..f{depth-1}: «L{i+1}» + include следующего."""
    host = {}
    for i in range(depth):
        body = ("L%d\n" % (i + 1)).encode()
        if i + 1 < depth:
            body += b"!include f%d.b2\n" % (i + 1)
        host["f%d.b2" % i] = body
    return host


CASES = [
    ("одиночный файл без включений",
     "r.b2", {b"r.b2": b"H 90\n:label\nDB 41\n"},
     b"H 90\n:label\nDB 41\n"),
    ("корень + одно включение",
     "r.b2", {b"r.b2": b"; head\n!include p.b2\n; tail\n",
              b"p.b2": b"H 48 90\n"},
     b"; head\nH 48 90\n; tail\n"),
    ("три включения; третье — пустой файл",
     "d/r.b2", {b"d/r.b2": b"!include p1.b2\nX\n!include p2.b2\n"
                            b"!include p3.b2\n",
                b"d/p1.b2": b"A\n", b"d/p2.b2": b"B\n", b"d/p3.b2": b""},
     b"A\nX\nB\n"),
    ("вложенное включение (каталог включающего)",
     "r.b2", {b"r.b2": b"!include sub/a.b2\nEND\n",
              b"sub/a.b2": b"A1\n!include b.b2\nA2\n",
              b"sub/b.b2": b"B1\nB2\n"},
     b"A1\nB1\nB2\nA2\nEND\n"),
    ("концы строк CRLF/CR/без-LF",
     "r.b2", {b"r.b2": b"one\r\ntwo\rthree\nfour"},
     b"one\ntwo\nthree\nfour\n"),
    ("повторное включение = повторная вставка",
     "r.b2", {b"r.b2": b"!include p.b2\n!include p.b2\n",
              b"p.b2": b"X\n"},
     b"X\nX\n"),
    ("директива в последней строке без терминатора",
     "r.b2", {b"r.b2": b"A\n!include p.b2", b"p.b2": b"B\n"},
     b"A\nB\n"),
    ("пустой корень -> пустой выход",
     "r.b2", {b"r.b2": b""}, b""),
    ("пробел перед ! — обычная строка (проходит)",
     "r.b2", {b"r.b2": b"  !include p.b2\nM ret\n"},
     b"  !include p.b2\nM ret\n"),
    ("! не в колонке 0 и комментарии",
     "r.b2", {b"r.b2": b"; !include x\nM ret\nH 90 ; ok\n"},
     b"; !include x\nM ret\nH 90 ; ok\n"),
    ("обратные слэши и регистр имени",
     "DIR1\\Root.B2", {b"dir1/root.b2": b"!include Part.B2\n",
                       b"dir1/part.b2": b"OK\n"},
     b"OK\n"),
    ("глубина 7 включений (предел)",
     "f0.b2", _chain(8), b"L1\nL2\nL3\nL4\nL5\nL6\nL7\nL8\n"),
    ("пустые строки вокруг включений",
     "r.b2", {b"r.b2": b"\n!include p.b2\n\n!include p.b2\n\n",
              b"p.b2": b"\n"},
     b"\n\n\n\n\n"),
    ("сентинел NUL обрезает файл",
     "r.b2", {b"r.b2": b"A\n\x00B\n!bogus\n"}, b"A\n"),
]

ERRORS = [
    ("плохой префикс директивы", "r.b2",
     {b"r.b2": b"!inc p.b2\n"}, 6, "FORMAT AT=0001"),
    ("голое !include", "r.b2",
     {b"r.b2": b"!include\n"}, 6, "FORMAT AT=0001"),
    ("пустой путь (пробел после префикса)", "r.b2",
     {b"r.b2": b"!include \n"}, 6, "FORMAT AT=0001"),
    ("!includex — не пробел в 9-й позиции", "r.b2",
     {b"r.b2": b"!includex y\n"}, 6, "FORMAT AT=0001"),
    ("путь из пробела не открывается", "r.b2",
     {b"r.b2": b"!include  p.b2\n"}, 4, "OPEN SRC"),
    ("включение отсутствует", "r.b2",
     {b"r.b2": b"!include nope.b2\n"}, 4, "OPEN SRC"),
    ("корень отсутствует", "no.b2", {}, 4, "OPEN SRC"),
    ("глубина 8 включений — DEPTH", "f0.b2", _chain(9), 11, "DEPTH"),
    ("цикл a -> a — DEPTH", "a.b2",
     {b"a.b2": b"!include a.b2\n"}, 11, "DEPTH"),
    ("включение >= 256 КиБ — BIG SRC", "r.b2",
     {b"r.b2": b"!include big.b2\n", b"big.b2": b"A" * 0x40000},
     7, "BIG SRC"),
    ("выход > 256 КиБ — BIG OUT", "r.b2",
     {b"r.b2": b"!include p1.b2\n!include p2.b2\n",
      b"p1.b2": b"X" * 0x100, b"p2.b2": b"Y" * 0x3FFFD},
     10, "BIG OUT"),
    ("полное имя длиннее 127 — LONG NAME", "d/r.b2",
     {b"d/r.b2": b"!include " + b"n" * 130 + b"\n"}, 3, "LONG NAME"),
    ("номер строки сквозной (ошибка во 2-м файле)", "r.b2",
     {b"r.b2": b"A\nB\n!include p.b2\n", b"p.b2": b"C\n!bogus\n"},
     6, "FORMAT AT=0005"),
]


def big_case(nbytes=24000):
    """Большой случай: корень + часть из n байт строк «H 90 ; x»."""
    part, root = bytearray(), bytearray()
    i = 0
    while len(part) < nbytes:
        part += b"H 90 ; line %d\n" % i
        i += 1
    root += b"; big\n!include p.b2\n; end\n"
    want = b"; big\n" + bytes(part) + b"; end\n"
    return "r.b2", {b"r.b2": bytes(root), b"p.b2": bytes(part)}, want


def check_oracle():
    """Самопроверка якорей оракулом (для батареи). Возврат — список провалов."""
    bad = []
    for name, root, host, want in CASES:
        try:
            got = lab_splice.splice(root, host)
            if got != want:
                bad.append("%s: want %r got %r" % (name, want[:30],
                                                    got[:30]))
        except lab_splice.SpliceError as e:
            bad.append("%s: неожиданная ошибка %s" % (name, e))
    for name, root, host, code, msg in ERRORS:
        try:
            lab_splice.splice(root, host)
            bad.append("%s: ошибка не возникла" % name)
        except lab_splice.SpliceError as e:
            if e.code != code or str(e) != msg:
                bad.append("%s: want %d/%s got %d/%s"
                           % (name, code, msg, e.code, e))
    return bad
