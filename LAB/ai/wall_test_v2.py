"""wall_test_v2.py — dev-тест wall.exe v2 (E6.4c-3, срез 1: * / %).

Паспорт файла: LAB/ai/wall_test_v2.py | слой: внешний инструмент |
роль: сверка wall.exe с оракулом LAB/py/lab_l2* на конструкциях
операторов * / % (E6.4c-3/1) + регресс v1 + исправление дефекта
chain_count (сравнения как терминаторы) + заголовки v1/v2 + полный
круг DEMO_MDM до эмуляции. Запуск: python3 LAB/ai/wall_test_v2.py.
"""
import os
import sys
import tempfile

UNI = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(UNI, "LAB", "py"))
import lab_brick          # noqa: E402
import lab_enc            # noqa: E402
import lab_l2             # noqa: E402
import lab_l2_cases       # noqa: E402
import lab_l2_cases2      # noqa: E402
import lab_l2_prog        # noqa: E402
import lab_pegen          # noqa: E402
import lab_run            # noqa: E402

WALL = os.path.join(UNI, "KERNEL", "L2-WALL", "wall.exe")
ENC = os.path.join(UNI, "KERNEL", "L1-ENC", "enc.exe")
BRICK = os.path.join(UNI, "KERNEL", "L1-BRICK", "brick.exe")
PEGEN = os.path.join(UNI, "KERNEL", "L0-PEGEN", "pegen.exe")

# ---- якоря среза 1: только v1-конструкции + * / % --------------------
MDM_ANCHORS = [
    ("mdm_basic", """\
func main
    var x
    var y
    x = 2 * 3 + 4 * 5
    x = 1 + 2 * 3
    x = 2 * (3 + 4)
    x = 100 / 7
    x = 100 % 7
    x = 2 & 3 * 3
    x = 1 << 2 * 2
    x = 0 - 7 * 2
    y = x * x + x / 2 % 3
end
"""),
    ("mdm_positions", """\
func f(a, b)
    return a * b + a % b
end
func main
    var x
    var s
    x = f(10, 3) / 4
    s = 0
    while x * 2 < 20 + 1
        x = x + 5 % 3
    end
    if x / 2 == 3 + 3
        setb(&x, 0, 1 * 2)
    end
    s = x
end
"""),
    ("mdm_neg", """\
func main
    var x
    var y
    var z
    x = 0 - 43
    y = x / 10
    z = x % 10
    x = y * 3 + z
end
"""),
    ("mdm_chain", """\
func main
    var x
    var y
    x = 1 * 2 * 3 * 4 * 5 / 6 % 7
    y = x / 2 / 3 * 4 % 5 * 6
    x = (y % 100 + 1) * (x + 2) / 3
end
"""),
    ("mdm_f13", """\
func main
    var x
    x = 2 * 3 + 4 * 5
    x = 1 + 2 * 3
    x = 2 * (3 + 4)
end
"""),
    ("cond_arith", """\
func main
    var x
    x = 0
    if 1 + 2 == 2 + 1
        x = 5
    end
end
"""),
    ("cond_shift", """\
func main
    var x
    x = 0
    if 1 << 2 == 2 << 1
        x = 5
    end
end
"""),
    ("while_arith", """\
func main
    var i
    var s
    i = 0
    s = 0
    while i + 1 < 5 + 1
        s = s + 2
        i = i + 1
    end
end
"""),
    ("mdm_conds", """\
func main
    var i
    var s
    i = 10
    s = 0
    while i % 3 == 1
        s = s + i
        i = i / 2
    end
    if s * 2 != 12 + 1
        s = s & 15
    end
end
"""),
]


def big_mdm(n=260):
    """детерминированный большой исходник с * / % повсюду"""
    ls = []
    ls.append("func main")
    ls.append("    var a")
    ls.append("    var b")
    ls.append("    a = 1")
    ls.append("    b = 2")
    k = 1
    while len(ls) < n - 6:
        ls.append("    a = a * %d + b %% %d" % (k % 17 + 1, k % 7 + 2))
        ls.append("    b = a / %d + b * %d" % (k % 5 + 1, k % 3 + 1))
        if k % 100 == 0:
            ls.append("    if a % 1000 < 500 + 1")
            ls.append("        a = a + 1")
            ls.append("    end")
        k += 1
    ls.append("    a = a + b")
    ls.append("end")
    return "\n".join(ls) + "\n"


# ---- ошибки: (имя, исходник); строка берётся из оракула ----------------
MDM_ERRORS = [
    ("хвост без операнда", "func main\n    var x\n    x = 6 *\nend\n"),
    ("оператор в начале", "func main\n    var x\n    x = * 5\nend\n"),
    ("двойной оператор", "func main\n    var x\n    x = 6 * * 5\nend\n"),
    ("% без операнда в аргументе",
     "func main\n    var x\n    x = len('ab') %\nend\n"),
    ("хвост / в возврате",
     "func f\n    return 10 /\nend\nfunc main\nend\n"),
]

DEMO_MDM = """\
; UNIVERSAL / WALL v2 / демонстрация операторов * / % (E6.4c-3/1).
; Печатает "U-MDM-OK 52": a=6*7=42; b=42/5=8; c=42%%5=2; v=8*10+2=82=0x52.
ext GetStdHandle
ext WriteFile
ext ExitProcess

str msg = 'U-MDM-OK '

var out

func hexnib(n)
    var t
    t = n & 15
    if t < 10
        t = t + 48
    else
        t = t + 55
    end
    return t
end

func main
    var a
    var b
    var c
    var v
    var h
    a = 6 * 7
    b = a / 5
    c = a % 5
    v = b * 10 + c
    h = GetStdHandle(-11)
    WriteFile(h, msg, len(msg), &out, 0)
    setb(&out, 0, hexnib(v >> 4))
    setb(&out, 1, hexnib(v & 15))
    setb(&out, 2, 13)
    setb(&out, 3, 10)
    WriteFile(h, &out, 4, &out, 0)
    ExitProcess(0)
end
"""

DEMO_MDM_PEG = """\
; UNIVERSAL / PEG v1 / обёртка WALL v2 (SPEC/11)
!module mdmdemo
!entry 1200
!idata 1000 28
!iat 1028 48
!stackcom 4000
!heapcom 4000
"""


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

    # 1) регресс v1: полные + фрагментные якоря (как T-E6-26, но здесь)
    for name, src, want in lab_l2_cases.CASES_FULL:
        ok, bad = check_full(ok, bad, "v1 %s" % name, src)
    for name, src, frag in lab_l2_cases.CASES_FRAG:
        want = lab_l2.compile_wall(src).encode()
        r = run_wall(src)
        good = (r.exit_code == 0 and frag.encode() in
                (r.files.get("t.b2") or b""))
        print("[%s] v1 фрагм. %s" % ("OK " if good else "FAIL", name))
        ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 2) отвержение v1 (26 ошибок)
    badl = []
    for name, src, line in lab_l2_prog.ERRORS:
        r = run_wall(src)
        want_out = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % line).encode()
        if not (r.exit_code == 6 and r.stdout == want_out):
            badl.append((name, r.exit_code, line))
    good = not badl
    print("[%s] v1 отвержение (%d)" % ("OK " if good else "FAIL",
                                       len(lab_l2_prog.ERRORS)))
    for b in badl[:5]:
        print("   %s: код=%s (ожидалась строка %d)" % b)
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 3) срез 1: якоря * / % — tool == оракулу
    for name, src in MDM_ANCHORS:
        ok, bad = check_full(ok, bad, "mdm %s" % name, src)
    big = big_mdm()
    ok, bad = check_full(ok, bad, "mdm big (%d строк)" % big.count("\n"), big)

    # 4) фрагментный якорь F13 из cases2 (только * / % + v1)
    for name, src, frag in lab_l2_cases2.CASES_FRAG2:
        if name != "F13 приоритет: * выше +, скобки":
            continue                      # остальные — массивы/&&: не срез 1
        want = lab_l2.compile_wall(src).encode()
        r = run_wall(src)
        good = (r.exit_code == 0 and frag.encode() in
                (r.files.get("t.b2") or b""))
        print("[%s] mdm %s" % ("OK " if good else "FAIL", name))
        ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 5) заголовки: v1-программа -> «WALL v1»; * / % -> «WALL v2»
    src_v1 = lab_l2_cases.CASES_FULL[0][1]
    out_v1 = run_wall(src_v1).files.get("t.b2", b"")
    h1 = out_v1.split(b"\n")[0] if out_v1 else b""
    good = h1 == b"; UNIVERSAL / WALL v1 / " \
        b"\xd1\x81\xd0\xb3\xd0\xb5\xd0\xbd\xd0\xb5\xd1\x80\xd0\xb8\xd1\x80" \
        b"\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbe \xd0\xba\xd0\xbe\xd0\xbc" \
        b"\xd0\xbf\xd0\xb8\xd0\xbb\xd1\x8f\xd1\x82\xd0\xbe\xd1\x80\xd0\xbe" \
        b"\xd0\xbc WALL (SPEC/11)"
    print("[%s] заголовок v1 у v1-программы" % ("OK " if good else "FAIL"))
    if not good:
        print("   %r" % h1[:60])
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    r = run_wall(MDM_ANCHORS[0][1])
    h2 = (r.files.get("t.b2") or b"").split(b"\n")[0]
    oracle_h2 = lab_l2.compile_wall(MDM_ANCHORS[0][1]).encode().split(b"\n")[0]
    good = h2 == oracle_h2 and b"WALL v2" in h2
    print("[%s] заголовок v2 у программы с * / %%" % ("OK " if good else "FAIL"))
    if not good:
        print("   %r" % h2[:60])
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 6) ошибки среза 1: строки из оракула
    badl = []
    for name, src in MDM_ERRORS:
        try:
            lab_l2.compile_wall(src)
            badl.append((name, "оракул принял", "-"))
            continue
        except lab_l2.WallError as e:
            line = e.line
        r = run_wall(src)
        want_out = ("U-L2-WALL ERR=FORMAT AT=%04X\r\n" % line).encode()
        if not (r.exit_code == 6 and r.stdout == want_out):
            badl.append((name, r.exit_code, line))
    good = not badl
    print("[%s] mdm отвержение (%d)" % ("OK " if good else "FAIL",
                                        len(MDM_ERRORS)))
    for b in badl[:5]:
        print("   %s: код=%s (строка %s)" % b)
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 7) все M-строки выхода кодируются enc (инвариант T-E6-34)
    r = run_wall(MDM_ANCHORS[0][1], "a.wall")
    b2 = r.files.get("t.b2", b"")
    r2 = lab_run.run_kv(ENC, ["a.b2", "a.brick"], {"a.b2": b2})
    r3 = lab_run.run_kv(BRICK, ["a.brick", "a.bin"],
                        {"a.brick": r2.files.get("a.brick", b"")})
    good = (r2.exit_code == 0 and r3.exit_code == 0)
    print("[%s] mdm выход кодируется enc+brick" % ("OK " if good else "FAIL"))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # 8) полный круг DEMO_MDM -> EXE -> эмуляция "U-MDM-OK 52"
    h = {"d.wall": DEMO_MDM.encode()}
    r1 = lab_run.run_kv(WALL, ["d.wall", "d.b2"], h)
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(ENC, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(BRICK, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = DEMO_MDM_PEG.encode()
    r4 = lab_run.run_kv(PEGEN, ["d.bin", "d.peg", "d.exe"], h)
    demo = r4.files.get("d.exe", b"")
    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, demo)
        os.close(fd)
        r5 = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)
    good = (r1.exit_code == 0 and r5.stdout == b"U-MDM-OK 52\r\n" and
            r5.exit_code == 0)
    print("[%s] полный круг mdm (U-MDM-OK 52)" % ("OK " if good else "FAIL"))
    if not good:
        print("   stdout=%r код=%s" % (r5.stdout[:60], r5.exit_code))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    print("\nИТОГ: %d OK / %d FAIL" % (ok, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
