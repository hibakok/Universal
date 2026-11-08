"""lab_l2_prog.py — программы-эталоны оракула WALL v1 (SPEC/11).

Вход:  нет (модуль-данные).
Выход: ERRORS — (имя, исходник, номер строки ошибки); DEMO_WALL /
       DEMO_WALL_PEG — программа полного круга (компиляция -> enc ->
       brick -> pegen -> эмуляция печатает "U-WALL-OK 37", код 0);
       big_source() — большой детерминированный исходник стресс-теста.
Функция: эталоны секций 9 батареи (T-E6-20..23); якоря компиляции —
         lab_l2_cases.py. Единая точка правды для будущего wall.exe.
"""

# (имя, исходник, ожидаемый номер строки ошибки WallError).
ERRORS = [
    ("неизвестное имя", "func main\n    x = 1\nend\n", 2),
    ("нет main", "func f\nend\n", 2),
    ("два main", "func main\nend\nfunc main\nend\n", 3),
    ("незакрытый блок", "func main\n", 1),
    ("else вне if", "func main\nelse\nend\n", 2),
    ("лишний end", "func main\nend\nend\n", 3),
    ("сравнение в выражении", "func main\n    var x\n    x = 1 < 2\nend\n", 3),
    ("присваивание str", "str s = 'a'\nfunc main\n    s = 1\nend\n", 3),
    ("len не к str", "var g\nfunc main\n    g = len(g)\nend\n", 3),
    ("не то число аргументов",
     "func f(a)\nend\nfunc main\n    f(1, 2)\nend\n", 4),
    ("ext больше 5 аргументов",
     "ext F\nfunc main\n    F(1, 2, 3, 4, 5, 6)\nend\n", 3),
    ("имя с подчёркивания", "func main\n    var _x\nend\n", 2),
    ("число вне диапазона",
     "func main\n    var x\n    x = 2147483648\nend\n", 3),
    ("объявление после func", "func main\nend\nvar x\n", 3),
    ("main с параметром", "func main(x)\nend\n", 1),
    ("незакрытая строка", "str s = 'abc\nfunc main\nend\n", 1),
    ("неизвестный экран", "str s = 'a\\qb'\nfunc main\nend\n", 1),
    ("вызов не-функции", "var g\nfunc main\n    g(1)\nend\n", 3),
    ("& на функции", "func f\nend\nfunc main\n    var x\n    x = &f\nend\n",
     5),
    ("повторное имя", "var x\nvar x\nfunc main\nend\n", 2),
    ("локаль == глобаль", "var g\nfunc main\n    var g\nend\n", 3),
    ("функция как значение",
     "func f\nend\nfunc main\n    var x\n    x = f\nend\n", 5),
    ("setb в выражении", "func main\n    var x\n    x = setb(1, 2, 3)\nend\n",
     3),
    ("пять параметров", "func f(a, b, c, d, e)\nend\nfunc main\nend\n", 1),
    ("дубликат параметра", "func f(a, a)\nend\nfunc main\nend\n", 1),
    ("недопустимый символ", "func main\n    var x\n    x = 1 $ 2\nend\n", 3),
]

# Полный круг: нетривиальная программа на WALL v1 (T-E6-21).
# Печатает "U-WALL-OK 37\r\n": сумма 1..10 = 55 = 0x37, две hex-цифры.
DEMO_WALL = """\
; UNIVERSAL / WALL v1 / демонстрация: функции, циклы, условия, строки,
; внешние функции kernel32, getb/setb. Печатает "U-WALL-OK 37" и выходит.

ext GetStdHandle
ext WriteFile
ext ExitProcess

str msg = 'U-WALL-OK '

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
    i = 1
    s = 0
    while i <= 10
        s = s + i
        i = i + 1
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

DEMO_WALL_PEG = """\
; UNIVERSAL / PEG v1 / обёртка WALL v1 (SPEC/11)
!module walldemo
!entry 1200
!idata 1000 28
!iat 1028 48
!stackcom 4000
!heapcom 4000
"""


def big_source(min_lines=1200):
    """Детерминированный большой исходник WALL (стресс-тест T-E6-23)."""
    import random
    rnd = random.Random(20261108)
    nf = 12
    lines = ["; большой сгенерированный исходник WALL (стресс-тест)",
             "ext ExitProcess",
             "var acc",
             "var buf",
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
    for f in range(nf):
        lines += ["func w%d(n)" % f,
                  "    var i",
                  "    var s",
                  "    i = 0",
                  "    s = 0",
                  "    while i < n",
                  "        s = s + i + %d" % f,
                  "        i = i + 1",
                  "    end",
                  "    return s",
                  "end"]
    lines += ["func main",
              "    var k",
              "    acc = 0",
              "    k = 0",
              "    while k < %d" % nf]
    while len(lines) < min_lines:
        r = rnd.randrange(3)
        if r == 0:
            lines.append("    acc = acc + %d & 255" % rnd.randrange(0, 500))
        elif r == 1:
            lines.append("    setb(&buf, %d, hexnib(acc >> 4))"
                         % rnd.randrange(0, 8))
        else:
            lines.append("    acc = getb(&buf, %d)" % rnd.randrange(0, 8))
    lines += ["    end", "    ExitProcess(0)", "end"]
    return "\n".join(lines) + "\n"
