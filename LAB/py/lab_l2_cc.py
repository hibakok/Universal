"""lab_l2_cc.py — эталоны срез 3 WALL v2: цепочки && / || (E6.4c-3/3).

Паспорт файла: LAB/py/lab_l2_cc.py | слой: внешний инструмент |
роль: якоря/ошибки/демо срез 3 (цепочки условий с short-circuit) для
батареи (секция 11, lab_t_wall3.py) и dev-теста LAB/ai/wall_test_cc.py.
Данные перенесены из wall_test_cc.py без изменений (E6.4c-3/3b).
"""

# ---- якоря срез 3: цепочки && / || во всех формах (без массивов — срез 4)
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
