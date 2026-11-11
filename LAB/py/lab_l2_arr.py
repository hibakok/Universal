"""lab_l2_arr.py — эталоны WALL срез 4a: объявления массивов (E6.4c-3/4).

Вход:  нет (модуль-данные).
Выход: ARR_ANCHORS — (имя, исходник) программ среза 4a: var a[n] глобально
       и локально, база адреса (lea), &массив, len(массив), DZ 8n, сдвиг
       слотов после массива, микс с срезами 1-3 (БЕЗ индексации e[i] и
       astore — они в срезе 4b); ARR_ERR_NAMES — имена массивных ошибок
       ERRORS2 (единый источник — lab_l2_prog); ARR_EXTRA_ERRORS —
       дополнительные ошибки среза 4a; DEMO_ARR / DEMO_ARR_PEG — полный
       круг «U-ARR-OK 45»; big_arr() — большой детерминированный исходник.
Функция: эталоны секции 11 батареи (T-E6-37/40/41/45/46) и dev-теста
         LAB/ai/wall_test_arr.py. Соглашение среза 3b: данные батареи
         живут в LAB/py, частная зона LAB/ai их только импортирует.
"""

# Якоря среза 4a: wall.exe == оракулу байт-в-байт (полный выход).
ARR_ANCHORS = [
    ("arr_A1 глобальный+локальный массив, len обоих",
     "var g[10]\nfunc main\n    var a[5]\n    var x\n"
     "    x = len(a)\n    x = x + len(g)\nend\n"),
    ("arr_A2 скаляры после массива (сдвиг слотов)",
     "func main\n    var a[3]\n    var x\n    var y\n"
     "    x = 1\n    y = 2\nend\n"),
    ("arr_A3 адреса &a и &g (arrbase / rip)",
     "var g[4]\nfunc main\n    var a[6]\n    var p\n    var q\n"
     "    p = &a\n    q = &g\nend\n"),
    ("arr_A4 массив в арифметике и аргументах вызова",
     "var g[7]\nfunc f(p, n)\n    var t\n"
     "    t = p + n\n    return t\nend\n"
     "func main\n    var a[8]\n    var r\n"
     "    r = f(a, len(a))\n    r = r + a + 1\n"
     "    r = r + g\nend\n"),
    ("arr_A5 глобальный [1] — вид arr, lea rip",
     "var g[1]\nfunc main\n    var x\n    x = g\nend\n"),
    ("arr_A6 локальный [1] — квирк скаляра (присваивание можно)",
     "func main\n    var a[1]\n    a = 5\n"
     "    var x\n    x = a + 1\nend\n"),
    ("arr_A7 параметры + массив (окно larr)",
     "func f(p)\n    var a[2]\n    var t\n"
     "    t = p + len(a)\n    return t\nend\n"
     "func main\n    var r\n    r = f(3)\nend\n"),
    ("arr_A8 микс с срезами 1-3 (массивы + % && break/continue)",
     "var g[10]\nfunc main\n    var a[5]\n    var x\n"
     "    var i\n    x = 0\n    i = 0\n"
     "    while i < 4 && x < 100\n"
     "        i = i + 1\n"
     "        if i % 2 == 1\n            continue\n        end\n"
     "        x = x + len(a) * 2\n"
     "        if x > 90\n            break\n        end\n"
     "    end\nend\n"),
    ("arr_A9 несколько массивов подряд",
     "func main\n    var a[2]\n    var b[3]\n"
     "    var c[4]\n    var x\n    x = len(a)\n"
     "    x = x + len(b) + len(c)\nend\n"),
    ("arr_A10 несколько функций с массивами (окна larr/ftab)",
     "var g[5]\nfunc f(n)\n    var a[3]\n"
     "    var t\n    t = n + len(a)\n"
     "    return t\nend\n"
     "func h\n    var b[2]\n    return len(b)\nend\n"
     "func main\n    var r\n    r = f(1) + h()\n"
     "    r = r + len(g)\nend\n"),
]

# Массивные ошибки ERRORS2 (lab_l2_prog — единый источник; фильтр по
# именам, как BC_ERR_NAMES среза 2).
ARR_ERR_NAMES = frozenset((
    "глобальный массив [0]", "размер массива не число",
    "массив слишком большой", "локальный массив [0]",
    "присвоить массив целиком", "присвоить локальный массив целиком",
    "запись в строку по индексу", "чтение строки по индексу",
    "len функции", "локаль-массив конфликтует",
))

# Дополнительные ошибки среза 4a (нет в ERRORS2; строка — из оракула).
ARR_EXTRA_ERRORS = [
    ("len локального скаляра", "func main\n    var x\n    x = len(x)\nend\n"),
    ("var a[4097] граница", "var a[4097]\nfunc main\nend\n"),
    ("var a[3 без закрывающей", "var a[3\nfunc main\nend\n"),
    ("var a[+3] не число", "var a[+3]\nfunc main\nend\n"),
]

# Полный круг среза 4a: объявления массивов, базы, len + срезы 1-3.
# Печатает "U-ARR-OK 45\r\n": len(a)*len(g) = 5*10 = 50; цикл с
# continue по нечётным i и +len(a)=5 по чётным (i=2,4): 50+10 = 60;
# + len(msg) = 9 -> 69 = 0x45 (break-ветка эмитится, но не срабатывает).
DEMO_ARR = """\
; UNIVERSAL / WALL v2 / демонстрация среза 4a: объявления массивов,
; адреса баз, len(массив). Печатает "U-ARR-OK 45" и выходит.

ext GetStdHandle
ext WriteFile
ext ExitProcess

str msg = 'U-ARR-OK '

var out
var g[10]

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
    var a[5]
    var x
    var i
    var h
    x = len(a) * len(g)
    i = 0
    while i < 4 && x < 1000
        i = i + 1
        if i % 2 == 1
            continue
        end
        x = x + len(a)
        if x > 1000
            break
        end
    end
    x = x + len(msg)
    h = GetStdHandle(-11)
    WriteFile(h, msg, len(msg), &out, 0)
    setb(&out, 0, hexnib(x >> 4))
    setb(&out, 1, hexnib(x & 15))
    setb(&out, 2, 13)
    setb(&out, 3, 10)
    WriteFile(h, &out, 4, &out, 0)
    ExitProcess(0)
end
"""

DEMO_ARR_PEG = """\
; UNIVERSAL / PEG v1 / обёртка WALL v2 (SPEC/11)
!module arrdemo
!entry 1200
!idata 1000 28
!iat 1028 48
!stackcom 4000
!heapcom 4000
"""


def big_arr(min_lines=190):
    """Детерминированный большой исходник: массивы среза 4a (объявления,
    базы, len; БЕЗ индексации — она в срезе 4b). Стресс T-E6-39/45."""
    import random
    rnd = random.Random(20261111)
    lines = ["; большой сгенерированный исходник: массивы среза 4a",
             "ext ExitProcess",
             "var acc",
             "var g[64]",
             "func hexnib(n)",
             "    var t",
             "    t = n & 15",
             "    if t < 10",
             "        t = t + 48",
             "    else",
             "        t = t + 55",
             "    end",
             "    return t",
             "end"]
    idx = 0
    while len(lines) < min_lines - 14:
        idx += 1
        na = rnd.randint(2, 9)
        nb = rnd.randint(2, 7)   # [1] — скаляр для len (квирк оракула)
        lines.append("func f%d(k)" % idx)
        lines.append("    var a[%d]" % na)
        lines.append("    var b[%d]" % nb)
        lines.append("    var t")
        lines.append("    t = k + len(a) * len(b) + len(g)")
        if idx % 3 == 0:
            lines.append("    if t > 100 && t < 100000")
            lines.append("        t = t + len(a)")
            lines.append("    else")
            lines.append("        t = t - len(b)")
            lines.append("    end")
        if idx % 4 == 0:
            lines.append("    while t > 200")
            lines.append("        t = t - len(b) * 2")
            lines.append("        if t % 5 == 3")
            lines.append("            break")
            lines.append("        end")
            lines.append("    end")
        lines.append("    return t")
        lines.append("end")
    lines.append("func main")
    lines.append("    var r")
    lines.append("    var p")
    lines.append("    var h")
    lines.append("    p = 0")
    lines.append("    r = 0")
    for i in range(1, idx + 1):
        if i % 2 == 1:
            lines.append("    r = r + f%d(%d)" % (i, i))
        else:
            lines.append("    p = p + len(g) + f%d(%d) / 2" % (i, i))
    lines.append("    r = r + p % 1000 + hexnib(len(g) & 15)")
    lines.append("    ExitProcess(0)")
    lines.append("end")
    return "\n".join(lines) + "\n"
