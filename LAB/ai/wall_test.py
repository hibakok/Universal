"""test_wall.py — проверка wall.exe против оракула (sandbox-инструмент).

Вход:  собранный KERNEL/L2-WALL/wall.exe.
Выход: отчёт: якоря, отвержение, полный круг, справка.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "py"))
import lab_l2                       # noqa: E402
import lab_l2_cases                 # noqa: E402
import lab_l2_prog                  # noqa: E402
import lab_run                      # noqa: E402

WALL = "/home/z/my-project/Universal/KERNEL/L2-WALL/wall.exe"


def run_wall(src, name="t.wall"):
    return lab_run.run_kv(WALL, [name, "t.b2"], {name: src.encode()})


def main():
    ok_n = bad_n = 0

    # 1) справка
    r = lab_run.run_kv(WALL, [], {})
    good = (r.stdout == b"U-L2-WALL CMDS: WALL <SRC.WALL> <OUT.B2>\r\n" and
            r.exit_code == 2)
    print("[%s] справка" % ("OK" if good else "FAIL"), r.stdout[:50],
          r.exit_code)
    ok_n, bad_n = ok_n + good, bad_n + (not good)

    # 2) полные якоря
    for name, src, want in lab_l2_cases.CASES_FULL:
        try:
            oracle = lab_l2.compile_wall(src).encode()
        except Exception as e:                      # noqa: BLE001
            oracle = ("ERR:" + str(e)).encode()
        r = run_wall(src)
        good = (r.exit_code == 0 and r.files.get("t.b2") == oracle and
                oracle and not oracle.startswith(b"ERR:"))
        print("[%s] якорь %s" % ("OK" if good else "FAIL", name),
              "" if good else "код=%s шагов=%d" % (r.exit_code, r.steps))
        if not good:
            got = r.files.get("t.b2", b"")
            print("   stdout=%r" % r.stdout[:80])
            for i, (a, b) in enumerate(zip(got.split(b"\n"),
                                           oracle.split(b"\n"))):
                if a != b:
                    print("   строка %d:\n     got:    %r\n     oracle: %r"
                          % (i + 1, a[:90], b[:90]))
                    break
        ok_n, bad_n = ok_n + good, bad_n + (not good)

    # 3) фрагментные якоря
    for name, src, frag in lab_l2_cases.CASES_FRAG:
        try:
            oracle = lab_l2.compile_wall(src).encode()
        except Exception as e:                      # noqa: BLE001
            oracle = b""
        r = run_wall(src)
        good = (r.exit_code == 0 and frag.encode() in
                (r.files.get("t.b2") or b""))
        print("[%s] фрагмент %s" % ("OK" if good else "FAIL", name))
        if not good:
            got = r.files.get("t.b2", b"") or b""
            print("   код=%s stdout=%r" % (r.exit_code, r.stdout[:60]))
            for i, (a, b) in enumerate(zip(got.split(b"\n"),
                                           oracle.split(b"\n"))):
                if a != b:
                    print("   строка %d:\n     got:    %r\n     oracle: %r"
                          % (i + 1, a[:90], b[:90]))
                    break
            else:
                print("   длины: got=%d oracle=%d" % (len(got),
                                                      len(oracle)))
        ok_n, bad_n = ok_n + good, bad_n + (not good)

    # 4) отвержение (26 ошибок)
    bad = []
    for name, src, line in lab_l2_prog.ERRORS:
        r = run_wall(src)
        want = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % line).encode()
        if not (r.exit_code == 6 and r.stdout == want):
            bad.append((name, r.exit_code, r.stdout[:40], line))
    good = not bad
    print("[%s] отвержение (%d/%d)" % ("OK" if good else "FAIL",
                                       len(lab_l2_prog.ERRORS) - len(bad),
                                       len(lab_l2_prog.ERRORS)))
    for b in bad[:6]:
        print("   %s: код=%s stdout=%r (ожидалась строка %d)" % b)
    ok_n, bad_n = ok_n + good, bad_n + (not good)

    print("\nИТОГ: %d OK / %d FAIL" % (ok_n, bad_n))
    return 1 if bad_n else 0


if __name__ == "__main__":
    sys.exit(main())
