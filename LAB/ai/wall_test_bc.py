"""wall_test_bc.py — dev-тест wall.exe v2 (E6.4c-3, срез 2: break/continue).

Паспорт файла: LAB/ai/wall_test_bc.py | слой: внешний инструмент |
роль: сверка wall.exe с оракулом LAB/py/lab_l2* на конструкциях
break/continue (E6.4c-3/2: kwtab 14, p1s_brk K2-S00E, p2s_break/
p2s_continue K2-Y00C) + регресс дефекта №15 (bstk 3072x32: if поверх
while больше не затирает lineidx объемлющего while — комментарий
обратного прыжка) + якорь B2-якорь-фрагменты + ошибки ERRORS2
(break/continue вне while) + полный круг DEMO_BC до эмуляции
«U-BC-OK 25». Запуск: python3 LAB/ai/wall_test_bc.py.
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
import lab_l2_prog        # noqa: E402
import lab_pegen          # noqa: E402
import lab_run            # noqa: E402

WALL = os.path.join(UNI, "KERNEL", "L2-WALL", "wall.exe")
ENC = os.path.join(UNI, "KERNEL", "L1-ENC", "enc.exe")
BRICK = os.path.join(UNI, "KERNEL", "L1-BRICK", "brick.exe")
PEGEN = os.path.join(UNI, "KERNEL", "L0-PEGEN", "pegen.exe")

# ---- якоря среза 2: v1-конструкции + break/continue (без && || массивов)
BC_ANCHORS = [
    ("bc_basic", """\
func main
    var i
    var s
    i = 0
    s = 0
    while i < 10
        i = i + 1
        if i == 5
            break
        end
        s = s + i
    end
end
"""),
    ("bc_continue", """\
func main
    var i
    var s
    i = 0
    s = 0
    while i < 6
        i = i + 1
        if i == 3
            continue
        end
        s = s + i
    end
end
"""),
    ("bc_ближайший while (вложенность)", """\
func main
    var a
    var b
    a = 0
    while a < 3
        b = 0
        while b < 5
            b = b + 1
            if b == 2
                continue
            end
            if b == 4
                break
            end
        end
        if a == 2
            break
        end
        a = a + 1
    end
end
"""),
    ("bc_if_else_вокруг", """\
func main
    var i
    var s
    i = 0
    s = 0
    while i < 20
        i = i + 1
        if i == 4
            continue
        else
            s = s + i
        end
        if s > 30
            break
        end
    end
end
"""),
    ("bc_return_в_цикле", """\
func f(n)
    var i
    i = 0
    while i < 100
        i = i + 1
        if i == n
            return i
        end
        if i * 2 > n + 7
            break
        end
    end
    return 0 - 1
end
func main
    var a
    var b
    a = f(5)
    b = f(3 * 10)
end
"""),
    ("bc_B2_ядро (if i==3/if i==5)", """\
func main
    var i
    var s
    i = 0
    s = 0
    while i < 6
        i = i + 1
        if i == 3
            continue
        end
        if i == 5
            break
        end
        s = s + i
    end
end
"""),
    ("bc_с_операторами_среза1", """\
func main
    var i
    var s
    i = 7 * 2
    s = 0
    while i > 0
        i = i - 3
        if i % 2 == 1
            continue
        end
        if i / 10 > 0
            break
        end
        s = s + i
    end
end
"""),
]

# ---- ошибки: строки из оракула (ERRORS2, только break/continue) ----
BC_ERRORS = [e for e in lab_l2_prog.ERRORS2
             if e[0] in ("break вне цикла", "continue вне цикла",
                         "break в if вне while")]

DEMO_BC = """\
; UNIVERSAL / WALL v2 / демонстрация break/continue (E6.4c-3/2).
; Печатает "U-BC-OK 25": сумма без кратных 3, break при s > 30:
; s = 1+2+4+5+7+8+10 = 37 = 0x25.
ext GetStdHandle
ext WriteFile
ext ExitProcess

str msg = 'U-BC-OK '

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
    while i < 20
        i = i + 1
        if i % 3 == 0
            continue
        end
        if s > 30
            break
        end
        s = s + i
    end
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

DEMO_BC_PEG = """\
; UNIVERSAL / PEG v1 / обёртка WALL v2 (SPEC/11)
!module bcdemo
!entry 1200
!idata 1000 28
!iat 1028 48
!stackcom 4000
!heapcom 4000
"""


def big_bc(n=220):
    """детерминированный большой исходник: break/continue во всех позициях"""
    ls = ["func main", "    var i", "    var s", "    i = 0", "    s = 0"]
    k = 0
    while len(ls) < n - 8:
        k += 1
        ls.append("    while i < %d + %d" % (k % 50 + 10, k % 7))
        ls.append("        i = i + 1")
        if k % 5 == 0:
            ls.append("        if i == %d" % (k % 40 + 3))
            ls.append("            continue")
            ls.append("        end")
        if k % 9 == 0:
            ls.append("        if i > %d" % (k % 30 + 35))
            ls.append("            break")
            ls.append("        end")
        ls.append("        s = s + i % 5")
        ls.append("    end")
        if k % 13 == 0:
            ls.append("    if s > %d" % (k * 100 % 900 + 50))
            ls.append("        s = s / 2")
            ls.append("    end")
        if k % 11 == 0:
            ls.append("    while s > 900")
            ls.append("        s = s - 100")
            ls.append("        if s < 0")
            ls.append("            break")
            ls.append("        end")
            ls.append("        if s > 950")
            ls.append("            continue")
            ls.append("        end")
            ls.append("    end")
        if k % 17 == 0:
            ls.append("    while i > 400")
            ls.append("        i = i - 1")
            ls.append("        if i == 401")
            ls.append("            continue")
            ls.append("        end")
            ls.append("        if i == 400")
            ls.append("            break")
            ls.append("        end")
            ls.append("    end")
    ls.append("    s = s + i")
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

    # 1) якоря break/continue — tool == оракулу байт-в-байт
    for name, src in BC_ANCHORS:
        ok, bad = check_full(ok, bad, name, src)
    big = big_bc()
    ok, bad = check_full(ok, bad, "bc big (%d строк)" % big.count("\n"), big)

    # 2) фрагменты якоря B2 (cases2): часть с break/continue
    b2src, b2frag = lab_l2_cases2.CASES_FULL2[1][1], None
    frag_cont = "M jmp $_w1 ; continue"
    frag_break = "M jmp $_w1e ; break"
    want = lab_l2.compile_wall(b2src).encode()  # && || ещё не поддержаны
    r = run_wall(b2src)
    good = r.exit_code == 6  # ERR=FORMAT до среза 3 (&& вне поддержки)
    print("[%s] B2 (&& ||) корректно отвергнут до среза 3"
          % ("OK " if good else "FAIL"))
    ok, bad = ok + (1 if good else 0), bad + (0 if good else 1)

    # ядро B2 без && || — фрагменты обязаны присутствовать
    core = BC_ANCHORS[5][1]
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
    h = (run_wall(BC_ANCHORS[0][1]).files.get("t.b2", b"")).split(b"\n")[0]
    oracle_h = lab_l2.compile_wall(BC_ANCHORS[0][1]).encode().split(b"\n")[0]
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
    src_tail = "func main\n    var i\n    i = 0\n    while i < 3\n        break 1\n    end\nend\n"
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
    h = {"d.wall": DEMO_BC.encode()}
    r1 = lab_run.run_kv(WALL, ["d.wall", "d.b2"], h)
    h["d.b2"] = r1.files.get("d.b2", b"")
    r2 = lab_run.run_kv(ENC, ["d.b2", "d.brick"], h)
    h["d.brick"] = r2.files.get("d.brick", b"")
    r3 = lab_run.run_kv(BRICK, ["d.brick", "d.bin"], h)
    h["d.bin"] = r3.files.get("d.bin", b"")
    h["d.peg"] = DEMO_BC_PEG.encode()
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
