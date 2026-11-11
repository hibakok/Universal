"""wall_test_bc.py — dev-тест wall.exe v2 (E6.4c-3, срез 2: break/continue).

Паспорт файла: LAB/ai/wall_test_bc.py | слой: внешний инструмент |
роль: быстрый dev-прогон срез 2 (break/continue) при работе над
wall.exe: сверка с оракулом LAB/py/lab_l2* + регресс дефекта №15 (bstk
3072x32) + якорь B2 + ошибки ERRORS2 + полный круг DEMO_BC. Эталоны
срез 2 — в LAB/py/lab_l2_bc.py (с E6.4c-3/3b общий источник с
батареей, секция 11 = T-E6-37..45); ошибки — фильтр BC_ERR_NAMES из
общего списка ERRORS2 (lab_l2_prog). Запуск: python3 LAB/ai/wall_test_bc.py.
"""
import os
import sys
import tempfile

UNI = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(UNI, "LAB", "py"))
import lab_brick          # noqa: E402
import lab_enc            # noqa: E402
import lab_l2             # noqa: E402
import lab_l2_bc          # noqa: E402
import lab_l2_cases2      # noqa: E402
import lab_l2_prog        # noqa: E402
import lab_pegen          # noqa: E402
import lab_run            # noqa: E402

WALL = os.path.join(UNI, "KERNEL", "L2-WALL", "wall.exe")
ENC = os.path.join(UNI, "KERNEL", "L1-ENC", "enc.exe")
BRICK = os.path.join(UNI, "KERNEL", "L1-BRICK", "brick.exe")
PEGEN = os.path.join(UNI, "KERNEL", "L0-PEGEN", "pegen.exe")

# ошибки срез 2: записи из общего ERRORS2 по именам BC_ERR_NAMES
BC_ERRORS = [e for e in lab_l2_prog.ERRORS2
             if e[0] in lab_l2_bc.BC_ERR_NAMES]


def run_wall(src, name="t.wall"):
    return lab_run.run_kv(WALL, [name, "t.b2"], {name: src.encode()})


def check_full(ok, bad, label, src):
    """tool == оракулу байт-в-байт (полный выход)"""
    want = lab_l2.compile_wall(src).encode()
    r = run_wall(src)
    good = (r.exit_code == 0 and r.files.get("t.b2") == want)
    print("[%s] %s" % ("OK " if good else "FAIL", label))
    if not good:
        got = r.files.get("t.b2", b"")
        print("   код=%s stdout=%r (tool %d, oracle %d байт)"
              % (r.exit_code, r.stdout[:60], len(got), len(want)))
        for i, (a, b) in enumerate(zip(got.split(b"\n"), want.split(b"\n"))):
            if a != b:
                print("   строка %d:\n     tool:   %r\n     oracle: %r"
                      % (i + 1, a[:90], b[:90]))
                break
    return ok + (1 if good else 0), bad + (0 if good else 1)


def main():
    ok = bad = 0

    # 1) якоря break/continue — tool == оракулу байт-в-байт
    for name, src in lab_l2_bc.BC_ANCHORS:
        ok, bad = check_full(ok, bad, name, src)
    big = lab_l2_bc.big_bc()
    ok, bad = check_full(ok, bad, "bc big (%d строк)" % big.count("\n"), big)

    # 2) якорь B2 (cases2) целиком: с E6.4c-3/3 (срез 3) цепочки && / ||
    #    компилируются — весь якорь == оракулу байт-в-байт
    #    (до срез 3 корректно отвергался ERR=FORMAT)
    b2src = lab_l2_cases2.CASES_FULL2[1][1]
    ok, bad = check_full(ok, bad, "bc B2 полный (цепочки — срез 3)", b2src)
    frag_cont = "M jmp $_w1 ; continue"
    frag_break = "M jmp $_w1e ; break"

    # ядро B2 без && || — фрагменты обязаны присутствовать
    core = next(s for n, s in lab_l2_bc.BC_ANCHORS
                if n.startswith("bc_B2_ядро"))
    r = run_wall(core)
    got = r.files.get("t.b2", b"")
    good = (r.exit_code == 0 and frag_cont.encode() in got and
            frag_break.encode() in got)
    print("[%s] bc фрагменты B2: %r / %r" % ("OK " if good else "FAIL",
                                             frag_cont, frag_break))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 3) регресс дефекта №15 (bstk 3072x32): комментарий обратного прыжка
    d15 = lab_l2_cases2.CASES_FULL2[1][1].replace("while i < 6 && s < 100",
                                                  "while i < 6").replace(
        "if i == 5 || s == 999", "if i == 5")
    ok, bad = check_full(ok, bad, "дефект №15: if в while (комментарий jmp)", d15)

    # 4) заголовок v2 у программы с break/continue (флаг в p1s_brk)
    h = (run_wall(lab_l2_bc.BC_ANCHORS[0][1]).files.get("t.b2",
                                                         b"")).split(b"\n")[0]
    oracle_h = lab_l2.compile_wall(lab_l2_bc.BC_ANCHORS[0][1]
                                    ).encode().split(b"\n")[0]
    good = h == oracle_h and b"WALL v2" in h
    print("[%s] заголовок v2 у программы с break/continue"
          % ("OK " if good else "FAIL"))
    if not good:
        print("   %r" % h[:60])
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 5) v1-программа остаётся v1 (обратная совместимость)
    src_v1 = "func main\n    var i\n    i = 0\n    while i < 3\n        i = i + 1\n    end\nend\n"
    h1 = (run_wall(src_v1).files.get("t.b2", b"")).split(b"\n")[0]
    good = b"WALL v1" in h1
    print("[%s] заголовок v1 у чистой v1-программы" % ("OK " if good else "FAIL"))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 6) ошибки: строки из оракула (ERRORS2: вне while)
    badl = []
    for name, src, line in BC_ERRORS:
        r = run_wall(src)
        want_out = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % line).encode()
        if not (r.exit_code == 6 and r.stdout == want_out):
            badl.append((name, r.exit_code, line))
    good = not badl
    print("[%s] bc отвержение (%d)" % ("OK " if good else "FAIL",
                                       len(BC_ERRORS)))
    for b in badl[:5]:
        print("   %s: код=%s (строка %s)" % b)
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 7) «break 1» — хвост после ключевого слова отвергается
    name, src_tail = lab_l2_bc.BC_BREAK_TAIL
    try:
        lab_l2.compile_wall(src_tail)
        line = None
    except lab_l2.WallError as e:
        line = e.line
    r = run_wall(src_tail)
    good = line is not None and r.exit_code == 6 and \
        r.stdout == ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % line).encode()
    print("[%s] bc хвост «break 1» отвергнут (строка %s)"
          % ("OK " if good else "FAIL", line))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 8) все M-строки выхода кодируются enc+brick (инвариант T-E6-34)
    r = run_wall(big, "a.wall")
    b2 = r.files.get("t.b2", b"")
    r2 = lab_run.run_kv(ENC, ["a.b2", "a.brick"], {"a.b2": b2})
    r3 = lab_run.run_kv(BRICK, ["a.brick", "a.bin"],
                        {"a.brick": r2.files.get("a.brick", b"")})
    good = (r2.exit_code == 0 and r3.exit_code == 0)
    print("[%s] bc выход кодируется enc+brick" % ("OK " if good else "FAIL"))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 9) полный круг DEMO_BC -> EXE -> эмуляция "U-BC-OK 25"
    h = {"d.wall": lab_l2_bc.DEMO_BC.encode()}
    r1 = lab_run.run_kv(WALL, ["d.wall", "d.b2"], h)
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(ENC, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(BRICK, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = lab_l2_bc.DEMO_BC_PEG.encode()
    r4 = lab_run.run_kv(PEGEN, ["d.bin", "d.peg", "d.exe"], h)
    demo = r4.files.get("d.exe", b"")
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, demo)
        os.close(fd)
        r5 = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    good = (r1.exit_code == 0 and r5.stdout == b"U-BC-OK 25\r\n" and
            r5.exit_code == 0)
    print("[%s] полный круг bc (U-BC-OK 25)" % ("OK " if good else "FAIL"))
    if not good:
        print("   stdout=%r код=%s" % (r5.stdout[:60], r5.exit_code))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    print("\nИТОГ: %d OK / %d FAIL" % (ok, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
