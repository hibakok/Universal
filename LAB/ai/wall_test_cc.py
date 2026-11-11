"""wall_test_cc.py — dev-тест wall.exe v2 (E6.4c-3, срез 3: цепочки && / ||).

Паспорт файла: LAB/ai/wall_test_cc.py | слой: внешний инструмент |
роль: сверка wall.exe с оракулом LAB/py/lab_l2* на цепочках условий
&& / || (E6.4c-3/3: лексер lt_and/lt_or K2-L001, терминаторы chain_count
K2-P009, p_cond K2-P018 — цикл дизъюнктов/конъюнктов + guard-эмиттер,
E036/E037/E038 в wall_pg.b2) + якоря B2/F14/F16 из lab_l2_cases2 +
ошибки (хвосты && / ||, одиночные & / |, скобки) + big_cc + полный
круг DEMO_CC до эмуляции «U-CC-OK 31».
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
import lab_pegen          # noqa: E402
import lab_run            # noqa: E402

WALL = os.path.join(UNI, "KERNEL", "L2-WALL", "wall.exe")
ENC = os.path.join(UNI, "KERNEL", "L1-ENC", "enc.exe")
BRICK = os.path.join(UNI, "KERNEL", "L1-BRICK", "brick.exe")
PEGEN = os.path.join(UNI, "KERNEL", "L0-PEGEN", "pegen.exe")

# ---- якоря среза 3: цепочки && / || во всех формах (без массивов — срез 4)
CC_ANCHORS = [
    ("cc_and_цепочка m=1 (без d/t-меток)", """\
func main
    var a
    var b
    var c
    a = 1
    b = 2
    c = 3
    while a < b && b < c && c < 10
        a = a + 1
    end
end
"""),
    ("cc_or_в_if_без_else", """\
func main
    var a
    a = 1
    if a == 1 || a == 2
        a = 0
    end
end
"""),
    ("cc_or_в_if_с_else (lfalse = _if<k>)", """\
func main
    var a
    a = 1
    if a == 1 || a == 2
        a = 0
    else
        a = 9
    end
end
"""),
    ("cc_m3_три_дизъюнкта (d2 d3 t)", """\
func main
    var a
    a = 1
    if a == 1 || a == 2 || a == 3
        a = 0
    end
end
"""),
    ("cc_смешанное a&&b || c&&d", """\
func main
    var a
    var b
    var c
    var d
    a = 1
    b = 2
    c = 3
    d = 4
    if a < b && b < c || c > d && d > 100
        a = 0
    end
end
"""),
    ("cc_глубокие_операнды (maxd=2)", """\
func main
    var a
    var b
    var c
    var d
    var e
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    if a + b < c * d && d - 1 < e / 2
        a = 0
    end
end
"""),
    ("cc_вызовы_в_операндах (maxc)", """\
func f(x)
    return x + 1
end
func g(x)
    return x * 2
end
func main
    var a
    var b
    a = 1
    b = 2
    if f(a) < 3 && g(b) < 4
        a = 0
    end
end
"""),
    ("cc_md_в_цепочке (терминатор chain_count)", """\
func main
    var i
    var s
    i = 0
    s = 0
    while i < 20
        if i % 2 == 0 && i <= 8
            s = s + i
        end
        i = i + 1
    end
end
"""),
    ("cc_цепочки_и_break_continue", """\
func main
    var i
    var s
    i = 0
    s = 0
    while i < 30 && s < 500
        i = i + 1
        if i % 3 == 0 || i > 25
            continue
        end
        if s > 40 || i == 20
            break
        end
        s = s + i
    end
end
"""),
    ("cc_вложенные_условия_с_цепочками", """\
func main
    var a
    var b
    a = 0
    while a < 5 || a > 100
        b = 0
        while b < 4 && a < 4
            b = b + 1
            if b == 2 || a == 3
                b = b + 10
            end
        end
        a = a + 1
    end
end
"""),
    ("cc_все_сравнения_в_цепочках", """\
func main
    var a
    var b
    a = 1
    b = 2
    if a == 1 && b != 3
        a = a + 1
    end
    if a < 5 && b <= 5 && a >= 1 && b > 0
        a = a + 1
    end
    if a != 1 || b == 999
        a = 0
    end
end
"""),
]

# ---- ошибки: строки берутся из оракула (литералы — короче программ)
CC_ERRORS = [
    ("хвост &&", "func main\n    if 1 < 2 &&\n        return\n    end\nend\n"),
    ("хвост ||", "func main\n    if 1 < 2 ||\n        return\n    end\nend\n"),
    ("&& в начале условия", "func main\n    if && 1 < 2\n        return\n    end\nend\n"),
    ("|| в начале условия", "func main\n    if || 1 < 2\n        return\n    end\nend\n"),
    ("&& в выражении", "func main\n    var a\n    a = 0\n    a = a && 1\nend\n"),
    ("одиночный & между сравнениями", "func main\n    if 1 < 2 & 3 > 4\n        return\n    end\nend\n"),
    ("одиночный | между сравнениями", "func main\n    if 1 < 2 | 3 > 4\n        return\n    end\nend\n"),
    ("&& без сравнения справа", "func main\n    if 1 < 2 && 3\n        return\n    end\nend\n"),
    ("скобки вокруг сравнения", "func main\n    if (1 < 2)\n        return\n    end\nend\n"),
    ("&& && подряд", "func main\n    if 1 < 2 && && 2 > 1\n        return\n    end\nend\n"),
]

DEMO_CC = """\
; UNIVERSAL / WALL v2 / демонстрация цепочек && / || (E6.4c-3/3).
; Печатает "U-CC-OK 31": s = 0+2+4+6+8 = 20 (i%2==0 && i<=8),
; +2 (if s == 6 || s == 20), i: 30 -> 27 (while i > 27 || s > 100),
; s = 22 + 27 = 49 = 0x31.
ext GetStdHandle
ext WriteFile
ext ExitProcess

str msg = 'U-CC-OK '

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
    var i
    var s
    var h
    i = 0
    s = 0
    while i < 30
        if i % 2 == 0 && i <= 8
            s = s + i
        end
        i = i + 1
    end
    if s == 6 || s == 20
        s = s + 2
    else
        s = s - 1000
    end
    while i > 27 || s > 100
        i = i - 1
    end
    s = s + i
    h = GetStdHandle(-11)
    WriteFile(h, msg, len(msg), &out, 0)
    setb(&out, 0, hexnib(s >> 4))
    setb(&out, 1, hexnib(s & 15))
    setb(&out, 2, 13)
    setb(&out, 3, 10)
    WriteFile(h, &out, 4, &out, 0)
    ExitProcess(0)
end
"""

DEMO_CC_PEG = """\
; UNIVERSAL / PEG v1 / обёртка WALL v2 (SPEC/11)
!module ccdemo
!entry 1200
!idata 1000 28
!iat 1028 48
!stackcom 4000
!heapcom 4000
"""


def big_cc(n=256):
    """детерминированный большой исходник: цепочки && / || во всех позициях"""
    ls = ["func main", "    var i", "    var s", "    var t",
          "    i = 0", "    s = 0", "    t = 0"]
    k = 0
    while len(ls) < n - 4:
        k += 1
        ls.append("    while i < %d && s < %d" % (k % 40 + 10, k % 900 + 100))
        ls.append("        i = i + 1")
        if k % 4 == 0:
            ls.append("        if i == %d || t > %d" % (k % 30 + 3, k % 500 + 50))
            ls.append("            t = t + 2")
            ls.append("        end")
        if k % 6 == 0:
            ls.append("        if i > %d && s > %d" % (k % 25 + 5, k % 700 + 30))
            ls.append("            continue")
            ls.append("        end")
        if k % 10 == 0:
            ls.append("        if s == %d || s == %d || s == %d"
                      % (k, k + 1, k + 2))
            ls.append("            break")
            ls.append("        end")
        ls.append("        s = s + i % 7")
        ls.append("    end")
        if k % 8 == 0:
            ls.append("    if i > %d || t > %d" % (k % 60 + 20, k % 400 + 10))
            ls.append("        i = i - 1")
            ls.append("    end")
    ls.append("    s = s + i + t")
    ls.append("end")
    return "\n".join(ls) + "\n"


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
    for name, src in CC_ANCHORS:
        ok, bad = check_full(ok, bad, name, src)
    big = big_cc()
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
    h = (run_wall(CC_ANCHORS[0][1]).files.get("t.b2", b"")).split(b"\n")[0]
    oracle_h = lab_l2.compile_wall(CC_ANCHORS[0][1]).encode().split(b"\n")[0]
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
    for name, src in CC_ERRORS:
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
                                       len(CC_ERRORS)))
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
    h = {"d.wall": DEMO_CC.encode()}
    r1 = lab_run.run_kv(WALL, ["d.wall", "d.b2"], h)
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(ENC, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(BRICK, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = DEMO_CC_PEG.encode()
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
