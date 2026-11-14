"""lab_t_wallself.py — секция 12 батареи: самохостинг wall.wall (E6.4d).

Вход:  колбэки check/kpath/kfile/kernel_host из lab_verify.
Выход: проверки T-E6-49a/b/c/d (печать через check).
Функция: самохостинг E6.4d — KERNEL/L2-WALL/wall.wall (WALL v2, корень
         с разрезом SPEC/10: wall_self_c.wall — сервис, wall_self_n.wall
         — проход 0, wall_self_pe/pd/p1.wall — проход 1) компилируется
         wall.exe байт-в-байт как оракул спрямлённого текста (склейка —
         оракул splice); полный круг enc+brick+pegen даёт рабочий EXE;
         CLI-поведение == wall.exe байт-в-байт (stdout и коды возврата)
         на матрице путей.
         E6.4d-2/2: проход 0 (разбиение строк + полная лексика + карта
         текстов) — ошибки лексера дают ERR=FORMAT AT=XXXX (код 6)
         с номерами строк == wall.exe == оракул _lex.
         E6.4d-2/3: проход 1 (читатели карты, диспетчер + kwtab,
         объявления var/str/ext + ntab/varr/sarr/earr, пост-проверка
         main) — ошибки разбора == оракул parse на классе источников
         без обработки func; источники, которым нужен func/статы (первая
         строка-func раньше точки решения), пропускаются — до шагов
         E6.4d-2/4+ каркас останавливается на первом func с ERR=FORMAT
         (задокументированное отличие; VERIFY-E6D.md).
         Границы BIG SRC: 131073 (отказ) и 131072 (оба инструмента
         дают нет main); буфер входа, карта текстов и таблицы прохода 1
         — GlobalAlloc (куча эмулятора 8 МиБ).
"""
import os
import tempfile

import lab_l2
import lab_l2_cases
import lab_l2_cases2
import lab_l2_err
import lab_l2_lex
import lab_l2_prog
import lab_run
import lab_splice
import lab_win

USAGE = b"U-L2-WALL CMDS: WALL <SRC.WALL> <OUT.B2>\r\n"

# «Все виды объявлений» (E6.4d-2/3): ext (заглавные ок), литерал со
# всеми экранами, массив, скаляр — разбор проходит, «нет main» (AT=0004)
KITCHEN = (b"ext GetStdHandle\n"
           b"str s = 'a\\nb\\r\\t\\0\\\\\\'z'\n"
           b"var a[3]\n"
           b"var g\n")


def _cases():
    """Матрица CLI-путей: (имя, args, host, argv0)."""
    # 131072 = граница чтения BIG SRC (131073 — отказ): 1 + 131064 + 1
    # + 6 байт; строки: гигантский комментарий, var g, пустая запись
    src_ok = b"var g\n"
    big_ok = b";" + b"x" * 131064 + b"\n" + b"var g\n"
    return [
        ("справка (0 аргументов)", [], {}, None),
        ("справка (1 аргумент)", ["t.wall"], {}, None),
        ("вход отсутствует", ["t.wall", "t.b2"], {}, None),
        ("длинное имя arg1", ["x" * 128, "t.b2"], {}, None),
        ("длинное имя arg2", ["t.wall", "x" * 128], {}, None),
        ("BIG SRC (>131073)", ["t.wall", "t.b2"],
         {"t.wall": b"\n" * 200000}, None),
        ("BIG SRC (граница 131073)", ["t.wall", "t.b2"],
         {"t.wall": b"\n" * 131073}, None),
        ("граница 131072: оба дают нет main", ["t.wall", "t.b2"],
         {"t.wall": big_ok}, None),
        ("нет main: объявления (var)", ["t.wall", "t.b2"],
         {"t.wall": src_ok}, None),
        ("нет main: все виды объявлений", ["t.wall", "t.b2"],
         {"t.wall": KITCHEN}, None),
        ("лексер: CRLF+CR, ошибка в строке 3", ["t.wall", "t.b2"],
         {"t.wall": b"func main\r\nvar i\r@ bad\r"}, None),
        ("лексер: неизвестный экран", ["t.wall", "t.b2"],
         {"t.wall": b"str s = 'a\\qb'\nfunc main\nend\n"}, None),
        ("лексер: незакрытая строка", ["t.wall", "t.b2"],
         {"t.wall": b"str s = 'abc\nfunc main\nend\n"}, None),
        ("лексер: число больше 31 бита", ["t.wall", "t.b2"],
         {"t.wall": b"func main\nvar i\ni = 99999999999\nend\n"}, None),
        ("лексер: не-ASCII имя (UTF-8)", ["t.wall", "t.b2"],
         {"t.wall": "func main\nvar \u0430\nend\n".encode("utf-8")}, None),
        ("argv0 с пробелом без кавычек", ["a.wall", "b.b2"], {}, "x y.exe"),
        ("мусор после кавычек argv0", ["t.wall", "t.b2"], {},
         '"C:\\UNI\\wall.exe"junk'),
        ("табуляция-разделитель", ["a.wall\tb.b2"], {}, None),
        ("хвостовые разделители", ["t.wall "], {"t.wall": src_ok}, None),
    ]


def _corpus():
    """(имя, текст) — пул для сверки прохода 0+1 каркаса с оракулом.

    Только ASCII-источники: оракул _lex работает со str (кириллица —
    имя), инструменты — с байтами (отказ на лексе); не-ASCII случаи
    сверяются инструмент-в-инструмент в матрице T-E6-49c. Решение о
    доступности (класс без обработки func — см. _expect_line) принима-
    ется в run(); здесь только пул."""
    out = []
    for n, s, _w in lab_l2_cases.CASES_FULL:
        out.append(("v1 " + n, s))
    for n, s, _f in lab_l2_cases.CASES_FRAG:
        out.append(("v1ф " + n, s))
    for n, s, _w in lab_l2_cases2.CASES_FULL2:
        out.append(("v2 " + n, s))
    for n, s, _f in lab_l2_cases2.CASES_FRAG2:
        out.append(("v2ф " + n, s))
    for n, s, _l in lab_l2_prog.ERRORS:
        out.append(("E1 " + n, s))
    for n, s, _l in lab_l2_prog.ERRORS2:
        out.append(("E2 " + n, s))
    out += [
        ("микро: CR-разбиение, ошибка в строке 3", "func main\rvar i\r@ bad\r"),
        ("микро: без хвостового перевода", "func main\nend"),
        ("микро: только комментарий", "; nothing"),
        ("микро: пустой файл", ""),
        ("микро: литерал 512 байт",
         "str s = '" + "x" * 512 + "'\nfunc main\nend"),
        ("микро: литерал 513 байт",
         "str s = '" + "x" * 513 + "'\nfunc main\nend"),
        ("микро: == в выражении (лексер пускает)",
         "func main\nvar i\ni = 1 == 2\nend"),
        ("big: big_source (1203 строки)", lab_l2_prog.big_source()),
        ("big: big_source2 (705 строк)", lab_l2_prog.big_source2()),
        # E6.4d-2/3: объявления и пост-проверка main (класс без func)
        ("микро: var g (нет main)", "var g\n"),
        ("микро: var x повтор", "var x\nvar x\nfunc main\nend\n"),
        ("микро: var a[0]", "var a[0]\nfunc main\nend\n"),
        ("микро: var a[n] (не число)", "var a[n]\nfunc main\nend\n"),
        ("микро: var a[5000] (слишком большой)", "var a[5000]\nfunc main\nend\n"),
        ("микро: var a[4096] нет main", "var a[4096]\n"),
        ("микро: var a[4097]", "var a[4097]\n"),
        ("микро: не-ключевое имя в объявлениях", "foo = 1\n"),
        ("микро: end в объявлениях", "end\n"),
        ("микро: var без имени", "var\n"),
        ("микро: var 5 (не имя)", "var 5\n"),
        ("микро: var _x (подчёркивание)", "var _x\n"),
        ("микро: var X (заглавная)", "var X\n"),
        ("микро: имя 64 байта", "var " + "x" * 64 + "\n"),
        ("микро: str без =", "str s\n"),
        ("микро: str = не литерал", "str s = 1\n"),
        ("микро: str лишний токен", "str s = 'x' y\n"),
        ("микро: str повтор", "str s = 'a'\nstr s = 'b'\n"),
        ("микро: ext дубликат без регистра", "ext Ab\next ab\n"),
        ("микро: девятый ext",
         "ext A\next B\next C\next D\next E\next F\next G\next H\next I\n"),
        ("микро: ext имя 32 байта", "ext " + "x" * 32 + "\n"),
        ("микро: str-объявление нет main", "str s = 'a'\n"),
        ("микро: все виды объявлений",
         "ext GetStdHandle\nstr s = 'a\\nb\\r\\t\\0\\\\\\'z'\nvar a[3]\nvar g\n"),
        ("микро: переводы строк (пусто)", "\n\n\n"),
        ("микро: main с параметром", "func main(x)\nend\n"),
        ("микро: незакрытый блок", "func main\n"),
    ]
    return [(n, s) for n, s in out if _ascii(s)]


def _ascii(s):
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def _expect_line(s):
    """Строка ожидаемой ошибки (int) или None — источник недоступен.

    Класс эквивалентности каркаса E6.4d-2/3 — источники, разбор которых
    решается до первой обработки func (заголовки/статы не реализованы):
    1) _lex отказал — ошибка лексера (ловится проходом 0 каркаса);
    2) parse отказал в строке L: если первая строка-func (первый токен
       id func) не раньше L — ошибка уровня объявлений/диспетчера,
       иначе None (нужен func-заголовок/статы);
    3) parse принял: func нет вовсе — «нет main» на последней непустой
       (пост-проверка, как wall.exe); func есть — None."""
    try:
        lines = lab_l2_lex._lex(s)
    except lab_l2_err.WallError as e:
        return e.line
    fline = next((no for no, toks, _t in lines
                  if toks and toks[0] == ("id", "func")), None)
    try:
        lab_l2.parse(s)
    except lab_l2_err.WallError as e:
        return e.line if fline is None or fline >= e.line else None
    return lab_l2_lex.last_line(lines) if fline is None else None


def run(check, kpath, kfile, kernel_host):
    wall = kpath("L2-WALL/wall.exe")
    enc_exe = kpath("L1-ENC/enc.exe")
    brick_exe = kpath("L1-BRICK/brick.exe")
    pegen_exe = kpath("L0-PEGEN/pegen.exe")

    # T-E6-49a: компиляция каркаса (корень+части, splice-оракул) ==
    # оракулу байт-в-байт
    src = b""
    r = None
    try:
        src = lab_splice.splice("L2-WALL/wall.wall", kernel_host())
        r = lab_run.run_kv(wall, ["s.wall", "s.b2"], {"s.wall": src})
        ok = r.exit_code == 0
        if ok:
            oracle = lab_l2.compile_wall(src.decode("latin1")).encode()
            ok = r.files.get("s.b2") == oracle
    except Exception as e:                    # noqa: BLE001 — любая = провал
        ok = False
        r = type("R", (), {"exit_code": "EXC:" + repr(e)})()
    check("T-E6-49a каркас wall.wall == оракулу (байт-в-байт)", ok,
          "код=%s" % r.exit_code)

    # T-E6-49b: полный круг каркаса: enc -> brick -> pegen -> EXE
    h = {"s.b2": r.files.get("s.b2", b"")}
    r2 = lab_run.run_kv(enc_exe, ["s.b2", "s.brick"], h)
    h["s.brick"] = r2.files.get("s.brick", b"")
    r3 = lab_run.run_kv(brick_exe, ["s.brick", "s.bin"], h)
    h["s.bin"] = r3.files.get("s.bin", b"")
    h["s.peg"] = lab_l2_prog.DEMO_WALL_PEG.encode()
    r4 = lab_run.run_kv(pegen_exe, ["s.bin", "s.peg", "s.exe"], h)
    exe = r4.files.get("s.exe", b"")
    check("T-E6-49b полный круг каркаса (enc+brick+pegen)",
          bool(r2.exit_code == 0 and r3.exit_code == 0 and
               r4.exit_code == 0 and exe),
          "коды=%s/%s/%s" % (r2.exit_code, r3.exit_code, r4.exit_code))

    # T-E6-49c: CLI-поведение каркаса == wall.exe (байт-в-байт)
    fd, path = tempfile.mkstemp(suffix=".exe")
    os.close(fd)
    open(path, "wb").write(exe)
    cases = _cases()
    bad = []
    for name, args, host, argv0 in cases:
        kw = {"argv0": argv0} if argv0 else {}
        rw = lab_win.Machine(wall, list(args), dict(host), **kw).run()
        rs = lab_win.Machine(path, list(args), dict(host), **kw).run()
        ok = rw.exit_code == rs.exit_code and rw.stdout == rs.stdout
        if not ok:
            bad.append(name)
    check("T-E6-49c CLI каркаса == wall.exe (%d путей)" % len(cases),
          not bad, "; ".join(bad[:3]))

    # T-E6-49d: проход 0+1 каркаса == оракул parse + инструмент wall.exe
    # на классе источников без обработки func (E6.4d-2/3)
    corpus = _corpus()
    bad = []
    skipped = 0
    for name, s in corpus:
        want_line = _expect_line(s)
        if want_line is None:
            skipped += 1
            continue
        wout = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % want_line).encode()
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": s.encode("latin1")}).run()
        ok = rs.exit_code == 6 and rs.stdout == wout
        if ok:                    # третья сторона: инструмент wall.exe
            rw = lab_win.Machine(wall, ["t.wall", "t.b2"],
                                 {"t.wall": s.encode("latin1")}).run()
            ok = rw.exit_code == 6 and rw.stdout == wout
        if not ok:
            bad.append("%s (код=%s)" % (name, rs.exit_code))
    check("T-E6-49d проход 0+1: объявления == оракулу parse "
          "(%d из %d, func-класс пропущен %d)"
          % (len(corpus) - skipped, len(corpus), skipped),
          not bad, "; ".join(bad[:3]))
    os.unlink(path)
