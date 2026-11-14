"""lab_l2_ix.py — эталоны WALL срез 4b: индексация e[i] и astore (E6.4c-3/4b).

Вход:  нет (модуль-данные).
Выход: IX_ANCHORS — (имя, исходник) якорей индексации: ссылки на
       B1/F11/F11d/F12/F15 из lab_l2_cases2 (выписаны вручную в E6.4c-2,
       единый источник — не дублируются) + новые якоря среза 4b;
       IX_ERR_NAMES — имена ошибок ERRORS2 среза 4b (единый источник —
       lab_l2_prog); IX_EXTRA_ERRORS — дополнительные ошибки среза 4b;
       big_ix() — большой детерминированный исходник (цепочки индексов,
       astore в циклах, индексация в условиях и аргументах).
Функция: эталоны секции 11 батареи (T-E6-37/39/40/47) и dev-теста
         LAB/ai/wall_test_ix.py. Соглашение среза 3b: данные батареи
         живут в LAB/py, частная зона LAB/ai их только импортирует.
"""

# Якоря среза 4b из cases2 (полные/фрагментные, выписаны в E6.4c-2):
# B1 — массив + astore/index + * / %; F11 — глобальный массив (lea rip
# база); F11d — DZ 8n; F12 — указатель в переменной (p[1] = 42);
# F15 — цепочка p[0][1] = 5 (база — выражение). wall == оракулу.
IX_CASES2_FULL = ("B1 массив + astore/index + * / %",)
IX_CASES2_FRAG = ("F11 глобальный массив: len и rip-адрес базы",
                  "F11d данные: глобальный массив DZ 8n",
                  "F12 указатель в переменной: p = &buf; p[1] = 42",
                  "F15 цепочка индексов: p[0][1] = 5")

# Новые якоря среза 4b (полный выход == оракулу): записи в глобальный
# массив в цикле (astore с цепочками && и *), чтение массива в
# аргументах вызова, глубокая цепочка p[0][1][2], getb/индекс рядом.
IX_ANCHORS = [
    ("ix_A1 astore в цикле с && и *",
     "var g[8]\nfunc main\n    var i\n    var n\n"
     "    i = 0\n    n = 0\n"
     "    while i < 8 && n < 100\n"
     "        g[i] = i * i\n"
     "        n = n + g[i]\n"
     "        i = i + 1\n"
     "    end\nend\n"),
    ("ix_A2 индекс в аргументах и в сравнении",
     "var g[4]\nfunc f(a, b)\n    return a + b\nend\n"
     "func main\n    var r\n    g[0] = 5\n    g[1] = 7\n"
     "    if g[0] < g[1]\n        r = f(g[0], g[1])\n    end\nend\n"),
    ("ix_A3 глубокая цепочка p[0][1][2] = 5",
     "func main\n    var p\n    var q\n    p = q\n"
     "    p[0][1][2] = 5\nend\n"),
    ("ix_A4 локальный массив: запись и чтение",
     "func main\n    var a[3]\n    var x\n"
     "    a[0] = 10\n    a[1] = a[0] + 1\n"
     "    a[2] = a[1] + a[0]\n    x = a[2]\nend\n"),
    ("ix_A5 индексация выражения-вызова и getb",
     "var buf\nfunc main\n    var x\n    x = getb(&buf, 0) + 1\n"
     "    x = x + 0\nend\n"),
    ("ix_A6 astore к параметру-указателю",
     "func f(p)\n    p[2] = 9\n    return p\nend\n"
     "func main\n    var g\n    g = f(&g)\nend\n"),
]

# Ошибки среза 4b из ERRORS2 (lab_l2_prog — единый источник).
IX_ERR_NAMES = frozenset((
    "запись в строку по индексу", "чтение строки по индексу",
))

# Дополнительные ошибки среза 4b (нет в ERRORS2; строки берёт оракул).
IX_EXTRA_ERRORS = [
    ("astore к функции", "func f\nend\nfunc main\n    f[0] = 5\nend\n"),
    ("astore к ext", "ext ExitProcess\nfunc main\n"
                     "    ExitProcess[0] = 5\nend\n"),
    ("astore к неизвестному", "func main\n    zz[0] = 5\nend\n"),
    ("индексация ext", "ext ExitProcess\nfunc main\n    var x\n"
                       "    x = ExitProcess[0]\nend\n"),
    ("astore без '='", "var g[2]\nfunc main\n    g[0]\nend\n"),
    ("astore без ]", "var g[2]\nfunc main\n    g[0 = 5\nend\n"),
    ("astore без закрывающей в цепочке",
     "var g[2]\nfunc main\n    var p\n    p[0][1 = 5\nend\n"),
]


def big_ix(min_lines=200):
    """Детерминированный большой исходник срез 4b: astore/индексация в
    циклах, цепочки индексов, индексация в условиях. Стресс T-E6-39."""
    import random
    rnd = random.Random(20261114)
    lines = ["; большой сгенерированный исходник: индексация среза 4b",
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
    while len(lines) < min_lines - 16:
        idx += 1
        na = rnd.randint(2, 9)
        lines.append("func f%d(k)" % idx)
        lines.append("    var a[%d]" % na)
        lines.append("    var t")
        lines.append("    var i")
        lines.append("    t = 0")
        lines.append("    i = 0")
        lines.append("    while i < %d && t < 10000" % na)
        lines.append("        a[i] = i * k + len(g)")
        lines.append("        t = t + a[i]")
        if idx % 3 == 0:
            lines.append("        if a[i] > 500 || t > 9000")
            lines.append("            i = i + 2")
            lines.append("            continue")
            lines.append("        end")
        lines.append("        i = i + 1")
        lines.append("    end")
        if idx % 4 == 0:
            lines.append("    if a[0] < a[%d]" % (na - 1))
            lines.append("        t = t + a[0] * 2")
            lines.append("    end")
        lines.append("    return t")
        lines.append("end")
    lines.append("func main")
    lines.append("    var r")
    lines.append("    var i")
    lines.append("    r = 0")
    lines.append("    i = 0")
    for i in range(1, idx + 1):
        if i % 2 == 1:
            lines.append("    r = r + f%d(%d)" % (i, i))
        else:
            lines.append("    g[i] = f%d(%d) / 2" % (i, i))
            lines.append("    r = r + g[i] % 1000")
    lines.append("    r = r + acc + hexnib(len(g) & 15)")
    lines.append("    ExitProcess(0)")
    lines.append("end")
    return "\n".join(lines) + "\n"
