#!/usr/bin/env python3
"""pat_e94_4b_map.py — патч MAP/M5-BRIDGE.md + MAP/METHODS-2.md для
E9.4-4b-1: карточки ветви P (предикаты, вычисляемые смещения, части
pe/pi/pf), три НОВЫХ кирпича K5-P018..P020, счётчики и RVAs.
Программная замена по точному образцу (урок сессии 81)."""
import io
import sys

BASE = "/home/z/my-project/repo/"

# новые RVA (тело + 0x1000) по карте bridge_labelmap
RVA = {"rd16": "21AB", "rd32": "222C", "fail_family": "234F",
       "guard": "2398", "check_head": "2425", "check_opt": "27BC",
       "check_base": "2A57", "check_sect": "2C52",
       "check_size": "314C", "check_body": "347B",
       "stub_name": "35A3", "rva_off": "3A2F",
       "walk_descs": "3A71", "cstr_len": "3F41",
       "check_dll": "4020", "walk_funcs": "41A7",
       "fam_chain": "4422", "print_facts": "45FB",
       "foreign_front": "4BB5", "print_ffacts": "5265"}


def sub(src, old, new, path="?"):
    if old not in src:
        sys.exit("не найдено в %s: %r..." % (path, old[:60]))
    return src.replace(old, new, 1)


# ------------------------------------------------------------ M5-BRIDGE.md
P = BASE + "MAP/M5-BRIDGE.md"
src = io.open(P, encoding="utf-8").read()

src = sub(src,
          "# M5-BRIDGE — карточки кирпичей моста, часть 1 (C/P/X — 26; итог ветвей: 115 — C/P/X 26 + D/W 16 + E 17 + L 17 + M 28)",
          "# M5-BRIDGE — карточки кирпичей моста, часть 1 (C/P/X — 29; итог ветвей: 123 — C/P/X 29 + D/W 29 + E 18 + L 17 + M 28 + G 2)")
src = sub(src,
          "trace_m.py (46470/46470). PEG — E9.2-4. Ветви D/W — MAP/M5-BRIDGE-D.md,",
          "trace_m.py (46470/46470). PEG — E9.2-4. Срез E9.4-4b-1\n"
          "(РАЗВИЛКА «СЕМЬЯ | ЧУЖОЙ» + ЧУЖИЕ ФАКТЫ): K5-P005 check_head —\n"
          "ОБЩИЙ фронт (раскладка полей ОТ e_lfanew — как lab_pe.parse),\n"
          "проверки P006..P016 — ПРЕДИКАТЫ (0/1) с вычисляемыми смещениями,\n"
          "K5-P018 fam_chain — цепочка-предикат (развилка в main),\n"
          "K5-P019 foreign_front — порт parse_foreign (чужой путь,\n"
          "bridge_self_pf.wall), K5-P020 print_ffacts — чужая факт-строка\n"
          "FOREIGN=1 SECT=…; разрез pe.wall -> pe/pi/pf (лимит 500).\n"
          "Ветви D/W — MAP/M5-BRIDGE-D.md,")

# P003 fail_family — общий отказ
src = sub(src,
          "| Функция | Печатает ERR=FAMILY и завершает процесс кодом 6 — единственный отказ семейства каркаса |",
          "| Функция | Печатает ERR=FAMILY и завершает процесс кодом 6 — ОБЩИЙ отказ моста (E9.4-4b-1: не семейство И не чужой валидный образ) |", "M5-BRIDGE.md P003")
src = sub(src,
          "| Используется в | K5-P004..P014, K5-P016 |\n| Тест | T-E9-19 (19 мутантов) |\n| Статус | готов |",
          "| Используется в | K5-P004..P014, K5-P016, K5-P019 (чужой фронт) |\n| Тест | T-E9-19 |\n| Статус | готов (E9.4-4b-1 — общий отказ) |", "M5-BRIDGE.md P003")
src = src.replace("(RVA 234F)", "(RVA 234F)")     # уже верно

# P004 guard — предикат
src = sub(src,
          "| Файл | bridge_self_pe.wall (RVA 2398) |\n| Функция | Проверяет границы чтения [off, off+n) из exebuf — нарушение: отказ семейства |\n| Вход | off, n — смещение/размер (знаковые) |\n| Выход | 0; off < 0 или off+n > exelen — ERR=FAMILY (как None оракула lab_pe) |\n| Состоит из | K5-P003 |\n| Используется в | K5-P005, K5-P013 |\n| Тест | T-E9-19 |\n| Статус | готов |",
          "| Файл | bridge_self_pe.wall (RVA 2398) |\n| Функция | Проверяет границы чтения [off, off+n) из exebuf — ПРЕДИКАТ (E9.4-4b-1: вызывающий решает — общий отказ или «не семейство») |\n| Вход | off, n — смещение/размер (знаковые) |\n| Выход | 0 — ок; 1 — за файлом (как срезка/None/struct.error оракула lab_pe) |\n| Состоит из | K5-P003 |\n| Используется в | K5-P005, K5-P013, K5-P019 |\n| Тест | T-E9-19 |\n| Статус | готов (E9.4-4b-1 — предикат) |")

# P005 check_head — общий фронт
src = sub(src,
          "| Файл | bridge_self_pe.wall (RVA 2411) |\n| Функция | Проверяет минимальную длину файла (0x1B0 — все поля SPEC/04), MZ и сигнатуру PE\\0\\0 по e_lfanew (с границей) |\n| Вход | глобали exebuf/exelen |\n| Выход | 0; нарушение — ERR=FAMILY |\n| Состоит из | K5-P002, K5-P003, K5-P004 |\n| Используется в | K5-X001 |\n| Тест | T-E9-19 (мутанты MZ/PE-сигнатура/короткий файл) |\n| Статус | готов |",
          "| Файл | bridge_self_pe.wall (RVA 2425) |\n| Функция | ОБЩИЙ фронт заголовков (E9.4-4b-1: семья и чужой): файл >= 64 Б, MZ, сигнатура PE\\0\\0 по e_lfanew + РАСКЛАДКА полей ОТ e_lfanew (как lab_pe.parse оракула E9.4-3a): coffoff/optoff/sizopt/numsect/tbloff -> глобали; слот-0 COFF — с границей |\n| Вход | глобали exebuf/exelen |\n| Выход | 0; lfanew/coffoff/optoff/sizopt/numsect/tbloff -> глобали; нарушение — ОБЩИЙ ERR=FAMILY |\n| Состоит из | K5-P001, K5-P002, K5-P003, K5-P004 |\n| Используется в | K5-X001, K5-P018, K5-P019 |\n| Тест | T-E9-19 (мутанты MZ/PE-сигнатура/мусор) |\n| Статус | готов (E9.4-4b-1 — общий фронт; было — фиксированные смещения) |")

# P006..P011 — предикаты + новые RVA
for k, rva, old_desc, new_desc in [
        ("check_opt", "27BC",
         "Проверяет Machine 0x8664, NumberOfSections 1, SizeOfOptionalHeader 0xF0, Characteristics 0x22, Magic 0x020B, Subsystem 3",
         "Проверяет Machine 0x8664, NumberOfSections 1, SizeOfOptionalHeader 0xF0, Characteristics 0x22, Magic 0x020B, Subsystem 3 — ПРЕДИКАТ по ВЫЧИСЛЯЕМЫМ смещениям (E9.4-4b-1)"),
        ("check_base", "2A57",
         "Проверяет ImageBase 0x140000000 (два dword: 0x40000000/1), SectionAlignment 0x1000, FileAlignment 0x200",
         "Проверяет ImageBase 0x140000000 (два dword: 0x40000000/1), SectionAlignment 0x1000, FileAlignment 0x200 — ПРЕДИКАТ (E9.4-4b-1)"),
        ("check_sect", "2C52",
         "Проверяет имя секции «.text» (8 байт), VirtualAddress 0x1000, Characteristics 0xE0000020; читает vsize/rawsize/rawptr в глобали",
         "Проверяет имя секции «.text» (8 байт), VirtualAddress 0x1000, Characteristics 0xE0000020 — ПРЕДИКАТ; читает vsize/rawsize/rawptr + codevaddr/falign/fend в глобали (E9.4-4b-1 — развилка)"),
        ("check_size", "314C",
         "Проверяет размерные инварианты: SizeOfImage == align_up(0x1000+vsize), SizeOfHeaders == PointerToRawData (кратно 0x200), SizeOfRawData кратно 0x200, размер файла == headers+raw; точка входа в [0x1000, 0x1000+vsize) (0x1200 легальна) — entryrva в глобаль",
         "Проверяет размерные инварианты: SizeOfImage == align_up(0x1000+vsize), SizeOfHeaders == PointerToRawData (кратно 0x200), SizeOfRawData кратно 0x200, размер файла == headers+raw; точка входа в [0x1000, 0x1000+vsize) (0x1200 легальна) — entryrva в глобаль — ПРЕДИКАТ (E9.4-4b-1)"),
        ("check_body", "347B",
         "Проверяет, что тело секции не пустое и не из одних нулей (первый ненулевой байт в [rawptr, rawptr+rawsize))",
         "Проверяет, что тело секции не пустое и не из одних нулей (первый ненулевой байт в [rawptr, rawptr+rawsize)) — ПРЕДИКАТ (E9.4-4b-1)"),
        ("stub_name", "35A3",
         "Разбирает DOS-заглушку: префикс «Universal L0 » (13 байт с 0x40), игла «. No DOS support.» (16 байт, первый полный матч в [0x40+13, 0x80-16]); имя = байты между ними — длина 1..31, без пробельных байтов 09-0D/1C-1F/20/85/A0 (как .isspace оракула); modlen в глобаль",
         "Разбирает DOS-заглушку: префикс «Universal L0 » (13 байт с 0x40), игла «. No DOS support.» (16 байт, первый полный матч в [0x40+13, 0x80-16]); имя = байты между ними — длина 1..31, без пробельных байтов 09-0D/1C-1F/20/85/A0 (как .isspace оракула); modlen в глобаль — ПРЕДИКАТ (E9.4-4b-1)")]:
    src = sub(src, "| Функция | %s |\n" % old_desc,
              "| Функция | %s |\n" % new_desc, "M5-BRIDGE.md %s" % k)

# RVA-замены карточек P (уникальные строки «RVA …» внутри карточек)
OLD_RVA = {"check_opt": "(RVA 2640)", "check_base": "(RVA 27FB)",
           "check_sect": "(RVA 292A)", "check_size": "(RVA 2C71)",
           "check_body": "(RVA 2ED5)", "stub_name": "(RVA 2FE9)",
           "rva_off": "(RVA 33FA)", "walk_descs": "(RVA 343C)",
           "cstr_len": "(RVA 3832)", "check_dll": "(RVA 3911)",
           "walk_funcs": "(RVA 3A7A)", "print_facts": "(RVA 3CEB)"}
for k, old in OLD_RVA.items():
    if old in src:
        src = src.replace(old, "(RVA %s)" % RVA[k], 1)
# статусы предикатов P006..P016
src = src.replace("| Тест | T-E9-19 |\n| Статус | готов (реинкарнация",
                  "| Тест | T-E9-19 |\n| Статус | готов (E9.4-4b-1 — предикат; реинкарнация")

# P012..P017 — файл pe -> pi
for name in ("rva_off", "walk_descs", "cstr_len", "check_dll",
             "walk_funcs", "print_facts"):
    src = sub(src,
              "| Файл | bridge_self_pe.wall (RVA %s) |" % RVA[name],
              "| Файл | bridge_self_pi.wall (RVA %s) — разрез pe по лимиту 500 (E9.4-4b-1) |" % RVA[name])

# новые карточки P018..P020 — после карточки P017 (print_facts)
anchor = "### K5-P017 — print_facts"
i = src.index(anchor)
j = src.index("\n## ", i) if "\n## " in src[i:] else len(src)
new_cards = """
### K5-P018 — fam_chain

| Поле | Значение |
|---|---|
| Слой | L5 (исходник — WALL) |
| Ветвь | P — развилка «семья | чужой» |
| Файл | bridge_self_pi.wall (RVA 4422) |
| Функция | СЕМЕЙНАЯ ЦЕПОЧКА-ПРЕДИКАТ: opt -> base -> sect -> size -> body -> заглушка -> импорты (как E9.2-1); 0 = образ семейства, 1 = нет (без выхода — решает развилка main) |
| Вход | глобали exebuf/exelen/lfanew/coffoff/optoff/tbloff (K5-P005) |
| Выход | 0 — семейство; 1 — не семейство (main -> K5-P019) |
| Состоит из | K5-P006..P016 |
| Используется в | K5-X001 |
| Тест | T-E9-18/19 (12 артефактов + мутанты-«перевёртыши») |
| Статус | готов (E9.4-4b-1) |

### K5-P019 — foreign_front

| Поле | Значение |
|---|---|
| Слой | L5 (исходник — WALL) |
| Ветвь | P — ЧУЖОЙ ПУТЬ (часть 3) |
| Файл | bridge_self_pf.wall (RVA 4BB5) |
| Функция | ПОРТ parse_foreign оракула (E9.4-3b, порядок SPEC/15 п. 10): чтения оракула покрывают [optoff, optoff+0xD8) (guard — как struct.error разбора) -> Machine 0x8664 + Magic 0x020B -> FileAlignment СТЕПЕНЬ 2 -> секция кода ПО ТОЧКЕ ВХОДА (первый слот [vaddr, vaddr+vsize); слот 0 в файле, слоты за файлом обрывают таблицу) -> EXECUTE 0x20000000 -> файл покрывает raw -> тело не нулевое -> вход в raw-части |
| Вход | глобали exebuf/exelen/lfanew/coffoff/optoff/numsect/tbloff (K5-P005) |
| Выход | 0; глобали спуска от СЕКЦИИ КОДА: vsize/rawsize/rawptr/entryrva/codevaddr/falign/fend/fsect; отказ — ERR=FAMILY (код 6) |
| Состоит из | K5-P001, K5-P002, K5-P003, K5-P004 |
| Используется в | K5-X001 |
| Тест | T-E9-29 (ПОРТ: крафты 3a/3b + 7 мутантов), probe_e94_4b.py |
| Статус | готов (E9.4-4b-1) |

### K5-P020 — print_ffacts

| Поле | Значение |
|---|---|
| Слой | L5 (исходник — WALL) |
| Ветвь | P — ЧУЖОЙ ПУТЬ (часть 3) |
| Файл | bridge_self_pf.wall (RVA 5265) |
| Функция | ЧУЖАЯ факт-строка «U-L5-BRIDGE FOREIGN=1 SECT=<i> ENTRY=<hex8> VSIZE=<hex8> RAW=<hex8> INS=<dec> TARGET=<hex8> BSS=<hex8>» — в factbuf (базовые s_f2..s_f8), одним WriteFile; факты == parse_foreign оракула |
| Вход | глобали fsect/entryrva/vsize/rawsize/inscount/target/bss |
| Выход | строка в stdout; возврат 0 |
| Состоит из | K5-C006, K5-C007, K5-C008 (ext WriteFile) |
| Используется в | K5-X001 |
| Тест | T-E9-29 (ПОРТ), T-E9-19 (перевёртыши) |
| Статус | готов (E9.4-4b-1) |

"""
src = src[:j] + "\n" + new_cards.rstrip("\n") + "\n" + src[j:]
io.open(P, "w", encoding="utf-8").write(src)
print("M5-BRIDGE.md:", src.count("\n") + 1, "строк")

# ------------------------------------------------------------ METHODS-2.md
P = BASE + "MAP/METHODS-2.md"
src = io.open(P, encoding="utf-8").read()
src = sub(src,
          "## Слой L5 — мост M5-BRIDGE (E9.2-1..4: каркас + спуск + эмиссия + PEG — 117 кирпичей)",
          "## Слой L5 — мост M5-BRIDGE (E9.2-1..4 + E9.4-4a/4b-1: каркас + спуск + эмиссия + PEG + порт FF/таблиц + развилка — 123 кирпича)")
src = sub(src,
          "| K5-P017 | print_facts | P | готов (E9.2-1/2) | `MAP/M5-BRIDGE.md` |",
          "| K5-P017 | print_facts | P | готов (E9.2-1/2) | `MAP/M5-BRIDGE.md` |\n"
          "| K5-P018 | fam_chain | P | готов (E9.4-4b-1) | `MAP/M5-BRIDGE.md` |\n"
          "| K5-P019 | foreign_front | P | готов (E9.4-4b-1) | `MAP/M5-BRIDGE.md` |\n"
          "| K5-P020 | print_ffacts | P | готов (E9.4-4b-1) | `MAP/M5-BRIDGE.md` |")
io.open(P, "w", encoding="utf-8").write(src)
print("METHODS-2.md:", src.count("\n") + 1, "строк")
print("OK")
