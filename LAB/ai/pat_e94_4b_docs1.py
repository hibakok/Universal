#!/usr/bin/env python3
"""pat_e94_4b_docs1.py — патч MAP/INDEX.md, MAP/INDEX-LAB.md, LAB/README.md,
TESTS/T-L5-BRIDGE.md для E9.4-4b-1 (развилка «семья | чужой» + чужие
факты). Программная замена по точному образцу."""
import io
import sys

BASE = "/home/z/my-project/repo/"


def sub(src, old, new, path):
    if old not in src:
        sys.exit("не найдено в %s: %r..." % (path, old[:70]))
    return src.replace(old, new, 1)


def wc(path):
    return io.open(BASE + path, encoding="utf-8").read().count("\n") + 1


# ------------------------------------------------------------ MAP/INDEX.md
P = "MAP/INDEX.md"
src = io.open(BASE + P, encoding="utf-8").read()

src = sub(src,
    "### KERNEL/L5-BRIDGE — мост BRIDGE v1 (E9.2-1 каркас + E9.2-2 спуск + E9.2-3a/b/c эмиссия: H -> метки -> M-строки канона)",
    "### KERNEL/L5-BRIDGE — мост BRIDGE v1 (E9.2-1 каркас + E9.2-2 спуск + E9.2-3a/b/c эмиссия + E9.4-4b-1 развилка «семья | чужой»)", P)
src = sub(src,
    "E9.4-4a — ПОРТ FF /4 + таблиц (decff/jtab/push_tgt — диффтест инструмента); отказы — коды 2..9) | 209 |",
    "E9.4-4a — ПОРТ FF /4 + таблиц (decff/jtab/push_tgt); E9.4-4b-1 — РАЗВИЛКА «семья | чужой» (check_head общий фронт / fam_chain предикат / foreign_front / print_ffacts — чужая факт-строка FOREIGN, файлы не пишутся); отказы — коды 2..9) | 226 |", P)
src = sub(src,
    "main (CLI → чтение → проверки → спуск → таблицы → карты (L) → эмиссия .b2 КАНОН (M/H) → PEG-выход (G) → факты M=/H=); 69 var (+pushmap — E9.4-4a) | 341 |",
    "main (CLI → чтение → общий фронт → РАЗВИЛКА «семья | чужой» (E9.4-4b-1): семья → проверки → спуск → таблицы → карты (L) → эмиссия .b2 КАНОН (M/H) → PEG-выход (G) → факты M=/H=; чужой → фронт P2 → спуск → чужие факты FOREIGN); 79 var (+pushmap — E9.4-4a; +lfanew/coffoff/optoff/sizopt/numsect/tbloff/codevaddr/falign/fend/fsect — E9.4-4b-1), 56 str (+s_ff1) | 378 |", P)
src = sub(src,
    "| `KERNEL/L5-BRIDGE/bridge_self_pe.wall` | ветвь P — разбор PE и семейство: rd16/rd32, fail_family, guard, check_head/opt/base/sect/size/body (инварианты SPEC/04), stub_name (префикс «Universal L0 » + игла «. No DOS support.» + имя 1..31 без пробельных байтов — как .isspace оракула), rva_off, walk_descs (IDT: один дескриптор + терминатор), cstr_len (quirk оракула len-1), check_dll (kernel32.dll без регистра), walk_funcs (счёт INT/IAT + чётность hint), print_facts (INS/TARGET/BSS + ВЫХОД M=/H= — E9.2-3c) | 415 |",
    "| `KERNEL/L5-BRIDGE/bridge_self_pe.wall` | ветвь P, ЧАСТЬ 1 (E9.4-4b-1) — ОБЩИЙ фронт + семейные проверки-ПРЕДИКАТ (0/1): rd16/rd32, fail_family (ОБЩИЙ отказ 6), guard (0/1), check_head (MZ + PE-сигнатура + раскладка полей ОТ e_lfanew: lfanew/coffoff/optoff/sizopt/numsect/tbloff — как lab_pe.parse), check_opt/base/sect/size/body (инварианты SPEC/04 — вычисляемые смещения; codevaddr/falign/fend — в check_sect), stub_name (имя 1..31 без пробельных байтов) | 286 |\n"
    "| `KERNEL/L5-BRIDGE/bridge_self_pi.wall` | ветвь P, ЧАСТЬ 2 (разрез pe по лимиту 500 — E9.4-4b-1) — импорты семейства + цепочка + факты: rva_off, walk_descs (IDT по DD[1] @optoff+0x78), cstr_len (quirk len-1), check_dll, walk_funcs (чётность hint) — ПРЕДИКАТЫ; fam_chain (K5-P018: 0 = семейство, 1 = нет — развилка в main), print_facts (INS/TARGET/BSS + ВЫХОД M=/H= — E9.2-3c) | 238 |\n"
    "| `KERNEL/L5-BRIDGE/bridge_self_pf.wall` | ветвь P, ЧАСТЬ 3 — ЧУЖОЙ ПУТЬ (E9.4-4b-1): foreign_front (K5-P019 — порт parse_foreign: Machine/Magic, FileAlignment степень 2, секция кода ПО ТОЧКЕ ВХОДА, EXECUTE, файл покрывает raw, тело не нулевое, вход в raw-части; глобали спуска от секции кода), print_ffacts (K5-P020 — чужая факт-строка FOREIGN=1 SECT=… == parse_foreign; файлы .b2/.peg не пишутся — срезы 4b-2+) | 152 |", P)
src = sub(src,
    "| `KERNEL/L5-BRIDGE/bridge.b2` | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c/4 + E9.4-4a): wall.exe(splice(bridge.wall)), плоский, 937200 Б — T-E9-17 | — |",
    "| `KERNEL/L5-BRIDGE/bridge.b2` | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c/4 + E9.4-4a/4b-1): wall.exe(splice(bridge.wall)), плоский, 1006092 Б — T-E9-17 | — |", P)
src = sub(src,
    "| `KERNEL/L5-BRIDGE/bridge.brick` | ГЕНЕРИРУЕМЫЙ артефакт: enc(bridge.b2), 884464 Б — T-E9-17 | — |",
    "| `KERNEL/L5-BRIDGE/bridge.brick` | ГЕНЕРИРУЕМЫЙ артефакт: enc(bridge.b2), 949580 Б — T-E9-17 | — |", P)
src = sub(src,
    "| `KERNEL/L5-BRIDGE/bridge.exe` | ГЕНЕРИРУЕМЫЙ артефакт: brick+pegen+bridge.peg — 93184 Б (тело 0x16926, target 0x16801, bss 0x125), вход 0x1200, импорты-восьмёрка; SHA-256 E79BE472… — T-E9-17; 12-й член семейства (круг T-E9-20: M=19635 H=0); пишет <выход>.b2 КАНОН (M/H — E9.2-3c) И <выход>.peg (E9.2-4) | — |",
    "| `KERNEL/L5-BRIDGE/bridge.exe` | ГЕНЕРИРУЕМЫЙ артефакт: brick+pegen+bridge.peg — 98816 Б (тело 0x17E42, target 0x17E01, bss 0x41), вход 0x1200, импорты-восьмёрка; SHA-256 4D23B561… — T-E9-17; 12-й член семейства (круг T-E9-20: M=20894 H=0); пишет <выход>.b2 КАНОН (M/H — E9.2-3c) И <выход>.peg (E9.2-4); ЧУЖИЕ PE32+ — факт-строка FOREIGN без эмиссии (E9.4-4b-1) | — |", P)
src = sub(src,
    "| `KERNEL/L5-BRIDGE/bridge.anchor.b2` + `bridge.anchor.peg` | ЯКОРЬ выхода моста о СВОЁМ образе (E9.3-1; регенерирован E9.4-4a): канон BRICK v2 (M=19635 H=0; 516 КиБ) + PEG v1 (!bss 125) == оракулу; СВИДЕТЕЛЬ выхода, НЕ вход конвейера (не путать с bridge.b2/bridge.peg — сборкой; T-E9-25; SPEC/15 п. 11) | 21097/8 |",
    "| `KERNEL/L5-BRIDGE/bridge.anchor.b2` + `bridge.anchor.peg` | ЯКОРЬ выхода моста о СВОЁМ образе (E9.3-1; регенерирован E9.4-4a/4b-1): канон BRICK v2 (M=20894 H=0; 550 КиБ) + PEG v1 (!bss 41) == оракулу; СВИДЕТЕЛЬ выхода, НЕ вход конвейера (не путать с bridge.b2/bridge.peg — сборкой; T-E9-25; SPEC/15 п. 11) | 22419/8 |", P)
src = sub(src,
    "| `KERNEL/L5-BRIDGE/BYTECODE.md` | карта образа: сводка, 119 функций (RVA — +decff/push_tgt/jtab; карта обновлена E9.4-4a — bridge_labelmap.py), данные (строки 55/глобали 87+10 массивов — w1 последним, канон 0 H), воспроизведение | 233 |",
    "| `KERNEL/L5-BRIDGE/BYTECODE.md` | карта образа: сводка, 122 функции (RVA — +fam_chain/foreign_front/print_ffacts; карта обновлена E9.4-4b-1 — gen_bytecode_e94_4b.py/bridge_labelmap.py), данные (строки 56/глобали 94+15 массивов — w1 последним, канон 0 H), воспроизведение | 256 |", P)
src = sub(src,
    "| `KERNEL/L5-BRIDGE/VERIFY.md` | подлинность + уровни проверки (242/242) + журнал срезов E9.2-1/2/3a/3b/3c/4 + E9.3-1 + E9.4-4a (порт FF /4 и таблиц; дефекты 0xC6=198, хвост !bss, 2^63 со знаком, булевы скобки, занятый ID K5-D014; уроки: транслитерация до WALL, слот-последний, ID по указателю) | 430 |",
    "| `KERNEL/L5-BRIDGE/VERIFY.md` | подлинность + уровни проверки (242/242) + журнал срезов E9.2-1/2/3a/3b/3c/4 + E9.3-1 + E9.4-4a + E9.4-4b-1 (развилка; уроки: границы декодера fend — конец тела, предикат вместо выхода, порядок чужого фронта == оракулу) | 490 |", P)
io.open(BASE + P, "w", encoding="utf-8").write(src)
print("INDEX.md:", wc(P))

# ------------------------------------------------------- MAP/INDEX-LAB.md
P = "MAP/INDEX-LAB.md"
src = io.open(BASE + P, encoding="utf-8").read()
src = sub(src,
    "| `LAB/ai/probe_e94_4a.py` | (частное) зонд-свидетель E9.4-4a ДО пересборки: сборка моста оракулами + прогоны под эмулятором — НЕЙТРАЛЬНОСТЬ (12 артефактов) + ПОРТ (synth4/5/6/7: факты/b2/peg == оракулу) — эталон порта до канонической пересборки (прецедент probe_e92_4) | 170 |",
    "| `LAB/ai/probe_e94_4a.py` | (частное) зонд-свидетель E9.4-4a ДО пересборки: сборка моста оракулами + прогоны под эмулятором — НЕЙТРАЛЬНОСТЬ (12 артефактов) + ПОРТ (synth4/5/6/7: факты/b2/peg == оракулу) — эталон порта до канонической пересборки (прецедент probe_e92_4) | 170 |\n"
    "| `LAB/ai/probe_e94_4b.py` | (частное) зонд-свидетель E9.4-4b-1 ДО пересборки: сборка моста оракулами + прогоны под эмулятором — НЕЙТРАЛЬНОСТЬ (12 артефактов: факты/b2/peg) + ПОРТ развилки (крафты foreign/foreign2: чужая факт-строка FOREIGN == parse_foreign, код 0, файлы НЕ создаются) + 7 мутантов-отказов (ERR=FAMILY 6) | 174 |\n"
    "| `LAB/ai/pat_e94_4b_corpus.py` | (частное) патч lab_t_bridge_corpus.py среза E9.4-4b-1: 12 мутантов T-E9-19 «переворачиваются» развилкой — ожидание foreign_line (факты parse_foreign), код 0 (программная замена по образцу — урок сессии 81) | 98 |\n"
    "| `LAB/ai/pat_e94_4b_map.py` | (частное) патч MAP/M5-BRIDGE.md + MAP/METHODS-2.md среза E9.4-4b-1: карточки ветви P (предикаты, вычисляемые смещения, части pe/pi/pf, новые RVA), +3 кирпича K5-P018..P020, счётчики | 138 |\n"
    "| `LAB/ai/gen_bytecode_e94_4b.py` | (частное) генератор BYTECODE.md среза E9.4-4b-1: карта функций/данных из bridge_labelmap.py (группировка по частям pe/pi/pf + описания), числа §1 — из фактов самопрогона | 246 |", P)
io.open(BASE + P, "w", encoding="utf-8").write(src)
print("INDEX-LAB.md:", wc(P))

# ---------------------------------------------------------- LAB/README.md
P = "LAB/README.md"
src = io.open(BASE + P, encoding="utf-8").read()
src = sub(src,
    "| `py/lab_t_bridge_foreign.py` | секция 18f батареи (группа 4 + CI; с E9.4-3b): СПУСК В ЧУЖОМ ТЕЛЕ — T-E9-29: parse_foreign (lab_bridge): исполняемая секция по точке входа + спуск в её теле (11 инструкций вкл. косвенный jmp с таблицей переходов) + факты для PEG v2 (target/bss — вилка на FileAlignment) + 7 мутантов-отказов + СОГЛАСОВАННОСТЬ 12 артефактов с parse_family на общих ключах; чистый Python без эмуляции |",
    "| `py/lab_t_bridge_foreign.py` | секция 18f батареи (группа 4 + CI; с E9.4-3b; ПОРТ E9.4-4b-1 — lab_run): СПУСК В ЧУЖОМ ТЕЛЕ — T-E9-29: parse_foreign (lab_bridge): исполняемая секция по точке входа + спуск в её теле (11 инструкций вкл. косвенный jmp с таблицей переходов) + факты для PEG v2 (target/bss — вилка на FileAlignment) + 7 мутантов-отказов + СОГЛАСОВАННОСТЬ 12 артефактов с parse_family на общих ключах + ПОРТ: bridge.exe на крафтах 3a/3b — чужая факт-строка FOREIGN == оракулу (код 0, файлы не создаются), 7 мутантов — ERR=FAMILY |", P)
io.open(BASE + P, "w", encoding="utf-8").write(src)
print("LAB/README.md:", wc(P))

# ------------------------------------------------------ TESTS/T-L5-BRIDGE
P = "TESTS/T-L5-BRIDGE.md"
src = io.open(BASE + P, encoding="utf-8").read()
src = sub(src,
    "(3) СОГЛАСОВАННОСТЬ: 12 артефактов семейства — факты parse_foreign == parse_family на общих ключах (body/vsize/raw/target/bss/entry_off/ins — обобщение вилки на FileAlignment верно семейству); чистый Python — без эмуляции; parse_family и bridge.exe не менялись | OK |",
    "(3) СОГЛАСОВАННОСТЬ: 12 артефактов семейства — факты parse_foreign == parse_family на общих ключах (body/vsize/raw/target/bss/entry_off/ins — обобщение вилки на FileAlignment верно семейству); (4) ПОРТ E9.4-4b-1 (сессия 84) — bridge.exe на крафтах 3a/3b: ЧУЖАЯ факт-строка FOREIGN=1 SECT=… == фактам parse_foreign (код 0, выходные файлы НЕ создаются — эмиссия срезы 4b-2+), 7 мутантов — ERR=FAMILY; T-E9-19 — 12 мутантов-«перевёртышей» (семейный инвариант сломан, образ валиден как чужой) — чужие факты, ожидание — оракул K.foreign_line | OK |", P)
src += """

## Журнал: срез E9.4-4b-1 — РАЗВИЛКА «СЕМЬЯ | ЧУЖОЙ» + ЧУЖИЕ ФАКТЫ (сессия 84)

Порт чужого пути в bridge.exe (SPEC/15 п. 10): общий фронт K5-P005
check_head (раскладка полей ОТ e_lfanew — как lab_pe.parse; отказы
фронта — общий ERR=FAMILY) -> семейная цепочка K5-P018 fam_chain
ПРЕДИКАТОМ (проверки P006..P016 — вычисляемые смещения + guard 0/1;
для семьи e_lfanew == 0x80 — нейтральность) -> не-семья уходит в
ЧУЖОЙ ПУТЬ: K5-P019 foreign_front (порт parse_foreign, порядок
проверок п. 10; глобали спуска от секции кода: codevaddr/falign/
fend) + спуск/тени/target (W001/W003 параметризованы) + K5-P020
print_ffacts — чужая факт-строка FOREIGN=1 SECT=… == parse_foreign,
код 0; файлы .b2/.peg НЕ создаются (эмиссия — срезы 4b-2+, скелет
как E9.2-1). Границы декодера — fend (конец тела; у семьи == exelen
— нейтрально). Разрез pe.wall по лимиту 500 -> pe/pi/pf. Тесты:
T-E9-29 +ПОРТ (крафты + мутанты под lab_run), T-E9-19 — 12
мутантов-«перевёртышей» дают чужие факты (ожидание — оракул), зонд
probe_e94_4b.py (12 + 2 + 7 == оракулу, с первого прогона). Батарея
242/242 (группы 1|4). Артефакты: 98816 Б, тело 0x17E42, M=20894
H=0 (якорь bridge регенерирован). Дефектов нет.
"""
io.open(BASE + P, "w", encoding="utf-8").write(src)
print("T-L5-BRIDGE.md:", wc(P))
print("OK")
