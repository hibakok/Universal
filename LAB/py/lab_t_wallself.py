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
         тела с var-объявлениями.
         E6.4d-3/2: выражения в стат-режиме (части ph/pp/pa) и статы
         S00B return / S00C setb / S00D namestmt (вызов-утверждение /
         astore / присваивание) — класс расширен на тела с выраже-
         ниями. E6.4d-3/3: статы bstk-группы — S009 if + S00A while
         (условие p_cond P018 стат-плечо, часть pc: сравнения
         ==/!=/</<=/>/>=, конъюнкты '&&' / дизъюнкты '||', v2flag) +
         S008 else (bstk kind 2 -> 3, ifarr) + S00F break/continue
         (скан bstk до while). Правило класса: строка стата сравнима,
         если (а) обе стороны отвергают её (perr == строка — ошибки
         фронтенда совпадают: проверки wall.exe прохода 1 == оракул
         parse на корпусе) или (б) обе принимают — тогда продолжение;
         ИСКЛЮЧЕНИЕ — ошибки только прохода 2 (cerr = строка ошибки
         compile_wall: неизвестное имя в выражении/условии, присваи-
         вание str и т.п.): каркас (без эмитции) даст 0, wall.exe 6 —
         вне класса. Ключевые слова str/ext в теле у каркаса идут в
         p1_namestmt (их нет в kw-плечах wall.exe): обычно ERR=FORMAT
         той же строки (сравнимо при perr == строка), но патологичес-
         кие «str = выр» / «ext(арг)» namestmt ПРИНИМАЕТ (оракул
         отвергает/принимает иначе) — вне класса (модель _kw_falls);
         корректные if/while/else/break/continue-строки обрабатывают
         собственные плечи S009/S00A/S008/S00F (E6.4d-3/3). Голый
         getb(...)-стат — вызов не-функции (cerr) — вне класса.
         Вложенная func — quirk wall.exe: инструменты принимают её
         как заголовок (плечо kw==3 раньше fcur; проверено: каркас ==
         wall.exe), оракул падает «не разобрано» — источник вне класса.
         Границы BIG SRC: 131073 (отказ) и 131072 (оба инструмента
         дают нет main); буфер входа, карта текстов и таблицы прохода 1
         — GlobalAlloc (куча эмулятора 16 МиБ с E6.4d-4/3a: +outmem
         2103264 = блоб канона 2048 + scr 64 + outbuf 2 МиБ; было
         8 МиБ — 98% занято); tabmem 4948032 = таблицы + bstk 3072x32
         + ifarr 32768x8.
         E6.4d-4/3a (срез A прохода 2): T-E6-52 — эмитция ПРОЛОГА
         (части wall_self_blob/e/y: блоб канона hex-литералами, out_*,
         emit_header/imports/entry).
         E6.4d-4/3b (срез B прохода 2): T-E6-52 — эмитция ФУНКЦИЙ
         (части wall_self_y/f: цикл строк p2_line + p2_funchdr +
         p2s_end/var/return + механика bstk if/while/else + кадры
         E010/E011/E017/E018/E019): на классе источников, тела
         которых — только var / голый return / end, выход каркаса
         обязан быть байт-в-байт равен выходу оракула ЦЕЛИКОМ
         (без глобальных str/var) или ТОЧНЫМ ПРЕФИКСОМ до секции
         «; --- данные: ...» (секции данных — срез C). Матрица:
         0/8 ext, 0..4 параметра (ARGREG), v2 (заголовок + локальные
         массивы), многозначные счётчики. Прочие статы тел — код 0
         без эмитции (вне класса; bstk-механика — регресс
         T-E6-49d).
"""
import os
import tempfile

import lab_run
import lab_splice
import lab_win

import lab_l2
import lab_l2_prog
import lab_t_wallself_corpus
from lab_t_wallself_corpus import KITCHEN
from lab_t_wallself_model import _expect_line

USAGE = b"U-L2-WALL CMDS: WALL <SRC.WALL> <OUT.B2>\r\n"


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
    corpus = lab_t_wallself_corpus.corpus()
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
    check("T-E6-49d проход 0+1: статы тел (все статы прохода 1) == "
          "оракулу parse (%d из %d, код-0 %d, вне класса %d)"
          % (len(corpus) - skipped, len(corpus), zeros, skipped),
          not bad, "; ".join(bad[:3]))

    # T-E6-52: эмитция пролога+функций (срезы A+B прохода 2,
    # E6.4d-4/3a..3b) — выход каркаса == выходу оракула на классе
    # «тела из var/голого return/end»: ЦЕЛИКОМ (без глобальных
    # str/var) или ТОЧНЫМ ПРЕФИКСОМ до секции «; --- данные: ...»
    # (секции данных — срез C); статы/выражения/данные — срезы C+
    src_8ext = ("ext GetStdHandle\next WriteFile\next ExitProcess\n"
                "ext GetCommandLineA\next CreateFile2\next ReadFile\n"
                "ext CloseHandle\next GlobalAlloc\nfunc f0(a, b, c, d)\n"
                "end\nfunc main\n  return\nend\n")
    emit_cases = [
        ("0 ext, полный выход",
         "func add(a, b)\nend\nfunc main\n  return\nend\n"),
        ("8 ext + 4 параметра (префикс: 10 var)",
         "\n".join("var v%d" % i for i in range(10)) + "\n" + src_8ext),
        ("v2: локальные массивы, полный выход",
         "func work(x)\n  var a[4]\n  var t[2]\n  return\nend\n"
         "func main\n  var i\n  var a[12]\n  return\nend\n"),
    ]
    bad = []
    for name, src in emit_cases:
        sb = src.encode("utf-8")
        out = lab_l2.compile_wall(src)
        lines = out.split("\n")
        cut = None
        for i, ln in enumerate(lines):
            if ln.startswith("; --- данные:"):
                cut = i
                break
        if cut is None:
            prefix = out.encode("utf-8")
        else:
            prefix = ("\n".join(lines[:cut]) + "\n").encode("utf-8")
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": sb}).run()
        got = rs.files.get("t.b2", b"")
        if not (rs.exit_code == 0 and rs.stdout == b"" and
                got == prefix):
            bad.append("%s (%d Б, нужно %d Б, код=%s)"
                       % (name, len(got), len(prefix), rs.exit_code))
    check("T-E6-52 эмитция пролога+функций == оракулу (3 источника)",
          not bad, "; ".join(bad[:3]))
    os.unlink(path)
