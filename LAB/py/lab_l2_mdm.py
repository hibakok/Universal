"""lab_l2_mdm.py — эталоны среза 1 WALL v2: операторы * / % (E6.4c-3/1).

Паспорт файла: LAB/py/lab_l2_mdm.py | слой: внешний инструмент |
роль: якоря/ошибки/демо среза 1 (умножение, деление, остаток) для
батареи (секция 11, lab_t_wall3.py) и dev-теста LAB/ai/wall_test_v2.py.
Данные перенесены из wall_test_v2.py без изменений (E6.4c-3/3b):
единый источник для CI и dev-прогонов, дублирование исключено.
"""

# ---- якоря срез 1: только v1-конструкции + * / % --------------------
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
