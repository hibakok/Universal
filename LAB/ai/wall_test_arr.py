"""wall_test_arr.py — dev-тест wall.exe: срез 4a — объявления массивов.

Вход:  репозиторий Universal (текущая копия).
Выход: код 0 (все проверки OK) / 1; печать [OK]/[FAIL] по секциям.
Функция: быстрая dev-проверка среза 4a (E6.4c-3/4) при работе над
         wall.exe: (1) якоря lab_l2_arr == оракулу байт-в-байт;
         (2) big_arr == оракулу; (3) отвержение массивных ошибок
         (ERRORS2 + экстра) с точными строками; (4) заголовки v1/v2;
         (5) полный круг DEMO_ARR -> enc -> brick -> pegen -> эмуляция
         -> «U-ARR-OK 45». Эталоны — LAB/py/lab_l2_arr.py (общий
         источник с батареей, конвенция среза 3b).
"""
import os
import sys
import tempfile

UNI = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(UNI, "LAB", "py"))

import lab_l2            # noqa: E402
import lab_l2_arr        # noqa: E402
import lab_l2_prog       # noqa: E402
import lab_run           # noqa: E402

WALL = os.path.join(UNI, "KERNEL", "L2-WALL", "wall.exe")
ENC = os.path.join(UNI, "KERNEL", "L1-ENC", "enc.exe")
BRICK = os.path.join(UNI, "KERNEL", "L1-BRICK", "brick.exe")
PEGEN = os.path.join(UNI, "KERNEL", "L0-PEGEN", "pegen.exe")

ok = bad = 0


def rep(good, label):
    global ok, bad
    print("[%s] %s" % ("OK " if good else "FAIL", label))
    if good:
        ok += 1
    else:
        bad += 1


def run_wall(src):
    return lab_run.run_kv(WALL, ["t.wall", "t.b2"], {"t.wall": src.encode()})


def check_full(label, src):
    want = lab_l2.compile_wall(src).encode()
    r = run_wall(src)
    good = r.exit_code == 0 and r.files.get("t.b2") == want
    rep(good, label + " (шагов %d)" % r.steps)
    if not good and r.exit_code == 0:
        got = (r.files.get("t.b2") or b"").decode("latin1").split("\n")
        wnt = want.decode("latin1").split("\n")
        for i, (a, b) in enumerate(zip(got, wnt)):
            if a != b:
                print("    строка %d:\n      wall:   %r\n      оракул: %r"
                      % (i + 1, a, b))
                break
        print("    длина: wall %d vs оракул %d" % (len(got), len(wnt)))


def main():
    # 1) якоря среза 4a == оракулу
    for name, src in lab_l2_arr.ARR_ANCHORS:
        check_full(name, src)

    # 2) big_arr == оракулу
    check_full("big_arr (%d строк)"
               % lab_l2_arr.big_arr().count("\n"), lab_l2_arr.big_arr())

    # 3) отвержение массивных ошибок с точными строками
    errs = [(n, s) for n, s, _l in lab_l2_prog.ERRORS2
            if n in lab_l2_arr.ARR_ERR_NAMES]
    errs += list(lab_l2_arr.ARR_EXTRA_ERRORS)
    for name, src in errs:
        try:
            lab_l2.compile_wall(src)
            rep(False, "ошибка «%s»: оракул принял" % name)
            continue
        except lab_l2.WallError as e:
            line = e.line
        r = run_wall(src)
        want_out = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % line).encode()
        rep(r.exit_code == 6 and r.stdout == want_out,
            "отвержение: %s (строка %d)" % (name, line))

    # 4) заголовок v2 (массив -> v2) и v1-регресс (без массивов)
    h = run_wall(lab_l2_arr.ARR_ANCHORS[0][1]).files.get("t.b2",
                                                          b"").split(b"\n")[0]
    rep(h == lab_l2.compile_wall(lab_l2_arr.ARR_ANCHORS[0][1])
        .encode().split(b"\n")[0] and b"WALL v2" in h,
        "заголовок v2 (массивы включают флаг)")
    v1 = lab_l2_prog.DEMO_WALL
    h = run_wall(v1).files.get("t.b2", b"").split(b"\n")[0]
    rep(h == lab_l2.compile_wall(v1).encode().split(b"\n")[0]
        and b"WALL v1" in h, "заголовок v1 (регресс)")

    # 5) полный круг DEMO_ARR -> ... -> эмуляция -> «U-ARR-OK 45»
    h = {"d.wall": lab_l2_arr.DEMO_ARR.encode()}
    r1 = lab_run.run_kv(WALL, ["d.wall", "d.b2"], h)
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(ENC, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(BRICK, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = lab_l2_arr.DEMO_ARR_PEG.encode()
    r4 = lab_run.run_kv(PEGEN, ["d.bin", "d.peg", "d.exe"], h)
    demo = r4.files.get("d.exe", b"")
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, demo)
        os.close(fd)
        r5 = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    rep(r1.exit_code == 0 and r2.exit_code == 0 and r3.exit_code == 0
        and r4.exit_code == 0 and r5.exit_code == 0
        and r5.stdout == b"U-ARR-OK 45\r\n",
        "полный круг DEMO_ARR (U-ARR-OK 45); шагов %d+%d+%d+%d+%d"
        % (r1.steps, r2.steps, r3.steps, r4.steps, r5.steps))

    print("\nИТОГ: %d OK / %d FAIL" % (ok, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
