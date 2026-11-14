"""lab_t_wallself.py — секция 12 батареи: каркас wall.wall (E6.4d-1..2).

Вход:  колбэки check/kpath/kfile/kernel_host из lab_verify.
Выход: проверки T-E6-49a/b/c (печать через check).
Функция: самохостинг E6.4d начат — KERNEL/L2-WALL/wall.wall (WALL v2)
         компилируется инструментом wall.exe байт-в-байт как оракул
         (R8); полный круг enc+brick+pegen даёт рабочий EXE; CLI-
         поведение каркаса == wall.exe байт-в-байт (stdout и коды
         возврата) на матрице путей. E6.4d-2: буфер входа — GlobalAlloc
         (8-й ext, GMEM_FIXED; один ReadFile с лимитом 131073) — матрица
         проверяет границы BIG SRC: 131073 (отказ) и 131072 (успех).
         Известное и ДОПУСТИМОЕ отличие шагов 1-2: содержимое выходного
         .b2 при успехе (каркас ещё не компилирует; проверяется пустой
         выход). Попутно секция защищает фикс дефекта №16 (str_emit:
         DB-строки литералов >= 13 байт — s_use каркаса 42 байта).
"""
import os
import tempfile

import lab_l2
import lab_l2_prog
import lab_run
import lab_win

USAGE = b"U-L2-WALL CMDS: WALL <SRC.WALL> <OUT.B2>\r\n"


def _cases():
    """Матрица CLI-путей: (имя, args, host, argv0)."""
    src_ok = b"func main\nend"
    big_ok = b";" + b"x" * (131072 - 15) + b"\n" + src_ok
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
        ("граница 131072: успех", ["t.wall", "t.b2"],
         {"t.wall": big_ok}, None),
        ("успех: пустая программа", ["t.wall", "t.b2"],
         {"t.wall": src_ok}, None),
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
    src = kfile("L2-WALL/wall.wall")

    # T-E6-49a: компиляция каркаса — wall.exe == оракулу байт-в-байт
    r = lab_run.run_kv(wall, ["s.wall", "s.b2"], {"s.wall": src})
    ok = r.exit_code == 0
    if ok:
        oracle = lab_l2.compile_wall(src.decode()).encode()
        ok = r.files.get("s.b2") == oracle
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
        if ok and rs.exit_code == 0 and name.startswith("успех"):
            ok = rs.files.get("t.b2", b"") == b""       # шаг 1: пустой .b2
        if not ok:
            bad.append(name)
    check("T-E6-49c CLI каркаса == wall.exe (%d путей)" % len(cases),
          not bad, "; ".join(bad[:3]))
    os.unlink(path)
