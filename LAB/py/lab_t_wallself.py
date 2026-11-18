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
         Границы BIG SRC (E6.4g-4: 256 КиБ): 262145 (отказ) и 262144
         (оба инструмента дают нет main); буфер входа, карта текстов и
         таблицы прохода 1 — GlobalAlloc (куча эмулятора 16 МиБ с
         E6.4d-4/3a: +outmem 2103264 = блоб канона 2048 + scr 64 +
         outbuf 2 МиБ; srcbuf — 262145 с E6.4g-4); tabmem 4948032 =
         таблицы + bstk 3072x32 + ifarr 32768x8.
         E6.4d-4/3a (срез A прохода 2): T-E6-52 — эмитция ПРОЛОГА
         (части wall_self_blob/e/y: блоб канона hex-литералами, out_*,
         emit_header/imports/entry).
         E6.4d-4/3b (срез B прохода 2): T-E6-52 — эмитция ФУНКЦИЙ
         (части wall_self_y/f: цикл строк p2_line + p2_funchdr +
         p2s_end/var/return + механика bstk if/while/else + кадры
         E010/E011/E017/E018/E019): на классе источников, тела
         которых — только var / голый return / end, выход каркаса
         обязан быть байт-в-байт равен выходу оракула. Матрица:
         0/8 ext, 0..4 параметра (ARGREG), v2 (заголовок + локальные
         массивы), многозначные счётчики. Прочие статы тел — код 0
         без эмитции (вне класса; bstk-механика — регресс
         T-E6-49d).
         E6.4d-4/3c-1 (срез C часть 1 — СЕКЦИИ ДАННЫХ): T-E6-52
         переведён на ПОЛНЫЙ выход (8 ext + 10 var — без префикса) +
         НОВЫЙ T-E6-54: секции данных == оракулу (пустая str «DZ 0»,
         экраны всех 6 видов, граница DB-строки 16/17, длинная str
         42 Б — класс дефекта №16, var-only скаляры/массивы «DZ 8»/
         «DZ 8n», отступы/«;»-хвосты — комментарий из карты текстов);
         эмиттеры K2-E009/E013/E014 (часть wall_self_e.wall) +
         K2-E027/E028 (НОВАЯ часть wall_self_d.wall); статы-выражения
         — срезы C+.
         E6.4d-4/3c-2/1 (срез C часть 2 шаг 1 — ВЫРАЖЕНИЯ эмит-
         режимом): НОВЫЙ T-E6-55 — return <выражение> == оракулу
         (числа/имена load-addr-len/скобки/унарный '-'/все операции
         + - | ^ & << >> * / %; длинные цепочки K=5, вложенные смеси
         уровней, v1/v2); глобаль pc_mode (0 — стат прохода 1,
         1 — эмит прохода 2), chain_count K2-P009 + эмит-плечи
         p_expr/p_mul/p_mdm/p_unary (часть wall_self_ph.wall) +
         эмиттеры K2-E020/E021/E022/E023/E024/E034/E035 (НОВАЯ часть
         wall_self_g.wall); p2_funchdr ставит st_p2maxd/st_p2maxc/
         st_p2nbase + окно lay из ftab; p2s_return Y008 — выражение +
         «M mov rax, r10». E6.4g-4: предел входа wall.exe и каркаса
         128 КиБ -> 256 КиБ (filebuf wall.exe перенесён в хвост bss
         после outbuf; оракул синхронизирован; границы BIG SRC
         262144/262145). Дефект №20 (закрыт): chain_count считал
         унарный '-' операцией (уровень 0) / терминатором (1/2) —
         T-адреса расходились с оракулом; фикс — флаг «конец
         операнда» в wall.exe и каркасе синхронно.
         E6.4d-4/3c-2/2 (срез C часть 2 шаг 2 — ВЫРАЖЕНИЯ С ВЫЗОВАМИ
         И ИНДЕКСАЦИЕЙ эмит-режимом): НОВЫЙ T-E6-56 — return <выраже-
         ние> с вызовами func/ext (0..5 аргументов, S5 + [rsp+20]),
         вложенными вызовами (фикс №19 + №21), getb и постфиксной
         индексацией (цепочки p[0][1], вызов-база f(0)[1], скобочная
         база (a+0)[2], вызовы в индексах) == оракулу ЦЕЛИКОМ;
         pa_stage K2-P017 + p_call_tail K2-P015 + helper emit_argload
         (НОВАЯ часть каркаса — функции wall_self_pa.wall) + эмит-плечи
         p_args/pp_prim0/pp_pairs/p_prim (wall_self_pp.wall: откат
         outcur + перепознание базы на d+k). ДЕФЕКТ №21 (закрыт,
         синхронно wall_pa.b2 P014 + пересборка wall.exe SHA
         295730EF…): pc_staged хранил только счёт без базы — двойная
         вложенность вызовов получала базу 0, затирала C-слоты
         объемлющего и занижала maxc/framesize (якорь: maxc 2 -> 3);
         найден сравнением каркаса с оракулом на новых источниках
         C-2/2 (dev wall_self_emit.py, 39 источников).
         E6.4d-4/3c-2/3 (срез C часть 2 шаг 3 — СТАТЫ-ИМЕНА
         эмит-режимом): НОВЫЙ T-E6-57 — тела с присваиваниями
         локали/глобали, вызовами-утверждениями func/ext (0..5
         аргументов, want 0), astore (k == 1 emit_load-база / k > 1
         цепочка pp_prim0(k)+pp_pairs(1, k-1), S0/S1/S2 ПОРОЗНЬ +
         хвост shl 3 / add / mov [r10], r11) и setb (S0/S1/S2 +
         байтовая запись [r10+r11] = al, индекс БЕЗ *8) == оракулу
         ЦЕЛИКОМ; emit_sstore K2-E02D + p2s_setb K2-Y009 +
         p2_namestmt K2-Y00B (НОВАЯ часть каркаса wall_self_t.wall)
         + плечи p2_line (kwi == 9 / цепочка — как Y002 wall.exe;
         break/continue — пропуск до C-3). ДЕФЕКТ №22 (закрыт,
         только каркас — guard в wall.exe P01D был): astore_chk
         копировал lay-окно st_locoff/st_loccnt БЕЗУСЛОВНО — в
         проходе 2 затирал окно p2_funchdr прошлогонними значениями
         конца прохода 1 (astore локали не в последней функции —
         ERR=FORMAT вместо кода 0); канарейка — локальные массивы в
         двух функциях (с дефектом: код 6 AT=0004). Источники
         T-E6-55/56/57 — модуль данных lab_t_wallself_emit_cases.py
         (лимит 500 строк; выделен по образцу corpus/model).
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
import lab_t_wallself_emit_cases as wscases

USAGE = b"U-L2-WALL CMDS: WALL <SRC.WALL> <OUT.B2>\r\n"


def _cases():
    """Матрица CLI-путей: (имя, args, host, argv0)."""
    # 262144 = граница чтения BIG SRC (262145 — отказ; E6.4g-4):
    # 1 + 262136 + 1 + 6 байт; строки: гигантский комментарий, var g
    src_ok = b"var g\n"
    big_ok = b";" + b"x" * 262136 + b"\n" + b"var g\n"
    return [
        ("справка (0 аргументов)", [], {}, None),
        ("справка (1 аргумент)", ["t.wall"], {}, None),
        ("вход отсутствует", ["t.wall", "t.b2"], {}, None),
        ("длинное имя arg1", ["x" * 128, "t.b2"], {}, None),
        ("длинное имя arg2", ["t.wall", "x" * 128], {}, None),
        ("BIG SRC (>262145)", ["t.wall", "t.b2"],
         {"t.wall": b"\n" * 300000}, None),
        ("BIG SRC (граница 262145)", ["t.wall", "t.b2"],
         {"t.wall": b"\n" * 262145}, None),
        ("граница 262144: оба дают нет main", ["t.wall", "t.b2"],
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

    # T-E6-52: эмитция пролога+функций+секций данных (срезы A+B+C-1
    # прохода 2, E6.4d-4/3a..3c-1) — выход каркаса == выходу оракула
    # ЦЕЛИКОМ на классе «тела из var/голого return/end» — ВКЛЮЧАЯ
    # глобальные str/var (срез C-1 замкнул хвост: до него — точный
    # префикс до секции «; --- данные: ...»; статы-выражения —
    # срезы C+)
    src_8ext = ("ext GetStdHandle\next WriteFile\next ExitProcess\n"
                "ext GetCommandLineA\next CreateFile2\next ReadFile\n"
                "ext CloseHandle\next GlobalAlloc\nfunc f0(a, b, c, d)\n"
                "end\nfunc main\n  return\nend\n")
    emit_cases = [
        ("0 ext, полный выход",
         "func add(a, b)\nend\nfunc main\n  return\nend\n"),
        ("8 ext + 10 var (полный: импорты + DZ-секция)",
         "\n".join("var v%d" % i for i in range(10)) + "\n" + src_8ext),
        ("v2: локальные массивы, полный выход",
         "func work(x)\n  var a[4]\n  var t[2]\n  return\nend\n"
         "func main\n  var i\n  var a[12]\n  return\nend\n"),
    ]
    bad = []
    for name, src in emit_cases:
        sb = src.encode("utf-8")
        out = lab_l2.compile_wall(src).encode("utf-8")
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": sb}).run()
        got = rs.files.get("t.b2", b"")
        if not (rs.exit_code == 0 and rs.stdout == b"" and
                got == out):
            bad.append("%s (%d Б, нужно %d Б, код=%s)"
                       % (name, len(got), len(out), rs.exit_code))
    check("T-E6-52 эмитция пролога+функций+данных == оракулу "
          "(3 источника)", not bad, "; ".join(bad[:3]))

    # T-E6-54: СЕКЦИИ ДАННЫХ (срез C-1, E6.4d-4/3c-1) — K2-E009
    # emit_cmt / E013 str_dlen / E014 str_emit / E027 emit_strdata /
    # E028 emit_globdata: «:имя» + DB-строки <= 16 байтов (экраны
    # \n \r \t \0 \\ ') / «DZ 0» / «DZ 8n»; комментарий — текст строки
    # объявления из карты текстов (без пробелов по краям и «;»-хвоста);
    # заголовки секций — только при непустой секции; выход ЦЕЛИКОМ ==
    # оракулу
    data_cases = [
        ("пустая str (DZ 0)",
         "str e = ''\nfunc main\n  return\nend\n"),
        ("экраны всех 6 видов",
         "str s = 'a\\nb\\rc\\td\\0e\\\\f'\nfunc main\n  "
         "return\nend\n"),
        ("граница DB-строки 16/17 байтов",
         "str a = '0123456789ABCDEF'\n"
         "str b = '0123456789ABCDEFG'\nfunc main\n  return\nend\n"),
        ("длинная str 42 Б — 3 строки DB (дефект №16)",
         "str u = 'U-L2-WALL CMDS: WALL <SRC.WALL> <OUT.B2>'\n"
         "func main\n  return\nend\n"),
        ("var-only: скаляры и массивы (DZ 8 / DZ 8n)",
         "var g\nvar a[3]\nvar z[1]\nfunc main\n  return\nend\n"),
        ("отступы и «;»-хвосты (карта текстов в комментариях)",
         "  var g ; комментарий\n\tstr s = 'ab' ; ещё\n"
         "  func main\n    return\n  end\n"),
    ]
    bad = []
    for name, src in data_cases:
        sb = src.encode("utf-8")
        out = lab_l2.compile_wall(src).encode("utf-8")
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": sb}).run()
        got = rs.files.get("t.b2", b"")
        if not (rs.exit_code == 0 and rs.stdout == b"" and
                got == out):
            bad.append("%s (%d Б, нужно %d Б, код=%s)"
                       % (name, len(got), len(out), rs.exit_code))
    check("T-E6-54 секции данных каркаса == оракулу (%d источников)"
          % len(data_cases), not bad, "; ".join(bad[:3]))

    # T-E6-55: ВЫРАЖЕНИЯ (срез C-2/1, E6.4d-4/3c-2/1) — pc_mode/
    # chain_count (дефект №20: унарный '-' в цепочке — флаг «конец
    # операнда», синхронный фикс wall.exe) / эмит-плечи p_expr-p_unary
    # + эмиттеры E020/E021/E022/E023/E024/E034/E035 (часть
    # wall_self_g.wall): return <выражение> из чисел/имён (load/addr/
    # len)/скобок/унарного '-' и операций + - | ^ & << >> * / % —
    # выход ЦЕЛИКОМ == оракулу
    expr_cases = wscases.EXPR_CASES
    bad = []
    for name, src in expr_cases:
        sb = src.encode("utf-8")
        out = lab_l2.compile_wall(src).encode("utf-8")
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": sb}).run()
        got = rs.files.get("t.b2", b"")
        if not (rs.exit_code == 0 and rs.stdout == b"" and
                got == out):
            bad.append("%s (%d Б, нужно %d Б, код=%s)"
                       % (name, len(got), len(out), rs.exit_code))
    check("T-E6-55 выражения return == оракулу (%d источников)"
          % len(expr_cases), not bad, "; ".join(bad[:3]))

    # T-E6-56: ВЫРАЖЕНИЯ С ВЫЗОВАМИ/GETB/ИНДЕКСАЦИЕЙ (срез C-2/2,
    # E6.4d-4/3c-2/2) — pa_stage/P017 (стейджинг C(base+cnt+1), 5-й
    # аргумент ext -> S5) + p_call_tail/P015 (загрузки ARGREG из
    # C(pc_cbase+i), «M call $имя» / «M call [rip+$_iat_имя]», хвост
    # «M mov r10, rax») + эмит-плечи p_args/P014, pp_prim0 (вызов +
    # getb: T-склад d + movzx) и обёртка p_prim (откат outcur,
    # перепознание базы на d+k) + pp_pairs/P01C (T-склад t(cur-1),
    # индекс на cur, хвост shl r10,3 / mov r11 / mov r10,[T] / add /
    # mov r10,[r10]) — части wall_self_pa/pp.wall; выход ЦЕЛИКОМ ==
    # оракулу. ДЕФЕКТ №21 (закрыт здесь, синхронно wall_pa.b2 P014):
    # pc_staged хранил только счёт без базы — двойная вложенность
    # вызовов (вызов в аргументах вызова с base > 0) получала базу 0
    # и затирала C-слоты объемлющего (maxc/framesize занижались,
    # стейджинг портил чужие аргументы); якорь-источник —
    # «вложенные вызовы» (f(g(h(1),2), h(g(3,h(4)))) — maxc 2 -> 3).
    call_cases = wscases.CALL_CASES
    bad = []
    for name, src in call_cases:
        sb = src.encode("utf-8")
        out = lab_l2.compile_wall(src).encode("utf-8")
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": sb}).run()
        got = rs.files.get("t.b2", b"")
        if not (rs.exit_code == 0 and rs.stdout == b"" and
                got == out):
            bad.append("%s (%d Б, нужно %d Б, код=%s)"
                       % (name, len(got), len(out), rs.exit_code))
    check("T-E6-56 выражения: вызовы+getb+индексация == оракулу "
          "(%d источников)" % len(call_cases), not bad, "; ".join(bad[:3]))

    # T-E6-57: СТАТЫ-ИМЕНА (срез C-2/3, E6.4d-4/3c-2/3) —
    # emit_sstore/E02D + p2s_setb/Y009 + p2_namestmt/Y00B (НОВАЯ
    # часть wall_self_t.wall) + плечи p2_line; ДЕФЕКТ №22 (закрыт,
    # только каркас): astore_chk копировал lay-окно безусловно — в
    # проходе 2 затирал окно p2_funchdr (st_locoff/st_loccnt —
    # прошлогонние с конца прохода 1); guard pc_mode == 0 — как
    # P01D wall.exe; канарейка — astore локального массива в
    # функции, отличной от последней функции прохода 1.
    stmt_cases = wscases.STMT_CASES
    bad = []
    for name, src in stmt_cases:
        sb = src.encode("utf-8")
        out = lab_l2.compile_wall(src).encode("utf-8")
        rs = lab_win.Machine(path, ["t.wall", "t.b2"],
                             {"t.wall": sb}).run()
        got = rs.files.get("t.b2", b"")
        if not (rs.exit_code == 0 and rs.stdout == b"" and
                got == out):
            bad.append("%s (%d Б, нужно %d Б, код=%s)"
                       % (name, len(got), len(out), rs.exit_code))
    check("T-E6-57 статы-имена: присваивания+вызовы+astore+setb == "
          "оракулу (%d источников)" % len(stmt_cases), not bad,
          "; ".join(bad[:3]))
    os.unlink(path)
