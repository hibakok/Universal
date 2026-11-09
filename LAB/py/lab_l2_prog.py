"""lab_l2_prog.py — программы-эталоны оракула WALL v1/v2 (SPEC/11).

Вход:  нет (модуль-данные).
Выход: ERRORS — (имя, исходник, номер строки ошибки) v1 (инструмент
       wall.exe E6.4b сверяется только с ними — T-E6-27); ERRORS2 —
       ошибки конструкций v2; DEMO_WALL / DEMO_WALL_PEG — программа
       полного круга v1 («U-WALL-OK 37»); DEMO_WALL2 / DEMO_WALL2_PEG —
       полный круг v2 (массивы, * / %, break/continue, && / ||, куча
       HeapAlloc; «U-WALL2-OK 85»); big_source() / big_source2() —
       большие детерминированные исходники стресс-теста.
Функция: эталоны секций 9 батареи (T-E6-20..24 и T-E6-31..35).
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

# Ошибки конструкций v2 (E6.4c; оракул — T-E6-32; инструмент — после
# E6.4c-3). Строка — номер строки WallError.
ERRORS2 = [
    ("break вне цикла", "func main\n    break\nend\n", 2),
    ("continue вне цикла", "func main\n    continue\nend\n", 2),
    ("break в if вне while",
     "func main\n    if 1 < 2\n        break\n    end\nend\n", 3),
    ("глобальный массив [0]", "var a[0]\nfunc main\nend\n", 1),
    ("размер массива не число", "var a[n]\nfunc main\nend\n", 1),
    ("массив слишком большой", "var a[5000]\nfunc main\nend\n", 1),
    ("локальный массив [0]", "func main\n    var a[0]\nend\n", 2),
    ("присвоить массив целиком",
     "var a[3]\nfunc main\n    a = 1\nend\n", 3),
    ("присвоить локальный массив целиком",
     "func main\n    var a[3]\n    a = 1\nend\n", 3),
    ("запись в строку по индексу",
     "str s = 'a'\nfunc main\n    s[0] = 1\nend\n", 3),
    ("чтение строки по индексу",
     "str s = 'a'\nfunc main\n    var x\n    x = s[0]\nend\n", 4),
    ("len функции",
     "func f\nend\nfunc main\n    var x\n    x = len(f)\nend\n", 5),
    ("локаль-массив конфликтует",
     "func main\n    var a[3]\n    var a\nend\n", 3),
]

# Полный круг v2: массивы, * / %, break/continue, && / ||, куча.
# Печатает "U-WALL2-OK 85\r\n": fib 0..11; сумма чётных fib[1..10] с
# break/continue = 88; p[0]=176, p[1]=176+89=265; 265/2=132; 132+1=133=0x85.
DEMO_WALL2 = """\
; UNIVERSAL / WALL v2 / демонстрация: массивы, умножение/деление/остаток,
; break/continue, цепочки условий, динамическая память (HeapAlloc).
; Печатает "U-WALL2-OK 85" и выходит.

ext GetStdHandle
ext WriteFile
ext ExitProcess
ext GetProcessHeap
ext HeapAlloc
ext HeapFree

str msg = 'U-WALL2-OK '

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
    var fib[12]
    var i
    var acc
    var h
    var p
    fib[0] = 0
    fib[1] = 1
    i = 2
    while i < 12
        fib[i] = fib[i - 1] + fib[i - 2]
        i = i + 1
    end
    acc = 0
    i = 0
    while i < 12 && acc < 1000
        if i > 9
            break
        end
        i = i + 1
        if i % 2 == 1
            continue
        end
        acc = acc + fib[i]
    end
    h = GetProcessHeap()
    p = HeapAlloc(h, 0, 64)
    p[0] = acc * 2
    p[1] = p[0] + fib[11]
    if p[1] > 200 && p[1] < 300
        acc = p[1] / 2
    else
        acc = 0
    end
    HeapFree(h, 0, p)
    if acc == 132 || acc == 999
        acc = acc + 1
    end
    h = GetStdHandle(-11)
    WriteFile(h, msg, len(msg), &out, 0)
    setb(&out, 0, hexnib(acc >> 4))
    setb(&out, 1, hexnib(acc & 15))
    setb(&out, 2, 13)
    setb(&out, 3, 10)
    WriteFile(h, &out, 4, &out, 0)
    ExitProcess(0)
end
"""

DEMO_WALL2_PEG = """\
; UNIVERSAL / PEG v1 / обёртка WALL v2 (SPEC/11)
!module walldemo2
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


def big_source2(min_lines=700):
    """Детерминированный большой исходник WALL v2 (стресс-тест T-E6-35):
    массивы, * / %, break/continue, && / ||. Тело держим < 60 КиБ
    (предел brick 64 КиБ)."""
    import random
    rnd = random.Random(20261109)
    nf = 10
    lines = ["; большой сгенерированный исходник WALL v2 (стресс-тест)",
             "ext ExitProcess",
             "var g[64]",
             "var acc"]
    for f in range(nf):
        lines += ["func w%d(n)" % f,
                  "    var a[16]",
                  "    var i",
                  "    var s",
                  "    i = 0",
                  "    while i < 16 && n > 0",
                  "        a[i] = i * %d + n / 3" % (f + 2),
                  "        i = i + 1",
                  "    end",
                  "    s = 0",
                  "    i = 0",
                  "    while i < 16",
                  "        if a[i] % 7 == 5",
                  "            continue",
                  "        end",
                  "        if s > 900000 || i > 15",
                  "            break",
                  "        end",
                  "        s = s + a[i] - s / 2",
                  "        i = i + 1",
                  "    end",
                  "    return s",
                  "end"]
    lines += ["func main",
              "    var k",
              "    acc = 0",
              "    k = 0",
              "    while k < %d || acc > 999999999" % nf]
    while len(lines) < min_lines:
        r = rnd.randrange(4)
        if r == 0:
            lines.append("    g[%d] = g[%d] * %d + acc / %d"
                         % (rnd.randrange(0, 64), rnd.randrange(0, 64),
                            rnd.randrange(1, 90), rnd.randrange(1, 9)))
        elif r == 1:
            lines.append("    acc = acc + g[%d] %% %d"
                         % (rnd.randrange(0, 64), rnd.randrange(2, 97)))
        elif r == 2:
            lines.append("    if acc > %d && g[%d] > %d"
                         % (rnd.randrange(100, 90000),
                            rnd.randrange(0, 64), rnd.randrange(0, 500)))
            lines.append("        acc = acc / %d" % rnd.randrange(2, 9))
            lines.append("    end")
        else:
            lines.append("    acc = g[%d] - g[%d] / %d"
                         % (rnd.randrange(0, 64), rnd.randrange(0, 64),
                            rnd.randrange(2, 9)))
    lines += ["    end", "    ExitProcess(0)", "end"]
    return "\n".join(lines) + "\n"
