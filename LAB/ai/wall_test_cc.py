"""wall_test_cc.py — dev-тест wall.exe v2 (E6.4c-3, срез 3: цепочки && / ||).

Паспорт файла: LAB/ai/wall_test_cc.py | слой: внешний инструмент |
роль: быстрый dev-прогон срез 3 (цепочки условий && / || с
short-circuit) при работе над wall.exe: сверка с оракулом
LAB/py/lab_l2* + якоря B2/F14/F16 из lab_l2_cases2 + ошибки + полный
круг DEMO_CC. Эталоны срез 3 — в LAB/py/lab_l2_cc.py (с E6.4c-3/3b
общий источник с батареей, секция 11 = T-E6-37..45).
Запуск: python3 LAB/ai/wall_test_cc.py.
"""
import os
import sys
import tempfile

UNI = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(UNI, "LAB", "py"))
import lab_brick          # noqa: E402
import lab_enc            # noqa: E402
import lab_l2             # noqa: E402
import lab_l2_cases2      # noqa: E402
import lab_l2_cc          # noqa: E402
import lab_pegen          # noqa: E402
import lab_run            # noqa: E402

WALL = os.path.join(UNI, "KERNEL", "L2-WALL", "wall.exe")
ENC = os.path.join(UNI, "KERNEL", "L1-ENC", "enc.exe")
BRICK = os.path.join(UNI, "KERNEL", "L1-BRICK", "brick.exe")
PEGEN = os.path.join(UNI, "KERNEL", "L0-PEGEN", "pegen.exe")


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

    # 1) якоря цепочек — tool == оракулу байт-в-байт
    for name, src in lab_l2_cc.CC_ANCHORS:
        ok, bad = check_full(ok, bad, name, src)
    big = lab_l2_cc.big_cc()
    ok, bad = check_full(ok, bad, "cc big (%d строк)" % big.count("\n"), big)

    # 2) полный якорь B2 (cases2): цепочки + break/continue — == оракулу
    b2src = lab_l2_cases2.CASES_FULL2[1][1]
    ok, bad = check_full(ok, bad, "cc B2 полный (cases2, && || + break)", b2src)

    # 3) фрагментные якоря F14/F16 (cases2)
    for want_name, src, frag in lab_l2_cases2.CASES_FRAG2:
        if not ("F14" in want_name or "F16" in want_name):
            continue
        r = run_wall(src)
        good = (r.exit_code == 0 and frag.encode() in r.files.get("t.b2", b""))
        print("[%s] cc фрагмент %s" % ("OK " if good else "FAIL", want_name))
        if not good:
            print("   код=%s stdout=%r" % (r.exit_code, r.stdout[:60]))
        ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 4) заголовок v2 у программы с цепочками (флаг в p_cond)
    h = (run_wall(lab_l2_cc.CC_ANCHORS[0][1]).files.get("t.b2",
                                                         b"")).split(b"\n")[0]
    oracle_h = lab_l2.compile_wall(lab_l2_cc.CC_ANCHORS[0][1]
                                    ).encode().split(b"\n")[0]
    good = h == oracle_h and b"WALL v2" in h
    print("[%s] заголовок v2 у программы с цепочками"
          % ("OK " if good else "FAIL"))
    if not good:
        print("   %r" % h[:60])
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 5) v1-программа остаётся v1 (обратная совместимость)
    src_v1 = ("func main\n    var i\n    i = 0\n    while i < 3\n"
              "        i = i + 1\n    end\nend\n")
    h1 = (run_wall(src_v1).files.get("t.b2", b"")).split(b"\n")[0]
    good = b"WALL v1" in h1
    print("[%s] заголовок v1 у чистой v1-программы" % ("OK " if good else "FAIL"))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 6) ошибки: строки из оракула (хвосты && / || и пр.)
    badl = []
    for name, src in lab_l2_cc.CC_ERRORS:
        try:
            lab_l2.compile_wall(src)
            line = None
        except lab_l2.WallError as e:
            line = e.line
        r = run_wall(src)
        if line is None:
            badl.append((name, "оракул принял", None))
            continue
        want_out = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % line).encode()
        if not (r.exit_code == 6 and r.stdout == want_out):
            badl.append((name, r.exit_code, line))
    good = not badl
    print("[%s] cc отвержение (%d)" % ("OK " if good else "FAIL",
                                       len(lab_l2_cc.CC_ERRORS)))
    for b in badl[:5]:
        print("   %s: код=%s (строка %s)" % b)
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 7) все M-строки выхода кодируются enc+brick (инвариант T-E6-34)
    r = run_wall(big, "a.wall")
    b2 = r.files.get("t.b2", b"")
    r2 = lab_run.run_kv(ENC, ["a.b2", "a.brick"], {"a.b2": b2})
    r3 = lab_run.run_kv(BRICK, ["a.brick", "a.bin"],
                        {"a.brick": r2.files.get("a.brick", b"")})
    good = (r2.exit_code == 0 and r3.exit_code == 0)
    print("[%s] cc выход кодируется enc+brick" % ("OK " if good else "FAIL"))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 8) полный круг DEMO_CC -> EXE -> эмуляция "U-CC-OK 31"
    h = {"d.wall": lab_l2_cc.DEMO_CC.encode()}
    r1 = lab_run.run_kv(WALL, ["d.wall", "d.b2"], h)
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(ENC, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(BRICK, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = lab_l2_cc.DEMO_CC_PEG.encode()
    r4 = lab_run.run_kv(PEGEN, ["d.bin", "d.peg", "d.exe"], h)
    demo = r4.files.get("d.exe", b"")
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, demo)
        os.close(fd)
        r5 = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    good = (r1.exit_code == 0 and r5.stdout == b"U-CC-OK 31\r\n" and
            r5.exit_code == 0)
    print("[%s] полный круг cc (U-CC-OK 31)" % ("OK " if good else "FAIL"))
    if not good:
        print("   stdout=%r код=%s" % (r5.stdout[:60], r5.exit_code))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    print("\nИТОГ: %d OK / %d FAIL" % (ok, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
