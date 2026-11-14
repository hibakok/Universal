"""lab_t_wallself.py — секция 12 батареи: самохостинг wall.wall (E6.4d).

Вход:  колбэки check/kpath/kfile/kernel_host из lab_verify.
Выход: проверки T-E6-49a/b/c/d (печать через check).
Функция: самохостинг E6.4d — KERNEL/L2-WALL/wall.wall (WALL v2, корень
         с разрезом SPEC/10: wall_self_c.wall — сервис, wall_self_n.wall
         — проход 0, wall_self_pe/pd/p1/p1s.wall — проход 1) компилируется
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
         без обработки func.
         E6.4d-2/4: заголовки func (S004 p1_funchdr + S00E fh_param —
         имя, <= 4 параметров, дубликаты, larr/bstk/ftab в куче tabmem)
         и закрытие func плечом end (S007 p1s_end: финальная запись
         ftab, fcur = 0) — класс расширен на источники с func-заголовками
         и ПУСТЫМИ телами: прочие статы тела дают ERR=FORMAT текущей
         строки (S006+ — шаг E6.4d-3); успешно разобранные источники
         дают КОД 0 (выход .b2 пока пуст — эмитция прохода 2 позже).
         E6.4d-3/1: локальные var (S006 p1s_var части p1s: имя,
         [n] 1..4096, at_end, дубликат в окне [st_locoff,
         st_locoff+st_loccnt), конфликт с глобальными — порядок
         проверок == wall.exe == оракул parse) — класс расширен на
         тела с var-объявлениями: ошибки обеих сторон на строке
         (сравнимо), корректные var — код 0.
         Вложенная func — quirk wall.exe: инструменты принимают её
         как заголовок (плечо kw==3 раньше fcur; проверено: каркас ==
         wall.exe), оракул падает «не разобрано» — источник вне класса.
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
        # E6.4d-2/4: заголовки func + плечо end (класс с пустыми телами)
        ("микро: func без имени", "func 5\nend\n"),
        ("микро: func имя повтор",
         "func f\nend\nfunc f\nend\nfunc main\nend\n"),
        ("микро: пустые скобки main — код 0", "func main()\nend\n"),
        ("микро: main 4 параметра", "func main(a, b, c, d)\nend\n"),
        ("микро: func скобка без закр", "func f(a\nend\nfunc main\nend\n"),
        ("микро: func конец мусор", "func f x\nend\nfunc main\nend\n"),
        ("микро: параметр == глобаль",
         "var g\nfunc f(g)\nend\nfunc main\nend\n"),
        ("микро: запятая без параметра", "func f(,)\nend\nfunc main\nend\n"),
        ("микро: end между func",
         "func f\nend\nend\nfunc main\nend\n"),
        ("микро: две func + main — код 0",
         "func a\nend\nfunc main\nend\n"),
        ("микро: CRLF-заголовки — код 0",
         "func f\r\nend\r\nfunc main\r\nend\r\n"),
        ("микро: var в теле (E6.4d-3/1 — сравнимо)", "func main\nvar i\nend\n"),
        ("микро: вложенная func (quirk — вне класса)",
         "func f\nfunc g\nend\nend\n"),
        # E6.4d-3/1: локальные var (S006) — ошибки и код-0
        ("микро: var в теле две — код 0", "func main\nvar i\nvar j\nend\n"),
        ("микро: var в теле массив — код 0", "func main\nvar a[3]\nend\n"),
        ("микро: var в теле a[4096] — код 0", "func main\nvar a[4096]\nend\n"),
        ("микро: var в теле a[4097]", "func main\nvar a[4097]\nend\n"),
        ("микро: var в теле a[0]", "func main\nvar a[0]\nend\n"),
        ("микро: var в теле dup", "func main\nvar i\nvar i\nend\n"),
        ("микро: var в теле dup параметра",
         "func f(x)\nvar x\nend\nfunc main\nend\n"),
        ("микро: var в теле конфликт глобали",
         "var g\nfunc main\nvar g\nend\n"),
        ("микро: var в теле конфликт str",
         "str s = 'a'\nfunc main\nvar s\nend\n"),
        ("микро: var в теле имя функции",
         "func f\nend\nfunc main\nvar f\nend\n"),
        ("микро: var в теле _x", "func main\nvar _x\nend\n"),
        ("микро: var в теле хвост мусор", "func main\nvar i = 5\nend\n"),
        ("микро: var между func — hdrfail",
         "func f\nend\nvar x\nfunc main\nend\n"),
        ("микро: var в теле + main(a)",
         "func f\nvar i\nend\nfunc main(a)\nend\n"),
    ]
    return [(n, s) for n, s in out if _ascii(s)]


def _ascii(s):
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def _expect_line(s):
    """(код, строка) — исход ожидания: (6, L) — ERR=FORMAT AT=L;
    (0, None) — успех (код 0, пустой stdout/.b2); None — источник вне
    класса эквивалентности каркаса (пропуск).

    Класс E6.4d-3/1 (S006 локальные var + S004 заголовки func + S007
    плечо end; в теле — только var/end): моделирование прохода 1
    каркаса по строкам оракула _lex (состояние fcur/seenfunc/fdepth;
    строки с токенами):
    1) _lex отказал — ошибка лексера (ловится проходом 0 каркаса);
    2) не-имя первым токеном — каркас ERR=FORMAT на строке; сравнимо,
       если оракул parse падает на той же строке;
    3) func — заголовок (в ЛЮБОМ состоянии — quirk wall.exe: плечо
       kw==3 раньше fcur; вложенная func — оракул падает на строке,
       инструменты принимают — вне класса); ошибка заголовка у обоих
       на строке заголовка; корректный заголовок — fcur=1/seenfunc=1/
       fdepth+1;
    4) в теле (fcur): end — закрытие (fdepth-1, fcur=0; лишние токены
       или лишний end — ошибка на строке); var — локаль (S006):
       ошибки имени/[n]/at_end/дубликата/глобали — на строке у обоих
       (порядок проверок совпадает), принято — продолжение; прочий
       стат — каркас ERR=FORMAT на строке (S008+ — следующие под-шаги
       E6.4d-3); сравнимо, если оракул падает на той же строке, иначе
       — вне класса;
    5) между func (seenfunc) — только func (заголовок), прочее —
       ERR=FORMAT на строке у обоих (плече hdrfail — как wall.exe:
       kw-статы действуют только при fcur != 0);
    6) до первой func — объявления S003 (как E6.4d-2/3);
    7) пост-проверки: незакрытый func — set_lastline (последняя
       непустая); ровно одна main без параметров — КОД 0 (выход .b2
       пуст — эмитция прохода 2 позже); main с параметрами — ошибка
       в строке заголовка main; не одна main — последняя непустая.
    Сравнимо = модель совпадает с ожиданием оракула parse (строка
    ошибки или приём). Инструмент wall.exe — третья сторона (проверя-
    ется прогоном)."""
    try:
        lines = lab_l2_lex._lex(s)
    except lab_l2_err.WallError as e:
        return (6, e.line)
    try:
        lab_l2.parse(s)
        perr = None
    except lab_l2_err.WallError as e:
        perr = e.line
    fcur = seen = fdepth = 0
    for no, toks, _t in lines:
        if not toks:
            continue
        k, v = toks[0]
        if k != "id":
            return (6, no) if perr == no else None
        if v == "func":
            if fcur:
                # вложенная func — quirk wall.exe: инструменты приняли
                # бы заголовок (проверено: каркас == wall.exe), оракул
                # падает на этой строке — вне класса
                return None
            if perr == no:
                return (6, no)
            fcur = 1
            seen = 1
            fdepth += 1
            continue
        if fcur:
            if v == "end":
                if perr == no:
                    return (6, no)
                fdepth -= 1
                fcur = 0
                continue
            if v == "var":
                # S006 (E6.4d-3/1): ошибки имени/[n]/at_end/дубликата/
                # глобали — на строке у обеих сторон (порядок совпа-
                # дает); принято — локаль в окне, продолжение
                if perr == no:
                    return (6, no)
                continue
            return (6, no) if perr == no else None
        if seen:
            return (6, no) if perr == no else None
        if perr == no:
            return (6, no)
    if fdepth or fcur:
        last = lab_l2_lex.last_line(lines)
        return (6, last) if perr == last else None
    # все func закрыты (тела пустые): пост-проверка main по заголовкам
    mains = mline = mpar = 0
    inf = 0
    for no, toks, _t in lines:
        if not toks:
            continue
        k, v = toks[0]
        if k == "id" and v == "func":
            inf = 1
            nm = toks[1][1] if len(toks) > 1 and toks[1][0] == "id" \
                else None
            np_ = 0
            if ("sym", "(") in toks:
                i = toks.index(("sym", "("))
                if not (i + 1 < len(toks) and toks[i + 1] == ("sym", ")")):
                    np_ = sum(1 for t in toks[i + 1:] if t[0] == "id")
            if nm == "main":
                mains += 1
                mline = no
                mpar = np_
        elif k == "id" and v == "end" and inf:
            inf = 0
    if mains == 1 and mpar == 0:
        return (0, None) if perr is None else None
    if mains == 1 and mpar != 0:
        return (6, mline) if perr == mline else None
    last = lab_l2_lex.last_line(lines)
    return (6, last) if perr == last else None


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
    # на классе источников с func-заголовками и ПУСТЫМИ телами
    # (E6.4d-2/4; тела с прочими статами — E6.4d-3)
    corpus = _corpus()
    bad = []
    skipped = 0
    zeros = 0
    for name, s in corpus:
        want = _expect_line(s)
        if want is None:
            skipped += 1
            continue
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": s.encode("latin1")}).run()
        if want[0] == 6:
            wout = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n"
                    % want[1]).encode()
            ok = rs.exit_code == 6 and rs.stdout == wout
        else:
            ok = rs.exit_code == 0 and rs.stdout == b""
            zeros += 1
        if ok:                    # третья сторона: инструмент wall.exe
            rw = lab_win.Machine(wall, ["t.wall", "t.b2"],
                                 {"t.wall": s.encode("latin1")}).run()
            if want[0] == 6:
                ok = rw.exit_code == 6 and rw.stdout == wout
            else:
                ok = rw.exit_code == 0 and rw.stdout == b""
        if not ok:
            bad.append("%s (код=%s)" % (name, rs.exit_code))
    check("T-E6-49d проход 0+1: заголовки func + end == оракулу parse "
          "(%d из %d, код-0 %d, вне класса %d)"
          % (len(corpus) - skipped, len(corpus), zeros, skipped),
          not bad, "; ".join(bad[:3]))
    os.unlink(path)
