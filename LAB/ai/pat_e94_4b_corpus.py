#!/usr/bin/env python3
"""pat_e94_4b_corpus.py — патч lab_t_bridge_corpus.py для E9.4-4b-1:
12 семейных мутантов T-E9-19 «переворачиваются» развилкой «семья |
чужой» — образ остаётся ВАЛИДНЫМ чужим PE32+ (семейный инвариант
сломан, машина/магия/секция/вход целы) — мост обязан печатать ЧУЖУЮ
факт-строку (факты parse_foreign оракула) и код 0. Программная замена
по точному образцу (урок сессии 81: длинные строки таблиц — только
python-заменой)."""
import io
import sys

P = "/home/z/my-project/repo/LAB/py/lab_t_bridge_corpus.py"
src = io.open(P, encoding="utf-8").read()

# 1) хелпер чужой факт-строки — после блока констант S_*
anchor = 'S_BIG = b"U-L5-BRIDGE ERR=BIG EXE\\r\\n"\n'
helper = anchor + '''

def foreign_line(data):
    """Чужая факт-строка моста (E9.4-4b-1) — факты parse_foreign:
    FOREIGN=1 SECT=<индекс секции кода> ENTRY/VSIZE/RAW/INS/TARGET/BSS."""
    f = lab_bridge.parse_foreign(data)
    pe = f["pe"]
    return ("U-L5-BRIDGE FOREIGN=1 SECT=%d ENTRY=%08X VSIZE=%08X RAW=%08X"
            " INS=%d TARGET=%08X BSS=%08X\\r\\n"
            % (pe["sections"].index(f["code"]), pe["addr_entry_point"],
               f["vsize"], f["raw"], len(f["ins"]), f["target"],
               f["bss"])).encode("latin1")

'''
if "def foreign_line" in src:
    print("хелпер уже есть — пропуск")
else:
    if anchor not in src:
        sys.exit("якорь S_BIG не найден")
    src = src.replace(anchor, helper, 1)

# 2) хелпер кейса-перевёртыша — внутри cli_cases (после def mut)
mut_anchor = """    def mut(off, val):
        b = bytearray(seed)
        b[off] = val
        return bytes(b)
"""
fcase = mut_anchor + '''
    def fcase(name, data):
        """Мутант-«перевёртыш» E9.4-4b-1: семейный инвариант сломан,
        образ остаётся ВАЛИДНЫМ чужим PE32+ — чужая факт-строка, код 0."""
        return (name, ["in.exe", "t.b2", "t.peg"], {"in.exe": data},
                foreign_line(data), 0)
'''
if "def fcase" in src:
    print("fcase уже есть — пропуск")
else:
    if mut_anchor not in src:
        sys.exit("якорь def mut не найден")
    src = src.replace(mut_anchor, fcase, 1)

# 3) 12 мутантов: S_FAMILY/6 -> fcase(...)
FLIPS = [("NumberOfSections", "mut(134, 2)"),
         ("ImageBase", "mut(176, 1)"),
         ("Subsystem", "mut(221, 4)"),
         ("имя секции", "mut(392, 120)"),
         ("SizeOfImage", "mut(208, 1)"),
         ("SizeOfHeaders", "mut(213, 3)"),
         ("заглушка", "mut(64, 117)"),
         ("игла", "mut(81, 120)"),
         ("пробел в имени", "mut(77, 32)"),
         ("DLL-имя", "mut(dll_off, 120)"),
         ("hint нечётный", "mut(thunk_off, seed[thunk_off] | 1)"),
         ("терминатор IDT", "mut(idt2_off, 1)")]
done = 0
for name, call in FLIPS:
    old = ('        ("%s", ["in.exe", "t.b2", "t.peg"],\n'
           '         {"in.exe": %s}, S_FAMILY, 6),\n' % (name, call))
    new = '        fcase("%s", %s),\n' % (name, call)
    if new in src:
        done += 1
        continue
    if old not in src:
        sys.exit("мутант не найден: %s" % name)
    src = src.replace(old, new, 1)
    done += 1
print("перевёрнуто мутантов: %d/12" % done)

io.open(P, "w", encoding="utf-8").write(src)
print("OK")
