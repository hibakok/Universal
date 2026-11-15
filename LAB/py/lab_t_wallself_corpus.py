"""lab_t_wallself_corpus.py — корпус секции 12: источники T-E6-49d.

Пул для сверки прохода 0+1 каркаса wall.wall с оракулом parse и
инструментом wall.exe (E6.4d-3/2: тела с var/return/setb/имя-статами;
выражения стат-режимом — см. lab_t_wallself.py). Только ASCII-источники:
оракул _lex работает со str (кириллица — имя), инструменты — с байтами
(отказ на лексе); не-ASCII случаи сверяются инструмент-в-инструмент в
матрице T-E6-49c. Решение о доступности (класс) принимает
_expect_line модуля lab_t_wallself_model.
"""
import lab_l2_cases
import lab_l2_cases2
import lab_l2_prog


KITCHEN = (b"ext GetStdHandle\n"
           b"str s = 'a\\nb\\r\\t\\0\\\\\\'z'\n"
           b"var a[3]\n"
           b"var g\n")

def corpus():
    """(имя, текст) — пул для сверки прохода 0+1 каркаса с оракулом.

    Только ASCII-источники: оракул _lex работает со str (кириллица —
    имя), инструменты — с байтами (отказ на лексе); не-ASCII случаи
    сверяются инструмент-в-инструмент в матрице T-E6-49c. Решение о
    доступности (класс без обработки func — см. _expect_line) принима-
    ется в run(); здесь только пул."""
    out = []
    for n, s, _w in lab_l2_cases.CASES_FULL:
        out.append(("v1 " + n, s))
    for n, s, _f in lab_l2_cases.CASES_FRAG:
        out.append(("v1ф " + n, s))
    for n, s, _w in lab_l2_cases2.CASES_FULL2:
        out.append(("v2 " + n, s))
    for n, s, _f in lab_l2_cases2.CASES_FRAG2:
        out.append(("v2ф " + n, s))
    for n, s, _l in lab_l2_prog.ERRORS:
        out.append(("E1 " + n, s))
    for n, s, _l in lab_l2_prog.ERRORS2:
        out.append(("E2 " + n, s))
    out += [
        ("микро: CR-разбиение, ошибка в строке 3", "func main\rvar i\r@ bad\r"),
        ("микро: без хвостового перевода", "func main\nend"),
        ("микро: только комментарий", "; nothing"),
        ("микро: пустой файл", ""),
        ("микро: литерал 512 байт",
         "str s = '" + "x" * 512 + "'\nfunc main\nend"),
        ("микро: литерал 513 байт",
         "str s = '" + "x" * 513 + "'\nfunc main\nend"),
        ("микро: == в выражении (лексер пускает)",
         "func main\nvar i\ni = 1 == 2\nend"),
        ("big: big_source (1203 строки)", lab_l2_prog.big_source()),
        ("big: big_source2 (705 строк)", lab_l2_prog.big_source2()),
        # E6.4d-2/3: объявления и пост-проверка main (класс без func)
        ("микро: var g (нет main)", "var g\n"),
        ("микро: var x повтор", "var x\nvar x\nfunc main\nend\n"),
        ("микро: var a[0]", "var a[0]\nfunc main\nend\n"),
        ("микро: var a[n] (не число)", "var a[n]\nfunc main\nend\n"),
        ("микро: var a[5000] (слишком большой)", "var a[5000]\nfunc main\nend\n"),
        ("микро: var a[4096] нет main", "var a[4096]\n"),
        ("микро: var a[4097]", "var a[4097]\n"),
        ("микро: не-ключевое имя в объявлениях", "foo = 1\n"),
        ("микро: end в объявлениях", "end\n"),
        ("микро: var без имени", "var\n"),
        ("микро: var 5 (не имя)", "var 5\n"),
        ("микро: var _x (подчёркивание)", "var _x\n"),
        ("микро: var X (заглавная)", "var X\n"),
        ("микро: имя 64 байта", "var " + "x" * 64 + "\n"),
        ("микро: str без =", "str s\n"),
        ("микро: str = не литерал", "str s = 1\n"),
        ("микро: str лишний токен", "str s = 'x' y\n"),
        ("микро: str повтор", "str s = 'a'\nstr s = 'b'\n"),
        ("микро: ext дубликат без регистра", "ext Ab\next ab\n"),
        ("микро: девятый ext",
         "ext A\next B\next C\next D\next E\next F\next G\next H\next I\n"),
        ("микро: ext имя 32 байта", "ext " + "x" * 32 + "\n"),
        ("микро: str-объявление нет main", "str s = 'a'\n"),
        ("микро: все виды объявлений",
         "ext GetStdHandle\nstr s = 'a\\nb\\r\\t\\0\\\\\\'z'\nvar a[3]\nvar g\n"),
        ("микро: переводы строк (пусто)", "\n\n\n"),
        ("микро: main с параметром", "func main(x)\nend\n"),
        ("микро: незакрытый блок", "func main\n"),
        # E6.4d-2/4: заголовки func + плечо end (класс с пустыми телами)
        ("микро: func без имени", "func 5\nend\n"),
        ("микро: func имя повтор",
         "func f\nend\nfunc f\nend\nfunc main\nend\n"),
        ("микро: пустые скобки main — код 0", "func main()\nend\n"),
        ("микро: main 4 параметра", "func main(a, b, c, d)\nend\n"),
        ("микро: func скобка без закр", "func f(a\nend\nfunc main\nend\n"),
        ("микро: func конец мусор", "func f x\nend\nfunc main\nend\n"),
        ("микро: параметр == глобаль",
         "var g\nfunc f(g)\nend\nfunc main\nend\n"),
        ("микро: запятая без параметра", "func f(,)\nend\nfunc main\nend\n"),
        ("микро: end между func",
         "func f\nend\nend\nfunc main\nend\n"),
        ("микро: две func + main — код 0",
         "func a\nend\nfunc main\nend\n"),
        ("микро: CRLF-заголовки — код 0",
         "func f\r\nend\r\nfunc main\r\nend\r\n"),
        ("микро: var в теле (E6.4d-3/1 — сравнимо)", "func main\nvar i\nend\n"),
        ("микро: вложенная func (quirk — вне класса)",
         "func f\nfunc g\nend\nend\n"),
        # E6.4d-3/1: локальные var (S006) — ошибки и код-0
        ("микро: var в теле две — код 0", "func main\nvar i\nvar j\nend\n"),
        ("микро: var в теле массив — код 0", "func main\nvar a[3]\nend\n"),
        ("микро: var в теле a[4096] — код 0", "func main\nvar a[4096]\nend\n"),
        ("микро: var в теле a[4097]", "func main\nvar a[4097]\nend\n"),
        ("микро: var в теле a[0]", "func main\nvar a[0]\nend\n"),
        ("микро: var в теле dup", "func main\nvar i\nvar i\nend\n"),
        ("микро: var в теле dup параметра",
         "func f(x)\nvar x\nend\nfunc main\nend\n"),
        ("микро: var в теле конфликт глобали",
         "var g\nfunc main\nvar g\nend\n"),
        ("микро: var в теле конфликт str",
         "str s = 'a'\nfunc main\nvar s\nend\n"),
        ("микро: var в теле имя функции",
         "func f\nend\nfunc main\nvar f\nend\n"),
        ("микро: var в теле _x", "func main\nvar _x\nend\n"),
        ("микро: var в теле хвост мусор", "func main\nvar i = 5\nend\n"),
        ("микро: var между func — hdrfail",
         "func f\nend\nvar x\nfunc main\nend\n"),
        ("микро: var в теле + main(a)",
         "func f\nvar i\nend\nfunc main(a)\nend\n"),
        # E6.4d-3/2: выражения + S00B return / S00C setb / S00D namestmt
        ("микро: return выр — код 0", "func main\nreturn 1 + 2 * 3\nend\n"),
        ("микро: return скобки/сдвиги — код 0",
         "func main\nreturn (1 << 2) + (8 >> 1) & 7 | 1 ^ 2\nend\n"),
        ("микро: return getb+len — код 0",
         "str s = 'AB'\nfunc main\nreturn getb(s, 1) + len(s)\nend\n"),
        ("микро: return без значения — код 0", "func main\nreturn\nend\n"),
        ("микро: return хвост мусор", "func main\nreturn 1 2\nend\n"),
        ("микро: return без правого операнда", "func main\nreturn 1 +\nend\n"),
        ("микро: return литерал", "func main\nreturn 'x'\nend\n"),
        ("микро: return len не имя", "func main\nreturn len(5)\nend\n"),
        ("микро: return неизвестное имя (вне класса — cerr)",
         "func main\nreturn zz\nend\n"),
        ("микро: return вызов — код 0",
         "func add2(a, b)\nreturn a + b\nend\nfunc main\nreturn add2(3, 4)\nend\n"),
        ("микро: return индексация — код 0",
         "var a[3]\nfunc main\nreturn a[1] + a[0 * 2][0]\nend\n"),
        ("микро: setb — код 0", "var b\nfunc main\nsetb(&b, 0, 65)\nend\n"),
        ("микро: setb два аргумента", "func main\nsetb(1, 2)\nend\n"),
        ("микро: setb четыре аргумента", "func main\nsetb(1, 2, 3, 4)\nend\n"),
        ("микро: setb хвост мусор", "var b\nfunc main\nsetb(&b, 0, 1) x\nend\n"),
        ("микро: присваивание — код 0", "func main\nvar x\nx = 1 << 2\nend\n"),
        ("микро: присваивание глобаль/str — код 0",
         "var g\nstr s = 'AB'\nfunc main\ng = len(s)\nend\n"),
        ("микро: присваивание унарный минус — код 0",
         "func main\nvar x\nx = -x\nx = --x\nend\n"),
        ("микро: присваивание в скобках — код 0",
         "func main\nvar x\nx = ((1 >> 1) + 1) & 3\nend\n"),
        ("микро: вызов-утверждение — код 0",
         "func f\nreturn\nend\nfunc main\nf()\nend\n"),
        ("микро: вызов-утверждение хвост", "func f\nend\nfunc main\nf() x\nend\n"),
        ("микро: вызов 5 аргументов ext — код 0",
         "ext WriteFile\nfunc main\nWriteFile(1, 2, 3, 4, 5)\nend\n"),
        ("микро: astore — код 0", "var a[3]\nfunc main\na[0] = 7\nend\n"),
        ("микро: astore локаль — код 0",
         "var m[4]\nfunc main\nvar i\nm[i + 1] = i * 2\nend\n"),
        ("микро: astore в str", "str s = 'a'\nfunc main\ns[0] = 1\nend\n"),
        ("микро: astore неизвестное имя", "func main\nzz[0] = 1\nend\n"),
        ("микро: astore в функцию",
         "func f\nend\nfunc main\nf[0] = 1\nend\n"),
        ("микро: astore в ext",
         "ext WriteFile\nfunc main\nWriteFile[0] = 1\nend\n"),
        ("микро: astore без '='", "var a[3]\nfunc main\na[0] 1\nend\n"),
        ("микро: str в теле (namestmt ERR)", "func main\nstr s = 'a'\nend\n"),
        ("микро: if = 5 (p_cond ERR — сравнимо)", "func main\nif = 5\nend\nend\n"),
        ("микро: if (x) без сравнения (сравнимо)", "func main\nvar x\nif (x)\nend\nend\n"),
        ("микро: break вне while", "func main\nbreak\nend\n"),
        ("микро: continue вне while", "func main\ncontinue\nend\n"),
        ("микро: getb-утверждение (вне класса — cerr getb)",
         "var b\nfunc main\ngetb(&b, 0)\nend\n"),
        # E6.4d-3/3: статы bstk-группы (S009/S00A/S008/S00F + p_cond)
        ("микро: if пустое тело — код 0", "func main\nif 1 < 2\nend\nend\n"),
        ("микро: if+else пустые тела — код 0",
         "func main\nif 1 >= 2\nelse\nend\nend\n"),
        ("микро: while пустое тело — код 0", "func main\nwhile 1 < 2\nend\nend\n"),
        ("микро: if с телом — код 0",
         "func main\nvar i\nif i < 2\ni = 3\nend\nend\n"),
        ("микро: while с break — код 0",
         "func main\nvar i\nwhile i < 10\nbreak\nend\nend\n"),
        ("микро: while с continue — код 0",
         "func main\nvar i\nwhile i < 10\ncontinue\nend\nend\n"),
        ("микро: if с && — код 0",
         "func main\nvar i\nif i > 0 && i < 10\nend\nend\n"),
        ("микро: if с || — код 0",
         "func main\nvar i\nif i > 0 || i < 10\nend\nend\n"),
        ("микро: все 6 сравнений — код 0",
         "func main\nvar i\nif i == 1\nend\nif i != 1\nend\nif i < 1\nend\n"
         "if i <= 1\nend\nif i > 1\nend\nif i >= 1\nend\nend\n"),
        ("микро: вложенные if в while + else — код 0",
         "func main\nvar i\nwhile i < 3\nif i == 1\ni = 2\nelse\ni = 3\nend\nend\nend\n"),
        ("микро: break в if внутри while — код 0",
         "func main\nvar i\nwhile i < 9\nif i == 5\nbreak\nend\nend\nend\n"),
        ("микро: if cond вызов — код 0",
         "func f\nreturn 1\nend\nfunc main\nif f() < 2\nend\nend\n"),
        ("микро: if без оператора", "func main\nvar i\nif i\nend\nend\n"),
        ("микро: if одиночный =", "func main\nif 1 = 2\nend\nend\n"),
        ("микро: if плохой оператор +", "func main\nif 1 + 2\nend\nend\n"),
        ("микро: if хвост мусор", "func main\nif 1 < 2 x\nend\nend\n"),
        ("микро: if cond неизвестное имя (вне класса — cerr)",
         "func main\nif zz < 2\nend\nend\n"),
        ("микро: else после while", "func main\nwhile 1 < 2\nend\nelse\nend\n"),
        ("микро: else после else",
         "func main\nif 1 < 2\nelse\nelse\nend\nend\n"),
        ("микро: else до if (в func)", "func main\nelse\nend\n"),
        ("микро: break 1 (в while)",
         "func main\nwhile 1 < 2\nbreak 1\nend\nend\n"),
        ("микро: continue хвост (в while)",
         "func main\nwhile 1 < 2\ncontinue x\nend\nend\n"),
        ("микро: незакрытый if",
         "func main\nif 1 < 2\nend\n"),
        ("микро: незакрытый while",
         "func main\nwhile 1 < 2\nend\n"),
        ("микро: end закрывает if, не func — код 0",
         "func main\nvar i\nif i < 2\nend\nreturn 1\nend\n"),
    ]
    return [(n, s) for n, s in out if _ascii(s)]


def _ascii(s):
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False
