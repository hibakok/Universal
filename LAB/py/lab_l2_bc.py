"""lab_l2_bc.py — эталоны срез 2 WALL v2: break/continue (E6.4c-3/2).

Паспорт файла: LAB/py/lab_l2_bc.py | слой: внешний инструмент |
роль: якоря/демо срез 2 (break/continue в while) для батареи (секция
11, lab_t_wall3.py) и dev-теста LAB/ai/wall_test_bc.py. Данные
перенесены из wall_test_bc.py без изменений (E6.4c-3/3b). Ошибки
среза 2 НЕ хранятся здесь: они выводятся фильтром BC_ERR_NAMES из
общего списка ERRORS2 (LAB/py/lab_l2_prog.py) — единый источник.
"""

# ---- якоря срез 2: v1-конструкции + break/continue (без && || массивов)
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
    ("bc_с_операторами_срез1", """\
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

# имена записей ERRORS2 (lab_l2_prog), относящихся к break/continue;
# строки ошибок берутся из общего списка — без дублирования данных
BC_ERR_NAMES = ("break вне цикла", "continue вне цикла",
                "break в if вне while")

# «break 1» — хвост после ключевого слова; строка — из оракула
BC_BREAK_TAIL = ("break 1 — хвост после ключевого слова",
                 "func main\n    var i\n    i = 0\n    while i < 3\n"
                 "        break 1\n    end\nend\n")

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
